"""
DinoChrome Service - Procesador de eventos TikTok para juego DinoChrome

Todo se renderiza en el browser via SSE (sin Selenium).
El frontend maneja: juego, overlays, audio TTS.

Concurrencia:
- Ice Cream / GG: siempre paralelo, nunca bloqueado
- Rose: secuencial entre si, pero Rosa la interrumpe
- Rosa: maxima prioridad, secuencial entre si, interrumpe Rose
"""

import os
import random
import time
import threading

from django.conf import settings

from apps.queue_system.base_service import BaseQueueService
from apps.integrations.elevenlabs.client import ElevenLabsClient
from apps.integrations.llm.client import LLMClient
from apps.services.dinochrome.overlays.views import send_dinochrome_event, AVAILABLE_GIFS


class DinoChromeService(BaseQueueService):

    def __init__(self):
        self.session_start = None
        self.elevenlabs = ElevenLabsClient()
        self.llm = LLMClient()
        self.gif_counter = 0

        # Concurrencia Rosa/Rose
        self.tts_lock = threading.Lock()       # Serializa todo TTS (Rosa y Rose)
        self.rosa_pending = 0                   # Contador de Rosas pendientes
        self.rosa_pending_lock = threading.Lock()
        self.rose_interrupted = threading.Event()  # Senal para interrumpir Rose

    def on_start(self):
        from datetime import datetime
        self.session_start = datetime.now()
        self.elevenlabs = ElevenLabsClient()
        self.llm = LLMClient()

    def on_stop(self):
        pass

    def process_event(self, live_event, queue_item):
        try:
            event_type = live_event.event_type

            if event_type == 'GiftEvent':
                return self._process_gift(live_event, queue_item)
            elif event_type == 'CommentEvent':
                return True
            elif event_type == 'LikeEvent':
                return True
            elif event_type == 'ShareEvent':
                return True
            elif event_type == 'FollowEvent':
                return True
            elif event_type == 'SubscribeEvent':
                return True
            else:
                return False

        except Exception:
            return False

    def _process_gift(self, live_event, queue_item):
        try:
            event_data = live_event.event_data
            gift_name = event_data.get('gift', {}).get('name', '').lower()
            username = live_event.user_nickname or live_event.user_unique_id or 'alguien'

            print(f"[DINOCHROME] Gift: {gift_name} de @{username} (streak: {live_event.streak_status}, Queue ID: {queue_item.id})")

            # === ICE CREAM / GIFs: paralelo, uno por racha (end/None) ===
            if any(kw in gift_name for kw in ['ice cream', 'cone', 'awesome', "you're awesome", 'enjoy music', 'music']):
                if live_event.streak_status in ('start', 'continue'):
                    return True
                self._send_dancing_gif(live_event)
                return True

            # === GG: paralelo, uno por racha (end/None) ===
            if gift_name == 'gg':
                if live_event.streak_status in ('start', 'continue'):
                    return True
                self._process_gg(username)
                return True

            # === ROSA: maxima prioridad, interrumpe Rose ===
            # Solo procesar cada evento individual (start/continue), ignorar end de racha
            if gift_name == 'rosa':
                if live_event.streak_status == 'end':
                    return True
                return self._process_rosa(username, queue_item)

            # === ROSE: secuencial, se interrumpe si hay Rosa pendiente ===
            # Solo procesar al final de racha (end) o sin racha (None)
            if gift_name == 'rose':
                if live_event.streak_status in ('start', 'continue'):
                    return True
                return self._process_rose(username, event_data, queue_item)

            # Otro regalo
            print(f"[DINOCHROME] Regalo '{gift_name}' de @{username}")
            return True

        except Exception as e:
            print(f"[DINOCHROME] Error critico: {e} (Queue ID: {queue_item.id})")
            import traceback
            traceback.print_exc()
            return False

    def _process_rosa(self, username, queue_item):
        """
        Rosa: maxima prioridad.
        - Interrumpe cualquier Rose en curso
        - Secuencial entre Rosas (una a la vez)
        - LLM se genera ANTES del lock (paralelo), pero restart+audio DENTRO del lock (secuencial)
        """
        # Marcar que hay Rosa pendiente -> Rose debe abortarse
        with self.rosa_pending_lock:
            self.rosa_pending += 1
        self.rose_interrupted.set()

        print(f"[DINOCHROME] ROSA de @{username} - prioridad maxima (pendientes: {self.rosa_pending})")

        # Generar LLM + TTS FUERA del lock (en paralelo mientras otra Rosa reproduce)
        ai_response, audio_file = self._generate_rosa_audio(username)

        # Adquirir lock para restart + reproduccion (secuencial)
        with self.tts_lock:
            self.rose_interrupted.clear()

            try:
                return self._play_rosa(username, ai_response, audio_file)
            finally:
                with self.rosa_pending_lock:
                    self.rosa_pending -= 1

    def _process_rose(self, username, event_data, queue_item):
        """
        Rose: secuencial, pero se aborta si hay Rosa pendiente.
        """
        # Si hay Rosa pendiente, no ejecutar Rose
        with self.rosa_pending_lock:
            if self.rosa_pending > 0:
                print(f"[DINOCHROME] Rose de @{username} ABORTADA - Rosa pendiente")
                return True

        # Adquirir lock TTS
        with self.tts_lock:
            # Verificar de nuevo dentro del lock
            with self.rosa_pending_lock:
                if self.rosa_pending > 0:
                    print(f"[DINOCHROME] Rose de @{username} ABORTADA - Rosa pendiente")
                    return True

            return self._handle_rose(username, event_data, queue_item)

    def _handle_rose(self, username, event_data, queue_item):
        """Rose gift: overlay + TTS correccion (puede ser interrumpida por Rosa)"""
        rose_start = time.time()

        # Enviar overlay
        send_dinochrome_event('rose_gift', {
            'username': username,
            'gift_name': 'Rose',
            'count': event_data.get('gift', {}).get('count', 1),
        })

        try:
            correction_text = f"No es 'Rose' {username}, es 'Rosa'... ROSA!"
            audio_file = self.elevenlabs.text_to_speech_and_save(
                correction_text,
                voice_id="KHCvMklQZZo0O30ERnVn",
                play_audio=False,
                wait=False
            )

            # Verificar interrupcion antes de reproducir
            if self.rose_interrupted.is_set():
                print(f"[DINOCHROME] Rose INTERRUMPIDA por Rosa antes de audio")
                return True

            if audio_file:
                self._send_tts_audio(audio_file)
                duration = self._get_audio_duration(audio_file)

                # Esperar duracion pero verificar interrupcion cada 0.5s
                elapsed = 0
                while elapsed < duration:
                    if self.rose_interrupted.is_set():
                        print(f"[DINOCHROME] Rose INTERRUMPIDA por Rosa durante audio")
                        return True
                    time.sleep(min(0.5, duration - elapsed))
                    elapsed += 0.5

                total_time = time.time() - rose_start
                print(f"[DINOCHROME] Rose completado en {total_time:.1f}s")
        except Exception as e:
            print(f"[DINOCHROME] Error en correccion: {e}")

        return True

    def _generate_rosa_audio(self, username):
        """Genera texto LLM + audio TTS para Rosa (puede correr en paralelo)"""
        system_prompts = [
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Estas frustrado pero de forma comica. Genera UNA SOLA FRASE corta (maximo 200 caracteres) expresando tu frustracion de forma exagerada pero divertida. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Eres dramatico y exagerado. Genera UNA SOLA FRASE corta (maximo 200 caracteres) como si fuera una tragedia comica. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Eres sarcastico. Genera UNA SOLA FRASE corta (maximo 200 caracteres) agradeciendo ironicamente. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Estas resignado pero filosofico. Genera UNA SOLA FRASE corta (maximo 200 caracteres) aceptando tu destino de forma graciosa. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Estas confundido y sorprendido. Genera UNA SOLA FRASE corta (maximo 200 caracteres) expresando tu confusion de forma graciosa. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Agradeces el regalo pero lamentas el reinicio. Genera UNA SOLA FRASE corta (maximo 200 caracteres) siendo amable pero dramatico. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Hablas como personaje de telenovela mexicana. Genera UNA SOLA FRASE corta (maximo 200 caracteres) super melodramatica y divertida. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
            f"Eres un streamer jugando DinoChrome en TikTok Live. {username} dono una rosa que reinicio tu juego. Eres jugueton y bromista. Genera UNA SOLA FRASE corta (maximo 200 caracteres) bromeando sobre la situacion. Menciona a {username}. IMPORTANTE: Sin maldiciones, sin groserias, sin palabras ofensivas. Contenido 100% familiar y apropiado para TikTok.",
        ]

        # PASO 1: Generar texto con LLM
        self.llm = LLMClient()
        ai_response = None
        try:
            llm_start = time.time()
            ai_response = self.llm.chat(
                user_message=f"El usuario {username} acaba de donar una rosa en el stream.",
                system_message=random.choice(system_prompts),
                max_tokens=200,
                temperature=0.9
            )
            llm_time = time.time() - llm_start
            print(f"[DINOCHROME] LLM respondio en {llm_time:.2f}s: '{ai_response}'")
        except Exception as e:
            print(f"[DINOCHROME] Error LLM: {e}")

        if not ai_response:
            ai_response = f"Ay {username}, me reiniciaste el juego con esa rosa!"

        # PASO 2: Generar audio con ElevenLabs
        audio_file = None
        try:
            audio_file = self.elevenlabs.text_to_speech_and_save(
                ai_response,
                voice_id="KHCvMklQZZo0O30ERnVn",
                play_audio=False,
                wait=False
            )
        except Exception as e:
            print(f"[DINOCHROME] Error ElevenLabs: {e}")

        return ai_response, audio_file

    def _play_rosa(self, username, ai_response, audio_file):
        """Reproduce Rosa: restart + audio (corre dentro del tts_lock, secuencial)"""
        rosa_start = time.time()

        try:
            send_dinochrome_event('game_restart', {})

            if audio_file:
                self._send_tts_audio(audio_file)

                duration = self._get_audio_duration(audio_file)
                if duration > 0:
                    print(f"[DINOCHROME] Rosa: esperando {duration:.1f}s audio...")
                    time.sleep(duration)

                total_time = time.time() - rosa_start
                print(f"[DINOCHROME] Rosa de @{username} completado en {total_time:.1f}s")
        except Exception as e:
            print(f"[DINOCHROME] Error reproduciendo Rosa: {e}")
            return False

        return True

    def _process_gg(self, username):
        """GG: reproduce TTS 'Cambiando la musica' (paralelo, no bloquea nada)"""
        try:
            audio_file = self.elevenlabs.text_to_speech_and_save(
                "Cambiando la musica",
                voice_id="KHCvMklQZZo0O30ERnVn",
                play_audio=False,
                wait=False
            )
            if audio_file:
                self._send_tts_audio(audio_file)
            print(f"[DINOCHROME] GG de @{username} - TTS enviado")
        except Exception as e:
            print(f"[DINOCHROME] Error en GG TTS: {e}")

    def _send_dancing_gif(self, live_event):
        """Envia un GIF bailando con posicion aleatoria (ilimitado)"""
        try:
            gif_index = self.gif_counter % len(AVAILABLE_GIFS)
            gif_filename = AVAILABLE_GIFS[gif_index]
            self.gif_counter += 1

            username = live_event.user_nickname or live_event.user_unique_id or 'Anonimo'

            send_dinochrome_event('dancing_gif', {
                'username': username,
                'gif_filename': gif_filename,
            })

            print(f"[DINOCHROME] GIF: {gif_filename} ({username})")

        except Exception as e:
            print(f"[DINOCHROME] Error enviando GIF: {e}")

    def _get_audio_duration(self, audio_file):
        """Calcula la duracion de un archivo MP3 en segundos"""
        try:
            absolute_path = os.path.join(str(settings.MEDIA_ROOT), audio_file)
            file_size = os.path.getsize(absolute_path)
            estimated_duration = file_size / (128000 / 8)
            return estimated_duration + 0.5
        except Exception as e:
            print(f"[DINOCHROME] Error calculando duracion audio: {e}")
            return 3.0

    def _send_tts_audio(self, audio_file):
        """Envia evento para que el browser reproduzca audio TTS"""
        if audio_file.startswith('/'):
            media_root = str(settings.MEDIA_ROOT)
            if audio_file.startswith(media_root):
                audio_url = settings.MEDIA_URL + audio_file[len(media_root):].lstrip('/')
            else:
                audio_url = settings.MEDIA_URL + os.path.basename(audio_file)
        else:
            audio_url = settings.MEDIA_URL + audio_file

        send_dinochrome_event('tts_audio', {
            'audio_url': audio_url,
        })
