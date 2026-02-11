import speech_recognition as sr

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def escuchar_y_transcribir(self):
        try:
            with sr.Microphone() as source:
                print(">> Calibrando ruido de fondo... (Silencio)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(">> ¡Habla ahora!")
                
                # Escucha con un límite de tiempo de 5 segundos
                audio = self.recognizer.listen(source, timeout=5)

                # show_all=True nos da un diccionario con 'confidence'
                respuesta_google = self.recognizer.recognize_google(
                    audio, 
                    language="es-ES", 
                    show_all=True
                )

                # Si Google no devuelve nada o devuelve una lista vacía
                if not respuesta_google or 'alternative' not in respuesta_google:
                    return {"texto": "", "confianza": 0.0, "status": "FAIL_SILENCIO"}

                # Tomamos la mejor alternativa (la primera)
                mejor_resultado = respuesta_google['alternative'][0]
                texto = mejor_resultado.get('transcript', '').lower()
                confianza = mejor_resultado.get('confidence', 0.0)

                return {
                    "texto": texto,
                    "confianza": confianza,
                    "status": "OK"
                }

        except sr.WaitTimeoutError:
            return {"status": "ERROR", "motivo": "Tiempo de espera agotado"}
        except sr.UnknownValueError:
            return {"status": "ERROR", "motivo": "No se entendió el audio"}
        except sr.RequestError:
            return {"status": "ERROR", "motivo": "Error de conexión con Google"}
        except Exception as e:
            return {"status": "ERROR", "motivo": str(e)}