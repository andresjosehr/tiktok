"""
Comando para ejecutar workers de todos los servicios activos

Uso:
    python manage.py run_queue_workers
    python manage.py run_queue_workers --verbose
    python manage.py run_queue_workers --service dinochrome
"""

from django.core.management.base import BaseCommand
from apps.queue_system.models import Service
from apps.queue_system.worker import ServiceWorker
import time
import signal
import sys


class Command(BaseCommand):
    help = 'Ejecuta workers para procesar colas de servicios activos'

    def __init__(self):
        super().__init__()
        self.workers = []
        self.running = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--service',
            type=str,
            help='Ejecutar solo un servicio específico (por slug)',
            required=False
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar logs detallados de procesamiento'
        )

    def handle(self, *args, **options):
        # Configurar handler de señales para detener gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        service_slug = options.get('service')
        verbose = options.get('verbose', False)

        # Obtener servicios
        if service_slug:
            # Un servicio específico
            services = Service.objects.filter(slug=service_slug, is_active=True)
            if not services.exists():
                self.stdout.write(
                    self.style.ERROR(f'❌ Servicio "{service_slug}" no encontrado o inactivo')
                )
                return
        else:
            # Todos los servicios activos
            services = Service.objects.filter(is_active=True)

        if not services.exists():
            self.stdout.write(self.style.WARNING('⚠️  No hay servicios activos'))
            return

        # Banner inicial
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🚀 QUEUE WORKERS - Sistema de Procesamiento de Eventos'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')

        # Crear y iniciar workers
        for service in services:
            self.stdout.write(f'📦 Iniciando worker para: {self.style.WARNING(service.name)}')

            try:
                worker = ServiceWorker(service, verbose=verbose)
                worker.start()
                self.workers.append(worker)

                self.stdout.write(
                    f'  ✅ Worker activo - Cola máxima: {service.max_queue_size} eventos'
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error iniciando worker: {e}')
                )

        if not self.workers:
            self.stdout.write(self.style.ERROR('❌ No se pudo iniciar ningún worker'))
            return

        # Resumen
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ {len(self.workers)} worker(s) activo(s)'))
        self.stdout.write('')
        self.stdout.write('💡 Presiona Ctrl+C para detener los workers')
        self.stdout.write('📊 Estadísticas cada 30 segundos...')
        self.stdout.write('')

        # Loop de monitoreo
        try:
            counter = 0
            while self.running:
                time.sleep(1)
                counter += 1

                # Mostrar estadísticas cada 30 segundos
                if counter % 30 == 0:
                    self._show_stats()

        except KeyboardInterrupt:
            pass

        # Detener workers
        self._stop_workers()

    def _signal_handler(self, signum, frame):
        """Handler para señales de sistema"""
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  Señal recibida, deteniendo workers...'))
        self.running = False

    def _stop_workers(self):
        """Detiene todos los workers gracefully"""
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⏹️  Deteniendo workers...'))

        for worker in self.workers:
            try:
                worker.stop()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error deteniendo {worker.service.name}: {e}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Todos los workers detenidos'))
        self.stdout.write('')

    def _show_stats(self):
        """Muestra estadísticas de los workers"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DE WORKERS'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        for worker in self.workers:
            status = worker.get_status()

            # Indicador de estado
            status_icon = '🟢' if status['running'] else '🔴'

            self.stdout.write(f"\n{status_icon} {self.style.WARNING(status['service'])}")
            self.stdout.write(f"  • Pendientes: {status['pending']}")
            self.stdout.write(f"  • Procesando: {status['processing']}")

            if status['async_threads'] > 0:
                self.stdout.write(f"  • Threads async activos: {status['async_threads']}")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
