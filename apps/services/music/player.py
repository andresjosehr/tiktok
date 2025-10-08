"""
Manejador de reproduccion de audio para el servicio de musica
"""

import os
import subprocess
import threading


class MusicPlayer:
    """
    Manejador de reproduccion de musica con control de interrupcion
    """

    def __init__(self):
        self.current_process = None
        self.current_song = None
        self.is_playing = False
        self.lock = threading.Lock()

    def play(self, file_path, on_finish_callback=None):
        """
        Envía audio al reproductor web (navegador Windows)

        Args:
            file_path (str): Ruta absoluta del archivo
            on_finish_callback (callable): Funcion a ejecutar cuando termine

        Returns:
            bool: True si se envió correctamente
        """
        if not os.path.exists(file_path):
            print(f"[PLAYER] Archivo no encontrado: {file_path}")
            return False

        self.stop()

        with self.lock:
            try:
                from apps.audio_player.views import set_audio
                set_audio(file_path, channel='music')

                self.current_song = file_path
                self.is_playing = True

                if on_finish_callback:
                    monitor_thread = threading.Thread(
                        target=self._monitor_web_playback,
                        args=(file_path, on_finish_callback),
                        daemon=True
                    )
                    monitor_thread.start()

                return True

            except Exception as e:
                print(f"[PLAYER] Error enviando audio: {str(e)}")
                self.is_playing = False
                return False

    def stop(self, interrupted=True):
        """
        Detiene la reproduccion actual

        Args:
            interrupted (bool): Si fue interrumpida (True) o termino naturalmente (False)

        Returns:
            bool: True si habia algo reproduciendose
        """
        with self.lock:
            if self.current_process and self.is_playing:
                try:
                    status = "(interrumpida)" if interrupted else ""
                    print(f"[PLAYER] Deteniendo reproduccion {status}")
                    self.current_process.terminate()
                    self.current_process.wait(timeout=2)
                    self.current_process = None
                    self.current_song = None
                    self.is_playing = False
                    return True
                except Exception as e:
                    print(f"[PLAYER] Error deteniendo: {str(e)}")

            return False

    def _monitor_playback(self, process, on_finish_callback):
        """
        Monitorea el proceso de reproduccion y ejecuta callback al terminar

        Args:
            process: Proceso de paplay
            on_finish_callback: Funcion a ejecutar cuando termine
        """
        try:
            # Esperar a que termine el proceso
            return_code = process.wait()

            # Solo ejecutar callback si termino normalmente (no interrumpido)
            with self.lock:
                if return_code == 0 and self.is_playing:
                    print(f"[PLAYER] Cancion terminada")
                    self.is_playing = False
                    self.current_song = None
                    self.current_process = None

                    if on_finish_callback:
                        on_finish_callback(interrupted=False)

        except Exception as e:
            print(f"[PLAYER] Error en monitor: {str(e)}")

    def _monitor_web_playback(self, file_path, on_finish_callback):
        """
        Monitorea la reproducción web y ejecuta callback después de la duración del audio

        Args:
            file_path: Ruta del archivo de audio
            on_finish_callback: Función a ejecutar cuando termine
        """
        try:
            import time

            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
                capture_output=True,
                text=True
            )

            duration = 5
            if result.returncode == 0:
                try:
                    duration = float(result.stdout.strip())
                except:
                    pass

            time.sleep(duration)

            with self.lock:
                if self.is_playing and self.current_song == file_path:
                    self.is_playing = False
                    self.current_song = None

                    if on_finish_callback:
                        on_finish_callback(interrupted=False)

        except Exception as e:
            print(f"[PLAYER] Error en monitor web: {str(e)}")

    def get_current_song(self):
        """Retorna la ruta de la cancion actual"""
        with self.lock:
            return self.current_song if self.is_playing else None

    def is_currently_playing(self):
        """Verifica si hay algo reproduciendose"""
        with self.lock:
            return self.is_playing
