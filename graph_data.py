graph_data = {
    "data": {
        "nodes": [
            { "data": { "id": "data1", "label": "Data Types", "progress": 80 } },
            { "data": { "id": "data2", "label": "Data Structures", "progress": 75 } },
            { "data": { "id": "data3", "label": "Databases", "progress": 70 } },
            { "data": { "id": "data4", "label": "Data Modeling", "progress": 65 } },
            { "data": { "id": "data5", "label": "Information Processing", "progress": 85 } }
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
            { "data": { "id": "algo1", "label": "Basic Programming", "progress": 90 } },
            { "data": { "id": "algo2", "label": "Control Structures", "progress": 85 } },
            { "data": { "id": "algo3", "label": "Functions", "progress": 80 } },
            { "data": { "id": "algo4", "label": "Arrays", "progress": 75 } },
            { "data": { "id": "algo5", "label": "Object-Oriented Programming", "progress": 70 } }
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
            { "data": { "id": "sys1", "label": "Operating Systems", "progress": 65 } },
            { "data": { "id": "sys2", "label": "Networks", "progress": 60 } },
            { "data": { "id": "sys3", "label": "System Architecture", "progress": 55 } },
            { "data": { "id": "sys4", "label": "Cloud Computing", "progress": 50 } }
        ],
        "edges": [
            { "data": { "source": "sys1", "target": "sys2" } },
            { "data": { "source": "sys2", "target": "sys3" } },
            { "data": { "source": "sys3", "target": "sys4" } }
        ]
    },
    "digital": {
        "nodes": [
            { "data": { "id": "dig1", "label": "Hardware Basics", "progress": 75 } },
            { "data": { "id": "dig2", "label": "Digital Logic", "progress": 70 } },
            { "data": { "id": "dig3", "label": "Input/Output Systems", "progress": 65 } },
            { "data": { "id": "dig4", "label": "Modern Technologies", "progress": 70 } }
        ],
        "edges": [
            { "data": { "source": "dig1", "target": "dig2" } },
            { "data": { "source": "dig2", "target": "dig3" } },
            { "data": { "source": "dig2", "target": "dig4" } }
        ]
    }
}