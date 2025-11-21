"""
Views para overlays de DinoChrome
Sistema de overlays específico para el servicio DinoChrome
"""

from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.conf import settings
import json
import time
from pathlib import Path


# Directorio para eventos compartidos entre procesos
EVENTS_DIR = Path(settings.BASE_DIR) / 'tmp' / 'dinochrome_overlay_events'
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


def rose_overlay_view(request):
    """
    Overlay de rosa (mismo comportamiento que el overlay genérico)
    """
    return render(request, 'dinochrome_overlays/rose.html')


def gif_overlay_view(request, slot):
    """
    Overlay de GIF bailando para un slot específico (1-5)

    Args:
        slot: Número de slot (1-5)
    """
    if slot < 1 or slot > 5:
        slot = 1

    context = {
        'slot': slot,
    }
    return render(request, 'dinochrome_overlays/gif_slot.html', context)


def overlay_events(request, overlay_type):
    """
    Server-Sent Events endpoint para enviar eventos en tiempo real

    Args:
        overlay_type: Tipo de overlay ('rose' o 'gif-1', 'gif-2', etc.)
    """
    def event_stream():
        last_ping = time.time()
        processed_files = set()

        while True:
            try:
                # Buscar archivos de eventos nuevos
                event_files = sorted(EVENTS_DIR.glob('*.json'))

                for event_file in event_files:
                    if event_file.name not in processed_files:
                        try:
                            # Leer evento
                            with open(event_file, 'r') as f:
                                event_data = json.load(f)

                            # Verificar si este evento es para este overlay
                            event_overlay_type = event_data.get('overlay_type', '')

                            if event_overlay_type == overlay_type:
                                # Enviar al cliente
                                yield f"data: {json.dumps(event_data)}\n\n"

                                # Marcar como procesado
                                processed_files.add(event_file.name)

                                # Eliminar archivo después de enviarlo
                                event_file.unlink()

                        except (json.JSONDecodeError, FileNotFoundError):
                            # Archivo corrupto o ya eliminado, ignorar
                            processed_files.add(event_file.name)

                # Limpiar set de archivos procesados si crece mucho
                if len(processed_files) > 100:
                    processed_files.clear()

                # Esperar antes de verificar nuevos eventos
                time.sleep(0.1)

                # Keep-alive
                current_time = time.time()
                if current_time - last_ping > 15:
                    yield f": keep-alive\n\n"
                    last_ping = current_time

            except Exception as e:
                print(f"Error en event_stream: {e}")
                time.sleep(1)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def send_dinochrome_overlay_event(overlay_type, event_type, data):
    """
    Envía un evento a un overlay específico de DinoChrome

    Args:
        overlay_type: Tipo de overlay ('rose' o 'gif-1', 'gif-2', etc.)
        event_type: Tipo de evento ('rose_gift', 'dancing_gif')
        data: Datos del evento
    """
    try:
        timestamp = int(time.time() * 1000000)
        filename = f"{timestamp}_{overlay_type}_{event_type}.json"
        filepath = EVENTS_DIR / filename

        event = {
            'overlay_type': overlay_type,
            'type': event_type,
            'data': data,
            'timestamp': timestamp
        }

        with open(filepath, 'w') as f:
            json.dump(event, f)

    except Exception as e:
        print(f"Error escribiendo evento de overlay DinoChrome: {e}")
