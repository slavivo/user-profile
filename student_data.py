"""Student data for development purposes."""

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
            'connected_nodes': [
                {'id': 'data2', 'connection_strength': 90},  # Data Structures
                {'id': 'algo1', 'connection_strength': 85},  # Basic Programming
                {'id': 'algo2', 'connection_strength': 80},  # Control Structures
                {'id': 'data3', 'connection_strength': 75},  # Databases
                {'id': 'sys3', 'connection_strength': 70}    # System Architecture
            ],
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
            'connected_nodes': [
                {'id': 'data1', 'connection_strength': 90},  # Data Types
                {'id': 'data2', 'connection_strength': 85},  # Data Structures
                {'id': 'data5', 'connection_strength': 85},  # Information Processing
                {'id': 'algo3', 'connection_strength': 75},  # Functions
                {'id': 'sys2', 'connection_strength': 70}    # Networks
            ],
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
            'connected_nodes': [
                {'id': 'sys1', 'connection_strength': 85},   # Operating Systems
                {'id': 'sys2', 'connection_strength': 80},   # Networks
                {'id': 'dig1', 'connection_strength': 90},   # Hardware Basics
                {'id': 'dig2', 'connection_strength': 85},   # Digital Logic
                {'id': 'algo3', 'connection_strength': 75}   # Functions
            ],
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