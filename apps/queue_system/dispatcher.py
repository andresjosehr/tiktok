"""
EventDispatcher - Sistema de distribución de eventos a colas de servicios

Este módulo se encarga de:
1. Recibir eventos (LiveEvent)
2. Buscar servicios activos suscritos al tipo de evento
3. Verificar espacio en cola
4. Encolar eventos con prioridad
5. Descartar eventos de baja prioridad si es necesario
"""

from .models import Service, ServiceEventConfig, EventQueue


class EventDispatcher:
    """Distribuye eventos a las colas de servicios suscritos"""

    @staticmethod
    def dispatch(live_event):
        """
        Distribuye un evento a todos los servicios suscritos

        Args:
            live_event: Instancia de LiveEvent a distribuir

        Returns:
            dict: Resumen de encolamiento por servicio
        """
        results = {
            'enqueued': [],
            'discarded': [],
            'queue_full': []
        }

        # 1. Obtener servicios activos suscritos a este tipo de evento
        configs = ServiceEventConfig.objects.filter(
            service__is_active=True,
            event_type=live_event.event_type,
            is_enabled=True
        ).select_related('service')

        # 2. Procesar cada configuración
        for config in configs:
            result = EventDispatcher._process_service_queue(live_event, config)

            if result['status'] == 'enqueued':
                results['enqueued'].append({
                    'service': config.service.name,
                    'priority': config.priority
                })
            elif result['status'] == 'discarded':
                results['discarded'].append({
                    'service': config.service.name,
                    'reason': result.get('reason', 'Unknown')
                })
            elif result['status'] == 'queue_full':
                results['queue_full'].append({
                    'service': config.service.name,
                    'reason': 'Cola llena sin eventos descartables'
                })

        return results

    @staticmethod
    def _process_service_queue(live_event, config):
        """
        Procesa el encolamiento para un servicio específico

        Args:
            live_event: El evento a encolar
            config: ServiceEventConfig del servicio

        Returns:
            dict: Resultado del procesamiento
        """
        service = config.service

        # 1. Filtrar por is_stackable para GiftEvent
        if live_event.event_type == 'GiftEvent' and not config.is_stackable:
            # Solo procesar si la racha ha finalizado (streak_status == 'end')
            if live_event.streak_status != 'end':
                return {
                    'status': 'skipped',
                    'reason': 'Evento no stackable - esperando fin de racha'
                }

        # 2. Verificar tamaño de cola
        current_queue_size = EventQueue.objects.filter(
            service=service,
            status='pending'
        ).count()

        # 3. Si hay espacio, encolar directamente
        if current_queue_size < service.max_queue_size:
            EventDispatcher._enqueue_event(live_event, config)
            return {'status': 'enqueued'}

        # 3. Cola llena - intentar descartar eventos de menor prioridad
        if config.is_discardable:
            # El nuevo evento es descartable
            # Intentar encontrar un evento descartable de menor prioridad
            discarded = EventDispatcher._try_discard_lower_priority(service, config.priority)

            if discarded:
                # Se descartó un evento de menor prioridad, encolar el nuevo
                EventDispatcher._enqueue_event(live_event, config)
                return {
                    'status': 'enqueued',
                    'discarded_event': discarded.id
                }
            else:
                # No hay eventos de menor prioridad descartables, descartar este
                return {
                    'status': 'discarded',
                    'reason': 'Cola llena - evento descartable sin eventos de menor prioridad'
                }
        else:
            # El nuevo evento NO es descartable
            # Intentar descartar un evento de menor prioridad que SÍ sea descartable
            discarded = EventDispatcher._try_discard_lower_priority(service, config.priority)

            if discarded:
                # Se descartó un evento descartable de menor prioridad
                EventDispatcher._enqueue_event(live_event, config)
                return {
                    'status': 'enqueued',
                    'discarded_event': discarded.id
                }
            else:
                # No se puede descartar nada, cola llena con eventos importantes
                return {
                    'status': 'queue_full',
                    'reason': 'Cola llena con eventos no descartables de mayor o igual prioridad'
                }

    @staticmethod
    def _enqueue_event(live_event, config):
        """
        Encola un evento en la cola del servicio

        Args:
            live_event: El evento a encolar
            config: ServiceEventConfig con la configuración
        """
        EventQueue.objects.create(
            service=config.service,
            live_event=live_event,
            session=live_event.session,
            priority=config.priority,
            is_async=config.is_async,
            status='pending'
        )

    @staticmethod
    def _try_discard_lower_priority(service, new_priority):
        """
        Intenta descartar un evento de menor prioridad que sea descartable

        Args:
            service: El servicio cuya cola revisar
            new_priority: Prioridad del nuevo evento

        Returns:
            EventQueue o None: El evento descartado o None si no se pudo descartar
        """
        # Buscar el evento descartable de menor prioridad
        # Ordenar por: prioridad ascendente (menor primero), luego por antiguedad (más viejo primero)
        event_to_discard = EventQueue.objects.filter(
            service=service,
            status='pending'
        ).select_related('live_event').order_by('priority', 'created_at').first()

        if event_to_discard:
            # Verificar que sea descartable
            event_config = ServiceEventConfig.objects.filter(
                service=service,
                event_type=event_to_discard.live_event.event_type
            ).first()

            if event_config and event_config.is_discardable:
                # Verificar que tenga menor prioridad que el nuevo evento
                if event_to_discard.priority < new_priority:
                    # Marcar como descartado
                    event_to_discard.mark_discarded()
                    return event_to_discard

        return None
