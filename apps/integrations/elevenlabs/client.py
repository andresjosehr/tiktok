"""
Cliente de ElevenLabs para text-to-speech

Documentación: https://elevenlabs.io/docs/api-reference/text-to-speech
"""

import os
import subprocess
import requests
from django.conf import settings
from apps.app_config.models import Config


class ElevenLabsClient:
    """Cliente para interactuar con la API de ElevenLabs"""

    # Usar API global para mejor latencia
    BASE_URL = "https://api-global-preview.elevenlabs.io/v1"

    def __init__(self):
        self.api_key = self._get_api_key()

    def _get_api_key(self):
        """Obtiene la API key desde la configuración"""
        try:
            config = Config.objects.get(meta_key='elevenlabs_api')
            return config.meta_value
        except Config.DoesNotExist:
            return None

    def text_to_speech(self, text, voice_id="21m00Tcm4TlvDq8ikWAM", model_id="eleven_flash_v2_5"):
        """
        Convierte texto a audio usando ElevenLabs con streaming para menor latencia

        Args:
            text (str): Texto a convertir
            voice_id (str): ID de la voz a usar (default: Rachel)
            model_id (str): Modelo de TTS (default: eleven_flash_v2_5 para baja latencia)

        Returns:
            bytes: Audio en formato MP3 o None si falla
        """
        if not self.api_key:
            print("[ELEVENLABS] ⚠️ API key no configurada")
            return None

        url = f"{self.BASE_URL}/text-to-speech/{voice_id}/stream"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            },
            "optimize_streaming_latency": 3
        }

        try:
            response = requests.post(url, json=data, headers=headers, stream=True)

            if response.status_code == 200:
                audio_chunks = []
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        audio_chunks.append(chunk)
                return b''.join(audio_chunks)
            else:
                print(f"[ELEVENLABS] ❌ Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"[ELEVENLABS] ❌ Exception en text_to_speech: {str(e)}")
            return None

    def text_to_speech_and_save(self, text, voice_id="21m00Tcm4TlvDq8ikWAM", model_id="eleven_flash_v2_5", play_audio=False, wait=False):
        """
        Convierte texto a audio y lo guarda en un archivo

        Args:
            text (str): Texto a convertir
            voice_id (str): ID de la voz a usar (default: Rachel)
            model_id (str): Modelo de TTS a usar
            play_audio (bool): Si es True, reproduce el audio automáticamente
            wait (bool): Si es True, espera a que termine la reproducción (requiere play_audio=True)

        Returns:
            str: Ruta del archivo generado o None si falla
        """
        audio_data = self.text_to_speech(text, voice_id, model_id)

        if audio_data:
            file_path = self.save_audio(audio_data)

            if file_path and play_audio:
                self.play_audio(file_path, wait=wait)

            return file_path

        return None

    def save_audio(self, audio_data, filename=None):
        """
        Guarda audio desde bytes MP3 a un archivo

        Args:
            audio_data (bytes): Audio en formato MP3
            filename (str): Nombre del archivo (opcional)

        Returns:
            str: Ruta relativa del archivo guardado o None si falla
        """
        try:
            # Crear directorio si no existe
            audio_dir = os.path.join(settings.MEDIA_ROOT, 'elevenlabs')
            os.makedirs(audio_dir, exist_ok=True)

            # Generar nombre de archivo si no se proporciona
            if not filename:
                import time
                filename = f"tts_{int(time.time())}.mp3"

            # Asegurar extensión .mp3
            if not filename.endswith('.mp3'):
                filename += '.mp3'

            # Ruta completa del archivo
            file_path = os.path.join(audio_dir, filename)

            # Guardar audio
            with open(file_path, 'wb') as f:
                f.write(audio_data)

            # Retornar ruta relativa desde MEDIA_ROOT
            relative_path = os.path.join('elevenlabs', filename)
            return relative_path

        except Exception as e:
            print(f"[ELEVENLABS] ❌ Error guardando audio: {str(e)}")
            return None

    def play_audio(self, file_path, wait=False):
        """
        Envía audio al reproductor web (navegador Windows)

        Args:
            file_path (str): Ruta relativa del archivo desde MEDIA_ROOT
            wait (bool): Si es True, espera a que termine la reproducción (bloqueante)

        Returns:
            bool: True si se envió correctamente
        """
        try:
            absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)

            if not os.path.exists(absolute_path):
                print(f"[ELEVENLABS] ❌ Archivo no encontrado: {absolute_path}")
                return False

            from apps.audio_player.views import set_audio
            set_audio(absolute_path, channel='voice')

            if wait:
                import subprocess
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', absolute_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    try:
                        duration = float(result.stdout.strip())
                        import time
                        time.sleep(duration)
                    except:
                        pass

            return True

        except Exception as e:
            print(f"[ELEVENLABS] ❌ Exception enviando audio: {str(e)}")
            return False

    def get_voices(self):
        """
        Obtiene la lista de voces disponibles

        Returns:
            list: Lista de voces o None si falla
        """
        if not self.api_key:
            print("[ELEVENLABS] ⚠️ API key no configurada")
            return None

        url = f"{self.BASE_URL}/voices"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.json().get('voices', [])
            else:
                print(f"[ELEVENLABS] ❌ Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"[ELEVENLABS] ❌ Exception en get_voices: {str(e)}")
            return None
