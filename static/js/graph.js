// Initial concept data for the detailed graphs
let conceptData = null;

// Function to get color based on mastery percentage
function getMasteryColor(masteryPercentage) {
    // Convert mastery percentage (0-100) to hue (0-120, red to green)
    const hue = (120 * masteryPercentage) / 100;
    return `hsl(${hue}, 70%, 80%)`;
}

// Function to calculate mastery percentage
function calculateMasteryPercentage(learningGoals) {
    if (!learningGoals || !Array.isArray(learningGoals)) return 0;
    const mastered = learningGoals.filter(goal => goal.mastered).length;
    return (mastered / learningGoals.length) * 100;
}

// Function to create tooltip element
function createTooltip(container) {
    const tooltip = document.createElement('div');
    tooltip.id = 'node-tooltip';
    tooltip.style.position = 'absolute';
    tooltip.style.display = 'none';
    tooltip.style.background = 'white';
    tooltip.style.padding = '12px';
    tooltip.style.borderRadius = '8px';
    tooltip.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
    tooltip.style.zIndex = '1000';
    tooltip.style.maxWidth = '300px';
    tooltip.style.fontSize = '14px';
    tooltip.style.fontFamily = 'system-ui, -apple-system, sans-serif';
    tooltip.style.color = '#334155';
    tooltip.style.pointerEvents = 'none';
    container.appendChild(tooltip);
    return tooltip;
}

// Function to show tooltip with learning goals
function showTooltip(event, node, container) {
    const tooltip = document.getElementById('node-tooltip') || createTooltip(container);
    const learningGoals = node.data('learning_goals');
    
    if (!learningGoals || !Array.isArray(learningGoals)) return;

    const masteryPercentage = calculateMasteryPercentage(learningGoals);
    const title = document.createElement('div');
    title.style.fontWeight = 'bold';
    title.style.marginBottom = '8px';
    title.style.borderBottom = '1px solid #e2e8f0';
    title.style.paddingBottom = '4px';
    title.textContent = `${node.data('label')} (${Math.round(masteryPercentage)}% Mastered)`;

    const goalsList = document.createElement('div');
    goalsList.style.display = 'flex';
    goalsList.style.flexDirection = 'column';
    goalsList.style.gap = '8px';

    learningGoals.forEach(goal => {
        const goalItem = document.createElement('div');
        goalItem.style.display = 'flex';
        goalItem.style.alignItems = 'center';
        goalItem.style.gap = '8px';

        const statusIcon = document.createElement('span');
        statusIcon.textContent = goal.mastered ? '✓' : '○';
        statusIcon.style.color = goal.mastered ? '#059669' : '#6B7280';
        statusIcon.style.fontWeight = 'bold';

        const goalText = document.createElement('span');
        goalText.textContent = goal.name;
        goalText.style.flex = '1';

        goalItem.appendChild(statusIcon);
        goalItem.appendChild(goalText);
        goalsList.appendChild(goalItem);
    });

    tooltip.innerHTML = '';
    tooltip.appendChild(title);
    tooltip.appendChild(goalsList);

    // Position the tooltip relative to the container
    const padding = 10;
    const containerRect = container.getBoundingClientRect();
    const x = event.renderedPosition.x + padding;
    const y = event.renderedPosition.y + padding;

    // Ensure tooltip stays within container bounds
    const tooltipWidth = 300; // max-width of tooltip
    const tooltipHeight = tooltip.offsetHeight;
    
    let finalX = x;
    let finalY = y;

    // Adjust horizontal position if tooltip would overflow right edge
    if (x + tooltipWidth > containerRect.width) {
        finalX = x - tooltipWidth - padding;
    }

    // Adjust vertical position if tooltip would overflow bottom edge
    if (y + tooltipHeight > containerRect.height) {
        finalY = y - tooltipHeight - padding;
    }

    tooltip.style.left = `${finalX}px`;
    tooltip.style.top = `${finalY}px`;
    tooltip.style.display = 'block';
}

// Function to hide tooltip
function hideTooltip() {
    const tooltip = document.getElementById('node-tooltip');
    if (tooltip) {
        tooltip.style.display = 'none';
    }
}

// Function to create mastery legend
function createMasteryLegend(container) {
    const legend = document.createElement('div');
    legend.style.position = 'absolute';
    legend.style.bottom = '20px';
    legend.style.right = '20px';
    legend.style.background = 'white';
    legend.style.padding = '10px';
    legend.style.borderRadius = '8px';
    legend.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    legend.style.zIndex = '10';
    
    const title = document.createElement('div');
    title.textContent = 'Mastery Scale';
    title.style.fontWeight = 'bold';
    title.style.marginBottom = '8px';
    title.style.fontSize = '12px';
    legend.appendChild(title);

    const gradientBar = document.createElement('div');
    gradientBar.style.height = '20px';
    gradientBar.style.width = '200px';
    gradientBar.style.background = 'linear-gradient(to right, hsl(0, 70%, 80%), hsl(60, 70%, 80%), hsl(120, 70%, 80%))';
    gradientBar.style.borderRadius = '4px';
    gradientBar.style.marginBottom = '4px';
    legend.appendChild(gradientBar);

    const labels = document.createElement('div');
    labels.style.display = 'flex';
    labels.style.justifyContent = 'space-between';
    labels.style.fontSize = '10px';
    labels.style.color = '#666';
    labels.innerHTML = '<span>0%</span><span>50%</span><span>100%</span>';
    legend.appendChild(labels);

    container.appendChild(legend);
}

// Function to fetch concept data from the backend
async function fetchConceptData() {
    try {
        const response = await fetch('/api/concept_graph_data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        conceptData = await response.json();
        return conceptData;
    } catch (error) {
        console.error('Error fetching concept data:', error);
        throw error;
    }
}

// Initialize cytoscape instance
function initializeCytoscape(container, elements) {
    if (window.cy) {
        window.cy.destroy();
    }

    // Create the cytoscape instance
    const cy = cytoscape({
        container: container,
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'background-color': function(ele) {
                        const learningGoals = ele.data('learning_goals');
                        if (!learningGoals) return '#e2e8f0';
                        
                        const masteryPercentage = calculateMasteryPercentage(learningGoals);
                        return getMasteryColor(masteryPercentage);
                    },
                    'border-width': 1,
                    'border-color': '#e2e8f0',
                    'color': '#334155',
                    'text-wrap': 'wrap',
                    'text-max-width': 100,
                    'font-size': 12,
                    'font-family': 'system-ui, -apple-system, sans-serif',
                    'font-weight': 500,
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': 130,
                    'height': 45,
                    'padding': 12,
                    'shape': 'round-rectangle',
                    'background-opacity': 0.95
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 1.5,
                    'line-color': '#e2e8f0',
                    'target-arrow-color': '#e2e8f0',
                    'target-arrow-shape': 'vee',
                    'curve-style': 'bezier',
                    'arrow-scale': 1.2,
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

    // Add tooltip event listeners
    cy.on('mouseover', 'node', function(event) {
        showTooltip(event, event.target, container);
    });

    cy.on('mouseout', 'node', function() {
        hideTooltip();
    });

    // Add the legend to the container
    createMasteryLegend(container);

    return cy;
}

// Function to update model options
function updateModelOptions(provider) {
    const modelSelect = document.getElementById('model-select');
    const models = modelConfigs[provider];
    
    modelSelect.innerHTML = models.map(model => 
        `<option value="${model.id}" ${model.default ? 'selected' : ''}>${model.name}</option>`
    ).join('');
}

// Function to handle root concepts button click
function handleRootConceptsClick() {
    const mainConcepts = document.getElementById('main-concepts');
    const conceptGraph = document.getElementById('concept-graph');
    const responseLog = document.getElementById('response-log');
    
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
    
    // Re-attach click handler to the new button
    document.getElementById('root-concepts').addEventListener('click', handleRootConceptsClick);
}

// Function to handle concept card clicks
async function handleConceptCardClick(card) {
    const mainConcepts = document.getElementById('main-concepts');
    const conceptGraph = document.getElementById('concept-graph');
    const responseLog = document.getElementById('response-log');
    const graphContainer = document.getElementById('graph-container');
    const breadcrumb = document.getElementById('concept-breadcrumb');
    
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

    // Make sure we have the concept data
    if (!conceptData) {
        try {
            await fetchConceptData();
        } catch (error) {
            console.error('Failed to fetch concept data:', error);
            return;
        }
    }

    // Initialize graph with fetched data
    window.cy = initializeCytoscape(graphContainer, conceptData[concept]);
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

        // Check for the response in the new format
        const graphData = data.response || data;

        if (!graphData) {
            console.error('No response data in API response');
            alert('No graph data received from API');
            return;
        }

        try {
            
            // Validate graph data structure
            if (!graphData.nodes || !graphData.edges) {
                throw new Error('Invalid graph data structure: missing nodes or edges');
            }

            // Update the local concept data
            if (conceptData) {
                conceptData[window.currentConcept] = graphData;
            }

            // Initialize the graph with new data
            window.cy = initializeCytoscape(document.getElementById('graph-container'), graphData);

        } catch (e) {
            console.error('Error processing graph data:', e);
            console.error('Raw response:', graphData);
            alert(`Error processing the generated graph data: ${e.message}`);
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
    // Attach click handlers to concept cards
    document.querySelectorAll('.concept-card').forEach(card => {
        card.addEventListener('click', () => handleConceptCardClick(card));
    });
    
    // Attach click handler to root concepts button
    document.getElementById('root-concepts').addEventListener('click', handleRootConceptsClick);
    
    // Set up API provider change handler
    document.getElementById('api-select').addEventListener('change', function() {
        updateModelOptions(this.value);
    });
    
    // Set up generate graph button handler
    document.getElementById('generate-graph').addEventListener('click', function() {
        handleGraphGeneration(this);
    });
    
    // Initialize model options
    updateModelOptions('gemini');
}); 