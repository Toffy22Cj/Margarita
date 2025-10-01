# [file name]: intent_classifier.py (completo y corregido)
import re
import json
from pathlib import Path

class IntentClassifier:
    """
    Clasificador de intención mejorado para decidir qué núcleo usar.
    """

    def __init__(self):
        self.system_keywords = [
            "abre", "inicia", "ejecuta", "crea", "haz", "nueva", "nuevo",
            "carpeta", "archivo", "open", "run", "make", "create", "folder", "file"
        ]
        
        self.system_patterns = [
            r'(abre|inicia|ejecuta)\s+(el|la|un|una)?\s*([^\s\.]+)',
            r'(crea|haz)\s+(una?\s+)?(carpeta|archivo)\s+(llamad[ao]?\s+)?([^\s\.]+)',
            r'(nuev[ao])\s+(carpeta|archivo)\s+([^\s\.]+)'
        ]

        # Cargar apps conocidas
        config_file = Path(__file__).resolve().parent.parent / "config" / "apps_config.json"
        self.known_apps = []
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    self.known_apps = list(json.load(f).keys())
                print(f"[IntentClassifier] Apps conocidas cargadas: {len(self.known_apps)}")
            except Exception as e:
                print(f"[IntentClassifier] Error cargando apps_config: {e}")

    def classify(self, text: str) -> str:
        text_l = text.lower().strip()
        
        # Si está vacío, conversación por defecto
        if not text_l:
            return "conversational"

        # --- Comandos del sistema (con patrones más precisos) ---
        # Verificar palabras clave primero
        has_system_keyword = any(
            re.search(rf'\b{re.escape(keyword)}\b', text_l) 
            for keyword in self.system_keywords
        )
        
        # Verificar patrones específicos
        has_system_pattern = any(
            re.search(pattern, text_l) 
            for pattern in self.system_patterns
        )
        
        # Verificar nombres de aplicaciones conocidas
        matches_app_name = any(
            re.search(rf'\b{re.escape(app)}\b', text_l) 
            for app in self.known_apps
        )
        
        if has_system_keyword or has_system_pattern or matches_app_name:
            return "system_command"

        # --- Traducción ---
        if re.search(r'\b(traduc|translate)\w*\b', text_l):
            return "translator_llm"

        # --- Programación / código ---
        code_keywords = ["código", "codigo", "programa", "python", "java", "javascript", 
                        "function", "función", "error", "debug", "variable", "clase",
                        "html", "css", "sql", "git", "commit", "repositorio"]
        
        if any(re.search(rf'\b{re.escape(keyword)}\b', text_l) for keyword in code_keywords):
            return "coder"

        # Por defecto: conversación
        return "conversational"

    def debug_classify(self, text: str) -> dict:
        """
        Versión de depuración que muestra por qué se tomó cada decisión.
        """
        text_l = text.lower().strip()
        debug_info = {
            'input': text,
            'final_intent': 'conversational',
            'reasons': []
        }
        
        if not text_l:
            debug_info['reasons'].append("Texto vacío -> conversación por defecto")
            return debug_info

        # Comandos del sistema
        system_keywords_found = [
            keyword for keyword in self.system_keywords 
            if re.search(rf'\b{re.escape(keyword)}\b', text_l)
        ]
        
        system_patterns_found = [
            pattern for pattern in self.system_patterns 
            if re.search(pattern, text_l)
        ]
        
        app_names_found = [
            app for app in self.known_apps 
            if re.search(rf'\b{re.escape(app)}\b', text_l)
        ]
        
        if system_keywords_found or system_patterns_found or app_names_found:
            debug_info['final_intent'] = 'system_command'
            if system_keywords_found:
                debug_info['reasons'].append(f"Palabras clave de sistema: {system_keywords_found}")
            if system_patterns_found:
                debug_info['reasons'].append(f"Patrones de sistema encontrados: {len(system_patterns_found)}")
            if app_names_found:
                debug_info['reasons'].append(f"Apps conocidas detectadas: {app_names_found}")
        
        # Traducción
        elif re.search(r'\b(traduc|translate)\w*\b', text_l):
            debug_info['final_intent'] = 'translator_llm'
            debug_info['reasons'].append("Palabra clave de traducción detectada")
        
        # Programación
        else:
            code_keywords_found = [
                keyword for keyword in [
                    "código", "codigo", "programa", "python", "java", "javascript", 
                    "function", "función", "error", "debug", "variable", "clase"
                ] if re.search(rf'\b{re.escape(keyword)}\b', text_l)
            ]
            
            if code_keywords_found:
                debug_info['final_intent'] = 'coder'
                debug_info['reasons'].append(f"Palabras clave de programación: {code_keywords_found}")
            else:
                debug_info['reasons'].append("Sin palabras clave específicas -> conversación por defecto")
        
        return debug_info

    def get_known_apps(self) -> list:
        """Retorna la lista de aplicaciones conocidas"""
        return self.known_apps


def classify_with_context(self, text: str, has_pending_action: bool = False) -> str:
    """
    Clasifica intención considerando el contexto de conversación
    """
    if has_pending_action:
        # Si hay acción pendiente, priorizar el procesamiento de la respuesta
        return "conversation_response"
    
    return self.classify(text)

# Función de prueba rápida
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    test_cases = [
        "abre navegador",
        "inicia la calculadora",
        "crea una carpeta",
        "traduce esto",
        "ayuda con código python",
        "hola cómo estás"
    ]
    
    for text in test_cases:
        print(f"'{text}' -> {classifier.classify(text)}")
        debug = classifier.debug_classify(text)
        print(f"   Debug: {debug['reasons']}\n")


        # En intent_classifier.py, agrega este método a la clase:
