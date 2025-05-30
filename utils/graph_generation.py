from typing import Dict, Any, List
import json
from .base import ApiClientFactory
import google.generativeai as genai
import openai
from graph_data import graph_data
from .template_handler import PromptTemplate

def get_api_client(provider: str, model: str = None, openai_key: str = None, genai_key: str = None):
    """Initialize and return appropriate API client based on provider."""
    if provider == 'openai':
        return openai.AsyncClient(api_key=openai_key)
    elif provider == 'gemini':
        genai.configure(api_key=genai_key)
        return genai.GenerativeModel(model if model else 'gemini-2.0-flash')
    else:
        raise ValueError('Invalid API provider')

async def generate_learning_goals_for_node(client, node_label: str, other_nodes: List[str], section_name: str, provider: str) -> List[Dict]:
    """Generate learning goals for a single node.
    
    Args:
        client: The API client to use
        node_label: The label of the current node
        other_nodes: List of labels of other nodes in the current section
        section_name: Name of the current main section
        provider: The API provider to use
    """
    try:
        # Format the other nodes as a bullet list
        other_nodes_text = "\n".join([f"- {node}" for node in other_nodes if node != node_label])
        
        # Get information about other main sections
        other_sections_info = []
        for section, data in graph_data.items():
            if section != section_name:  # Skip current section
                section_nodes = [node['data']['label'] for node in data['nodes']]
                other_sections_info.append(f"{section}:\n" + "\n".join([f"- {node}" for node in section_nodes]))
        
        other_sections_text = "\n\n".join(other_sections_info)
        template_vars = {}
        system_prompt = PromptTemplate.render('graph_learning_goals_system', **template_vars)
        template_vars = {
            "node_label": node_label,
            "section_name": section_name,
            "other_nodes": other_nodes_text,
            "other_sections": other_sections_text
        }
        user_prompt = PromptTemplate.render('graph_learning_goals_user', **template_vars)

        # Create API client
        api_client = ApiClientFactory.create_client(provider, client)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
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
            print(f"Learning goals: {learning_goals}")
            
            # Validate learning goals format and convert to required structure
            if not isinstance(learning_goals, dict):
                raise ValueError("Response is not a dictionary of grade levels")
            
            # Expected grade levels
            expected_grades = ['5th_grade', '6th_grade', '7th_grade', '8th_grade', '9th_grade', 'extra']
            
            # Convert grade-based goals to objects with name, grade, and mastered fields
            formatted_goals = []
            idx = 0
            for grade, goals in learning_goals.items():
                if grade not in expected_grades:
                    print(f"Warning: Unexpected grade level {grade}")
                    continue
                    
                if not isinstance(goals, list):
                    print(f"Warning: Goals for grade {grade} is not a list")
                    continue
                
                for goal in goals:
                    if isinstance(goal, str):
                        formatted_goals.append({
                            "name": goal,
                            "id": f"{node_label.lower().replace(' ', '_')}_{idx}",
                            "grade": grade,
                            "mastered": False
                        })
                    idx += 1
            if not formatted_goals:
                raise ValueError("No valid learning goals found in response")
            
            return formatted_goals
            
        except json.JSONDecodeError:
            raise ValueError("Failed to parse learning goals response as JSON")
            
    except Exception as e:
        print(f"Error generating learning goals for node {node_label}: {str(e)}")
        raise

async def generate_graph_async(api_provider: str, model: str, concept: str, openai_key: str = None, genai_key: str = None) -> Dict:
    """Generate learning goals for all nodes in a given concept's graph."""
    try:
        # Validate concept exists in graph_data
        if concept not in graph_data:
            return {'error': f'Concept {concept} not found in graph data'}, 400

        # Get client
        try:
            client = get_api_client(api_provider, model, openai_key, genai_key)
        except ValueError as e:
            return {'error': str(e)}, 400

        # Get the graph structure for the concept
        graph = graph_data[concept]
        
        # Get all node labels from the graph
        all_node_labels = [node['data']['label'] for node in graph['nodes']]
        
        # Generate learning goals for each node
        for node in graph['nodes']:
            try:
                node_label = node['data']['label']
                learning_goals = await generate_learning_goals_for_node(
                    client,
                    node_label,
                    all_node_labels,
                    concept,
                    api_provider
                )
                # Update the node with new learning goals
                node['data']['learning_goals'] = learning_goals
            except Exception as e:
                print(f"Error processing node {node_label}: {str(e)}")
                # Continue with other nodes even if one fails
                continue

        return {
            'response': graph,
            'message': 'Learning goals generated successfully'
        }

    except Exception as e:
        print(f"Error generating learning goals: {str(e)}")
        return {'error': str(e)}, 500

def format_graph_for_cytoscape(graph_json: Dict) -> Dict:
    """Format the graph data for Cytoscape visualization."""
    return {
        "nodes": [
            {"data": {
                "id": node["data"]["id"],
                "label": node["data"]["label"],
                "learning_goals": node["data"].get("learning_goals", [])
            }} for node in graph_json["nodes"]
        ],
        "edges": [
            {"data": {
                "source": edge["data"]["source"],
                "target": edge["data"]["target"]
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