"""Student data for development purposes."""

student_data = {
    'id': 'STU2024001',
    'school_year': '2023-2024',
    'grade': 'Second Grade',
    'class': '2.A',
    'abilities': {
        'cognitive': {
            'pattern_recognition': 92,
            'processing_speed': 75,
            'problem_decomposition': 85,
            'spatial_reasoning': 70,
            'logical_reasoning': 88,
            'abstract_thinking': 82,
            'memory_capacity': 88,
            'information_organization': 78
        },
        'social': {
            'emotional_intelligence': 85,
            'social_perception': 82,
            'communication_clarity': 75,
            'active_listening': 80,
            'empathy': 88,
            'stress_management': 72
        },
        'physical': {
            'hand_eye_coordination': 85,
            'fine_motor_skills': 78,
            'typing_speed': 70,
            'visual_acuity': 82
        }
    },
    'attitudes': {
        'growth_mindset': 82,
        'persistence': 85,
        'curiosity': 90,
        'initiative': 75,
        'adaptability': 80,
        'risk_taking': 72,
        'self_discipline': 85,
        'collaboration': 88,
        'open_mindedness': 85,
        'responsibility': 85,
        'attention_to_detail': 80,
        'innovation_orientation': 78
    },
    'competencies': {
        'learning_competency': 75,
        'problem_solving': 85,
        'communication': 80,
        'social_and_personal': 82,
        'civic': 75,
        'digital': 88,
        'work': 78,
        'cultural_awareness': 80
    },
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
                {
                    'id': 'ACT001_GOAL1',
                    'type': 'regular',
                    'name': 'Master fundamental algorithmic concepts and their practical applications in data management'
                },
                {
                    'id': 'ACT001_GOAL2',
                    'type': 'regular',
                    'name': 'Develop ability to analyze and compare algorithm efficiency using time and space complexity'
                },
                {
                    'id': 'ACT001_GOAL3',
                    'type': 'graph',
                    'name': 'Implement and use common data structures effectively',
                    'learning_goal_id': 'data2_goal1'
                },
                {
                    'id': 'ACT001_GOAL4',
                    'type': 'graph',
                    'name': 'Analyze time and space complexity of operations',
                    'learning_goal_id': 'data2_goal2'
                },
                {
                    'id': 'ACT001_GOAL5',
                    'type': 'graph',
                    'name': 'Create reusable and modular functions',
                    'learning_goal_id': 'algo3_goal1'
                }
            ],
            'competency_scores': {
                'Problem Solving': 9.0,
                'Learning Competency': 8.5,
                'Digital': 8.5,
                'Work': 8.0,
                'Communication': 7.5
            },
            'taxonomy': {
                'processing_levels': [
                    {'level': 'Analysis', 'weight': 0.4},
                    {'level': 'Use of Knowledge', 'weight': 0.4},
                    {'level': 'Metacognitive System', 'weight': 0.2}
                ],
                'knowledge_domains': [
                    {'domain': 'Information', 'weight': 0.3},
                    {'domain': 'Mental Procedures', 'weight': 0.7}
                ]
            },
            'student_performance': {
                'learning_goals': {
                    'ACT001_GOAL1': {
                        'name': 'Master fundamental algorithmic concepts and their practical applications in data management',
                        'mastered': True
                    },
                    'ACT001_GOAL2': {
                        'name': 'Develop ability to analyze and compare algorithm efficiency using time and space complexity',
                        'mastered': True
                    },
                    'ACT001_GOAL3': {
                        'name': 'Implement and use common data structures effectively',
                        'mastered': True
                    },
                    'ACT001_GOAL4': {
                        'name': 'Analyze time and space complexity of operations',
                        'mastered': True
                    },
                    'ACT001_GOAL5': {
                        'name': 'Create reusable and modular functions',
                        'mastered': False
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
                {
                    'id': 'ACT002_GOAL1',
                    'type': 'regular',
                    'name': 'Master data visualization techniques and best practices for scientific data'
                },
                {
                    'id': 'ACT002_GOAL2',
                    'type': 'regular',
                    'name': 'Develop proficiency in data cleaning, analysis, and statistical methods'
                },
                {
                    'id': 'ACT002_GOAL3',
                    'type': 'graph',
                    'name': 'Understand fundamental data types and their use cases',
                    'learning_goal_id': 'data1_goal1'
                },
                {
                    'id': 'ACT002_GOAL4',
                    'type': 'graph',
                    'name': 'Process and transform data efficiently',
                    'learning_goal_id': 'data5_goal1'
                },
                {
                    'id': 'ACT002_GOAL5',
                    'type': 'graph',
                    'name': 'Implement data validation and cleaning',
                    'learning_goal_id': 'data5_goal2'
                }
            ],
            'competency_scores': {
                'Digital': 9.0,
                'Communication': 8.5,
                'Problem Solving': 8.5,
                'Learning Competency': 8.0,
                'Cultural Awareness': 7.5
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
                'learning_goals': {
                    'ACT002_GOAL1': {
                        'name': 'Master data visualization techniques and best practices for scientific data',
                        'mastered': True
                    },
                    'ACT002_GOAL2': {
                        'name': 'Develop proficiency in data cleaning, analysis, and statistical methods',
                        'mastered': True
                    },
                    'ACT002_GOAL3': {
                        'name': 'Understand fundamental data types and their use cases',
                        'mastered': True
                    },
                    'ACT002_GOAL4': {
                        'name': 'Process and transform data efficiently',
                        'mastered': True
                    },
                    'ACT002_GOAL5': {
                        'name': 'Implement data validation and cleaning',
                        'mastered': False
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
                {
                    'id': 'ACT003_GOAL1',
                    'type': 'regular',
                    'name': 'Understand fundamental principles of robotics and mechatronics'
                },
                {
                    'id': 'ACT003_GOAL2',
                    'type': 'regular',
                    'name': 'Develop practical skills in robot assembly and hardware integration'
                },
                {
                    'id': 'ACT003_GOAL3',
                    'type': 'graph',
                    'name': 'Understand computer hardware components',
                    'learning_goal_id': 'dig1_goal1'
                },
                {
                    'id': 'ACT003_GOAL4',
                    'type': 'graph',
                    'name': 'Troubleshoot hardware issues',
                    'learning_goal_id': 'dig1_goal2'
                },
                {
                    'id': 'ACT003_GOAL5',
                    'type': 'graph',
                    'name': 'Implement digital logic circuits',
                    'learning_goal_id': 'dig2_goal1'
                }
            ],
            'competency_scores': {
                'Problem Solving': 9.0,
                'Digital': 8.5,
                'Work': 8.5,
                'Learning Competency': 8.0,
                'Social and Personal': 7.5
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
                'learning_goals': {
                    'ACT003_GOAL1': {
                        'name': 'Understand fundamental principles of robotics and mechatronics',
                        'mastered': True
                    },
                    'ACT003_GOAL2': {
                        'name': 'Develop practical skills in robot assembly and hardware integration',
                        'mastered': True
                    },
                    'ACT003_GOAL3': {
                        'name': 'Understand computer hardware components',
                        'mastered': True
                    },
                    'ACT003_GOAL4': {
                        'name': 'Troubleshoot hardware issues',
                        'mastered': True
                    },
                    'ACT003_GOAL5': {
                        'name': 'Implement digital logic circuits',
                        'mastered': False
                    }
                }
            }
        }
    ]
} 