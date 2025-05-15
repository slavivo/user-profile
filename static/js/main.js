document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabs = document.querySelectorAll('nav a');
    const quickLinks = document.querySelectorAll('.tab-link');
    const contents = document.querySelectorAll('#profile, #concept-map, #competencies, #abilities-attitudes, #personalization');

    function switchTab(targetId) {
        // Update tab styles
        tabs.forEach(t => {
            if (t.getAttribute('href') === '#' + targetId) {
                t.classList.remove('border-transparent', 'text-gray-500');
                t.classList.add('border-indigo-500', 'text-indigo-600');
            } else {
                t.classList.remove('border-indigo-500', 'text-indigo-600');
                t.classList.add('border-transparent', 'text-gray-500');
            }
        });

        // Show corresponding content
        contents.forEach(content => {
            if (content.id === targetId) {
                content.classList.remove('hidden');
            } else {
                content.classList.add('hidden');
            }
        });
    }

    // Handle navigation tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = tab.getAttribute('href').substring(1);
            switchTab(targetId);
        });
    });

    // Handle quick links
    quickLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-tab');
            switchTab(targetId);
        });
    });
}); 