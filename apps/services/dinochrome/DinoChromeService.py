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

            print(f"[DINOCHROME] 🎁 Procesando regalo: {gift_name} (Queue ID: {queue_item.id})")

            # Si es una rosa, reiniciar el juego y reproducir audio
            if 'rose' in gift_name or 'rosa' in gift_name:
                print(f"[DINOCHROME] 🌹 Rosa detectada! (Queue ID: {queue_item.id})")

                # Generar texto dinámico con LLM usando prompts variados
                username = live_event.user_nickname or live_event.user_unique_id or 'alguien'

                # Sistema de prompts variados con diferentes emociones y contextos
                system_prompts = [
                    # Enojado / Frustrado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Estás frustrado pero de forma cómica. Genera UNA SOLA FRASE corta (máximo 200 caracteres) expresando tu frustración de forma exagerada pero divertida. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Dramático / Exagerado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Eres dramático y exagerado. Genera UNA SOLA FRASE corta (máximo 200 caracteres) como si fuera una tragedia cómica. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Sarcástico / Irónico
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Eres sarcástico. Genera UNA SOLA FRASE corta (máximo 200 caracteres) agradeciendo irónicamente. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Resignado / Filosófico
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Estás resignado pero filosófico. Genera UNA SOLA FRASE corta (máximo 200 caracteres) aceptando tu destino de forma graciosa. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Sorprendido / Confundido
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Estás confundido y sorprendido. Genera UNA SOLA FRASE corta (máximo 200 caracteres) expresando tu confusión de forma graciosa. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Agradecido pero afectado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Agradeces el regalo pero lamentas el reinicio. Genera UNA SOLA FRASE corta (máximo 200 caracteres) siendo amable pero dramático. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Melodramático / Telenovela
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Hablas como personaje de telenovela mexicana. Genera UNA SOLA FRASE corta (máximo 200 caracteres) super melodramática y divertida. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Juguetón / Bromista
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó una rosa que reinició tu juego. Eres juguetón y bromista. Genera UNA SOLA FRASE corta (máximo 200 caracteres) bromeando sobre la situación. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok."
                ]

                # Seleccionar un prompt aleatorio
                selected_prompt = random.choice(system_prompts)

                # PASO 1: Generar texto con LLM
                try:
                    llm_start = time.time()
                    ai_response = self.llm.chat(
                        user_message=f"El usuario {username} acaba de donar una rosa en el stream.",
                        system_message=selected_prompt,
                        max_tokens=50,  # Reducido para frases más cortas
                        temperature=0.9
                    )
                    llm_time = time.time() - llm_start
                    print(f"[DINOCHROME] ⏱️ LLM generó texto en {llm_time:.2f}s")
                except Exception as e:
                    print(f"[DINOCHROME] ❌ Error LLM: {e}")
                    ai_response = f"Ay {username}, me reiniciaste el juego!"

                # Verificar que hay respuesta
                if not ai_response:
                    ai_response = f"Gracias por la rosa {username}, pero me reiniciaste el juego!"

                # PASO 2: Generar audio con ElevenLabs
                try:
                    audio_file = self.elevenlabs.text_to_speech_and_save(
                        ai_response,
                        voice_id="KHCvMklQZZo0O30ERnVn",
                        play_audio=False,
                        wait=False
                    )

                    # PASO 3: Reiniciar juego + Reproducir audio simultáneamente
                    if audio_file:
                        self.chrome.restart()  # Reiniciar primero (sin latencia)
                        self.elevenlabs.play_audio(audio_file, wait=True)  # Reproducir inmediatamente después
                        print(f"[DINOCHROME] ✅ Proceso completado (Queue ID: {queue_item.id})")
                    else:
                        print(f"[DINOCHROME] ⚠️ No se generó archivo de audio (Queue ID: {queue_item.id})")
                except Exception as e:
                    print(f"[DINOCHROME] ❌ Error ElevenLabs: {e}")
                    return False

                return True

            # No es una rosa, solo retornar True
            print(f"[DINOCHROME] ℹ️ No es una rosa, ignorando (Queue ID: {queue_item.id})")
            return True

        except Exception as e:
            print(f"[DINOCHROME] ❌ Error crítico: {e} (Queue ID: {queue_item.id})")
            import traceback
            traceback.print_exc()
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
