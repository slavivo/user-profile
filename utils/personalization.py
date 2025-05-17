import random
from typing import Dict, List, Tuple
from student_data import student_data
from graph_data import graph_data

def get_aggregated_concept_scores(student_data: Dict) -> Dict[str, float]:
    """
    Aggregate concept scores across all activities to get current mastery levels.
    
    Args:
        student_data (Dict): Student data containing activities and their concept scores
        
    Returns:
        Dict[str, float]: Dictionary mapping concept IDs to their current scores
    """
    concept_scores = {}
    activities = student_data.get('activities', [])
    
    # Collect all scores
    for activity in activities:
        activity_scores = activity.get('student_performance', {}).get('concept_scores', {})
        for concept_id, data in activity_scores.items():
            if concept_id not in concept_scores:
                concept_scores[concept_id] = []
            concept_scores[concept_id].append(data.get('score', 0))
    
    # Average the scores for each concept
    return {
        concept_id: sum(scores) / len(scores)
        for concept_id, scores in concept_scores.items()
    }

def get_aggregated_competency_scores(student_data: Dict) -> Dict[str, float]:
    """
    Aggregate competency scores across all activities to get current levels.
    
    Args:
        student_data (Dict): Student data containing activities and their competency scores
        
    Returns:
        Dict[str, float]: Dictionary mapping competency names to their current scores
    """
    competency_scores = {}
    activities = student_data.get('activities', [])
    
    # Collect all scores
    for activity in activities:
        activity_scores = activity.get('competency_scores', {})
        for comp_name, score in activity_scores.items():
            if comp_name not in competency_scores:
                competency_scores[comp_name] = []
            competency_scores[comp_name].append(score)
    
    # Average the scores for each competency
    return {
        comp_name: sum(scores) / len(scores)
        for comp_name, scores in competency_scores.items()
    }

def get_concept_candidates(focus_type: str, student_data: Dict) -> List[str]:
    """
    Get candidate concepts based on the focus type.
    
    Args:
        focus_type (str): One of 'polish', 'discover', or 'broaden'
        student_data (Dict): Student data containing concept scores
        
    Returns:
        List[str]: List of concept IDs matching the focus criteria
    """
    concept_scores = get_aggregated_concept_scores(student_data)
    candidates = []
    
    if focus_type == 'polish':
        # Get concepts with scores between 1-9
        candidates = [cid for cid, score in concept_scores.items() 
                     if 1 <= score < 9]
    
    elif focus_type == 'discover':
        # Get all known concepts (those with scores)
        known_concepts = set(concept_scores.keys())
        # Get all connected concepts from the graph data
        connected_concepts = set()
        
        for category, data in graph_data.items():
            for edge in data['edges']:
                if edge['source'] in known_concepts:
                    connected_concepts.add(edge['target'])
                if edge['target'] in known_concepts:
                    connected_concepts.add(edge['source'])
        
        # Filter for concepts with score 0 or not yet scored
        candidates = [cid for cid in connected_concepts 
                     if cid not in concept_scores or concept_scores.get(cid, 0) == 0]
    
    elif focus_type == 'broaden':
        # Get concepts with scores 9-10
        candidates = [cid for cid, score in concept_scores.items() 
                     if score >= 9]
    
    return candidates

def get_competency_candidates(focus_type: str, student_data: Dict) -> List[str]:
    """
    Get candidate competencies based on the focus type.
    
    Args:
        focus_type (str): Either 'strong' or 'weak'
        student_data (Dict): Student data containing competency scores
        
    Returns:
        List[str]: List of competency names matching the focus criteria
    """
    competency_scores = get_aggregated_competency_scores(student_data)
    
    # Handle empty scores
    if not competency_scores:
        # Return default competencies if no scores available
        return ['problem_solving', 'critical_thinking', 'analytical_skills']
    
    # Sort competencies by score
    sorted_competencies = sorted(
        competency_scores.items(),
        key=lambda x: x[1],
        reverse=(focus_type == 'strong')
    )
    
    # Get top 3 strongest or weakest competencies
    # If we have fewer than 3, return all of them
    return [comp for comp, _ in sorted_competencies[:3]]

def select_focus_elements(concept_focus: str, competency_focus: str) -> Tuple[str, str]:
    """
    Select one concept and one competency based on the focus types.
    
    Args:
        concept_focus (str): Type of concept focus ('polish', 'discover', or 'broaden')
        competency_focus (str): Type of competency focus ('strong' or 'weak')
        
    Returns:
        Tuple[str, str]: Selected concept ID and competency name
    """
    # Get candidate concepts
    concept_candidates = get_concept_candidates(concept_focus, student_data)
    if not concept_candidates:
        raise ValueError(f"No concepts found matching the {concept_focus} criteria")
    
    # Get candidate competencies
    competency_candidates = get_competency_candidates(competency_focus, student_data)
    if not competency_candidates:
        raise ValueError(f"No competencies found matching the {competency_focus} criteria")
    
    # Randomly select one concept and one competency
    selected_concept = random.choice(concept_candidates)
    selected_competency = random.choice(competency_candidates)
    
    return selected_concept, selected_competency

def prepare_personalized_activity_params(concept_focus: str, competency_focus: str) -> Dict:
    """
    Prepare parameters for activity generation based on personalization choices.
    
    Args:
        concept_focus (str): Type of concept focus ('polish', 'discover', or 'broaden')
        competency_focus (str): Type of competency focus ('strong' or 'weak')
        
    Returns:
        Dict: Parameters for activity generation
    """
    # Select focus elements
    concept_id, competency = select_focus_elements(concept_focus, competency_focus)
    print(f"Concept ID: {concept_id}, Competency: {competency}")
    # Get concept name from graph data
    concept_name = None
    for category, data in graph_data.items():
        for node in data['nodes']:
            if node['data']['id'] == concept_id:
                concept_name = node['data']['label']
                break
        if concept_name:
            break
    
    if not concept_name:
        concept_name = concept_id
    
    # Prepare activity parameters
    activity_params = {
        "name": f"Personalized Activity: {concept_name}",
        "mode": "combined",
        "concepts": [concept_id],
        "competencies": {
            "problem_solving": 50,
            "critical_thinking": 50,
            "analytical_skills": 50,
            "technical_proficiency": 50,
            "communication": 50,
            "collaboration": 50
        }
    }
    
    # Set the selected competency to a higher value (80%)
    normalized_competency = competency.lower().replace(' ', '_')
    if normalized_competency == 'analysis':
        normalized_competency = 'analytical_skills'
    activity_params["competencies"][normalized_competency] = 80
    
    # Add a brief description based on the focus types
    focus_descriptions = {
        'polish': 'improving understanding of partially mastered concepts',
        'discover': 'exploring new connected concepts',
        'broaden': 'deepening knowledge of well-understood concepts'
    }
    
    competency_descriptions = {
        'strong': 'leveraging strong competencies',
        'weak': 'developing weaker competencies'
    }
    
    activity_params["brief_description"] = (
        f"A personalized activity focused on {focus_descriptions[concept_focus]} "
        f"while {competency_descriptions[competency_focus]}. "
        f"Primary concept: {concept_name}. "
        f"Key competency: {competency}."
    )
    
    return activity_params 