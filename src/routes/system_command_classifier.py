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
                r'run\s+(.+)',
                r'lanzar\s+(.+)',
                r'start\s+(.+)'
            ],
            'create_folder': [
                # Patrones básicos
                r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?(.+)',
                r'make\s+(?:a\s+)?folder\s+(?:called\s+)?(.+)',
                r'nueva\s+carpeta\s+(.+)',
                r'crear\s+(?:una\s+)?carpeta\s+(.+)',
                
                # Patrones con ubicación
                r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?([^\\n]+?)\s+en\s+([^\\n]+)',
                r'crea\s+(?:una\s+)?carpeta\s+en\s+([^\\n]+?)\s+(?:llamada\s+)?([^\\n]+)',
                r'make\s+(?:a\s+)?folder\s+(?:called\s+)?([^\\n]+?)\s+in\s+([^\\n]+)',
                r'make\s+(?:a\s+)?folder\s+in\s+([^\\n]+?)\s+(?:called\s+)?([^\\n]+)'
            ],
            'create_file': [
                r'crea\s+(?:un\s+)?archivo\s+(?:llamado\s+)?(.+)',
                r'haz\s+(?:un\s+)?archivo\s+(.+)',
                r'create\s+(?:a\s+)?file\s+(?:called\s+)?(.+)',
                r'nuevo\s+archivo\s+(.+)',
                r'crear\s+(?:un\s+)?archivo\s+(.+)'
            ],
            'search_folder': [
                r'busca\s+(?:la\s+)?carpeta\s+(.+)',
                r'encuentra\s+(?:la\s+)?carpeta\s+(.+)',
                r'localiza\s+(?:la\s+)?carpeta\s+(.+)',
                r'search\s+(?:for\s+)?folder\s+(.+)',
                r'find\s+(?:the\s+)?folder\s+(.+)',
                r'locate\s+(?:the\s+)?folder\s+(.+)'
            ],
            'system_info': [
                r'informaci[oó]n\s+del\s+sistema',
                r'muestra\s+(?:la\s+)?informaci[oó]n\s+del\s+sistema',
                r'sistema\s+info',
                r'system\s+information',
                r'system\s+info',
                r'muestra\s+el\s+sistema'
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

    def _extract_folder_params(self, match_groups: tuple, pattern_type: str) -> dict:
        """
        Extrae parámetros para comandos de carpeta, manejando ubicaciones.
        """
        if not match_groups:
            return {"folder_name": None, "location": None}
        
        groups = [g for g in match_groups if g]  # Filtrar grupos None
        
        if len(groups) == 1:
            # Comando simple: "crea carpeta proyectos"
            return {"folder_name": self.sanitize_param(groups[0]), "location": None}
        
        elif len(groups) >= 2:
            # Comando con ubicación
            if pattern_type == "location_first":
                # "crea carpeta en documentos proyectos"
                return {
                    "folder_name": self.sanitize_param(groups[1]),
                    "location": self.sanitize_param(groups[0])
                }
            else:
                # "crea carpeta proyectos en documentos"
                return {
                    "folder_name": self.sanitize_param(groups[0]),
                    "location": self.sanitize_param(groups[1])
                }
        
        return {"folder_name": None, "location": None}

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
                    # Comandos sin parámetros (system_info)
                    if command_type == 'system_info':
                        return {
                            'type': command_type,
                            'params': '',
                            'matched_text': text,
                            'confidence': 'high'
                        }
                    
                    # Comandos de carpeta con ubicación
                    elif command_type == 'create_folder' and len(match.groups()) >= 2:
                        if 'en' in pattern or 'in' in pattern:
                            # Determinar el tipo de patrón
                            pattern_type = "location_first" if pattern.find('en') < pattern.find('llamada') else "name_first"
                            folder_params = self._extract_folder_params(match.groups(), pattern_type)
                            
                            if folder_params["folder_name"]:
                                return {
                                    'type': command_type,
                                    'params': folder_params,
                                    'matched_text': text,
                                    'confidence': 'high'
                                }
                    
                    # Comandos normales con un parámetro
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

    def parse_complex_command(self, text: str) -> dict:
        """
        Método adicional para análisis más detallado de comandos complejos.
        Útil para comandos que necesitan procesamiento especial.
        """
        text_lower = text.lower().strip()
        
        # Análisis específico para comandos de carpeta con ubicación
        folder_patterns = [
            # "crea carpeta <nombre> en <ubicación>"
            r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?([^\\n]+?)\s+en\s+([^\\n]+)',
            # "crea carpeta en <ubicación> <nombre>"
            r'crea\s+(?:una\s+)?carpeta\s+en\s+([^\\n]+?)\s+(?:llamada\s+)?([^\\n]+)',
            # "crea una carpeta en <ubicación>"
            r'crea\s+(?:una\s+)?carpeta\s+en\s+([^\\n]+)'
        ]
        
        for pattern in folder_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return {
                        'type': 'create_folder',
                        'params': {
                            'folder_name': self.sanitize_param(groups[0]),
                            'location': self.sanitize_param(groups[1])
                        },
                        'complex': True
                    }
                elif len(groups) == 1:
                    return {
                        'type': 'create_folder',
                        'params': {
                            'folder_name': 'nueva carpeta',  # Nombre por defecto
                            'location': self.sanitize_param(groups[0])
                        },
                        'complex': True
                    }
        
        return {'type': None, 'complex': False}


# Función de prueba
if __name__ == "__main__":
    classifier = SystemCommandClassifier()
    
    test_commands = [
        "crea una carpeta en documentos",
        "crea carpeta proyectos en escritorio", 
        "crea una carpeta llamada mis archivos en documentos",
        "abre navegador",
        "información del sistema",
        "crea archivo notas.txt"
    ]
    
    print("🔧 Probando clasificador de comandos:")
    for cmd in test_commands:
        result = classifier.classify(cmd)
        complex_result = classifier.parse_complex_command(cmd)
        
        print(f"\n📝 Comando: '{cmd}'")
        print(f"   Clasificación: {result['type']} (confianza: {result['confidence']})")
        print(f"   Parámetros: {result['params']}")
        if complex_result['complex']:
            print(f"   🎯 Análisis complejo: {complex_result}")