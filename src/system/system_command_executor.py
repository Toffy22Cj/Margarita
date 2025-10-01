# [file name]: system_command_executor.py (completamente corregido)
import os
import re
import json
import subprocess
import platform
import shutil
from pathlib import Path

class SystemCommandExecutor:
    """
    Ejecuta comandos del sistema de forma segura con soporte para configuración personalizada.
    """

    def __init__(self, config_file: str = "configs/apps_config.json", base_path=None):
        self.system = platform.system()
        self.base_path = Path(base_path) if base_path else Path.home()
        
        # Corregir la ruta del archivo de configuración
        current_dir = Path(__file__).resolve().parent.parent
        self.config_file = current_dir / config_file
        
        # Crear directorio config si no existe
        self.config_file.parent.mkdir(exist_ok=True)
        
        self.applications = self._load_application_mappings()
        print(f"[SystemCommandExecutor] Sistema detectado: {self.system}")
        print(f"[SystemCommandExecutor] Configuración cargada desde: {self.config_file}")
        print(f"[SystemCommandExecutor] Aplicaciones cargadas: {list(self.applications.keys())}")

    def _default_app_mappings(self):
        """Mapeo por defecto según el sistema operativo"""
        if self.system == "Linux":
            return {
                'navegador': 'microsoft-edge-stable',
                'firefox': 'firefox',
                'chrome': 'google-chrome',
                'edge': 'microsoft-edge-stable',
                'calculadora': 'gnome-calculator',
                'editor': 'gnome-text-editor',
                'terminal': 'gnome-terminal',
                'archivos': 'nautilus',
                'documentos': 'libreoffice',
                'writer': 'libreoffice --writer',
                'excel': 'libreoffice --calc',
                'libreoffice': 'libreoffice'
            }
        elif self.system == "Windows":
            return {
                'navegador': 'msedge',
                'edge': 'msedge',
                'chrome': 'chrome',
                'calculadora': 'calc.exe',
                'editor': 'notepad.exe',
                'terminal': 'cmd.exe',
                'archivos': 'explorer.exe',
                'documentos': 'winword.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
                'notepad': 'notepad.exe'
            }
        else:  # macOS
            return {
                'navegador': 'Safari',
                'safari': 'Safari',
                'chrome': 'Google Chrome',
                'edge': 'Microsoft Edge',
                'calculadora': 'Calculator',
                'editor': 'TextEdit',
                'terminal': 'Terminal',
                'archivos': 'Finder'
            }

    def _load_application_mappings(self):
        """
        Carga el mapeo de aplicaciones desde config/apps_config.json si existe,
        si no, usa los valores por defecto según el sistema operativo.
        """
        # Si el archivo de configuración existe, cargarlo
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_apps = json.load(f)
                print(f"[SystemCommandExecutor] Configuración cargada desde: {self.config_file}")
                return user_apps
            except Exception as e:
                print(f"[WARN] No se pudo cargar {self.config_file}: {e}")
        
        # Si no existe, crear uno con los valores por defecto
        default_apps = self._default_app_mappings()
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(default_apps, f, indent=2, ensure_ascii=False)
            print(f"[SystemCommandExecutor] Archivo de configuración creado: {self.config_file}")
        except Exception as e:
            print(f"[WARN] No se pudo crear el archivo de configuración: {e}")
        
        return default_apps

    def _find_application(self, app_name: str):
        """
        Busca una aplicación en el sistema usando diferentes estrategias.
        Retorna el comando ejecutable si lo encuentra.
        """
        app_name_lower = app_name.lower()
        
        # Estrategia 1: Buscar en el mapeo configurado
        for key, command in self.applications.items():
            if re.search(rf"\b{re.escape(key)}\b", app_name_lower):
                return command, key
        
        # Estrategia 2: Buscar directamente en el PATH
        if shutil.which(app_name):
            return app_name, app_name
        
        # Estrategia 3: Para Windows, probar con extensiones comunes
        if self.system == "Windows":
            for ext in ['.exe', '.com', '.bat', '.cmd']:
                if shutil.which(app_name + ext):
                    return app_name + ext, app_name
        
        return None, app_name

    def open_application(self, app_name: str) -> str:
        """Abre una aplicación usando la mejor estrategia disponible"""
        command, found_name = self._find_application(app_name)
        
        if not command:
            return f"No pude encontrar la aplicación '{app_name}' en el sistema"
        
        try:
            if self.system == "Windows":
                # Usar os.startfile para archivos ejecutables
                if command.endswith(('.exe', '.com', '.bat', '.cmd')):
                    os.startfile(command)
                else:
                    subprocess.Popen(command, shell=True)
            elif self.system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", command])
            else:  # Linux
                # Verificar si el comando existe en el PATH
                executable = command.split()[0] if ' ' in command else command
                if shutil.which(executable) is None:
                    return f"No encontré el ejecutable '{executable}' para '{found_name}'"
                
                # Ejecutar en segundo plano
                subprocess.Popen(
                    command.split(), 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            return f"Aplicación '{found_name}' abierta correctamente"
            
        except Exception as e:
            return f"Error al abrir '{found_name}': {str(e)}"

    def create_file(self, file_path: str, content: str = ""):
        """
        Crea un archivo en la ruta especificada. 
        Si la ruta es relativa, se toma desde base_path.
        """
        path = Path(file_path)
        
        # Si es ruta relativa, anclarla al base_path
        if not path.is_absolute():
            path = self.base_path / path

        # Crear directorios si no existen
        path.parent.mkdir(parents=True, exist_ok=True)

        # Crear el archivo con contenido inicial
        path.write_text(content, encoding="utf-8")
        return f"Archivo creado en: {path}"

    def create_folder(self, folder_path: str):
        """
        Crea una carpeta en la ruta especificada.
        """
        path = Path(folder_path)
        if not path.is_absolute():
            path = self.base_path / path

        path.mkdir(parents=True, exist_ok=True)
        return f"Carpeta creada en: {path}"

    def find_or_create_folder(self, folder_path: str, auto_create: bool = False) -> dict:
        """
        Busca una carpeta y si no existe, pregunta si se desea crear.
        
        Args:
            folder_path: Ruta de la carpeta a buscar/crear
            auto_create: Si es True, crea automáticamente sin preguntar
            
        Returns:
            dict: Información sobre el resultado de la operación
        """
        path = Path(folder_path)
        if not path.is_absolute():
            path = self.base_path / path

        result = {
            "exists": False,
            "path": str(path),
            "message": "",
            "created": False
        }

        # Verificar si la carpeta existe
        if path.exists() and path.is_dir():
            result["exists"] = True
            result["message"] = f"✅ La carpeta ya existe: {path}"
            return result
        
        # Si no existe
        result["message"] = f"❌ La carpeta no existe: {path}"
        
        # Opción de crear automáticamente
        if auto_create:
            try:
                path.mkdir(parents=True, exist_ok=True)
                result["created"] = True
                result["exists"] = True
                result["message"] = f"✅ Carpeta creada automáticamente: {path}"
                return result
            except Exception as e:
                result["message"] = f"❌ Error al crear carpeta: {str(e)}"
                return result
        
        # Si no hay auto_create, retornar información para que el llamador decida
        return result

    def search_folder(self, folder_name: str, search_path: str = None) -> dict:
        """
        Busca una carpeta en el sistema.
        
        Args:
            folder_name: Nombre de la carpeta a buscar
            search_path: Ruta donde buscar (por defecto base_path)
            
        Returns:
            dict: Resultados de la búsqueda
        """
        search_dir = Path(search_path) if search_path else self.base_path
        folder_name = folder_name.lower()
        
        results = {
            "found": False,
            "matches": [],
            "search_path": str(search_dir),
            "message": ""
        }
        
        try:
            # Buscar recursivamente
            for path in search_dir.rglob("*"):
                if path.is_dir() and folder_name in path.name.lower():
                    results["matches"].append({
                        "path": str(path),
                        "name": path.name,
                        "parent": str(path.parent)
                    })
            
            if results["matches"]:
                results["found"] = True
                results["message"] = f"✅ Encontradas {len(results['matches'])} coincidencias para '{folder_name}'"
            else:
                results["message"] = f"❌ No se encontraron carpetas con '{folder_name}' en {search_dir}"
                
        except Exception as e:
            results["message"] = f"❌ Error en la búsqueda: {str(e)}"
        
        return results

    def _clean_filename(self, filename: str) -> str:
        """Limpia el nombre de archivo de caracteres inválidos y evita rutas peligrosas"""
        # Remover caracteres inválidos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Prevenir path traversal
        filename = os.path.basename(filename)
        
        # Limpiar espacios extra
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename

    def get_system_info(self) -> str:
        """Obtiene información del sistema"""
        info = {
            "Sistema": platform.system(),
            "Versión": platform.release(),
            "Arquitectura": platform.architecture()[0],
            "Procesador": platform.processor(),
            "Directorio actual": os.getcwd(),
            "Directorio base": str(self.base_path)
        }
        return "\n".join([f"{k}: {v}" for k, v in info.items()])

    def execute_command(self, command_type: str, params: str) -> str:
        """Ejecuta un comando basado en el tipo y parámetros"""
        if command_type == 'open_app':
            return self.open_application(params)
        elif command_type == 'create_folder':
            return self.create_folder(params)
        elif command_type == 'create_file':
            return self.create_file(params)
        elif command_type == 'search_folder':
            result = self.search_folder(params)
            return result["message"]
        else:
            return "Tipo de comando no reconocido"

    def reload_config(self):
        """Recarga la configuración de aplicaciones"""
        self.applications = self._load_application_mappings()
        return "Configuración recargada correctamente"


# Prueba rápida
if __name__ == "__main__":
    executor = SystemCommandExecutor()
    print("🔧 Probando ejecutor...")
    
    # Probar búsqueda de carpeta
    print("\n🔍 Probando búsqueda de carpetas:")
    result = executor.search_folder("documentos")
    print(result["message"])
    if result["matches"]:
        for match in result["matches"][:3]:  # Mostrar solo las primeras 3
            print(f"  - {match['path']}")
    
    # Probar búsqueda y creación
    print("\n📁 Probando búsqueda y creación:")
    test_folder = "mi_carpeta_test"
    result = executor.find_or_create_folder(test_folder)
    print(result["message"])
    
    if not result["exists"]:
        # Simular decisión del usuario de crear
        print(f"💡 ¿Quieres crear la carpeta '{test_folder}'? (simulando 'sí')")
        result = executor.find_or_create_folder(test_folder, auto_create=True)
        print(result["message"])
    
    print(executor.execute_command('open_app', 'navegador'))