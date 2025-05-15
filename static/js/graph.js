// Model configurations
const modelConfigs = {
    gemini: [
        { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', default: true },
        { id: 'gemini-2.5-flash-preview-04-17', name: 'Gemini 2.5 Flash' },
        { id: 'gemini-2.5-pro-preview-05-06', name: 'Gemini 2.5 Pro' }
    ],
    openai: [
        { id: 'gpt-4o-2024-08-06', name: 'GPT-4O', default: true },
        { id: 'o4-mini-2025-04-16', name: 'GPT-4O Mini' },
        { id: 'o3-mini-2025-01-31', name: 'GPT-3O Mini' }
    ]
};

// Initial concept data for the detailed graphs
const conceptData = {
    data: {
        nodes: [
            { data: { id: 'data1', label: 'Data Types', progress: 80 } },
            { data: { id: 'data2', label: 'Data Structures', progress: 75 } },
            { data: { id: 'data3', label: 'Databases', progress: 70 } },
            { data: { id: 'data4', label: 'Data Modeling', progress: 65 } },
            { data: { id: 'data5', label: 'Information Processing', progress: 85 } }
        ],
        edges: [
            { data: { source: 'data1', target: 'data2' } },
            { data: { source: 'data2', target: 'data3' } },
            { data: { source: 'data3', target: 'data4' } },
            { data: { source: 'data1', target: 'data5' } }
        ]
    },
    algorithms: {
        nodes: [
            { data: { id: 'algo1', label: 'Basic Programming', progress: 90 } },
            { data: { id: 'algo2', label: 'Control Structures', progress: 85 } },
            { data: { id: 'algo3', label: 'Functions', progress: 80 } },
            { data: { id: 'algo4', label: 'Arrays', progress: 75 } },
            { data: { id: 'algo5', label: 'Object-Oriented Programming', progress: 70 } }
        ],
        edges: [
            { data: { source: 'algo1', target: 'algo2' } },
            { data: { source: 'algo2', target: 'algo3' } },
            { data: { source: 'algo3', target: 'algo4' } },
            { data: { source: 'algo4', target: 'algo5' } }
        ]
    },
    systems: {
        nodes: [
            { data: { id: 'sys1', label: 'Operating Systems', progress: 65 } },
            { data: { id: 'sys2', label: 'Networks', progress: 60 } },
            { data: { id: 'sys3', label: 'System Architecture', progress: 55 } },
            { data: { id: 'sys4', label: 'Cloud Computing', progress: 50 } }
        ],
        edges: [
            { data: { source: 'sys1', target: 'sys2' } },
            { data: { source: 'sys2', target: 'sys3' } },
            { data: { source: 'sys3', target: 'sys4' } }
        ]
    },
    digital: {
        nodes: [
            { data: { id: 'dig1', label: 'Hardware Basics', progress: 75 } },
            { data: { id: 'dig2', label: 'Digital Logic', progress: 70 } },
            { data: { id: 'dig3', label: 'Input/Output Systems', progress: 65 } },
            { data: { id: 'dig4', label: 'Modern Technologies', progress: 70 } }
        ],
        edges: [
            { data: { source: 'dig1', target: 'dig2' } },
            { data: { source: 'dig2', target: 'dig3' } },
            { data: { source: 'dig2', target: 'dig4' } }
        ]
    }
};

// Initialize cytoscape instance
function initializeCytoscape(container, elements) {
    if (window.cy) {
        window.cy.destroy();
    }
    return cytoscape({
        container: container,
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'background-color': '#ffffff',
                    'border-width': '2px',
                    'border-color': '#6366f1',
                    'color': '#1f2937',
                    'text-wrap': 'wrap',
                    'text-max-width': '100px',
                    'font-size': '12px',
                    'font-family': 'system-ui, -apple-system, sans-serif',
                    'font-weight': '500',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': '130px',
                    'height': '45px',
                    'padding': '12px',
                    'shadow-blur': '10px',
                    'shadow-color': '#a5b4fc',
                    'shadow-opacity': 0.3,
                    'shadow-offset-x': '0px',
                    'shadow-offset-y': '4px',
                    'border-radius': '8px'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#cbd5e1',
                    'target-arrow-color': '#cbd5e1',
                    'target-arrow-shape': 'vee',
                    'curve-style': 'bezier',
                    'arrow-scale': 1.5,
                    'line-style': 'solid'
                }
            }
        ],
        layout: {
            name: 'dagre',
            rankDir: 'TB',
            padding: 50,
            spacingFactor: 1.5,
            animate: true,
            animationDuration: 500
        }
    });
}

// Function to update model options
function updateModelOptions(provider) {
    const modelSelect = document.getElementById('model-select');
    const models = modelConfigs[provider];
    
    modelSelect.innerHTML = models.map(model => 
        `<option value="${model.id}" ${model.default ? 'selected' : ''}>${model.name}</option>`
    ).join('');
}

// Function to handle concept card clicks
function handleConceptCardClick(card, mainConcepts, conceptGraph, responseLog, graphContainer, breadcrumb) {
    const concept = card.getAttribute('data-concept');
    window.currentConcept = concept;
    
    // Update active state
    document.querySelectorAll('.concept-card').forEach(c => {
        c.classList.remove('active');
        c.classList.remove('bg-indigo-50');
    });
    card.classList.add('active');
    card.classList.add('bg-indigo-50');
    
    mainConcepts.classList.add('hidden');
    conceptGraph.classList.remove('hidden');
    responseLog.classList.add('hidden');
    
    // Update breadcrumb
    const conceptTitle = card.querySelector('h3').textContent;
    const breadcrumbItem = document.createElement('li');
    breadcrumbItem.className = 'inline-flex items-center';
    breadcrumbItem.innerHTML = `
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        <span class="ml-1 text-sm font-medium text-gray-500">${conceptTitle}</span>
    `;
    breadcrumb.querySelector('ol').appendChild(breadcrumbItem);

    // Initialize graph with existing data
    window.cy = initializeCytoscape(graphContainer, conceptData[concept]);
}

// Function to handle root concepts button click
function handleRootConceptsClick(mainConcepts, conceptGraph, responseLog) {
    mainConcepts.classList.remove('hidden');
    conceptGraph.classList.add('hidden');
    responseLog.classList.add('hidden');
    window.currentConcept = null;
    if (window.cy) {
        window.cy.destroy();
        window.cy = null;
    }
    // Reset breadcrumb
    document.getElementById('concept-breadcrumb').querySelector('ol').innerHTML = `
        <li class="inline-flex items-center">
            <button id="root-concepts" class="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-900">
                Main Concepts
            </button>
        </li>
    `;
}

// Function to handle graph generation
async function handleGraphGeneration(generateBtn) {
    if (!window.currentConcept) {
        alert('Please select a concept first');
        return;
    }

    const apiProvider = document.getElementById('api-select').value;
    const model = document.getElementById('model-select').value;
    
    try {
        generateBtn.disabled = true;
        generateBtn.innerHTML = 'Generating...';
        
        const response = await fetch('/generate_graph', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                api_provider: apiProvider,
                model: model,
                concept: window.currentConcept
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Show response in log
        const responseLog = document.getElementById('response-log');
        const responseContent = document.getElementById('response-content');
        responseLog.classList.remove('hidden');
        
        // Format and display the full response for debugging
        responseContent.textContent = JSON.stringify(data, null, 2);

        if (data.error) {
            console.error('API returned error:', data.error);
            alert(`Error from API: ${data.error}`);
            return;
        }

        if (!data.response) {
            console.error('No response data in API response');
            alert('No graph data received from API');
            return;
        }

        try {
            console.log('Attempting to parse response:', data.response);
            let graphData;
            
            // If response is already an object, use it directly
            if (typeof data.response === 'object') {
                graphData = data.response;
            } else {
                // Try to parse the response as JSON
                graphData = JSON.parse(data.response);
            }

            // Validate graph data structure
            if (!graphData.nodes || !graphData.edges) {
                throw new Error('Invalid graph data structure: missing nodes or edges');
            }

            // Convert the data format if needed
            const cytoscapeElements = {
                nodes: graphData.nodes.map(node => ({
                    data: {
                        id: node.id,
                        label: node.label,
                        progress: node.progress
                    }
                })),
                edges: graphData.edges.map(edge => ({
                    data: {
                        source: edge.source,
                        target: edge.target
                    }
                }))
            };

            console.log('Formatted graph data:', cytoscapeElements);
            window.cy = initializeCytoscape(document.getElementById('graph-container'), cytoscapeElements);
        } catch (e) {
            console.error('Error parsing graph data:', e);
            console.error('Raw response:', data.response);
            alert(`Error parsing the generated graph data: ${e.message}`);
        }
    } catch (error) {
        console.error('Error generating graph:', error);
        alert('Error generating graph: ' + error.message);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = 'Generate New Graph';
    }
}

// Initialize everything when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const mainConcepts = document.getElementById('main-concepts');
    const conceptGraph = document.getElementById('concept-graph');
    const graphContainer = document.getElementById('graph-container');
    const rootConceptsBtn = document.getElementById('root-concepts');
    const breadcrumb = document.getElementById('concept-breadcrumb');
    const responseLog = document.getElementById('response-log');
    const generateBtn = document.getElementById('generate-graph');
    
    // Initialize model options
    updateModelOptions('gemini');

    // Set up event listeners
    document.getElementById('api-select').addEventListener('change', function() {
        updateModelOptions(this.value);
    });

    document.querySelectorAll('.concept-card').forEach(card => {
        card.addEventListener('click', () => handleConceptCardClick(
            card, mainConcepts, conceptGraph, responseLog, graphContainer, breadcrumb
        ));
    });

    rootConceptsBtn.addEventListener('click', () => handleRootConceptsClick(
        mainConcepts, conceptGraph, responseLog
    ));

    generateBtn.addEventListener('click', () => handleGraphGeneration(generateBtn));
}); 