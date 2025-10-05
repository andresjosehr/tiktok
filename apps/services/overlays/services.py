"""
Overlays Service - Manejo de overlays visuales para streaming

Este servicio maneja eventos de TikTok y muestra overlays en OBS/streaming.
Actualmente solo simula las acciones con timeouts y logs.
"""

import time
import logging
from apps.queue_system.base_service import BaseQueueService

# Configurar logger
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

        print("=" * 60)
        print("🎨 Overlays Service - INICIADO")
        print("=" * 60)
        print("📋 Configuración:")
        print("  • Modo: ASYNC (paralelo)")
        print("  • Estado: Esperando eventos...")
        print("=" * 60)
        logger.info("Overlays Service iniciado")

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        from datetime import datetime
        if self.session_start:
            duration = datetime.now() - self.session_start
            print("\n" + "=" * 60)
            print("🎨 Overlays Service - DETENIDO")
            print("=" * 60)
            print(f"⏱️  Tiempo activo: {duration}")
            print(f"📊 Eventos procesados: {self.events_processed}")
            print("=" * 60)
        logger.info("Overlays Service detenido")

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
            user = live_event.user_nickname or live_event.user_unique_id

            # Log del evento recibido
            print(f"\n🎨 [Overlays] Procesando {event_type}")
            print(f"   👤 Usuario: {user}")
            print(f"   🎯 Prioridad: {queue_item.priority}")
            print(f"   ⚡ Modo: ASYNC")

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
                logger.warning(f"Tipo de evento no manejado: {event_type}")
                return False

            if result:
                self.events_processed += 1

            return result

        except Exception as e:
            logger.error(f"Error procesando evento: {e}")
            print(f"   ❌ Error: {e}")
            return False

    def _process_gift(self, live_event):
        """Procesa evento de regalo"""
        gift_data = live_event.event_data.get('gift', {})
        gift_name = gift_data.get('name', 'Unknown')
        diamonds = gift_data.get('diamond_count', 0)
        repeat_count = live_event.event_data.get('repeat_count', 1)

        print(f"   🎁 Regalo: {gift_name} x{repeat_count}")
        print(f"   💎 Diamantes: {diamonds}")
        print(f"   🎬 Acción: Mostrar animación de regalo en overlay")

        # Simular procesamiento (más largo para regalos)
        time.sleep(1.2)

        print(f"   ✅ Overlay de regalo mostrado")
        logger.info(f"Gift overlay: {gift_name} de {live_event.user_nickname}")
        return True

    def _process_comment(self, live_event):
        """Procesa evento de comentario"""
        comment = live_event.event_data.get('comment', '')

        print(f"   💬 Comentario: {comment[:50]}{'...' if len(comment) > 50 else ''}")
        print(f"   🎬 Acción: Mostrar comentario flotante en overlay")

        # Simular procesamiento
        time.sleep(0.4)

        print(f"   ✅ Comentario mostrado")
        logger.info(f"Comment overlay de {live_event.user_nickname}")
        return True

    def _process_like(self, live_event):
        """Procesa evento de like"""
        like_count = live_event.event_data.get('like_count', 1)

        print(f"   ❤️  Likes: {like_count}")
        print(f"   🎬 Acción: Animación de corazones en overlay")

        # Simular procesamiento (rápido)
        time.sleep(0.2)

        print(f"   ✅ Animación de like mostrada")
        logger.info(f"Like overlay de {live_event.user_nickname}")
        return True

    def _process_share(self, live_event):
        """Procesa evento de compartir"""
        print(f"   📤 Compartido")
        print(f"   🎬 Acción: Banner de agradecimiento por share")

        # Simular procesamiento
        time.sleep(0.5)

        print(f"   ✅ Banner de share mostrado")
        logger.info(f"Share overlay de {live_event.user_nickname}")
        return True

    def _process_follow(self, live_event):
        """Procesa evento de follow"""
        print(f"   👤 Nuevo seguidor")
        print(f"   🎬 Acción: Alerta de nuevo seguidor en overlay")

        # Simular procesamiento
        time.sleep(0.7)

        print(f"   ✅ Alerta de follow mostrada")
        logger.info(f"Follow overlay de {live_event.user_nickname}")
        return True

    def _process_join(self, live_event):
        """Procesa evento de join"""
        print(f"   🚪 Usuario se unió")
        print(f"   🎬 Acción: Mensaje de bienvenida en overlay")

        # Simular procesamiento (rápido)
        time.sleep(0.3)

        print(f"   ✅ Mensaje de bienvenida mostrado")
        logger.info(f"Join overlay de {live_event.user_nickname}")
        return True

    def _process_subscribe(self, live_event):
        """Procesa evento de suscripción"""
        print(f"   ⭐ Nueva suscripción")
        print(f"   🎬 Acción: Overlay especial de suscripción")

        # Simular procesamiento (importante, tarda más)
        time.sleep(1.0)

        print(f"   ✅ Overlay de suscripción mostrado")
        logger.info(f"Subscribe overlay de {live_event.user_nickname}")
        return True
