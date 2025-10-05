from django.apps import AppConfig


class LlmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations.llm'
    verbose_name = 'LLM Integration'
