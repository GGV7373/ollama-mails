import requests
import json
from typing import Optional

OLLAMA_API_URL = "http://localhost:11434/api/generate"

class OllamaClient:
    """Client for interacting with Ollama AI models"""

    def __init__(self, model: str = "mistral", base_url: str = OLLAMA_API_URL):
        self.model = model
        self.base_url = base_url

    def generate_email(
        self,
        context: str,
        email_style: str = "professional",
        file_summaries: str = "",
        temperature: float = 0.7
    ) -> str:
        """
        Generate an email using the Ollama model.

        Args:
            context: User-provided context for the email
            email_style: Style of the email (professional, casual, short reply, business)
            file_summaries: Extracted text from uploaded files
            temperature: Model temperature for creativity (0.0 to 1.0)

        Returns:
            Generated email textError: 404 Client Error: Not Found for url: http://localhost:11434/api/generate
        """

        # Build the prompt
        prompt = self._build_prompt(context, email_style, file_summaries)

        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": temperature
                },
                timeout=300,  # 5 minutes timeout for generation
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "Error: No response from model").strip()

        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure Ollama is running on localhost:11434"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model took too long to generate."
        except Exception as e:
            return f"Error: {str(e)}"

    def _build_prompt(self, context: str, style: str, file_summaries: str) -> str:
        """Build the prompt for the AI model"""

        style_instructions = {
            "professional": "Write a professional, formal email with proper business tone.",
            "casual": "Write a casual, friendly email with a warm tone.",
            "short reply": "Write a brief, concise email reply (2-3 sentences).",
            "business": "Write a business email that is formal but friendly, suitable for corporate communication."
        }

        style_instruction = style_instructions.get(style, style_instructions["professional"])

        prompt = f"""You are an expert email writer. {style_instruction}

Context provided by the user:
{context}"""

        if file_summaries.strip():
            prompt += f"""

Additional context from uploaded files:
{file_summaries}"""

        prompt += """

Please write a clear, well-structured email based on the above context.
Start with an appropriate greeting and end with a professional closing.
Only provide the email text, nothing else."""

        return prompt

    def check_connection(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def list_available_models(self) -> list:
        """List available Ollama models"""
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except:
            return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            response = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": model_name},
                timeout=600  # 10 minutes timeout for model pulling
            )
            return response.status_code == 200
        except:
            return False

    def set_model(self, model_name: str) -> None:
        """Set the active model"""
        self.model = model_name
