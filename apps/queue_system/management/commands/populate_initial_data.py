from django.core.management.base import BaseCommand
from apps.queue_system.models import Service, ServiceEventConfig
from apps.app_config.models import Config


class Command(BaseCommand):
    help = 'Popula datos iniciales: Config de tiktok_user y servicios DinoChrome y Overlays'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando población de datos iniciales...'))

        # 1. Crear config de tiktok_user
        self.stdout.write('\n📝 Creando configuración de tiktok_user...')
        config, created = Config.objects.get_or_create(
            meta_key='tiktok_user',
            defaults={'meta_value': ''}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "tiktok_user" creada'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Config "tiktok_user" ya existe'))

        # Crear config de elevenlabs_api
        self.stdout.write('\n🔑 Creando configuración de elevenlabs_api...')
        config, created = Config.objects.get_or_create(
            meta_key='elevenlabs_api',
            defaults={'meta_value': ''}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "elevenlabs_api" creada'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Config "elevenlabs_api" ya existe'))

        # Crear config de llm_url
        self.stdout.write('\n🤖 Creando configuración de llm_url...')
        config, created = Config.objects.get_or_create(
            meta_key='llm_url',
            defaults={'meta_value': 'https://api.deepseek.com/chat/completions'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "llm_url" creada'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Config "llm_url" ya existe'))

        # Crear config de llm_key
        self.stdout.write('\n🔑 Creando configuración de llm_key...')
        config, created = Config.objects.get_or_create(
            meta_key='llm_key',
            defaults={'meta_value': ''}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "llm_key" creada'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Config "llm_key" ya existe'))

        # Crear config de llm_model
        self.stdout.write('\n🧠 Creando configuración de llm_model...')
        config, created = Config.objects.get_or_create(
            meta_key='llm_model',
            defaults={'meta_value': 'deepseek-chat'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "llm_model" creada'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Config "llm_model" ya existe'))

        # Crear config de llm_system_prompt
        self.stdout.write('\n💬 Creando configuración de llm_system_prompt...')
        config, created = Config.objects.get_or_create(
            meta_key='llm_system_prompt',
            defaults={'meta_value': 'You are a helpful assistant for a TikTok Live streaming system. Generate brief, friendly responses to viewer interactions.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Config "llm_system_prompt" creada'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Config "llm_system_prompt" ya existe'))

        # 2. Crear servicio DinoChrome
        self.stdout.write('\n🦖 Creando servicio DinoChrome...')
        dinochrome, created = Service.objects.get_or_create(
            slug='dinochrome',
            defaults={
                'name': 'DinoChrome',
                'service_class': 'apps.services.dinochrome.DinoChromeService.DinoChromeService',
                'description': 'Servicio que controla Chrome para interacciones con el navegador',
                'is_active': True,
                'max_queue_size': 50
            }
        )

        # Actualizar service_class si ya existe pero tiene el valor antiguo
        if not created and dinochrome.service_class != 'apps.services.dinochrome.DinoChromeService.DinoChromeService':
            dinochrome.service_class = 'apps.services.dinochrome.DinoChromeService.DinoChromeService'
            dinochrome.save()
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Servicio DinoChrome creado'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Servicio DinoChrome ya existe'))

        # Configuraciones de eventos para DinoChrome (SYNC para la mayoría)
        dinochrome_configs = [
            {
                'event_type': 'GiftEvent',
                'is_enabled': True,
                'priority': 10,  # Máxima prioridad
                'is_async': False,  # SYNC
                'is_discardable': False  # Nunca descartar regalos
            },
            {
                'event_type': 'CommentEvent',
                'is_enabled': True,
                'priority': 6,
                'is_async': False,  # SYNC
                'is_discardable': True
            },
            {
                'event_type': 'LikeEvent',
                'is_enabled': True,
                'priority': 3,
                'is_async': False,  # SYNC
                'is_discardable': True
            },
            {
                'event_type': 'ShareEvent',
                'is_enabled': True,
                'priority': 7,
                'is_async': False,  # SYNC
                'is_discardable': False
            },
            {
                'event_type': 'FollowEvent',
                'is_enabled': True,
                'priority': 8,
                'is_async': False,  # SYNC
                'is_discardable': False
            },
            {
                'event_type': 'JoinEvent',
                'is_enabled': False,  # Deshabilitado
                'priority': 2,
                'is_async': False,
                'is_discardable': True
            },
            {
                'event_type': 'SubscribeEvent',
                'is_enabled': True,
                'priority': 9,
                'is_async': False,  # SYNC
                'is_discardable': False
            },
        ]

        self.stdout.write('  📋 Configurando eventos para DinoChrome...')
        for config_data in dinochrome_configs:
            config, created = ServiceEventConfig.objects.get_or_create(
                service=dinochrome,
                event_type=config_data['event_type'],
                defaults=config_data
            )
            mode = 'ASYNC' if config_data['is_async'] else 'SYNC'
            status = '✅' if config_data['is_enabled'] else '❌'
            if created:
                self.stdout.write(f'    {status} {config_data["event_type"]} (P:{config_data["priority"]}, {mode})')

        # 3. Crear servicio Overlays
        self.stdout.write('\n🎨 Creando servicio Overlays...')
        overlays, created = Service.objects.get_or_create(
            slug='overlays',
            defaults={
                'name': 'Overlays',
                'service_class': 'apps.services.overlays.services.OverlaysService',
                'description': 'Servicio que maneja overlays visuales en OBS/streaming',
                'is_active': True,
                'max_queue_size': 100
            }
        )

        # Actualizar service_class si ya existe pero tiene el valor antiguo
        if not created and overlays.service_class != 'apps.services.overlays.services.OverlaysService':
            overlays.service_class = 'apps.services.overlays.services.OverlaysService'
            overlays.save()
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Servicio Overlays creado'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Servicio Overlays ya existe'))

        # Configuraciones de eventos para Overlays (TODOS ASYNC)
        overlays_configs = [
            {
                'event_type': 'GiftEvent',
                'is_enabled': True,
                'priority': 10,
                'is_async': True,  # ASYNC
                'is_discardable': False
            },
            {
                'event_type': 'CommentEvent',
                'is_enabled': True,
                'priority': 5,
                'is_async': True,  # ASYNC
                'is_discardable': True
            },
            {
                'event_type': 'LikeEvent',
                'is_enabled': True,
                'priority': 2,
                'is_async': True,  # ASYNC
                'is_discardable': True
            },
            {
                'event_type': 'ShareEvent',
                'is_enabled': True,
                'priority': 6,
                'is_async': True,  # ASYNC
                'is_discardable': True
            },
            {
                'event_type': 'FollowEvent',
                'is_enabled': True,
                'priority': 7,
                'is_async': True,  # ASYNC
                'is_discardable': False
            },
            {
                'event_type': 'JoinEvent',
                'is_enabled': True,
                'priority': 3,
                'is_async': True,  # ASYNC
                'is_discardable': True
            },
            {
                'event_type': 'SubscribeEvent',
                'is_enabled': True,
                'priority': 8,
                'is_async': True,  # ASYNC
                'is_discardable': False
            },
        ]

        self.stdout.write('  📋 Configurando eventos para Overlays...')
        for config_data in overlays_configs:
            config, created = ServiceEventConfig.objects.get_or_create(
                service=overlays,
                event_type=config_data['event_type'],
                defaults=config_data
            )
            mode = 'ASYNC' if config_data['is_async'] else 'SYNC'
            status = '✅' if config_data['is_enabled'] else '❌'
            if created:
                self.stdout.write(f'    {status} {config_data["event_type"]} (P:{config_data["priority"]}, {mode})')

        # Resumen final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Población de datos completada exitosamente!'))
        self.stdout.write('='*60)
        self.stdout.write('\n📊 Resumen:')
        self.stdout.write(f'  • Config: 6 registros (tiktok_user, elevenlabs_api, llm_url, llm_key, llm_model, llm_system_prompt)')
        self.stdout.write(f'  • Servicios: 2 (DinoChrome, Overlays)')
        self.stdout.write(f'  • DinoChrome: {ServiceEventConfig.objects.filter(service=dinochrome).count()} configuraciones de eventos (SYNC)')
        self.stdout.write(f'  • Overlays: {ServiceEventConfig.objects.filter(service=overlays).count()} configuraciones de eventos (ASYNC)')
        self.stdout.write('\n💡 Puedes ver la configuración en el admin de Django')
        self.stdout.write('')
