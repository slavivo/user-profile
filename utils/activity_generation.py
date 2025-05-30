from typing import Dict, List, Any, Tuple
import json
import time
from .base import (
    ApiClientFactory,
    get_learning_goals_prompt,
    get_connected_concepts_prompt,
    get_competency_prompt,
    get_taxonomy_prompt,
    generate_with_retry
)
from .template_handler import PromptTemplate
from graph_data import graph_data

def format_competencies_text(competencies: Dict[str, int]) -> str:
    """Format competencies dictionary into a readable text format."""
    prefix = "Target Competency Levels:\n"
    return prefix + "\n".join([f"- {key.replace('_', ' ').title()}: {value}%" for key, value in competencies.items()])

def format_concepts_text(concepts: List[str]) -> str:
    """Format concepts list into a readable text format."""
    prefix = "Concepts to Focus On:\n"
    return prefix + "\n".join([f"- {concept}" for concept in concepts])

def format_learning_goals_text(learning_goals: List[str]) -> str:
    """Format learning goals list into a readable text format."""
    prefix = "Learning Goals to Achieve:\n"
    return prefix + "\n".join([f"- {goal}" for goal in learning_goals])

def format_taxonomy_text(taxonomy: Dict[str, Any]) -> str:
    """Format taxonomy dictionary into a readable text format."""
    if not taxonomy:
        return ""
        
    result = "Taxonomy Classification:\n"
    
    # Format processing levels
    if "processing_levels" in taxonomy:
        result += "Processing Levels:\n"
        for key, value in taxonomy["processing_levels"].items():
            result += f"- {key.replace('_', ' ').title()}: {value}%\n"
    
    # Format knowledge domains
    if "knowledge_domains" in taxonomy:
        result += "Knowledge Domains:\n"
        for key, value in taxonomy["knowledge_domains"].items():
            result += f"- {key.replace('_', ' ').title()}: {value}%\n"
            
    return result.strip()

def get_all_concept_nodes() -> List[Dict]:
    """Get all concept nodes from the graph data."""
    all_nodes = []
    for category, data in graph_data.items():
        all_nodes.extend(data['nodes'])
    return all_nodes

async def generate_full_description(
    client: Any,
    provider: str,
    model: str,
    name: str,
    mode: str,
    brief_description: str = None,
    full_description: str = None,
    concepts: List[str] = None,
    competencies: Dict[str, int] = None,
    learning_goals: List[str] = None,
    taxonomy: Dict[str, Any] = None
) -> str:
    """Generate full description based on the mode and available inputs."""
    
    api_client = ApiClientFactory.create_client(provider, client)
    
    if mode == "full" and full_description:
        return full_description
    
    template_name = None
    template_vars = {"name": name}
    
    if mode == "brief":
        template_name = "full_description_from_brief"
        template_vars["brief_description"] = brief_description
    elif mode == "competencies":
        template_name = "full_description_from_competencies"
        template_vars.update({
            "brief_description": brief_description,
            "competencies_text": format_competencies_text(competencies)
        })
    elif mode == "learning-goals":
        template_name = "full_description_from_learning_goals"
        template_vars.update({
            "brief_description": brief_description,
            "goals_text": "\n".join([f"- {goal}" for goal in learning_goals])
        })
    elif mode == "combined":
        template_name = "full_description_from_combined"
        template_vars.update({
            "competencies_text": format_competencies_text(competencies) if competencies else "",
            "goals_text": format_learning_goals_text(learning_goals) if learning_goals else "",
            "brief_description": "Brief Description: " + brief_description if brief_description else "",
            "full_description": "Full Description Base: " + full_description if full_description else "",
            "taxonomy_text": format_taxonomy_text(taxonomy) if taxonomy else ""
        })
    elif mode == "taxonomy":
        template_name = "full_description_from_taxonomy"
        # Get processing levels and knowledge domains from the nested structure
        proc_levels = taxonomy.get("processing_levels", {})
        know_domains = taxonomy.get("knowledge_domains", {})
        
        # Flatten the taxonomy dictionary for template rendering
        template_vars.update({
            "brief_description": brief_description,
            "retrieval": proc_levels.get("retrieval", 0),
            "comprehension": proc_levels.get("comprehension", 0),
            "analysis": proc_levels.get("analysis", 0),
            "knowledge_utilization": proc_levels.get("knowledge_utilization", 0),
            "metacognition": proc_levels.get("metacognition", 0),
            "self_system_thinking": proc_levels.get("self_system_thinking", 0),
            "information_domain": know_domains.get("information", 40),
            "mental_procedures_domain": know_domains.get("mental_procedures", 40),
            "psychomotor_procedures_domain": know_domains.get("psychomotor_procedures", 20)
        })
    else:
        raise ValueError(f"Unsupported mode: {mode}")
    
    prompt = PromptTemplate.render(template_name, **template_vars)

    params = ApiClientFactory.create_params(
        provider,
        client=client,
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response = await api_client.chat_completion_request(params)
    return response.content

async def generate_activity_metadata(
    client: Any,
    provider: str,
    model: str,
    name: str,
    mode: str,
    description: str = None,
    brief_description: str = None,
    full_description: str = None,
    concepts: List[str] = None,
    competencies: Dict[str, int] = None,
    learning_goals: List[str] = None,
    taxonomy: Dict[str, Any] = None,
    is_brief_mode: bool = False
) -> Dict:
    """Generate complete activity metadata using AI"""
    
    try:
        # Generate full description if needed
        description = await generate_full_description(
            client=client,
            provider=provider,
            model=model,
            name=name,
            mode=mode,
            brief_description=brief_description,
            full_description=full_description,
            concepts=concepts,
            competencies=competencies,
            learning_goals=learning_goals,
            taxonomy=taxonomy
        )

        # Generate remaining metadata based on what we don't already have
        metadata = {
            "name": name,
            "description": description
        }
        
        # Get all available learning goals from the graph
        graph_goals_by_node = {}
        for category, data in graph_data.items():
            for node in data['nodes']:
                if 'learning_goals' in node['data']:
                    node_label = node['data']['label']
                    goals = [f"{goal['id']}: {goal['name']}" for goal in node['data']['learning_goals']]
                    graph_goals_by_node[node_label] = goals
        
        # Format graph goals for the prompt
        graph_goals_text = "\n".join([
            f"Learning Goals for {node_label}: {', '.join(goals)}"
            for node_label, goals in graph_goals_by_node.items()
        ])
        
        # If learning goals are not provided, generate them
        if not learning_goals:
            # Use the template to generate learning goals
            prompt = PromptTemplate.render(
                "get_learning_goals",
                name=name,
                description=description,
                graph_goals=graph_goals_text
            )
            
            messages = [{
                "role": "user",
                "content": prompt
            }]
            
            goals_data = await generate_with_retry(client, provider, model, messages)
            
            # Combine selected graph goals and additional goals with their assessment criteria
            learning_goals = []
            metadata["learning_goals"] = []
            for category, data in graph_data.items():
                for node in data['nodes']:
                    if 'learning_goals' in node['data']:
                        learning_goals.extend(node['data']['learning_goals'])
            for goal in goals_data.get('selected_goals', []):
                for lg in learning_goals:
                    if str(lg['id']) == str(goal):
                        metadata["learning_goals"].append({
                            'id': lg['id'],
                            'type': 'graph',
                            'name': lg['name'],
                            'learning_goal_id': lg['id']
                        })
        else:
            metadata["learning_goals"] = learning_goals
        
        # Generate competency scores if not provided
        if not competencies:
            messages = [{
                "role": "user",
                "content": get_competency_prompt(name, description, metadata["learning_goals"])
            }]
            metadata["competencies"] = await generate_with_retry(client, provider, model, messages)
        else:
            metadata["competencies"] = competencies
        
        # Generate taxonomy if not provided
        if not taxonomy:
            messages = [{
                "role": "user",
                "content": get_taxonomy_prompt(name, description, metadata["learning_goals"])
            }]
            taxonomy_data = await generate_with_retry(client, provider, model, messages)
            
            # Convert flat taxonomy to nested structure
            metadata["taxonomy"] = {
                "processing_levels": {
                    "retrieval": taxonomy_data.get("retrieval", 0),
                    "comprehension": taxonomy_data.get("comprehension", 0),
                    "analysis": taxonomy_data.get("analysis", 0),
                    "knowledge_utilization": taxonomy_data.get("knowledge_utilization", 0),
                    "metacognition": taxonomy_data.get("metacognition", 0),
                    "self_system_thinking": taxonomy_data.get("self_system_thinking", 0)
                },
                "knowledge_domains": {
                    "information": 40,
                    "mental_procedures": 40,
                    "psychomotor_procedures": 20
                }
            }
        else:
            # Use provided taxonomy with nested structure
            # Check if taxonomy already has nested structure
            if "processing_levels" in taxonomy:
                metadata["taxonomy"] = taxonomy
            else:
                # Convert flat structure to nested structure
                metadata["taxonomy"] = {
                    "processing_levels": {
                        "retrieval": taxonomy.get("retrieval", 0),
                        "comprehension": taxonomy.get("comprehension", 0),
                        "analysis": taxonomy.get("analysis", 0),
                        "knowledge_utilization": taxonomy.get("knowledge_utilization", 0),
                        "metacognition": taxonomy.get("metacognition", 0),
                        "self_system_thinking": taxonomy.get("self_system_thinking", 0)
                    },
                    "knowledge_domains": taxonomy.get("knowledge_domains", {
                        "information": 40,
                        "mental_procedures": 40,
                        "psychomotor_procedures": 20
                    })
                }
        return metadata
        
    except Exception as e:
        print(f"Error in activity generation: {str(e)}")
        raise 