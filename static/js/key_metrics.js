// Fetch and render key metrics data
async function fetchAndRenderKeyMetrics() {
    try {
        const [abilitiesResponse, attitudesResponse] = await Promise.all([
            fetch('/api/abilities'),
            fetch('/api/attitudes')
        ]);

        const abilities = await abilitiesResponse.json();
        const attitudes = await attitudesResponse.json();

        // Get all abilities in a flat array with their values
        const allAbilities = [
            ...abilities.cognitive.map(a => ({ name: a.name, value: a.value })),
            ...abilities.social.map(a => ({ name: a.name, value: a.value })),
            ...abilities.physical.map(a => ({ name: a.name, value: a.value }))
        ];

        // Sort abilities by value and get top 3
        const topAbilities = allAbilities
            .sort((a, b) => b.value - a.value)
            .slice(0, 3);

        // Sort attitudes by value and get top 3
        const topAttitudes = attitudes
            .sort((a, b) => b.value - a.value)
            .slice(0, 3)
            .map(a => ({ name: a.name, value: a.value }));

        // Render top abilities
        const topAbilitiesContainer = document.querySelector('#top-abilities-container');
        if (topAbilitiesContainer) {
            topAbilitiesContainer.innerHTML = topAbilities.map(ability => `
                <li class="flex items-center justify-between">
                    <span class="text-sm text-gray-600">${ability.name}</span>
                    <span class="text-sm font-medium text-indigo-600">${ability.value}%</span>
                </li>
            `).join('');
        }

        // Render key attitudes
        const keyAttitudesContainer = document.querySelector('#key-attitudes-container');
        if (keyAttitudesContainer) {
            keyAttitudesContainer.innerHTML = topAttitudes.map(attitude => `
                <li class="flex items-center justify-between">
                    <span class="text-sm text-gray-600">${attitude.name}</span>
                    <span class="text-sm font-medium text-indigo-600">${attitude.value}%</span>
                </li>
            `).join('');
        }

    } catch (error) {
        console.error('Error fetching key metrics data:', error);
    }
}

// Call the function when the page loads
document.addEventListener('DOMContentLoaded', fetchAndRenderKeyMetrics); 