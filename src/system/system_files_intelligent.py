# [file name]: src/system/system_files_intelligent.py
import os
from pathlib import Path
from .system_files import SystemFiles

class IntelligentFileManager:
    """Gestor inteligente que verifica existencia y pregunta al usuario - CON SOPORTE PARA RUTAS COMPLEJAS"""
    
    def __init__(self, base_path=None):
        self.files_manager = SystemFiles(base_path)
    
    def smart_create_folder(self, folder_name: str, location: str = None) -> dict:
        """Crea carpeta inteligentemente verificando existencia - SOPORTA RUTAS COMPLEJAS"""
        result = {
            "success": False,
            "message": "",
            "path": None,
            "already_exists": False,
            "created_paths": []  # Nueva: lista de rutas creadas
        }
        
        print(f"[IntelligentFileManager] Creando carpeta: '{folder_name}' en ubicación: '{location}'")
        
        # Construir ruta completa - usar los nombres originales con mayúsculas
        if location:
            # location puede ser una ruta compleja como "Documentos/Proyectos/MiApp"
            location_path = Path(location)  # Preservar mayúsculas y estructura de rutas
            if not location_path.is_absolute():
                location_path = self.files_manager.base_path / location_path
            full_path = location_path / folder_name  # Preservar mayúsculas del folder_name
        else:
            full_path = Path(folder_name)  # Preservar mayúsculas del folder_name
            if not full_path.is_absolute():
                full_path = self.files_manager.base_path / full_path

        result["path"] = str(full_path)
        
        # Verificar si ya existe
        if full_path.exists():
            if full_path.is_dir():
                result["already_exists"] = True
                result["message"] = f"✅ La carpeta '{folder_name}' ya existe en: {full_path}"  # Usar folder_name original
                return result
            else:
                result["message"] = f"❌ Ya existe un archivo con ese nombre: {full_path}"
                return result
        
        # Si no existe, crear - parents=True crea todos los directorios padres necesarios
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            result["success"] = True
            
            # Registrar todas las rutas creadas (útil para rutas complejas)
            current_path = full_path
            while current_path != self.files_manager.base_path and not current_path.exists():
                # En realidad, mkdir(parents=True) crea todo de una vez, pero podemos registrar la ruta completa
                current_path = current_path.parent
            
            result["message"] = f"✅ Carpeta '{folder_name}' creada en: {full_path}"  # Usar folder_name original
            if "/" in str(location) or "\\" in str(location):
                result["message"] += f"\n   📁 Ruta completa creada: {location}/{folder_name}"
            
            return result
        except Exception as e:
            result["message"] = f"❌ Error al crear carpeta: {str(e)}"
            return result
    
    def smart_create_file(self, file_name: str, location: str = None, content: str = "") -> dict:
        """Crea archivo inteligentemente con verificaciones - SOPORTA RUTAS COMPLEJAS"""
        result = {
            "success": False,
            "message": "",
            "path": None,
            "folder_created": False
        }
        
        print(f"[IntelligentFileManager] Creando archivo: '{file_name}' en ubicación: '{location}'")
        
        # Construir ruta completa - usar los nombres originales con mayúsculas
        if location:
            # location puede ser una ruta compleja como "Documentos/Proyectos/MiApp"
            location_path = Path(location)  # Preservar mayúsculas y estructura de rutas
            if not location_path.is_absolute():
                location_path = self.files_manager.base_path / location_path
            full_path = location_path / file_name  # Preservar mayúsculas del file_name
        else:
            full_path = Path(file_name)  # Preservar mayúsculas del file_name
            if not full_path.is_absolute():
                full_path = self.files_manager.base_path / full_path

        result["path"] = str(full_path)
        
        # Verificar si el directorio padre existe - parents=True crea toda la estructura necesaria
        parent_dir = full_path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                result["folder_created"] = True
            except Exception as e:
                result["message"] = f"❌ Error al crear directorio: {str(e)}"
                return result
        
        # Verificar si el archivo ya existe
        if full_path.exists():
            result["message"] = f"⚠️ El archivo ya existe: {full_path}"
            return result
        
        # Crear el archivo
        try:
            full_path.write_text(content, encoding="utf-8")
            result["success"] = True
            folder_msg = " (se creó la carpeta contenedora)" if result["folder_created"] else ""
            result["message"] = f"✅ Archivo '{file_name}' creado en: {full_path}{folder_msg}"  # Usar file_name original
            
            # Si la ubicación es una ruta compleja, mostrar información adicional
            if location and ("/" in location or "\\" in location):
                result["message"] += f"\n   📁 Ruta: {location}/{file_name}"
            
            return result
        except Exception as e:
            result["message"] = f"❌ Error al crear archivo: {str(e)}"
            return result
    
    def find_or_create_for_file(self, file_name: str, target_folder: str = None) -> dict:
        """Busca carpeta para archivo y si no existe, pregunta"""
        result = {
            "folder_exists": False,
            "folder_created": False,
            "folder_path": None,
            "suggestion": None,
            "suggested_folders": []
        }
        
        # Si se especifica carpeta destino (puede ser ruta compleja)
        if target_folder:
            folder_path = Path(target_folder)  # Preservar mayúsculas
            if not folder_path.is_absolute():
                folder_path = self.files_manager.base_path / folder_path
            
            if not folder_path.exists():
                result["suggestion"] = f"¿Quieres crear la carpeta '{target_folder}' para guardar '{file_name}'?"  # Usar nombres originales
                result["folder_path"] = str(folder_path)
                return result
            else:
                result["folder_exists"] = True
                result["folder_path"] = str(folder_path)
                return result
        
        # Buscar carpeta apropiada (lógica inteligente)
        suggested_folders = self._suggest_folders(file_name)
        result["suggested_folders"] = suggested_folders
        
        if suggested_folders:
            result["suggestion"] = f"¿En qué carpeta quieres guardar '{file_name}'? Sugerencias: {', '.join(suggested_folders)}"  # Usar file_name original
        else:
            result["suggestion"] = f"¿Dónde quieres guardar '{file_name}'? Puedes decirme una carpeta específica o ruta completa."  # Usar file_name original
        
        return result
    
    def _suggest_folders(self, file_name: str) -> list:
        """Sugiere carpetas basadas en el tipo de archivo"""
        file_lower = file_name.lower()  # Solo para comparación interna
        common_folders = self.files_manager.get_suggested_folders()
        suggestions = []
        
        # Lógica de sugerencias basada en extensiones/palabras clave
        if any(ext in file_lower for ext in ['.txt', '.doc', '.docx', '.pdf', '.xlsx', '.pptx']):
            preferred = ['Documentos', 'Escritorio']
        elif any(ext in file_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']):
            preferred = ['Imágenes', 'Fotos', 'Escritorio']
        elif any(ext in file_lower for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']):
            preferred = ['Videos', 'Películas', 'Escritorio']
        elif any(ext in file_lower for ext in ['.mp3', '.wav', '.flac', '.aac']):
            preferred = ['Música', 'Audios', 'Escritorio']
        elif any(ext in file_lower for ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']):
            preferred = ['Proyectos', 'Desarrollo', 'Documentos', 'Escritorio']
        else:
            preferred = ['Documentos', 'Escritorio', 'Descargas']
        
        # Filtrar carpetas que existen y están en preferred
        for folder in preferred:
            if folder in common_folders and folder not in suggestions:
                suggestions.append(folder)
        
        # Agregar otras carpetas comunes si no hay suficientes sugerencias
        for folder in common_folders:
            if folder not in suggestions and len(suggestions) < 3:
                suggestions.append(folder)
        
        return suggestions[:3]  # Máximo 3 sugerencias