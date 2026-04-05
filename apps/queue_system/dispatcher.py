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

    # Prioridades por tipo de regalo (mayor número = mayor prioridad)
    # Los regalos no listados usan la prioridad base del ServiceEventConfig
    GIFT_PRIORITIES = {
        # Rosa: LLM + TTS + restart (máxima prioridad)
        'rosa': 10,
        # Rose: TTS corrección
        'rose': 9,
        # GIF bailando
        'ice_cream': 8,
        'ice cream cone': 8,
        'ice cream': 8,
        'cone': 8,
        'awesome': 8,
        "you're awesome": 8,
        'youre awesome': 8,
        'enjoy music': 8,
        'music': 8,
    }

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
            'queue_full': [],
            'skipped': []
        }

        # Log de entrada
        event_info = f"{live_event.event_type} de @{live_event.user_nickname}"
        if live_event.event_type == 'GiftEvent':
            gift_name = EventDispatcher._get_gift_name(live_event)
            if gift_name:
                event_info = f"GiftEvent[{gift_name}] de @{live_event.user_nickname}"
        elif live_event.event_type == 'CommentEvent':
            comment = live_event.event_data.get('comment', '')[:30]
            event_info = f"CommentEvent['{comment}'] de @{live_event.user_nickname}"

        print(f"[DISPATCHER] ━━━ Distribuyendo: {event_info}")

        # 1. Obtener servicios activos suscritos a este tipo de evento
        configs = ServiceEventConfig.objects.filter(
            service__is_active=True,
            event_type=live_event.event_type,
            is_enabled=True
        ).select_related('service')

        if not configs.exists():
            print(f"[DISPATCHER] ⚠️  Sin servicios suscritos a {live_event.event_type}")
            return results

        # 2. Procesar cada configuración
        for config in configs:
            result = EventDispatcher._process_service_queue(live_event, config)
            service_name = config.service.name

            if result['status'] == 'enqueued':
                priority = result.get('priority', config.priority)
                results['enqueued'].append({
                    'service': service_name,
                    'priority': priority
                })
                # Log detallado
                queue_size = EventQueue.objects.filter(
                    service=config.service, status='pending'
                ).count()
                discarded_info = ""
                if result.get('discarded_event'):
                    discarded_info = f" (descartó evento #{result['discarded_event']})"
                print(f"[DISPATCHER] ✅ {service_name}: Encolado P:{priority} | Cola: {queue_size}/{config.service.max_queue_size}{discarded_info}")

            elif result['status'] == 'skipped':
                results['skipped'].append({
                    'service': service_name,
                    'reason': result.get('reason', 'Unknown')
                })
                print(f"[DISPATCHER] ⏭️  {service_name}: Saltado - {result.get('reason', 'racha en curso')}")

            elif result['status'] == 'discarded':
                results['discarded'].append({
                    'service': service_name,
                    'reason': result.get('reason', 'Unknown')
                })
                print(f"[DISPATCHER] 🗑️  {service_name}: Descartado - {result.get('reason', 'cola llena')}")

            elif result['status'] == 'queue_full':
                results['queue_full'].append({
                    'service': service_name,
                    'reason': 'Cola llena sin eventos descartables'
                })
                print(f"[DISPATCHER] 🔴 {service_name}: Cola llena ({config.service.max_queue_size}/{config.service.max_queue_size})")

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
                    'reason': f'Racha en curso (status={live_event.streak_status})'
                }

        # 2. Calcular prioridad efectiva (considerando tipo de regalo)
        effective_priority = config.priority
        if live_event.event_type == 'GiftEvent':
            gift_name = EventDispatcher._get_gift_name(live_event)
            if gift_name:
                gift_priority = EventDispatcher.GIFT_PRIORITIES.get(gift_name.lower())
                if gift_priority is not None:
                    effective_priority = gift_priority

        # 3. Verificar tamaño de cola
        current_queue_size = EventQueue.objects.filter(
            service=service,
            status='pending'
        ).count()

        # 4. Si hay espacio, encolar directamente
        if current_queue_size < service.max_queue_size:
            EventDispatcher._enqueue_event(live_event, config)
            return {'status': 'enqueued', 'priority': effective_priority}

        # 5. Cola llena - intentar descartar eventos de menor prioridad
        if config.is_discardable:
            # El nuevo evento es descartable
            # Intentar encontrar un evento descartable de menor prioridad
            discarded = EventDispatcher._try_discard_lower_priority(service, effective_priority)

            if discarded:
                # Se descartó un evento de menor prioridad, encolar el nuevo
                EventDispatcher._enqueue_event(live_event, config)
                return {
                    'status': 'enqueued',
                    'priority': effective_priority,
                    'discarded_event': discarded.id
                }
            else:
                # No hay eventos de menor prioridad descartables, descartar este
                return {
                    'status': 'discarded',
                    'reason': f'Cola llena, sin eventos P<{effective_priority} descartables'
                }
        else:
            # El nuevo evento NO es descartable
            # Intentar descartar un evento de menor prioridad que SÍ sea descartable
            discarded = EventDispatcher._try_discard_lower_priority(service, effective_priority)

            if discarded:
                # Se descartó un evento descartable de menor prioridad
                EventDispatcher._enqueue_event(live_event, config)
                return {
                    'status': 'enqueued',
                    'priority': effective_priority,
                    'discarded_event': discarded.id
                }
            else:
                # No se puede descartar nada, cola llena con eventos importantes
                return {
                    'status': 'queue_full',
                    'reason': f'Cola llena ({current_queue_size}/{service.max_queue_size}), evento no descartable'
                }

    @staticmethod
    def _enqueue_event(live_event, config):
        """
        Encola un evento en la cola del servicio

        Args:
            live_event: El evento a encolar
            config: ServiceEventConfig con la configuración
        """
        # Determinar prioridad (puede ser sobrescrita por tipo de regalo)
        priority = config.priority
        gift_name = None

        # Para GiftEvent, verificar si hay prioridad específica por regalo
        if live_event.event_type == 'GiftEvent':
            gift_name = EventDispatcher._get_gift_name(live_event)
            if gift_name:
                gift_priority = EventDispatcher.GIFT_PRIORITIES.get(gift_name.lower())
                if gift_priority is not None:
                    priority = gift_priority

        EventQueue.objects.create(
            service=config.service,
            live_event=live_event,
            session=live_event.session,
            priority=priority,
            is_async=config.is_async,
            status='pending'
        )

    @staticmethod
    def _get_gift_name(live_event):
        """
        Extrae el nombre del regalo de event_data

        Args:
            live_event: El evento con los datos del regalo

        Returns:
            str o None: Nombre del regalo o None si no se encuentra
        """
        try:
            event_data = live_event.event_data
            if isinstance(event_data, dict):
                # Estructura: event_data['gift']['name']
                gift = event_data.get('gift', {})
                if isinstance(gift, dict):
                    return gift.get('name')
        except Exception:
            pass
        return None

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
                    print(f"[DISPATCHER] 🗑️  Descartado evento P:{event_to_discard.priority} para hacer espacio a P:{new_priority}")
                    return event_to_discard

        return None
