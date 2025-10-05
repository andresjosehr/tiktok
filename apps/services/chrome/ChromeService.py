"""Chrome Service - DinoChrome con auto-play"""

import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChromeService:
    def __init__(self):
        self.driver = None

    def initialize_browser(self, headless=False):
        """Inicializa Chrome con DinoChrome"""
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)

        # Cargar DinoChrome desde chrome-dino-game.github.io
        self.driver.get("https://chrome-dino-game.github.io/")
        time.sleep(1.5)

        # Auto-play
        threading.Thread(target=self._auto_play, daemon=True).start()
        return True

    def _auto_play(self):
        """Inicia y juega automáticamente"""
        time.sleep(2)

        # Hacer inmortal
        self.driver.execute_script("Runner.prototype.gameOver = function() {};")

        # Iniciar juego - múltiples intentos
        for _ in range(3):
            self.driver.execute_script("document.dispatchEvent(new KeyboardEvent('keydown', {keyCode: 32}));")
            time.sleep(0.3)

        # Configurar velocidad
        configured = False

        # Loop: detectar y saltar
        while self.driver:
            result = self.driver.execute_script("""
                if (typeof Runner !== 'undefined' && Runner.instance_) {
                    var r = Runner.instance_;

                    // Configurar velocidad fija (solo la primera vez)
                    if (r.config.ACCELERATION !== 0) {
                        r.setSpeed(6);
                        r.config.ACCELERATION = 0;
                        return 'configured';
                    }

                    // Saltar obstáculos
                    if (r.horizon?.obstacles?.[0]) {
                        var dist = r.horizon.obstacles[0].xPos - r.tRex.xPos;
                        if (dist > 0 && dist < 100 && !r.tRex.jumping) {
                            document.dispatchEvent(new KeyboardEvent('keydown', {keyCode: 32}));
                            return dist;
                        }
                    }
                    return 'ok';
                }
                return 'no_runner';
            """)

            if result == 'configured' and not configured:
                print("[CHROME] ✅ Velocidad configurada")
                configured = True
            elif isinstance(result, (int, float)):
                print(f"[CHROME] 🦖 Salto! ({result}px)")
            elif result == 'no_runner':
                print("[CHROME] ⚠️ Runner no disponible")

            time.sleep(0.03)

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
