import gzip
import subprocess
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse


def database_backup(request):
    db = settings.DATABASES['default']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if db['ENGINE'] == 'django.db.backends.mysql':
        cmd = [
            'mysqldump',
            '-h', db['HOST'],
            '-P', str(db['PORT']),
            '-u', db['USER'],
            f"--password={db['PASSWORD']}",
            db['NAME'],
        ]
        filename = f"{db['NAME']}_{timestamp}.sql.gz"
    elif db['ENGINE'] == 'django.db.backends.sqlite3':
        cmd = ['sqlite3', str(db['NAME']), '.dump']
        filename = f"db_{timestamp}.sql.gz"
    else:
        return HttpResponse('Unsupported database engine', status=400)

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        return HttpResponse(f'Backup failed: {result.stderr.decode()}', status=500)

    compressed = gzip.compress(result.stdout)

    response = HttpResponse(compressed, content_type='application/gzip')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
