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
├── utils.py           # Utility functions and API handling
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
- GPT-4O
- GPT-4O Mini
- GPT-3O Mini

## Graph Generation Process

1. **Initial Description**: The system first generates a free-form description of the concept relationships
2. **JSON Formatting**: The description is then formatted into a proper JSON structure
3. **Validation**: The JSON structure is validated for correct format and completeness
4. **Visualization**: The graph is rendered using Cytoscape.js with a hierarchical layout

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

## License

[Your chosen license]

## Contributing

[Your contribution guidelines] 