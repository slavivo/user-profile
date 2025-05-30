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

def format_activity_for_student_data(activity_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the raw activity metadata from generate_activity_metadata into the structure
    expected by student_data.py activities list.
    """
    if not activity_metadata:
        print("Warning: Received empty activity_metadata to format.")
        return None

    new_activity_id = f"ACT_DECOMP_{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:4]}"

    formatted_competency_scores = {}
    raw_competencies = activity_metadata.get('competencies', {})
    if isinstance(raw_competencies, dict):
        for key, value in raw_competencies.items():
            formatted_key = ' '.join(word.capitalize() for word in key.split('_'))
            try:
                formatted_competency_scores[formatted_key] = float(value) / 10.0
            except (ValueError, TypeError):
                print(f"Warning: Could not convert competency score for {key}: {value} to float. Setting to 0.0")
                formatted_competency_scores[formatted_key] = 0.0
    else:
        print(f"Warning: Competencies data is not a dictionary: {raw_competencies}. Skipping competency formatting.")

    formatted_taxonomy = {"processing_levels": [], "knowledge_domains": []}
    raw_taxonomy = activity_metadata.get('taxonomy', {})
    if isinstance(raw_taxonomy, dict):
        for level_key, level_value in raw_taxonomy.get("processing_levels", {}).items():
            try:
                formatted_taxonomy["processing_levels"].append({
                    "level": ' '.join(word.capitalize() for word in level_key.split('_')),
                    "weight": float(level_value) / 100.0
                })
            except (ValueError, TypeError):
                 print(f"Warning: Could not convert taxonomy processing level for {level_key}: {level_value}. Skipping.")

        for domain_key, domain_value in raw_taxonomy.get("knowledge_domains", {}).items():
            try:
                formatted_taxonomy["knowledge_domains"].append({
                    "domain": ' '.join(word.capitalize() for word in domain_key.split('_')),
                    "weight": float(domain_value) / 100.0
                })
            except (ValueError, TypeError):
                print(f"Warning: Could not convert taxonomy knowledge domain for {domain_key}: {domain_value}. Skipping.")
    else:
        print(f"Warning: Taxonomy data is not a dictionary: {raw_taxonomy}. Skipping taxonomy formatting.")

    student_performance = {"learning_goals": {}}
    raw_learning_goals = activity_metadata.get('learning_goals', [])
    if isinstance(raw_learning_goals, list):
        for goal in raw_learning_goals:
            if isinstance(goal, dict):
                goal_id = goal.get('id')
                goal_name = goal.get('name')
                if goal_id and goal_name:
                    student_performance['learning_goals'][goal_id] = {'name': goal_name, 'mastered': False}
                else:
                    print(f"Warning: Skipping learning goal due to missing id or name: {goal}")
            else:
                print(f"Warning: Learning goal item is not a dictionary: {goal}")
    else:
        print(f"Warning: Learning goals data is not a list: {raw_learning_goals}. Skipping learning goal performance setup.")

    formatted_activity = {
        'id': new_activity_id,
        'name': activity_metadata.get('name', "Unnamed Decomposed Activity"),
        'description': activity_metadata.get('description', "No description provided."),
        'learning_goals': raw_learning_goals,
        'competency_scores': formatted_competency_scores,
        'taxonomy': formatted_taxonomy,
        'student_performance': student_performance
    }
    return formatted_activity

def update_student_data_file(new_activities: List[Dict[str, Any]]):
    if not new_activities:
        print("No new activities generated to update student_data.py.")
        return

    try:
        student_data['activities'].extend(new_activities)
        student_data_filepath = 'student_data.py'
        with open(student_data_filepath, 'w', encoding='utf-8') as f:
            f.write("# student_data.py - This file is auto-generated and will be overwritten.\n")
            f.write("# flake8: noqa\n")
            f.write("# pylint: disable=all\n")
            f.write("student_data = ")
            f.write(pprint.pformat(student_data, indent=4, width=120, sort_dicts=False))
            f.write("\n")
        print(f"Successfully updated {student_data_filepath} with {len(new_activities)} new activities.")
    except FileNotFoundError:
        print(f"Error: {student_data_filepath} not found for updating.")
    except Exception as e:
        print(f"Error updating {student_data_filepath}: {e}")

async def main() -> List[Dict[str, Any]]:
    """
    Main function to read methodology descriptions, decompose, generate metadata,
    and return formatted activities.
    """
    api_key = "AIzaSyBm58TYTkwmnk0M0A0p66gfdagTBtOhYw4"
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")
        return []

    try:
        gemini_model_instance = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"Error initializing Gemini model 'gemini-2.0-flash': {e}")
        return []

    provider = "gemini"
    model_name_for_logging_or_params = 'gemini-2.0-flash'

    data_dir_path = "data"
    output_dir_path = os.path.join(data_dir_path, "decomposed")
    metadata_output_dir_path = os.path.join(output_dir_path, "metadata")

    all_new_formatted_activities_for_student_data = []

    for path in [output_dir_path, metadata_output_dir_path]:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"Created output directory: {path}")
            except OSError as e:
                print(f"Error creating output directory {path}: {e}")
                return []
        elif not os.path.isdir(path):
            print(f"Error: {path} exists but is not a directory.")
            return []

    if not os.path.isdir(data_dir_path):
        print(f"Error: Data directory '{data_dir_path}' not found.")
        return []

    print(f"Processing .txt files from directory: {data_dir_path}\n")

    for filename in os.listdir(data_dir_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(data_dir_path, filename)
            print(f"--- Processing file: {filename} ---")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    methodology_description = f.read()
                
                if not methodology_description.strip():
                    print("File is empty. Skipping.")
                    print(f"--- End of processing for file: {filename} ---\n")
                    continue
                
                decomposed_activities = await decompose_methodology(
                    client=gemini_model_instance,
                    provider=provider,
                    model=model_name_for_logging_or_params,
                    methodology_description=methodology_description
                )
                
                base_filename, _ = os.path.splitext(filename)
                output_filename = f"{base_filename}.json"
                output_file_path = os.path.join(output_dir_path, output_filename)
                try:
                    with open(output_file_path, 'w', encoding='utf-8') as outfile:
                        json.dump(decomposed_activities, outfile, indent=2, ensure_ascii=False)
                    print(f"Successfully saved decomposed activities to: {output_file_path}")
                except IOError as e:
                    print(f"Error saving JSON to file {output_file_path}: {e}")
                
                print("\n--- Generating metadata for each activity ---")
                current_file_activities_metadata = [] 

                for idx, single_activity_data in enumerate(decomposed_activities):
                    activity_full_desc = single_activity_data.get("full_description")
                    activity_name_suffix = single_activity_data.get("name", single_activity_data.get("title", f"Activity {idx + 1}"))

                    if not activity_full_desc:
                        print(f"Skipping metadata generation for {activity_name_suffix} due to missing full_description.")
                        continue

                    activity_meta_name = f"{base_filename} - {activity_name_suffix}"
                    print(f"Generating metadata for: {activity_meta_name}")

                    try:
                        activity_metadata = await generate_activity_metadata(
                            client=gemini_model_instance,
                            provider=provider,
                            model=model_name_for_logging_or_params,
                            name=activity_meta_name,
                            mode="full",
                            full_description=activity_full_desc
                        )
                        current_file_activities_metadata.append(activity_metadata)

                        metadata_filename = f"{base_filename}_{activity_name_suffix.replace(' ', '_').replace('-', '_').lower()}_metadata.json"
                        metadata_file_path = os.path.join(metadata_output_dir_path, metadata_filename)
                        try:
                            with open(metadata_file_path, 'w', encoding='utf-8') as meta_outfile:
                                json.dump(activity_metadata, meta_outfile, indent=2, ensure_ascii=False)
                            print(f"Successfully saved metadata to: {metadata_file_path}")
                        except IOError as e:
                            print(f"Error saving metadata JSON to file {metadata_file_path}: {e}")

                    except Exception as e:
                        print(f"Error generating metadata for {activity_meta_name}: {e}")
                
                print("--- Finished generating metadata for all activities in this file ---")

                for activity_meta_obj in current_file_activities_metadata:
                    formatted_activity = format_activity_for_student_data(activity_meta_obj)
                    if formatted_activity:
                        all_new_formatted_activities_for_student_data.append(formatted_activity)

            except Exception as e:
                print(f"Error processing file {filename}: {e}")
            finally:
                print(f"--- End of processing for file: {filename} ---\n")
    
    return all_new_formatted_activities_for_student_data

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    newly_generated_activities = []
    try:
        newly_generated_activities = loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred during main execution: {e}")
    finally:
        loop.close()
    
    if newly_generated_activities:
        update_student_data_file(newly_generated_activities)
    else:
        print("No activities were generated by main(), so student_data.py will not be updated.")
