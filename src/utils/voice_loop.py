# [file name]: src/utils/voice_loop.py
import os
import time
import threading
from .vad_recorder import VADRecorder  # Import relativo
from .stt import SpeechToText  # Import relativo
from .tts import TextToSpeech  # Import relativo
from src.routes.router import Router
from src.routes.intent_classifier import IntentClassifier


class VoiceLoop:
    """
    Bucle principal de voz para Margarita
    Maneja la grabación, transcripción y respuesta por voz
    """
    
    def __init__(self, model_size="small", device="cpu"):
        print("🎤 Inicializando VoiceLoop...")
        
        # Inicializar componentes de voz
        self.vad = VADRecorder()
        self.stt = SpeechToText(model_size=model_size, device=device)
        self.tts = TextToSpeech()
        
        # Inicializar procesamiento de texto
        self.router = Router()
        self.classifier = IntentClassifier()
        
        # Estado del bucle
        self.is_running = False
        self.current_thread = None
        
        print("✅ VoiceLoop inicializado correctamente")
    
    def process_audio_input(self, audio_file: str) -> str:
        """
        Procesa un archivo de audio: transcribe y genera respuesta
        """
        try:
            # Transcribir audio a texto
            print("👂 Transcribiendo audio...")
            text = self.stt.transcribe(audio_file, lang="es")
            
            if not text or text.strip() == "":
                return "No escuché nada. ¿Podrías repetirlo?"
            
            print(f"📝 Tú dijiste: '{text}'")
            
            # Procesar el texto
            response = self._process_text(text)
            
            # Generar audio de respuesta
            if response and response.strip():
                print("🗣️ Generando audio de respuesta...")
                audio_output = self.tts.speak(response)
                return audio_output
            
            return None
            
        except Exception as e:
            print(f"❌ Error procesando audio: {e}")
            return None
    
    def _process_text(self, text: str) -> str:
        """
        Procesa texto y devuelve respuesta
        """
        try:
            # Clasificar intención
            debug_info = self.classifier.debug_classify(text)
            intent = debug_info['final_intent']
            
            print(f"🎯 Intención detectada: {intent}")
            
            # Enrutar
            if intent == "system_command":
                response = self.router.auto_send(text)
            else:
                response = self.router.send(intent, text)
            
            return response
            
        except Exception as e:
            return f"❌ Error procesando tu solicitud: {str(e)}"
    
    def start_loop(self):
        """
        Inicia el bucle principal de voz
        """
        if self.is_running:
            print("⚠️ VoiceLoop ya está en ejecución")
            return
        
        self.is_running = True
        print("\n🎤 Bucle de voz iniciado")
        print("Di 'parar' o 'salir' para terminar")
        print("-" * 40)
        
        while self.is_running:
            try:
                # Grabación con VAD
                print("\n🎤 Escuchando... (habla ahora)")
                audio_file = self.vad.record()
                
                if not audio_file:
                    print("⚠️ No se grabó audio, reintentando...")
                    continue
                
                # Procesar audio
                response_audio = self.process_audio_input(audio_file)
                
                # Reproducir respuesta si existe
                if response_audio and os.path.exists(response_audio):
                    # Reproducir audio (Linux)
                    os.system(f"aplay {response_audio} 2>/dev/null")
                    
                    # Limpiar archivo temporal
                    try:
                        os.remove(response_audio)
                    except:
                        pass
                
                # Pequeña pausa entre iteraciones
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupción por teclado")
                self.stop_loop()
                break
            except Exception as e:
                print(f"❌ Error en el bucle de voz: {e}")
                continue
    
    def stop_loop(self):
        """
        Detiene el bucle de voz
        """
        self.is_running = False
        print("\n🛑 Bucle de voz detenido")
    
    def start_async(self):
        """
        Inicia el bucle de voz en un hilo separado
        """
        if self.current_thread and self.current_thread.is_alive():
            print("⚠️ VoiceLoop ya está ejecutándose en un hilo")
            return
        
        self.current_thread = threading.Thread(target=self.start_loop)
        self.current_thread.daemon = True
        self.current_thread.start()
        print("✅ VoiceLoop iniciado en hilo separado")
    
    def wait_for_completion(self):
        """
        Espera a que el hilo de voz termine
        """
        if self.current_thread:
            self.current_thread.join()


# Función de prueba
if __name__ == "__main__":
    voice_loop = VoiceLoop()
    
    try:
        print("🔊 Iniciando prueba de VoiceLoop...")
        voice_loop.start_loop()
    except KeyboardInterrupt:
        voice_loop.stop_loop()
        print("👋 Prueba terminada")