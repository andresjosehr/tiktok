import gzip
import os
import subprocess
import tempfile

import requests as http_requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def database_backup(request):
    """Generate a gzipped mysqldump of the local database."""
    db = settings.DATABASES['default']

    cmd = [
        'docker', 'exec', 'tiktok_mysql',
        'mysqldump',
        '-u', db['USER'],
        f"--password={db['PASSWORD']}",
        db['NAME'],
    ]
    result = subprocess.run(cmd, capture_output=True)

    # Filter out mysqldump warning lines
    sql_lines = [l for l in result.stdout.decode().splitlines(True) if not l.startswith('mysqldump:')]
    sql_clean = ''.join(sql_lines).encode()

    if result.returncode != 0 or not sql_clean.strip():
        return JsonResponse({'error': f'Dump failed: {result.stderr.decode()}'}, status=500)

    compressed = gzip.compress(sql_clean)
    response = JsonResponse({'status': 'ok'})
    # Return raw gzip binary
    from django.http import HttpResponse
    response = HttpResponse(compressed, content_type='application/gzip')
    response['Content-Disposition'] = 'attachment; filename="backup.sql.gz"'
    return response


@csrf_exempt
def database_sync(request):
    """Pull backup from remote server and restore it locally."""
    remote_ip = request.GET.get('from', '192.168.1.237')
    remote_port = request.GET.get('port', '8000')
    remote_url = f'http://{remote_ip}:{remote_port}/backup/'

    db = settings.DATABASES['default']
    root_pw = os.environ.get('DB_ROOT_PASSWORD', 'root')

    # 1. Download backup from remote
    try:
        resp = http_requests.get(remote_url, timeout=60)
        resp.raise_for_status()
    except Exception as e:
        return JsonResponse({'error': f'Failed to download from {remote_url}: {str(e)}'}, status=500)

    # 2. Decompress gzip
    try:
        sql_data = gzip.decompress(resp.content)
    except Exception as e:
        return JsonResponse({'error': f'Failed to decompress: {str(e)}'}, status=500)

    # 3. Write SQL to temp file and copy to container
    with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as tmp:
        tmp.write(sql_data)
        tmp_path = tmp.name

    try:
        cp = subprocess.run(['docker', 'cp', tmp_path, 'tiktok_mysql:/tmp/restore.sql'], capture_output=True)
        if cp.returncode != 0:
            return JsonResponse({'error': f'docker cp failed: {cp.stderr.decode()}'}, status=500)
    finally:
        os.unlink(tmp_path)

    # 4. Drop, recreate, and import
    restore_script = (
        f"mysql -u root -p'{root_pw}' -e "
        f"'DROP DATABASE IF EXISTS {db['NAME']}; CREATE DATABASE {db['NAME']};' 2>/dev/null && "
        f"mysql -u root -p'{root_pw}' {db['NAME']} < /tmp/restore.sql 2>/dev/null && "
        f"rm /tmp/restore.sql"
    )
    result = subprocess.run(['docker', 'exec', 'tiktok_mysql', 'bash', '-c', restore_script], capture_output=True)

    if result.returncode != 0:
        return JsonResponse({'error': f'Restore failed: {result.stdout.decode()} {result.stderr.decode()}'}, status=500)

    # 5. Verify
    verify = subprocess.run(
        ['docker', 'exec', 'tiktok_mysql', 'bash', '-c',
         f"mysql -u root -p'{root_pw}' {db['NAME']} -e 'SHOW TABLES;' 2>/dev/null"],
        capture_output=True
    )
    if not verify.stdout.strip():
        return JsonResponse({'error': 'Restore completed but database is empty'}, status=500)

    return JsonResponse({'success': True, 'source': remote_url})
