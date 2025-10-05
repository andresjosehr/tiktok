from django.db import models


class BaseModel(models.Model):
    """
    Modelo base abstracto con timestamps automáticos
    Todos los modelos deben heredar de este
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización")

    class Meta:
        abstract = True
