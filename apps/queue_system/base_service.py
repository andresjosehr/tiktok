"""
BaseQueueService - Clase base abstracta para servicios de cola

Todos los servicios que procesen eventos deben heredar de esta clase
e implementar el método process_event()
"""

from abc import ABC, abstractmethod
from apps.tiktok_events.models import LiveEvent
from .models import EventQueue


class BaseQueueService(ABC):
    """
    Clase base abstracta para todos los servicios de cola

    Los servicios deben heredar de esta clase e implementar process_event()

    Ejemplo:
        class OBSOverlayService(BaseQueueService):
            def process_event(self, live_event, queue_item):
                if live_event.event_type == 'GiftEvent':
                    self.show_gift_animation(live_event)
                    return True
                return False
    """

    @abstractmethod
    def process_event(self, live_event: LiveEvent, queue_item: EventQueue) -> bool:
        """
        Procesa un evento de la cola.

        Este método DEBE ser implementado por cada servicio.

        Args:
            live_event: El evento de TikTok a procesar
            queue_item: El item de la cola (contiene metadata como prioridad, estado, etc.)

        Returns:
            bool: True si se procesó exitosamente, False si falló

        Ejemplo:
            def process_event(self, live_event, queue_item):
                try:
                    if live_event.event_type == 'GiftEvent':
                        gift_name = live_event.event_data['gift']['name']
                        self.display_gift(gift_name)
                        return True
                    return False
                except Exception as e:
                    print(f"Error: {e}")
                    return False
        """
        pass

    def on_start(self):
        """
        Hook ejecutado cuando el worker inicia (opcional).

        Útil para:
        - Conectar a servicios externos (OBS, Chrome, etc.)
        - Inicializar recursos
        - Configurar estado inicial

        Ejemplo:
            def on_start(self):
                self.obs_client = OBSWebSocket()
                self.obs_client.connect()
                print("✅ Conectado a OBS")
        """
        pass

    def on_stop(self):
        """
        Hook ejecutado cuando el worker se detiene (opcional).

        Útil para:
        - Cerrar conexiones
        - Liberar recursos
        - Limpiar estado

        Ejemplo:
            def on_stop(self):
                self.obs_client.disconnect()
                print("👋 Desconectado de OBS")
        """
        pass

    def on_event_received(self, live_event: LiveEvent, queue_item: EventQueue):
        """
        Hook ejecutado ANTES de procesar un evento (opcional).

        Útil para:
        - Logging
        - Métricas
        - Validaciones previas

        Ejemplo:
            def on_event_received(self, live_event, queue_item):
                print(f"📥 Recibido: {live_event.event_type} (P:{queue_item.priority})")
        """
        pass

    def on_event_processed(self, live_event: LiveEvent, queue_item: EventQueue, success: bool):
        """
        Hook ejecutado DESPUÉS de procesar un evento (opcional).

        Args:
            live_event: El evento procesado
            queue_item: El item de la cola
            success: Si el procesamiento fue exitoso

        Útil para:
        - Logging de resultados
        - Métricas
        - Limpieza post-procesamiento

        Ejemplo:
            def on_event_processed(self, live_event, queue_item, success):
                status = "✅" if success else "❌"
                print(f"{status} Procesado: {live_event.event_type}")
        """
        pass
