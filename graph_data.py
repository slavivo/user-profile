graph_data = {
    "data": {
        "nodes": [
            { "data": { "id": "data1", "label": "Data Types", "learning_goals": [
                { "id": "data1_goal1", "name": "Understand fundamental data types and their use cases", "mastered": True, "assessment_criterias": [
                    "Can identify and explain different data types",
                    "Can choose appropriate data types for specific use cases",
                    "Can demonstrate understanding of type constraints and limitations"
                ] },
                { "id": "data1_goal2", "name": "Apply type conversion and validation techniques", "mastered": True, "assessment_criterias": [
                    "Can implement type conversion between different data types",
                    "Can write validation functions for data type checking",
                    "Can handle type conversion errors appropriately"
                ] },
                { "id": "data1_goal3", "name": "Implement custom data type definitions", "mastered": False, "assessment_criterias": [
                    "Can create custom data type definitions",
                    "Can implement type-specific methods and behaviors",
                    "Can document and test custom data types"
                ] }
            ] } },
            { "data": { "id": "data2", "label": "Data Structures", "learning_goals": [
                { "id": "data2_goal1", "name": "Implement and use common data structures effectively", "mastered": True, "assessment_criterias": [
                    "Can implement basic data structures from scratch",
                    "Can choose appropriate data structures for specific problems",
                    "Can demonstrate efficient usage of built-in data structures"
                ] },
                { "id": "data2_goal2", "name": "Analyze time and space complexity of operations", "mastered": True, "assessment_criterias": [
                    "Can calculate Big O notation for operations",
                    "Can compare different implementations based on complexity",
                    "Can optimize code based on complexity analysis"
                ] },
                { "id": "data2_goal3", "name": "Design custom data structures for specific use cases", "mastered": False, "assessment_criterias": [
                    "Can identify when custom data structures are needed",
                    "Can design efficient custom data structures",
                    "Can implement and test custom data structures"
                ] }
            ] } },
            { "data": { "id": "data3", "label": "Databases", "learning_goals": [
                { "id": "data3_goal1", "name": "Design and query relational databases", "mastered": False, "assessment_criterias": [
                    "Can design normalized database schemas",
                    "Can write complex SQL queries",
                    "Can implement database relationships and constraints"
                ] },
                { "id": "data3_goal2", "name": "Implement NoSQL database solutions", "mastered": False, "assessment_criterias": [
                    "Can choose appropriate NoSQL database types",
                    "Can design document/collection structures",
                    "Can implement efficient NoSQL queries"
                ] },
                { "id": "data3_goal3", "name": "Optimize database performance and indexing", "mastered": False, "assessment_criterias": [
                    "Can create and maintain appropriate indexes",
                    "Can analyze and optimize query performance",
                    "Can implement database caching strategies"
                ] }
            ] } },
            { "data": { "id": "data4", "label": "Data Modeling", "learning_goals": [
                { "id": "data4_goal1", "name": "Create efficient data models and schemas", "mastered": False, "assessment_criterias": [
                    "Can design logical data models",
                    "Can implement physical data models",
                    "Can validate data model efficiency"
                ] },
                { "id": "data4_goal2", "name": "Apply normalization techniques", "mastered": False, "assessment_criterias": [
                    "Can identify normalization requirements",
                    "Can implement different normalization forms",
                    "Can balance normalization with performance"
                ] },
                { "id": "data4_goal3", "name": "Design data warehouses and data lakes", "mastered": False, "assessment_criterias": [
                    "Can design data warehouse schemas",
                    "Can implement ETL processes",
                    "Can create data lake architectures"
                ] }
            ] } },
            { "data": { "id": "data5", "label": "Information Processing", "learning_goals": [
                { "id": "data5_goal1", "name": "Process and transform data efficiently", "mastered": True, "assessment_criterias": [
                    "Can implement data transformation pipelines",
                    "Can handle large datasets efficiently",
                    "Can optimize data processing workflows"
                ] },
                { "id": "data5_goal2", "name": "Implement data validation and cleaning", "mastered": True, "assessment_criterias": [
                    "Can write data validation rules",
                    "Can implement data cleaning procedures",
                    "Can handle data quality issues"
                ] },
                { "id": "data5_goal3", "name": "Apply data compression and optimization", "mastered": False, "assessment_criterias": [
                    "Can implement data compression algorithms",
                    "Can optimize data storage formats",
                    "Can balance compression with performance"
                ] }
            ] } }
        ],
        "edges": [
            { "data": { "source": "data1", "target": "data2" } },
            { "data": { "source": "data2", "target": "data3" } },
            { "data": { "source": "data3", "target": "data4" } },
            { "data": { "source": "data1", "target": "data5" } }
        ]
    },
    "algorithms": {
        "nodes": [
            { "data": { "id": "algo1", "label": "Basic Programming", "learning_goals": [
                { "id": "algo1_goal1", "name": "Write clean and efficient basic programs", "mastered": True, "assessment_criterias": [
                    "Can write readable and maintainable code",
                    "Can implement basic algorithms correctly",
                    "Can follow coding standards and best practices"
                ] },
                { "id": "algo1_goal2", "name": "Debug and troubleshoot code effectively", "mastered": True, "assessment_criterias": [
                    "Can identify and fix common programming errors",
                    "Can use debugging tools effectively",
                    "Can implement error handling strategies"
                ] },
                { "id": "algo1_goal3", "name": "Apply best coding practices and standards", "mastered": True, "assessment_criterias": [
                    "Can follow language-specific conventions",
                    "Can write self-documenting code",
                    "Can implement proper code organization"
                ] }
            ] } },
            { "data": { "id": "algo2", "label": "Control Structures", "learning_goals": [
                { "id": "algo2_goal1", "name": "Implement complex control flow patterns", "mastered": True, "assessment_criterias": [
                    "Can implement nested control structures",
                    "Can handle complex branching logic",
                    "Can optimize control flow patterns"
                ] },
                { "id": "algo2_goal2", "name": "Optimize conditional logic", "mastered": True, "assessment_criterias": [
                    "Can simplify complex conditions",
                    "Can implement efficient branching",
                    "Can handle edge cases effectively"
                ] },
                { "id": "algo2_goal3", "name": "Design state machines and workflows", "mastered": False, "assessment_criterias": [
                    "Can design state transition diagrams",
                    "Can implement state machines",
                    "Can handle complex workflow patterns"
                ] }
            ] } },
            { "data": { "id": "algo3", "label": "Functions", "learning_goals": [
                { "id": "algo3_goal1", "name": "Create reusable and modular functions", "mastered": True, "assessment_criterias": [
                    "Can write functions with single responsibility",
                    "Can implement proper function parameters",
                    "Can create reusable function libraries"
                ] },
                { "id": "algo3_goal2", "name": "Implement higher-order functions", "mastered": True, "assessment_criterias": [
                    "Can create and use callback functions",
                    "Can implement function composition",
                    "Can work with function decorators"
                ] },
                { "id": "algo3_goal3", "name": "Apply functional programming principles", "mastered": False, "assessment_criterias": [
                    "Can implement pure functions",
                    "Can work with immutable data structures",
                    "Can apply functional programming patterns"
                ] }
            ] } },
            { "data": { "id": "algo4", "label": "Arrays", "learning_goals": [
                { "id": "algo4_goal1", "name": "Manipulate and process array data structures", "mastered": False, "assessment_criterias": [
                    "Can implement array operations efficiently",
                    "Can handle multi-dimensional arrays",
                    "Can process array data in bulk"
                ] },
                { "id": "algo4_goal2", "name": "Implement array-based algorithms", "mastered": False, "assessment_criterias": [
                    "Can implement sorting algorithms",
                    "Can implement searching algorithms",
                    "Can optimize array-based solutions"
                ] },
                { "id": "algo4_goal3", "name": "Optimize array operations", "mastered": False, "assessment_criterias": [
                    "Can minimize array operations",
                    "Can implement efficient array transformations",
                    "Can handle large array datasets"
                ] }
            ] } },
            { "data": { "id": "algo5", "label": "Object-Oriented Programming", "learning_goals": [
                { "id": "algo5_goal1", "name": "Design and implement OOP principles", "mastered": False, "assessment_criterias": [
                    "Can implement encapsulation",
                    "Can apply inheritance and polymorphism",
                    "Can use abstraction effectively"
                ] },
                { "id": "algo5_goal2", "name": "Create class hierarchies and interfaces", "mastered": False, "assessment_criterias": [
                    "Can design class hierarchies",
                    "Can implement interfaces",
                    "Can create abstract classes"
                ] },
                { "id": "algo5_goal3", "name": "Apply design patterns effectively", "mastered": False, "assessment_criterias": [
                    "Can implement common design patterns",
                    "Can choose appropriate patterns",
                    "Can adapt patterns to specific needs"
                ] }
            ] } }
        ],
        "edges": [
            { "data": { "source": "algo1", "target": "algo2" } },
            { "data": { "source": "algo2", "target": "algo3" } },
            { "data": { "source": "algo3", "target": "algo4" } },
            { "data": { "source": "algo4", "target": "algo5" } }
        ]
    },
    "systems": {
        "nodes": [
            { "data": { "id": "sys1", "label": "Operating Systems", "learning_goals": [
                { "id": "sys1_goal1", "name": "Understand OS concepts and process management", "mastered": False, "assessment_criterias": [
                    "Can explain OS architecture",
                    "Can manage processes and threads",
                    "Can implement process synchronization"
                ] },
                { "id": "sys1_goal2", "name": "Implement system calls and services", "mastered": False, "assessment_criterias": [
                    "Can use system calls effectively",
                    "Can implement system services",
                    "Can handle system-level operations"
                ] },
                { "id": "sys1_goal3", "name": "Manage system resources effectively", "mastered": False, "assessment_criterias": [
                    "Can monitor system resources",
                    "Can optimize resource usage",
                    "Can implement resource management"
                ] }
            ] } },
            { "data": { "id": "sys2", "label": "Networks", "learning_goals": [
                { "id": "sys2_goal1", "name": "Implement network protocols and security", "mastered": False, "assessment_criterias": [
                    "Can implement network protocols",
                    "Can implement security measures",
                    "Can handle network communication"
                ] },
                { "id": "sys2_goal2", "name": "Design network architectures", "mastered": False, "assessment_criterias": [
                    "Can design network topologies",
                    "Can implement network services",
                    "Can scale network solutions"
                ] },
                { "id": "sys2_goal3", "name": "Troubleshoot network issues", "mastered": False, "assessment_criterias": [
                    "Can diagnose network problems",
                    "Can implement network monitoring",
                    "Can resolve network issues"
                ] }
            ] } },
            { "data": { "id": "sys3", "label": "System Architecture", "learning_goals": [
                { "id": "sys3_goal1", "name": "Design scalable system architectures", "mastered": False, "assessment_criterias": [
                    "Can design distributed systems",
                    "Can implement scaling strategies",
                    "Can handle system load balancing"
                ] },
                { "id": "sys3_goal2", "name": "Implement microservices", "mastered": False, "assessment_criterias": [
                    "Can design microservice architectures",
                    "Can implement service communication",
                    "Can manage service deployment"
                ] },
                { "id": "sys3_goal3", "name": "Apply system design patterns", "mastered": False, "assessment_criterias": [
                    "Can implement architectural patterns",
                    "Can choose appropriate patterns",
                    "Can adapt patterns to requirements"
                ] }
            ] } },
            { "data": { "id": "sys4", "label": "Cloud Computing", "learning_goals": [
                { "id": "sys4_goal1", "name": "Deploy and manage cloud-based solutions", "mastered": False, "assessment_criterias": [
                    "Can deploy applications to cloud",
                    "Can manage cloud resources",
                    "Can implement cloud services"
                ] },
                { "id": "sys4_goal2", "name": "Implement cloud security measures", "mastered": False, "assessment_criterias": [
                    "Can implement cloud security",
                    "Can manage access control",
                    "Can protect cloud resources"
                ] },
                { "id": "sys4_goal3", "name": "Optimize cloud resource usage", "mastered": False, "assessment_criterias": [
                    "Can optimize cloud costs",
                    "Can implement auto-scaling",
                    "Can manage cloud performance"
                ] }
            ] } }
        ],
        "edges": [
            { "data": { "source": "sys1", "target": "sys2" } },
            { "data": { "source": "sys2", "target": "sys3" } },
            { "data": { "source": "sys3", "target": "sys4" } }
        ]
    },
    "digital": {
        "nodes": [
            { "data": { "id": "dig1", "label": "Hardware Basics", "learning_goals": [
                { "id": "dig1_goal1", "name": "Understand computer hardware components", "mastered": True, "assessment_criterias": [
                    "Can identify hardware components",
                    "Can explain component functions",
                    "Can understand hardware interactions"
                ] },
                { "id": "dig1_goal2", "name": "Troubleshoot hardware issues", "mastered": True, "assessment_criterias": [
                    "Can diagnose hardware problems",
                    "Can implement hardware fixes",
                    "Can prevent hardware issues"
                ] },
                { "id": "dig1_goal3", "name": "Optimize hardware performance", "mastered": False, "assessment_criterias": [
                    "Can optimize hardware settings",
                    "Can implement performance improvements",
                    "Can monitor hardware performance"
                ] }
            ] } },
            { "data": { "id": "dig2", "label": "Digital Logic", "learning_goals": [
                { "id": "dig2_goal1", "name": "Implement digital logic circuits", "mastered": True, "assessment_criterias": [
                    "Can design logic circuits",
                    "Can implement Boolean functions",
                    "Can optimize circuit design"
                ] },
                { "id": "dig2_goal2", "name": "Design combinational circuits", "mastered": True, "assessment_criterias": [
                    "Can design combinational logic",
                    "Can implement circuit components",
                    "Can optimize circuit performance"
                ] },
                { "id": "dig2_goal3", "name": "Create sequential logic systems", "mastered": False, "assessment_criterias": [
                    "Can design sequential circuits",
                    "Can implement state machines",
                    "Can optimize timing in circuits"
                ] }
            ] } },
            { "data": { "id": "dig3", "label": "Input/Output Systems", "learning_goals": [
                { "id": "dig3_goal1", "name": "Design I/O interfaces and protocols", "mastered": False, "assessment_criterias": [
                    "Can design I/O interfaces",
                    "Can implement I/O protocols",
                    "Can optimize I/O performance"
                ] },
                { "id": "dig3_goal2", "name": "Implement device drivers", "mastered": False, "assessment_criterias": [
                    "Can write device drivers",
                    "Can handle device communication",
                    "Can manage device resources"
                ] },
                { "id": "dig3_goal3", "name": "Optimize I/O performance", "mastered": False, "assessment_criterias": [
                    "Can optimize I/O operations",
                    "Can implement buffering strategies",
                    "Can handle I/O bottlenecks"
                ] }
            ] } },
            { "data": { "id": "dig4", "label": "Modern Technologies", "learning_goals": [
                { "id": "dig4_goal1", "name": "Apply modern digital technologies", "mastered": True, "assessment_criterias": [
                    "Can use modern digital tools",
                    "Can implement new technologies",
                    "Can adapt to technological changes"
                ] },
                { "id": "dig4_goal2", "name": "Implement IoT solutions", "mastered": False, "assessment_criterias": [
                    "Can design IoT systems",
                    "Can implement IoT protocols",
                    "Can manage IoT devices"
                ] },
                { "id": "dig4_goal3", "name": "Design embedded systems", "mastered": False, "assessment_criterias": [
                    "Can design embedded solutions",
                    "Can implement real-time systems",
                    "Can optimize embedded performance"
                ] }
            ] } }
        ],
        "edges": [
            { "data": { "source": "dig1", "target": "dig2" } },
            { "data": { "source": "dig2", "target": "dig3" } },
            { "data": { "source": "dig2", "target": "dig4" } }
        ]
    }
}