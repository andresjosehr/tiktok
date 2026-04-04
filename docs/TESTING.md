# Sistema de Testing para TikTok Live Events

## Problema

El sistema de eventos de TikTok Live es complejo y tiene múltiples componentes que deben funcionar de manera coordinada:

1. **Captura de eventos** - Recibe eventos de TikTok (regalos, comentarios, likes, etc.)
2. **Dispatcher** - Distribuye eventos a las colas de servicios según prioridad
3. **Workers** - Procesan eventos de las colas de cada servicio
4. **Servicios** - Ejecutan acciones específicas (TTS, overlays, música, etc.)

**Problemas específicos identificados:**

- **Falta de visibilidad**: No había forma de saber qué estaba pasando internamente sin revisar la base de datos
- **Testing costoso**: Probar requería donaciones reales en TikTok
- **Prioridades no verificables**: No había logs que mostraran si el sistema de prioridades funcionaba
- **Tiempos desconocidos**: No se sabía cuánto tardaba cada operación (LLM, TTS, descarga de YouTube)
- **Errores silenciosos**: Muchos errores no se logueaban adecuadamente

---

## Objetivo del Testing

Crear un sistema de testing integral que permita:

1. **Simular eventos** sin necesidad de donaciones reales
2. **Validar el flujo completo** desde la captura hasta la ejecución
3. **Verificar prioridades** - que Ice Cream (P:10) se procese antes que Rose (P:9)
4. **Medir tiempos** de cada operación para identificar cuellos de botella
5. **Detectar errores** de manera clara y rápida

---

## Qué queremos lograr

### 1. Simulación continua de eventos
Un comando que genere eventos aleatorios de manera continua, simulando un stream real:
- Regalos: Ice Cream, Rose, Awesome, GG, Enjoy Music
- Comentarios: Comandos de música (!despacito, !shakira, etc.)
- Configuración de probabilidades y tiempos

### 2. Logging centralizado y claro
Todos los logs van a `logs/event_system.log` con formato consistente:
```
[COMPONENTE] EMOJI Acción: detalles (tiempo)
```

### 3. Trazabilidad completa
Poder seguir un evento desde que llega hasta que se procesa:
```
[DISPATCHER] ━━━ Distribuyendo: GiftEvent[Ice Cream] de @Usuario
[DISPATCHER] ✅ DinoChrome: Encolado P:10 | Cola: 1/50
[DinoChrome] 🍦 Ice Cream de @Usuario detectado!
[DinoChrome] ✅ LLM generó texto en 2.35s
[DinoChrome] ✅ Ice Cream completado | Total: 8.1s
```

### 4. Verificación de prioridades
Confirmar que el sistema de prioridades por regalo funciona:
- Ice Cream → P:10 (LLM + TTS + restart)
- Rose → P:9 (TTS simple)
- Awesome → P:8 (solo GIF)

---

## Modificaciones Realizadas

### 1. Comando de simulación (`simulate_events.py`)

**Ubicación:** `apps/tiktok_events/management/commands/simulate_events.py`

**Uso:**
```bash
# Test de 60 segundos (default)
python manage.py simulate_events

# Test de 2 minutos, evento cada 2 segundos
python manage.py simulate_events --duration 120 --interval 2

# Modo infinito hasta Ctrl+C
python manage.py simulate_events --forever --interval 3

# Con detalles de cada evento
python manage.py simulate_events --verbose

# Ajustar probabilidades
python manage.py simulate_events --weights "ice:5,rose:3,awesome:2,gg:1,music:1,enjoy:1"
```

**Eventos simulados:**
| Evento | Descripción | Prioridad |
|--------|-------------|-----------|
| Ice Cream | LLM + TTS + restart juego | P:10 |
| Rose | TTS "No es Rose, es Rosa..." | P:9 |
| Awesome | GIF overlay | P:8 |
| GG | Créditos de música | - |
| !cancion | Solicitud de música | - |
| Enjoy Music | GIF overlay | P:8 |

---

### 2. Sistema de prioridad por regalo (`dispatcher.py`)

**Ubicación:** `apps/queue_system/dispatcher.py`

**Cambios:**
- Añadido diccionario `GIFT_PRIORITIES` con prioridades por nombre de regalo
- Modificado `_enqueue_event()` para usar prioridad específica del regalo
- Añadido logging detallado de cada operación de dispatch

**Prioridades configuradas:**
```python
GIFT_PRIORITIES = {
    'ice_cream': 10, 'ice cream cone': 10, 'cone': 10,
    'rose': 9, 'rosa': 9,
    'awesome': 8, "you're awesome": 8, 'enjoy music': 8,
}
```

**Nuevo formato de logs:**
```
[DISPATCHER] ━━━ Distribuyendo: GiftEvent[Ice Cream Cone] de @Usuario
[DISPATCHER] ✅ DinoChrome: Encolado P:10 | Cola: 3/50
[DISPATCHER] ⏭️  Music: Saltado - Racha en curso (status=start)
[DISPATCHER] 🗑️  Overlays: Descartado - Cola llena, sin eventos P<8 descartables
[DISPATCHER] 🔴 Service: Cola llena (50/50)
```

---

### 3. Logging en OverlaysService (`services.py`)

**Ubicación:** `apps/services/overlays/services.py`

**Cambios:**
- Añadido logging para TODOS los tipos de eventos (antes solo Rosa)
- Añadido timing en milisegundos
- Añadido información de prioridad y usuario

**Nuevo formato de logs:**
```
[OVERLAYS] 🌹 Rosa de @Usuario x1 → Overlay enviado (15ms)
[OVERLAYS] 🎁 Gift[Awesome] de @Usuario x3 (P:8) (1205ms)
[OVERLAYS] 💬 Comment de @Usuario: '!despacito' (P:5) (402ms)
[OVERLAYS] ❤️  Like de @Usuario x50 (P:2) (201ms)
[OVERLAYS] ➕ Follow de @Usuario (P:7) (702ms)
```

---

### 4. Logging en ServiceWorker (`worker.py`)

**Ubicación:** `apps/queue_system/worker.py`

**Cambios:**
- Añadido timing total de procesamiento por evento
- Añadido nombre de usuario en los logs
- Añadido nombre del regalo para GiftEvent

**Nuevo formato de logs:**
```
[DinoChrome] GiftEvent[Ice Cream Cone] de @Usuario (P:10) completado en 12500ms
[Overlays] GiftEvent[Rose] de @Usuario (P:9) completado en 1205ms
[Music] CommentEvent de @Usuario (P:5) completado en 8523ms
```

---

### 5. Logging en MusicService (`services.py`)

**Ubicación:** `apps/services/music/services.py`

**Cambios:**
- Añadido detección explícita de rachas
- Añadido timing de búsqueda y descarga de YouTube
- Añadido duración de canciones en formato mm:ss
- Mejorado formato de mensajes con emojis consistentes

**Nuevo formato de logs:**
```
[MUSIC] 🔥 Racha detectada: @Usuario x5 GG
[MUSIC] 🆕 Créditos @Usuario: +1 (Disponibles: 1/1)
[MUSIC] 🎵 Comando recibido: 'despacito' de @Usuario
[MUSIC] 🔍 Buscando en YouTube: 'despacito'...
[MUSIC] ✅ Descargado 'Despacito - Luis Fonsi' (3:47) en 8.2s
[MUSIC] 💳 Crédito usado: @Usuario (Restantes: 0/1)
[MUSIC] ⏭️  Interrumpiendo canción actual para @Usuario
[MUSIC] ▶️  Reproduciendo: 'Despacito - Luis Fonsi' (3:47) | Total: 9.5s
```

---

### 6. Logging en DinoChromeService (`DinoChromeService.py`)

**Ubicación:** `apps/services/dinochrome/DinoChromeService.py`

**Cambios:**
- Añadido timing detallado para Ice Cream (LLM + TTS + Audio)
- Añadido timing para Rose (TTS + Audio)
- Añadido nombre de usuario en todos los logs
- Resumen de tiempos al finalizar cada operación

**Nuevo formato de logs:**
```
[DINOCHROME] 🍦 Ice Cream de @Usuario detectado! (Queue ID: 123)
[DINOCHROME] 🎲 Prompt seleccionado: Eres un streamer jugando...
[DINOCHROME] 🤖 Llamando al LLM...
[DINOCHROME] ✅ LLM generó texto en 2.35s
[DINOCHROME] 💬 Respuesta LLM: 'Ay Usuario, me reiniciaste el juego!'
[DINOCHROME] 🔊 TTS generado en 1.20s
[DINOCHROME] ✅ Ice Cream completado | LLM:2.4s + TTS:1.2s + Audio:4.5s = Total:8.1s

[DINOCHROME] 🌹 Rose de @Usuario detectada (Queue ID: 124)
[DINOCHROME] 🌹 Overlay enviado
[DINOCHROME] ✅ Rose completado | TTS:1.1s + Audio:3.2s = Total:4.3s

[DINOCHROME] 💃 GIF enviado: bailando_1.gif → Slot 3 (Usuario: @Usuario)
[DINOCHROME] ♻️ Slot 3 liberado
```

---

## Cómo usar el sistema de testing

### Paso 1: Iniciar el sistema de eventos
```bash
python manage.py start_event_system
```

### Paso 2: En otra terminal, iniciar la simulación
```bash
python manage.py simulate_events --duration 120 --interval 2 --verbose
```

### Paso 3: Revisar los logs
```bash
# Ver logs en tiempo real
tail -f logs/event_system.log

# Buscar errores
grep "❌" logs/event_system.log

# Ver solo dispatcher
grep "\[DISPATCHER\]" logs/event_system.log

# Ver tiempos de Ice Cream
grep "Ice Cream completado" logs/event_system.log
```

---

## Validación de resultados

### Verificar que las prioridades funcionan:
1. Buscar en el log eventos de diferentes prioridades llegando casi simultáneamente
2. Verificar que Ice Cream (P:10) se procesa antes que Rose (P:9)
3. Verificar que Rose (P:9) se procesa antes que Awesome (P:8)

### Verificar tiempos aceptables:
- Ice Cream: < 15 segundos (LLM + TTS + Audio)
- Rose: < 6 segundos (TTS + Audio)
- Awesome: < 2 segundos (solo GIF)
- Música: < 15 segundos (búsqueda + descarga + inicio reproducción)

### Verificar que no hay errores:
```bash
grep -E "❌|Error|Exception|Failed" logs/event_system.log
```

---

## Estructura de archivos modificados

```
apps/
├── queue_system/
│   ├── dispatcher.py          # Sistema de prioridades + logging
│   └── worker.py              # Timing de procesamiento
├── services/
│   ├── dinochrome/
│   │   └── DinoChromeService.py   # Timing detallado LLM/TTS
│   ├── music/
│   │   └── services.py        # Logging de créditos y YouTube
│   └── overlays/
│       └── services.py        # Logging de todos los eventos
└── tiktok_events/
    └── management/
        └── commands/
            └── simulate_events.py  # Comando de simulación

logs/
└── event_system.log           # Log centralizado
```
