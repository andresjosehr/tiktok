"""
Overlays Service - Manejo de overlays visuales para streaming

Este servicio maneja eventos de TikTok y muestra overlays en OBS/streaming.
"""

import time
from apps.queue_system.base_service import BaseQueueService


class OverlaysService(BaseQueueService):
    """
    Servicio que maneja overlays visuales en OBS/streaming

    Características:
    - Procesa eventos de TikTok
    - Simula overlays con timeouts
    - Modo ASYNC (eventos se procesan en paralelo)
    """

    def __init__(self):
        self.session_start = None
        self.events_processed = 0

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        from datetime import datetime
        self.session_start = datetime.now()
        print(f"[OVERLAYS] 🚀 Servicio iniciado")

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        print(f"[OVERLAYS] ⏹️  Servicio detenido | Total eventos: {self.events_processed}")

    def process_event(self, live_event, queue_item):
        """
        Procesa eventos de TikTok y muestra overlays

        Args:
            live_event: El evento de TikTok
            queue_item: Metadata de la cola

        Returns:
            bool: True si se procesó exitosamente
        """
        start_time = time.time()
        event_type = live_event.event_type
        username = live_event.user_nickname or live_event.user_unique_id or 'Anónimo'

        try:
            # Procesar según tipo de evento
            if event_type == 'GiftEvent':
                result = self._process_gift(live_event, queue_item)

            elif event_type == 'CommentEvent':
                result = self._process_comment(live_event, queue_item)

            elif event_type == 'LikeEvent':
                result = self._process_like(live_event, queue_item)

            elif event_type == 'ShareEvent':
                result = self._process_share(live_event, queue_item)

            elif event_type == 'FollowEvent':
                result = self._process_follow(live_event, queue_item)

            elif event_type == 'JoinEvent':
                result = self._process_join(live_event, queue_item)

            elif event_type == 'SubscribeEvent':
                result = self._process_subscribe(live_event, queue_item)

            else:
                print(f"[OVERLAYS] ⚠️  Evento desconocido: {event_type}")
                return False

            elapsed = (time.time() - start_time) * 1000
            if result:
                self.events_processed += 1

            return result

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            print(f"[OVERLAYS] ❌ Error procesando {event_type} de @{username}: {e} ({elapsed:.0f}ms)")
            return False

    def _process_gift(self, live_event, queue_item):
        """Procesa evento de regalo"""
        start_time = time.time()
        event_data = live_event.event_data
        gift_name = event_data.get('gift', {}).get('name', 'Unknown')
        gift_count = event_data.get('gift', {}).get('count', 1)
        username = live_event.user_nickname or live_event.user_unique_id or 'Anónimo'

        try:
            # Solo procesar rosas para overlay especial
            if gift_name.lower() in ['rose', 'rosa']:
                from .views import send_overlay_event

                overlay_data = {
                    'username': username,
                    'gift_name': gift_name,
                    'count': gift_count,
                }

                send_overlay_event('rose_gift', overlay_data)
                elapsed = (time.time() - start_time) * 1000
                print(f"[OVERLAYS] 🌹 Rosa de @{username} x{gift_count} → Overlay enviado ({elapsed:.0f}ms)")
            else:
                elapsed = (time.time() - start_time) * 1000
                print(f"[OVERLAYS] 🎁 Gift[{gift_name}] de @{username} x{gift_count} (P:{queue_item.priority}) ({elapsed:.0f}ms)")

            time.sleep(1.2)
            return True

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            print(f"[OVERLAYS] ❌ Error gift: {e} ({elapsed:.0f}ms)")
            return False

    def _process_comment(self, live_event, queue_item):
        """Procesa evento de comentario"""
        start_time = time.time()
        username = live_event.user_nickname or 'Anónimo'
        comment = live_event.event_data.get('comment', '')[:50]

        time.sleep(0.4)
        elapsed = (time.time() - start_time) * 1000
        print(f"[OVERLAYS] 💬 Comment de @{username}: '{comment}' (P:{queue_item.priority}) ({elapsed:.0f}ms)")
        return True

    def _process_like(self, live_event, queue_item):
        """Procesa evento de like"""
        start_time = time.time()
        username = live_event.user_nickname or 'Anónimo'
        like_count = live_event.event_data.get('likeCount', 1)

        time.sleep(0.2)
        elapsed = (time.time() - start_time) * 1000
        print(f"[OVERLAYS] ❤️  Like de @{username} x{like_count} (P:{queue_item.priority}) ({elapsed:.0f}ms)")
        return True

    def _process_share(self, live_event, queue_item):
        """Procesa evento de compartir"""
        start_time = time.time()
        username = live_event.user_nickname or 'Anónimo'

        time.sleep(0.5)
        elapsed = (time.time() - start_time) * 1000
        print(f"[OVERLAYS] 🔄 Share de @{username} (P:{queue_item.priority}) ({elapsed:.0f}ms)")
        return True

    def _process_follow(self, live_event, queue_item):
        """Procesa evento de follow"""
        start_time = time.time()
        username = live_event.user_nickname or 'Anónimo'

        time.sleep(0.7)
        elapsed = (time.time() - start_time) * 1000
        print(f"[OVERLAYS] ➕ Follow de @{username} (P:{queue_item.priority}) ({elapsed:.0f}ms)")
        return True

    def _process_join(self, live_event, queue_item):
        """Procesa evento de join"""
        start_time = time.time()
        username = live_event.user_nickname or 'Anónimo'

        time.sleep(0.3)
        elapsed = (time.time() - start_time) * 1000
        print(f"[OVERLAYS] 👋 Join de @{username} (P:{queue_item.priority}) ({elapsed:.0f}ms)")
        return True

    def _process_subscribe(self, live_event, queue_item):
        """Procesa evento de suscripción"""
        start_time = time.time()
        username = live_event.user_nickname or 'Anónimo'

        time.sleep(1.0)
        elapsed = (time.time() - start_time) * 1000
        print(f"[OVERLAYS] ⭐ Subscribe de @{username} (P:{queue_item.priority}) ({elapsed:.0f}ms)")
        return True
