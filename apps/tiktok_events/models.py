from django.db import models
from django.utils import timezone
from apps.base_models import BaseModel


class LiveSession(BaseModel):
    """
    Modelo para agrupar eventos de TikTok Live por sesión de captura
    Una sesión representa un período continuo de recolección de eventos
    """

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('aborted', 'Aborted'),
    ]

    # Identificación
    name = models.CharField(max_length=255, null=True, blank=True, help_text="Nombre opcional de la sesión")

    # Control de tiempo
    started_at = models.DateTimeField(auto_now_add=True, db_index=True, help_text="Inicio de la sesión")
    ended_at = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Fin de la sesión")

    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="Estado de la sesión"
    )

    # Contexto
    room_id = models.BigIntegerField(db_index=True, help_text="ID de la sala/live monitoreada")
    streamer_unique_id = models.CharField(max_length=255, db_index=True, help_text="Username del streamer")

    # Estadísticas (se actualizan conforme se agregan eventos)
    total_events = models.IntegerField(default=0, help_text="Total de eventos capturados")

    # Notas opcionales
    notes = models.TextField(null=True, blank=True, help_text="Notas sobre esta sesión")

    class Meta:
        db_table = 'live_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['room_id', 'started_at']),
            models.Index(fields=['status', 'started_at']),
        ]
        verbose_name = 'Live Session'
        verbose_name_plural = 'Live Sessions'

    def __str__(self):
        duration = self.get_duration_display()
        return f"Session {self.id} - {self.streamer_unique_id} ({duration})"

    def end_session(self, status='completed'):
        """Finaliza la sesión"""
        self.ended_at = timezone.now()
        self.status = status
        self.save(update_fields=['ended_at', 'status'])

    def get_duration(self):
        """Retorna la duración de la sesión en segundos"""
        end_time = self.ended_at or timezone.now()
        return (end_time - self.started_at).total_seconds()

    def get_duration_display(self):
        """Retorna la duración en formato legible"""
        duration = self.get_duration()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        return f"{hours}h {minutes}m"

    def increment_events(self):
        """Incrementa el contador de eventos"""
        self.total_events += 1
        self.save(update_fields=['total_events'])


class LiveEvent(BaseModel):
    """
    Modelo para almacenar todos los eventos de TikTok Live
    Soporta eventos con racha (streaks) como GiftEvent y LikeEvent
    """

    # Choices
    STREAK_STATUS_CHOICES = [
        ('start', 'Start'),
        ('continue', 'Continue'),
        ('end', 'End'),
    ]

    # Relación con sesión
    session = models.ForeignKey(
        LiveSession,
        on_delete=models.CASCADE,
        related_name='events',
        db_index=True,
        null=True,
        blank=True,
        help_text="Sesión a la que pertenece este evento"
    )

    # Identificación del evento
    event_type = models.CharField(max_length=100, db_index=True, help_text="Tipo de evento (CommentEvent, GiftEvent, etc.)")
    timestamp = models.DateTimeField(db_index=True, help_text="Momento del evento")

    # Contexto del live
    room_id = models.BigIntegerField(db_index=True, help_text="ID de la sala/live")
    streamer_unique_id = models.CharField(max_length=255, db_index=True, help_text="Username del streamer")

    # Usuario principal (quien realiza la acción)
    user_id = models.BigIntegerField(db_index=True, null=True, blank=True, help_text="TikTok user ID")
    user_unique_id = models.CharField(max_length=255, db_index=True, null=True, blank=True, help_text="Username del usuario")
    user_nickname = models.CharField(max_length=255, null=True, blank=True, help_text="Nickname del usuario")

    # Control de rachas (streak)
    is_streaking = models.BooleanField(default=False, db_index=True, help_text="Si el evento está en racha activa")
    streak_id = models.CharField(max_length=255, null=True, blank=True, db_index=True, help_text="ID único de la racha")
    streak_status = models.CharField(
        max_length=10,
        choices=STREAK_STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="Estado de la racha: start, continue, end"
    )

    # Datos específicos del evento en JSON
    event_data = models.JSONField(help_text="Toda la información específica del evento en formato JSON")

    class Meta:
        db_table = 'live_events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['room_id', 'timestamp']),
            models.Index(fields=['user_id', 'is_streaking', 'timestamp']),
            models.Index(fields=['event_type', 'room_id']),
            models.Index(fields=['session', 'timestamp']),
        ]
        verbose_name = 'Live Event'
        verbose_name_plural = 'Live Events'

    def __str__(self):
        return f"{self.event_type} - {self.user_unique_id or 'Unknown'} @ {self.timestamp}"

    def is_streak_start(self):
        """Verifica si es el inicio de una racha"""
        return self.streak_status == 'start'

    def is_streak_end(self):
        """Verifica si es el fin de una racha"""
        return self.streak_status == 'end'

    @classmethod
    def get_streak_events(cls, streak_id):
        """Obtiene todos los eventos de una racha específica"""
        return cls.objects.filter(streak_id=streak_id).order_by('timestamp')

    @classmethod
    def get_user_events(cls, user_unique_id, room_id=None):
        """Obtiene todos los eventos de un usuario"""
        queryset = cls.objects.filter(user_unique_id=user_unique_id)
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        return queryset.order_by('timestamp')

    @classmethod
    def get_room_events(cls, room_id, event_type=None):
        """Obtiene todos los eventos de una sala/live"""
        queryset = cls.objects.filter(room_id=room_id)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        return queryset.order_by('timestamp')
