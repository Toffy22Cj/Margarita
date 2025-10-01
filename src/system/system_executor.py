from .system_applications import SystemApplications
from .system_files import SystemFiles
from .system_info import SystemInfo

class SystemCommandExecutor:
    """
    Orquestador principal que elige qué clase usar para cada comando
    """

    def __init__(self, config_file: str = "configs/apps_config.json", base_path=None):
        self.apps_manager = SystemApplications(config_file)
        self.files_manager = SystemFiles(base_path)
        self.info_manager = SystemInfo(base_path)
        
        print("[SystemCommandExecutor] Inicializado con todos los módulos")

    def execute_command(self, command_type: str, params: str) -> str:
        """Ejecuta un comando basado en el tipo y parámetros"""
        if command_type == 'open_app':
            return self.apps_manager.open_application(params)
        elif command_type == 'create_folder':
            return self.files_manager.create_folder(params)
        elif command_type == 'create_file':
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


# Prueba rápida
if __name__ == "__main__":
    executor = SystemCommandExecutor()
    print("🔧 Probando ejecutor modular...")
    
    # Probar diferentes módulos
    print("\n📁 Probando creación de carpeta:")
    print(executor.execute_command('create_folder', 'test_modular'))
    
    print("\n🔍 Probando búsqueda de carpetas:")
    print(executor.execute_command('search_folder', 'documentos'))
    
    print("\n💻 Probando información del sistema:")
    print(executor.execute_command('system_info', ''))
    
    print("\n🖥️ Probando apertura de aplicación:")
    print(executor.execute_command('open_app', 'navegador'))