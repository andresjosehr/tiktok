"""
DinoChrome Service - Controlador de Chrome para interacciones

Este servicio maneja eventos de TikTok y ejecuta acciones en Chrome/navegador.
Actualmente solo simula las acciones con timeouts y logs.
"""

from apps.queue_system.base_service import BaseQueueService
from apps.services.dinochrome.ChromeService import ChromeService
from apps.integrations.elevenlabs.client import ElevenLabsClient


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
        self.elevenlabs = ElevenLabsClient()

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        from datetime import datetime
        self.session_start = datetime.now()

        # Inicializar navegador Chrome con DinoChrome
        self.chrome.initialize_browser(headless=False)

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        from datetime import datetime

        # Cerrar navegador Chrome
        self.chrome.close()

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
                return False

        except Exception:
            return False

    def _process_gift(self, live_event, queue_item):
        """Procesa evento de regalo"""
        event_data = live_event.event_data
        gift_name = event_data.get('gift', {}).get('name', '').lower()

        # Si es una rosa, reiniciar el juego y reproducir audio
        if 'rose' in gift_name or 'rosa' in gift_name:
            print(f"[DINOCHROME] 🌹 Rosa detectada! Reiniciando juego...")

            # Primero reiniciar el juego
            self.chrome.restart()

            # Luego reproducir audio de forma SÍNCRONA (espera a que termine)
            print(f"[DINOCHROME] 🔊 Reproduciendo audio...")
            self.elevenlabs.text_to_speech_and_save(
                "No no no no, me lo reiniciaste, ahora que voy a hacer? Estaba tan metido en mi juego y vienes tu y me lo reinicias, que cagada, te quiero mataar",
                play_audio=True,
                wait=True  # IMPORTANTE: Espera a que termine el audio
            )

            print(f"[DINOCHROME] ✅ Audio terminado")
            return True

        return True

    def _process_comment(self, live_event, queue_item):
        """Procesa evento de comentario"""
        return True

    def _process_like(self, live_event, queue_item):
        """Procesa evento de like"""
        return True

    def _process_share(self, live_event, queue_item):
        """Procesa evento de compartir"""
        return True

    def _process_follow(self, live_event, queue_item):
        """Procesa evento de follow"""
        return True

    def _process_subscribe(self, live_event, queue_item):
        """Procesa evento de suscripción"""
        return True
