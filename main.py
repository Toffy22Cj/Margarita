# [file name]: main.py
#!/usr/bin/env python3
"""
Margarita - Asistente Personal Inteligente
Sistema unificado con interfaz de voz y texto
"""

import os
import sys
import threading
import time
from pathlib import Path

# Añadir el directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from src.vad_recorder import VADRecorder
from src.stt import SpeechToText
from src.tts import TextToSpeech
from src.router import Router
from src.intent_classifier import IntentClassifier


class MargaritaApp:
    """
    Aplicación principal de Margarita que unifica voz y texto
    """
    
    def __init__(self):
        print("🔄 Inicializando Margarita...")
        
        # Inicializar componentes
        self.vad = VADRecorder()
        self.stt = SpeechToText(model_size="small", device="cpu")
        self.tts = TextToSpeech()
        self.router = Router()
        self.classifier = IntentClassifier()
        
        # Estado de la aplicación
        self.running = False
        self.current_mode = None
        
        print("✅ Margarita inicializada correctamente")
    
    def process_text(self, text: str) -> str:
        """
        Procesa texto y devuelve la respuesta
        """
        try:
            if not text or text.strip() == "":
                return "No escuché nada. ¿Podrías repetirlo?"
            
            print(f"📝 Procesando: '{text}'")
            
            # Clasificar intención
            debug_info = self.classifier.debug_classify(text)
            intent = debug_info['final_intent']
            
            print(f"🎯 Intención: {intent}")
            for reason in debug_info['reasons']:
                print(f"   📍 {reason}")
            
            # Enrutar
            if intent == "system_command":
                response = self.router.auto_send(text)
            else:
                response = self.router.send(intent, text)
            
            return response
            
        except Exception as e:
            return f"❌ Error procesando tu solicitud: {str(e)}"
    
    def voice_mode(self):
        """
        Modo de reconocimiento de voz continuo
        """
        print("\n🎤 MODO VOZ ACTIVADO")
        print("Di 'modo texto' para cambiar a entrada por teclado")
        print("Di 'salir' para terminar el programa")
        print("-" * 50)
        
        self.current_mode = "voice"
        self.running = True
        
        while self.running:
            try:
                # Grabación con VAD
                print("\n🎤 Escuchando... (habla ahora)")
                audio_file = self.vad.record()
                if not audio_file:
                    print("⚠️ No se grabó audio, reintentando...")
                    continue
                
                # Transcripción
                print("👂 Transcribiendo...")
                text = self.stt.transcribe(audio_file, lang="es")
                
                if not text or text.strip() == "":
                    print("⚠️ No se detectó speech")
                    continue
                
                print(f"📝 Tú dijiste: '{text}'")
                
                # Comandos especiales del modo voz
                if any(cmd in text.lower() for cmd in ["modo texto", "texto", "teclado"]):
                    self.text_mode()
                    return
                
                if any(cmd in text.lower() for cmd in ["salir", "terminar", "adiós"]):
                    self.quit_app()
                    return
                
                # Procesar texto
                response = self.process_text(text)
                print(f"🤖 Margarita: {response}")
                
                # TTS
                if response and response.strip():
                    print("🗣️ Generando audio...")
                    out_wav = self.tts.speak(response)
                    if os.path.exists(out_wav):
                        os.system(f"aplay {out_wav} 2>/dev/null")
                    # Limpiar archivo temporal
                    try:
                        os.remove(out_wav)
                    except:
                        pass
            
            except KeyboardInterrupt:
                self.quit_app()
                return
            except Exception as e:
                print(f"❌ Error en modo voz: {e}")
                continue
    
    def text_mode(self):
        """
        Modo de entrada por teclado
        """
        print("\n⌨️  MODO TEXTO ACTIVADO")
        print("Escribe 'modo voz' para cambiar a reconocimiento de voz")
        print("Escribe 'salir' para terminar el programa")
        print("-" * 50)
        
        self.current_mode = "text"
        self.running = True
        
        while self.running:
            try:
                text = input("\nTú: ").strip()
                
                if not text:
                    continue
                
                # Comandos especiales del modo texto
                if text.lower() in ["modo voz", "voz", "audio"]:
                    self.voice_mode()
                    return
                
                if text.lower() in ["salir", "exit", "quit"]:
                    self.quit_app()
                    return
                
                # Procesar texto
                response = self.process_text(text)
                print(f"🤖 Margarita: {response}")
                
            except KeyboardInterrupt:
                self.quit_app()
                return
            except Exception as e:
                print(f"❌ Error en modo texto: {e}")
                continue
    
    def interactive_mode(self):
        """
        Modo interactivo que permite elegir entre voz y texto
        """
        print("""
    🎀 Margarita - Asistente Personal 🎀
    ===================================
    
    ¿Cómo quieres interactuar?
    
    1. 🎤 Modo Voz - Reconocimiento de voz continuo
    2. ⌨️  Modo Texto - Entrada por teclado
    3. 🚀 Modo Automático - Intenta voz, falla a texto
    4. ❌ Salir
    
        """)
        
        while True:
            try:
                choice = input("Elige una opción (1-4): ").strip()
                
                if choice == "1":
                    self.voice_mode()
                    break
                elif choice == "2":
                    self.text_mode()
                    break
                elif choice == "3":
                    self.auto_mode()
                    break
                elif choice == "4":
                    self.quit_app()
                    break
                else:
                    print("❌ Opción no válida. Por favor elige 1-4")
            
            except KeyboardInterrupt:
                self.quit_app()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def auto_mode(self):
        """
        Modo automático: intenta usar voz, si falla usa texto
        """
        print("\n🚀 MODO AUTOMÁTICO ACTIVADO")
        print("Intentando modo voz...")
        
        try:
            # Probar si el sistema de audio funciona
            test_audio = self.vad.record(timeout=3)
            if test_audio:
                print("✅ Sistema de voz funcionando, iniciando modo voz...")
                self.voice_mode()
            else:
                raise Exception("No se pudo grabar audio")
                
        except Exception as e:
            print(f"❌ Modo voz no disponible: {e}")
            print("🔀 Cambiando a modo texto...")
            self.text_mode()
    
    def quick_command(self, command: str):
        """
        Ejecuta un comando rápido sin interfaz interactiva
        """
        print(f"⚡ Ejecutando comando rápido: {command}")
        response = self.process_text(command)
        print(f"🤖 {response}")
        return response
    
    def quit_app(self):
        """
        Cierra la aplicación gracefulmente
        """
        print("\n👋 Saliendo de Margarita...")
        self.running = False
        print("¡Hasta pronto! 🎀")


def main():
    """
    Función principal con argumentos de línea de comandos
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Margarita - Asistente Personal")
    parser.add_argument(
        "--mode", 
        choices=["voice", "text", "auto", "interactive"],
        default="interactive",
        help="Modo de operación (default: interactive)"
    )
    parser.add_argument(
        "--command", 
        type=str,
        help="Ejecuta un comando rápido y sale"
    )
    
    args = parser.parse_args()
    
    # Crear instancia de la app
    app = MargaritaApp()
    
    try:
        if args.command:
            # Modo comando rápido
            app.quick_command(args.command)
        else:
            # Modos interactivos
            if args.mode == "voice":
                app.voice_mode()
            elif args.mode == "text":
                app.text_mode()
            elif args.mode == "auto":
                app.auto_mode()
            else:  # interactive
                app.interactive_mode()
    
    except KeyboardInterrupt:
        app.quit_app()
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        app.quit_app()


if __name__ == "__main__":
    main()