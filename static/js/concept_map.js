document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing concept map JS...');
    
    const saveButton = document.getElementById('save-graph');
    if (!saveButton) {
        console.error('Save graph button not found!');
        return;
    }
    
    console.log('Save button found, adding click listener...');
    saveButton.addEventListener('click', async function() {
        console.log('Save button clicked');
        try {
            const response = await fetch('/save_graph_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.error) {
                console.error('Error saving graph:', data.error);
                alert('Failed to save graph: ' + data.error);
            } else {
                console.log('Graph saved successfully');
                alert('Graph saved successfully!');
            }
        } catch (error) {
            console.error('Error saving graph:', error);
            alert('Failed to save graph. Please try again.');
        }
    });
    
    console.log('Concept map JS initialization complete');
}); 