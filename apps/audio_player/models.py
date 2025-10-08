from django.db import models


class CurrentAudio(models.Model):
    """Modelo para almacenar audios reproduciéndose en diferentes canales"""

    CHANNEL_MUSIC = 'music'
    CHANNEL_VOICE = 'voice'

    CHANNEL_CHOICES = [
        (CHANNEL_MUSIC, 'Música de fondo'),
        (CHANNEL_VOICE, 'Voz/Efectos'),
    ]

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, unique=True)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    timestamp = models.FloatField(null=True, blank=True)
    playing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Audio Actual"
        verbose_name_plural = "Audios Actuales"

    def __str__(self):
        return f"{self.channel}: {self.file_path or 'None'}"

    @classmethod
    def get_current(cls, channel='voice'):
        """Obtiene o crea la instancia para un canal específico"""
        obj, created = cls.objects.get_or_create(channel=channel)
        return obj

    @classmethod
    def set_current(cls, file_path, channel='voice'):
        """Establece el audio actual para un canal específico"""
        import time
        obj = cls.get_current(channel=channel)
        obj.file_path = file_path
        obj.timestamp = time.time()
        obj.playing = True
        obj.save()
        print(f"[AUDIO_PLAYER] Nuevo audio establecido en canal '{channel}': {file_path}")
        return obj
