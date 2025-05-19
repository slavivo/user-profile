from typing import Dict, Any, Tuple
import json
from .base import (
    ApiClientFactory,
    get_initial_graph_prompt,
    get_reformatting_prompt,
    is_valid_graph_format
)
import google.generativeai as genai
import openai
from graph_data import graph_data

def get_api_client(provider: str, model: str = None, openai_key: str = None, genai_key: str = None):
    """Initialize and return appropriate API client based on provider."""
    if provider == 'openai':
        return openai.AsyncClient(api_key=openai_key)
    elif provider == 'gemini':
        genai.configure(api_key=genai_key)
        return genai.GenerativeModel(model if model else 'gemini-2.0-flash')
    else:
        raise ValueError('Invalid API provider')

async def get_reformatting_client(provider_preference='gemini', openai_key: str = None, genai_key: str = None):
    """Get a client for reformatting, preferring Gemini 2.0 flash or GPT-4O"""
    try:
        if provider_preference == 'gemini':
            genai.configure(api_key=genai_key)
            client = genai.GenerativeModel('gemini-2.0-flash')
            return 'gemini', client
        else:
            client = openai.AsyncClient(api_key=openai_key)
            return 'openai', client
    except Exception:
        # If preferred provider fails, try the other one
        try:
            if provider_preference == 'gemini':
                client = openai.AsyncClient(api_key=openai_key)
                return 'openai', client
            else:
                genai.configure(api_key=genai_key)
                client = genai.GenerativeModel('gemini-2.0-flash')
                return 'gemini', client
        except Exception as e:
            raise Exception("Failed to initialize both Gemini and OpenAI clients") from e

async def generate_learning_goals(client, concept: str, nodes: list, provider: str) -> Dict:
    """Generate learning goals for each node in the graph."""
    try:
        # Prepare nodes list for the prompt
        nodes_text = "\n".join([f"- {node['id']}: {node['label']}" for node in nodes])
        
        # Read and format the learning goals prompt
        with open('prompts/get_learning_goals.txt', 'r') as f:
            prompt_template = f.read()
        
        prompt = prompt_template.replace('${concept}', concept).replace('${nodes}', nodes_text)

        # Create API client
        api_client = ApiClientFactory.create_client(provider, client)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that generates learning goals for educational concepts."},
            {"role": "user", "content": prompt}
        ]
        
        # Set parameters
        params = ApiClientFactory.create_params(
            provider,
            client=client,
            messages=messages,
            model='gemini-2.0-flash' if provider == 'gemini' else 'gpt-4o-2024-08-06',
            temperature=0.7,
            max_tokens=2000
        )
        
        # Get response
        response = await api_client.chat_completion_request(params)
        # Parse and validate the response
        try:
            response_text = response.content
            response_text = response_text.strip()
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                response_text = response_text[start:end]
            else:
                raise ValueError("Response is not a dictionary")
            
            learning_goals = json.loads(response_text)
            # Validate each node's learning goals
            for node_id, goals in learning_goals.items():
                if not isinstance(goals, list):
                    raise ValueError(f"Learning goals for {node_id} is not a list")
                for goal in goals:
                    if not isinstance(goal, dict) or 'name' not in goal or 'mastered' not in goal:
                        raise ValueError(f"Invalid learning goal format for {node_id}")
            
            return learning_goals
        except json.JSONDecodeError:
            raise ValueError("Failed to parse learning goals response as JSON")
            
    except Exception as e:
        print(f"Error generating learning goals: {str(e)}")
        raise

async def generate_graph_async(api_provider: str, model: str, concept: str, openai_key: str = None, genai_key: str = None) -> Dict:
    """Generate a knowledge graph for a given concept using the specified AI provider."""
    try:
        # Step 1: Generate initial graph description
        try:
            client = get_api_client(api_provider, model, openai_key, genai_key)
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
        formatted_response = None
        for attempt in range(3):
            try:
                # Get reformatting client (Gemini 2.0 flash or GPT-4O)
                reformat_provider, reformat_client = await get_reformatting_client(openai_key=openai_key, genai_key=genai_key)
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
                    break

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

        if not formatted_response:
            return {
                'error': 'Failed to generate valid graph format',
                'initial_description': initial_description
            }, 500

        # Step 3: Generate learning goals for each node
        learning_goals = None
        formatted_response = json.loads(formatted_response)
        for attempt in range(3):
            try:
                learning_goals = await generate_learning_goals(
                    reformat_client,
                    concept,
                    formatted_response['nodes'],
                    reformat_provider
                )
                break
            except Exception as e:
                if attempt == 2:  # Last attempt failed
                    print(f"Error generating learning goals after 3 attempts: {str(e)}")
                    # Return graph without learning goals if all attempts fail
                    return {
                        'response': formatted_response,
                        'initial_description': initial_description,
                        'warning': 'Failed to generate learning goals after 3 attempts'
                    }
                continue

        # Add learning goals to each node if generation was successful
        if learning_goals:
            for node in formatted_response['nodes']:
                node['learning_goals'] = learning_goals.get(node['id'], [])
        return {
            'response': json.dumps(formatted_response),
            'initial_description': initial_description
        }

    except Exception as e:
        print(f"Error generating graph: {str(e)}")
        return {'error': str(e)}, 500

def format_graph_for_cytoscape(graph_json: Dict) -> Dict:
    """Format the graph data for Cytoscape visualization."""
    return {
        "nodes": [
            {"data": {
                "id": node["id"],
                "label": node["label"],
                "learning_goals": node.get("learning_goals", [])
            }} for node in graph_json["nodes"]
        ],
        "edges": [
            {"data": {
                "source": edge["source"],
                "target": edge["target"]
            }} for edge in graph_json["edges"]
        ]
    }

def get_concept_name(node_id: str) -> str:
    """Get concept name from its ID by searching through all graph data."""
    for category, data in graph_data.items():
        for node in data['nodes']:
            if node['data']['id'] == node_id:
                return node['data']['label']
    return node_id  # Return ID if name not found

def get_all_nodes():
    """Return all nodes from all concept graphs combined."""
    all_nodes = []
    for category, data in graph_data.items():
        all_nodes.extend(data['nodes'])
    return all_nodes 