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

// Function to format grade level for display
function formatGradeLevel(grade) {
    switch(grade) {
        case '5th_grade': return '5th Grade';
        case '6th_grade': return '6th Grade';
        case '7th_grade': return '7th Grade';
        case '8th_grade': return '8th Grade';
        case '9th_grade': return '9th Grade';
        case 'extra': return 'Extra';
        default: return grade;
    }
}

// Function to show learning goals view
function showLearningGoals(node) {
    const mainConcepts = document.getElementById('main-concepts');
    const conceptGraph = document.getElementById('concept-graph');
    const learningGoalsView = document.getElementById('learning-goals-view');
    const learningGoalsList = document.getElementById('learning-goals-list');
    const learningGoalsTitle = document.getElementById('learning-goals-title');
    const breadcrumb = document.getElementById('concept-breadcrumb').querySelector('ol');
    
    // Store the current node's data globally for filtering
    window.currentNodeData = node.data();
    
    // Hide graph, show learning goals
    conceptGraph.classList.add('hidden');
    learningGoalsView.classList.remove('hidden');
    
    // Update title
    learningGoalsTitle.textContent = node.data('label');
    
    // Update breadcrumb - make previous items clickable and current item gray
    const breadcrumbItem = document.createElement('li');
    breadcrumbItem.className = 'inline-flex items-center';
    breadcrumbItem.innerHTML = `
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        <span class="ml-1 text-sm font-medium text-gray-500">${node.data('label')}</span>
    `;
    
    // Update previous breadcrumb items to be clickable
    Array.from(breadcrumb.children).forEach(item => {
        const span = item.querySelector('span');
        if (span) {
            span.className = 'ml-1 text-sm font-medium text-indigo-600 hover:text-indigo-900 cursor-pointer';
        }
    });
    
    breadcrumb.appendChild(breadcrumbItem);
    
    // Set up grade filter event listeners
    setupGradeFilters();
    
    // Display all goals initially
    filterGoalsByGrade('all');
}

// Function to set up grade filter event listeners
function setupGradeFilters() {
    const gradeFilters = document.querySelectorAll('.grade-filter');
    gradeFilters.forEach(button => {
        // Remove existing listeners
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add new listener
        newButton.addEventListener('click', () => {
            const grade = newButton.getAttribute('data-grade');
            filterGoalsByGrade(grade);
        });
    });
}

// Function to filter learning goals by grade
function filterGoalsByGrade(selectedGrade) {
    if (!window.currentNodeData) return;
    
    const learningGoalsList = document.getElementById('learning-goals-list');
    const learningGoals = window.currentNodeData.learning_goals || [];
    
    // Update filter button styles
    document.querySelectorAll('.grade-filter').forEach(button => {
        const grade = button.getAttribute('data-grade');
        if (grade === selectedGrade) {
            button.className = 'grade-filter px-3 py-1 text-sm font-medium rounded-full bg-indigo-100 text-indigo-800 hover:bg-indigo-200';
        } else {
            button.className = 'grade-filter px-3 py-1 text-sm font-medium rounded-full bg-gray-100 text-gray-800 hover:bg-gray-200';
        }
    });
    
    // Clear and populate learning goals list
    learningGoalsList.innerHTML = '';
    
    // Filter and sort goals
    const filteredGoals = learningGoals.filter(goal => 
        selectedGrade === 'all' || goal.grade === selectedGrade
    ).sort((a, b) => {
        const gradeOrder = {
            '5th_grade': 1,
            '6th_grade': 2,
            '7th_grade': 3,
            '8th_grade': 4,
            '9th_grade': 5,
            'extra': 6
        };
        return gradeOrder[a.grade] - gradeOrder[b.grade];
    });
    
    // Group goals by grade if showing all
    const groupedGoals = selectedGrade === 'all' 
        ? filteredGoals.reduce((acc, goal) => {
            if (!acc[goal.grade]) acc[goal.grade] = [];
            acc[goal.grade].push(goal);
            return acc;
        }, {})
        : { [selectedGrade]: filteredGoals };
    
    // Display goals
    Object.entries(groupedGoals).forEach(([grade, goals]) => {
        if (goals.length === 0) return;
        
        if (selectedGrade === 'all') {
            // Add grade header
            const gradeHeader = document.createElement('li');
            gradeHeader.className = 'px-4 py-2 bg-gray-50';
            gradeHeader.innerHTML = `<h4 class="text-sm font-medium text-gray-900">${formatGradeLevel(grade)}</h4>`;
            learningGoalsList.appendChild(gradeHeader);
        }
        
        goals.forEach(goal => {
            const li = document.createElement('li');
            li.className = 'px-4 py-4 sm:px-6';
            li.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <span class="flex-shrink-0 h-5 w-5 text-${goal.mastered ? 'green' : 'gray'}-500">
                            ${goal.mastered ? '✓' : '○'}
                        </span>
                        <p class="ml-3 text-sm text-gray-900">${goal.name}</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        ${selectedGrade === 'all' ? 
                            `<span class="text-xs font-medium text-gray-500">${formatGradeLevel(goal.grade)}</span>` : 
                            ''
                        }
                        <button class="toggle-mastery ml-4 px-3 py-1 text-xs font-medium rounded-full ${
                            goal.mastered 
                                ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                        }">
                            ${goal.mastered ? 'Mastered' : 'Not Mastered'}
                        </button>
                    </div>
                </div>
            `;
            
            // Add click handler for the mastery toggle button
            const toggleButton = li.querySelector('.toggle-mastery');
            toggleButton.addEventListener('click', () => {
                goal.mastered = !goal.mastered;
                // Update the button appearance
                toggleButton.className = `toggle-mastery ml-4 px-3 py-1 text-xs font-medium rounded-full ${
                    goal.mastered 
                        ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                        : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`;
                toggleButton.textContent = goal.mastered ? 'Mastered' : 'Not Mastered';
                // Update the status icon
                const statusIcon = li.querySelector('.flex-shrink-0');
                statusIcon.textContent = goal.mastered ? '✓' : '○';
                statusIcon.className = `flex-shrink-0 h-5 w-5 text-${goal.mastered ? 'green' : 'gray'}-500`;
                
                // Update node color in the graph
                if (window.cy) {
                    const node = window.cy.$(`#${window.currentNodeData.id}`);
                    if (node) {
                        node.style('background-color', getMasteryColor(calculateMasteryPercentage(window.currentNodeData.learning_goals)));
                    }
                }
            });
            
            learningGoalsList.appendChild(li);
        });
    });
}

// Function to handle root concepts button click
function handleRootConceptsClick() {
    const mainConcepts = document.getElementById('main-concepts');
    const conceptGraph = document.getElementById('concept-graph');
    const learningGoalsView = document.getElementById('learning-goals-view');
    const responseLog = document.getElementById('response-log');
    
    // Hide all other views
    mainConcepts.classList.remove('hidden');
    conceptGraph.classList.add('hidden');
    learningGoalsView.classList.add('hidden');
    responseLog.classList.add('hidden');
    window.currentConcept = null;
    
    if (window.cy) {
        window.cy.destroy();
        window.cy = null;
    }
    
    // Reset breadcrumb
    const breadcrumb = document.getElementById('concept-breadcrumb');
    breadcrumb.querySelector('ol').innerHTML = `
        <li class="inline-flex items-center">
            <button id="root-concepts" class="inline-flex items-center text-sm font-medium text-gray-500">
                Main Concepts
            </button>
        </li>
    `;
    
    // Re-attach click handler to the new button
    document.getElementById('root-concepts').addEventListener('click', handleRootConceptsClick);
}

// Function to handle breadcrumb navigation
function handleBreadcrumbClick(index) {
    const breadcrumb = document.getElementById('concept-breadcrumb').querySelector('ol');
    const mainConcepts = document.getElementById('main-concepts');
    const conceptGraph = document.getElementById('concept-graph');
    const learningGoalsView = document.getElementById('learning-goals-view');
    const responseLog = document.getElementById('response-log');
    
    // Remove all items after the clicked index
    while (breadcrumb.children.length > index + 1) {
        breadcrumb.removeChild(breadcrumb.lastChild);
    }
    
    // Update styles for breadcrumb items
    Array.from(breadcrumb.children).forEach((item, i) => {
        const span = item.querySelector('span');
        if (span) {
            if (i === index) {
                span.className = 'ml-1 text-sm font-medium text-gray-500';
            } else {
                span.className = 'ml-1 text-sm font-medium text-indigo-600 hover:text-indigo-900 cursor-pointer';
            }
        }
    });
    
    // Hide all views first
    mainConcepts.classList.add('hidden');
    conceptGraph.classList.add('hidden');
    learningGoalsView.classList.add('hidden');
    responseLog.classList.add('hidden');
    
    // Show appropriate view based on index
    if (index === 0) {
        // Main Concepts view
        mainConcepts.classList.remove('hidden');
        window.currentConcept = null;
    } else if (index === 1) {
        // Graph view
        conceptGraph.classList.remove('hidden');
    } else if (index === 2) {
        // Learning goals view
        conceptGraph.classList.add('hidden');
        learningGoalsView.classList.remove('hidden');
    }
}

// Function to create cytoscape instance
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
                    'curve-style': 'bezier'
                }
            }
        ],
        layout: {
            name: 'fcose',
            animate: true,
            animationDuration: 500,
            nodeRepulsion: 8000,
            nodeOverlap: 20,
            idealEdgeLength: 100,
            padding: 50,
            componentSpacing: 100,
            randomize: true
        }
    });

    // Add node click event
    cy.on('tap', 'node', function(event) {
        showLearningGoals(event.target);
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
    // Remove any existing event listeners
    const breadcrumb = document.getElementById('concept-breadcrumb');
    const newBreadcrumb = breadcrumb.cloneNode(true);
    breadcrumb.parentNode.replaceChild(newBreadcrumb, breadcrumb);
    
    // Attach click handlers to concept cards
    document.querySelectorAll('.concept-card').forEach(card => {
        card.addEventListener('click', () => handleConceptCardClick(card));
    });
    
    // Attach click handler to breadcrumb navigation
    newBreadcrumb.addEventListener('click', function(e) {
        const breadcrumbItem = e.target.closest('li');
        if (breadcrumbItem) {
            const index = Array.from(breadcrumbItem.parentNode.children).indexOf(breadcrumbItem);
            handleBreadcrumbClick(index);
        }
    });
    
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