# Comandos Rápidos

## Inicialización

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py populate_initial_data
docker-compose exec web python manage.py createsuperuser
```

## Iniciar Sistema

```bash
# Iniciar todo (captura + workers)
docker-compose exec web python manage.py start_event_system

# Con nombre de sesión
docker-compose exec web python manage.py start_event_system --session-name "Sesión noche"

# Con logs detallados
docker-compose exec web python manage.py start_event_system --verbose
```

## Base de Datos

```bash
# Migraciones
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Reiniciar BD (elimina todo)
docker-compose exec db bash -c "mysql -u root -p\${MYSQL_ROOT_PASSWORD} tiktok_db -e 'DROP DATABASE tiktok_db; CREATE DATABASE tiktok_db;'"
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py populate_initial_data

# Shell Django
docker-compose exec web python manage.py shell
```

## Docker

```bash
# Ver logs
docker-compose logs -f
docker-compose logs -f web
docker-compose logs -f db

# Acceder al contenedor
docker-compose exec web bash
docker-compose exec db bash

# Reiniciar
docker-compose restart
docker-compose restart web

# Detener
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reconstruir
docker-compose build
docker-compose up -d --build
```

## Acceso

- Django: http://localhost:8000
- Admin: http://localhost:8000/admin
- MySQL: localhost:3306
