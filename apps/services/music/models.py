from django.db import models
from django.utils import timezone
from apps.base_models import BaseModel


class MusicCredit(BaseModel):
    """
    Modelo para trackear creditos de musica por usuario
    Los creditos se ganan enviando regalos especificos
    """

    # Relacion con sesion (se resetea cuando termina el live)
    session = models.ForeignKey(
        'tiktok_events.LiveSession',
        on_delete=models.CASCADE,
        related_name='music_credits',
        db_index=True,
        help_text="Sesion del live"
    )

    # Usuario
    username = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Username del usuario en TikTok"
    )

    # Contadores
    total_gifts = models.IntegerField(
        default=0,
        help_text="Total de regalos validos enviados (incluyendo rachas)"
    )
    credits_used = models.IntegerField(
        default=0,
        help_text="Creditos ya utilizados"
    )

    # Timestamps
    last_gift_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Ultima vez que envio un regalo valido"
    )
    last_request_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Ultima vez que pidio una cancion"
    )

    class Meta:
        db_table = 'music_credits'
        unique_together = ['session', 'username']
        ordering = ['-total_gifts']
        verbose_name = 'Music Credit'
        verbose_name_plural = 'Music Credits'
        indexes = [
            models.Index(fields=['session', 'username']),
            models.Index(fields=['session', '-total_gifts']),
        ]

    def __str__(self):
        return f"{self.username} - {self.credits_available}/{self.total_gifts} creditos"

    @property
    def credits_available(self):
        """Calcula creditos disponibles"""
        return max(0, self.total_gifts - self.credits_used)

    def add_gifts(self, count=1):
        """Agrega regalos (incrementa creditos)"""
        self.total_gifts += count
        self.last_gift_at = timezone.now()
        self.save(update_fields=['total_gifts', 'last_gift_at'])

    def use_credit(self):
        """Usa un credito (retorna True si tenia disponible)"""
        if self.credits_available > 0:
            self.credits_used += 1
            self.last_request_at = timezone.now()
            self.save(update_fields=['credits_used', 'last_request_at'])
            return True
        return False


class MusicHistory(BaseModel):
    """
    Historial de canciones reproducidas
    """

    # Relacion con sesion
    session = models.ForeignKey(
        'tiktok_events.LiveSession',
        on_delete=models.CASCADE,
        related_name='music_history',
        db_index=True,
        help_text="Sesion del live"
    )

    # Usuario que pidio la cancion
    username = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Username que solicito la cancion"
    )

    # Informacion de busqueda
    query = models.CharField(
        max_length=500,
        help_text="Termino de busqueda usado"
    )

    # Informacion del video
    youtube_url = models.URLField(
        max_length=500,
        help_text="URL del video de YouTube"
    )
    youtube_id = models.CharField(
        max_length=50,
        help_text="ID del video de YouTube"
    )
    title = models.CharField(
        max_length=500,
        help_text="Titulo del video"
    )
    duration = models.IntegerField(
        help_text="Duracion en segundos"
    )

    # Archivo descargado
    file_path = models.CharField(
        max_length=500,
        help_text="Ruta del archivo de audio descargado"
    )

    # Control de reproduccion
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Cuando empezo a reproducirse"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuando termino la reproduccion"
    )
    was_interrupted = models.BooleanField(
        default=False,
        help_text="Si fue interrumpida por otra cancion"
    )

    class Meta:
        db_table = 'music_history'
        ordering = ['-started_at']
        verbose_name = 'Music History'
        verbose_name_plural = 'Music History'
        indexes = [
            models.Index(fields=['session', '-started_at']),
            models.Index(fields=['username', '-started_at']),
        ]

    def __str__(self):
        return f"{self.username}: {self.title} ({self.query})"

    def mark_finished(self, interrupted=False):
        """Marca la cancion como terminada"""
        self.finished_at = timezone.now()
        self.was_interrupted = interrupted
        self.save(update_fields=['finished_at', 'was_interrupted'])
