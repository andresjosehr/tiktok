"""
Cliente de YouTube para busqueda y descarga de audio usando yt-dlp
"""

import os
import yt_dlp
from django.conf import settings


class YouTubeClient:
    """Cliente para buscar y descargar audio desde YouTube"""

    def __init__(self):
        self.download_dir = os.path.join(settings.MEDIA_ROOT, 'music')
        os.makedirs(self.download_dir, exist_ok=True)

    def search_and_download(self, query, max_duration=300):
        """
        Busca una cancion en YouTube y descarga el audio

        Args:
            query (str): Termino de busqueda
            max_duration (int): Duracion maxima en segundos (default: 5 minutos)

        Returns:
            dict: Informacion del video descargado o None si falla
                {
                    'youtube_id': str,
                    'youtube_url': str,
                    'title': str,
                    'duration': int,
                    'file_path': str
                }
        """
        try:
            # Opciones de yt-dlp optimizadas para audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'match_filter': self._duration_filter(max_duration),
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Buscar en YouTube (primer resultado)
                print(f"[YOUTUBE] Buscando: {query}")
                search_url = f"ytsearch1:{query}"

                # Extraer informacion sin descargar
                info = ydl.extract_info(search_url, download=False)

                if not info or 'entries' not in info or len(info['entries']) == 0:
                    print(f"[YOUTUBE] No se encontraron resultados para: {query}")
                    return None

                # Obtener primer resultado
                video_info = info['entries'][0]

                # Verificar duracion
                duration = video_info.get('duration', 0)
                if duration > max_duration:
                    print(f"[YOUTUBE] Video muy largo: {duration}s > {max_duration}s")
                    return None

                # Descargar
                video_url = video_info['webpage_url']
                print(f"[YOUTUBE] Descargando: {video_info['title']}")

                download_info = ydl.extract_info(video_url, download=True)

                # Construir ruta del archivo
                video_id = download_info['id']
                file_path = os.path.join(self.download_dir, f"{video_id}.mp3")

                # Verificar que el archivo existe
                if not os.path.exists(file_path):
                    print(f"[YOUTUBE] Archivo no encontrado: {file_path}")
                    return None

                print(f"[YOUTUBE] Descarga exitosa: {file_path}")

                return {
                    'youtube_id': video_id,
                    'youtube_url': video_url,
                    'title': download_info['title'],
                    'duration': duration,
                    'file_path': file_path
                }

        except Exception as e:
            print(f"[YOUTUBE] Error: {str(e)}")
            return None

    def _duration_filter(self, max_duration):
        """Filtro para limitar duracion de videos"""
        def filter_func(info, *, incomplete):
            duration = info.get('duration')
            if duration and duration > max_duration:
                return f'Video muy largo: {duration}s > {max_duration}s'
        return filter_func

    def get_file_path(self, youtube_id):
        """Obtiene la ruta de un archivo ya descargado"""
        file_path = os.path.join(self.download_dir, f"{youtube_id}.mp3")
        return file_path if os.path.exists(file_path) else None

    def get_playlist_videos(self, playlist_url, max_videos=50):
        """
        Obtiene la lista de videos de una playlist de YouTube

        Args:
            playlist_url (str): URL de la playlist
            max_videos (int): Maximo de videos a obtener

        Returns:
            list: Lista de diccionarios con info de videos
                [{
                    'youtube_id': str,
                    'youtube_url': str,
                    'title': str,
                    'duration': int
                }]
        """
        try:
            ydl_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"[YOUTUBE] Extrayendo playlist...")
                playlist_info = ydl.extract_info(playlist_url, download=False)

                if not playlist_info or 'entries' not in playlist_info:
                    print(f"[YOUTUBE] No se pudo extraer playlist")
                    return []

                videos = []
                for entry in playlist_info['entries'][:max_videos]:
                    if entry:
                        videos.append({
                            'youtube_id': entry.get('id', ''),
                            'youtube_url': entry.get('url', ''),
                            'title': entry.get('title', 'Unknown'),
                            'duration': entry.get('duration', 0)
                        })

                print(f"[YOUTUBE] Playlist extraida: {len(videos)} videos")
                return videos

        except Exception as e:
            print(f"[YOUTUBE] Error extrayendo playlist: {str(e)}")
            return []

    def download_video(self, youtube_url, max_duration=600):
        """
        Descarga un video especifico por URL

        Args:
            youtube_url (str): URL del video
            max_duration (int): Duracion maxima

        Returns:
            dict: Info del video descargado o None
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)

                video_id = info['id']
                file_path = os.path.join(self.download_dir, f"{video_id}.mp3")

                if not os.path.exists(file_path):
                    return None

                return {
                    'youtube_id': video_id,
                    'youtube_url': youtube_url,
                    'title': info['title'],
                    'duration': info.get('duration', 0),
                    'file_path': file_path
                }

        except Exception as e:
            print(f"[YOUTUBE] Error descargando video: {str(e)}")
            return None

    def delete_file(self, file_path):
        """Elimina un archivo de audio"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[YOUTUBE] Archivo eliminado: {file_path}")
                return True
        except Exception as e:
            print(f"[YOUTUBE] Error eliminando archivo: {str(e)}")
        return False
