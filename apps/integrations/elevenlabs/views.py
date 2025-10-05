from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from apps.integrations.elevenlabs.client import ElevenLabsClient


@staff_member_required
def test_tts_view(request):
    """Vista para probar text-to-speech"""
    if request.method == 'POST':
        text = request.POST.get('text', '')

        if not text:
            return JsonResponse({'success': False, 'error': 'Texto vacío'})

        try:
            client = ElevenLabsClient()
            audio_path = client.text_to_speech_and_save(text, play_audio=True)

            if audio_path:
                # Construir URL del archivo de audio
                from django.conf import settings
                audio_url = f"{settings.MEDIA_URL}{audio_path}"
                return JsonResponse({
                    'success': True,
                    'message': f'Audio generado y reproduciendo: "{text}"',
                    'audio_url': audio_url
                })
            else:
                return JsonResponse({'success': False, 'error': 'Error generando audio'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # Renderizar el formulario HTML
    return render(request, 'admin/elevenlabs_test.html', {
        'title': 'Prueba de ElevenLabs TTS',
    })
