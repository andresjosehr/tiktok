"""
LLM Integration Service
Procesa eventos de TikTok usando LLMs genéricos
"""
import logging
from apps.queue_system.base_service import BaseQueueService
from .client import LLMClient

logger = logging.getLogger(__name__)


class LLMService(BaseQueueService):
    """
    Servicio que procesa eventos de TikTok usando LLMs.

    Genera respuestas automáticas basadas en los eventos recibidos.
    Compatible con cualquier proveedor de LLM (OpenAI, Claude, DeepSeek, LMStudio, etc.)
    """

    def __init__(self):
        super().__init__()
        self.client = None

    def on_start(self):
        """Inicializa el cliente LLM al arrancar el servicio"""
        self.client = LLMClient()
        logger.info(f"[LLM Service] Started - URL: {self.client.api_url}, Model: {self.client.model}")

    def process_event(self, live_event, queue_item):
        """
        Procesa un evento de TikTok generando una respuesta con LLM

        Args:
            live_event: Instancia de LiveEvent
            queue_item: Instancia de EventQueue

        Returns:
            bool: True si se procesó correctamente, False en caso contrario
        """
        if not self.client or not self.client.api_url:
            logger.error("[LLM Service] Cliente no configurado correctamente")
            return False

        try:
            # Generar respuesta
            response = self.client.generate_response(
                event_type=live_event.event_type,
                username=live_event.user_name or "Unknown",
                event_data=live_event.event_data
            )

            if response:
                logger.info(f"[LLM Service] {live_event.event_type} from {live_event.user_name}: {response[:100]}...")
                # Aquí podrías guardar la respuesta, enviarla a TTS, mostrarla en overlay, etc.
                return True
            else:
                logger.warning(f"[LLM Service] No response generated for {live_event.event_type}")
                return False

        except Exception as e:
            logger.error(f"[LLM Service] Error processing event: {str(e)}")
            return False
