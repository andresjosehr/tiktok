# Instalación

```bash
# 1. Instalar PulseAudio en WSL (para reproducción de audio)
sudo apt update
sudo apt install pulseaudio-utils

# 2. Clonar repositorio (si aplica)
# git clone <repo-url>
# cd tiktok

# 3. Crear archivo .env (ajustar valores según necesidad)
cat > .env << EOF
DB_NAME=tiktok_db
DB_USER=tiktok_user
DB_PASSWORD=tiktok_password
DB_ROOT_PASSWORD=root_password
DISPLAY=:0
EOF

# 4. Construir y levantar contenedores
docker-compose build
docker-compose up -d

# 5. Ejecutar migraciones
docker-compose exec web python manage.py migrate

# 6. Poblar datos iniciales (servicios DinoChrome y Overlays)
docker-compose exec web python manage.py populate_initial_data

# 7. Proyecto listo para usar
docker-compose exec web python manage.py start_event_system
```
