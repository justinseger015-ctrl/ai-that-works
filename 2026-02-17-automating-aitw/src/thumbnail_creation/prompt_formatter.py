"""Prompt template formatting for thumbnail creation."""

from pathlib import Path


class PromptFormatter:
    """Handles loading and formatting of prompt templates."""
    
    def __init__(self, template_path: Path):
        """
        Initialize the prompt formatter.
        
        Args:
            template_path: Path to the prompt template file
        """
        self.template_path = template_path
        self._template: str | None = None
    
    def _load_template(self) -> str:
        """
        Load the template from file (cached after first load).
        
        Returns:
            The template string
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        if self._template is None:
            if not self.template_path.exists():
                raise FileNotFoundError(f"Template not found: {self.template_path}")
            
            with open(self.template_path, "r") as f:
                self._template = f.read()
        
        return self._template
    
    def format(
        self,
        title: str,
        subtitle: str,
        episode_number: str,
        feedback: str | None = None
    ) -> str:
        """
        Format the prompt template with the provided values.

        Args:
            title: The episode title
            subtitle: The episode subtitle
            episode_number: The episode number
            feedback: Optional feedback for image regeneration

        Returns:
            The formatted prompt string
        """
        template = self._load_template()
        prompt = template.format(
            title=title,
            subtitle=subtitle,
            episode_number=episode_number,
        )

        # Append feedback if provided
        if feedback:
            prompt += f"\n\nIMPORTANT USER FEEDBACK: {feedback}\nPlease incorporate this feedback when generating the image."

        return prompt

