from django.db import migrations


def create_tugofwar_service(apps, schema_editor):
    Service = apps.get_model('queue_system', 'Service')
    ServiceEventConfig = apps.get_model('queue_system', 'ServiceEventConfig')

    service, _ = Service.objects.get_or_create(
        slug='tugofwar',
        defaults={
            'name': 'Tug of War',
            'service_class': 'apps.services.tugofwar.TugOfWarService.TugOfWarService',
            'description': 'Juego interactivo Tug of War - regalos de TikTok mueven la barra',
            'is_active': True,
            'max_queue_size': 100,
        }
    )

    ServiceEventConfig.objects.get_or_create(
        service=service,
        event_type='GiftEvent',
        defaults={
            'is_enabled': True,
            'priority': 10,
            'is_async': True,
            'is_discardable': False,
            'is_stackable': True,
        }
    )

    # Desactivar DinoChrome, Overlays y Music
    Service.objects.filter(
        slug__in=['dinochrome', 'overlays', 'music']
    ).update(is_active=False)


def reverse_tugofwar_service(apps, schema_editor):
    Service = apps.get_model('queue_system', 'Service')
    ServiceEventConfig = apps.get_model('queue_system', 'ServiceEventConfig')

    ServiceEventConfig.objects.filter(service__slug='tugofwar').delete()
    Service.objects.filter(slug='tugofwar').delete()

    # Reactivar los servicios anteriores
    Service.objects.filter(
        slug__in=['dinochrome', 'overlays', 'music']
    ).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('queue_system', '0003_service_obs_scene_name'),
    ]

    operations = [
        migrations.RunPython(create_tugofwar_service, reverse_tugofwar_service),
    ]
