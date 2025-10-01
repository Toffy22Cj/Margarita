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
        """Limpia parámetros preservando mayúsculas"""
        if not param:
            return None
        safe = re.sub(r'[<>:"/\\|?*]', '', param).strip()
        return safe if safe else None

    def parse_complex_folder_command(self, text: str) -> dict:
        """
        Análisis especializado para comandos complejos de carpeta
        """
        text_lower = text.lower().strip()  # Solo para matching
        
        print(f"[Classifier] Analizando comando complejo: {text}")
        
        # Patrón 1: "crea carpeta <nombre> en <ubicación>"
        pattern1 = r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?([^\n]+?)\s+en\s+([^\n]+)'
        match1 = re.search(pattern1, text_lower)
        if match1:
            # Extraer del texto ORIGINAL para preservar mayúsculas
            start1, end1 = match1.span(1)
            start2, end2 = match1.span(2)
            folder_name = self.sanitize_param(text[start1:end1])
            location = self.sanitize_param(text[start2:end2])
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
            # Extraer del texto ORIGINAL para preservar mayúsculas
            start1, end1 = match2.span(1)
            start2, end2 = match2.span(2)
            location = self.sanitize_param(text[start1:end1])
            folder_name = self.sanitize_param(text[start2:end2])
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
            # Extraer del texto ORIGINAL para preservar mayúsculas
            start, end = match3.span(1)
            location = self.sanitize_param(text[start:end])
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
            # Extraer del texto ORIGINAL para preservar mayúsculas
            start1, end1 = match.span(1)
            start2, end2 = match.span(2)
            return {
                'type': 'create_file',
                'params': {
                    'file_name': self.sanitize_param(text[start1:end1]),
                    'location': self.sanitize_param(text[start2:end2])
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
                    
                    # Comandos con parámetros simples - extraer del texto original
                    if match.group(1):
                        start, end = match.span(1)
                        raw_param = text[start:end].strip()
                    else:
                        raw_param = None
                    
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
        "crea una carpeta en Documentos",
        "crea carpeta Proyectos en Escritorio", 
        "crea una carpeta llamada Mis Archivos en Documentos",
        "crea archivo Notas.txt en Documentos",
        "abre navegador"
    ]
    
    print("🔧 Probando clasificador MEJORADO:")
    for cmd in test_commands:
        result = classifier.classify(cmd)
        print(f"\n📝 Comando: '{cmd}'")
        print(f"   Tipo: {result['type']}")
        print(f"   Parámetros: {result['params']}")
        print(f"   Confianza: {result['confidence']}")