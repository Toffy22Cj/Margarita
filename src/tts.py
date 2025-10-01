# src/tts.py
from TTS.api import TTS

class TextToSpeech:
    def __init__(self, model_name="tts_models/es/css10/vits"):
        self.tts = TTS(model_name)

    def speak(self, text: str, output="output.wav"):
        """
        Genera audio en español a partir de texto.
        """
        self.tts.tts_to_file(text=text, file_path=output)
        return output


# --- Ejemplo de uso ---
if __name__ == "__main__":
    tts = TextToSpeech()
    wav_file = tts.speak("Hola, soy Margarita, tu asistente.")
    print("Audio generado en:", wav_file)
