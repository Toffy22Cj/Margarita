# [file name]: src/system/system_files.py
import os
import re
from pathlib import Path

class SystemFiles:
    """Maneja operaciones con archivos y carpetas"""

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path.home()

    def create_file(self, file_path: str, content: str = "") -> str:
        """Crea un archivo en la ruta especificada"""
        path = Path(file_path)
        
        # Si es ruta relativa, anclarla al base_path
        if not path.is_absolute():
            path = self.base_path / path

        # Crear directorios si no existen
        path.parent.mkdir(parents=True, exist_ok=True)

        # Crear el archivo con contenido inicial
        path.write_text(content, encoding="utf-8")
        return f"✅ Archivo creado en: {path}"

    def create_folder(self, folder_path: str) -> str:
        """Crea una carpeta en la ruta especificada"""
        path = Path(folder_path)
        if not path.is_absolute():
            path = self.base_path / path

        path.mkdir(parents=True, exist_ok=True)
        return f"✅ Carpeta creada en: {path}"

    def create_folder_in_location(self, folder_name: str, location: str) -> str:
        """Crea una carpeta en una ubicación específica"""
        if not location:
            return self.create_folder(folder_name)
        
        # Construir ruta completa
        location_path = Path(location)
        if not location_path.is_absolute():
            location_path = self.base_path / location_path
        
        full_path = location_path / folder_name
        full_path.mkdir(parents=True, exist_ok=True)
        return f"✅ Carpeta '{folder_name}' creada en: {full_path}"

    def create_file_in_location(self, file_name: str, location: str, content: str = "") -> str:
        """Crea un archivo en una ubicación específica"""
        if not location:
            return self.create_file(file_name, content)
        
        # Construir ruta completa
        location_path = Path(location)
        if not location_path.is_absolute():
            location_path = self.base_path / location_path
        
        full_path = location_path / file_name
        return self.create_file(str(full_path), content)

    def find_or_create_folder(self, folder_path: str, auto_create: bool = False) -> dict:
        """Busca una carpeta y si no existe, pregunta si se desea crear"""
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
        
        return result

    def search_folder(self, folder_name: str, search_path: str = None) -> dict:
        """Busca una carpeta en el sistema"""
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

    def check_folder_exists(self, folder_path: str) -> bool:
        """Verifica si una carpeta existe"""
        path = Path(folder_path)
        if not path.is_absolute():
            path = self.base_path / path
        return path.exists() and path.is_dir()

    def get_suggested_folders(self) -> list:
        """Retorna una lista de carpetas sugeridas comunes"""
        common_folders = [
            "Documentos", "Escritorio", "Descargas", 
            "Imágenes", "Música", "Videos", "Proyectos"
        ]
        
        existing_folders = []
        for folder in common_folders:
            if self.check_folder_exists(folder):
                existing_folders.append(folder)
        
        return existing_folders

    def _clean_filename(self, filename: str) -> str:
        """Limpia el nombre de archivo de caracteres inválidos"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        filename = os.path.basename(filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename