from typing import Dict, List, Any, Tuple
import json
from .base import (
    ApiClientFactory,
    get_full_description_prompt,
    get_learning_goals_prompt,
    get_connected_concepts_prompt,
    get_competency_prompt,
    get_taxonomy_prompt
)

def validate_and_extract_json(response_text: str) -> Tuple[bool, Any]:
    """Validate and extract JSON from AI response."""
    try:
        response_text = response_text.strip()
        # Find the first { or [ and last } or ]
        start_brace = response_text.find('{')
        start_bracket = response_text.find('[')
        start = min(start_brace if start_brace != -1 else float('inf'),
                   start_bracket if start_bracket != -1 else float('inf'))
        
        end_brace = response_text.rfind('}')
        end_bracket = response_text.rfind(']')
        end = max(end_brace, end_bracket) + 1
        
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            data = json.loads(json_str)
            return True, data
        else:
            print("No JSON structure found in the response")
            return False, None
    except Exception as e:
        print(f"JSON validation failed: {str(e)}")
        return False, None

async def generate_with_retry(client: Any, provider: str, model: str, messages: List[Dict], max_attempts: int = 3) -> Any:
    """Generate response with retry logic and JSON validation."""
    api_client = ApiClientFactory.create_client(provider, client)
    
    for attempt in range(max_attempts):
        try:
            params = ApiClientFactory.create_params(
                provider,
                client=client,
                model=model,
                messages=messages
            )
            response = await api_client.chat_completion_request(params)
            is_valid, data = validate_and_extract_json(response.content)
            
            if is_valid:
                return data
            
            if attempt == max_attempts - 1:
                raise ValueError(f"Failed to generate valid JSON after {max_attempts} attempts")
                
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            continue
    
    raise ValueError(f"Failed to generate response after {max_attempts} attempts")

async def generate_activity_metadata(
    client: Any,
    provider: str,
    model: str,
    name: str,
    description: str,
    is_brief_mode: bool
) -> Dict:
    """Generate complete activity metadata using AI"""
    
    # If brief mode, first generate full description
    if is_brief_mode:
        api_client = ApiClientFactory.create_client(provider, client)
        params = ApiClientFactory.create_params(
            provider,
            client=client,
            model=model,
            messages=[{
                "role": "user",
                "content": get_full_description_prompt(name, description)
            }]
        )
        response = await api_client.chat_completion_request(params)
        description = response.content  # No JSON validation needed for description

    try:
        # Generate learning goals with retry
        messages = [{
            "role": "user",
            "content": get_learning_goals_prompt(name, description)
        }]
        learning_goals = await generate_with_retry(client, provider, model, messages)

        # Generate connected concepts with retry
        messages = [{
            "role": "user",
            "content": get_connected_concepts_prompt(name, description, learning_goals)
        }]
        connected_concepts = await generate_with_retry(client, provider, model, messages)

        # Generate competency scores with retry
        messages = [{
            "role": "user",
            "content": get_competency_prompt(name, description, learning_goals)
        }]
        competencies = await generate_with_retry(client, provider, model, messages)

        # Generate taxonomy classification with retry
        messages = [{
            "role": "user",
            "content": get_taxonomy_prompt(name, description, learning_goals)
        }]
        taxonomy = await generate_with_retry(client, provider, model, messages)

        # Return complete activity data
        return {
            "name": name,
            "description": description,
            "learning_goals": learning_goals,
            "connected_concepts": connected_concepts,
            "competencies": competencies,
            "taxonomy": taxonomy,
            "created_at": None  # This should be set by the main application
        }
    except Exception as e:
        print(f"Error in activity generation: {str(e)}")
        raise 