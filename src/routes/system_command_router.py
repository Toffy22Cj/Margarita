# [file name]: src/routes/system_command_router.py
import re
from pathlib import Path
from .system_command_classifier import SystemCommandClassifier  # Import relativo
from src.system.system_executor import SystemCommandExecutor


class SystemCommandRouter:
    """
    Integra el clasificador y el ejecutor de comandos.
    """

    def __init__(self, config_file: str = "configs/apps_config.json"):
        self.classifier = SystemCommandClassifier()
        self.executor = SystemCommandExecutor(config_file)

    def handle_command(self, text: str) -> str:
        """
        Recibe un texto, lo clasifica y lo ejecuta.
        Devuelve el resultado como string.
        """
        result = self.classifier.classify(text)

        if result["confidence"] == "none" or result["type"] is None:
            return f"No entendí el comando: '{text}'"

        return self.executor.execute_command(result["type"], result["params"])

    def parse_folder_command(self, command: str) -> dict:
        """
        Analiza comandos de creación de carpetas para extraer nombre y ubicación.
        
        Ejemplos:
        - "crea una carpeta en documentos" → nombre: "nueva carpeta", ubicación: "documentos"
        - "crea carpeta proyectos en escritorio" → nombre: "proyectos", ubicación: "escritorio"
        - "crea una carpeta llamada mis archivos" → nombre: "mis archivos", ubicación: None
        """
        
        command_lower = command.lower()
        
        # Patrones para extraer nombre y ubicación
        patterns = [
            # Patrón: "crea [una] carpeta [llamada] <nombre> en <ubicación>"
            r'crea\s+(?:una\s+)?carpeta\s+(?:llamada\s+)?([^\n]+?)\s+en\s+([^\n]+)$',
            # Patrón: "crea [una] carpeta en <ubicación> [llamada] <nombre>"
            r'crea\s+(?:una\s+)?carpeta\s+en\s+([^\n]+?)\s+(?:llamada\s+)?([^\n]+)$',
            # Patrón: "crea carpeta <nombre>"
            r'crea\s+(?:una\s+)?carpeta\s+(.+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command_lower)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    # Determinar qué grupo es nombre y cuál ubicación
                    if 'en' in command_lower.split('carpeta')[-1].split(groups[0])[0]:
                        # Formato: "crea carpeta <nombre> en <ubicación>"
                        folder_name = groups[0].strip()
                        location = groups[1].strip()
                    else:
                        # Formato: "crea carpeta en <ubicación> <nombre>"
                        location = groups[0].strip()
                        folder_name = groups[1].strip()
                    
                    return {
                        "folder_name": folder_name,
                        "location": location,
                        "success": True
                    }
                elif len(groups) == 1:
                    # Solo nombre, sin ubicación
                    return {
                        "folder_name": groups[0].strip(),
                        "location": None,
                        "success": True
                    }
        
        return {
            "folder_name": None,
            "location": None,
            "success": False,
            "error": "No se pudo entender el comando de carpeta"
        }

    def handle_advanced_folder_command(self, command: str) -> str:
        """
        Maneja comandos avanzados de creación de carpetas con ubicación.
        """
        parsed = self.parse_folder_command(command)
        
        if not parsed["success"]:
            return f"❌ {parsed['error']}"
        
        folder_name = parsed["folder_name"]
        location = parsed["location"]
        
        if not folder_name:
            return "❌ No especificaste el nombre de la carpeta"
        
        # Si no hay ubicación específica, crear en base_path
        if not location:
            return self.executor.execute_command('create_folder', folder_name)
        
        # Buscar la ubicación especificada
        files_manager = self.executor.get_files_manager()
        search_result = files_manager.search_folder(location)
        
        if search_result["found"]:
            # Usar la primera coincidencia encontrada
            target_path = search_result["matches"][0]["path"]
            full_path = Path(target_path) / folder_name
            return self.executor.execute_command('create_folder', str(full_path))
        else:
            # La ubicación no existe, preguntar si crear
            return (f"❌ No encontré la ubicación '{location}'. "
                   f"¿Quieres crear la carpeta '{folder_name}' en tu directorio principal? "
                   f"(Responde 'sí' para crear o 'no' para cancelar)")


if __name__ == "__main__":
    import re
    router = SystemCommandRouter()

    print("=== Probador de Comandos del Sistema ===")
    print("Escribe comandos como:")
    print("- abre navegador")
    print("- crea carpeta proyectos")
    print("- crea carpeta documentos en escritorio")
    print("- crea una carpeta llamada mis archivos en documentos")
    print("Escribe 'salir' para terminar.\n")

    while True:
        user_input = input(">> ").strip()
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Adiós 👋")
            break

        # Procesar comandos de carpeta de manera avanzada
        if any(word in user_input.lower() for word in ['crea', 'carpeta']):
            response = router.handle_advanced_folder_command(user_input)
        else:
            response = router.handle_command(user_input)
        
        print(f"🤖 {response}")