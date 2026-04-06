"""
Django command para descargar la musica de Epidemic Sound desde Google Drive.
Uso: python manage.py download_music
"""

import os
import gdown
from django.conf import settings
from django.core.management.base import BaseCommand


GOOGLE_DRIVE_FOLDER_ID = '1IF27NKGMKl2izgZXjYNtLtpUfhi0h8UC'
GOOGLE_DRIVE_URL = f'https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}'


class Command(BaseCommand):
    help = 'Descarga la musica de Epidemic Sound desde Google Drive a media/music/'

    def handle(self, *args, **options):
        music_dir = os.path.join(settings.MEDIA_ROOT, 'music')
        os.makedirs(music_dir, exist_ok=True)

        existing = sum(1 for f in os.listdir(music_dir) if f.endswith('.mp3'))
        self.stdout.write(f'Tracks existentes en media/music/: {existing}')
        self.stdout.write(f'Descargando desde Google Drive...\n')

        gdown.download_folder(
            url=GOOGLE_DRIVE_URL,
            output=music_dir,
            quiet=False,
            use_cookies=False,
        )

        total = sum(1 for f in os.listdir(music_dir) if f.endswith('.mp3'))
        new = total - existing
        self.stdout.write(self.style.SUCCESS(f'\n{new} tracks nuevos descargados'))
        self.stdout.write(self.style.SUCCESS(f'Total tracks en media/music/: {total}'))
