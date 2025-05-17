// Fetch and render abilities data
async function fetchAndRenderAbilities() {
    try {
        const [abilitiesResponse, attitudesResponse] = await Promise.all([
            fetch('/api/abilities'),
            fetch('/api/attitudes')
        ]);

        const abilities = await abilitiesResponse.json();
        const attitudes = await attitudesResponse.json();

        // Render cognitive abilities
        const cognitiveContainer = document.querySelector('#cognitive-abilities-container');
        if (cognitiveContainer && abilities.cognitive) {
            cognitiveContainer.innerHTML = abilities.cognitive.map(ability => `
                <div class="progress-bar-wrapper">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-sm font-medium text-gray-700">${ability.name}</span>
                        <span class="text-sm font-medium text-gray-700">${ability.value}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${ability.value}%"></div>
                    </div>
                </div>
            `).join('');
        }

        // Render social abilities
        const socialContainer = document.querySelector('#social-abilities-container');
        if (socialContainer && abilities.social) {
            socialContainer.innerHTML = abilities.social.map(ability => `
                <div class="progress-bar-wrapper">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-sm font-medium text-gray-700">${ability.name}</span>
                        <span class="text-sm font-medium text-gray-700">${ability.value}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${ability.value}%"></div>
                    </div>
                </div>
            `).join('');
        }

        // Render physical abilities
        const physicalContainer = document.querySelector('#physical-abilities-container');
        if (physicalContainer && abilities.physical) {
            physicalContainer.innerHTML = abilities.physical.map(ability => `
                <div class="progress-bar-wrapper">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-sm font-medium text-gray-700">${ability.name}</span>
                        <span class="text-sm font-medium text-gray-700">${ability.value}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${ability.value}%"></div>
                    </div>
                </div>
            `).join('');
        }

        // Render attitudes
        const attitudesContainer = document.querySelector('#attitudes-container');
        if (attitudesContainer && attitudes) {
            attitudesContainer.innerHTML = attitudes.map(attitude => `
                <div class="progress-bar-wrapper">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-sm font-medium text-gray-700">${attitude.name}</span>
                        <span class="text-sm font-medium text-gray-700">${attitude.value}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${attitude.value}%"></div>
                    </div>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error('Error fetching abilities data:', error);
    }
}

// Call the function when the page loads
document.addEventListener('DOMContentLoaded', fetchAndRenderAbilities); 