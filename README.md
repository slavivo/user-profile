# Student Profile and Concept Map System

A Flask-based web application for visualizing student profiles, competencies, and generating AI-powered concept maps for educational topics.

## Features

- **Student Profile Dashboard**: View and manage student information and academic progress
- **Interactive Concept Maps**: 
  - Visualize educational concepts using Cytoscape.js
  - AI-powered graph generation using OpenAI or Google Gemini
  - Hierarchical concept visualization with progress tracking
- **Competency Tracking**: 
  - Monitor progress across 8 key competency areas:
    - Learning Competency
    - Problem Solving
    - Communication
    - Social and Personal
    - Civic
    - Digital
    - Work
    - Cultural Awareness
  - Dynamic UI that displays only active competencies (scores > 0)
- **Activity Management**:
  - AI-powered activity generation with multiple creation modes
  - Structured activity data with learning goals, competencies, and taxonomy
  - Integrated student performance tracking
- **Personalization**:
  - Concept focus selection (polish, discover, or broaden)
  - Competency focus selection (target strong or weak areas)
  - AI-driven activity generation based on focus areas

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

## Core Directory Structure

```
.
├── app.py              # Main Flask application
├── utils/             # Core utilities and helper functions
├── prompts/           # AI prompt templates for various features
├── static/            # Frontend assets and JavaScript
├── templates/         # HTML templates and components
└── config.ini         # API configuration (not in git)
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

## Prompt System

The application uses a template-based prompt system for AI interactions. All prompts are stored as text files in the `prompts/` directory, making them easy to edit without touching the code.

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