# src/vad_recorder.py
import collections
import sys
import wave
import webrtcvad
import sounddevice as sd
import numpy as np
import tempfile

SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION = 30  # ms
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)


class VADRecorder:
    def __init__(self, aggressiveness=2):
        self.vad = webrtcvad.Vad(aggressiveness)

    def _frame_generator(self, audio):
        for i in range(0, len(audio), FRAME_SIZE):
            yield audio[i:i + FRAME_SIZE]

    def record(self, timeout=10):
        print("🎤 Habla (Margarita detectará silencio para cortar)...")

        recording = []
        with sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype="int16",
            blocksize=FRAME_SIZE
        ) as stream:
            silence_frames = 0
            while True:
                frame, _ = stream.read(FRAME_SIZE)
                frame = frame.flatten()
                recording.extend(frame)

                is_speech = self.vad.is_speech(frame.tobytes(), SAMPLE_RATE)
                if not is_speech:
                    silence_frames += 1
                else:
                    silence_frames = 0

                if silence_frames > int(0.8 * SAMPLE_RATE / FRAME_SIZE):  # ~0.8s de silencio
                    break

                if len(recording) > SAMPLE_RATE * timeout:  # seguridad
                    break

        # Guardar a WAV temporal
        wav_path = tempfile.mktemp(suffix=".wav")
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # int16
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(np.array(recording, dtype=np.int16).tobytes())

        return wav_path


# --- Ejemplo ---
if __name__ == "__main__":
    vad = VADRecorder()
    wav = vad.record()
    print("Archivo guardado:", wav)
