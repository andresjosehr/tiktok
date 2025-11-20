"""Chrome Service - DinoChrome con auto-play"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ChromeService:
    def __init__(self):
        self.driver = None

    def initialize_browser(self, headless=False, width=800, height=600):
        """Inicializa Chrome con DinoChrome"""
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={width},{height}')

        # Usar webdriver-manager para instalar ChromeDriver automáticamente
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        # Cargar DinoChrome local desde Django
        self.driver.get("http://localhost:8000/dino/")
        time.sleep(3)  # Esperar a que termine la animación de inicio

        # Auto-play (ya está implementado en el juego)
        return True

    def get_score(self):
        """Obtiene el score actual del juego"""
        try:
            return self.driver.execute_script("""
                const scoreElem = document.querySelector('[data-score]');
                return scoreElem ? parseInt(scoreElem.textContent) : 0;
            """)
        except:
            return 0

    def get_high_score(self):
        """Obtiene el récord del juego"""
        try:
            return self.driver.execute_script("""
                const highScoreElem = document.querySelector('[data-high-score]');
                return highScoreElem ? parseInt(highScoreElem.textContent) : 0;
            """)
        except:
            return 0

    def restart(self):
        """Reinicia el juego"""
        try:
            self.driver.execute_script("window.restartGame();")
            return True
        except:
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
