"""
DinoChrome Service - Controlador de Chrome para interacciones

Este servicio maneja eventos de TikTok y ejecuta acciones en Chrome/navegador.
Actualmente solo simula las acciones con timeouts y logs.
"""

import logging
from apps.queue_system.base_service import BaseQueueService
from apps.services.chrome.ChromeService import ChromeService

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
        self.chrome = ChromeService()

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

        # Inicializar navegador Chrome con DinoChrome
        if self.chrome.initialize_browser(headless=False):
            logger.info("✅ Navegador Chrome inicializado con DinoChrome")
        else:
            logger.warning("⚠️  No se pudo inicializar el navegador Chrome")

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        from datetime import datetime

        # Cerrar navegador Chrome
        self.chrome.close()

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
            logger.info(f"[INICIO] Procesando {event_type} de {user} (Prioridad: {queue_item.priority}, Queue ID: {queue_item.id})")

            # Procesar según tipo de evento
            if event_type == 'GiftEvent':
                return self._process_gift(live_event, queue_item)

            elif event_type == 'CommentEvent':
                return self._process_comment(live_event, queue_item)

            elif event_type == 'LikeEvent':
                return self._process_like(live_event, queue_item)

            elif event_type == 'ShareEvent':
                return self._process_share(live_event, queue_item)

            elif event_type == 'FollowEvent':
                return self._process_follow(live_event, queue_item)

            elif event_type == 'SubscribeEvent':
                return self._process_subscribe(live_event, queue_item)

            else:
                logger.warning(f"Tipo de evento no manejado: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Error procesando evento {event_type} de {user}: {e}", exc_info=True)
            print(f"   ❌ Error: {e}")
            return False

    def _process_gift(self, live_event, queue_item):
        """Procesa evento de regalo"""
        gift_data = live_event.event_data.get('gift', {})
        gift_name = gift_data.get('name', 'Unknown')
        gift_id = gift_data.get('id', 'Unknown')
        diamonds = gift_data.get('diamond_count', 0)
        repeat_count = live_event.event_data.get('repeat_count', 1)
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   🎁 Regalo: {gift_name} x{repeat_count} ({diamonds} diamantes)")
        logger.info(f"[GIFT] Usuario: {user} | Regalo: {gift_name} (ID:{gift_id}) | Cantidad: x{repeat_count} | Diamantes: {diamonds} | Queue: {queue_item.id}")

        print(f"   ✅ Regalo procesado")
        logger.info(f"[GIFT] ✅ Regalo procesado: {gift_name} de {user}")
        return True

    def _process_comment(self, live_event, queue_item):
        """Procesa evento de comentario"""
        comment = live_event.event_data.get('comment', '')
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   💬 Comentario: {comment[:50]}{'...' if len(comment) > 50 else ''}")
        logger.info(f"[COMMENT] Usuario: {user} | Mensaje: '{comment}' | Queue: {queue_item.id}")

        print(f"   ✅ Comentario procesado")
        logger.info(f"[COMMENT] ✅ Comentario procesado de {user}")
        return True

    def _process_like(self, live_event, queue_item):
        """Procesa evento de like"""
        like_count = live_event.event_data.get('like_count', 1)
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   ❤️  Likes: {like_count}")
        logger.info(f"[LIKE] Usuario: {user} | Cantidad: {like_count} likes | Queue: {queue_item.id}")

        print(f"   ✅ Like procesado")
        logger.info(f"[LIKE] ✅ Like procesado de {user}")
        return True

    def _process_share(self, live_event, queue_item):
        """Procesa evento de compartir"""
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   📤 Compartido")
        logger.info(f"[SHARE] Usuario: {user} compartió el live | Queue: {queue_item.id}")

        print(f"   ✅ Share procesado")
        logger.info(f"[SHARE] ✅ Share procesado de {user}")
        return True

    def _process_follow(self, live_event, queue_item):
        """Procesa evento de follow"""
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   👤 Nuevo seguidor")
        logger.info(f"[FOLLOW] Nuevo seguidor: {user} | Queue: {queue_item.id}")

        print(f"   ✅ Follow procesado")
        logger.info(f"[FOLLOW] ✅ Follow procesado de {user}")
        return True

    def _process_subscribe(self, live_event, queue_item):
        """Procesa evento de suscripción"""
        user = live_event.user_nickname or live_event.user_unique_id

        print(f"   ⭐ Nueva suscripción")
        logger.info(f"[SUBSCRIBE] Nueva suscripción de: {user} | Queue: {queue_item.id}")

        print(f"   ✅ Suscripción procesada")
        logger.info(f"[SUBSCRIBE] ✅ Suscripción procesada de {user}")
        return True
