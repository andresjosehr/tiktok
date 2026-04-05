from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.conf import settings
import json
import time
from pathlib import Path


EVENTS_DIR = Path(settings.BASE_DIR) / 'tmp' / 'tugofwar_events'
EVENTS_DIR.mkdir(parents=True, exist_ok=True)


def game_view(request):
    return render(request, 'tugofwar/index.html')


def game_events(request):
    """SSE endpoint for real-time donation events from TugOfWarService"""
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
                print(f"[TUGOFWAR] Error en event_stream: {e}")
                time.sleep(1)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def send_tugofwar_event(event_type, data):
    """
    Envia un evento al frontend del Tug of War via SSE

    Args:
        event_type: 'donation' | 'reset' | etc.
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
        print(f"[TUGOFWAR] Error escribiendo evento: {e}")
