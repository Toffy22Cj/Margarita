# [file name]: system_command_router.py
from .system_command_classifier import SystemCommandClassifier
from .system_command_executor import SystemCommandExecutor


class SystemCommandRouter:
    """
    Integra el clasificador y el ejecutor de comandos.
    """

    def __init__(self, config_file: str = "apps_config.json"):
        self.classifier = SystemCommandClassifier()
        self.executor = SystemCommandExecutor(config_file)

    def handle_command(self, text: str) -> str:
        """
        Recibe un texto, lo clasifica y lo ejecuta.
        Devuelve el resultado como string.
        """
        result = self.classifier.classify(text)

        if result["confidence"] == "none" or result["type"] is None:
            return f"No entendí el comando: '{text}'"

        return self.executor.execute_command(result["type"], result["params"])


if __name__ == "__main__":
    router = SystemCommandRouter()

    print("=== Probador de Comandos del Sistema ===")
    print("Escribe comandos como:")
    print("- abre navegador")
    print("- crea carpeta proyectos")
    print("- crea archivo notas")
    print("Escribe 'salir' para terminar.\n")

    while True:
        user_input = input(">> ").strip()
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Adiós 👋")
            break

        response = router.handle_command(user_input)
        print(response)
