"""
Utilidades del sistema - STT, TTS, VAD, etc.
"""
from .stt import SpeechToText
from .tts import TextToSpeech
from .vad_recorder import VADRecorder
from .voice_loop import VoiceLoop
from .translation_utils import TranslationUtils, translate_via_llm, validate_translation_semantic

__all__ = [
    'SpeechToText', 
    'TextToSpeech', 
    'VADRecorder', 
    'VoiceLoop',
    'TranslationUtils',
    'translate_via_llm', 
    'validate_translation_semantic'
]