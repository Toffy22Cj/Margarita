# src/stt.py
from faster_whisper import WhisperModel

class SpeechToText:
    def __init__(self, model_size="small", device="cpu"):
        self.model = WhisperModel(model_size, device=device)

    def transcribe(self, audio_path: str, lang="es") -> str:
        """
        Transcribe un archivo de audio a texto.
        """
        segments, info = self.model.transcribe(audio_path, language=lang)
        text = " ".join([seg.text for seg in segments])
        return text.strip()


# --- Ejemplo de uso ---
if __name__ == "__main__":
    stt = SpeechToText(model_size="small", device="cpu")
    text = stt.transcribe("src/test/test.wav", lang="es")
    print("Reconocido:", text)
