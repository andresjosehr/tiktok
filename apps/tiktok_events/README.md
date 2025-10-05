# TikTok Events - Captura de Eventos de TikTok Live

Sistema para capturar y almacenar todos los eventos de TikTok Live en tiempo real con soporte para rachas (streaks).

## 📋 Características

- ✅ Captura de eventos en tiempo real de TikTok Live
- ✅ Soporte completo para rachas (gifts y likes)
- ✅ Almacenamiento en base de datos con estructura JSON flexible
- ✅ Panel de administración Django
- ✅ Trackeo de múltiples tipos de eventos

## 🎯 Eventos Soportados

| Evento | Descripción | Soporte Racha |
|--------|-------------|---------------|
| `CommentEvent` | Comentarios en el chat | ❌ |
| `GiftEvent` | Regalos enviados | ✅ |
| `LikeEvent` | Likes al stream | ✅ |
| `ShareEvent` | Compartir el live | ❌ |
| `FollowEvent` | Nuevos seguidores | ❌ |
| `JoinEvent` | Usuarios uniéndose | ❌ |
| `SubscribeEvent` | Suscripciones | ❌ |

## 🗄️ Estructura del Modelo

### LiveEvent

```python
- event_type: Tipo de evento (CommentEvent, GiftEvent, etc.)
- timestamp: Momento del evento
- room_id: ID de la sala/live
- streamer_unique_id: Username del streamer
- user_id: TikTok user ID
- user_unique_id: Username del usuario
- user_nickname: Nickname del usuario
- is_streaking: Si está en racha activa
- streak_id: ID único de la racha
- streak_status: Estado de la racha (start, continue, end)
- event_data: JSON con datos específicos del evento
- created_at: Timestamp de creación en BD
```

### Estructura event_data (JSON)

#### CommentEvent
```json
{
  "comment": "texto del comentario",
  "user": {
    "is_super_fan": true,
    "is_moderator": false,
    "member_level": 5,
    "gifter_level": 10,
    "badges": [...]
  }
}
```

#### GiftEvent (con racha)
```json
{
  "gift": {
    "id": 5655,
    "name": "Rosa",
    "diamond_count": 1,
    "streakable": true
  },
  "repeat_count": 1,
  "streak_total_count": 15,
  "is_streaking": true,
  "value_usd": 0.15,
  "from_user": {...},
  "to_user": {...}
}
```

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos

Edita el archivo `.env`:

```env
DB_NAME=tiktok_db
DB_USER=tiktok_user
DB_PASSWORD=tiktok_password123
DB_HOST=localhost
DB_PORT=3306
```

### 3. Ejecutar migraciones

```bash
python manage.py migrate
```

### 4. Crear superusuario (opcional, para admin)

```bash
python manage.py createsuperuser
```

## 📡 Uso

### Capturar eventos de un live

```bash
python manage.py capture_tiktok_live <username>
```

**Ejemplo:**
```bash
python manage.py capture_tiktok_live isaackogz
```

El comando se conectará al live del usuario y comenzará a capturar todos los eventos en tiempo real.

### Salida en consola

```
🎬 Iniciando captura de eventos para @isaackogz...
✅ Conectado a @isaackogz - Room ID: 123456789
💬 user123: Hola!
🔄 user456 envió Rosa x1 (Total racha: 1)
🔄 user456 envió Rosa x1 (Total racha: 2)
✅ user456 envió Rosa x1 (Total racha: 3)
❤️ user789 dio like
```

## 🎯 Sistema de Rachas (Streaks)

El sistema detecta automáticamente cuándo un regalo o like es parte de una racha:

- **Start** 🟢: Primera acción de una racha
- **Continue** 🟡: Racha en progreso
- **End** 🔴: Última acción de la racha

### Ejemplo de flujo de racha:

```
1. Usuario envía Rosa x1 → streak_status: "start", total: 1
2. Usuario envía Rosa x1 → streak_status: "continue", total: 2
3. Usuario envía Rosa x1 → streak_status: "continue", total: 3
4. Usuario envía Rosa x1 → streak_status: "end", total: 4
```

Todos los eventos de una racha comparten el mismo `streak_id`.

## 📊 Panel de Administración

Accede al admin de Django en: `http://localhost:8000/admin`

### Características del Admin:

- ✅ Filtros por tipo de evento, racha, fecha
- ✅ Búsqueda por usuario, streamer, room_id
- ✅ Visualización JSON formateada
- ✅ Badges de color para estados de racha
- ✅ Jerarquía por fecha

## 🔍 Consultas Útiles

### Top gifters de un live

```python
from apps.tiktok_events.models import LiveEvent
from django.db.models import Sum, F

top_gifters = LiveEvent.objects.filter(
    room_id=123456789,
    event_type='GiftEvent',
    streak_status='end'  # Solo rachas finalizadas
).values('user_unique_id', 'user_nickname').annotate(
    total_gifts=Sum('event_data__streak_total_count')
).order_by('-total_gifts')
```

### Timeline de eventos de un live

```python
events = LiveEvent.objects.filter(
    room_id=123456789
).order_by('timestamp')

for event in events:
    print(f"{event.timestamp} - {event.event_type} - {event.user_unique_id}")
```

### Obtener todos los eventos de una racha

```python
streak_events = LiveEvent.get_streak_events('123_GiftEvent_5655_1234567890')

for event in streak_events:
    print(f"{event.timestamp} - Total: {event.event_data['streak_total_count']}")
```

### Usuarios más activos (comentarios)

```python
from django.db.models import Count

top_commenters = LiveEvent.objects.filter(
    room_id=123456789,
    event_type='CommentEvent'
).values('user_unique_id', 'user_nickname').annotate(
    total_comments=Count('id')
).order_by('-total_comments')
```

## 🎨 Personalización

### Agregar nuevos eventos

1. Importa el evento en `services.py`:
```python
from TikTokLive.events import NuevoEvento
```

2. Registra el handler:
```python
self.client.on(NuevoEvento)(self.on_nuevo_evento)
```

3. Crea el método handler:
```python
async def on_nuevo_evento(self, event: NuevoEvento):
    event_data = {
        # ... estructura del evento
    }
    LiveEvent.objects.create(...)
```

## 🐛 Troubleshooting

### Error de conexión a MySQL
- Verifica que MySQL esté corriendo
- Verifica credenciales en `.env`
- Asegúrate de que la base de datos existe

### No captura eventos
- Verifica que el usuario esté en live
- Usa el username correcto (sin @)
- Revisa los logs de la consola

### Rachas no se detectan correctamente
- Asegúrate de que el regalo sea "streakable"
- Verifica que `event.streaking` tenga el valor correcto

## 📝 Notas Importantes

- ⚠️ Esta es una librería **no oficial** de TikTok
- ⚠️ No usar en producción sin considerar las limitaciones
- ⚠️ TikTok puede cambiar su API en cualquier momento
- ✅ El `event_data` JSON permite flexibilidad para cambios futuros
- ✅ Siempre guarda el payload completo para debugging

## 🔗 Recursos

- [TikTokLive Library](https://github.com/isaackogan/TikTokLive)
- [Django Documentation](https://docs.djangoproject.com/)

## 📄 Licencia

MIT
