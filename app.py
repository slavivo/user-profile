from flask import Flask, render_template, jsonify, request
import configparser
import google.generativeai as genai
import openai
from utils.base import (
    ApiClientFactory, 
    get_initial_graph_prompt,
    get_reformatting_prompt,
    is_valid_graph_format
)
import asyncio
import uuid
from datetime import datetime
from utils.activity_generation import generate_activity_metadata
from utils.personalization import prepare_personalized_activity_params
from student_data import student_data
from graph_data import graph_data
from meta_data import meta_data
import json

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

def get_concept_name(node_id):
    """Get concept name from its ID by searching through all graph data."""
    for category, data in graph_data.items():
        for node in data['nodes']:
            if node['data']['id'] == node_id:
                return node['data']['label']
    return node_id  # Return ID if name not found

@app.route('/')
def index():
    return render_template('pages/profile.html', student=student_data, get_concept_name=get_concept_name)

async def get_reformatting_client(provider_preference='gemini'):
    """Get a client for reformatting, preferring Gemini 2.0 flash or GPT-4O"""
    try:
        if provider_preference == 'gemini':
            genai.configure(api_key=GENAI_KEY)
            client = genai.GenerativeModel('gemini-2.0-flash')
            return 'gemini', client
        else:
            client = openai.AsyncClient(api_key=OPENAI_KEY)
            return 'openai', client
    except Exception:
        # If preferred provider fails, try the other one
        try:
            if provider_preference == 'gemini':
                client = openai.AsyncClient(api_key=OPENAI_KEY)
                return 'openai', client
            else:
                genai.configure(api_key=GENAI_KEY)
                client = genai.GenerativeModel('gemini-2.0-flash')
                return 'gemini', client
        except Exception as e:
            raise Exception("Failed to initialize both Gemini and OpenAI clients") from e

async def generate_graph_async(api_provider, model, concept):
    try:
        # Step 1: Generate initial graph description
        try:
            client = get_api_client(api_provider, model)
        except ValueError as e:
            return {'error': str(e)}, 400

        # Create API client for initial description
        api_client = ApiClientFactory.create_client(api_provider, client)

        # Get initial description
        initial_messages = [
            {"role": "system", "content": "You are a helpful AI assistant that generates knowledge graphs for educational concepts."},
            {"role": "user", "content": get_initial_graph_prompt(concept)}
        ]

        initial_params = ApiClientFactory.create_params(
            api_provider,
            client=client,
            messages=initial_messages,
            model=model,
            temperature=0.7,
            max_tokens=2000
        )

        initial_response = await api_client.chat_completion_request(initial_params)
        initial_description = initial_response.content

        # Step 2: Format the description into proper JSON
        # Try up to 3 times with validation
        for attempt in range(3):
            try:
                # Get reformatting client (Gemini 2.0 flash or GPT-4O)
                reformat_provider, reformat_client = await get_reformatting_client()
                reformat_api_client = ApiClientFactory.create_client(reformat_provider, reformat_client)

                # Prepare reformatting messages
                reformat_messages = [
                    {"role": "system", "content": "You are a helpful AI assistant that formats knowledge graph descriptions into JSON."},
                    {"role": "user", "content": get_reformatting_prompt(concept, initial_description)}
                ]

                reformat_model = 'gemini-2.0-flash' if reformat_provider == 'gemini' else 'gpt-4o-2024-08-06'
                reformat_params = ApiClientFactory.create_params(
                    reformat_provider,
                    client=reformat_client,
                    messages=reformat_messages,
                    model=reformat_model,
                    temperature=0.2,
                    max_tokens=2000
                )

                reformat_response = await reformat_api_client.chat_completion_request(reformat_params)
                formatted_response = reformat_response.content

                is_valid, formatted_response = is_valid_graph_format(formatted_response)
                
                if is_valid:
                    return {
                        'response': formatted_response,
                        'initial_description': initial_description
                    }
                
                if attempt == 2:  # Last attempt failed
                    return {
                        'error': 'Failed to generate valid graph format after 3 attempts',
                        'initial_description': initial_description,
                        'last_attempt': formatted_response
                    }, 500

            except Exception as e:
                if attempt == 2:  # Last attempt failed
                    raise e
                continue

    except Exception as e:
        print(f"Error generating graph: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    data = request.json
    api_provider = data.get('api_provider')
    model = data.get('model')
    concept = data.get('concept')

    if not api_provider or not concept or not model:
        return jsonify({'error': 'Missing required parameters'}), 400

    # Run the async function in the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(generate_graph_async(api_provider, model, concept))
        
        # If generation was successful, update the stored graph data
        if isinstance(result, dict) and not result.get('error'):
            # Update the graph data for the specific concept
            if 'response' in result:
                try:
                    # Parse the response if it's a string
                    graph_json = json.loads(result['response']) if isinstance(result['response'], str) else result['response']
                    
                    # Format the data for Cytoscape
                    formatted_data = {
                        "nodes": [
                            {"data": {
                                "id": node["id"],
                                "label": node["label"],
                                "progress": node["progress"]
                            }} for node in graph_json["nodes"]
                        ],
                        "edges": [
                            {"data": {
                                "source": edge["source"],
                                "target": edge["target"]
                            }} for edge in graph_json["edges"]
                        ]
                    }
                    
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
    finally:
        loop.close()

@app.route('/activities_content')
def activities_content():
    """Return just the activities section HTML"""
    return render_template('components/activities/activities_list.html', activities=student_data['activities'], get_concept_name=get_concept_name)

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
        
        # Format activity data
        activity_data = {
            'id': f"ACT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8]}",
            'name': generated_data['name'],
            'description': generated_data['description'],
            'learning_goals': generated_data['learning_goals'],
            'connected_nodes': [
                {
                    'id': node_id,
                    'connection_strength': strength
                }
                for node_id, strength in generated_data['connected_concepts'].items()
            ],
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
                'overall_score': 0,  # Initialize with 0
                'concept_scores': {
                    concept_id: {
                        'name': get_concept_name(concept_id),  # Use the helper function to get proper concept names
                        'score': 0  # Initialize with 0
                    }
                    for concept_id in generated_data['connected_concepts'].keys()
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

        if not concept_focus or not competency_focus:
            return jsonify({'error': 'Missing required parameters'}), 400

        # Get personalized activity parameters
        try:
            activity_params = prepare_personalized_activity_params(concept_focus, competency_focus)
            return jsonify(activity_params)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all_nodes')
def get_all_nodes():
    """Return all nodes from all concept graphs combined"""
    try:
        # Get all nodes from all categories in graph_data
        all_nodes = []
        for category, data in graph_data.items():
            all_nodes.extend(data['nodes'])
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

if __name__ == '__main__':
    app.run(debug=True) 