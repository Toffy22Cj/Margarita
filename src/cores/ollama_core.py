import subprocess
import json
from typing import Optional


class OllamaCore:
    """
    Wrapper para modelos gestionados por Ollama.
    Permite enviar prompts y obtener respuestas de texto.
    """

    def __init__(self, model: str, provider: str = "ollama"):
        self.model = model
        self.provider = provider

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Llama al modelo usando `ollama run`.
        """
        try:
            cmd = ["ollama", "run", self.model]
            process = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate(prompt)

            if stderr:
                print(f"[OllamaCore:{self.model}] Error:", stderr)

            return stdout.strip()

        except Exception as e:
            return f"[ERROR OllamaCore:{self.model}] {e}"
