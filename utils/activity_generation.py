from typing import Dict, List, Any, Tuple
import json
import time
from .base import (
    ApiClientFactory,
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

def format_ovu_areas(graph_data: Dict) -> str:
    """Format OVU areas and their outcomes into a readable text format."""
    print("\n=== Formatting OVU Areas ===")
    result = []
    for category, data in graph_data.items():
        print(f"Processing category: {category}")
        if "ovu" in data:
            for ovu in data["ovu"]:
                print(f"Processing OVU: {ovu['id']}")
                result.append(f"Area ID: {ovu['id']}\nOutcome: {ovu['outcome']}\n")
    formatted_result = "\n".join(result)
    print(f"Formatted {len(result)} OVU areas across all categories")
    return formatted_result

def format_topics(graph_data: Dict, selected_ovu: List[str]) -> Tuple[str, str]:
    """Format selected OVU info and available topics into readable text formats."""
    print("\n=== Formatting Topics ===")
    print(f"Selected OVU areas: {selected_ovu}")
    
    # First, find which categories our selected OVUs belong to
    selected_categories = set()
    for category, data in graph_data.items():
        if "ovu" in data:
            for ovu in data["ovu"]:
                if ovu["id"] in selected_ovu:
                    print(f"Found OVU {ovu['id']} in category: {category}")
                    selected_categories.add(category)
    
    print(f"Selected categories: {selected_categories}")
    
    # Format selected OVU info
    ovu_info = []
    for category, data in graph_data.items():
        if "ovu" in data:
            for ovu in data["ovu"]:
                if ovu["id"] in selected_ovu:
                    print(f"Including OVU info for: {ovu['id']} from category {category}")
                    ovu_info.append(f"Area ID: {ovu['id']}\nOutcome: {ovu['outcome']}")
    
    selected_ovu_info = "\n".join(ovu_info)
    
    # Format available topics
    topics = []
    total_topics = 0
    
    for category, data in graph_data.items():
        if category in selected_categories and "nodes" in data:
            print(f"\nGetting topics from category: {category}")
            for node in data["nodes"]:
                # The following code is commented out as it might be useful in the future when topics have direct OVU connections
                # if any(ovu in node["data"]["ovu_connections"] for ovu in selected_ovu):
                total_topics += 1
                print(f"Including topic: {node['data']['id']} ({node['data']['label']}) from category {category}")
                topics.append(f"Topic ID: {node['data']['id']}\nLabel: {node['data']['label']}\nCategory: {category}")
    
    available_topics = "\n".join(topics)
    print(f"Found {total_topics} topics in selected categories: {', '.join(selected_categories)}")
    
    return selected_ovu_info, available_topics

def format_learning_goals(graph_data: Dict, selected_topics: List[str]) -> str:
    """Format learning goals from selected topics into a readable text format."""
    print("\n=== Formatting Learning Goals ===")
    print(f"Selected topics: {selected_topics}")
    
    goals = []
    total_goals = 0
    for category, data in graph_data.items():
        print(f"\nChecking category: {category}")
        if "nodes" in data:
            for node in data["nodes"]:
                if node["data"]["id"] in selected_topics and "learning_goals" in node["data"]:
                    print(f"\nProcessing goals for topic: {node['data']['label']} in category {category}")
                    goals.append(f"Topic: {node['data']['label']} (Category: {category})")
                    for goal in node["data"]["learning_goals"]:
                        total_goals += 1
                        print(f"  Found goal: {goal['id']} - {goal['name']}")
                        goals.append(f"  Goal ID: {goal['id']}\n  Name: {goal['name']}\n  Grade: {goal['grade']}")
    
    formatted_result = "\n".join(goals)
    print(f"Total learning goals found: {total_goals} across {len(selected_topics)} topics")
    return formatted_result

async def generate_learning_goals_metadata(
    client: Any,
    provider: str,
    model: str,
    name: str,
    description: str,
    existing_learning_goals: List[str] = None
) -> List[Dict]:
    """Generate learning goals metadata using a three-step approach."""
    print("\n====== Starting Learning Goals Generation ======")
    print(f"Activity: {name}")
    print(f"Model: {model}")
    
    if existing_learning_goals:
        print("Using existing learning goals, skipping generation")
        return existing_learning_goals

    try:
        # Step 1: Select OVU areas
        print("\n=== Step 1: OVU Selection ===")
        ovu_areas = format_ovu_areas(graph_data)
        prompt = PromptTemplate.render(
            "select_ovu_areas",
            name=name,
            description=description,
            ovu_areas=ovu_areas
        )
        
        messages = [{"role": "user", "content": prompt}]
        ovu_data = await generate_with_retry(client, provider, model, messages)
        selected_ovu = ovu_data["selected_ovu"]
        print(f"Selected OVU areas: {selected_ovu}")
        
        # Step 2: Select topics
        print("\n=== Step 2: Topic Selection ===")
        selected_ovu_info, available_topics = format_topics(graph_data, selected_ovu)
        prompt = PromptTemplate.render(
            "select_topics",
            name=name,
            description=description,
            selected_ovu_info=selected_ovu_info,
            available_topics=available_topics
        )
        
        messages = [{"role": "user", "content": prompt}]
        topics_data = await generate_with_retry(client, provider, model, messages)
        selected_topics = topics_data["selected_topics"]
        print(f"Selected topics: {selected_topics}")
        
        # Step 3: Select learning goals
        print("\n=== Step 3: Learning Goals Selection ===")
        available_goals = format_learning_goals(graph_data, selected_topics)
        prompt = PromptTemplate.render(
            "select_learning_goals",
            name=name,
            description=description,
            available_goals=available_goals
        )
        
        messages = [{"role": "user", "content": prompt}]
        goals_data = await generate_with_retry(client, provider, model, messages)
        print(f"Selected learning goals: {goals_data['selected_goals']}")
        
        # Format the final output
        print("\n=== Formatting Final Output ===")
        metadata_goals = []
        
        # Process selected goals from the graph
        for category, data in graph_data.items():
            print(f"Checking category: {category}")
            if "nodes" in data:
                for node in data["nodes"]:
                    if node["data"]["id"] in selected_topics and "learning_goals" in node["data"]:
                        for lg in node["data"]["learning_goals"]:
                            if lg["id"] in goals_data["selected_goals"]:
                                print(f"Including goal {lg['id']} from topic {node['data']['label']} in category {category}")
                                metadata_goals.append({
                                    'id': lg['id'],
                                    'type': 'graph',
                                    'name': lg['name'],
                                    'learning_goal_id': lg['id']
                                })
        
        # Process additional generated goals
        if "additional_goals" in goals_data and goals_data["additional_goals"]:
            print("\nProcessing additional generated goals:")
            for i, goal in enumerate(goals_data["additional_goals"]):
                goal_id = f"generated_goal_{i+1}"
                print(f"Including generated goal: {goal}")
                metadata_goals.append({
                    'id': goal_id,
                    'type': 'external',
                    'name': goal
                })
        
        print(f"\nFinal output contains {len(metadata_goals)} learning goals "
              f"({sum(1 for g in metadata_goals if g['type'] == 'graph')} from graph, "
              f"{sum(1 for g in metadata_goals if g['type'] == 'external')} generated)")
        return metadata_goals
        
    except Exception as e:
        print(f"\n!!! Error in learning goals generation: {str(e)}")
        raise

async def generate_competencies_metadata(
    client: Any,
    provider: str,
    model: str,
    name: str,
    description: str,
    learning_goals: List[Dict],
    existing_competencies: Dict[str, int] = None
) -> Dict[str, int]:
    """Generate competencies metadata if not provided."""
    if existing_competencies:
        return existing_competencies

    messages = [{
        "role": "user",
        "content": get_competency_prompt(name, description, learning_goals)
    }]
    return await generate_with_retry(client, provider, model, messages)

async def generate_taxonomy_metadata(
    client: Any,
    provider: str,
    model: str,
    name: str,
    description: str,
    learning_goals: List[Dict],
    existing_taxonomy: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate taxonomy metadata if not provided."""
    if existing_taxonomy:
        # Check if taxonomy already has nested structure
        if "processing_levels" in existing_taxonomy:
            return existing_taxonomy
        # Convert flat structure to nested structure
        return {
            "processing_levels": {
                "retrieval": existing_taxonomy.get("retrieval", 0),
                "comprehension": existing_taxonomy.get("comprehension", 0),
                "analysis": existing_taxonomy.get("analysis", 0),
                "knowledge_utilization": existing_taxonomy.get("knowledge_utilization", 0),
                "metacognition": existing_taxonomy.get("metacognition", 0),
                "self_system_thinking": existing_taxonomy.get("self_system_thinking", 0)
            },
            "knowledge_domains": existing_taxonomy.get("knowledge_domains", {
                "information": 40,
                "mental_procedures": 40,
                "psychomotor_procedures": 20
            })
        }

    messages = [{
        "role": "user",
        "content": get_taxonomy_prompt(name, description, learning_goals)
    }]
    taxonomy_data = await generate_with_retry(client, provider, model, messages)
    
    return {
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

        # Initialize metadata with basic information
        metadata = {
            "name": name,
            "description": description
        }
        
        # Generate learning goals metadata
        metadata["learning_goals"] = await generate_learning_goals_metadata(
            client=client,
            provider=provider,
            model=model,
            name=name,
            description=description,
            existing_learning_goals=learning_goals
        )
        
        # Generate competency scores
        metadata["competencies"] = await generate_competencies_metadata(
            client=client,
            provider=provider,
            model=model,
            name=name,
            description=description,
            learning_goals=metadata["learning_goals"],
            existing_competencies=competencies
        )
        
        # Generate taxonomy
        metadata["taxonomy"] = await generate_taxonomy_metadata(
            client=client,
            provider=provider,
            model=model,
            name=name,
            description=description,
            learning_goals=metadata["learning_goals"],
            existing_taxonomy=taxonomy
        )
        
        return metadata
        
    except Exception as e:
        print(f"Error in activity generation: {str(e)}")
        raise 