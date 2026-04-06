from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MusicHistory',
        ),
        migrations.DeleteModel(
            name='MusicCredit',
        ),
    ]
