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
from student_data import student_data

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
    return render_template('pages/profile.html', student=student_data)

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
        return jsonify(result)
    finally:
        loop.close()

@app.route('/activities_content')
def activities_content():
    """Return just the activities section HTML"""
    return render_template('components/activities/activities_list.html', activities=student_data['activities'])

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
            'connected_nodes': list(generated_data['connected_concepts'].keys()),
            'competency_scores': {
                'problem_solving': int(generated_data['competencies']['problem_solving'] / 10),
                'critical_thinking': int(generated_data['competencies']['critical_thinking'] / 10),
                'analysis': int(generated_data['competencies']['analytical_skills'] / 10),
                'technical': int(generated_data['competencies']['technical_proficiency'] / 10),
                'communication': int(generated_data['competencies']['communication'] / 10),
                'collaboration': int(generated_data['competencies']['collaboration'] / 10)
            },
            'taxonomy': {
                'processing_levels': [
                    {'level': 'Retrieval', 'weight': generated_data['taxonomy']['processing_levels']['retrieval'] / 100},
                    {'level': 'Comprehension', 'weight': generated_data['taxonomy']['processing_levels']['comprehension'] / 100},
                    {'level': 'Analysis', 'weight': generated_data['taxonomy']['processing_levels']['analysis'] / 100},
                    {'level': 'Use of Knowledge', 'weight': generated_data['taxonomy']['processing_levels']['knowledge_utilization'] / 100},
                    {'level': 'Metacognitive', 'weight': generated_data['taxonomy']['processing_levels']['metacognition'] / 100},
                    {'level': 'Self-system Thinking', 'weight': generated_data['taxonomy']['processing_levels']['self_system_thinking'] / 100}
                ],
                'knowledge_domains': [
                    {'domain': 'Information', 'weight': generated_data['taxonomy']['knowledge_domains']['information'] / 100},
                    {'domain': 'Mental Procedures', 'weight': generated_data['taxonomy']['knowledge_domains']['mental_procedures'] / 100},
                    {'domain': 'Psychomotor Procedures', 'weight': generated_data['taxonomy']['knowledge_domains']['psychomotor_procedures'] / 100}
                ]
            },
            'student_performance': {
                'overall_score': 0,  # Initialize with 0
                'concept_scores': {
                    concept_id: {
                        'name': concept_id.title(),  # Placeholder name, should be replaced with actual concept names
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

@app.route('/api/concepts')
def get_concepts():
    """Return the current concept graph data"""
    try:
        # Return the concepts from student data
        # This assumes student_data has a 'concept_graph' field
        # If not, you'll need to modify this to match your data structure
        if 'concept_graph' in student_data:
            return jsonify(student_data['concept_graph'])
        else:
            # Return a default concept graph structure
            return jsonify({
                'nodes': [
                    {'id': 'algo1', 'label': 'Algorithms', 'progress': 75},
                    {'id': 'data1', 'label': 'Data Structures', 'progress': 65},
                    {'id': 'prog1', 'label': 'Programming Basics', 'progress': 90},
                    {'id': 'web1', 'label': 'Web Development', 'progress': 80},
                    {'id': 'db1', 'label': 'Databases', 'progress': 70},
                    {'id': 'net1', 'label': 'Networking', 'progress': 60}
                ],
                'edges': [
                    {'source': 'prog1', 'target': 'algo1'},
                    {'source': 'prog1', 'target': 'data1'},
                    {'source': 'algo1', 'target': 'web1'},
                    {'source': 'data1', 'target': 'db1'},
                    {'source': 'web1', 'target': 'net1'}
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 