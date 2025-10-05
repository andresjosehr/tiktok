from django.db import models
from apps.base_models import BaseModel


class Config(BaseModel):
    """
    Modelo para almacenar configuraciones clave-valor de la aplicación
    """
    meta_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Clave de configuración única"
    )
    meta_value = models.TextField(
        help_text="Valor de la configuración (puede ser JSON, texto, etc.)"
    )

    class Meta:
        db_table = 'app_config'
        ordering = ['meta_key']
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'

    def __str__(self):
        return f"{self.meta_key}: {self.meta_value[:50]}..."

    @classmethod
    def get_value(cls, key, default=None):
        """Obtiene el valor de una configuración"""
        try:
            config = cls.objects.get(meta_key=key)
            return config.meta_value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, key, value):
        """Establece o actualiza el valor de una configuración"""
        config, created = cls.objects.update_or_create(
            meta_key=key,
            defaults={'meta_value': value}
        )
        return config
