from django.core.management.base import BaseCommand
from apps.queue_system.models import Service, ServiceEventConfig


class Command(BaseCommand):
    help = 'Agrega el servicio Music al proyecto existente'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎵 Agregando servicio Music...'))

        # Crear servicio Music
        music, created = Service.objects.get_or_create(
            slug='music',
            defaults={
                'name': 'Music',
                'service_class': 'apps.services.music.services.MusicService',
                'description': 'Servicio de reproduccion de musica local (MP3s desde media/music/). Gift GG salta a la siguiente cancion.',
                'is_active': True,
                'max_queue_size': 30
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Servicio Music creado'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Servicio Music ya existe'))

        # Configuraciones de eventos para Music (solo GiftEvent)
        config, created = ServiceEventConfig.objects.get_or_create(
            service=music,
            event_type='GiftEvent',
            defaults={
                'is_enabled': True,
                'priority': 9,
                'is_async': False,
                'is_discardable': False
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ GiftEvent configurado (P:9, SYNC)'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  GiftEvent ya existe'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Servicio Music configurado!'))
        self.stdout.write('  • Coloca MP3s en media/music/')
        self.stdout.write('  • Gift "GG" salta a la siguiente cancion')
        self.stdout.write('  • Reproduccion automatica continua')
