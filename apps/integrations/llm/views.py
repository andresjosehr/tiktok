from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .client import LLMClient
import json
import logging

logger = logging.getLogger(__name__)


def test_llm(request):
    """Página de prueba para el LLM"""
    return render(request, 'llm/test.html')


@require_http_methods(["POST"])
def send_message(request):
    """Envía un mensaje al LLM y devuelve la respuesta"""
    try:
        logger.info("[LLM View] Received request")
        data = json.loads(request.body)
        message = data.get('message', '')

        logger.info(f"[LLM View] Message: '{message[:50]}...'")

        if not message:
            logger.warning("[LLM View] No message provided")
            return JsonResponse({
                'success': False,
                'error': 'No message provided'
            }, status=400)

        # Inicializar cliente y enviar mensaje
        logger.info("[LLM View] Initializing LLM client")
        client = LLMClient()

        if not client.api_url:
            logger.error("[LLM View] LLM URL not configured")
            return JsonResponse({
                'success': False,
                'error': 'LLM URL not configured. Please configure llm_url in Config.'
            }, status=500)

        # Enviar mensaje
        logger.info("[LLM View] Sending message to LLM")
        response = client.chat(message)

        if response:
            logger.info(f"[LLM View] Success! Response: '{response[:50]}...'")
            return JsonResponse({
                'success': True,
                'response': response,
                'model': client.model,
                'provider': client.api_url
            })
        else:
            logger.error("[LLM View] No response from LLM client")
            return JsonResponse({
                'success': False,
                'error': 'No response from LLM. Check API key and configuration. Check logs for details.'
            }, status=500)

    except Exception as e:
        logger.error(f"[LLM View] Exception: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
