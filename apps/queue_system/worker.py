"""
ServiceWorker - Worker que procesa la cola de un servicio

Este módulo se encarga de:
1. Sacar eventos de la cola por orden de prioridad
2. Procesarlos usando la clase del servicio
3. Manejar modo async vs sync
4. Marcar eventos como completados/fallidos
"""

import threading
import time
from importlib import import_module
from django.db import close_old_connections
from .models import Service, EventQueue


class ServiceWorker:
    """
    Worker que procesa la cola de un servicio específico

    Funcionalidad:
    - Obtiene eventos de la cola ordenados por prioridad
    - Procesa eventos SYNC (espera) o ASYNC (paralelo)
    - Maneja errores y marca estados
    - Ejecuta hooks del servicio (on_start, on_stop)
    """

    def __init__(self, service: Service, verbose: bool = True):
        """
        Inicializa el worker

        Args:
            service: Instancia de Service a procesar
            verbose: Si debe imprimir logs detallados
        """
        self.service = service
        self.verbose = verbose
        self.service_instance = None
        self.running = False
        self.thread = None
        self.async_threads = []  # Track async threads

    def _load_service_instance(self):
        """
        Carga dinámicamente la clase del servicio

        Returns:
            Instancia del servicio

        Raises:
            ImportError: Si no se puede importar la clase
            AttributeError: Si la clase no existe en el módulo
        """
        try:
            # Separar module_path y class_name
            # Ej: "apps.obs_overlay.services.OBSOverlayService"
            module_path, class_name = self.service.service_class.rsplit('.', 1)

            # Importar el módulo
            module = import_module(module_path)

            # Obtener la clase
            service_class = getattr(module, class_name)

            # Instanciar
            return service_class()

        except (ImportError, AttributeError) as e:
            self._log(f"❌ Error cargando servicio {self.service.name}: {e}", force=True)
            raise

    def start(self):
        """Inicia el worker en un thread separado"""
        if self.running:
            self._log("⚠️  Worker ya está corriendo", force=True)
            return

        try:
            # Cargar instancia del servicio
            self.service_instance = self._load_service_instance()
            self._log(f"✅ Servicio {self.service.name} cargado")

            # Ejecutar hook on_start
            self.service_instance.on_start()

            # Iniciar thread
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

            self._log(f"🚀 Worker iniciado para {self.service.name}")

        except Exception as e:
            self._log(f"❌ Error iniciando worker: {e}", force=True)
            raise

    def stop(self):
        """Detiene el worker gracefully"""
        if not self.running:
            return

        self._log(f"⏹️  Deteniendo worker {self.service.name}...")

        # Marcar como no corriendo
        self.running = False

        # Esperar a que termine el thread principal
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        # Esperar threads async
        for thread in self.async_threads:
            if thread.is_alive():
                thread.join(timeout=2)

        # Ejecutar hook on_stop
        if self.service_instance:
            self.service_instance.on_stop()

        self._log(f"✅ Worker {self.service.name} detenido")

    def _run_loop(self):
        """Loop principal del worker"""
        self._log(f"🔄 Loop iniciado para {self.service.name}")

        while self.running:
            try:
                # Cerrar conexiones viejas de Django
                close_old_connections()

                # Obtener siguiente evento de la cola
                queue_item = self._get_next_event()

                if not queue_item:
                    # No hay eventos, esperar un poco
                    time.sleep(0.1)
                    continue

                # LOG: Evento obtenido de la cola
                self._log(
                    f"📥 [{self.service.name}] Obtenido de cola: {queue_item.live_event.event_type} "
                    f"(P:{queue_item.priority}, ID:{queue_item.id})"
                )

                # Marcar como procesando
                queue_item.mark_processing()

                # Procesar según modo (async o sync)
                if queue_item.is_async:
                    # ASYNC: Procesar en thread separado (no esperar)
                    self._log(f"🔀 [{self.service.name}] Procesando ASYNC (ID:{queue_item.id})")
                    thread = threading.Thread(
                        target=self._process_event_safe,
                        args=(queue_item,),
                        daemon=True
                    )
                    thread.start()
                    self.async_threads.append(thread)

                    # Limpiar threads terminados
                    self.async_threads = [t for t in self.async_threads if t.is_alive()]

                else:
                    # SYNC: Procesar y esperar
                    self._log(f"⏳ [{self.service.name}] Procesando SYNC (ID:{queue_item.id})")
                    self._process_event_safe(queue_item)

            except Exception as e:
                self._log(f"❌ Error en loop: {e}", force=True)
                time.sleep(1)  # Esperar antes de reintentar

        self._log(f"🛑 Loop terminado para {self.service.name}")

    def _get_next_event(self):
        """
        Obtiene el siguiente evento de la cola

        Returns:
            EventQueue o None si no hay eventos
        """
        return EventQueue.objects.filter(
            service=self.service,
            status='pending'
        ).select_related('live_event', 'session').order_by(
            '-priority',  # Mayor prioridad primero
            'created_at'  # Más viejo primero (FIFO dentro de misma prioridad)
        ).first()

    def _process_event_safe(self, queue_item: EventQueue):
        """
        Procesa un evento con manejo de errores

        Args:
            queue_item: El item de la cola a procesar
        """
        start_time = time.time()
        live_event = queue_item.live_event
        event_type = live_event.event_type
        username = live_event.user_nickname or live_event.user_unique_id or 'Unknown'

        # Info adicional para GiftEvent
        extra_info = ""
        if event_type == 'GiftEvent':
            gift_name = live_event.event_data.get('gift', {}).get('name', '')
            extra_info = f"[{gift_name}] "

        try:
            # Cerrar conexiones viejas (importante en threads)
            close_old_connections()

            # Hook: antes de procesar
            self.service_instance.on_event_received(live_event, queue_item)

            # Procesar el evento
            success = self.service_instance.process_event(live_event, queue_item)

            # Calcular tiempo
            elapsed = (time.time() - start_time) * 1000

            # Marcar resultado
            if success:
                queue_item.mark_completed()
                self._log(
                    f"✅ [{self.service.name}] {event_type}{extra_info}de @{username} "
                    f"(P:{queue_item.priority}) completado en {elapsed:.0f}ms"
                )
            else:
                queue_item.mark_failed()
                self._log(
                    f"❌ [{self.service.name}] {event_type}{extra_info}de @{username} "
                    f"(P:{queue_item.priority}) falló en {elapsed:.0f}ms",
                    force=True
                )

            # Hook: después de procesar
            self.service_instance.on_event_processed(live_event, queue_item, success)

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            # Error crítico, marcar como fallido
            queue_item.mark_failed()
            self._log(
                f"💥 [{self.service.name}] Error procesando {event_type}{extra_info}"
                f"de @{username}: {e} ({elapsed:.0f}ms)",
                force=True
            )

    def _log(self, message: str, force: bool = False):
        """
        Log helper

        Args:
            message: Mensaje a imprimir
            force: Si debe imprimir aunque verbose=False
        """
        if self.verbose or force:
            print(message)

    def get_status(self):
        """
        Obtiene el estado actual del worker

        Returns:
            dict: Estado del worker
        """
        pending = EventQueue.objects.filter(
            service=self.service,
            status='pending'
        ).count()

        processing = EventQueue.objects.filter(
            service=self.service,
            status='processing'
        ).count()

        return {
            'service': self.service.name,
            'running': self.running,
            'pending': pending,
            'processing': processing,
            'async_threads': len([t for t in self.async_threads if t.is_alive()])
        }
