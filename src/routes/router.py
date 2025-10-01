# [file name]: router.py (actualizado para estructura modular)
import yaml
from pathlib import Path
from src.cores.ollama_core import OllamaCore
from src.routes.intent_classifier import IntentClassifier
from src.routes.system_command_classifier import SystemCommandClassifier  # Desde routes
from src.system.system_executor import SystemCommandExecutor  # Desde system

class Router:
    def __init__(self, config_path="configs/cores.yaml"):
        # Cargar la configuración YAML
        self.config = yaml.safe_load(Path(config_path).read_text())
        self.cores = self._load_cores()
        self.classifier = IntentClassifier()
        self.system_classifier = SystemCommandClassifier()  # Ahora desde routes
        self.system_executor = SystemCommandExecutor()  # Desde system
        print(f"[Router] Cargados núcleos: {list(self.cores.keys())}")

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

    def auto_send(self, text: str) -> str:
        """
        Detecta la intención automáticamente y llama al núcleo correcto.
        """
        try:
            intent = self.classifier.classify(text)
            print(f"[Router] Intención clasificada: {intent}")
            
            # Manejar comandos del sistema
            if intent == "system_command":
                command_info = self.system_classifier.classify(text)
                if command_info['type']:
                    print(f"[Router] Ejecutando comando: {command_info['type']} -> {command_info['params']}")
                    result = self.system_executor.execute_command(
                        command_info['type'], 
                        command_info['params']
                    )
                    return f"🤖 {result}"
                else:
                    return "❌ No entendí el comando del sistema. ¿Podrías reformularlo?"
            
            # Manejar otros núcleos
            if intent not in self.cores or self.cores[intent] is None:
                fallback_msg = f"⚠️ Núcleo {intent} no disponible. Usando conversacional."
                print(f"[Router] {fallback_msg}")
                intent = "conversational"  # Fallback a conversacional
            
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