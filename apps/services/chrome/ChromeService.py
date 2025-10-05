"""Chrome Service - DinoChrome con auto-play"""

import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChromeService:
    def __init__(self):
        self.driver = None

    def initialize_browser(self, headless=False):
        """Inicializa Chrome con DinoChrome nativo en modo offline"""
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)

        # Modo offline
        self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': True,
            'downloadThroughput': 0,
            'uploadThroughput': 0,
            'latency': 0
        })

        # Activar dino
        try:
            self.driver.get("https://www.google.com")
        except:
            pass

        # Auto-play
        threading.Thread(target=self._auto_play, daemon=True).start()
        return True

    def _auto_play(self):
        """Inicia y juega automáticamente"""
        time.sleep(1)

        # Iniciar juego
        self.driver.execute_script("document.dispatchEvent(new KeyboardEvent('keydown', {keyCode: 32}));")
        time.sleep(0.3)

        # Loop: detectar y saltar
        while self.driver:
            self.driver.execute_script("""
                if (typeof Runner !== 'undefined' && Runner.instance_) {
                    var r = Runner.instance_;
                    if (r.crashed) r.restart();
                    if (r.horizon?.obstacles?.[0]) {
                        var dist = r.horizon.obstacles[0].xPos - r.tRex.xPos;
                        if (dist > 0 && dist < 150 && !r.tRex.jumping)
                            document.dispatchEvent(new KeyboardEvent('keydown', {keyCode: 32}));
                    }
                }
            """)
            time.sleep(0.03)

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
