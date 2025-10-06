"""
DinoChrome Service - Controlador de Chrome para interacciones

Este servicio maneja eventos de TikTok y ejecuta acciones en Chrome/navegador.
Actualmente solo simula las acciones con timeouts y logs.
"""

from apps.queue_system.base_service import BaseQueueService
from apps.services.dinochrome.ChromeService import ChromeService
from apps.integrations.elevenlabs.client import ElevenLabsClient
from apps.integrations.llm.client import LLMClient


class DinoChromeService(BaseQueueService):
    """
    Servicio que controla Chrome para interacciones con el navegador

    Características:
    - Procesa eventos de TikTok
    - Simula acciones en Chrome con timeouts
    - Modo SYNC (eventos se procesan secuencialmente)
    """

    def __init__(self):
        self.session_start = None
        self.chrome = ChromeService()
        self.elevenlabs = ElevenLabsClient()
        self.llm = LLMClient()

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        from datetime import datetime
        self.session_start = datetime.now()

        # Inicializar navegador Chrome con DinoChrome
        self.chrome.initialize_browser(headless=False)

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        from datetime import datetime

        # Cerrar navegador Chrome
        self.chrome.close()

    def process_event(self, live_event, queue_item):
        """
        Procesa eventos de TikTok y ejecuta acciones en Chrome

        Args:
            live_event: El evento de TikTok
            queue_item: Metadata de la cola

        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            event_type = live_event.event_type

            # Procesar según tipo de evento
            if event_type == 'GiftEvent':
                return self._process_gift(live_event, queue_item)

            elif event_type == 'CommentEvent':
                return self._process_comment(live_event, queue_item)

            elif event_type == 'LikeEvent':
                return self._process_like(live_event, queue_item)

            elif event_type == 'ShareEvent':
                return self._process_share(live_event, queue_item)

            elif event_type == 'FollowEvent':
                return self._process_follow(live_event, queue_item)

            elif event_type == 'SubscribeEvent':
                return self._process_subscribe(live_event, queue_item)

            else:
                return False

        except Exception:
            return False

    def _process_gift(self, live_event, queue_item):
        """Procesa evento de regalo"""
        import random
        import time

        try:
            event_data = live_event.event_data
            gift_name = event_data.get('gift', {}).get('name', '').lower()

            # Si es una rosa, reiniciar el juego y reproducir audio
            if 'rose' in gift_name or 'rosa' in gift_name:
                print(f"[DINOCHROME] 🌹 Rosa detectada! Reiniciando juego...")

                # Primero reiniciar el juego
                self.chrome.restart()

                # Generar texto dinámico con LLM usando prompts variados
                username = live_event.user_nickname or live_event.user_unique_id or 'alguien'

                # Sistema de prompts variados con diferentes emociones y contextos
                system_prompts = [
                    # Enojado / Frustrado
                    f"Eres un jugador de DinoChrome en un directo de TikTok. {username} acaba de donarte una rosa y eso reinició tu juego justo cuando ibas muy bien. Estás FURIOSO y frustrado. Genera una respuesta corta (máximo 2-3 frases) expresando tu enojo de forma exagerada pero graciosa. Menciona a {username} directamente. Habla en primera persona como si estuvieras transmitiendo en vivo.",

                    # Dramático / Exagerado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} te donó una rosa que reinició tu partida. Eres EXTREMADAMENTE dramático y exagerado. Genera una respuesta corta (máximo 2-3 frases) como si fuera el fin del mundo, pero de forma cómica. Menciona a {username}. Actúa como si estuvieras narrando una tragedia épica.",

                    # Sarcástico / Irónico
                    f"Eres un jugador de DinoChrome en directo de TikTok. {username} donó una rosa que reinició tu juego. Eres muy SARCÁSTICO e irónico. Genera una respuesta corta (máximo 2-3 frases) agradeciendo 'irónicamente' el regalo mientras dejas claro tu frustración. Menciona a {username}. Usa mucho sarcasmo.",

                    # Resignado / Filosófico
                    f"Eres un streamer de DinoChrome en TikTok Live. {username} te envió una rosa que reinició tu partida. Estás resignado pero filosófico. Genera una respuesta corta (máximo 2-3 frases) aceptando tu destino de forma melodramática pero graciosa. Menciona a {username}. Habla como si fuera tu karma o destino.",

                    # Vengativo / Amenazante (de broma)
                    f"Eres un jugador de DinoChrome transmitiendo en TikTok. {username} donó una rosa que reinició tu juego. Estás 'amenazando' venganza de forma EXAGERADA y cómica (obviamente de broma). Genera una respuesta corta (máximo 2-3 frases) haciendo amenazas absurdas y graciosas. Menciona a {username}. Sé dramático pero claramente jugando.",

                    # Confundido / Traicionado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} te donó una rosa que reinició tu partida. Te sientes TRAICIONADO y confundido. Genera una respuesta corta (máximo 2-3 frases) preguntándote por qué te hicieron esto, de forma dramática. Menciona a {username}. Actúa como si fuera una traición épica.",

                    # Histérico / Pánico
                    f"Eres un jugador de DinoChrome en directo de TikTok. {username} donó una rosa que reinició tu juego. Entras en PÁNICO total y hablas de forma histérica. Genera una respuesta corta (máximo 2-3 frases) con mucha energía, como si estuvieras en shock. Menciona a {username}. Sé muy expresivo y caótico.",

                    # Melodramático / Telenovela
                    f"Eres un streamer de DinoChrome en TikTok Live. {username} te envió una rosa que reinició tu partida. Responde como si estuvieras en una TELENOVELA mexicana, super melodramático. Genera una respuesta corta (máximo 2-3 frases) con mucho drama. Menciona a {username}. Actúa como villano o protagonista de telenovela."
                ]

                # Seleccionar un prompt aleatorio
                selected_prompt = random.choice(system_prompts)

                # Generar respuesta con el prompt personalizado
                try:
                    # MEDICIÓN: Tiempo de generación de texto con LLM
                    llm_start = time.time()
                    ai_response = self.llm.chat(
                        user_message=f"El usuario {username} acaba de donar una rosa en el stream.",
                        system_message=selected_prompt,
                        max_tokens=150,
                        temperature=0.9
                    )
                    llm_time = time.time() - llm_start
                    print(f"[DINOCHROME] ⏱️ LLM generó texto en {llm_time:.2f}s")
                except Exception as e:
                    print(f"[DINOCHROME] ❌ Error LLM: {e}")
                    ai_response = f"No no no {username}! Me reiniciaste el juego justo cuando iba súper bien! Ahora qué voy a hacer?"

                # Verificar que hay respuesta
                if not ai_response:
                    ai_response = f"Gracias por la rosa {username}, pero me reiniciaste el juego!"

                try:
                    audio_file = self.elevenlabs.text_to_speech_and_save(
                        ai_response,
                        voice_id="KHCvMklQZZo0O30ERnVn",
                        play_audio=False,
                        wait=False
                    )
                    if audio_file:
                        self.elevenlabs.play_audio(audio_file, wait=True)
                except Exception as e:
                    print(f"[DINOCHROME] ❌ Error ElevenLabs: {e}")

                return True

            return True

        except Exception as e:
            print(f"[DINOCHROME] ❌ Error: {e}")
            return False

    def _process_comment(self, live_event, queue_item):
        """Procesa evento de comentario"""
        return True

    def _process_like(self, live_event, queue_item):
        """Procesa evento de like"""
        return True

    def _process_share(self, live_event, queue_item):
        """Procesa evento de compartir"""
        return True

    def _process_follow(self, live_event, queue_item):
        """Procesa evento de follow"""
        return True

    def _process_subscribe(self, live_event, queue_item):
        """Procesa evento de suscripción"""
        return True
