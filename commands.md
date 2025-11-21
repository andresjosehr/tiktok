# Comandos Frecuentes

## Iniciar Sistema Completo
```bash
python manage.py start_event_system
```

Opciones:
- `--session-name NAME`: Nombre personalizado para la sesión
- `--verbose`: Mostrar logs detallados

## Otros Comandos Útiles

### Migraciones
```bash
python manage.py migrate
python manage.py makemigrations
```

### Datos Iniciales
```bash
python manage.py populate_initial_data
```

### Comandos Avanzados

#### Solo Captura (sin workers)
```bash
python manage.py capture_tiktok_live
```

#### Solo Workers (sin captura)
```bash
python manage.py run_queue_workers
```

### Reset Database
```bash
docker-compose exec db bash -c "mysql -u root -p\${MYSQL_ROOT_PASSWORD} tiktok_db -e 'DROP DATABASE tiktok_db; CREATE DATABASE tiktok_db;'"
```
