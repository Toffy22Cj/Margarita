# [file name]: src/system/system_executor.py
from .system_applications import SystemApplications
from .system_files import SystemFiles
from .system_info import SystemInfo
from .system_files_intelligent import IntelligentFileManager
from .conversation_manager import ConversationManager

class SystemCommandExecutor:
    """
    Orquestador principal que elige qué clase usar para cada comando
    """

    def __init__(self, config_file: str = "configs/apps_config.json", base_path=None):
        self.apps_manager = SystemApplications(config_file)
        self.files_manager = SystemFiles(base_path)
        self.info_manager = SystemInfo(base_path)
        self.intelligent_manager = IntelligentFileManager(base_path)
        self.conversation_manager = ConversationManager(self)
        
        print("[SystemCommandExecutor] Inicializado con todos los módulos incluyendo gestor inteligente")

    def execute_command(self, command_type: str, params) -> str:
        """Ejecuta un comando basado en el tipo y parámetros"""
        print(f"[Executor] Ejecutando comando: {command_type} con params: {params}")
        
        if command_type == 'open_app':
            return self.apps_manager.open_application(params)
        elif command_type == 'create_folder':
            # Si params es un diccionario (con nombre y ubicación)
            if isinstance(params, dict):
                folder_name = params.get('folder_name')
                location = params.get('location')
                result = self.intelligent_manager.smart_create_folder(folder_name, location)
                return result["message"]
            else:
                # Comando simple
                return self.files_manager.create_folder(params)
        elif command_type == 'create_file':
            # Si params es un diccionario (con nombre y ubicación)
            if isinstance(params, dict):
                file_name = params.get('file_name')
                location = params.get('location')
                result = self.intelligent_manager.smart_create_file(file_name, location)
                return result["message"]
            else:
                # Comando simple
                return self.files_manager.create_file(params)
        elif command_type == 'search_folder':
            result = self.files_manager.search_folder(params)
            return result["message"]
        elif command_type == 'system_info':
            return self.info_manager.get_system_info()
        else:
            return "Tipo de comando no reconocido"

    def get_applications_manager(self) -> SystemApplications:
        """Retorna el gestor de aplicaciones"""
        return self.apps_manager

    def get_files_manager(self) -> SystemFiles:
        """Retorna el gestor de archivos"""
        return self.files_manager

    def get_info_manager(self) -> SystemInfo:
        """Retorna el gestor de información del sistema"""
        return self.info_manager

    def get_intelligent_manager(self) -> IntelligentFileManager:
        """Retorna el gestor inteligente"""
        return self.intelligent_manager

    def get_conversation_manager(self) -> ConversationManager:
        """Retorna el gestor de conversación"""
        return self.conversation_manager


# Prueba rápida
if __name__ == "__main__":
    executor = SystemCommandExecutor()
    print("🔧 Probando ejecutor modular inteligente...")
    
    # Probar diferentes módulos
    print("\n📁 Probando creación inteligente de carpeta:")
    result = executor.intelligent_manager.smart_create_folder("test_inteligente", "Documentos")
    print(result["message"])
    
    print("\n📄 Probando creación inteligente de archivo:")
    result = executor.intelligent_manager.smart_create_file("notas.txt", "Documentos", "Contenido de prueba")
    print(result["message"])
    
    print("\n🔍 Probando búsqueda de carpetas:")
    print(executor.execute_command('search_folder', 'documentos'))
    
    print("\n💻 Probando información del sistema:")
    print(executor.execute_command('system_info', ''))