"""
Views para el sistema de overlays
"""

from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.conf import settings
import json
import time
import os
from pathlib import Path


# Directorio para eventos compartidos entre procesos
EVENTS_DIR = Path(settings.BASE_DIR) / 'tmp' / 'overlay_events'
EVENTS_DIR.mkdir(parents=True, exist_ok=True)


def overlay_view(request):
    """
    Vista principal del overlay para OBS Browser Source
    """
    return render(request, 'overlays/overlay.html')


def overlay_events(request):
    """
    Server-Sent Events (SSE) endpoint para enviar eventos en tiempo real
    Lee eventos desde archivos JSON compartidos entre procesos
    """
    def event_stream():
        # Enviar keep-alive cada 15 segundos
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
                # Log error pero continuar
                print(f"Error en event_stream: {e}")
                time.sleep(1)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def send_overlay_event(event_type, data):
    """
    Función helper para enviar eventos al overlay
    Escribe eventos en archivos JSON que serán leídos por el SSE endpoint

    Args:
        event_type: Tipo de evento (rose_gift, etc.)
        data: Datos del evento
    """
    try:
        # Crear nombre único basado en timestamp
        timestamp = int(time.time() * 1000000)  # microsegundos
        filename = f"{timestamp}_{event_type}.json"
        filepath = EVENTS_DIR / filename

        # Escribir evento
        event = {
            'type': event_type,
            'data': data,
            'timestamp': timestamp
        }

        with open(filepath, 'w') as f:
            json.dump(event, f)

    except Exception as e:
        print(f"Error escribiendo evento de overlay: {e}")
