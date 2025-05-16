import os
from string import Template
from pathlib import Path

class PromptTemplate:
    _template_cache = {}
    
    @classmethod
    def get_template(cls, template_name: str) -> Template:
        """
        Load and cache a template file.
        
        Args:
            template_name: Name of the template file without extension
            
        Returns:
            Template object
        """
        if template_name not in cls._template_cache:
            # Get the project root directory (where app.py is located)
            project_root = Path(__file__).parent.parent
            template_path = project_root / 'prompts' / f'{template_name}.txt'
            
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                cls._template_cache[template_name] = Template(template_content)
            except FileNotFoundError:
                raise FileNotFoundError(f"Template file {template_name}.txt not found in prompts directory")
            
        return cls._template_cache[template_name]
    
    @classmethod
    def render(cls, template_name: str, **kwargs) -> str:
        """
        Render a template with the given variables.
        
        Args:
            template_name: Name of the template file without extension
            **kwargs: Variables to substitute in the template
            
        Returns:
            Rendered template string
        """
        template = cls.get_template(template_name)
        try:
            return template.substitute(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing required variable in template {template_name}: {e}") 