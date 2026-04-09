# TikTok Live Interactive - Sistema de Juegos Interactivos para TikTok Live

Sistema Django para capturar eventos de TikTok Live en tiempo real y procesarlos a traves de juegos interactivos que reaccionan a gifts de los viewers. Diseñado para operar multiples lives simultaneos con contenido automatizado.

## Requisitos

- Docker + Docker Compose (produccion)
- Python 3.10+ (desarrollo local)
- VLC (reproduccion de audio)
- OBS Studio (streaming a TikTok)

## Inicio Rapido

### Docker (produccion)

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py populate_initial_data
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py start_event_system --verbose
```

### Local (desarrollo)

```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate  # usa SQLite automaticamente sin .env
python manage.py runserver 8080
```

## Arquitectura

```
TikTok Live Stream
       |
TikTokLiveClient (captura eventos en tiempo real)
       |
LiveEvent + ViewerCountEvent → Base de datos
       |
EventDispatcher (prioridad por tipo de gift)
       |
   +---+---+---+
   |       |       |
DinoChrome  Music   Overlays
(SYNC)     (SYNC)   (ASYNC)
   |       |       |
Chrome+    VLC     OBS Browser
Selenium   MP3s   Sources
+TTS+LLM
```

### Tres capas

1. **Captura**: `TikTokEventCapture` conecta a TikTok Live via WebSocket, captura gifts, comments, likes, follows, joins, suscripciones y viewer count en tiempo real
2. **Distribucion**: `EventDispatcher` enruta eventos a servicios activos con prioridad por tipo de gift
3. **Procesamiento**: `ServiceWorker` por servicio (SYNC secuencial o ASYNC paralelo)

## Servicios

### DinoChrome (`apps/services/dinochrome/`)
Juego Chrome Dino controlado por Selenium con auto-play AI.
- Rosa → LLM genera respuesta + TTS la reproduce + reinicio del juego
- Rose → TTS "No es Rose, es ROSA!" + overlay
- Ice Cream → GIFs de animalitos bailando (10 slots)
- Otros gifts → TTS de agradecimiento default

### Music (`apps/services/music/`)
Reproduccion de musica de fondo desde archivos locales.
- Reproduce MP3s de `media/music/` en orden aleatorio
- Gift "GG" → salta a la siguiente cancion
- Musica de Epidemic Sound (royalty-free, legal para TikTok Live)
- **Copyright de musica NO permitido en TikTok Live** (desde julio 2025)

### Overlays (`apps/services/overlays/`)
Overlays visuales para OBS via browser sources.
- Procesa eventos en modo ASYNC (paralelo)
- GIFs, animaciones y notificaciones visuales

## Analytics

Dashboard de metricas post-live disponible en `/analytics/`:

- **KPIs por sesion**: Revenue, $/hora, peak viewers, conversion rate, avg watch time
- **Viewer timeline**: Grafico de viewers concurrentes + unicos acumulados
- **Actividad por minuto**: Joins, gifts, comments, likes apilados
- **Gifts**: Breakdown por tipo + tabla de top gifters
- **Comparacion**: Seleccionar multiples sesiones y comparar lado a lado

### Datos capturados automaticamente

| Dato | Como se captura |
|------|----------------|
| Viewers concurrentes | `ViewerCountEvent` via `RoomUserSeqEvent` |
| Viewers unicos acumulados | `ViewerCountEvent.total_unique_viewers` |
| Gifts con valor en diamonds | `GiftEvent.event_data.gift.diamond_count` |
| Duracion de sesion | `LiveSession.started_at / ended_at` |
| Cuenta y juego por sesion | `LiveSession.account` + `LiveSession.game_type` |

## Gestion de Cuentas

### TikTokAccount
Modelo para gestionar multiples cuentas de TikTok:
- Pais y region (determina audiencia via IP)
- Agencia (para obtener stream keys)
- Proxy asignado (IP residencial del pais de la cuenta)
- Datos de inversion (precio de compra, fecha)
- Estado (activa, puede hacer live, tiene stream key)

Registrar cuentas en Django Admin: `/admin/` → TikTok Accounts

## Musica

### Descargar musica de Epidemic Sound
```bash
# Opcion 1: Script de navegador (pegar en consola de epidemicsound.com)
# Ver scripts/epidemic_downloader.js

# Opcion 2: Desde Google Drive (requiere setup)
python manage.py download_music
```

Los MP3s van en `media/music/`. El servicio los encuentra automaticamente.

## Streaming con OBS

### Requisitos para TikTok Live
- 1000+ followers en la cuenta
- Stream key via agencia (Creator Network) o SE.Live plugin
- TikTok Live Studio requiere 3 lives de 25 min para desbloquear camara virtual

### Multi-instancia
- OBS: `obs64.exe --multi --portable` (Windows)
- Audio: Virtual Audio Cable (VB-Audio) por instancia
- Proxy: Proxifier para rutear cada OBS por proxy diferente
- Cada cuenta necesita IP del pais correspondiente

## Estructura del Proyecto

```
apps/
  tiktok_events/          # Captura + TikTokAccount + Analytics dashboard
  queue_system/           # Sistema de colas generico
  app_config/             # Config key-value
  services/
    dinochrome/           # Chrome Dino game (Selenium)
    music/                # Reproduccion MP3 local
    overlays/             # Overlays visuales OBS
  integrations/
    elevenlabs/           # Text-to-speech
    llm/                  # LLM generico (OpenAI-compatible)
    obs/                  # OBS WebSocket control
  audio_player/           # Web audio player
  simulator/              # Simulador de eventos

docs/
  tiktok-farm/            # Documentacion del negocio
    README.md             # Indice
    modelo-de-negocio.md  # Proyecciones, costos, ROI
    infraestructura.md    # Hardware, proxies, OBS, audio
    cuentas-y-agencias.md # Agencias, verificacion, retiros
    juegos-interactivos.md # Catalogo de juegos + principios de diseno
    estrategia-de-contenido.md # Horarios, rotacion, optimizacion
    riesgos-y-mitigacion.md    # Shadow ban, deteccion, compartimentalizacion
    plan-de-ejecucion.md       # Fases 0-3

scripts/
  epidemic_downloader.js  # Descarga masiva de Epidemic Sound

config/                   # Django settings + urls
media/music/              # MP3s de Epidemic Sound (no en git)
```

## Comandos Utiles

```bash
# Capturar eventos de un live
python manage.py capture_tiktok_live --username <user>

# Ejecutar workers
python manage.py run_queue_workers [--service dinochrome]

# Sistema completo (capture + workers)
python manage.py start_event_system --verbose

# Agregar servicio de musica
python manage.py add_music_service

# Descargar musica
python manage.py download_music
```

## Acceso

| URL | Descripcion |
|-----|-------------|
| `/admin/` | Django Admin |
| `/analytics/` | Dashboard de metricas |
| `/dino/` | Juego DinoChrome |
| `/simulator/` | Simulador de eventos |
| `/audio/` | Audio player web |
