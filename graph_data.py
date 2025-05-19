graph_data = {
    "data": {
        "nodes": [
            { "data": { "id": "data1", "label": "Data Types", "learning_goals": [
                { "name": "Understand fundamental data types and their use cases", "mastered": True },
                { "name": "Apply type conversion and validation techniques", "mastered": True },
                { "name": "Implement custom data type definitions", "mastered": False }
            ] } },
            { "data": { "id": "data2", "label": "Data Structures", "learning_goals": [
                { "name": "Implement and use common data structures effectively", "mastered": True },
                { "name": "Analyze time and space complexity of operations", "mastered": True },
                { "name": "Design custom data structures for specific use cases", "mastered": False }
            ] } },
            { "data": { "id": "data3", "label": "Databases", "learning_goals": [
                { "name": "Design and query relational databases", "mastered": False },
                { "name": "Implement NoSQL database solutions", "mastered": False },
                { "name": "Optimize database performance and indexing", "mastered": False }
            ] } },
            { "data": { "id": "data4", "label": "Data Modeling", "learning_goals": [
                { "name": "Create efficient data models and schemas", "mastered": False },
                { "name": "Apply normalization techniques", "mastered": False },
                { "name": "Design data warehouses and data lakes", "mastered": False }
            ] } },
            { "data": { "id": "data5", "label": "Information Processing", "learning_goals": [
                { "name": "Process and transform data efficiently", "mastered": True },
                { "name": "Implement data validation and cleaning", "mastered": True },
                { "name": "Apply data compression and optimization", "mastered": False }
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
                { "name": "Write clean and efficient basic programs", "mastered": True },
                { "name": "Debug and troubleshoot code effectively", "mastered": True },
                { "name": "Apply best coding practices and standards", "mastered": True }
            ] } },
            { "data": { "id": "algo2", "label": "Control Structures", "learning_goals": [
                { "name": "Implement complex control flow patterns", "mastered": True },
                { "name": "Optimize conditional logic", "mastered": True },
                { "name": "Design state machines and workflows", "mastered": False }
            ] } },
            { "data": { "id": "algo3", "label": "Functions", "learning_goals": [
                { "name": "Create reusable and modular functions", "mastered": True },
                { "name": "Implement higher-order functions", "mastered": True },
                { "name": "Apply functional programming principles", "mastered": False }
            ] } },
            { "data": { "id": "algo4", "label": "Arrays", "learning_goals": [
                { "name": "Manipulate and process array data structures", "mastered": False },
                { "name": "Implement array-based algorithms", "mastered": False },
                { "name": "Optimize array operations", "mastered": False }
            ] } },
            { "data": { "id": "algo5", "label": "Object-Oriented Programming", "learning_goals": [
                { "name": "Design and implement OOP principles", "mastered": False },
                { "name": "Create class hierarchies and interfaces", "mastered": False },
                { "name": "Apply design patterns effectively", "mastered": False }
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
                { "name": "Understand OS concepts and process management", "mastered": False },
                { "name": "Implement system calls and services", "mastered": False },
                { "name": "Manage system resources effectively", "mastered": False }
            ] } },
            { "data": { "id": "sys2", "label": "Networks", "learning_goals": [
                { "name": "Implement network protocols and security", "mastered": False },
                { "name": "Design network architectures", "mastered": False },
                { "name": "Troubleshoot network issues", "mastered": False }
            ] } },
            { "data": { "id": "sys3", "label": "System Architecture", "learning_goals": [
                { "name": "Design scalable system architectures", "mastered": False },
                { "name": "Implement microservices", "mastered": False },
                { "name": "Apply system design patterns", "mastered": False }
            ] } },
            { "data": { "id": "sys4", "label": "Cloud Computing", "learning_goals": [
                { "name": "Deploy and manage cloud-based solutions", "mastered": False },
                { "name": "Implement cloud security measures", "mastered": False },
                { "name": "Optimize cloud resource usage", "mastered": False }
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
                { "name": "Understand computer hardware components", "mastered": True },
                { "name": "Troubleshoot hardware issues", "mastered": True },
                { "name": "Optimize hardware performance", "mastered": False }
            ] } },
            { "data": { "id": "dig2", "label": "Digital Logic", "learning_goals": [
                { "name": "Implement digital logic circuits", "mastered": True },
                { "name": "Design combinational circuits", "mastered": True },
                { "name": "Create sequential logic systems", "mastered": False }
            ] } },
            { "data": { "id": "dig3", "label": "Input/Output Systems", "learning_goals": [
                { "name": "Design I/O interfaces and protocols", "mastered": False },
                { "name": "Implement device drivers", "mastered": False },
                { "name": "Optimize I/O performance", "mastered": False }
            ] } },
            { "data": { "id": "dig4", "label": "Modern Technologies", "learning_goals": [
                { "name": "Apply modern digital technologies", "mastered": True },
                { "name": "Implement IoT solutions", "mastered": False },
                { "name": "Design embedded systems", "mastered": False }
            ] } }
        ],
        "edges": [
            { "data": { "source": "dig1", "target": "dig2" } },
            { "data": { "source": "dig2", "target": "dig3" } },
            { "data": { "source": "dig2", "target": "dig4" } }
        ]
    }
}