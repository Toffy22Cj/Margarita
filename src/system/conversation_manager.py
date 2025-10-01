# [file name]: src/system/conversation_manager.py
class ConversationManager:
    """Maneja el flujo de conversación con el usuario"""
    
    def __init__(self, executor):
        self.executor = executor
        self.pending_actions = {}
    
    def handle_system_command(self, command_data: dict, user_id: str = "default") -> str:
        """Maneja comandos del sistema con flujo conversacional"""
        command_type = command_data['type']
        params = command_data['params']
        
        print(f"[ConversationManager] Procesando comando: {command_type} con params: {params}")
        print(f"[ConversationManager] Estado actual de pending_actions: {self.pending_actions}")
        
        # Comando de crear carpeta con ubicación
        if command_type == 'create_folder':
            if isinstance(params, dict):
                folder_name = params.get('folder_name')
                location = params.get('location')
                
                print(f"[ConversationManager] folder_name: {folder_name}, location: {location}")
                
                if folder_name and location:
                    # Ejecutar directamente: "crea carpeta proyectos en documentos"
                    result = self.executor.intelligent_manager.smart_create_folder(folder_name, location)
                    return result["message"]
                elif location and not folder_name:
                    # Preguntar nombre: "crea carpeta en documentos"
                    self.pending_actions[user_id] = {
                        'action': 'create_folder_in_location',
                        'location': location  # Preservar mayúsculas originales
                    }
                    print(f"[ConversationManager] ✅ Guardada acción pendiente: {self.pending_actions[user_id]}")
                    return f"¿Qué nombre quieres para la carpeta en '{location}'?"  # Usar location original
                elif folder_name and not location:
                    # Preguntar ubicación: "crea carpeta proyectos"
                    self.pending_actions[user_id] = {
                        'action': 'create_folder_with_name',
                        'folder_name': folder_name  # Preservar mayúsculas originales
                    }
                    print(f"[ConversationManager] ✅ Guardada acción pendiente: {self.pending_actions[user_id]}")
                    suggested = self.executor.intelligent_manager.files_manager.get_suggested_folders()
                    return f"¿Dónde quieres crear la carpeta '{folder_name}'? Sugerencias: {', '.join(suggested[:3])}"
            else:
                # Comando simple como "crea carpeta proyectos"
                # VERIFICAR: Si el parámetro parece una ubicación en lugar de un nombre
                if params and any(loc in params.lower() for loc in ['documentos', 'escritorio', 'descargas', 'imágenes', 'música', 'videos']):
                    # Probablemente es "crea carpeta en documentos" mal interpretado
                    self.pending_actions[user_id] = {
                        'action': 'create_folder_in_location',
                        'location': params  # Preservar mayúsculas originales
                    }
                    print(f"[ConversationManager] ✅ Guardada acción pendiente: {self.pending_actions[user_id]}")
                    return f"¿Qué nombre quieres para la carpeta en '{params}'?"  # Usar params original
                else:
                    self.pending_actions[user_id] = {
                        'action': 'create_folder_simple',
                        'folder_name': params  # Preservar mayúsculas originales
                    }
                    print(f"[ConversationManager] ✅ Guardada acción pendiente: {self.pending_actions[user_id]}")
                    suggested = self.executor.intelligent_manager.files_manager.get_suggested_folders()
                    return f"¿Dónde quieres crear la carpeta '{params}'? Sugerencias: {', '.join(suggested[:3])}"
        
        # Comando de crear archivo
        elif command_type == 'create_file':
            if isinstance(params, dict):
                file_name = params.get('file_name')
                location = params.get('location')
                
                if file_name and location:
                    # Ejecutar directamente: "crea archivo notas.txt en documentos"
                    result = self.executor.intelligent_manager.smart_create_file(file_name, location)
                    return result["message"]
                elif file_name and not location:
                    # Verificar dónde guardar: "crea archivo notas.txt"
                    result = self.executor.intelligent_manager.find_or_create_for_file(file_name)
                    
                    if result["suggestion"]:
                        self.pending_actions[user_id] = {
                            'action': 'create_file_with_name',
                            'file_name': file_name,  # Preservar mayúsculas originales
                            'suggested_folders': result["suggested_folders"]
                        }
                        print(f"[ConversationManager] ✅ Guardada acción pendiente: {self.pending_actions[user_id]}")
                        return result["suggestion"]
                    else:
                        result = self.executor.intelligent_manager.smart_create_file(file_name)
                        return result["message"]
            else:
                # Comando simple como "crea archivo notas.txt"
                result = self.executor.intelligent_manager.find_or_create_for_file(params)
                
                if result["suggestion"]:
                    self.pending_actions[user_id] = {
                        'action': 'create_file_with_name',
                        'file_name': params,  # Preservar mayúsculas originales
                        'suggested_folders': result["suggested_folders"]
                    }
                    print(f"[ConversationManager] ✅ Guardada acción pendiente: {self.pending_actions[user_id]}")
                    return result["suggestion"]
                else:
                    result = self.executor.intelligent_manager.smart_create_file(params)
                    return result["message"]
        
        # Otros comandos (ejecutar directamente)
        return self.executor.execute_command(command_type, params)
    
    def handle_user_response(self, response: str, user_id: str = "default") -> str:
        """Maneja respuestas del usuario a preguntas pendientes"""
        if user_id not in self.pending_actions:
            return "No tengo acciones pendientes para procesar."
        
        action = self.pending_actions[user_id]
        response_clean = response.strip()
        
        print(f"[ConversationManager] Procesando respuesta: '{response}' para acción: {action['action']}")
        
        try:
            if action['action'] == 'create_folder_in_location':
                folder_name = response_clean  # Preservar mayúsculas de la respuesta
                location = action['location']  # Ya tiene las mayúsculas originales
                del self.pending_actions[user_id]
                
                result = self.executor.intelligent_manager.smart_create_folder(folder_name, location)
                return result["message"]
            
            elif action['action'] == 'create_folder_with_name':
                location = response_clean  # Preservar mayúsculas de la respuesta
                folder_name = action['folder_name']  # Ya tiene las mayúsculas originales
                del self.pending_actions[user_id]
                
                result = self.executor.intelligent_manager.smart_create_folder(folder_name, location)
                return result["message"]
            
            elif action['action'] == 'create_folder_simple':
                location = response_clean  # Preservar mayúsculas de la respuesta
                folder_name = action['folder_name']  # Ya tiene las mayúsculas originales
                del self.pending_actions[user_id]
                
                result = self.executor.intelligent_manager.smart_create_folder(folder_name, location)
                return result["message"]
            
            elif action['action'] == 'create_file_with_name':
                folder_choice = response_clean  # Preservar mayúsculas de la respuesta
                file_name = action['file_name']  # Ya tiene las mayúsculas originales
                del self.pending_actions[user_id]
                
                # Crear archivo en la carpeta elegida
                result = self.executor.intelligent_manager.smart_create_file(file_name, folder_choice)
                return result["message"]
        
        except Exception as e:
            del self.pending_actions[user_id]
            return f"❌ Ocurrió un error al procesar tu respuesta: {str(e)}"
        
        return "No pude entender tu respuesta para la acción pendiente."
    
    def has_pending_action(self, user_id: str = "default") -> bool:
        """Verifica si hay acciones pendientes para el usuario"""
        has_action = user_id in self.pending_actions
        print(f"[ConversationManager] Verificando acción pendiente para '{user_id}': {has_action}")
        if has_action:
            print(f"[ConversationManager] Acción pendiente: {self.pending_actions[user_id]}")
        return has_action
    
    def clear_pending_actions(self, user_id: str = "default"):
        """Limpia las acciones pendientes del usuario"""
        if user_id in self.pending_actions:
            del self.pending_actions[user_id]