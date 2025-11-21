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
        self.gif_counter = 0  # Contador para secuencia de GIFs
        self.gif_slot_queue = []  # Cola de slots disponibles [1, 2, 3, 4, 5]

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        from datetime import datetime
        self.session_start = datetime.now()

        # Inicializar cola de slots (todos disponibles al inicio)
        self.gif_slot_queue = [1, 2, 3, 4, 5]

        # Inicializar navegador Chrome con DinoChrome (con interfaz gráfica)
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

            # Si es "You're awesome", activar GIF bailando
            if "you're awesome" in gift_name or "awesome" in gift_name:
                # Usar repeat_count (número de regalos en este evento)
                gift_count = event_data.get('repeat_count', 1)

                print(f"[DINOCHROME] 🎉 You're awesome detectado! Cantidad: x{gift_count} (Queue ID: {queue_item.id})")

                # Enviar un GIF por cada regalo
                for i in range(gift_count):
                    self._send_dancing_gif(live_event)
                    print(f"[DINOCHROME] 💃 GIF {i+1}/{gift_count} enviado")

                return True

            # Si es un cono de helado, reiniciar el juego y reproducir audio
            if 'ice cream' in gift_name or 'cone' in gift_name:
                print(f"[DINOCHROME] 🍦 Cono de helado detectado! (Queue ID: {queue_item.id})")

                # Generar texto dinámico con LLM usando prompts variados
                username = live_event.user_nickname or live_event.user_unique_id or 'alguien'

                # Sistema de prompts variados con diferentes emociones y contextos
                system_prompts = [
                    # Enojado / Frustrado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Estás frustrado pero de forma cómica. Genera UNA SOLA FRASE corta (máximo 200 caracteres) expresando tu frustración de forma exagerada pero divertida. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Dramático / Exagerado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Eres dramático y exagerado. Genera UNA SOLA FRASE corta (máximo 200 caracteres) como si fuera una tragedia cómica. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Sarcástico / Irónico
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Eres sarcástico. Genera UNA SOLA FRASE corta (máximo 200 caracteres) agradeciendo irónicamente. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Resignado / Filosófico
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Estás resignado pero filosófico. Genera UNA SOLA FRASE corta (máximo 200 caracteres) aceptando tu destino de forma graciosa. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Sorprendido / Confundido
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Estás confundido y sorprendido. Genera UNA SOLA FRASE corta (máximo 200 caracteres) expresando tu confusión de forma graciosa. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Agradecido pero afectado
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Agradeces el regalo pero lamentas el reinicio. Genera UNA SOLA FRASE corta (máximo 200 caracteres) siendo amable pero dramático. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Melodramático / Telenovela
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Hablas como personaje de telenovela mexicana. Genera UNA SOLA FRASE corta (máximo 200 caracteres) super melodramática y divertida. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok.",

                    # Juguetón / Bromista
                    f"Eres un streamer jugando DinoChrome en TikTok Live. {username} donó un cono de helado que reinició tu juego. Eres juguetón y bromista. Genera UNA SOLA FRASE corta (máximo 200 caracteres) bromeando sobre la situación. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserías, sin palabras ofensivas. PROHIBIDO usar palabras como: muerte, muerto, morir, suicidio, matar, asesinar, maldita/o, diablos, infierno, o cualquier referencia a violencia, daño físico o temas sensibles. Contenido 100% familiar y apropiado para TikTok."
                ]

                # Seleccionar un prompt aleatorio
                selected_prompt = random.choice(system_prompts)
                print(f"[DINOCHROME] 🎲 Prompt seleccionado: {selected_prompt[:100]}...")

                # PASO 1: Generar texto con LLM
                try:
                    llm_start = time.time()
                    print(f"[DINOCHROME] 🤖 Llamando al LLM...")
                    ai_response = self.llm.chat(
                        user_message=f"El usuario {username} acaba de donar un cono de helado en el stream.",
                        system_message=selected_prompt,
                        max_tokens=200,  # Aumentado para reasoning + respuesta
                        temperature=0.9
                    )
                    llm_time = time.time() - llm_start

                    if ai_response:
                        print(f"[DINOCHROME] ✅ LLM generó texto en {llm_time:.2f}s")
                        print(f"[DINOCHROME] 💬 Respuesta LLM: '{ai_response}'")
                    else:
                        print(f"[DINOCHROME] ⚠️ LLM retornó None en {llm_time:.2f}s")
                        ai_response = f"Ay {username}, me reiniciaste el juego con ese helado!"
                        print(f"[DINOCHROME] 🔄 Usando fallback: '{ai_response}'")

                except Exception as e:
                    print(f"[DINOCHROME] ❌ Error LLM: {e}")
                    ai_response = f"Ay {username}, me reiniciaste el juego con ese helado!"
                    print(f"[DINOCHROME] 🔄 Usando fallback por error: '{ai_response}'")

                # Verificar que hay respuesta
                if not ai_response:
                    ai_response = f"Gracias por el cono de helado {username}, pero me reiniciaste el juego!"
                    print(f"[DINOCHROME] 🔄 Usando fallback final: '{ai_response}'")

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


            # No es ningún regalo configurado, solo retornar True
            print(f"[DINOCHROME] ℹ️ Regalo no configurado, ignorando (Queue ID: {queue_item.id})")
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

    def _send_dancing_gif(self, live_event):
        """
        Envía un GIF bailando a un slot disponible

        Gestiona sistema de slots (máximo 5 GIFs simultáneos)
        y secuencia de GIFs (va rotando por los 10 GIFs disponibles)
        """
        try:
            from apps.services.dinochrome.overlays.views import send_dinochrome_overlay_event, AVAILABLE_GIFS

            # Si no hay slots disponibles, liberar el más viejo (FIFO)
            if not self.gif_slot_queue:
                print(f"[DINOCHROME] ⚠️ Todos los slots ocupados, reciclando slot 1")
                self.gif_slot_queue = [1, 2, 3, 4, 5]

            # Obtener siguiente slot disponible
            slot = self.gif_slot_queue.pop(0)

            # Obtener siguiente GIF de la secuencia
            gif_index = self.gif_counter % len(AVAILABLE_GIFS)
            gif_filename = AVAILABLE_GIFS[gif_index]
            self.gif_counter += 1

            # Datos del evento
            event_data = live_event.event_data
            username = live_event.user_nickname or live_event.user_unique_id or 'Anónimo'
            gift_name = event_data.get('gift', {}).get('name', 'Regalo')

            # Enviar evento al slot
            send_dinochrome_overlay_event(
                overlay_type=f'gif-{slot}',
                event_type='dancing_gif',
                data={
                    'username': username,
                    'gift_name': gift_name,
                    'gif_filename': gif_filename,
                    'slot': slot,
                }
            )

            print(f"[DINOCHROME] 💃 GIF enviado: {gif_filename} → Slot {slot} (Usuario: {username})")

            # Programar liberación del slot después de 60 segundos
            import threading
            def free_slot():
                import time
                time.sleep(60)
                if slot not in self.gif_slot_queue:
                    self.gif_slot_queue.append(slot)
                    print(f"[DINOCHROME] ♻️ Slot {slot} liberado")

            threading.Thread(target=free_slot, daemon=True).start()

        except Exception as e:
            print(f"[DINOCHROME] ❌ Error enviando GIF bailando: {e}")
            import traceback
            traceback.print_exc()
