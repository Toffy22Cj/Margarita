# [file name]: voice_loop.py (actualizado)
import os
import time
from src.vad_recorder import VADRecorder
from src.stt import SpeechToText
from src.tts import TextToSpeech
from src.router import Router
from src.intent_classifier import IntentClassifier

# --- Inicializar módulos ---
vad = VADRecorder()
stt = SpeechToText(model_size="small", device="cpu")
tts = TextToSpeech()
router = Router()
intent_classifier = IntentClassifier()

def main_loop():
    print("=== Margarita Voice Loop con VAD ===")
    print("🎤 Di comandos como: 'abre el navegador', 'crea una carpeta', 'traduce esto'")
    print("💻 Comandos de código: 'ayuda con python', 'explica esta función'")
    print("💬 O simplemente conversa normalmente")
    print("Presiona Ctrl+C para salir.\n")

    try:
        while True:
            # --- 1. Grabación con VAD ---
            print("🎤 Escuchando... (habla ahora)")
            audio_file = vad.record()
            if not audio_file:
                print("⚠️ No se grabó audio, reintentando...")
                continue
                
            print(f"✅ Audio guardado: {audio_file}")

            # --- 2. STT ---
            print("👂 Transcribiendo audio...")
            try:
                text = stt.transcribe(audio_file, lang="es")
                if not text or text.strip() == "":
                    print("⚠️ No se detectó speech, reintentando...")
                    continue
            except Exception as e:
                print(f"❌ Error en STT: {e}")
                continue
                
            print(f"📝 Tú dijiste: '{text}'")

            # --- 3. Detectar intención (con debug) ---
            debug_info = intent_classifier.debug_classify(text)
            intent = debug_info['final_intent']
            
            print(f"🎯 Intención detectada: {intent}")
            for reason in debug_info['reasons']:
                print(f"   📍 {reason}")

            # --- 4. Router envía al núcleo correspondiente ---
            print(f"🔄 Enrutando a núcleo: {intent}...")
            try:
                if intent == "system_command":
                    # Para comandos del sistema, usar auto_send que maneja la ejecución
                    response = router.auto_send(text)
                else:
                    # Para otros tipos, usar envío directo
                    response = router.send(intent, text)
                    
                print(f"🤖 Margarita: {response}")
            except Exception as e:
                response = f"Lo siento, hubo un error procesando tu solicitud: {str(e)}"
                print(f"❌ Error en router: {e}")

            # --- 5. TTS ---
            if response and response.strip():
                print("🗣️ Generando audio...")
                try:
                    out_wav = tts.speak(response)
                    if os.path.exists(out_wav):
                        print("🔊 Reproduciendo audio...")
                        os.system(f"aplay {out_wav} 2>/dev/null")  # Silencia errores de aplay
                    else:
                        print(f"⚠️ Archivo de audio no encontrado: {out_wav}")
                except Exception as e:
                    print(f"❌ Error en TTS: {e}")
            else:
                print("⚠️ No hay respuesta para convertir a audio")

            print("\n" + "="*50 + "\n")

    except KeyboardInterrupt:
        print("\n👋 Saliendo de Margarita...")
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")

def quick_test_mode():
    """
    Modo de prueba rápida sin audio - para testing
    """
    print("=== MODO PRUEBA RÁPIDA ===")
    print("Escribe comandos para probar (escribe 'salir' para terminar)\n")
    
    while True:
        try:
            text = input("Tú: ").strip()
            if text.lower() in ['salir', 'exit', 'quit']:
                break
            if not text:
                continue
                
            # Procesar igual que en el loop principal
            debug_info = intent_classifier.debug_classify(text)
            intent = debug_info['final_intent']
            
            print(f"🎯 Intención: {intent}")
            for reason in debug_info['reasons']:
                print(f"   📍 {reason}")
                
            if intent == "system_command":
                response = router.auto_send(text)
            else:
                response = router.send(intent, text)
                
            print(f"🤖 Margarita: {response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        quick_test_mode()
    else:
        main_loop()