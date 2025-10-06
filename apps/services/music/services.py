"""
Music Service - Servicio de reproduccion de musica desde YouTube

Este servicio maneja:
- Asignacion de creditos por regalos
- Validacion de usuarios con creditos
- Busqueda y descarga de canciones
- Reproduccion con interrupcion inmediata
- Reproduccion automatica de playlist de fondo
"""

import random
import threading
import time
from django.db import transaction
from apps.queue_system.base_service import BaseQueueService
from apps.services.music.models import MusicCredit, MusicHistory
from apps.services.music.youtube_client import YouTubeClient
from apps.services.music.player import MusicPlayer
from apps.app_config.models import Config


class MusicService(BaseQueueService):
    """
    Servicio de musica con sistema de creditos

    Caracteristicas:
    - Usuarios ganan creditos enviando regalos especificos
    - Comandos !cancion <nombre> para buscar en YouTube
    - Reproduccion inmediata (interrumpe cancion actual)
    - Rachas cuentan como multiples creditos
    """

    # Configuracion hardcodeada
    GIFT_NAME = 'gg'  # Nombre del regalo que da creditos
    MAX_DURATION = 300  # Duracion maxima en segundos (5 minutos)
    DEFAULT_PLAYLIST = 'https://www.youtube.com/playlist?list=PLxZHtuv5hUL94eMtcOOV0BiZu6a4cRo4J'

    def __init__(self):
        self.youtube = YouTubeClient()
        self.player = MusicPlayer()
        self.current_session = None
        self.current_history_entry = None

        # Control de reproduccion automatica
        self.playlist_videos = []
        self.background_thread = None
        self.background_running = False
        self.user_request_active = False

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        print("[MUSIC] Servicio de musica iniciado")

        # Iniciar reproduccion automatica de fondo
        self._start_background_music()

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        print("[MUSIC] Deteniendo servicio de musica...")

        # Detener thread de fondo
        self.background_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)

        # Detener reproduccion actual
        if self.player.is_currently_playing():
            self.player.stop(interrupted=False)

        # Marcar cancion actual como finalizada
        if self.current_history_entry:
            self.current_history_entry.mark_finished(interrupted=False)

    def process_event(self, live_event, queue_item):
        """
        Procesa eventos de TikTok

        Args:
            live_event: Evento de TikTok
            queue_item: Item de la cola

        Returns:
            bool: True si se proceso exitosamente
        """
        try:
            # Guardar sesion actual
            self.current_session = live_event.session

            event_type = live_event.event_type

            # Procesar segun tipo
            if event_type == 'GiftEvent':
                return self._process_gift(live_event)

            elif event_type == 'CommentEvent':
                return self._process_comment(live_event)

            return False

        except Exception as e:
            print(f"[MUSIC] Error procesando evento: {str(e)}")
            return False

    def _process_gift(self, live_event):
        """
        Procesa regalos para asignar creditos

        Args:
            live_event: Evento de regalo

        Returns:
            bool: True si se asignaron creditos
        """
        try:
            event_data = live_event.event_data
            username = live_event.user_unique_id

            # Verificar si es el regalo correcto (GG)
            gift_name = event_data.get('gift', {}).get('name', '').lower()

            if self.GIFT_NAME.lower() not in gift_name:
                return True  # No es el regalo configurado, pero no es error

            # Determinar cantidad de creditos (por rachas)
            credit_count = 1

            # Si es una racha, contar todos los regalos
            if live_event.is_streaking:
                # Obtener cantidad de la racha
                gift_data = event_data.get('gift', {})
                repeat_count = event_data.get('repeatCount', 1)
                credit_count = repeat_count

            # Asignar creditos
            with transaction.atomic():
                credit, created = MusicCredit.objects.get_or_create(
                    session=live_event.session,
                    username=username
                )

                credit.add_gifts(credit_count)

                action = "Nuevos creditos" if created else "Creditos agregados"
                print(f"[MUSIC] {action}: {username} +{credit_count} "
                      f"(Total: {credit.credits_available}/{credit.total_gifts})")

            return True

        except Exception as e:
            print(f"[MUSIC] Error procesando regalo: {str(e)}")
            return False

    def _process_comment(self, live_event):
        """
        Procesa comentarios para detectar comandos de musica

        Args:
            live_event: Evento de comentario

        Returns:
            bool: True si se proceso el comando
        """
        try:
            comment = live_event.event_data.get('comment', '').strip()
            username = live_event.user_unique_id

            # Verificar si es comando de musica
            if not comment.lower().startswith('!cancion '):
                return True  # No es comando, pero no es error

            # Extraer query
            query = comment[9:].strip()  # Remover '!cancion '

            if not query:
                print(f"[MUSIC] Comando vacio de {username}")
                return False

            # Verificar creditos
            try:
                credit = MusicCredit.objects.get(
                    session=live_event.session,
                    username=username
                )
            except MusicCredit.DoesNotExist:
                print(f"[MUSIC] {username} sin creditos (no ha enviado regalos)")
                return False

            if credit.credits_available <= 0:
                print(f"[MUSIC] {username} sin creditos disponibles "
                      f"({credit.credits_used}/{credit.total_gifts} usados)")
                return False

            # Buscar y descargar cancion
            print(f"[MUSIC] Buscando: '{query}' (solicitado por {username})")

            video_info = self.youtube.search_and_download(query, self.MAX_DURATION)

            if not video_info:
                print(f"[MUSIC] No se pudo descargar: {query}")
                return False

            # Descontar credito
            with transaction.atomic():
                credit.use_credit()
                print(f"[MUSIC] Credito usado: {username} "
                      f"({credit.credits_available}/{credit.total_gifts} restantes)")

            # Registrar en historial
            history_entry = MusicHistory.objects.create(
                session=live_event.session,
                username=username,
                query=query,
                youtube_url=video_info['youtube_url'],
                youtube_id=video_info['youtube_id'],
                title=video_info['title'],
                duration=video_info['duration'],
                file_path=video_info['file_path']
            )

            # Marcar cancion actual como interrumpida si existe
            if self.current_history_entry and self.player.is_currently_playing():
                self.current_history_entry.mark_finished(interrupted=True)

            # Indicar que hay un request de usuario activo
            self.user_request_active = True

            # Reproducir cancion
            success = self.player.play(
                video_info['file_path'],
                on_finish_callback=lambda interrupted: self._on_song_finished(
                    history_entry,
                    interrupted
                )
            )

            if success:
                self.current_history_entry = history_entry
                print(f"[MUSIC] Reproduciendo: {video_info['title']}")
            else:
                print(f"[MUSIC] Error reproduciendo: {video_info['title']}")
                history_entry.mark_finished(interrupted=True)

            return success

        except Exception as e:
            print(f"[MUSIC] Error procesando comentario: {str(e)}")
            return False

    def _on_song_finished(self, history_entry, interrupted):
        """
        Callback cuando termina una cancion

        Args:
            history_entry: Entrada del historial
            interrupted: Si fue interrumpida o termino naturalmente
        """
        try:
            history_entry.mark_finished(interrupted=interrupted)

            if not interrupted:
                print(f"[MUSIC] Cancion terminada: {history_entry.title}")
                self.current_history_entry = None
                self.user_request_active = False  # Permitir musica de fondo

        except Exception as e:
            print(f"[MUSIC] Error en callback: {str(e)}")

    def _start_background_music(self):
        """Inicia el thread de reproduccion automatica de fondo"""
        print("[MUSIC] Iniciando reproduccion automatica de fondo...")

        # Extraer videos de la playlist
        self.playlist_videos = self.youtube.get_playlist_videos(self.DEFAULT_PLAYLIST)

        if not self.playlist_videos:
            print("[MUSIC] No se pudo cargar la playlist")
            return

        print(f"[MUSIC] Playlist cargada: {len(self.playlist_videos)} videos")

        # Iniciar thread
        self.background_running = True
        self.background_thread = threading.Thread(
            target=self._background_music_loop,
            daemon=True
        )
        self.background_thread.start()

    def _background_music_loop(self):
        """Loop del thread de reproduccion automatica"""
        print("[MUSIC] Thread de fondo iniciado")

        # Mezclar playlist
        random.shuffle(self.playlist_videos)
        current_index = 0

        while self.background_running:
            try:
                # Si hay un request de usuario, esperar
                if self.user_request_active or self.player.is_currently_playing():
                    time.sleep(2)
                    continue

                # Obtener siguiente video
                if current_index >= len(self.playlist_videos):
                    # Reiniciar playlist
                    random.shuffle(self.playlist_videos)
                    current_index = 0

                video = self.playlist_videos[current_index]
                current_index += 1

                print(f"[MUSIC] Reproduccion automatica: {video['title']}")

                # Verificar si ya esta descargado
                file_path = self.youtube.get_file_path(video['youtube_id'])

                if not file_path:
                    # Descargar video
                    video_url = f"https://www.youtube.com/watch?v={video['youtube_id']}"
                    video_info = self.youtube.download_video(video_url)

                    if not video_info:
                        print(f"[MUSIC] Error descargando video de fondo: {video['title']}")
                        continue

                    file_path = video_info['file_path']

                # Reproducir
                self.player.play(
                    file_path,
                    on_finish_callback=lambda interrupted: self._on_background_finished(interrupted)
                )

                # Esperar a que termine
                while self.player.is_currently_playing() and self.background_running:
                    time.sleep(1)

            except Exception as e:
                print(f"[MUSIC] Error en thread de fondo: {str(e)}")
                time.sleep(5)

        print("[MUSIC] Thread de fondo detenido")

    def _on_background_finished(self, interrupted):
        """Callback cuando termina una cancion de fondo"""
        if not interrupted:
            print("[MUSIC] Cancion de fondo terminada")

    def _get_config(self, key, default=''):
        """
        Obtiene configuracion del sistema

        Args:
            key: Clave de configuracion
            default: Valor por defecto

        Returns:
            str: Valor de configuracion
        """
        try:
            config = Config.objects.get(meta_key=key)
            return config.meta_value
        except Config.DoesNotExist:
            return default
