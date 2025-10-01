# [file name]: src/routes/system_command_classifier.py
import re
import os

class SystemCommandClassifier:
    """
    Clasificador de comandos del sistema MEJORADO
    """

    def __init__(self):
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
                # Patrones básicos (sin ubicación)
                r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?(.+)$',
                r'make\s+(?:a\s+)?folder\s+(?:called\s+)?(.+)$',
                r'nueva\s+carpeta\s+(.+)$',
            ],
            'create_file': [
                r'crea\s+(?:un\s+)?archivo\s+(?:llamado\s+)?(.+)',
                r'create\s+(?:a\s+)?file\s+(?:called\s+)?(.+)',
                r'nuevo\s+archivo\s+(.+)',
            ],
            'search_folder': [
                r'busca\s+(?:la\s+)?carpeta\s+(.+)',
                r'encuentra\s+(?:la\s+)?carpeta\s+(.+)',
                r'search\s+(?:for\s+)?folder\s+(.+)',
            ],
            'system_info': [
                r'informaci[oó]n\s+del\s+sistema',
                r'system\s+information',
                r'system\s+info',
            ]
        }

    def sanitize_param(self, param: str) -> str:
        """Limpia parámetros"""
        if not param:
            return None
        safe = re.sub(r'[<>:"/\\|?*]', '', param).strip()
        return safe if safe else None

    def parse_complex_folder_command(self, text: str) -> dict:
        """
        Análisis especializado para comandos complejos de carpeta
        """
        text_lower = text.lower().strip()
        
        print(f"[Classifier] Analizando comando complejo: {text}")
        
        # Patrón 1: "crea carpeta <nombre> en <ubicación>"
        pattern1 = r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?([^\n]+?)\s+en\s+([^\n]+)'
        match1 = re.search(pattern1, text_lower)
        if match1:
            folder_name = self.sanitize_param(match1.group(1))
            location = self.sanitize_param(match1.group(2))
            print(f"[Classifier] Patrón 1: nombre='{folder_name}', ubicación='{location}'")
            return {
                'type': 'create_folder',
                'params': {'folder_name': folder_name, 'location': location},
                'matched_text': text,
                'confidence': 'high'
            }
        
        # Patrón 2: "crea carpeta en <ubicación> <nombre>"
        pattern2 = r'crea\s+(?:una\s+)?carpeta\s+en\s+([^\n]+?)\s+(?:llamada\s+)?([^\n]+)'
        match2 = re.search(pattern2, text_lower)
        if match2:
            location = self.sanitize_param(match2.group(1))
            folder_name = self.sanitize_param(match2.group(2))
            print(f"[Classifier] Patrón 2: nombre='{folder_name}', ubicación='{location}'")
            return {
                'type': 'create_folder',
                'params': {'folder_name': folder_name, 'location': location},
                'matched_text': text,
                'confidence': 'high'
            }
        
        # Patrón 3: "crea carpeta en <ubicación>" (sin nombre)
        pattern3 = r'crea\s+(?:una\s+)?carpeta\s+en\s+([^\n]+)'
        match3 = re.search(pattern3, text_lower)
        if match3:
            location = self.sanitize_param(match3.group(1))
            print(f"[Classifier] Patrón 3: ubicación='{location}' (sin nombre)")
            return {
                'type': 'create_folder',
                'params': {'folder_name': None, 'location': location},
                'matched_text': text,
                'confidence': 'high'
            }
        
        return None

    def parse_complex_file_command(self, text: str) -> dict:
        """Análisis para comandos de archivo con ubicación"""
        text_lower = text.lower().strip()
        
        # Patrón: "crea archivo <nombre> en <ubicación>"
        pattern = r'crea\s+(?:un\s+)?archivo\s+(?:llamado\s+)?([^\n]+?)\s+en\s+([^\n]+)'
        match = re.search(pattern, text_lower)
        if match:
            return {
                'type': 'create_file',
                'params': {
                    'file_name': self.sanitize_param(match.group(1)),
                    'location': self.sanitize_param(match.group(2))
                },
                'matched_text': text,
                'confidence': 'high'
            }
        
        return None

    def classify(self, text: str) -> dict:
        """
        Clasifica comandos con análisis complejo primero
        """
        text_lower = text.lower().strip()
        
        print(f"[Classifier] Clasificando: '{text}'")
        
        # PRIMERO: Análisis complejo para comandos con ubicación
        if any(word in text_lower for word in ['crea', 'carpeta']):
            folder_result = self.parse_complex_folder_command(text)
            if folder_result:
                return folder_result
        
        if any(word in text_lower for word in ['crea', 'archivo', 'file']):
            file_result = self.parse_complex_file_command(text)
            if file_result:
                return file_result
        
        # SEGUNDO: Búsqueda normal por patrones
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Comandos sin parámetros
                    if command_type == 'system_info':
                        return {
                            'type': command_type,
                            'params': '',
                            'matched_text': text,
                            'confidence': 'high'
                        }
                    
                    # Comandos con parámetros simples
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


# Pruebas
if __name__ == "__main__":
    classifier = SystemCommandClassifier()
    
    test_commands = [
        "crea una carpeta en documentos",
        "crea carpeta proyectos en escritorio", 
        "crea una carpeta llamada mis archivos en documentos",
        "crea archivo notas.txt en documentos",
        "abre navegador"
    ]
    
    print("🔧 Probando clasificador MEJORADO:")
    for cmd in test_commands:
        result = classifier.classify(cmd)
        print(f"\n📝 Comando: '{cmd}'")
        print(f"   Tipo: {result['type']}")
        print(f"   Parámetros: {result['params']}")
        print(f"   Confianza: {result['confidence']}")