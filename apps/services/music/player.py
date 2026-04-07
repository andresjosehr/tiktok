"""
Manejador de reproduccion de audio para el servicio de musica
"""

import os
import sys
import subprocess
import threading
import shutil


class MusicPlayer:
    """
    Manejador de reproduccion de musica con control de interrupcion
    Usa VLC directamente para reproducir audio
    """

    def __init__(self):
        self.current_process = None
        self.current_song = None
        self.is_playing = False
        self.lock = threading.Lock()

    def play(self, file_path, on_finish_callback=None):
        """
        Reproduce audio usando VLC

        Args:
            file_path (str): Ruta absoluta del archivo
            on_finish_callback (callable): Funcion a ejecutar cuando termine

        Returns:
            bool: True si se inició correctamente
        """
        print(f"[PLAYER] ========== INICIO DE REPRODUCCION ==========")
        print(f"[PLAYER] Ruta recibida: {file_path}")
        print(f"[PLAYER] Tipo de ruta: {type(file_path)}")
        print(f"[PLAYER] Ruta en repr: {repr(file_path)}")
        print(f"[PLAYER] Sistema operativo: {sys.platform}")
        print(f"[PLAYER] Ruta normalizada (os.path.normpath): {os.path.normpath(file_path)}")

        # Verificar existencia
        exists = os.path.exists(file_path)
        print(f"[PLAYER] ¿Archivo existe?: {exists}")

        if exists:
            print(f"[PLAYER] Tamaño del archivo: {os.path.getsize(file_path)} bytes")
            print(f"[PLAYER] Ruta absoluta: {os.path.abspath(file_path)}")
        else:
            print(f"[PLAYER] ARCHIVO NO ENCONTRADO!")
            print(f"[PLAYER] Directorio padre: {os.path.dirname(file_path)}")
            print(f"[PLAYER] ¿Directorio existe?: {os.path.exists(os.path.dirname(file_path))}")
            if os.path.exists(os.path.dirname(file_path)):
                print(f"[PLAYER] Archivos en el directorio: {os.listdir(os.path.dirname(file_path))}")
            return False

        # Ubicación de VLC
        vlc_path = shutil.which('vlc')
        print(f"[PLAYER] VLC encontrado en: {vlc_path}")

        self.stop()

        with self.lock:
            try:
                # Reproducir con VLC en modo headless (sin interfaz)
                print(f"[PLAYER] Iniciando proceso VLC...")

                # Construir comando de VLC
                vlc_cmd = 'vlc'

                # En Windows, usar ruta completa si shutil.which() no lo encuentra
                if sys.platform == 'win32' and vlc_path is None:
                    vlc_cmd = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
                    print(f"[PLAYER] Usando ruta completa de VLC para Windows: {vlc_cmd}")

                process = subprocess.Popen(
                    [vlc_cmd, '--intf', 'dummy', '--play-and-exit', '--no-video', '--gain=0.1', file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                self.current_process = process
                self.current_song = file_path
                self.is_playing = True

                if on_finish_callback:
                    monitor_thread = threading.Thread(
                        target=self._monitor_playback,
                        args=(process, on_finish_callback),
                        daemon=True
                    )
                    monitor_thread.start()

                print(f"[PLAYER] Reproduciendo con VLC: {os.path.basename(file_path)}")
                print(f"[PLAYER] PID del proceso: {process.pid}")
                print(f"[PLAYER] ========== FIN DE INICIO DE REPRODUCCION ==========")
                return True

            except Exception as e:
                print(f"[PLAYER] Error reproduciendo audio: {str(e)}")
                print(f"[PLAYER] Tipo de error: {type(e).__name__}")
                import traceback
                print(f"[PLAYER] Traceback: {traceback.format_exc()}")
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
            process: Proceso de VLC
            on_finish_callback: Funcion a ejecutar cuando termine
        """
        try:
            # Esperar a que termine el proceso
            return_code = process.wait()

            with self.lock:
                # Verificar que este proceso sigue siendo el actual
                # (si se llamo stop() o play() con otra cancion, current_process cambio)
                is_current = self.current_process == process

                if is_current and self.is_playing:
                    # Termino naturalmente (no fue interrumpido por stop())
                    print(f"[PLAYER] Cancion terminada (return_code={return_code})")
                    self.is_playing = False
                    self.current_song = None
                    self.current_process = None

            # Ejecutar callback FUERA del lock para evitar deadlocks
            if is_current and on_finish_callback:
                on_finish_callback(interrupted=False)

        except Exception as e:
            print(f"[PLAYER] Error en monitor: {str(e)}")

    def get_current_song(self):
        """Retorna la ruta de la cancion actual"""
        with self.lock:
            return self.current_song if self.is_playing else None

    def is_currently_playing(self):
        """Verifica si hay algo reproduciendose"""
        with self.lock:
            return self.is_playing
