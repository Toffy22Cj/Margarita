# [file name]: src/routes/router.py
import yaml
from pathlib import Path
from src.cores.ollama_core import OllamaCore
from .intent_classifier import IntentClassifier
from .system_command_classifier import SystemCommandClassifier
from src.system.system_executor import SystemCommandExecutor

class Router:
    def __init__(self, config_path="configs/cores.yaml"):
        # Cargar la configuración YAML
        self.config = yaml.safe_load(Path(config_path).read_text())
        self.cores = self._load_cores()
        self.classifier = IntentClassifier()
        self.system_classifier = SystemCommandClassifier()
        self.system_executor = SystemCommandExecutor()
        self.conversation_manager = self.system_executor.get_conversation_manager()
        
        print(f"[Router] Cargados núcleos: {list(self.cores.keys())}")
        print(f"[Router] Sistema de comandos y conversación listo")

    def _load_cores(self):
        cores = {}
        for name, cfg in self.config.get("cores", {}).items():
            provider = cfg.get("provider")
            model = cfg.get("model")
            if provider == "ollama":
                try:
                    cores[name] = OllamaCore(model=model)
                    print(f"[Router] ✅ Núcleo cargado: {name} -> {model}")
                except Exception as e:
                    print(f"[Router] ❌ Error cargando núcleo {name}: {e}")
                    cores[name] = None
            elif provider == "service":
                # placeholder para futuros núcleos externos
                cores[name] = None
                print(f"[Router] ⚠️  Núcleo de servicio: {name} (no implementado)")
        return cores

 # [file name]: src/routes/router.py
    def auto_send(self, text: str, user_id: str = "default") -> str:
        """
        Detecta la intención automáticamente y llama al núcleo correcto.
        """
        try:
            # PRIMERO: Verificar si hay conversación pendiente - CON MÁS DEBUG
            has_pending = self.conversation_manager.has_pending_action(user_id)
            print(f"[Router] Verificando conversación pendiente para '{user_id}': {has_pending}")
            
            if has_pending:
                print(f"[Router] ✅ Continuando conversación pendiente: '{text}'")
                response = self.conversation_manager.handle_user_response(text, user_id)
                print(f"[Router] Respuesta del conversation_manager: {response}")
                return f"🤖 {response}"
            
            # SEGUNDO: Solo si no hay conversación pendiente, clasificar la intención
            intent = self.classifier.classify(text)
            print(f"[Router] Intención clasificada: {intent}")
            
            # Manejar comandos del sistema
            if intent == "system_command":
                command_info = self.system_classifier.classify(text)
                print(f"[Router] Comando del sistema detectado: {command_info['type']} -> {command_info['params']}")
                
                if command_info['type']:
                    result = self.conversation_manager.handle_system_command(command_info, user_id)
                    return f"🤖 {result}"
                else:
                    return "❌ No entendí el comando del sistema. ¿Podrías reformularlo?"
            
            # Manejar otros núcleos
            if intent not in self.cores or self.cores[intent] is None:
                fallback_msg = f"⚠️ Núcleo {intent} no disponible. Usando conversacional."
                print(f"[Router] {fallback_msg}")
                intent = "conversational"
            
            return self.cores[intent].generate(text)
            
        except Exception as e:
            return f"❌ Error procesando tu solicitud: {str(e)}"

    def send(self, core_name: str, prompt: str) -> str:
        """
        Llamada directa, sin clasificación automática.
        """
        try:
            if core_name not in self.cores or self.cores[core_name] is None:
                return f"❌ Núcleo {core_name} no encontrado."
            return self.cores[core_name].generate(prompt)
        except Exception as e:
            return f"❌ Error en núcleo {core_name}: {str(e)}"

    def get_system_executor(self) -> SystemCommandExecutor:
        """Retorna el ejecutor de comandos del sistema para acceso directo"""
        return self.system_executor

    def get_conversation_manager(self):
        """Retorna el gestor de conversación"""
        return self.conversation_manager

    def clear_conversation(self, user_id: str = "default"):
        """Limpia la conversación pendiente de un usuario"""
        self.conversation_manager.clear_pending_actions(user_id)
        return f"✅ Conversación limpiada para usuario: {user_id}"


# También vamos a agregar más debug al conversation_manager.py