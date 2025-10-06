from django.core.management.base import BaseCommand
from apps.queue_system.models import Service, ServiceEventConfig
from apps.app_config.models import Config


class Command(BaseCommand):
    help = 'Agrega el servicio Music al proyecto existente'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎵 Agregando servicio Music...'))

        # Crear servicio Music
        self.stdout.write('\n🎵 Creando servicio Music...')
        music, created = Service.objects.get_or_create(
            slug='music',
            defaults={
                'name': 'Music',
                'service_class': 'apps.services.music.services.MusicService',
                'description': 'Servicio de reproduccion de musica desde YouTube con sistema de creditos',
                'is_active': True,
                'max_queue_size': 30
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Servicio Music creado'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Servicio Music ya existe'))

        # Crear configs para Music
        self.stdout.write('\n🎵 Creando configuracion de music_gift_name...')
        config, created = Config.objects.get_or_create(
            meta_key='music_gift_name',
            defaults={'meta_value': 'rosa'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "music_gift_name" creada (valor: rosa)'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Config "music_gift_name" ya existe (valor actual: {config.meta_value})'))

        self.stdout.write('\n⏱️  Creando configuracion de music_max_duration...')
        config, created = Config.objects.get_or_create(
            meta_key='music_max_duration',
            defaults={'meta_value': '300'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "music_max_duration" creada (valor: 300 segundos)'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Config "music_max_duration" ya existe (valor actual: {config.meta_value})'))

        # Configuraciones de eventos para Music
        music_configs = [
            {
                'event_type': 'GiftEvent',
                'is_enabled': True,
                'priority': 9,
                'is_async': False,
                'is_discardable': False
            },
            {
                'event_type': 'CommentEvent',
                'is_enabled': True,
                'priority': 7,
                'is_async': False,
                'is_discardable': True
            },
        ]

        self.stdout.write('\n📋 Configurando eventos para Music...')
        for config_data in music_configs:
            config, created = ServiceEventConfig.objects.get_or_create(
                service=music,
                event_type=config_data['event_type'],
                defaults=config_data
            )
            mode = 'ASYNC' if config_data['is_async'] else 'SYNC'
            status = '✅' if config_data['is_enabled'] else '❌'
            if created:
                self.stdout.write(f'  {status} {config_data["event_type"]} (P:{config_data["priority"]}, {mode})')
            else:
                self.stdout.write(f'  ⚠️  {config_data["event_type"]} ya existe')

        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Servicio Music agregado exitosamente!'))
        self.stdout.write('='*60)
        self.stdout.write('\n📊 Configuracion:')
        self.stdout.write(f'  • Servicio: Music (slug: music)')
        self.stdout.write(f'  • Clase: apps.services.music.services.MusicService')
        self.stdout.write(f'  • Max queue size: 30')
        self.stdout.write(f'  • Eventos configurados: {ServiceEventConfig.objects.filter(service=music).count()}')
        self.stdout.write('\n🎮 Como usar:')
        self.stdout.write('  1. Los usuarios deben enviar el regalo configurado (default: rosa)')
        self.stdout.write('  2. Cada regalo da 1 credito (rachas cuentan multiple)')
        self.stdout.write('  3. Usar comando: !cancion <nombre de la cancion>')
        self.stdout.write('  4. La cancion se reproduce inmediatamente')
        self.stdout.write('\n⚙️  Configuracion adicional:')
        self.stdout.write('  • Cambiar regalo: Editar "music_gift_name" en Config')
        self.stdout.write('  • Cambiar duracion max: Editar "music_max_duration" en Config (segundos)')
        self.stdout.write('')
