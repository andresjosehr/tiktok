"""
Cliente genérico de LLM compatible con múltiples proveedores
Soporta: OpenAI, Claude, DeepSeek, LMStudio, etc.
"""

import requests
import logging
from apps.app_config.models import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """Cliente genérico para interactuar con APIs de LLM (formato OpenAI-compatible)"""

    def __init__(self):
        self.api_url = self._get_config('llm_url')
        self.api_key = self._get_config('llm_key')
        self.model = self._get_config('llm_model', 'deepseek-chat')
        self.system_prompt = self._get_config(
            'llm_system_prompt',
            'You are a helpful assistant for a TikTok Live streaming system.'
        )

        # Log initialization
        logger.info(f"[LLM Client] Initialized - URL: {self.api_url}, Model: {self.model}, API Key: {'***' + self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else 'NOT SET'}")

    def _get_config(self, key, default=''):
        """Obtiene configuración desde la base de datos"""
        try:
            config = Config.objects.get(meta_key=key)
            return config.meta_value or default
        except Config.DoesNotExist:
            return default

    def chat(self, user_message, system_message=None, max_tokens=150, temperature=0.7):
        """
        Envía un mensaje al LLM y obtiene respuesta

        Args:
            user_message (str): Mensaje del usuario
            system_message (str): Mensaje del sistema (opcional, usa self.system_prompt si no se especifica)
            max_tokens (int): Máximo de tokens en la respuesta
            temperature (float): Temperatura del modelo (0-2)

        Returns:
            str: Respuesta del LLM o None si falla
        """
        if not self.api_url:
            logger.error("[LLM] URL no configurada")
            return None

        logger.info(f"[LLM] Sending message: '{user_message[:50]}...'")

        # Construir mensajes
        messages = []
        if system_message or self.system_prompt:
            messages.append({
                'role': 'system',
                'content': system_message or self.system_prompt
            })
        messages.append({
            'role': 'user',
            'content': user_message
        })

        # Headers
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            logger.info(f"[LLM] Using API key: ***{self.api_key[-4:]}")
        else:
            logger.warning("[LLM] No API key set!")

        # Request body (formato OpenAI-compatible)
        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }

        logger.info(f"[LLM] Request to {self.api_url}")
        logger.debug(f"[LLM] Request body: {data}")

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )

            logger.info(f"[LLM] Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"[LLM] Response JSON: {result}")
                # Formato OpenAI: choices[0].message.content
                content = result['choices'][0]['message']['content'].strip()
                logger.info(f"[LLM] Response received: '{content[:100]}...'")
                return content
            else:
                logger.error(f"[LLM] Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("[LLM] Request timeout after 30 seconds")
            return None
        except KeyError as e:
            logger.error(f"[LLM] Unexpected response format - missing key: {e}")
            logger.error(f"[LLM] Full response: {response.text if 'response' in locals() else 'No response'}")
            return None
        except Exception as e:
            logger.error(f"[LLM] Exception: {str(e)}", exc_info=True)
            return None

    def generate_response(self, event_type, username, event_data=None):
        """
        Genera una respuesta específica para un evento de TikTok

        Args:
            event_type (str): Tipo de evento (GiftEvent, CommentEvent, etc.)
            username (str): Nombre del usuario
            event_data (dict): Datos adicionales del evento

        Returns:
            str: Respuesta generada o None si falla
        """
        event_data = event_data or {}

        # Construir prompts específicos por tipo de evento
        prompts = {
            'GiftEvent': f"User {username} sent a gift: {event_data.get('gift_name', 'unknown')} (value: {event_data.get('gift_cost', 0)}). Generate a brief thank you message.",
            'CommentEvent': f"User {username} commented: '{event_data.get('comment', '')}'. Generate a brief response.",
            'FollowEvent': f"User {username} just followed the stream. Generate a brief welcome message.",
            'ShareEvent': f"User {username} shared the stream. Generate a brief thank you message.",
            'SubscribeEvent': f"User {username} subscribed. Generate a brief celebration message.",
            'LikeEvent': f"User {username} liked the stream ({event_data.get('like_count', 1)} likes). Generate a very brief acknowledgment.",
            'JoinEvent': f"User {username} joined the stream. Generate a very brief welcome.",
        }

        prompt = prompts.get(
            event_type,
            f"A {event_type} event occurred from user {username}. Acknowledge it briefly."
        )

        return self.chat(prompt, max_tokens=100, temperature=0.8)
