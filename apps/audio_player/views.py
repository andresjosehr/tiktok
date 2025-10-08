"""
Views para el reproductor de audio web
"""

import os
import json
import time
from django.http import StreamingHttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
from .models import CurrentAudio


def player_page(request):
    """
    Página HTML con el reproductor de audio
    """
    return render(request, 'audio_player/player.html')


def set_audio(file_path, channel='voice'):
    """
    Función para establecer el audio actual desde los servicios

    Args:
        file_path (str): Ruta absoluta del archivo de audio
        channel (str): Canal de audio ('music' o 'voice')
    """
    CurrentAudio.set_current(file_path, channel=channel)


def get_current_audio(request):
    """
    Endpoint que devuelve los audios actuales de todos los canales
    """
    music = CurrentAudio.get_current(channel='music')
    voice = CurrentAudio.get_current(channel='voice')

    def get_audio_url(current_audio):
        if current_audio.file_path and os.path.exists(current_audio.file_path):
            media_root = settings.MEDIA_ROOT.rstrip('/')
            if current_audio.file_path.startswith(media_root):
                relative_path = current_audio.file_path[len(media_root):].lstrip('/')
                return {
                    'audio_url': f"{settings.MEDIA_URL}{relative_path}",
                    'timestamp': current_audio.timestamp,
                    'playing': current_audio.playing
                }
        return {
            'audio_url': None,
            'timestamp': None,
            'playing': False
        }

    return JsonResponse({
        'music': get_audio_url(music),
        'voice': get_audio_url(voice)
    })


def event_stream(request):
    """
    Server-Sent Events stream para notificar nuevo audio
    """
    def event_generator():
        last_timestamp = 0

        # Enviar mensaje inicial de conexión
        yield ": connected\n\n"

        while True:
            try:
                # Verificar si hay nuevo audio
                if current_audio['timestamp'] and current_audio['timestamp'] > last_timestamp:
                    if current_audio['file_path'] and os.path.exists(current_audio['file_path']):
                        relative_path = current_audio['file_path'].replace(settings.MEDIA_ROOT + '/', '')
                        audio_url = f"{settings.MEDIA_URL}{relative_path}"

                        data = json.dumps({
                            'audio_url': audio_url,
                            'timestamp': current_audio['timestamp']
                        })

                        yield f"data: {data}\n\n"
                        last_timestamp = current_audio['timestamp']

                time.sleep(0.5)  # Polling cada 500ms

                # Enviar keepalive cada 10 iteraciones (5 segundos)
                if int(time.time() * 2) % 10 == 0:
                    yield ": keepalive\n\n"

            except GeneratorExit:
                break

    response = StreamingHttpResponse(
        event_generator(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@require_http_methods(["POST"])
def stop_audio(request):
    """
    Endpoint para detener el audio actual
    """
    global current_audio
    current_audio['playing'] = False
    return JsonResponse({'status': 'stopped'})
