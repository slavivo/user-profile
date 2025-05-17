// Fetch and render competencies data
async function fetchAndRenderCompetencies() {
    try {
        const response = await fetch('/api/competencies');
        const competencies = await response.json();

        const container = document.querySelector('#competencies-container');
        if (container && competencies) {
            container.innerHTML = competencies.map(competency => `
                <div class="bg-gray-50 p-4 rounded-lg">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-lg font-medium text-gray-900">${competency.name}</h3>
                        <span class="text-sm font-medium text-indigo-600">${competency.value}%</span>
                    </div>
                    <div class="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div class="absolute top-0 left-0 h-full bg-indigo-600 rounded-full" 
                             style="width: ${competency.value}%"></div>
                    </div>
                    <p class="mt-2 text-sm text-gray-600" id="${competency.id}-description"></p>
                </div>
            `).join('');
        }

        // Add descriptions for each competency
        const descriptions = {
            'learning_competency': 'Ability to effectively manage learning strategies and self-education',
            'problem_solving': 'Critical thinking and problem-solving capabilities',
            'communication': 'Effective communication and expression skills',
            'social_and_personal': 'Interpersonal skills and self-development',
            'civic': 'Understanding civic responsibilities and democratic values',
            'digital': 'Digital literacy and technology competence',
            'work': 'Work habits and project management skills',
            'cultural_awareness': 'Cultural understanding and artistic expression'
        };

        // Update descriptions
        competencies.forEach(competency => {
            const descElement = document.getElementById(`${competency.id}-description`);
            if (descElement) {
                descElement.textContent = descriptions[competency.id] || '';
            }
        });

    } catch (error) {
        console.error('Error fetching competencies data:', error);
    }
}

// Call the function when the page loads
document.addEventListener('DOMContentLoaded', fetchAndRenderCompetencies); 