# [file name]: system_command_classifier.py
import re
import os

class SystemCommandClassifier:
    """
    Clasificador de comandos del sistema para ejecutar acciones.
    Detecta patrones comunes y extrae parámetros de forma segura.
    """

    def __init__(self):
        # Diccionario de patrones, fácil de ampliar
        self.command_patterns = {
            'open_app': [
                r'abre\s+(.+)', 
                r'inicia\s+(.+)', 
                r'ejecuta\s+(.+)',
                r'open\s+(.+)',
                r'run\s+(.+)'
            ],
            'create_folder': [
                r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?(.+)',
                r'make\s+(?:a\s+)?folder\s+(?:called\s+)?(.+)',
                r'nueva\s+carpeta\s+(.+)'
            ],
            'create_file': [
                r'crea\s+(?:un\s+)?archivo\s+(?:llamado\s+)?(.+)',
                r'haz\s+(?:un\s+)?archivo\s+(.+)',
                r'create\s+(?:a\s+)?file\s+(?:called\s+)?(.+)',
                r'nuevo\s+archivo\s+(.+)'
            ]
        }

    def sanitize_param(self, param: str) -> str:
        """
        Limpia el parámetro para evitar caracteres inválidos o peligrosos.
        """
        if not param:
            return None
        # Quitar caracteres no permitidos en nombres de archivo/carpeta
        safe = re.sub(r'[<>:"/\\|?*]', '', param).strip()
        return safe if safe else None

    def classify(self, text: str) -> dict:
        """
        Detecta si el texto contiene un comando del sistema y extrae parámetros.
        Returns: {'type': command_type, 'params': extracted_params, 'matched_text': text, 'confidence': str}
        """
        text_lower = text.lower().strip()

        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    raw_param = match.group(1).strip() if match.group(1) else None
                    param = self.sanitize_param(raw_param)

                    return {
                        'type': command_type,
                        'params': param,
                        'matched_text': text,
                        'confidence': 'high' if param else 'medium'
                    }

        return {
            'type': None,
            'params': None,
            'matched_text': text,
            'confidence': 'none'
        }
