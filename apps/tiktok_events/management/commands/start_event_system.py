"""
Comando maestro para iniciar el sistema completo de eventos

Este comando integra:
- Captura de eventos de TikTok Live
- Workers de procesamiento de colas
- Dashboard de estadísticas en tiempo real
- Gestión unificada de procesos

Uso:
    python manage.py start_event_system
    python manage.py start_event_system --session-name "Sesión noche"
    python manage.py start_event_system --verbose

Nota: El username de TikTok se obtiene de la tabla Config (meta_key='tiktok_user')
"""

import os
import logging
import django
import signal
import sys
import time
import threading
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.tiktok_events.services import TikTokEventCapture
from apps.queue_system.models import Service, EventQueue
from apps.queue_system.worker import ServiceWorker
from apps.app_config.models import Config


# Ruta del archivo de log
LOG_FILE = os.path.join(settings.BASE_DIR, 'logs', 'event_system.log')


class Command(BaseCommand):
    help = 'Inicia el sistema completo: captura de TikTok + workers de servicios'

    def __init__(self):
        super().__init__()
        self.running = True
        self.workers = []
        self.tiktok_capture = None
        self.tiktok_thread = None
        self.stats = {
            'events_captured': 0,
            'events_queued': 0,
            'start_time': None
        }

    def _setup_logging(self):
        """Configura logging a archivo (borra el anterior al iniciar)"""
        # Crear directorio si no existe
        log_dir = os.path.dirname(LOG_FILE)
        os.makedirs(log_dir, exist_ok=True)

        # Borrar archivo anterior si existe
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

        # Configurar logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)  # También a consola
            ]
        )

        # Redirigir prints a logging manteniendo compatibilidad con file object
        class PrintLogger:
            def __init__(self, original_stdout, logger, level=logging.INFO):
                self._original = original_stdout
                self.logger = logger
                self.level = level
                self.encoding = getattr(original_stdout, 'encoding', 'utf-8')
                self.errors = getattr(original_stdout, 'errors', 'replace')

            def write(self, message):
                if message and message.strip():
                    self.logger.log(self.level, message.strip())
                return len(message) if message else 0

            def flush(self):
                pass

            def fileno(self):
                return self._original.fileno()

            def isatty(self):
                return False

        # Redirigir stdout para capturar prints
        sys.stdout = PrintLogger(sys.stdout, logging.getLogger('stdout'))

        logging.info(f"📝 Log iniciado: {LOG_FILE}")

    def add_arguments(self, parser):
        parser.add_argument(
            '--session-name',
            type=str,
            help='Nombre opcional para identificar esta sesión',
            required=False
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar logs detallados de procesamiento'
        )
        parser.add_argument(
            '--simulator',
            action='store_true',
            help='Modo simulador: solo inicia workers sin conectar a TikTok (usar con /simulator/)'
        )

    def handle(self, *args, **options):
        # Configurar logging a archivo
        self._setup_logging()

        # Configurar handlers de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        session_name = options.get('session_name')
        verbose = options.get('verbose', False)
        simulator_mode = options.get('simulator', False)

        if simulator_mode:
            username = 'simulator'
        else:
            # Obtener username desde Config
            username = Config.get_value('tiktok_user')
            if not username:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ Error: No se encontró el username de TikTok.\n'
                        'Por favor configura "tiktok_user" en el admin de Config'
                    )
                )
                return

        # Banner inicial
        self._show_banner(username, session_name, simulator_mode)

        # Configurar Django para async
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()

        try:
            # 1. Iniciar workers de servicios
            self._start_service_workers(verbose)

            if simulator_mode:
                # Modo simulador: solo workers, sin TikTok
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('=' * 70))
                self.stdout.write(self.style.SUCCESS('🎮 MODO SIMULADOR ACTIVO'))
                self.stdout.write(self.style.SUCCESS('=' * 70))
                self.stdout.write('')
                self.stdout.write('📡 Workers listos para recibir eventos del simulador')
                self.stdout.write('🌐 Abre /simulator/ en el navegador para enviar eventos')
                self.stdout.write('💡 Presiona Ctrl+C para detener')
                self.stdout.write('')
                self.stats['start_time'] = datetime.now()
                self._monitoring_loop_simulator()
            else:
                # 2. Iniciar captura de TikTok
                self._start_tiktok_capture(username, session_name)

                # 3. Loop de monitoreo
                self._monitoring_loop()

        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
        finally:
            # Detener todo
            self._shutdown()

    def _show_banner(self, username, session_name, simulator_mode=False):
        """Muestra el banner inicial"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        if simulator_mode:
            self.stdout.write(self.style.SUCCESS('🎮 SISTEMA DE EVENTOS - MODO SIMULADOR'))
        else:
            self.stdout.write(self.style.SUCCESS('🚀 SISTEMA DE EVENTOS TIKTOK - INICIO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        if not simulator_mode:
            self.stdout.write(f'\n📺 Streamer: {self.style.WARNING("@" + username)}')
        if session_name:
            self.stdout.write(f'📝 Sesión: {self.style.WARNING(session_name)}')
        self.stdout.write(f'⏰ Hora inicio: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('')

    def _start_service_workers(self, verbose):
        """Inicia los workers de servicios"""
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('📦 INICIANDO WORKERS DE SERVICIOS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        services = Service.objects.filter(is_active=True)

        if not services.exists():
            self.stdout.write(self.style.WARNING('⚠️  No hay servicios activos'))
            return

        for service in services:
            self.stdout.write(f'🔧 Iniciando worker: {self.style.WARNING(service.name)}')

            try:
                worker = ServiceWorker(service, verbose=verbose)
                worker.start()
                self.workers.append(worker)

                self.stdout.write(f'  ✅ Worker activo (cola máx: {service.max_queue_size})')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error iniciando worker: {e}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ {len(self.workers)} worker(s) iniciado(s)'))
        self.stdout.write('')

    def _start_tiktok_capture(self, username, session_name):
        """Inicia la captura de TikTok en un thread"""
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('📡 INICIANDO CAPTURA DE TIKTOK LIVE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        self.stdout.write(f'🎬 Conectando a @{username}...')

        try:
            self.tiktok_capture = TikTokEventCapture(username, session_name=session_name)

            # Iniciar en thread separado
            self.tiktok_thread = threading.Thread(
                target=self._run_tiktok_capture,
                daemon=True
            )
            self.tiktok_thread.start()

            # Esperar un poco para verificar conexión
            time.sleep(2)

            self.stdout.write(self.style.SUCCESS('✅ Captura de TikTok iniciada'))
            self.stdout.write('')

            self.stats['start_time'] = datetime.now()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error iniciando captura: {e}'))
            raise

    def _run_tiktok_capture(self):
        """Ejecuta la captura de TikTok (corre en thread)"""
        try:
            self.tiktok_capture.start()
        except Exception as e:
            print(f"\n❌ Error en captura de TikTok: {e}")
            self.running = False

    def _monitoring_loop(self):
        """Loop de monitoreo principal"""
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('📊 SISTEMA ACTIVO - Monitoreo en tiempo real'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write('💡 Presiona Ctrl+C para detener el sistema')
        self.stdout.write('📊 Estadísticas cada 30 segundos...')
        self.stdout.write('')

        counter = 0

        while self.running:
            time.sleep(1)
            counter += 1

            # Mostrar estadísticas cada 30 segundos
            if counter % 30 == 0:
                self._show_stats()

            # Verificar si el thread de TikTok sigue vivo
            if self.tiktok_thread and not self.tiktok_thread.is_alive():
                self.stdout.write('')
                self.stdout.write(
                    self.style.WARNING('⚠️  Captura de TikTok detenida inesperadamente')
                )
                self.running = False

    def _monitoring_loop_simulator(self):
        """Loop de monitoreo para modo simulador (sin TikTok)"""
        counter = 0
        while self.running:
            time.sleep(1)
            counter += 1
            if counter % 30 == 0:
                self._show_stats()

    def _show_stats(self):
        """Muestra estadísticas del sistema"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DEL SISTEMA'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Tiempo de ejecución
        if self.stats['start_time']:
            uptime = datetime.now() - self.stats['start_time']
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            self.stdout.write(f"\n⏱️  Tiempo activo: {hours}h {minutes}m")

        # Estadísticas de sesión
        if self.tiktok_capture and self.tiktok_capture.session:
            session = self.tiktok_capture.session
            self.stdout.write(f"📝 Sesión ID: {session.id}")
            self.stdout.write(f"📊 Eventos capturados: {session.total_events}")

        # Estadísticas de workers
        self.stdout.write(f"\n🔧 Workers activos: {len(self.workers)}")
        for worker in self.workers:
            status = worker.get_status()
            status_icon = '🟢' if status['running'] else '🔴'

            self.stdout.write(f"\n{status_icon} {self.style.WARNING(status['service'])}")
            self.stdout.write(f"  • Pendientes: {status['pending']}")
            self.stdout.write(f"  • Procesando: {status['processing']}")

            if status['async_threads'] > 0:
                self.stdout.write(f"  • Threads async: {status['async_threads']}")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

    def _signal_handler(self, signum, frame):
        """Handler para señales de sistema"""
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  Señal recibida, deteniendo sistema...'))
        self.running = False

    def _shutdown(self):
        """Detiene todo el sistema gracefully"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('⏹️  DETENIENDO SISTEMA'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # 1. Detener workers
        if self.workers:
            self.stdout.write('🔧 Deteniendo workers...')
            for worker in self.workers:
                try:
                    worker.stop()
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Error deteniendo {worker.service.name}: {e}')
                    )
            self.stdout.write('  ✅ Todos los workers detenidos')

        # 2. Finalizar sesión de TikTok
        if self.tiktok_capture and self.tiktok_capture.session:
            self.stdout.write('\n📝 Finalizando sesión de TikTok...')
            try:
                self.tiktok_capture.session.end_session(status='completed')
                duration = self.tiktok_capture.session.get_duration_display()
                total = self.tiktok_capture.session.total_events

                self.stdout.write(f'  ✅ Sesión finalizada')
                self.stdout.write(f'  • Duración: {duration}')
                self.stdout.write(f'  • Eventos capturados: {total}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error finalizando sesión: {e}'))

        # Resumen final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ SISTEMA DETENIDO EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
