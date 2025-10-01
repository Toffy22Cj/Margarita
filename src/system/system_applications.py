import os
import re
import json
import subprocess
import platform
import shutil
from pathlib import Path

class SystemApplications:
    """Maneja la apertura de aplicaciones del sistema"""

    def __init__(self, config_file: str = "configs/apps_config.json"):
        self.system = platform.system()
        
        # Corregir la ruta del archivo de configuración
        current_dir = Path(__file__).resolve().parent.parent.parent
        self.config_file = current_dir / config_file
        
        # Crear directorio config si no existe
        self.config_file.parent.mkdir(exist_ok=True)
        
        self.applications = self._load_application_mappings()
        print(f"[SystemApplications] Sistema detectado: {self.system}")

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
        """Carga el mapeo de aplicaciones desde archivo JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_apps = json.load(f)
                print(f"[SystemApplications] Configuración cargada desde: {self.config_file}")
                return user_apps
            except Exception as e:
                print(f"[WARN] No se pudo cargar {self.config_file}: {e}")
        
        # Si no existe, crear uno con los valores por defecto
        default_apps = self._default_app_mappings()
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(default_apps, f, indent=2, ensure_ascii=False)
            print(f"[SystemApplications] Archivo de configuración creado: {self.config_file}")
        except Exception as e:
            print(f"[WARN] No se pudo crear el archivo de configuración: {e}")
        
        return default_apps

    def _find_application(self, app_name: str):
        """Busca una aplicación en el sistema"""
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
                if command.endswith(('.exe', '.com', '.bat', '.cmd')):
                    os.startfile(command)
                else:
                    subprocess.Popen(command, shell=True)
            elif self.system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", command])
            else:  # Linux
                executable = command.split()[0] if ' ' in command else command
                if shutil.which(executable) is None:
                    return f"No encontré el ejecutable '{executable}' para '{found_name}'"
                
                subprocess.Popen(
                    command.split(), 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            return f"Aplicación '{found_name}' abierta correctamente"
            
        except Exception as e:
            return f"Error al abrir '{found_name}': {str(e)}"

    def reload_config(self):
        """Recarga la configuración de aplicaciones"""
        self.applications = self._load_application_mappings()
        return "Configuración recargada correctamente"