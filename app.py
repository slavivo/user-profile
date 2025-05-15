from flask import Flask, render_template, jsonify, request
import configparser
import google.generativeai as genai
import openai
from utils import (
    ApiClientFactory, 
    get_initial_graph_prompt,
    get_reformatting_prompt,
    is_valid_graph_format
)
import asyncio
from functools import partial
import json

app = Flask(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configure API clients
OPENAI_KEY = config['DEFAULT']['OPENAI_KEY']
GENAI_KEY = config['DEFAULT']['GENAI_KEY']

# Sample student data - in a real app, this would come from a database
student_data = {
    'id': 'STU2024001',
    'school_year': '2023-2024',
    'grade': 'Second Grade',
    'class': '2.A',
    'top_abilities': [
        {'name': 'Pattern Recognition', 'value': 92},
        {'name': 'Problem Decomposition', 'value': 88},
        {'name': 'Logical Reasoning', 'value': 85}
    ],
    'top_attitudes': [
        {'name': 'Growth Mindset', 'value': 95},
        {'name': 'Curiosity', 'value': 90},
        {'name': 'Initiative', 'value': 87}
    ],
    'abilities': {
        'cognitive': {
            'pattern_recognition': 92,
            'processing_speed': 84,
            'problem_decomposition': 88,
            'spatial_reasoning': 78,
            'logical_reasoning': 85,
            'abstract_thinking': 82,
            'memory_capacity': 80,
            'information_organization': 82
        },
        'physical': {
            'hand_eye_coordination': 78,
            'fine_motor_skills': 75,
            'typing_speed': 85,
            'visual_acuity': 80
        },
        'social': {
            'emotional_intelligence': 88,
            'social_perception': 85,
            'communication_clarity': 83,
            'active_listening': 82,
            'empathy': 87,
            'stress_management': 79
        }
    },
    'attitudes': {
        'growth_mindset': 95,
        'persistence': 88,
        'curiosity': 90,
        'initiative': 87,
        'adaptability': 85,
        'risk_taking': 80,
        'self_discipline': 86,
        'collaboration': 89,
        'open_mindedness': 88,
        'responsibility': 91,
        'attention_to_detail': 84,
        'innovation_orientation': 86
    }
}

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
        if api_provider == 'openai':
            client = openai.AsyncClient(api_key=OPENAI_KEY)
        elif api_provider == 'gemini':
            genai.configure(api_key=GENAI_KEY)
            client = genai.GenerativeModel(model)
        else:
            return {'error': 'Invalid API provider'}, 400

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

if __name__ == '__main__':
    app.run(debug=True) 