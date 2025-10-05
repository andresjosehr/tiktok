"""
DinoChrome Service - Controlador de Chrome para interacciones

Este servicio maneja eventos de TikTok y ejecuta acciones en Chrome/navegador.
Actualmente solo simula las acciones con timeouts y logs.
"""

import time
import logging
from apps.queue_system.base_service import BaseQueueService

# Configurar logger
logger = logging.getLogger('dinochrome')


class DinoChromeService(BaseQueueService):
    """
    Servicio que controla Chrome para interacciones con el navegador

    Características:
    - Procesa eventos de TikTok
    - Simula acciones en Chrome con timeouts
    - Modo SYNC (eventos se procesan secuencialmente)
    """

    def __init__(self):
        self.session_start = None

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        from datetime import datetime
        self.session_start = datetime.now()

        print("=" * 60)
        print("🦖 DinoChrome Service - INICIADO")
        print("=" * 60)
        print("📋 Configuración:")
        print("  • Modo: SYNC (secuencial)")
        print("  • Estado: Esperando eventos...")
        print("=" * 60)
        logger.info("DinoChrome Service iniciado")

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        from datetime import datetime
        if self.session_start:
            duration = datetime.now() - self.session_start
            print("\n" + "=" * 60)
            print("🦖 DinoChrome Service - DETENIDO")
            print("=" * 60)
            print(f"⏱️  Tiempo activo: {duration}")
            print("=" * 60)
        logger.info("DinoChrome Service detenido")

    def process_event(self, live_event, queue_item):
        """
        Procesa eventos de TikTok y ejecuta acciones en Chrome

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
            print(f"\n🦖 [DinoChrome] Procesando {event_type}")
            print(f"   👤 Usuario: {user}")
            print(f"   🎯 Prioridad: {queue_item.priority}")

            # Procesar según tipo de evento
            if event_type == 'GiftEvent':
                return self._process_gift(live_event)

            elif event_type == 'CommentEvent':
                return self._process_comment(live_event)

            elif event_type == 'LikeEvent':
                return self._process_like(live_event)

            elif event_type == 'ShareEvent':
                return self._process_share(live_event)

            elif event_type == 'FollowEvent':
                return self._process_follow(live_event)

            elif event_type == 'SubscribeEvent':
                return self._process_subscribe(live_event)

            else:
                logger.warning(f"Tipo de evento no manejado: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Error procesando evento: {e}")
            print(f"   ❌ Error: {e}")
            return False

    def _process_gift(self, live_event):
        """Procesa evento de regalo"""
        gift_data = live_event.event_data.get('gift', {})
        gift_name = gift_data.get('name', 'Unknown')
        diamonds = gift_data.get('diamond_count', 0)
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   🎁 Regalo: {gift_name} ({diamonds} diamantes)")
        print(f"   ⚙️  Acción Chrome: Mostrar animación de regalo")
        logger.info(f"Procesando regalo: {gift_name} ({diamonds} diamantes) de {user}")

        # Simular procesamiento con timeout
        time.sleep(0.8)

        print(f"   ✅ Regalo procesado")
        logger.info(f"Regalo procesado exitosamente: {gift_name} de {user}")
        return True

    def _process_comment(self, live_event):
        """Procesa evento de comentario"""
        comment = live_event.event_data.get('comment', '')
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   💬 Comentario: {comment[:50]}{'...' if len(comment) > 50 else ''}")
        print(f"   ⚙️  Acción Chrome: Mostrar comentario en overlay")
        logger.info(f"Procesando comentario de {user}: {comment[:100]}")

        # Simular procesamiento
        time.sleep(0.3)

        print(f"   ✅ Comentario procesado")
        logger.info(f"Comentario procesado exitosamente de {user}")
        return True

    def _process_like(self, live_event):
        """Procesa evento de like"""
        like_count = live_event.event_data.get('like_count', 1)
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   ❤️  Likes: {like_count}")
        print(f"   ⚙️  Acción Chrome: Actualizar contador de likes")
        logger.info(f"Procesando {like_count} like(s) de {user}")

        # Simular procesamiento
        time.sleep(0.2)

        print(f"   ✅ Like procesado")
        logger.debug(f"Like procesado exitosamente de {user}")
        return True

    def _process_share(self, live_event):
        """Procesa evento de compartir"""
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   📤 Compartido")
        print(f"   ⚙️  Acción Chrome: Mostrar notificación de share")
        logger.info(f"Procesando share de {user}")

        # Simular procesamiento
        time.sleep(0.5)

        print(f"   ✅ Share procesado")
        logger.info(f"Share procesado exitosamente de {user}")
        return True

    def _process_follow(self, live_event):
        """Procesa evento de follow"""
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   👤 Nuevo seguidor")
        print(f"   ⚙️  Acción Chrome: Mostrar animación de follow")
        logger.info(f"Procesando follow de {user}")

        # Simular procesamiento
        time.sleep(0.6)

        print(f"   ✅ Follow procesado")
        logger.info(f"Follow procesado exitosamente de {user}")
        return True

    def _process_subscribe(self, live_event):
        """Procesa evento de suscripción"""
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   ⭐ Nueva suscripción")
        print(f"   ⚙️  Acción Chrome: Mostrar animación de suscripción")
        logger.info(f"Procesando suscripción de {user}")

        # Simular procesamiento
        time.sleep(0.7)

        print(f"   ✅ Suscripción procesada")
        logger.info(f"Suscripción procesada exitosamente de {user}")
        return True
