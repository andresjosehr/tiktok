from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tiktok_events', '0003_livesession_liveevent_session_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TikTokAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de última actualización')),
                ('unique_id', models.CharField(help_text='@username de TikTok', max_length=255, unique=True)),
                ('nickname', models.CharField(blank=True, help_text='Nombre visible de la cuenta', max_length=255)),
                ('tiktok_user_id', models.BigIntegerField(blank=True, help_text='ID numérico de TikTok', null=True)),
                ('country', models.CharField(help_text='Código de país ISO (US, UK, DE, SA, MX...)', max_length=2)),
                ('region', models.CharField(blank=True, help_text='Región específica (New York, London...)', max_length=255)),
                ('language', models.CharField(default='en', help_text='Idioma del contenido', max_length=10)),
                ('is_active', models.BooleanField(default=True, help_text='Si la cuenta está activa para hacer lives')),
                ('can_go_live', models.BooleanField(default=True, help_text='Si tiene permiso para hacer live')),
                ('follower_count', models.IntegerField(default=0, help_text='Cantidad de seguidores')),
                ('agency_name', models.CharField(blank=True, help_text='Nombre de la agencia/creator network', max_length=255)),
                ('has_stream_key', models.BooleanField(default=False, help_text='Si tiene acceso a stream key via agencia')),
                ('proxy_host', models.CharField(blank=True, help_text='Host del proxy asignado', max_length=255)),
                ('proxy_type', models.CharField(blank=True, help_text='Tipo: residential, 4g, 5g, etc.', max_length=50)),
                ('purchase_price', models.DecimalField(decimal_places=2, default=0, help_text='Costo de compra de la cuenta (USD)', max_digits=10)),
                ('purchase_date', models.DateField(blank=True, help_text='Fecha de compra', null=True)),
                ('notes', models.TextField(blank=True, help_text='Notas sobre esta cuenta')),
            ],
            options={
                'verbose_name': 'TikTok Account',
                'verbose_name_plural': 'TikTok Accounts',
                'db_table': 'tiktok_accounts',
                'ordering': ['country', 'unique_id'],
            },
        ),
        migrations.AddField(
            model_name='livesession',
            name='account',
            field=models.ForeignKey(
                blank=True,
                help_text='Cuenta de TikTok utilizada en esta sesión',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='sessions',
                to='tiktok_events.tiktokaccount',
            ),
        ),
        migrations.AddField(
            model_name='livesession',
            name='game_type',
            field=models.CharField(blank=True, default='', help_text='Juego/servicio activo (dinochrome, slot_machine, etc.)', max_length=100),
            preserve_default=False,
        ),
    ]
