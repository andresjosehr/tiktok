"""
Cliente de OBS WebSocket para controlar OBS Studio remotamente
"""

import time
import obsws_python as obs
from apps.app_config.models import Config


class OBSClient:
    """Cliente para interactuar con OBS via WebSocket"""

    def __init__(self):
        self.host = self._get_config('obs_ws_host', 'localhost')
        self.port = int(self._get_config('obs_ws_port', '4455'))
        self.password = self._get_config('obs_ws_password', '')

    def _get_config(self, key, default=''):
        try:
            config = Config.objects.get(meta_key=key)
            return config.meta_value or default
        except Config.DoesNotExist:
            return default

    def _connect(self):
        return obs.ReqClient(
            host=self.host,
            port=self.port,
            password=self.password,
            timeout=5
        )

    def refresh_all_browser_sources(self):
        """
        Refresca todos los browser sources de OBS cambiando la URL
        a about:blank y restaurandola para forzar recarga completa.

        Returns:
            dict: {'success': bool, 'refreshed': list, 'error': str}
        """
        try:
            client = self._connect()
            inputs = client.get_input_list('browser_source')

            # Guardar URLs originales y poner about:blank
            original_urls = {}
            for inp in inputs.inputs:
                name = inp['inputName']
                try:
                    settings = client.get_input_settings(name)
                    original_urls[name] = settings.input_settings.get('url', '')
                    client.set_input_settings(name, {'url': 'about:blank'}, True)
                except Exception as e:
                    print(f"[OBS] Error en '{name}': {e}")

            time.sleep(2)

            # Restaurar URLs originales
            refreshed = []
            for name, url in original_urls.items():
                try:
                    client.set_input_settings(name, {'url': url}, True)
                    refreshed.append(name)
                except Exception as e:
                    print(f"[OBS] Error restaurando '{name}': {e}")

            client.disconnect()
            return {
                'success': True,
                'refreshed': refreshed,
                'total': len(refreshed)
            }

        except ConnectionRefusedError:
            return {
                'success': False,
                'error': 'No se pudo conectar a OBS. Esta corriendo?'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
