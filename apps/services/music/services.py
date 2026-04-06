"""
Music Service - Servicio de reproduccion de musica desde archivos locales

Este servicio maneja:
- Reproduccion secuencial de MP3s desde media/music/
- Gift "gg" salta a la siguiente cancion
- Reproduccion automatica continua como musica de fondo
"""

import os
import random
import threading
import time

from django.conf import settings
from apps.queue_system.base_service import BaseQueueService
from apps.services.music.player import MusicPlayer


class MusicService(BaseQueueService):
    """
    Servicio de musica con reproduccion secuencial de MP3s locales.

    - Reproduce canciones en orden desde media/music/
    - Gift "gg" salta a la siguiente cancion
    - Cuando termina la lista, la baraja y empieza de nuevo
    """

    GIFT_NAME = 'gg'
    MUSIC_DIR = os.path.join(settings.MEDIA_ROOT, 'music')

    def __init__(self):
        self.player = MusicPlayer()
        self.tracks = []
        self.current_index = 0
        self.background_thread = None
        self.background_running = False

    def _load_tracks(self):
        """Carga todos los MP3 del directorio de musica"""
        self.tracks = []

        if not os.path.exists(self.MUSIC_DIR):
            os.makedirs(self.MUSIC_DIR, exist_ok=True)
            print(f"[MUSIC] Directorio creado: {self.MUSIC_DIR}")
            return

        for root, dirs, files in os.walk(self.MUSIC_DIR):
            for f in files:
                if f.lower().endswith('.mp3'):
                    self.tracks.append(os.path.join(root, f))

        self.tracks.sort()
        random.shuffle(self.tracks)
        self.current_index = 0
        print(f"[MUSIC] {len(self.tracks)} tracks cargados desde {self.MUSIC_DIR}")

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        print("[MUSIC] Servicio de musica iniciado")
        self._load_tracks()

        if self.tracks:
            self._start_background_music()
        else:
            print("[MUSIC] No hay tracks en media/music/ - servicio en espera")

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        print("[MUSIC] Deteniendo servicio de musica...")
        self.background_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        if self.player.is_currently_playing():
            self.player.stop(interrupted=False)

    def process_event(self, live_event, queue_item):
        """Procesa eventos de TikTok"""
        try:
            if live_event.event_type == 'GiftEvent':
                return self._process_gift(live_event)
            return True
        except Exception as e:
            print(f"[MUSIC] Error procesando evento: {str(e)}")
            return False

    def _process_gift(self, live_event):
        """Gift GG = saltar a la siguiente cancion"""
        event_data = live_event.event_data
        gift_name = event_data.get('gift', {}).get('name', '').lower()

        if self.GIFT_NAME.lower() not in gift_name:
            return True

        nickname = live_event.user_nickname or live_event.user_unique_id
        print(f"[MUSIC] ⏭️ @{nickname} envio GG - saltando cancion")

        self._play_next()
        return True

    def _play_next(self):
        """Reproduce la siguiente cancion de la lista"""
        if not self.tracks:
            return

        # Si llegamos al final, barajar y reiniciar
        if self.current_index >= len(self.tracks):
            random.shuffle(self.tracks)
            self.current_index = 0
            print("[MUSIC] Playlist reiniciada y barajada")

        track_path = self.tracks[self.current_index]
        self.current_index += 1

        filename = os.path.basename(track_path)
        print(f"[MUSIC] ▶️ [{self.current_index}/{len(self.tracks)}] {filename}")

        self.player.play(
            track_path,
            on_finish_callback=lambda interrupted: self._on_song_finished(interrupted)
        )

    def _on_song_finished(self, interrupted):
        """Callback cuando termina una cancion"""
        if not interrupted and self.background_running:
            self._play_next()

    def _start_background_music(self):
        """Inicia reproduccion automatica de fondo"""
        self.background_running = True
        self.background_thread = threading.Thread(
            target=self._background_music_loop,
            daemon=True
        )
        self.background_thread.start()

    def _background_music_loop(self):
        """Loop inicial que arranca la primera cancion"""
        print("[MUSIC] Reproduccion automatica iniciada")
        # Esperar un momento antes de empezar
        time.sleep(2)

        if self.background_running and not self.player.is_currently_playing():
            self._play_next()
