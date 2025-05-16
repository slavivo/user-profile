from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import Tuple, Dict, Any, Optional, List
import numpy as np
import openai
import google.generativeai as genai
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
from .template_handler import PromptTemplate

class RateLimiter:
    def __init__(self, interval):
        self.interval = interval
        self.next_available = 0
        self.lock = asyncio.Lock()
        
    async def acquire(self, index):
        async with self.lock:
            now = asyncio.get_event_loop().time()
            if now < self.next_available:
                wait_time = self.next_available - now
                await asyncio.sleep(wait_time)
            
            # Mark this token as used and set next available time
            self.next_available = max(self.next_available, asyncio.get_event_loop().time()) + self.interval

@dataclass
class NormalizedResponse:
    """Normalized response class to standardize responses across different APIs"""
    content: str
    model: str
    provider: str
    raw_response: Any = None
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None

def normalize_response(response: Any, provider: str) -> NormalizedResponse:
    """
    Normalize an API response to a standard format
    
    Parameters:
    response (Any): The raw API response
    provider (str): The API provider name ("openai", "gemini", or "deepseek")
    
    Returns:
    NormalizedResponse: Standardized response object
    """
    provider = provider.lower()
    
    # Gemini response normalization
    if provider == "gemini":
        try:
            content = response.text
            model = getattr(response, "model", "gemini")
            
            # Gemini might provide usage statistics differently
            usage = None
            if hasattr(response, "usage"):
                usage = {}
                if hasattr(response.usage, "prompt_tokens"):
                    usage["prompt_tokens"] = response.usage.prompt_tokens
                if hasattr(response.usage, "completion_tokens"):
                    usage["completion_tokens"] = response.usage.completion_tokens
                if hasattr(response.usage, "total_tokens"):
                    usage["total_tokens"] = response.usage.total_tokens
            
            finish_reason = None
            if hasattr(response, "finish_reason"):
                finish_reason = response.finish_reason
            
            return NormalizedResponse(
                content=content,
                model=model,
                provider="gemini",
                raw_response=response,
                usage=usage,
                finish_reason=finish_reason
            )
        except Exception as e:
            print(f"Error normalizing Gemini response: {e}")
            # Return minimal response
            return NormalizedResponse(
                content=getattr(response, "text", "Error processing response"),
                model="gemini",
                provider="gemini",
                raw_response=response
            )
    
    # DeepSeek and openAI response normalization
    elif provider == "deepseek" or provider == "openai":
        try:
            content = response.choices[0].message.content
            model = response.model
            
            usage = None
            if hasattr(response, "usage"):
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            finish_reason = None
            if hasattr(response.choices[0], "finish_reason"):
                finish_reason = response.choices[0].finish_reason
            
            return NormalizedResponse(
                content=content,
                model=model,
                provider="deepseek",
                raw_response=response,
                usage=usage,
                finish_reason=finish_reason
            )
        except Exception as e:
            print(f"Error normalizing DeepSeek response: {e}")
            # Return minimal response
            return NormalizedResponse(
                content=getattr(response, "content", "Error processing response"),
                model=getattr(response, "model", "deepseek-chat"),
                provider="deepseek",
                raw_response=response
            )
    
    # Handle unsupported providers
    else:
        raise ValueError(f"Unsupported API provider: {provider}")

# Base RequestParams class for common parameters
class BaseRequestParams:
    """Base class for request parameters across different API providers"""
    
    def __init__(
        self,
        provider,
        client,
        messages=None,
        model=None,
        max_tokens=300,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        seed=None,
        **kwargs # Accept and ignore additional params
    ):
        self.provider = provider
        self.client = client
        self.messages = messages
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.seed = seed
        self.additional_params = kwargs
    
    @abstractmethod
    def get_params(self) -> Dict:
        """Return parameters specific to the API provider"""
        pass


# OpenAI specific RequestParams
class OpenAIRequestParams(BaseRequestParams):
    """Parameters specific to OpenAI API"""
    
    def __init__(
        self,
        provider,
        client,
        messages=openai.NOT_GIVEN,
        tools=openai.NOT_GIVEN,
        tool_choice=openai.NOT_GIVEN,
        model='gpt-4o-2024-08-06',
        max_tokens=300,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        seed=openai.NOT_GIVEN,
        logprobs=openai.NOT_GIVEN,
        top_logprobs=openai.NOT_GIVEN,
        response_format=openai.NOT_GIVEN,
        **kwargs
    ):
        super().__init__(
            provider=provider,
            client=client,
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            **kwargs
        )
        self.tools = tools
        self.tool_choice = tool_choice
        self.logprobs = logprobs
        self.top_logprobs = top_logprobs
        self.response_format = response_format
    
    def get_params(self) -> Dict:
        """Return parameters for OpenAI API"""
        return {
            "messages": self.messages,
            "tools": self.tools,
            "tool_choice": self.tool_choice,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "seed": self.seed,
            "logprobs": self.logprobs,
            "top_logprobs": self.top_logprobs,
            "response_format": self.response_format,
        }


# Gemini specific RequestParams
class GeminiRequestParams(BaseRequestParams):
    """Parameters specific to Google Gemini API"""
    
    def __init__(
        self,
        provider,
        client,
        messages=None,
        model='gemini-2.0-flash',
        max_tokens=300,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        seed=None,
        **kwargs
    ):
        super().__init__(
            provider=provider,
            client=client,
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            **kwargs
        )
            
    def get_params(self) -> Dict:
        """Return parameters for Gemini API"""
        # Convert messages format from OpenAI to Gemini if needed
        content = self._convert_messages_to_gemini_format(self.messages)

        generation_config = genai.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        
        return {
            "contents": content,
            "generation_config": generation_config,
        }
    
    def _convert_messages_to_gemini_format(self, messages):
        if not messages:
            return []

        gemini_messages = []
        system_message = None

        # Extract system message if present
        for message in messages:
            if message.get("role") == "system":
                system_message = message.get("content", "")
                break
            
        # Process conversation messages
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")

            # Skip system messages as we'll handle them separately
            if role == "system":
                continue
            
            # Map OpenAI roles to Gemini roles
            gemini_role = "user" if role == "user" else "model"

            # If this is the first user message and we have a system message,
            # prepend system message to user content
            if role == "user" and system_message and not gemini_messages:
                content = system_message + "\n\n" + content
                system_message = None  # Clear to avoid adding again

            # Add message to the conversation
            gemini_messages.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })

        return gemini_messages


# DeepSeek specific RequestParams
class DeepSeekRequestParams(BaseRequestParams):
    """Parameters specific to DeepSeek API"""
    
    def __init__(
        self,
        provider,
        client,
        messages=openai.NOT_GIVEN,
        model='deepseek-chat',
        max_tokens=300,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        **kwargs
    ):
        super().__init__(
            provider=provider,
            client=client,
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            **kwargs
        )
    
    def get_params(self) -> Dict:
        """Return parameters for DeepSeek API"""
        return {
            "messages": self.messages,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }


# API Client abstract base class
class ApiClient(ABC):
    """Abstract base class for API clients"""
    
    @abstractmethod
    async def chat_completion_request(self, params):
        """Send a chat completion request to the API"""
        pass


# OpenAI API Client
class OpenAIClient(ApiClient):
    """Client for OpenAI API"""

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.provider = "openai"
    
    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    async def chat_completion_request(self, params: OpenAIRequestParams):
        """Send a chat completion request to OpenAI API"""
        try:
            response = await params.client.beta.chat.completions.parse(**params.get_params())
            return normalize_response(response, params.provider)
        except Exception as e:
            print("Unable to generate OpenAI ChatCompletion response")
            print(f"Exception: {e}")
            raise e


# Gemini API Client
class GeminiClient(ApiClient):
    """Client for Google Gemini API"""

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.provider = "gemini"
    
    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    async def chat_completion_request(self, params: GeminiRequestParams):
        """Send a chat completion request to Gemini API"""
        try:
            response = await params.client.generate_content_async(**params.get_params())
            return normalize_response(response, params.provider)
        except Exception as e:
            print("Unable to generate Gemini API response")
            print(f"Exception: {e}")
            raise e


# DeepSeek API Client
class DeepSeekClient(ApiClient):
    """Client for DeepSeek API"""

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.provider = "deepseek"
    
    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    async def chat_completion_request(self, params: DeepSeekRequestParams):
        """Send a chat completion request to DeepSeek API"""
        try:
            response = await params.client.beta.chat.completions.parse(**params.get_params())
            return normalize_response(response, params.provider)
        except Exception as e:
            print("Unable to generate DeepSeek API response")
            print(f"Exception: {e}")
            raise e


# Factory to create appropriate client based on API provider
class ApiClientFactory:
    """Factory to create API clients based on provider"""
    
    @staticmethod
    def create_client(provider: str, client) -> ApiClient:
        """Create an API client based on provider name"""
        provider = provider.lower()
        if provider == "openai":
            return OpenAIClient(client)
        elif provider == "gemini":
            return GeminiClient(client)
        elif provider == "deepseek":
            return DeepSeekClient(client)
        else:
            raise ValueError(f"Unsupported API provider: {provider}")

    @staticmethod
    def create_params(provider: str, **kwargs) -> BaseRequestParams:
        """Create request parameters based on provider name"""
        provider = provider.lower()
        if provider == "openai":
            return OpenAIRequestParams(provider, **kwargs)
        elif provider == "gemini":
            return GeminiRequestParams(provider, **kwargs)
        elif provider == "deepseek":
            return DeepSeekRequestParams(provider, **kwargs)
        else:
            raise ValueError(f"Unsupported API provider: {provider}")

def print_logprobs(logprobs):
    """
    This function prints the logprobs

    Parameters:
    logprobs (list): List of logprobs
    """

    categories_probs = []
    for logprob in logprobs:
        token = logprob.token.strip().lower()
        for i, (category, prob) in enumerate(categories_probs):
            if len(category) > len(token):
                if (category == token) or (
                    category.startswith(token) and len(token) >= 2
                ):
                    categories_probs[i] = (category, prob + np.exp(logprob.logprob))
                    break
            else:
                if (category == token) or (
                    token.startswith(category) and len(category) >= 2
                ):
                    categories_probs[i] = (token, prob + np.exp(logprob.logprob))
                    break
        else:
            categories_probs.append((token, np.exp(logprob.logprob)))

    for category, prob in categories_probs:
        print(f"Category: {category}, linear probability: {np.round(prob*100,2)}")

def get_initial_graph_prompt(concept):
    return PromptTemplate.render('initial_graph', concept=concept)

def get_reformatting_prompt(concept, initial_response):
    return PromptTemplate.render('reformatting', concept=concept, initial_response=initial_response)

def is_valid_graph_format(response_text):
    """Validate if the response has the correct graph format"""
    try:
        import json
        
        # Basic input validation
        if not response_text:
            print("Error: Empty response")
            return False
            
        # Preprocessing
        # Try to extract JSON if there's additional text
        try:
            response_text = response_text.strip()
            # Find the first { and last }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                response_text = response_text[start:end]
            else:
                print("No JSON-like structure found in the response")
                return False
        except Exception as e:
            print(f"Preprocessing failed: {str(e)}")
        
        try:
            data = json.loads(response_text)
            print("JSON parsed successfully")
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}")
            print("Failed text:", repr(response_text))
            return False
        
        # Check basic structure
        if not isinstance(data, dict):
            print("Failed: data is not a dictionary")
            return False
        if 'nodes' not in data or 'edges' not in data:
            print("Failed: missing 'nodes' or 'edges' keys")
            return False
        if not isinstance(data['nodes'], list) or not isinstance(data['edges'], list):
            print("Failed: 'nodes' or 'edges' is not a list")
            return False
                        
        # Check nodes format
        for i, node in enumerate(data['nodes']):
            if not isinstance(node, dict):
                print(f"Failed: node {i} is not a dictionary")
                return False
            if 'id' not in node or 'label' not in node or 'progress' not in node:
                print(f"Failed: node {i} missing required fields")
                return False
            if not isinstance(node['id'], str) or not isinstance(node['label'], str):
                print(f"Failed: node {i} has invalid id or label type")
                return False
            
            # Convert progress to float if it's a string
            if isinstance(node['progress'], str):
                try:
                    node['progress'] = float(node['progress'])
                except ValueError:
                    print(f"Failed: node {i} progress cannot be converted to number")
                    return False
            
            if not isinstance(node['progress'], (int, float)):
                print(f"Failed: node {i} progress is not a number")
                return False
            if node['progress'] < 0 or node['progress'] > 100:
                print(f"Failed: node {i} progress {node['progress']} is out of range")
                return False
        
        # Check edges format
        for i, edge in enumerate(data['edges']):
            if not isinstance(edge, dict):
                print(f"Failed: edge {i} is not a dictionary")
                return False
            if 'source' not in edge or 'target' not in edge:
                print(f"Failed: edge {i} missing source or target")
                return False
            if not isinstance(edge['source'], str) or not isinstance(edge['target'], str):
                print(f"Failed: edge {i} has invalid source or target type")
                return False
                
        return True, response_text
    except Exception as e:
        print(f"Validation failed with exception: {str(e)}")
        print("Response text:", repr(response_text))
        return False
    
def get_full_description_prompt(name: str, brief_description: str) -> str:
    return PromptTemplate.render('full_description', name=name, brief_description=brief_description)

def get_learning_goals_prompt(name: str, description: str) -> str:
    return PromptTemplate.render('learning_goals', name=name, description=description)

def get_connected_concepts_prompt(name: str, description: str, learning_goals: List[str]) -> str:
    goals_text = "\n".join([f"- {goal}" for goal in learning_goals])
    return PromptTemplate.render('connected_concepts', name=name, description=description, goals_text=goals_text)

def get_competency_prompt(name: str, description: str, learning_goals: List[str]) -> str:
    goals_text = "\n".join([f"- {goal}" for goal in learning_goals])
    return PromptTemplate.render('competency', name=name, description=description, goals_text=goals_text)

def get_taxonomy_prompt(name: str, description: str, learning_goals: List[str]) -> str:
    goals_text = "\n".join([f"- {goal}" for goal in learning_goals])
    return PromptTemplate.render('taxonomy', name=name, description=description, goals_text=goals_text)