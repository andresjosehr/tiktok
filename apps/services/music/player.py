"""
Manejador de reproduccion de audio para el servicio de musica
Envia audio al browser de DinoChrome via SSE (sin VLC)
"""

import os
import threading
import time

from django.conf import settings


class MusicPlayer:
    """
    Reproduce musica enviando URLs al browser via SSE.
    El browser se encarga de la reproduccion real.
    """

    def __init__(self):
        self.current_song = None
        self.is_playing = False
        self.lock = threading.Lock()
        self._finish_callback = None
        self._duration_thread = None

    def play(self, file_path, on_finish_callback=None):
        """
        Envia cancion al browser via SSE

        Args:
            file_path (str): Ruta absoluta del archivo MP3
            on_finish_callback (callable): Funcion a ejecutar cuando termine

        Returns:
            bool: True si se envio correctamente
        """
        if not os.path.exists(file_path):
            print(f"[PLAYER] Archivo no encontrado: {file_path}")
            return False

        self.stop()

        with self.lock:
            try:
                # Construir URL relativa para el browser
                media_root = str(settings.MEDIA_ROOT)
                if file_path.startswith(media_root):
                    relative_path = file_path[len(media_root):].lstrip('/')
                else:
                    relative_path = os.path.basename(file_path)

                audio_url = settings.MEDIA_URL + relative_path

                # Enviar evento SSE al browser
                from apps.services.dinochrome.overlays.views import send_dinochrome_event
                music_data = {
                    'audio_url': audio_url,
                    'filename': os.path.basename(file_path),
                }
                send_dinochrome_event('music_play', music_data)

                # Guardar para browsers que se conecten tarde
                self._save_last_music(music_data)

                self.current_song = file_path
                self.is_playing = True
                self._finish_callback = on_finish_callback

                # Estimar duracion y programar callback
                duration = self._estimate_duration(file_path)
                print(f"[PLAYER] Enviado al browser: {os.path.basename(file_path)} (~{duration:.0f}s)")

                if on_finish_callback:
                    self._duration_thread = threading.Thread(
                        target=self._wait_and_finish,
                        args=(duration, file_path, on_finish_callback),
                        daemon=True
                    )
                    self._duration_thread.start()

                return True

            except Exception as e:
                print(f"[PLAYER] Error: {e}")
                self.is_playing = False
                return False

    def stop(self, interrupted=True):
        """Detiene la reproduccion actual"""
        with self.lock:
            if self.is_playing:
                try:
                    from apps.services.dinochrome.overlays.views import send_dinochrome_event
                    send_dinochrome_event('music_stop', {})
                except Exception:
                    pass

                self.current_song = None
                self.is_playing = False
                self._finish_callback = None
                return True
            return False

    def _wait_and_finish(self, duration, file_path, callback):
        """Espera la duracion estimada y ejecuta callback"""
        time.sleep(duration)

        with self.lock:
            # Verificar que sigue siendo la misma cancion
            if self.current_song == file_path and self.is_playing:
                self.is_playing = False
                self.current_song = None

                should_callback = True
            else:
                should_callback = False

        if should_callback:
            callback(interrupted=False)

    def _estimate_duration(self, file_path):
        """Estima duracion de un MP3 en segundos"""
        try:
            file_size = os.path.getsize(file_path)
            # MP3 tipico: ~192kbps
            return file_size / (192000 / 8)
        except Exception:
            return 180  # Fallback: 3 minutos

    def _save_last_music(self, data):
        """Guarda la ultima cancion para browsers que se conecten tarde"""
        try:
            import json
            from pathlib import Path
            from django.conf import settings as s
            last_file = Path(s.BASE_DIR) / 'tmp' / 'dinochrome_last_music.json'
            last_file.parent.mkdir(parents=True, exist_ok=True)
            with open(last_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def get_current_song(self):
        with self.lock:
            return self.current_song if self.is_playing else None

    def is_currently_playing(self):
        with self.lock:
            return self.is_playing
