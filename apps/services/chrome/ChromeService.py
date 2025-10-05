"""
Chrome Service - Capa de abstracción para controlar Chrome/navegador

Este servicio maneja la conexión con el navegador y operaciones del juego DinoChrome.
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time

logger = logging.getLogger('chrome')


class ChromeService:
    """
    Servicio para controlar Chrome y el juego DinoChrome

    Métodos principales:
    - initialize_browser(): Abre ventana con DinoChrome activado
    - jump(): Hace saltar el dinosaurio
    - restart_game(): Reinicia el juego
    """

    def __init__(self):
        self.driver = None
        self.game_url = "chrome://dino"

    def initialize_browser(self, headless=False):
        """
        Inicializa una nueva ventana del navegador con DinoChrome

        Args:
            headless (bool): Si True, ejecuta en modo headless (sin interfaz gráfica)

        Returns:
            bool: True si se inicializó correctamente
        """
        try:
            logger.info("[CHROME] Inicializando navegador Chrome...")

            # Configurar opciones de Chrome
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--remote-debugging-port=9222')

            # Agregar user-data-dir único para evitar conflictos
            import tempfile
            user_data_dir = tempfile.mkdtemp(prefix='chrome_')
            chrome_options.add_argument(f'--user-data-dir={user_data_dir}')

            # Inicializar driver
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("[CHROME] Driver inicializado correctamente")

            # Navegar a DinoChrome
            logger.info(f"[CHROME] Navegando a {self.game_url}...")
            self.driver.get(self.game_url)
            time.sleep(1)  # Esperar a que cargue el juego

            logger.info("[CHROME] ✅ Navegador inicializado con DinoChrome activado")
            return True

        except WebDriverException as e:
            logger.error(f"[CHROME] ❌ Error al inicializar navegador: {e}")
            return False
        except Exception as e:
            logger.error(f"[CHROME] ❌ Error inesperado: {e}", exc_info=True)
            return False

    def jump(self):
        """
        Hace saltar el dinosaurio en el juego DinoChrome

        Returns:
            bool: True si el salto se ejecutó correctamente
        """
        if not self.driver:
            logger.error("[CHROME] ❌ Navegador no inicializado. Llama a initialize_browser() primero")
            return False

        try:
            logger.info("[CHROME] Ejecutando salto del dinosaurio...")

            # Obtener el elemento body y enviar espacio para saltar
            body = self.driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.SPACE)

            logger.info("[CHROME] ✅ Dinosaurio saltó correctamente")
            return True

        except WebDriverException as e:
            logger.error(f"[CHROME] ❌ Error al ejecutar salto: {e}")
            return False
        except Exception as e:
            logger.error(f"[CHROME] ❌ Error inesperado al saltar: {e}", exc_info=True)
            return False

    def restart_game(self):
        """
        Reinicia el juego DinoChrome

        Returns:
            bool: True si el juego se reinició correctamente
        """
        if not self.driver:
            logger.error("[CHROME] ❌ Navegador no inicializado. Llama a initialize_browser() primero")
            return False

        try:
            logger.info("[CHROME] Reiniciando juego DinoChrome...")

            # Recargar la página para reiniciar el juego
            self.driver.refresh()
            time.sleep(1)  # Esperar a que cargue

            logger.info("[CHROME] ✅ Juego reiniciado correctamente")
            return True

        except WebDriverException as e:
            logger.error(f"[CHROME] ❌ Error al reiniciar juego: {e}")
            return False
        except Exception as e:
            logger.error(f"[CHROME] ❌ Error inesperado al reiniciar: {e}", exc_info=True)
            return False

    def close(self):
        """
        Cierra el navegador y libera recursos

        Returns:
            bool: True si se cerró correctamente
        """
        if self.driver:
            try:
                logger.info("[CHROME] Cerrando navegador...")
                self.driver.quit()
                self.driver = None
                logger.info("[CHROME] ✅ Navegador cerrado correctamente")
                return True
            except Exception as e:
                logger.error(f"[CHROME] ❌ Error al cerrar navegador: {e}")
                return False
        return True

    def is_initialized(self):
        """
        Verifica si el navegador está inicializado

        Returns:
            bool: True si el driver está activo
        """
        return self.driver is not None

    def __del__(self):
        """Destructor: asegura que el navegador se cierre al destruir el objeto"""
        self.close()
