"""
Comando para actualizar la configuración del LLM
"""
from django.core.management.base import BaseCommand
from apps.app_config.models import Config


class Command(BaseCommand):
    help = 'Actualiza la configuración del LLM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Modelo a usar (ej: llama-3.3-70b-versatile)',
        )
        parser.add_argument(
            '--url',
            type=str,
            help='URL del endpoint (ej: https://api.groq.com/openai/v1/chat/completions)',
        )
        parser.add_argument(
            '--key',
            type=str,
            help='API key',
        )
        parser.add_argument(
            '--show',
            action='store_true',
            help='Mostrar configuración actual',
        )

    def handle(self, *args, **options):
        if options['show']:
            self.show_config()
            return

        updated = []

        if options['model']:
            config, _ = Config.objects.get_or_create(meta_key='llm_model')
            config.meta_value = options['model']
            config.save()
            updated.append(f"modelo → {options['model']}")

        if options['url']:
            config, _ = Config.objects.get_or_create(meta_key='llm_url')
            config.meta_value = options['url']
            config.save()
            updated.append(f"URL → {options['url']}")

        if options['key']:
            config, _ = Config.objects.get_or_create(meta_key='llm_key')
            config.meta_value = options['key']
            config.save()
            key_display = f"***{options['key'][-4:]}" if len(options['key']) >= 4 else "****"
            updated.append(f"API key → {key_display}")

        if updated:
            self.stdout.write(self.style.SUCCESS(f"✅ Configuración actualizada:"))
            for item in updated:
                self.stdout.write(f"   - {item}")
            self.stdout.write("\n")
            self.show_config()
        else:
            self.stdout.write(self.style.WARNING("⚠️  No se especificaron opciones para actualizar"))
            self.stdout.write("Usa --help para ver las opciones disponibles\n")
            self.show_config()

    def show_config(self):
        """Muestra la configuración actual"""
        self.stdout.write(self.style.SUCCESS("📋 Configuración actual del LLM:"))

        configs = {
            'llm_url': 'URL',
            'llm_key': 'API Key',
            'llm_model': 'Modelo',
            'llm_system_prompt': 'System Prompt'
        }

        for key, label in configs.items():
            try:
                config = Config.objects.get(meta_key=key)
                value = config.meta_value

                # Ocultar API key
                if key == 'llm_key' and value:
                    value = f"***{value[-4:]}" if len(value) >= 4 else "****"

                # Truncar system prompt
                if key == 'llm_system_prompt' and value and len(value) > 60:
                    value = value[:60] + "..."

                self.stdout.write(f"   {label}: {value or '(vacío)'}")
            except Config.DoesNotExist:
                self.stdout.write(f"   {label}: (no configurado)")
