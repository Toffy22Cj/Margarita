import platform
import os
from pathlib import Path

class SystemInfo:
    """Proporciona información del sistema"""

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path.home()

    def get_system_info(self) -> str:
        """Obtiene información detallada del sistema"""
        info = {
            "Sistema": platform.system(),
            "Versión": platform.release(),
            "Arquitectura": platform.architecture()[0],
            "Procesador": platform.processor(),
            "Directorio actual": os.getcwd(),
            "Directorio base": str(self.base_path)
        }
        return "\n".join([f"{k}: {v}" for k, v in info.items()])

    def get_disk_usage(self) -> str:
        """Obtiene información del uso del disco"""
        try:
            usage = shutil.disk_usage(self.base_path)
            total_gb = usage.total // (1024**3)
            used_gb = usage.used // (1024**3)
            free_gb = usage.free // (1024**3)
            
            return (f"Uso del disco en {self.base_path}:\n"
                   f"  Total: {total_gb} GB\n"
                   f"  Usado: {used_gb} GB\n"
                   f"  Libre: {free_gb} GB")
        except Exception as e:
            return f"Error al obtener información del disco: {str(e)}"