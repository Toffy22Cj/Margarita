# [file name]: src/routes/__init__.py
from .router import Router
from .intent_classifier import IntentClassifier
from .system_command_classifier import SystemCommandClassifier

# Eliminar esta línea si existe:
# from .system_command_router import SystemCommandRouter

__all__ = [
    'Router',
    'IntentClassifier', 
    'SystemCommandClassifier',
    # 'SystemCommandRouter'  # Eliminar esta línea
]