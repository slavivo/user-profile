from flask import Flask, render_template, jsonify, request
import configparser
import asyncio
import uuid
from datetime import datetime
import json
from utils.activity_generation import generate_activity_metadata
from utils.methodology_decomposition import decompose_methodology
from utils.personalization import prepare_personalized_activity_params
from utils.graph_generation import (
    generate_graph_async,
    get_concept_name,
    get_all_nodes,
    format_graph_for_cytoscape
)
from student_data import student_data
from graph_data import graph_data
from meta_data import meta_data
import google.generativeai as genai
import openai

app = Flask(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configure API clients
OPENAI_KEY = config['DEFAULT']['OPENAI_KEY']
GENAI_KEY = config['DEFAULT']['GENAI_KEY']

def get_api_client(provider: str, model: str = None):
    """Initialize and return appropriate API client based on provider."""
    if provider == 'openai':
        return openai.AsyncClient(api_key=OPENAI_KEY)
    elif provider == 'gemini':
        genai.configure(api_key=GENAI_KEY)
        return genai.GenerativeModel(model if model else 'gemini-2.0-flash')
    else:
        raise ValueError('Invalid API provider')

@app.route('/')
def index():
    return render_template('pages/profile.html', student=student_data, get_concept_name=get_concept_name, graph_data=graph_data)

@app.route('/generate_graph', methods=['POST'])
async def generate_graph():
    data = request.json
    api_provider = data.get('api_provider')
    model = data.get('model')
    concept = data.get('concept')

    if not api_provider or not concept or not model:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        result = await generate_graph_async(
            api_provider=api_provider,
            model=model,
            concept=concept,
            openai_key=OPENAI_KEY,
            genai_key=GENAI_KEY
        )
        
        # If generation was successful, update the stored graph data
        if isinstance(result, dict) and not result.get('error'):
            # Update the graph data for the specific concept
            if 'response' in result:
                try:
                    # Parse the response if it's a string
                    graph_json = json.loads(result['response']) if isinstance(result['response'], str) else result['response']
                    
                    # Format the data for Cytoscape
                    formatted_data = format_graph_for_cytoscape(graph_json)
                    
                    # Store the formatted data
                    graph_data[concept] = formatted_data
                    
                    # Return both the new graph and confirmation of update
                    return jsonify({
                        'response': formatted_data,
                        'message': 'Graph data updated successfully',
                        'initial_description': result.get('initial_description')
                    })
                except (json.JSONDecodeError, KeyError) as e:
                    return jsonify({
                        'error': f'Failed to process graph data: {str(e)}',
                        'initial_description': result.get('initial_description')
                    }), 500
        
        return jsonify(result)
    except Exception as e:
        print(f"Error generating graph: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/activities_content')
def activities_content():
    """Return just the activities section HTML"""
    return render_template('components/activities/main.html', student=student_data, get_concept_name=get_concept_name, graph_data=graph_data)

@app.route('/generate_activity', methods=['POST'])
async def generate_activity():
    try:
        data = request.json
        name = data.get('name')
        provider = data.get('provider')
        model = data.get('model')
        mode = data.get('mode')

        # Validate required fields
        if not all([name, provider, model, mode]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            client = get_api_client(provider, model)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Prepare generation parameters based on mode
        generation_params = {
            'client': client,
            'provider': provider,
            'model': model,
            'name': name,
            'mode': mode,
            'taxonomy': data.get('taxonomy')  # Add taxonomy parameter for all modes
        }

        # Add mode-specific parameters
        if mode == 'brief':
            generation_params['brief_description'] = data.get('brief_description')
        elif mode == 'full':
            generation_params['full_description'] = data.get('full_description')
        elif mode == 'concepts':
            generation_params.update({
                'brief_description': data.get('brief_description'),
                'concepts': data.get('concepts', [])
            })
        elif mode == 'competencies':
            generation_params.update({
                'brief_description': data.get('brief_description'),
                'competencies': data.get('competencies', {})
            })
        elif mode == 'learning-goals':
            generation_params.update({
                'brief_description': data.get('brief_description'),
                'learning_goals': data.get('learning_goals', [])
            })
        elif mode == 'taxonomy':
            generation_params.update({
                'brief_description': data.get('brief_description'),
                'taxonomy': data.get('taxonomy', {})
            })
        elif mode == 'combined':
            # Add all available parameters for combined mode
            generation_params.update({
                'brief_description': data.get('brief_description'),
                'full_description': data.get('full_description'),
                'concepts': data.get('concepts'),
                'competencies': data.get('competencies'),
                'learning_goals': data.get('learning_goals'),
                'taxonomy': data.get('taxonomy')
            })
        else:
            return jsonify({'error': f'Unsupported mode: {mode}'}), 400
        
        # Generate activity metadata
        generated_data = await generate_activity_metadata(**generation_params)
        print(f"Generated data: {generated_data}")
        
        # Format activity data
        activity_data = {
            'id': f"ACT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8]}",
            'name': generated_data['name'],
            'description': generated_data['description'],
            'learning_goals': generated_data['learning_goals'],
            'competency_scores': {
                'Learning Competency': float(generated_data['competencies'].get('learning_competency', 0)) / 10,
                'Problem Solving': float(generated_data['competencies'].get('problem_solving', 0)) / 10,
                'Communication': float(generated_data['competencies'].get('communication', 0)) / 10,
                'Social and Personal': float(generated_data['competencies'].get('social_and_personal', 0)) / 10,
                'Civic': float(generated_data['competencies'].get('civic', 0)) / 10,
                'Digital': float(generated_data['competencies'].get('digital', 0)) / 10,
                'Work': float(generated_data['competencies'].get('work', 0)) / 10,
                'Cultural Awareness': float(generated_data['competencies'].get('cultural_awareness', 0)) / 10
            },
            'taxonomy': {
                'processing_levels': [
                    {'level': 'Retrieval', 'weight': float(generated_data['taxonomy']['processing_levels'].get('retrieval', 0)) / 100},
                    {'level': 'Comprehension', 'weight': float(generated_data['taxonomy']['processing_levels'].get('comprehension', 0)) / 100},
                    {'level': 'Analysis', 'weight': float(generated_data['taxonomy']['processing_levels'].get('analysis', 0)) / 100},
                    {'level': 'Use of Knowledge', 'weight': float(generated_data['taxonomy']['processing_levels'].get('knowledge_utilization', 0)) / 100},
                    {'level': 'Metacognitive System', 'weight': float(generated_data['taxonomy']['processing_levels'].get('metacognition', 0)) / 100},
                    {'level': 'Self-system Thinking', 'weight': float(generated_data['taxonomy']['processing_levels'].get('self_system_thinking', 0)) / 100}
                ],
                'knowledge_domains': [
                    {'domain': 'Information', 'weight': float(generated_data['taxonomy']['knowledge_domains'].get('information', 0)) / 100},
                    {'domain': 'Mental Procedures', 'weight': float(generated_data['taxonomy']['knowledge_domains'].get('mental_procedures', 0)) / 100},
                    {'domain': 'Psychomotor Procedures', 'weight': float(generated_data['taxonomy']['knowledge_domains'].get('psychomotor_procedures', 0)) / 100}
                ]
            },
            'student_performance': {
                'learning_goals': {
                    goal['id']: {
                        'name': goal['name'],
                        'mastered': False
                    } for goal in generated_data['learning_goals']
                }
            }
        }
        
        # Add to activities list
        student_data['activities'].append(activity_data)
        return jsonify({'success': True, 'activity': activity_data})
        
    except Exception as e:
        print(f"Error generating activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/prepare_personalized_params', methods=['POST'])
def prepare_personalized_params():
    try:
        data = request.json
        concept_focus = data.get('concept_focus')
        competency_focus = data.get('competency_focus')
        provider = data.get('provider', 'gemini')  # Default to gemini if not provided
        model = data.get('model', 'gemini-2.0-flash')  # Default to gemini-2.0-flash if not provided

        if not concept_focus or not competency_focus:
            return jsonify({'error': 'Missing required parameters'}), 400

        # Get all nodes from the graph data
        all_nodes = []
        for category in graph_data.values():
            if isinstance(category, dict) and 'nodes' in category:
                all_nodes.extend(category['nodes'])

        # Collect learning goals based on concept focus
        selected_learning_goals = []
        brief_description = ""

        if concept_focus == 'unmastered':
            # Find concepts with both mastered and unmastered learning goals
            for node in all_nodes:
                node_data = node['data']
                learning_goals = node_data.get('learning_goals', [])
                mastered_goals = [goal for goal in learning_goals if goal.get('mastered', False)]
                unmastered_goals = [goal for goal in learning_goals if not goal.get('mastered', False)]
                
                if mastered_goals and unmastered_goals:
                    # Add unmastered goals
                    selected_learning_goals.extend([
                        {
                            'id': goal['id'],
                            'name': goal['name'],
                            'node_label': node_data['label']
                        }
                        for goal in unmastered_goals
                    ])
            
            brief_description = "Generate an activity that helps master unmastered learning goals while building upon already mastered concepts."

        elif concept_focus == 'new':
            # Find concepts with no mastered learning goals
            for node in all_nodes:
                node_data = node['data']
                learning_goals = node_data.get('learning_goals', [])
                if not any(goal.get('mastered', False) for goal in learning_goals):
                    # Add all goals from this concept
                    selected_learning_goals.extend([
                        {
                            'id': goal['id'],
                            'name': goal['name'],
                            'node_label': node_data['label']
                        }
                        for goal in learning_goals
                    ])
            
            brief_description = "Generate an activity that introduces new concepts and their learning goals."

        elif concept_focus == 'broaden':
            # Find concepts where all learning goals are mastered
            for node in all_nodes:
                node_data = node['data']
                learning_goals = node_data.get('learning_goals', [])
                if all(goal.get('mastered', False) for goal in learning_goals):
                    brief_description = f"Generate an activity that broadens and deepens knowledge in {node_data['label']}, where all learning goals have been mastered. The activity should explore advanced applications and connections to other concepts."
                    break  # We only need one concept for broadening

        # Get competency levels based on focus
        competencies = {}
        if competency_focus == 'strong':
            # Focus on competencies with higher scores
            for comp in meta_data['competencies']:
                score = student_data.get('competencies', {}).get(comp['id'], 0)
                if score >= 7:  # Consider scores 7-10 as strong
                    competencies[comp['id']] = 80  # Set high target for strong competencies
                else:
                    competencies[comp['id']] = 50  # Set moderate target for others
        else:  # weak
            # Focus on competencies with lower scores
            for comp in meta_data['competencies']:
                score = student_data.get('competencies', {}).get(comp['id'], 0)
                if score <= 3:  # Consider scores 0-3 as weak
                    competencies[comp['id']] = 80  # Set high target for weak competencies
                else:
                    competencies[comp['id']] = 50  # Set moderate target for others

        # Prepare activity parameters
        activity_params = {
            'name': f"Personalized Activity - {concept_focus.capitalize()}",
            'provider': provider,
            'model': model,
            'brief_description': brief_description,
            'learning_goals': selected_learning_goals,
            'competencies': competencies
        }

        return jsonify(activity_params)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all_nodes')
def get_all_nodes_route():
    """Return all nodes from all concept graphs combined"""
    try:
        all_nodes = get_all_nodes()
        return jsonify(all_nodes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/concept_graph_data')
def get_concept_graph_data():
    """Return the detailed concept graph data for all categories"""
    try:
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/taxonomy')
def get_taxonomy():
    """Return the taxonomy data including processing levels and domain of knowledge"""
    try:
        return jsonify(meta_data['taxonomy'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/competencies')
def get_competencies():
    """Return the list of competencies with student values if available"""
    try:
        competencies = meta_data['competencies']
        student_competencies = student_data.get('competencies', {})
        
        # Merge metadata with student values
        enriched_competencies = []
        for comp in competencies:
            comp_data = comp.copy()
            comp_data['value'] = student_competencies.get(comp['id'], 0)
            enriched_competencies.append(comp_data)
            
        return jsonify(enriched_competencies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/abilities')
def get_abilities():
    """Return all abilities (cognitive, social, and physical) with student values if available"""
    try:
        abilities = meta_data['abilities']
        student_abilities = student_data.get('abilities', {})
        
        # Merge metadata with student values for each ability category
        enriched_abilities = {}
        for category in ['cognitive', 'social', 'physical']:
            category_meta = abilities.get(category, [])
            student_category = student_abilities.get(category, {})
            
            enriched_category = []
            for ability in category_meta:
                ability_data = ability.copy()
                ability_data['value'] = student_category.get(ability['id'], 0)
                enriched_category.append(ability_data)
                
            enriched_abilities[category] = enriched_category
            
        return jsonify(enriched_abilities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attitudes')
def get_attitudes():
    """Return the list of attitudes with student values if available"""
    try:
        attitudes = meta_data['attitudes']
        student_attitudes = student_data.get('attitudes', {})
        
        # Merge metadata with student values
        enriched_attitudes = []
        for attitude in attitudes:
            attitude_data = attitude.copy()
            attitude_data['value'] = student_attitudes.get(attitude['id'], 0)
            enriched_attitudes.append(attitude_data)
            
        return jsonify(enriched_attitudes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_graph_data', methods=['POST'])
def save_graph_data():
    """Save the current graph data to graph_data.py file"""
    try:
        # Convert the graph data to a JSON string
        graph_data_str = json.dumps(graph_data, indent=2)
        
        # Replace JSON booleans with Python booleans
        graph_data_str = graph_data_str.replace('"mastered": false', '"mastered": False')
        graph_data_str = graph_data_str.replace('"mastered": true', '"mastered": True')
        
        # Format as a Python variable assignment
        graph_data_str = "graph_data = " + graph_data_str
        
        # Write to the file
        with open('graph_data.py', 'w') as f:
            f.write(graph_data_str)
            
        return jsonify({'success': True, 'message': 'Graph data saved successfully'})
    except Exception as e:
        print(f"Error saving graph data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_student_data', methods=['POST'])
def save_student_data():
    """Save the current student data to student_data.py file"""
    try:
        # Convert the student data to a JSON string
        student_data_str = json.dumps(student_data, indent=2)
        
        # Replace JSON booleans with Python booleans
        student_data_str = student_data_str.replace('"mastered": false', '"mastered": False')
        student_data_str = student_data_str.replace('"mastered": true', '"mastered": True')
        
        # Format as a Python variable assignment
        student_data_str = "student_data = " + student_data_str
        
        # Write to the file
        with open('student_data.py', 'w') as f:
            f.write(student_data_str)
            
        return jsonify({'success': True, 'message': 'Student data saved successfully'})
    except Exception as e:
        print(f"Error saving student data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/import_methodology', methods=['POST'])
async def import_methodology():
    """Import a methodology by decomposing it into activities and generating metadata"""
    try:
        data = request.json
        methodology_description = data.get('methodology_description')
        provider = data.get('provider', 'gemini')  # Default to gemini if not provided
        model = data.get('model', 'gemini-2.0-flash')  # Default model

        if not methodology_description:
            return jsonify({'error': 'Missing methodology description'}), 400

        try:
            client = get_api_client(provider, model)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        # First, decompose the methodology into activities
        decomposed_activities = await decompose_methodology(
            client=client,
            provider=provider,
            model=model,
            methodology_description=methodology_description
        )

        # Generate activities for each decomposed activity
        generated_activities = []
        for idx, single_activity_data in enumerate(decomposed_activities):
            activity_full_desc = single_activity_data.get("full_description")
            activity_name = single_activity_data.get("name", single_activity_data.get("title", f"Activity {idx + 1}"))

            if not activity_full_desc:
                print(f"Skipping activity generation for {activity_name} due to missing full_description")
                continue

            # Prepare activity generation request
            activity_request = {
                'name': activity_name,
                'provider': provider,
                'model': model,
                'mode': 'full',
                'full_description': activity_full_desc
            }

            try:
                # Create a request context and call generate_activity
                with app.test_request_context(method='POST', json=activity_request):
                    activity_result = await generate_activity()
                    if isinstance(activity_result, tuple):
                        response_data, status_code = activity_result
                        if status_code == 200 and 'activity' in response_data:
                            generated_activities.append(response_data['activity'])
                    elif isinstance(activity_result, dict) and 'activity' in activity_result:
                        generated_activities.append(activity_result['activity'])
            except Exception as e:
                print(f"Error generating activity {activity_name}: {str(e)}")
                continue

        return jsonify({
            'success': True,
            'message': f'Successfully generated {len(generated_activities)} activities',
            'activities': generated_activities
        })

    except Exception as e:
        print(f"Error importing methodology: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 