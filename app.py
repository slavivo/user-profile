from flask import Flask, render_template, jsonify, request
import configparser
import google.generativeai as genai
import openai
from utils.base import (
    ApiClientFactory, 
    get_initial_graph_prompt,
    get_reformatting_prompt,
    is_valid_graph_format
)
import asyncio
from functools import partial
import json
import uuid
from datetime import datetime
from utils.activity_generation import generate_activity_metadata

app = Flask(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configure API clients
OPENAI_KEY = config['DEFAULT']['OPENAI_KEY']
GENAI_KEY = config['DEFAULT']['GENAI_KEY']

def get_api_client(provider: str, model: str = None):
    """Initialize and return appropriate API client based on provider."""
    if provider == 'openai':
        return openai.AsyncClient(api_key=OPENAI_KEY)
    elif provider == 'gemini':
        genai.configure(api_key=GENAI_KEY)
        return genai.GenerativeModel(model if model else 'gemini-2.0-flash')
    else:
        raise ValueError('Invalid API provider')

# Sample student data - in a real app, this would come from a database
student_data = {
    'id': 'STU2024001',
    'school_year': '2023-2024',
    'grade': 'Second Grade',
    'class': '2.A',
    'top_abilities': [
        {'name': 'Pattern Recognition', 'value': 92},
        {'name': 'Memory Capacity', 'value': 88},
        {'name': 'Emotional Intelligence', 'value': 85}
    ],
    'top_attitudes': [
        {'name': 'Curiosity', 'value': 90},
        {'name': 'Collaboration', 'value': 88},
        {'name': 'Responsibility', 'value': 85}
    ],
    'activities': [
        {
            'id': 'ACT001',
            'name': 'Algorithm Design Challenge',
            'description': '''This advanced programming activity focuses on developing efficient sorting algorithms for managing student records in a school database system. The challenge consists of multiple phases:

1. Understanding Data Structures
- Analysis of different data structures (arrays, linked lists, trees)
- Evaluation of their pros and cons for sorting operations
- Memory complexity considerations

2. Algorithm Development
- Implementation of at least two different sorting algorithms
- Comparison of time complexity between implementations
- Optimization for specific use cases (e.g., partially sorted data)

3. Real-world Application
- Integration with a mock student database
- Handling edge cases and error conditions
- Implementation of data validation and error handling

4. Performance Analysis
- Measuring algorithm performance with different dataset sizes
- Creating performance comparison charts
- Writing a technical report on findings

The activity emphasizes both theoretical understanding and practical implementation, requiring students to think critically about algorithm efficiency and real-world applications.''',
            'learning_goals': [
                'Master fundamental algorithmic concepts and their practical applications in data management',
                'Develop ability to analyze and compare algorithm efficiency using time and space complexity',
                'Gain practical experience in implementing and optimizing sorting algorithms',
                'Learn to evaluate and select appropriate data structures for specific use cases',
                'Develop technical documentation and analysis skills'
            ],
            'connected_nodes': ['Data Structures', 'Basic Programming', 'Control Structures', 'Databases', 'System Architecture'],
            'competency_scores': {
                'problem_solving': 9,
                'logical_reasoning': 8,
                'coding': 7,
                'analysis': 8,
                'documentation': 7
            },
            'taxonomy': {
                'processing_levels': [
                    {'level': 'Analysis', 'weight': 0.4},
                    {'level': 'Use of Knowledge', 'weight': 0.4},
                    {'level': 'Metacognitive', 'weight': 0.2}
                ],
                'knowledge_domains': [
                    {'domain': 'Information', 'weight': 0.3},
                    {'domain': 'Mental Procedures', 'weight': 0.7}
                ]
            },
            'student_performance': {
                'overall_score': 8,
                'concept_scores': {
                    'data2': {
                        'name': 'Data Structures',
                        'score': 9
                    },
                    'algo1': {
                        'name': 'Basic Programming',
                        'score': 8
                    },
                    'algo2': {
                        'name': 'Control Structures',
                        'score': 7
                    },
                    'data3': {
                        'name': 'Databases',
                        'score': 8
                    },
                    'sys3': {
                        'name': 'System Architecture',
                        'score': 7
                    }
                }
            }
        },
        {
            'id': 'ACT002',
            'name': 'Data Visualization Project',
            'description': '''An comprehensive data visualization project focusing on climate change data analysis and presentation. This multi-week project encompasses several key areas:

1. Data Collection and Preparation
- Gathering climate data from multiple reliable sources
- Data cleaning and normalization techniques
- Creating a unified dataset format

2. Statistical Analysis
- Identifying key trends and patterns
- Calculating significant statistical measures
- Correlation analysis between different climate variables

3. Visualization Development
- Creating interactive visualizations using modern tools (D3.js/Python)
- Implementing multiple visualization types:
  * Time series analysis
  * Geographic heat maps
  * Correlation matrices
  * Interactive dashboards

4. Narrative Development
- Crafting a compelling story with the data
- Developing an interactive presentation
- Creating user documentation

5. Technical Implementation
- Writing clean, maintainable code
- Implementing responsive design principles
- Ensuring cross-browser compatibility

The project emphasizes both technical skills and communication abilities, requiring students to transform complex data into understandable visualizations while maintaining scientific accuracy.''',
            'learning_goals': [
                'Master data visualization techniques and best practices for scientific data',
                'Develop proficiency in data cleaning, analysis, and statistical methods',
                'Learn to create interactive and responsive visualizations using modern tools',
                'Understand principles of visual storytelling and data narrative',
                'Gain experience in technical documentation and project presentation'
            ],
            'connected_nodes': ['Data Types', 'Data Structures', 'Information Processing', 'Functions', 'Networks'],
            'competency_scores': {
                'data_analysis': 8,
                'visualization': 9,
                'communication': 7,
                'programming': 8,
                'design': 9
            },
            'taxonomy': {
                'processing_levels': [
                    {'level': 'Comprehension', 'weight': 0.3},
                    {'level': 'Analysis', 'weight': 0.4},
                    {'level': 'Use of Knowledge', 'weight': 0.3}
                ],
                'knowledge_domains': [
                    {'domain': 'Information', 'weight': 0.4},
                    {'domain': 'Mental Procedures', 'weight': 0.6}
                ]
            },
            'student_performance': {
                'overall_score': 8,
                'concept_scores': {
                    'data1': {
                        'name': 'Data Types',
                        'score': 9
                    },
                    'data2': {
                        'name': 'Data Structures',
                        'score': 8
                    },
                    'data5': {
                        'name': 'Information Processing',
                        'score': 8
                    },
                    'algo3': {
                        'name': 'Functions',
                        'score': 7
                    },
                    'sys2': {
                        'name': 'Networks',
                        'score': 7
                    }
                }
            }
        },
        {
            'id': 'ACT003',
            'name': 'Robotics Workshop',
            'description': '''An intensive robotics workshop that combines hardware assembly, programming, and problem-solving in a practical context. The workshop is structured into several modules:

1. Robot Design and Assembly
- Understanding robot components and their functions
- Circuit design and electronic components
- Sensor integration and calibration
- Mechanical assembly and testing

2. Programming and Control
- Introduction to robotics programming
- Implementing basic movement controls
- Sensor data processing
- Advanced navigation algorithms

3. Obstacle Course Challenge
- Course analysis and strategy development
- Implementation of navigation algorithms
- Real-time sensor data processing
- Error handling and recovery

4. Advanced Features
- Implementation of autonomous behavior
- Multiple operation modes
- Remote control capabilities
- Data logging and analysis

5. Documentation and Presentation
- Technical documentation
- Code documentation
- Project presentation
- Performance analysis

The workshop emphasizes hands-on learning and practical problem-solving, requiring students to integrate knowledge from multiple domains including electronics, programming, and mechanical engineering.''',
            'learning_goals': [
                'Understand fundamental principles of robotics and mechatronics',
                'Develop practical skills in robot assembly and hardware integration',
                'Master basic and advanced robotics programming concepts',
                'Learn sensor integration and real-time data processing',
                'Gain experience in project documentation and technical presentation',
                'Develop problem-solving skills in a hardware-software integrated environment'
            ],
            'connected_nodes': ['Operating Systems', 'Networks', 'Hardware Basics', 'Digital Logic', 'Functions'],
            'competency_scores': {
                'hardware': 8,
                'programming': 7,
                'problem_solving': 9,
                'system_integration': 8,
                'documentation': 7
            },
            'taxonomy': {
                'processing_levels': [
                    {'level': 'Comprehension', 'weight': 0.2},
                    {'level': 'Use of Knowledge', 'weight': 0.5},
                    {'level': 'Analysis', 'weight': 0.3}
                ],
                'knowledge_domains': [
                    {'domain': 'Information', 'weight': 0.2},
                    {'domain': 'Mental Procedures', 'weight': 0.4},
                    {'domain': 'Psychomotor Procedures', 'weight': 0.4}
                ]
            },
            'student_performance': {
                'overall_score': 8,
                'concept_scores': {
                    'sys1': {
                        'name': 'Operating Systems',
                        'score': 7
                    },
                    'sys2': {
                        'name': 'Networks',
                        'score': 8
                    },
                    'dig1': {
                        'name': 'Hardware Basics',
                        'score': 9
                    },
                    'dig2': {
                        'name': 'Digital Logic',
                        'score': 8
                    },
                    'algo3': {
                        'name': 'Functions',
                        'score': 7
                    }
                }
            }
        }
    ],
    'abilities': {
        'cognitive': {
            'pattern_recognition': 92,
            'processing_speed': 35,
            'problem_decomposition': 78,
            'spatial_reasoning': 28,
            'logical_reasoning': 72,
            'abstract_thinking': 42,
            'memory_capacity': 88,
            'information_organization': 75
        },
        'physical': {
            'hand_eye_coordination': 82,
            'fine_motor_skills': 32,
            'typing_speed': 25,
            'visual_acuity': 75
        },
        'social': {
            'emotional_intelligence': 85,
            'social_perception': 72,
            'communication_clarity': 38,
            'active_listening': 82,
            'empathy': 78,
            'stress_management': 30
        }
    },
    'attitudes': {
        'growth_mindset': 75,
        'persistence': 82,
        'curiosity': 90,
        'initiative': 45,
        'adaptability': 78,
        'risk_taking': 28,
        'self_discipline': 72,
        'collaboration': 88,
        'open_mindedness': 80,
        'responsibility': 85,
        'attention_to_detail': 35,
        'innovation_orientation': 70
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
        try:
            client = get_api_client(api_provider, model)
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

@app.route('/activities_content')
def activities_content():
    """Return just the activities section HTML"""
    return render_template('components/activities/activities_list.html', activities=student_data['activities'])

@app.route('/generate_activity', methods=['POST'])
async def generate_activity():
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        provider = data.get('provider')
        model = data.get('model')
        is_brief_mode = data.get('mode') == 'brief'

        if not all([name, description, provider, model]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            client = get_api_client(provider, model)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Generate activity metadata
        generated_data = await generate_activity_metadata(
            client=client,
            provider=provider,
            model=model,
            name=name,
            description=description,
            is_brief_mode=is_brief_mode
        )
        
        # Format activity data to match existing structure
        activity_data = {
            'id': f"ACT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8]}",
            'name': generated_data['name'],
            'description': generated_data['description'],
            'learning_goals': generated_data['learning_goals'],
            'connected_nodes': list(generated_data['connected_concepts'].keys()),
            'competency_scores': {
                'problem_solving': int(generated_data['competencies']['problem_solving'] / 10),
                'critical_thinking': int(generated_data['competencies']['critical_thinking'] / 10),
                'analysis': int(generated_data['competencies']['analytical_skills'] / 10),
                'technical': int(generated_data['competencies']['technical_proficiency'] / 10),
                'communication': int(generated_data['competencies']['communication'] / 10),
                'collaboration': int(generated_data['competencies']['collaboration'] / 10)
            },
            'taxonomy': {
                'processing_levels': [
                    {'level': 'Retrieval', 'weight': generated_data['taxonomy']['retrieval'] / 100},
                    {'level': 'Comprehension', 'weight': generated_data['taxonomy']['comprehension'] / 100},
                    {'level': 'Analysis', 'weight': generated_data['taxonomy']['analysis'] / 100},
                    {'level': 'Use of Knowledge', 'weight': generated_data['taxonomy']['knowledge_utilization'] / 100},
                    {'level': 'Metacognitive', 'weight': generated_data['taxonomy']['metacognition'] / 100},
                    {'level': 'Self-system Thinking', 'weight': generated_data['taxonomy']['self_system_thinking'] / 100}
                ],
                'knowledge_domains': [
                    {'domain': 'Information', 'weight': 0.4},
                    {'domain': 'Mental Procedures', 'weight': 0.6}
                ]
            },
            'student_performance': {
                'overall_score': 0,  # Initialize with 0
                'concept_scores': {
                    concept_id: {
                        'name': concept_id.title(),  # Placeholder name, should be replaced with actual concept names
                        'score': 0  # Initialize with 0
                    }
                    for concept_id in generated_data['connected_concepts'].keys()
                }
            }
        }
        
        # Add to activities list
        student_data['activities'].append(activity_data)
        return jsonify({'success': True, 'activity': activity_data})
        
    except Exception as e:
        print(f"Error generating activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 