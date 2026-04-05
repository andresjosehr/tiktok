# Infraestructura

## Hardware disponible

### PC de Mesa (nodo principal de streams)
- **CPU**: Ryzen 9 7900X (12 cores / 24 threads)
- **GPU**: RTX 4070 (NVENC 8va gen, hasta 8 sesiones simultaneas)
- **RAM**: 64GB DDR5
- **Capacidad estimada**: 7-8 instancias simultaneas
- **Cuello de botella**: NVENC (8 sesiones max por hardware)

### Laptop Windows (nodo secundario)
- **CPU**: Intel i7 10th gen (6 cores)
- **GPU**: RTX 2070 Super (NVENC)
- **RAM**: 36GB DDR4
- **Almacenamiento**: 1TB
- **Capacidad estimada**: 3-4 instancias simultaneas

### MacBook Pro (cerebro/orquestador)
- **CPU**: M4 Pro (12 cores)
- **RAM**: 24GB unificada
- **Rol**: NO para streams (sin NVENC, audio routing complicado en macOS)
- **Uso ideal**: Dashboard centralizado, base de datos, monitoreo, desarrollo

### Capacidad total combinada: 10-12 instancias simultaneas

## Por que NVENC es critico

```
Con NVENC (GPU RTX):
  1 stream OBS → ~3-5% CPU (encoding lo hace la GPU)
  4 streams   → ~15-20% CPU
  CPU queda libre para Django, VLC, Chrome

Sin NVENC (solo CPU):
  1 stream OBS (x264 ultrafast) → ~15-20% CPU
  3 streams → ~50-60% CPU
  Poco margen para otras cosas
```

Para PCs sin GPU dedicada: maximo 2 instancias comodas. Con GPU: 3-4+ instancias.

## Consumo de recursos por instancia

| Componente | RAM | CPU (con NVENC) |
|-----------|-----|-----------------|
| OBS Studio | ~500 MB | ~3-5% |
| Django + Workers | ~200 MB | ~5% |
| VLC (audio) | ~50 MB | ~2% |
| Chrome (juego) | ~500 MB | ~5% |
| **Total por instancia** | **~1.2-1.5 GB** | **~15%** |

## OBS Multi-instancia

### Windows
```bash
# Multiples instancias con perfiles separados
obs64.exe --multi --portable
```
- Soportado nativamente con `--multi`
- Cada instancia tiene su propia configuracion
- Cada una apunta a su propio RTMP (stream key de TikTok)

### macOS
- OBS **no soporta** `--multi` nativamente
- Workarounds: duplicar .app o usar contenedores
- No recomendado para streams, mejor usar Mac como orquestador

## Aislamiento de audio (Windows)

Cada instancia necesita su propio canal de audio para que OBS capture solo el audio de ESA instancia.

### Software necesario
- **VB-Audio Virtual Cable** (gratuito, 1 cable) + packs adicionales (~$10 por pack de cables extra)
- **VoiceMeeter Banana** (gratuito/donationware) para routing avanzado

### Configuracion por instancia

```
Instancia 1:
  VLC → --aout=directsound --directx-audio-device="CABLE-A Output"
  Chrome → Windows App Volume Mixer → CABLE-A Output
  OBS #1 → Captura audio de "CABLE-A Output"

Instancia 2:
  VLC → --directx-audio-device="CABLE-B Output"
  Chrome → CABLE-B Output
  OBS #2 → Captura audio de "CABLE-B Output"

(repetir por cada instancia)
```

### Cambio necesario en el codigo
En `Config` de Django agregar `audio_device` por instancia para que VLC rutee al cable virtual correcto. El parametro se pasa al comando VLC en `ElevenLabsClient` y `MusicPlayer`.

## Proxies (OBLIGATORIO para multi-cuenta)

Cada cuenta de TikTok necesita IP diferente. TikTok detecta multiples cuentas en la misma IP.

### Tipos de proxy (de mejor a peor para TikTok)

| Tipo | Deteccion | Costo/mes | Recomendado |
|------|-----------|-----------|-------------|
| 4G/5G movil | Muy baja | $25-40 | Si (mejor opcion) |
| Residencial estatico | Baja | $20-30 | Si |
| Residencial rotativo | Baja | $15-25 | Si, pero IP cambiante |
| Datacenter | Alta | $5-10 | NO - TikTok los detecta |

### Requisito critico
La IP del proxy **debe ser del mismo pais que la cuenta**. TikTok usa IP como senal principal para determinar audiencia del live.

```
Cuenta US → Proxy residencial US → Audiencia US ($$$)
Cuenta UK → Proxy residencial UK → Audiencia UK ($$)
Cuenta US + IP Colombia → Mismatch → Throttling
```

## Arquitectura distribuida (futuro)

```
MacBook (Cerebro):
  - Dashboard web central
  - Base de datos MySQL centralizada
  - API de control
  - Monitoreo de todos los nodos

PC de Mesa (Nodo 1):           Laptop Windows (Nodo 2):
  - 7-8 instancias OBS           - 3-4 instancias OBS
  - Django x 7-8                  - Django x 3-4
  - NVENC encoding                - NVENC encoding

Todos en la misma red local.
```

## Configuracion OBS recomendada (por stream)

```
Encoder:     NVENC (si hay GPU) / x264 ultrafast (si no)
Resolution:  720p (1280x720)
FPS:         30
Bitrate:     2500-3000 kbps
Profile:     Main
Preset:      Quality (NVENC) / ultrafast (x264)
```

TikTok recomienda 720p. En pantalla de celular nadie nota diferencia con 1080p, y ahorra recursos.

## Ancho de banda necesario

```
Por stream: ~3 Mbps upload
5 streams:  ~15 Mbps
10 streams: ~30 Mbps
12 streams: ~36 Mbps

Verificar que tu conexion de internet tenga suficiente upload.
```
