# Student Profile and Concept Map System

A Flask-based web application for visualizing student profiles, competencies, and generating AI-powered concept maps for educational topics.

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

2. Choose your preferred installation method:

### Option A: Using pip (recommended for most users)

1. Create and activate a virtual environment:
   ```bash
   # On Linux/macOS:
   python -m venv venv
   source venv/bin/activate

   # On Windows (Command Prompt):
   python -m venv venv
   venv\Scripts\activate.bat

   # On Windows (PowerShell):
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option B: Using conda

1. Create and activate a conda environment:
   ```bash
   # On Linux/macOS/Windows:
   conda env create -f environment.yml
   conda activate user-profile
   ```

### Configuration

After installing dependencies, create a `config.ini` file in the root directory:
```ini
[DEFAULT]
OPENAI_KEY = your_openai_api_key
GENAI_KEY = your_google_gemini_api_key
```

### Running the Application

Start the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000` by default.

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

The application uses a template-based prompt system for AI interactions. All prompts are stored as text files in the `prompts/` directory. Here's a detailed overview of each prompt and its purpose:

### Activity Creation Prompts

The activity creation process is two-phased:

1. **Full Description Generation**
   - Located in `full_description_from_*.txt` files
   - Different modes based on input metadata:
     - `full_description_from_brief.txt`: Generates from brief description
     - `full_description_from_combined.txt`: Uses combined metadata (concepts, competencies, etc.)
     - `full_description_from_competencies.txt`: Focuses on specific competencies
     - `full_description_from_concepts.txt`: Based on selected concepts
     - `full_description_from_learning_goals.txt`: Uses existing learning goals
     - `full_description_from_taxonomy.txt`: Based on taxonomy classification

2. **Metadata Generation**
   - After full description is created, these prompts generate specific metadata:
     - `get_competencies.txt`: Extracts and scores relevant competencies
     - `get_taxonomy.txt`: Determines processing levels and knowledge domains
     - Learning goals selection (three-step process):
       1. `select_ovu_areas.txt`: Selects 1-2 most relevant Overall Value Understanding areas
       2. `select_topics.txt`: Identifies 1-3 most relevant topics from the selected areas
       3. `select_learning_goals.txt`: Chooses appropriate learning goals from the selected topics

### Learning Goals Generation

Used for generating learning goals in the knowledge graph:
- `graph_learning_goals_system.txt`: System prompt providing context and guidelines
- `graph_learning_goals_user.txt`: User prompt specifying the task and requirements
- These work together to ensure learning goals are properly integrated with the knowledge graph

### Methodology Processing

- `methodology_decompose.txt`: Used to break down teaching methodologies into individual activities
- Helps create structured activity sequences from higher-level pedagogical approaches

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