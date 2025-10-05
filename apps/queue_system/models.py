from django.db import models
from django.utils import timezone
from apps.base_models import BaseModel


class Service(BaseModel):
    """
    Modelo para definir servicios que procesan eventos
    Ejemplos: OBS Overlay, Chrome Control, GMod Integration
    """

    # Identificación
    name = models.CharField(max_length=255, help_text="Nombre descriptivo del servicio")
    slug = models.SlugField(max_length=100, unique=True, db_index=True, help_text="Identificador único del servicio")
    service_class = models.CharField(
        max_length=500,
        help_text="Ruta completa de la clase Python (ej: apps.obs_overlay.services.OBSOverlayService)"
    )
    description = models.TextField(null=True, blank=True, help_text="Descripción del servicio")

    # Configuración
    is_active = models.BooleanField(default=True, db_index=True, help_text="Si el servicio está activo")
    max_queue_size = models.IntegerField(default=100, help_text="Tamaño máximo de la cola de eventos")

    class Meta:
        db_table = 'services'
        ordering = ['name']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name}"

    def get_pending_count(self):
        """Retorna el número de eventos pendientes en la cola"""
        return self.queue_items.filter(status='pending').count()

    def get_processing_count(self):
        """Retorna el número de eventos en procesamiento"""
        return self.queue_items.filter(status='processing').count()


class ServiceEventConfig(BaseModel):
    """
    Configuración de qué eventos procesa cada servicio y cómo
    """

    # Relaciones
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='event_configs',
        help_text="Servicio al que pertenece esta configuración"
    )

    # Tipo de evento
    EVENT_TYPE_CHOICES = [
        ('CommentEvent', 'Comment Event'),
        ('GiftEvent', 'Gift Event'),
        ('LikeEvent', 'Like Event'),
        ('ShareEvent', 'Share Event'),
        ('FollowEvent', 'Follow Event'),
        ('JoinEvent', 'Join Event'),
        ('SubscribeEvent', 'Subscribe Event'),
    ]
    event_type = models.CharField(
        max_length=100,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
        help_text="Tipo de evento que se procesará"
    )

    # Configuración
    is_enabled = models.BooleanField(default=True, help_text="Si este tipo de evento está habilitado para procesarse")
    priority = models.IntegerField(
        default=5,
        help_text="Prioridad del evento (1-10, donde 10 es máxima prioridad)"
    )
    is_async = models.BooleanField(
        default=False,
        help_text="Si este tipo de evento puede procesarse en paralelo (async) o debe esperar (sync)"
    )
    is_discardable = models.BooleanField(
        default=True,
        help_text="Si este evento puede descartarse cuando la cola está llena"
    )

    class Meta:
        db_table = 'service_event_configs'
        unique_together = ['service', 'event_type']
        ordering = ['-priority', 'event_type']
        verbose_name = 'Service Event Configuration'
        verbose_name_plural = 'Service Event Configurations'
        indexes = [
            models.Index(fields=['service', 'event_type', 'is_enabled']),
        ]

    def __str__(self):
        status = "✅" if self.is_enabled else "❌"
        async_mode = "ASYNC" if self.is_async else "SYNC"
        return f"{status} {self.service.name} - {self.event_type} (P:{self.priority}, {async_mode})"


class EventQueue(BaseModel):
    """
    Cola de eventos pendientes de procesar por cada servicio
    """

    # Relaciones
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='queue_items',
        db_index=True,
        help_text="Servicio que procesará este evento"
    )
    live_event = models.ForeignKey(
        'tiktok_events.LiveEvent',
        on_delete=models.CASCADE,
        related_name='queue_items',
        help_text="Evento de TikTok a procesar"
    )
    session = models.ForeignKey(
        'tiktok_events.LiveSession',
        on_delete=models.CASCADE,
        related_name='queue_items',
        null=True,
        blank=True,
        help_text="Sesión a la que pertenece el evento"
    )

    # Estado
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('discarded', 'Discarded'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Estado del evento en la cola"
    )

    # Configuración (copiada de ServiceEventConfig al encolar)
    priority = models.IntegerField(help_text="Prioridad del evento (copiada de la configuración)")
    is_async = models.BooleanField(help_text="Si debe procesarse async (copiada de la configuración)")

    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True, help_text="Momento en que se procesó el evento")

    class Meta:
        db_table = 'event_queue'
        ordering = ['-priority', 'created_at']
        verbose_name = 'Event Queue Item'
        verbose_name_plural = 'Event Queue'
        indexes = [
            models.Index(fields=['service', 'status', '-priority', 'created_at']),
            models.Index(fields=['service', 'status']),
            models.Index(fields=['live_event']),
        ]

    def __str__(self):
        return f"{self.service.name} - {self.live_event.event_type} [{self.status}] (P:{self.priority})"

    def mark_processing(self):
        """Marca el evento como en procesamiento"""
        self.status = 'processing'
        self.save(update_fields=['status'])

    def mark_completed(self):
        """Marca el evento como completado"""
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def mark_failed(self):
        """Marca el evento como fallido"""
        self.status = 'failed'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def mark_discarded(self):
        """Marca el evento como descartado"""
        self.status = 'discarded'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])
