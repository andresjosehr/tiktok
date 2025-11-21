"""
Overlays Service - Manejo de overlays visuales para streaming

Este servicio maneja eventos de TikTok y muestra overlays en OBS/streaming.
"""

import time
import logging
from apps.queue_system.base_service import BaseQueueService

logger = logging.getLogger('overlays')


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

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        pass

    def process_event(self, live_event, queue_item):
        """
        Procesa eventos de TikTok y muestra overlays

        Args:
            live_event: El evento de TikTok
            queue_item: Metadata de la cola

        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            event_type = live_event.event_type

            # Procesar según tipo de evento
            if event_type == 'GiftEvent':
                result = self._process_gift(live_event)

            elif event_type == 'CommentEvent':
                result = self._process_comment(live_event)

            elif event_type == 'LikeEvent':
                result = self._process_like(live_event)

            elif event_type == 'ShareEvent':
                result = self._process_share(live_event)

            elif event_type == 'FollowEvent':
                result = self._process_follow(live_event)

            elif event_type == 'JoinEvent':
                result = self._process_join(live_event)

            elif event_type == 'SubscribeEvent':
                result = self._process_subscribe(live_event)

            else:
                return False

            if result:
                self.events_processed += 1

            return result

        except Exception:
            return False

    def _process_gift(self, live_event):
        """Procesa evento de regalo"""
        try:
            # Obtener datos del regalo
            event_data = live_event.event_data
            gift_name = event_data.get('gift', {}).get('name', '')

            # Solo procesar rosas
            if gift_name.lower() in ['rose', 'rosa']:
                from .views import send_overlay_event

                # Preparar datos para el overlay
                overlay_data = {
                    'username': live_event.user_nickname or live_event.user_unique_id or 'Anónimo',
                    'gift_name': gift_name,
                    'count': event_data.get('gift', {}).get('count', 1),
                }

                # Enviar al overlay
                send_overlay_event('rose_gift', overlay_data)

                logger.info(f"Rosa enviada al overlay: {overlay_data['username']} x{overlay_data['count']}")

            time.sleep(1.2)
            return True

        except Exception as e:
            logger.error(f"Error procesando gift: {e}")
            return False

    def _process_comment(self, live_event):
        """Procesa evento de comentario"""
        time.sleep(0.4)
        return True

    def _process_like(self, live_event):
        """Procesa evento de like"""
        time.sleep(0.2)
        return True

    def _process_share(self, live_event):
        """Procesa evento de compartir"""
        time.sleep(0.5)
        return True

    def _process_follow(self, live_event):
        """Procesa evento de follow"""
        time.sleep(0.7)
        return True

    def _process_join(self, live_event):
        """Procesa evento de join"""
        time.sleep(0.3)
        return True

    def _process_subscribe(self, live_event):
        """Procesa evento de suscripción"""
        time.sleep(1.0)
        return True
