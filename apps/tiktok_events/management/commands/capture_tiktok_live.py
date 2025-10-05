import os
import django
from django.core.management.base import BaseCommand
from apps.tiktok_events.services import TikTokEventCapture
from apps.app_config.models import Config


class Command(BaseCommand):
    help = 'Captura eventos de TikTok Live en tiempo real desde la configuración'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username del streamer de TikTok (sin @). Si no se proporciona, usa tiktok_user de Config',
            required=False
        )

    def handle(self, *args, **options):
        # Obtener username del argumento o de la configuración
        username = options.get('username')

        if not username:
            username = Config.get_value('tiktok_user')

            if not username:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ Error: No se encontró el username.\n'
                        'Por favor:\n'
                        '1. Ejecuta: python manage.py capture_tiktok_live --username <username>\n'
                        '2. O configura "tiktok_user" en el admin de Config'
                    )
                )
                return

            self.stdout.write(
                self.style.SUCCESS(f'✅ Username obtenido de Config: @{username}')
            )

        # Configurar Django para async
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()

        self.stdout.write(
            self.style.SUCCESS(f'📡 Iniciando captura de eventos para @{username}')
        )

        try:
            capture = TikTokEventCapture(username)
            capture.start()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⏹️ Captura detenida por el usuario')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
