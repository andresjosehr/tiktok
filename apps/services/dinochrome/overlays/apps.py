from django.apps import AppConfig


class DinoChromeOverlaysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.services.dinochrome.overlays'
    label = 'dinochrome_overlays'  # Label único para evitar conflicto con 'overlays'
