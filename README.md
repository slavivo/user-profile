# Student Profile and Concept Map System

A Flask-based web application for visualizing student profiles, competencies, and generating AI-powered concept maps for educational topics.

## Features

- **Student Profile Dashboard**: View and manage student information and academic progress
- **Interactive Concept Maps**: 
  - Visualize educational concepts using Cytoscape.js
  - AI-powered graph generation using OpenAI or Google Gemini
  - Hierarchical concept visualization with progress tracking
- **Competency Tracking**: Monitor progress across 8 key competency areas
- **Personalization**: (Coming soon) Customize learning paths and preferences

## Technology Stack

- **Backend**: Python/Flask
- **Frontend**: 
  - HTML/JavaScript
  - TailwindCSS for styling
  - Cytoscape.js for graph visualization
- **AI Integration**:
  - Google Gemini API
  - OpenAI API
  - Support for multiple model variants

## Project Structure

```
.
├── app.py              # Main Flask application
├── utils/
│   ├── base.py        # Core utility functions and prompt handling
│   └── template_handler.py  # Template system for prompts
├── prompts/           # AI prompt templates
│   ├── graph_generation.txt    # Knowledge graph generation
│   ├── initial_graph.txt       # Initial graph description
│   ├── reformatting.txt        # JSON structure formatting
│   ├── learning_goals.txt      # Learning goals generation
│   ├── connected_concepts.txt   # Concept connections
│   ├── competency.txt          # Competency analysis
│   └── taxonomy.txt            # Taxonomy classification
├── static/
│   └── js/
│       └── graph.js   # Graph visualization and interaction logic
├── templates/
│   └── index.html     # Main application template
├── config.ini         # API configuration (not in git)
└── requirements.txt   # Python dependencies
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `config.ini` file in the root directory:
   ```ini
   [DEFAULT]
   OPENAI_KEY = your_openai_api_key
   GENAI_KEY = your_google_gemini_api_key
   ```

5. Run the application:
   ```bash
   python app.py
   ```

## API Configuration

The application supports two AI providers:

### Google Gemini Models
- Gemini 2.0 Flash (default)
- Gemini 2.5 Flash
- Gemini 2.5 Pro

### OpenAI Models
- GPT-4o
- GPT-4o Mini
- GPT-3o Mini

## Graph Generation Process

1. **Initial Description**: The system first generates a free-form description of the concept relationships
2. **JSON Formatting**: The description is then formatted into a proper JSON structure
3. **Validation**: The JSON structure is validated for correct format and completeness
4. **Visualization**: The graph is rendered using Cytoscape.js with a hierarchical layout

## Prompt System

The application uses a template-based prompt system for AI interactions. All prompts are stored as text files in the `prompts/` directory, making them easy to edit without touching the code.

### Available Prompts

1. **graph_generation.txt**: Generates a knowledge graph for a concept
2. **initial_graph.txt**: Creates initial description of concept relationships
3. **reformatting.txt**: Converts descriptions to JSON structure
4. **learning_goals.txt**: Generates learning goals for activities
5. **connected_concepts.txt**: Identifies related concepts
6. **competency.txt**: Analyzes competency development
7. **taxonomy.txt**: Classifies activities using Marzano's Taxonomy

### Editing Prompts

Prompts use a simple template syntax with variables denoted by `${variable_name}`. For example:

```
Activity Name: ${name}
Description: ${description}
```

To edit a prompt:

1. Navigate to the `prompts/` directory
2. Open the desired .txt file in any text editor
3. Modify the text while keeping the ${variable} placeholders intact
4. Save the file

#### Important Guidelines

- **DO NOT** change or remove the ${variable} placeholders
- **DO NOT** rename the prompt files
- Keep the JSON format examples in the prompts if they exist
- Maintain clear formatting and structure
- Test changes with different concepts/activities

#### Available Variables

Different prompts use different variables:

- `${concept}`: Used in graph-related prompts
- `${name}`: Activity name
- `${description}`: Activity description
- `${goals_text}`: Formatted learning goals
- `${initial_response}`: Initial graph description

### Example Prompt Edit

Original in `learning_goals.txt`:
```
Based on the following activity, identify 3-5 specific learning goals:
Activity Name: ${name}
Description: ${description}
```

Modified version:
```
Based on the following activity, identify 4-6 detailed learning goals:
Activity Name: ${name}
Description: ${description}

Please ensure each goal is:
1. Highly specific and measurable
2. Starts with a strong action verb
3. Focuses on one clear outcome
```

## Development

### Adding New Features

1. Backend changes go in `app.py` or `utils.py`
2. Frontend JavaScript changes go in `static/js/graph.js`
3. UI changes go in `templates/index.html`

### Code Style

- Python: Follow PEP 8 guidelines
- JavaScript: Use modern ES6+ features
- HTML/CSS: Follow TailwindCSS conventions

## Security Notes

- Never commit `config.ini` or any files containing API keys
- Use environment variables in production
- Keep dependencies updated for security patches