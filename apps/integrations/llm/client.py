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
            print("[LLM] ❌ ERROR: URL no configurada")
            logger.error("[LLM] URL no configurada")
            return None

        print(f"[LLM] 📤 Enviando mensaje: '{user_message[:80]}...'")
        logger.info(f"[LLM] Sending message: '{user_message[:50]}...'")

        # Construir mensajes
        messages = []
        if system_message or self.system_prompt:
            messages.append({
                'role': 'system',
                'content': system_message or self.system_prompt
            })
            print(f"[LLM] 📋 System prompt (primeros 100 chars): '{(system_message or self.system_prompt)[:100]}...'")
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
            print(f"[LLM] 🔑 Usando API key: ***{self.api_key[-4:] if len(self.api_key) >= 4 else '????'}")
            logger.info(f"[LLM] Using API key: ***{self.api_key[-4:]}")
        else:
            print("[LLM] ⚠️ WARNING: No hay API key configurada!")
            logger.warning("[LLM] No API key set!")

        # Request body (formato OpenAI-compatible)
        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }

        # Configurar reasoning para modelos que lo soporten (Groq)
        if 'groq.com' in self.api_url:
            # Para modelos GPT-OSS, usar reasoning_effort="low" para minimizar tokens de razonamiento
            if 'gpt-oss' in self.model:
                data['reasoning_effort'] = 'low'
                print(f"[LLM] 🔽 Usando reasoning_effort=low (minimiza razonamiento)")
            else:
                # Para otros modelos, deshabilitar reasoning completamente
                data['include_reasoning'] = False
                print(f"[LLM] 🚫 Deshabilitando reasoning (include_reasoning=False)")

        print(f"[LLM] 🌐 Enviando request a: {self.api_url}")
        print(f"[LLM] 🤖 Modelo: {self.model}, Max tokens: {max_tokens}, Temp: {temperature}")
        logger.info(f"[LLM] Request to {self.api_url}")
        logger.debug(f"[LLM] Request body: {data}")

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )

            print(f"[LLM] 📥 Response status: {response.status_code}")
            logger.info(f"[LLM] Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"[LLM] Response JSON: {result}")

                # Formato OpenAI: choices[0].message.content
                message = result['choices'][0]['message']
                content = message.get('content', '').strip()

                # Verificar finish_reason
                finish_reason = result['choices'][0].get('finish_reason')

                if content:
                    print(f"[LLM] ✅ SUCCESS: '{content}'")
                    if finish_reason:
                        print(f"[LLM] 🏁 Finish reason: {finish_reason}")
                    logger.info(f"[LLM] Response received: '{content[:100]}...'")
                    return content
                else:
                    # Si content está vacío
                    print(f"[LLM] ⚠️ WARNING: Content vacío!")
                    print(f"[LLM] 🏁 Finish reason: {finish_reason}")

                    # Si hay reasoning (aunque debería estar deshabilitado)
                    if 'reasoning' in message:
                        reasoning = message.get('reasoning', '').strip()
                        print(f"[LLM] 🧠 Reasoning detectado (no debería aparecer): '{reasoning[:150]}...'")

                    print(f"[LLM] 📄 Full response JSON: {result}")
                    logger.warning(f"[LLM] Empty content. Finish reason: {finish_reason}. Full JSON: {result}")
                    return None
            else:
                print(f"[LLM] ❌ ERROR {response.status_code}: {response.text}")
                logger.error(f"[LLM] Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print("[LLM] ⏱️ TIMEOUT: Request timeout after 30 seconds")
            logger.error("[LLM] Request timeout after 30 seconds")
            return None
        except KeyError as e:
            print(f"[LLM] ❌ KeyError: Formato de respuesta inesperado - clave faltante: {e}")
            print(f"[LLM] 📄 Full response: {response.text if 'response' in locals() else 'No response'}")
            logger.error(f"[LLM] Unexpected response format - missing key: {e}")
            logger.error(f"[LLM] Full response: {response.text if 'response' in locals() else 'No response'}")
            return None
        except Exception as e:
            print(f"[LLM] ❌ EXCEPTION: {str(e)}")
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
