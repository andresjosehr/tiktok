"""
Views para DinoChrome unificado
SSE endpoint unico para todos los eventos (patron Tug of War)
"""

from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.conf import settings
import json
import time
from pathlib import Path


# Directorio para eventos compartidos entre procesos
EVENTS_DIR = Path(settings.BASE_DIR) / 'tmp' / 'dinochrome_events'
EVENTS_DIR.mkdir(parents=True, exist_ok=True)

# Lista de GIFs disponibles (en orden de secuencia)
AVAILABLE_GIFS = [
    'cat-dancing.gif',
    'catgroove7tv-catgroove.gif',
    'cute-pug.gif',
    'dancing-dancing-dino.gif',
    'dog-dance.gif',
    'dog-dancing.gif',
    'doge.gif',
    'gianbortion-cat.gif',
    'gorrila-dancing.gif',
    'monkey-dance.gif',
]


def dinochrome_view(request):
    """Vista unificada: juego + overlays + audio en una sola pagina"""
    context = {
        'available_gifs_json': json.dumps(AVAILABLE_GIFS),
    }
    return render(request, 'dinochrome/index.html', context)


def dinochrome_current_music(request):
    """Retorna la cancion actual del music service (para browsers que se conectan tarde)"""
    from django.http import JsonResponse
    try:
        from apps.services.music.player import MusicPlayer
        from apps.queue_system.models import Service
        from apps.queue_system.worker import ServiceWorker

        # Buscar el worker activo de music y obtener la cancion actual
        # Como no tenemos acceso directo al worker, re-enviamos desde el player
        # Truco: guardar la ultima cancion enviada en un archivo
        last_music_file = Path(settings.BASE_DIR) / 'tmp' / 'dinochrome_last_music.json'
        if last_music_file.exists():
            with open(last_music_file, 'r') as f:
                data = json.load(f)
            return JsonResponse(data)
    except Exception:
        pass
    return JsonResponse({'audio_url': None})


def dinochrome_events(request):
    """SSE endpoint unico para todos los eventos de DinoChrome"""
    def event_stream():
        last_ping = time.time()
        processed_files = set()

        while True:
            try:
                event_files = sorted(EVENTS_DIR.glob('*.json'))

                for event_file in event_files:
                    if event_file.name not in processed_files:
                        try:
                            with open(event_file, 'r') as f:
                                event_data = json.load(f)

                            yield f"data: {json.dumps(event_data)}\n\n"
                            processed_files.add(event_file.name)
                            event_file.unlink()

                        except (json.JSONDecodeError, FileNotFoundError):
                            processed_files.add(event_file.name)

                if len(processed_files) > 100:
                    processed_files.clear()

                time.sleep(0.1)

                current_time = time.time()
                if current_time - last_ping > 15:
                    yield ": keep-alive\n\n"
                    last_ping = current_time

            except Exception as e:
                print(f"[DINOCHROME] Error en event_stream: {e}")
                time.sleep(1)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def send_dinochrome_event(event_type, data):
    """
    Envia un evento al frontend de DinoChrome via SSE

    Args:
        event_type: 'rose_gift' | 'dancing_gif' | 'game_restart' | 'tts_audio'
        data: dict con los datos del evento
    """
    try:
        timestamp = int(time.time() * 1000000)
        filename = f"{timestamp}_{event_type}.json"
        filepath = EVENTS_DIR / filename

        event = {
            'type': event_type,
            'data': data,
            'timestamp': timestamp
        }

        with open(filepath, 'w') as f:
            json.dump(event, f)

    except Exception as e:
        print(f"[DINOCHROME] Error escribiendo evento: {e}")
