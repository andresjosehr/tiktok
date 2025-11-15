# TikTok Live Events - Sistema de Captura y Procesamiento

Proyecto Django con sistema de captura de eventos de TikTok Live y procesamiento mediante colas con múltiples servicios.

## 📋 Índice

- [Requisitos](#requisitos)
- [Inicialización del Proyecto](#inicialización-del-proyecto)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Apps del Proyecto](#apps-del-proyecto)
- [Sistema de Colas](#sistema-de-colas)
- [Comandos Principales](#comandos-principales)
- [Crear Servicios Personalizados](#crear-servicios-personalizados)
- [Estructura del Proyecto](#estructura-del-proyecto)

---

## 🔧 Requisitos

- Docker
- Docker Compose

---

## 🚀 Inicialización del Proyecto

### 1. Levantar los contenedores

```bash
docker-compose up -d
```

### 2. Ejecutar las migraciones

```bash
docker-compose exec web python manage.py migrate
```

### 3. Poblar datos iniciales

```bash
docker-compose exec web python manage.py populate_initial_data
```

Este comando crea:
- Configuración de `tiktok_user`
- Servicios: **DinoChrome** (SYNC) y **Overlays** (ASYNC)
- Configuraciones de eventos para cada servicio

### 4. Crear un superusuario

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 🏗️ Arquitectura del Sistema

El sistema está diseñado con 3 componentes principales:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CAPTURA DE EVENTOS (TikTok Live)                         │
│    TikTokLiveClient → on_gift() → LiveEvent.create()        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. DISTRIBUCIÓN (EventDispatcher)                           │
│    - Busca servicios activos suscritos                      │
│    - Verifica espacio en cola                               │
│    - Encola con prioridad                                   │
│    - Descarta eventos de baja prioridad si es necesario     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PROCESAMIENTO (ServiceWorkers)                           │
│    - Cada servicio tiene su propia cola                     │
│    - Procesa por orden de prioridad                         │
│    - Modo SYNC (secuencial) o ASYNC (paralelo)              │
│    - Ejecuta acciones específicas del servicio              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Apps del Proyecto

### `apps/tiktok_events`
**Captura de eventos de TikTok Live**

**Modelos:**
- `LiveSession` - Sesiones de captura (períodos de tiempo)
- `LiveEvent` - Eventos individuales de TikTok (regalos, comentarios, likes, etc.)

**Funcionalidad:**
- Captura eventos en tiempo real de TikTok Live
- Soporta rachas (streaks) para regalos y likes
- Asocia eventos a sesiones
- Limpieza automática de caracteres especiales

### `apps/queue_system`
**Sistema de colas de eventos**

**Modelos:**
- `Service` - Definición de servicios (DinoChrome, Overlays, etc.)
- `ServiceEventConfig` - Configuración de eventos por servicio (prioridad, async/sync, descartable)
- `EventQueue` - Cola de eventos pendientes por servicio

**Componentes:**
- `EventDispatcher` - Distribuye eventos a servicios suscritos
- `BaseQueueService` - Clase base abstracta para servicios
- `ServiceWorker` - Worker que procesa colas

### `apps/app_config`
**Configuración general**

- Almacena configuraciones key-value del sistema
- Ejemplo: `tiktok_user` - username del streamer

### `apps/services/dinochrome`
**Servicio de automatización de Chrome - DinoChrome Game**

- Control de Chrome mediante Selenium WebDriver
- Juego DinoChrome (clon de Chrome Dino) disponible en `/dino/`
- Auto-play con IA integrada
- Procesamiento SYNC (acciones secuenciales)
- **Funcionalidad destacada**: Al recibir regalo "Rosa", reinicia el juego y reproduce audio con ElevenLabs TTS

### `apps/services/overlays`
**Servicio de overlays visuales**

- Manejo de overlays para streaming/OBS
- Procesamiento ASYNC (eventos en paralelo)
- Diferentes tiempos de display por tipo de evento
- Ideal para notificaciones visuales durante streams

### `apps/integrations/elevenlabs`
**Integración con ElevenLabs TTS**

- Text-to-speech de alta calidad
- API key configurable vía `Config` (meta_key: `elevenlabs_api`)
- Almacenamiento de audio en `media/elevenlabs/`
- Reproducción mediante PulseAudio (paplay en Docker)
- Soporte para reproducción síncrona (wait=True) y asíncrona

### `apps/integrations/llm`
**Cliente genérico de LLM**

- Compatible con APIs formato OpenAI (DeepSeek, Claude, GPT, LMStudio, Ollama)
- Configuración vía `Config`: `llm_url`, `llm_key`, `llm_model`, `llm_system_prompt`
- Generación automática de respuestas por tipo de evento
- Ideal para chatbots y respuestas automáticas

### `apps/base_models`
**Modelos base del proyecto**

- `BaseModel`: Modelo abstracto con timestamps automáticos (created_at, updated_at)
- Todos los modelos del proyecto heredan de esta clase

---

## 🎯 Sistema de Colas

### Conceptos Clave

**Service (Servicio):**
- Define un procesador de eventos
- Ejemplo: DinoChrome, Overlays, GMod Integration
- Tiene cola máxima configurable
- Puede estar activo/inactivo

**ServiceEventConfig (Configuración de Eventos):**
- Define qué eventos procesa cada servicio
- **Prioridad** (1-10): Orden de procesamiento (10 = máxima)
- **Modo**: SYNC (secuencial) o ASYNC (paralelo)
- **Descartable**: Si se puede eliminar cuando la cola está llena

**EventQueue (Cola de Eventos):**
- Eventos pendientes de procesar por servicio
- Estados: `pending`, `processing`, `completed`, `failed`, `discarded`
- Ordenados por prioridad descendente

### Ejemplo de Configuración

**Servicio DinoChrome** (Control de Chrome):
| Evento | Prioridad | Modo | Descartable |
|--------|-----------|------|-------------|
| GiftEvent | 10 | SYNC | ❌ |
| SubscribeEvent | 9 | SYNC | ❌ |
| FollowEvent | 8 | SYNC | ❌ |
| CommentEvent | 6 | SYNC | ✅ |
| LikeEvent | 3 | SYNC | ✅ |

**Servicio Overlays** (Overlays visuales en OBS):
| Evento | Prioridad | Modo | Descartable |
|--------|-----------|------|-------------|
| GiftEvent | 10 | ASYNC | ❌ |
| SubscribeEvent | 8 | ASYNC | ❌ |
| FollowEvent | 7 | ASYNC | ❌ |
| CommentEvent | 5 | ASYNC | ✅ |
| LikeEvent | 2 | ASYNC | ✅ |

**Diferencias clave:**
- **DinoChrome**: Todo SYNC (espera que cada acción termine antes de la siguiente)
- **Overlays**: Todo ASYNC (puede mostrar múltiples overlays en paralelo)

---

## 🎮 Comandos Principales

### Iniciar el Sistema Completo (Recomendado)

```bash
# Inicia todo: captura de TikTok + workers de procesamiento
docker-compose exec web python manage.py start_event_system

# Con nombre de sesión personalizado
docker-compose exec web python manage.py start_event_system --session-name "Sesión de tarde"

# Con logs detallados
docker-compose exec web python manage.py start_event_system --verbose
```

**¿Qué hace?**
- Inicia automáticamente todos los workers de servicios activos
- Conecta a TikTok Live y captura eventos en tiempo real
- Muestra dashboard con estadísticas cada 30 segundos
- Gestión unificada de todos los procesos
- Detención graceful con Ctrl+C (finaliza sesión y detiene workers)
- El username se toma de la configuración `tiktok_user` en Config

**Este es el comando recomendado para uso normal** 🌟

---

### Comandos Individuales (Uso Avanzado)

#### Capturar Solo Eventos de TikTok Live

```bash
# Capturar eventos (el username se toma de Config)
docker-compose exec web python manage.py capture_tiktok_live

# Especificar username manualmente
docker-compose exec web python manage.py capture_tiktok_live --username nombrestreamer

# Con nombre de sesión
docker-compose exec web python manage.py capture_tiktok_live --session-name "Sesión de tarde"
```

**¿Qué hace?**
- Se conecta al live de TikTok del streamer
- Captura todos los eventos (regalos, comentarios, likes, follows, etc.)
- Guarda en `LiveEvent`
- Distribuye automáticamente a las colas de servicios activos
- Crea una nueva sesión cada vez que se ejecuta
- **Nota**: Los eventos se encolan pero NO se procesan hasta que ejecutes `run_queue_workers`

#### Ejecutar Solo Workers (Procesadores de Cola)

```bash
# Ejecutar todos los servicios activos
docker-compose exec web python manage.py run_queue_workers

# Solo un servicio específico
docker-compose exec web python manage.py run_queue_workers --service dinochrome

# Con logs detallados
docker-compose exec web python manage.py run_queue_workers --verbose
```

**¿Qué hace?**
- Inicia workers para cada servicio activo
- Procesa eventos de la cola por orden de prioridad
- Muestra estadísticas cada 30 segundos
- Detención graceful con Ctrl+C
- **Nota**: Solo procesa eventos, NO captura de TikTok

### Poblar Datos Iniciales

```bash
docker-compose exec web python manage.py populate_initial_data
```

**¿Qué crea?**
- Config `tiktok_user` (vacío)
- Servicio DinoChrome con 7 configuraciones de eventos (SYNC)
- Servicio Overlays con 7 configuraciones de eventos (ASYNC)

---

## 🛠️ Crear Servicios Personalizados

### Paso 1: Crear la Clase del Servicio

Crea un archivo `apps/mi_servicio/services.py`:

```python
from apps.queue_system.base_service import BaseQueueService

class MiServicio(BaseQueueService):

    def on_start(self):
        """Se ejecuta al iniciar el worker"""
        print("🚀 Mi Servicio iniciado")
        # Conectar a servicios externos, inicializar recursos, etc.

    def on_stop(self):
        """Se ejecuta al detener el worker"""
        print("👋 Mi Servicio detenido")
        # Cerrar conexiones, limpiar recursos, etc.

    def process_event(self, live_event, queue_item):
        """
        Procesa un evento de la cola

        Returns:
            bool: True si se procesó exitosamente, False si falló
        """
        try:
            if live_event.event_type == 'GiftEvent':
                # Procesar regalo
                gift_name = live_event.event_data['gift']['name']
                user = live_event.user_nickname
                print(f"🎁 {user} envió {gift_name}")
                # Tu lógica aquí...
                return True

            elif live_event.event_type == 'CommentEvent':
                # Procesar comentario
                comment = live_event.event_data['comment']
                user = live_event.user_nickname
                print(f"💬 {user}: {comment}")
                # Tu lógica aquí...
                return True

            return False  # Evento no manejado

        except Exception as e:
            print(f"❌ Error: {e}")
            return False
```

### Paso 2: Registrar el Servicio en el Admin

1. Ir al admin de Django: http://localhost:8000/admin
2. Ir a "Services" → "Add Service"
3. Llenar los campos:
   - **Name**: Mi Servicio
   - **Slug**: mi_servicio
   - **Service class**: `apps.mi_servicio.services.MiServicio`
   - **Max queue size**: 100
   - **Is active**: ✅

### Paso 3: Configurar Eventos

Dentro del mismo formulario, en "Service Event Configurations":

| Event Type | Enabled | Priority | Async | Discardable |
|------------|---------|----------|-------|-------------|
| GiftEvent | ✅ | 10 | ❌ | ❌ |
| CommentEvent | ✅ | 5 | ✅ | ✅ |
| LikeEvent | ✅ | 2 | ✅ | ✅ |

### Paso 4: Ejecutar el Worker

```bash
docker-compose exec web python manage.py run_queue_workers --service mi_servicio
```

---

## 📂 Estructura del Proyecto

```
.
├── apps/
│   ├── tiktok_events/              # Captura de eventos de TikTok
│   │   ├── models.py               # LiveSession, LiveEvent
│   │   ├── services.py             # TikTokEventCapture
│   │   ├── admin.py                # Admin de eventos
│   │   └── management/commands/
│   │       ├── capture_tiktok_live.py
│   │       └── start_event_system.py  # Sistema completo
│   │
│   ├── queue_system/               # Sistema de colas
│   │   ├── models.py               # Service, ServiceEventConfig, EventQueue
│   │   ├── dispatcher.py           # EventDispatcher
│   │   ├── base_service.py         # BaseQueueService (clase abstracta)
│   │   ├── worker.py               # ServiceWorker
│   │   ├── admin.py                # Admin de servicios y colas
│   │   └── management/commands/
│   │       ├── populate_initial_data.py
│   │       └── run_queue_workers.py
│   │
│   ├── services/                   # Servicios implementados
│   │   ├── dinochrome/             # Chrome automation + DinoChrome game
│   │   │   ├── DinoChromeService.py
│   │   │   ├── ChromeService.py    # Selenium WebDriver wrapper
│   │   │   └── dino-game/          # Juego DinoChrome (Django app)
│   │   └── overlays/               # Overlays visuales
│   │       └── services.py         # OverlaysService
│   │
│   ├── integrations/               # Integraciones externas
│   │   ├── elevenlabs/             # Text-to-speech
│   │   │   ├── client.py           # ElevenLabsClient
│   │   │   ├── views.py            # API endpoints
│   │   │   └── urls.py
│   │   └── llm/                    # LLM genérico
│   │       ├── client.py           # LLMClient (OpenAI-compatible)
│   │       ├── services.py         # LLMService
│   │       └── models.py
│   │
│   ├── app_config/                 # Configuración general
│   │   └── models.py               # Config (key-value storage)
│   │
│   └── base_models.py              # BaseModel con timestamps
│
├── config/                         # Configuración Django
│   ├── settings.py
│   └── urls.py
│
├── media/                          # Archivos multimedia
│   └── elevenlabs/                 # Audio generado por TTS
│
├── docker-compose.yml              # Docker Compose
├── Dockerfile                      # Imagen Django
├── requirements.txt                # Dependencias Python
├── .env                            # Variables de entorno
├── CLAUDE.md                       # Instrucciones para Claude Code
└── manage.py
```

---

## 🔗 Acceso

- **Aplicación Django**: http://localhost:8000
- **Admin de Django**: http://localhost:8000/admin
- **MySQL**: localhost:3306

---

## 📊 Flujo Completo de Ejemplo

### Opción 1: Sistema Completo (Recomendado) ⭐

```bash
docker-compose exec web python manage.py start_event_system --verbose
```

**Output:**
```
======================================================================
🚀 SISTEMA DE EVENTOS TIKTOK - INICIO
======================================================================

📺 Streamer: @nombrestreamer
⏰ Hora inicio: 2025-10-05 15:30:00

======================================================================
📦 INICIANDO WORKERS DE SERVICIOS
======================================================================

🔧 Iniciando worker: DinoChrome
  ✅ Worker activo (cola máx: 50)
🔧 Iniciando worker: Overlays
  ✅ Worker activo (cola máx: 100)

✅ 2 worker(s) iniciado(s)

======================================================================
📡 INICIANDO CAPTURA DE TIKTOK LIVE
======================================================================

🎬 Conectando a @nombrestreamer...
✅ Captura de TikTok iniciada

======================================================================
📊 SISTEMA ACTIVO - Monitoreo en tiempo real
======================================================================

💡 Presiona Ctrl+C para detener el sistema
📊 Estadísticas cada 30 segundos...

💬 usuario123: Hola!
🎁 usuario456 envió Rosa x1
✅ [DinoChrome] CommentEvent (P:6) completado
✅ [Overlays] CommentEvent (P:5) completado
✅ [DinoChrome] GiftEvent (P:10) completado
✅ [Overlays] GiftEvent (P:10) completado

======================================================================
📊 ESTADÍSTICAS DEL SISTEMA
======================================================================

⏱️  Tiempo activo: 0h 5m
📝 Sesión ID: 1
📊 Eventos capturados: 42

🔧 Workers activos: 2

🟢 DinoChrome
  • Pendientes: 0
  • Procesando: 0

🟢 Overlays
  • Pendientes: 0
  • Procesando: 0
  • Threads async: 0

======================================================================
```

### Opción 2: Comandos Separados (Avanzado)

#### Terminal 1: Capturar eventos de TikTok

```bash
docker-compose exec web python manage.py capture_tiktok_live --username nombrestreamer
```

**Output:**
```
🎬 Iniciando captura de eventos para @nombrestreamer...
✅ Conectado a @nombrestreamer - Room ID: 123456
📝 Sesión creada: #1 - Sin nombre
💬 usuario123: Hola!
🎁 usuario456 envió Rosa x1
❤️ usuario789 dio like
```

#### Terminal 2: Ejecutar workers

```bash
docker-compose exec web python manage.py run_queue_workers --verbose
```

**Output:**
```
============================================================
🚀 QUEUE WORKERS - Sistema de Procesamiento de Eventos
============================================================

📦 Iniciando worker para: DinoChrome
  ✅ Worker activo - Cola máxima: 50 eventos
📦 Iniciando worker para: Overlays
  ✅ Worker activo - Cola máxima: 100 eventos

✅ 2 worker(s) activo(s)

💡 Presiona Ctrl+C para detener los workers
📊 Estadísticas cada 30 segundos...

✅ [DinoChrome] CommentEvent (P:6) completado
✅ [Overlays] CommentEvent (P:5) completado
✅ [DinoChrome] GiftEvent (P:10) completado
✅ [Overlays] GiftEvent (P:10) completado
```

### Lo que está pasando internamente:

1. **TikTok Live** envía evento "Hola!"
2. Se guarda en **LiveEvent**
3. **EventDispatcher** lo distribuye:
   - DinoChrome cola (P:6, SYNC)
   - Overlays cola (P:5, ASYNC)
4. **Workers** procesan:
   - DinoChrome: espera a que termine antes del siguiente
   - Overlays: procesa en paralelo sin esperar

---

## 🐛 Comandos de Desarrollo

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Acceder al shell de Django
docker-compose exec web python manage.py shell

# Acceder al contenedor
docker-compose exec web bash

# Reiniciar contenedores
docker-compose restart

# Detener todo
docker-compose down

# Eliminar base de datos (cuidado!)
docker-compose down -v
```

---

## 📝 Notas Importantes

- **Prioridad**: Los eventos con mayor prioridad (10) se procesan primero
- **SYNC vs ASYNC**: SYNC espera que termine cada evento antes del siguiente, ASYNC procesa múltiples en paralelo
- **Descartable**: Cuando la cola está llena, eventos marcados como descartables se eliminan para hacer espacio a eventos más importantes
- **Sesiones**: Cada ejecución del comando `capture_tiktok_live` crea una nueva sesión
- **Workers**: Deben estar corriendo para que los eventos se procesen, de lo contrario se acumulan en la cola

---

## 🎓 Conceptos Clave

**¿Cuándo usar SYNC?**
- Cuando las acciones deben ejecutarse en orden estricto
- Cuando una acción depende del resultado de la anterior
- Ejemplo: Acciones en Chrome que requieren esperar la página

**¿Cuándo usar ASYNC?**
- Cuando las acciones son independientes
- Cuando quieres máxima velocidad de procesamiento
- Ejemplo: Mostrar overlays visuales que no interfieren entre sí

**¿Qué eventos marcar como descartables?**
- Eventos de baja importancia (likes, joins)
- Eventos muy frecuentes (comentarios comunes)
- **NUNCA**: Regalos, suscripciones, follows

---

## 🔌 Integraciones Disponibles

### ElevenLabs TTS
1. Obtener API key de https://elevenlabs.io
2. Configurar en Django admin: `Config` → `elevenlabs_api`
3. Usar en servicios:
```python
from apps.integrations.elevenlabs.client import ElevenLabsClient

client = ElevenLabsClient()
client.text_to_speech_and_save(
    "Texto a convertir",
    play_audio=True,
    wait=True  # SYNC: espera a que termine
)
```

### LLM (DeepSeek, Claude, GPT, LMStudio)
1. Configurar en Django admin:
   - `llm_url`: https://api.deepseek.com/v1/chat/completions (o tu endpoint)
   - `llm_key`: Tu API key
   - `llm_model`: deepseek-chat (o tu modelo)
   - `llm_system_prompt`: Prompt del sistema
2. Usar en servicios:
```python
from apps.integrations.llm.client import LLMClient

client = LLMClient()
response = client.chat("Tu mensaje aquí")
```

### Chrome Automation (DinoChrome)
- Ya configurado en DinoChrome service
- Juego disponible en http://localhost:8000/dino/
- Auto-play habilitado
- Controlable mediante `ChromeService`:
```python
from apps.services.dinochrome.ChromeService import ChromeService

chrome = ChromeService()
chrome.initialize_browser(headless=False)
chrome.restart()  # Reiniciar juego
score = chrome.get_score()  # Obtener puntaje
```

---

## 🚀 Próximos Pasos

1. Crear tus propios servicios personalizados
2. Configurar las prioridades según tus necesidades
3. Ajustar tamaños de cola por servicio
4. Implementar lógica específica en `process_event()`
5. Monitorear el admin para ver estadísticas de la cola
6. Integrar ElevenLabs para respuestas de voz
7. Configurar LLM para chatbot automático
8. Personalizar acciones en DinoChrome según eventos

¡El sistema está listo para procesar eventos de TikTok Live! 🎉
