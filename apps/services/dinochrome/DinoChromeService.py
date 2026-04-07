"""
DinoChrome Service - Procesador de eventos TikTok para juego DinoChrome

Todo se renderiza en el browser via SSE (sin Selenium).
El frontend maneja: juego, overlays, audio TTS.
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
        self.gif_slot_queue = []

    def on_start(self):
        from datetime import datetime
        self.session_start = datetime.now()
        self.gif_slot_queue = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # Recargar clientes con config actualizada de la DB
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
        try:
            event_data = live_event.event_data
            gift_name = event_data.get('gift', {}).get('name', '').lower()
            username = live_event.user_nickname or live_event.user_unique_id or 'alguien'

            print(f"[DINOCHROME] Gift: {gift_name} de @{username} (streak: {live_event.streak_status}, Queue ID: {queue_item.id})")

            # Rose: solo procesar al FINALIZAR la racha (una sola accion con el total)
            if gift_name == 'rose':
                if live_event.streak_status in ('start', 'continue'):
                    return True  # Ignorar intermedios, esperar al end
                return self._handle_rose(username, event_data, queue_item)

            # Para Rosa, Ice Cream, etc: procesar CADA evento, ignorar solo el end
            if live_event.streak_status == 'end':
                return True

            # Rosa: LLM + TTS + reinicia el juego (cada uno de la racha)
            if gift_name == 'rosa':
                return self._handle_rosa(username, queue_item)

            # Ice Cream / Awesome / Enjoy Music: GIF bailando (cada uno de la racha)
            if any(kw in gift_name for kw in ['ice cream', 'cone', 'awesome', "you're awesome", 'enjoy music', 'music']):
                self._send_dancing_gif(live_event)
                return True

            # Otro regalo: audio agradecimiento
            print(f"[DINOCHROME] Regalo '{gift_name}' de @{username} - agradecimiento")
            self._send_tts_audio('default_gift_thanks.mp3')
            return True

        except Exception as e:
            print(f"[DINOCHROME] Error critico: {e} (Queue ID: {queue_item.id})")
            import traceback
            traceback.print_exc()
            return False

    def _handle_rose(self, username, event_data, queue_item):
        """Rose gift: overlay + TTS correccion"""
        rose_start = time.time()

        # Enviar overlay de rosa al frontend
        send_dinochrome_event('rose_gift', {
            'username': username,
            'gift_name': 'Rose',
            'count': event_data.get('gift', {}).get('count', 1),
        })

        # Generar y enviar audio TTS
        try:
            correction_text = f"No es 'Rose' {username}, es 'Rosa'... ROSA!"
            audio_file = self.elevenlabs.text_to_speech_and_save(
                correction_text,
                voice_id="KHCvMklQZZo0O30ERnVn",
                play_audio=False,
                wait=False
            )
            if audio_file:
                self._send_tts_audio(audio_file)
                duration = self._get_audio_duration(audio_file)
                if duration > 0:
                    time.sleep(duration)
                total_time = time.time() - rose_start
                print(f"[DINOCHROME] Rose completado en {total_time:.1f}s")
        except Exception as e:
            print(f"[DINOCHROME] Error en correccion: {e}")

        return True

    def _handle_rosa(self, username, queue_item):
        """Rosa gift: LLM respuesta + TTS + restart juego"""
        rosa_start = time.time()

        # Sistema de prompts variados
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

        # PASO 1: Generar texto con LLM (re-instanciar para tomar config actualizada)
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
        try:
            audio_file = self.elevenlabs.text_to_speech_and_save(
                ai_response,
                voice_id="KHCvMklQZZo0O30ERnVn",
                play_audio=False,
                wait=False
            )

            # PASO 3: Reiniciar juego + enviar audio (todo via SSE)
            if audio_file:
                send_dinochrome_event('game_restart', {})
                self._send_tts_audio(audio_file)

                # Esperar a que el audio termine antes de procesar el siguiente evento
                duration = self._get_audio_duration(audio_file)
                if duration > 0:
                    print(f"[DINOCHROME] Esperando {duration:.1f}s a que termine el audio...")
                    time.sleep(duration)

                total_time = time.time() - rosa_start
                print(f"[DINOCHROME] Rosa completado en {total_time:.1f}s")
            else:
                send_dinochrome_event('game_restart', {})
        except Exception as e:
            print(f"[DINOCHROME] Error ElevenLabs: {e}")
            send_dinochrome_event('game_restart', {})
            return False

        return True

    def _send_dancing_gif(self, live_event):
        """Envia un GIF bailando a un slot disponible"""
        try:
            if not self.gif_slot_queue:
                self.gif_slot_queue = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

            slot = self.gif_slot_queue.pop(0)

            gif_index = self.gif_counter % len(AVAILABLE_GIFS)
            gif_filename = AVAILABLE_GIFS[gif_index]
            self.gif_counter += 1

            event_data = live_event.event_data
            username = live_event.user_nickname or live_event.user_unique_id or 'Anonimo'
            gift_name = event_data.get('gift', {}).get('name', 'Regalo')

            send_dinochrome_event('dancing_gif', {
                'username': username,
                'gift_name': gift_name,
                'gif_filename': gif_filename,
                'slot': slot,
            })

            print(f"[DINOCHROME] GIF: {gif_filename} -> Slot {slot} ({username})")

            def free_slot():
                time.sleep(60)
                if slot not in self.gif_slot_queue:
                    self.gif_slot_queue.append(slot)

            threading.Thread(target=free_slot, daemon=True).start()

        except Exception as e:
            print(f"[DINOCHROME] Error enviando GIF: {e}")
            import traceback
            traceback.print_exc()

    def _get_audio_duration(self, audio_file):
        """Calcula la duracion de un archivo MP3 en segundos"""
        try:
            import struct

            absolute_path = os.path.join(str(settings.MEDIA_ROOT), audio_file)
            file_size = os.path.getsize(absolute_path)

            # Estimacion para MP3: bitrate tipico de ElevenLabs es ~128kbps
            # duracion = tamaño_bytes / (bitrate_bps / 8)
            estimated_duration = file_size / (128000 / 8)
            return estimated_duration + 0.5  # Medio segundo extra de margen
        except Exception as e:
            print(f"[DINOCHROME] Error calculando duracion audio: {e}")
            return 3.0  # Fallback: 3 segundos

    def _send_tts_audio(self, audio_file):
        """Envia evento para que el browser reproduzca audio TTS"""
        # Construir URL relativa al media root
        if audio_file.startswith('/'):
            # Path absoluto: extraer parte relativa a MEDIA_ROOT
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

    def _process_comment(self, live_event, queue_item):
        return True

    def _process_like(self, live_event, queue_item):
        return True

    def _process_share(self, live_event, queue_item):
        return True

    def _process_follow(self, live_event, queue_item):
        return True

    def _process_subscribe(self, live_event, queue_item):
        return True
