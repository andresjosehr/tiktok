# TikTok - Django + MySQL con Docker

Proyecto Django con MySQL usando Docker Compose.

## Requisitos

- Docker
- Docker Compose

## Inicialización del Proyecto

### 1. Crear el proyecto Django

```bash
docker-compose run web django-admin startproject config .
```

### 2. Configurar la base de datos MySQL

Edita el archivo `config/settings.py`:

```python
# Importar os al inicio del archivo
import os
from pathlib import Path

# Reemplazar la sección DATABASES con:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

### 3. Levantar los contenedores

```bash
docker-compose up -d
```

### 4. Ejecutar las migraciones

```bash
docker-compose exec web python manage.py migrate
```

### 5. Crear un superusuario (opcional)

```bash
docker-compose exec web python manage.py createsuperuser
```

## Acceso

- **Aplicación Django**: http://localhost:8000
- **Admin de Django**: http://localhost:8000/admin
- **MySQL**: localhost:3306

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes (elimina datos de MySQL)
docker-compose down -v

# Crear una nueva app
docker-compose exec web python manage.py startapp nombre_app

# Acceder al shell de Django
docker-compose exec web python manage.py shell

# Acceder al contenedor de Django
docker-compose exec web bash

# Acceder a MySQL
docker-compose exec db mysql -u tiktok_user -p tiktok_db
```

## Estructura del Proyecto

```
.
├── config/              # Configuración del proyecto Django
├── docker-compose.yml   # Configuración de Docker Compose
├── Dockerfile           # Imagen de Django
├── requirements.txt     # Dependencias de Python
├── .env                 # Variables de entorno
└── manage.py            # Utilidad de Django
```
