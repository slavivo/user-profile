from typing import Dict, List, Any
from utils.base import generate_with_retry, ApiClientFactory
from utils.template_handler import PromptTemplate
from utils.activity_generation import generate_activity_metadata
import asyncio
import os
import google.generativeai as genai
import json
import configparser
from datetime import datetime
import uuid
import pprint
from student_data import student_data

async def decompose_methodology(
    client: Any,
    provider: str,
    model: str,
    methodology_description: str,
    max_attempts: int = 3
) -> List[Dict[str, Any]]:
    template_vars = {"methodology_description": methodology_description}
    prompt = PromptTemplate.render('methodology_decompose', **template_vars)

    messages = [{"role": "user", "content": prompt}]

    response_data = await generate_with_retry(
        client=client,
        provider=provider,
        model=model,
        messages=messages,
        max_attempts=max_attempts
    )

    if not isinstance(response_data, list):
        raise ValueError(
            f"Expected a list of activities, but got {type(response_data)}. Response: {response_data}"
        )

    validated_activities = []
    for i, activity in enumerate(response_data):
        if not isinstance(activity, dict):
            raise ValueError(
                f"Activity at index {i} is not a dictionary. Response: {response_data}"
            )
        if "full_description" not in activity or not isinstance(activity["full_description"], str):
            raise ValueError(
                f"Activity at index {i} is missing 'full_description' or it's not a string. Response: {response_data}"
            )
        if "questions_asked" not in activity or not isinstance(activity["questions_asked"], list):
            activity["questions_asked"] = activity.get("questions_asked", [])
        for q_idx, question in enumerate(activity["questions_asked"]):
            if not isinstance(question, str):
                raise ValueError(
                    f"Question at index {q_idx} for activity {i} is not a string. Response: {response_data}"
                )
        validated_activities.append(activity)

    return validated_activities