# Tug of War - Prototipo Interactivo para TikTok Live

## Descripcion General

Prototipo standalone de un juego interactivo "Tug of War" (Jalar la Cuerda) diseñado para TikTok Live. Los viewers donan regalos reales de TikTok para apoyar a su bando. El bando que acumule mas puntos de ventaja gana la ronda.

El prototipo es un archivo HTML puro (`tug-of-war.html`) con CSS y JavaScript, sin dependencias externas ni conexion al backend Django. Los botones simulan las donaciones que en produccion llegarian via `TikTokLiveClient`.

---

## Como Ejecutar

1. Abrir `tug-of-war.html` en Chrome
2. Click o presionar cualquier tecla en la pantalla de inicio para desbloquear el audio
3. Usar los botones o atajos de teclado para simular donaciones

### Atajos de Teclado

| Tecla | Accion |
|-------|--------|
| 1 | Hombres: GG (1 moneda) |
| 2 | Hombres: Fuegos artificiales (5 monedas) |
| 3 | Hombres: Estrella (10 monedas) |
| 8 | Mujeres: Helado (1 moneda) |
| 9 | Mujeres: Corazon coreano (5 monedas) |
| 0 | Mujeres: Rosa (10 monedas) |

---

## Mecanica del Juego

### Sistema de Puntuacion

- Cada regalo suma su valor en monedas al bando correspondiente
- La barra de progreso y la pared se mueven segun la **diferencia de puntos** (no el ratio)
- **WIN_DIFF = 50**: El primer bando que saque 50 puntos de ventaja gana la ronda
- La barra empieza 50/50 y se mueve proporcionalmente a la diferencia

### Regalos Asignados por Bando

| Bando | Regalo | Valor | Imagen |
|-------|--------|-------|--------|
| Hombres | GG | 1 moneda | `img/gifts/gg.webp` |
| Hombres | Maracas | 1 moneda | `img/gifts/maracas.webp` |
| Hombres | Fuegos artificiales | 5 monedas | `img/gifts/fireworks.webp` |
| Hombres | Estrella | 10 monedas | `img/gifts/star.webp` |
| Mujeres | Cono de helado | 1 moneda | `img/gifts/ice_cream.webp` |
| Mujeres | Te adoro | 1 moneda | `img/gifts/love_you.webp` |
| Mujeres | Corazon coreano | 5 monedas | `img/gifts/korean_heart.webp` |
| Mujeres | Rosa | 10 monedas | `img/gifts/rosa.webp` |

Las imagenes son iconos reales del CDN de TikTok descargados localmente.

### Escalado de Personajes

Los personajes cambian de tamano segun la diferencia de puntos:
- Empate: ambos al 100%
- Ganando: crece hasta 130%
- Perdiendo: se encoge hasta 70%

### Rondas y Gloria

- **GLORY_ROUNDS = 5**: El primer bando que gane 5 rondas dispara el "Glory Moment"
- Tras el Glory, el marcador global se reinicia y comienza un nuevo ciclo
- Los trofeos acumulados (cuantas veces un bando ha ganado el Glory) se mantienen durante todo el live
- Una sola categoria por sesion de live (no rota entre rondas)
- **ROUND_SECONDS = 180**: Cada ronda dura maximo 3 minutos. Si nadie llega a WIN_DIFF, gana el que tiene mas puntos

---

## Efectos Visuales

### Sistema de Particulas (Canvas)

Canvas HTML5 que renderiza particulas en tiempo real:
- **Particulas ambientales**: flotan suavemente de fondo
- **Burst de donacion**: explota particulas del color del bando al donar
- **Sparks en la pared**: chispas cada vez que se dona
- **Escala con el valor**: regalos mas caros generan mas particulas

### Efectos por Valor de Regalo

| Valor | Efectos |
|-------|---------|
| 1 moneda | Burst pequeno + sparks en pared |
| 5 monedas | Burst grande + shake + lightning + shockwave + 30% chance de TTS hype |
| 10 monedas | Espectaculo completo: triple burst escalonado, triple lightning, doble shockwave, lluvia de particulas, texto "REGALAZO" en pantalla, TTS |

### Aura de Fuego (Flame Aura System)

Sistema de llamas renderizado en canvas dedicado por personaje, activado por combos:
- Canvas separado por personaje que sigue su posicion
- Se redimensiona dinamicamente para llamas mas grandes
- Particulas tipo `FlameParticle` con fisica propia (gravedad, wobble, drift)
- Colores evolucionan con la intensidad:
  - Bajo: solo color del equipo
  - Medio: centro amarillo, puntas del color
  - Alto: centro blanco caliente, capas naranja/rojo
  - Godlike: nucleo electrico blanco, multiples capas
- Glow central radial que crece con la intensidad
- Se apaga suavemente (fade out) cuando el combo expira

### Fondo Dinamico

- Gradiente radial que cambia de color segun quien domina
- Edge glow pulsante en los bordes cuando un bando esta cerca de ganar

### Screen Shake

Dos niveles de intensidad (`shake-light`, `shake-heavy`) aplicados al contenedor principal. Se activa con donaciones grandes y momentos criticos.

---

## Sistema de Combos

### Deteccion

- Cada bando tiene su streak **independiente**
- Ventana de 2 segundos entre donaciones para mantener el combo
- Decay timer de 2.5 segundos: si no se dona, el combo se pierde

### Tiers

| Tier | Combo | Nombre | Tamano texto | Efectos adicionales |
|------|-------|--------|-------------|---------------------|
| 1 | 3-4x | COMBO | 36px | - |
| 2 | 5-7x | SUPER | 48px | Screen shake |
| 3 | 8-11x | MEGA | 64px | Screen shake + particulas al centro |
| 4 | 12-19x | ULTRA | 80px | + lightning |
| 5 | 20+x | GODLIKE | 110px | + doble lightning + lluvia de particulas |

### Mensajes Aleatorios por Tier

| Tier | Mensajes posibles |
|------|-------------------|
| 1 | COMBO!, NICE!, DALE! |
| 2 | SUPER!, ON FIRE!, VAMOS! |
| 3 | MEGA!, BRUTAL!, IMPARABLE! |
| 4 | ULTRA!, DESTRUCCION!, LOCURA! |
| 5 | GODLIKE!, LEGENDARIO!, APOCALIPSIS!, DIOS MIO! |

### Animaciones de Combo

- Rotacion minima (max 1-3 grados) para no ser excesiva
- Escala progresiva segun el tier
- Cada combo muestra el nombre del donador debajo del texto
- Contador persistente en la esquina del bando mientras dura el combo

### TTS en Combos

- Solo se reproduce TTS al **subir de tier** (no en cada hit)
- Usa la voz del bando que hace el combo (masculina para hombres, femenina para mujeres)

---

## Danger Zone

Se activa cuando la diferencia de puntos llega al 65% del WIN_DIFF (32.5 puntos con WIN_DIFF=50).

### Efectos en el Personaje Perdedor

- **Temblor**: animacion `dangerTremble` a 0.3s, movimiento lateral de 3px
- **Oscurecimiento**: brightness 0.6, saturacion al 30%
- **Semi-transparencia**: opacity 0.55
- **Glow rojo**: drop-shadow rojo
- **Sin llamas**: el danger NO usa el sistema de llamas (eso es exclusivo de combos)

### Audio

- Sonido de alarma (sfx sintetizado) cada 5 segundos
- TTS: "Estan en peligro" o "A punto de perder" segun la severidad
- Drum roll en loop mientras dura el peligro

---

## Comeback

Se activa cuando un bando estaba perdiendo fuerte (normalized < -0.5) y remonta hasta cerca del empate (normalized >= -0.1).

### Efectos

- Banner "COMEBACK!" con nombre del equipo
- Sonido: reverse sweep + power chord + cymbal + sparkles ascendentes
- SFX: impacto dramatico (`sfx_comeback_hit.mp3`)
- TTS: "COMEBACK!" o "LA REMONTADA!" con la voz del bando
- Explosion de particulas del lado que remonta
- Screen shake fuerte
- Solo se activa una vez por equipo por ronda

---

## Tension Final (Ultimos 30 Segundos)

### Efectos

- **Vignette roja** en los bordes de la pantalla
- **Progress bar pulsa** con efecto heartbeat
- **Heartbeat sonoro** que se acelera a medida que baja el tiempo
- **TTS "Ultimos 30 segundos!"** al activarse
- **TTS "DIEZ SEGUNDOS!"** al llegar a 10s
- **Timer tick** sonoro los ultimos 10 segundos
- Timer visual se pone rojo y parpadea

---

## Victoria de Ronda (Cinematica)

Diseño intencionalmente diferente a todo lo demas del juego para que se distinga del caos visual:

### Elementos

- **Barras negras** letterbox arriba y abajo (como pelicula)
- **Dimmer**: fondo se oscurece al 50%
- **Texto blanco limpio** con fuente Inter (NO Bebas Neue, NO color del equipo, NO glow)
- **"RONDA X"** pequeno arriba, nombre del equipo grande abajo
- **Linea de acento** del color del equipo debajo del texto (unico toque de color)
- **Score global** debajo en gris ("3 - 2")

### Audio

- Sonido sintetizado: golpe grave seco + tono limpio (diferente a combos/regalos)
- SFX: fanfarria de trompetas (`sfx_round_win_fanfare.mp3`)
- TTS: "SIIII! GANAMOS ESTA RONDA!" o "ESA ES LA NUESTRA! VAMOS!" con la voz del bando ganador

### Timing

- Duracion total: 2.5 segundos
- Siguiente ronda arranca inmediatamente despues

---

## Glory Moment

Se dispara cuando un bando acumula 5 victorias de ronda (GLORY_ROUNDS).

### Diferencias con Victoria de Ronda

El Glory es un evento a pantalla completa completamente diferente:

- **Flash blanco** de entrada
- **Fondo radial** del color del ganador que pulsa
- **Emoji gigante** (200px) que entra rotando 180 grados
- **"GLORY"** en dorado con triple glow, texto que explota desde grande
- **Nombre del equipo** animado
- **Trofeos acumulados** debajo
- **Lluvia de 30 trofeos/coronas/estrellas** cayendo
- **5 explosiones de particulas** escalonadas en posiciones aleatorias
- **Triple confetti** (dorado + color + dorado + color + blanco)
- **Triple lightning** (dorado + color + blanco)
- **Screen shake** triple (pesado, medio, suave)

### Audio

- SFX: himno de victoria epico (`sfx_glory_anthem.mp3`)
- Sonido sintetizado: fanfarria masiva con doble hit
- TTS: "GLORY! CAMPEONES!" o "VICTORIA ABSOLUTA!" con la voz del bando

### Post-Glory

- Duracion: 6 segundos
- Marcador global se reinicia a 0-0
- Trofeos de series ganadas se mantienen permanentemente
- Nueva ronda arranca automaticamente

---

## Scoreboard Lateral

Siempre visible a los lados de la pantalla:

- **Numero de wins** por bando (color del equipo)
- **Pips** (bolitas) que se van llenando con animacion pop al ganar cada ronda
- **Trofeos** acumulados de series completas ganadas

---

## Pantalla de Inicio

Obligatoria para desbloquear el audio del navegador:

- Emojis del versus con espada
- Titulo de la categoria con gradiente de colores
- "TUG OF WAR" en subtitulo
- "CLICK PARA COMENZAR" parpadeando
- Al interactuar: desbloquea AudioContext y arranca la primera ronda

---

## Sistema de Audio

### Capa 1: Web Audio API (Sonidos Sintetizados)

Generados en tiempo real con osciladores y noise:

| Funcion | Descripcion |
|---------|-------------|
| `sfxRosa(pan, p)` | Blip suave para regalos de 1 moneda |
| `sfxHelado(pan, p)` | Whoosh + tono grave + sparkle para 5 monedas |
| `sfxRegalo(pan, p)` | Explosion epica: sub-bass + sweep + chord + cascada |
| `sfxCombo(tier, isLeft)` | 5 niveles escalando de blip a explosion multicapa |
| `sfxWallClash(amount)` | Impacto en la pared, escala con el monto |
| `sfxDangerAlarm()` | Sirena corta de dos tonos |
| `sfxComeback()` | Reverse sweep + power chord + cymbal |
| `sfxTimerTick()` | Tick de urgencia |

**Pitch diferenciado**: Hombres usan multiplicador 0.75 (grave), mujeres 1.3 (agudo). Cada bando tiene identidad sonora propia.

**Paneo stereo**: Hombres a la izquierda (-0.5), mujeres a la derecha (+0.5).

### Capa 2: TTS Pregenerados (ElevenLabs v3)

Clips de voz generados con ElevenLabs API usando el modelo `eleven_v3` con audio tags para maxima expresividad.

**Voces:**
- Masculina: Josh (`TxGEqnHWrfWFTfGW9XjX`) - voz joven, autoritaria
- Femenina: Rachel (`21m00Tcm4TlvDq8ikWAM`) - voz clara, energetica

**Audio tags utilizados:** `[shouts]`, `[excited]`, `[curious]`, `[applause]`, `[laughs]`

**Parametro `language_code: "es"`** para forzar español nativo.

#### Clips TTS (por genero, 26 clips x 2 voces = 52 total)

| ID | Texto | Momento |
|----|-------|---------|
| `round_start_1` | "PELEEN!" | Inicio de ronda |
| `round_start_2` | "A LA GUERRA!" | Inicio de ronda (alt) |
| `combo_t1` | "Combo!" | Tier 1 |
| `combo_t2` | "Super!" | Tier 2 |
| `combo_t3_a/b` | "MEGA!" / "BRUTAL!" | Tier 3 |
| `combo_t4_a/b` | "ULTRA!" / "DESTRUCCION!" | Tier 4 |
| `combo_t5_a/b` | "GODLIKE!" / "LEGENDARIO!" | Tier 5 |
| `danger_1` | "Estan en peligro!" | Danger zone |
| `danger_critical` | "A punto de perder!" | Danger critico |
| `comeback_1/2` | "COMEBACK!" / "LA REMONTADA!" | Comeback |
| `round_win_1/2` | "SIIII! GANAMOS!" / "ESA ES LA NUESTRA!" | Victoria de ronda |
| `regalo_1` | "REGALAZO!" | Regalo de 10 monedas |
| `tension_30s` | "Ultimos 30 segundos!" | 30s restantes |
| `tension_10s` | "DIEZ SEGUNDOS!" | 10s restantes |
| `glory_1/2` | "GLORY! CAMPEONES!" / "VICTORIA ABSOLUTA!" | Glory moment |
| `empate` | "EMPATE! Tiempo extra!" | Empate |
| `hype_1/2/3/4` | "Ohhh!" / "Vamos!" / "Esta parejo!" / "Que locura!" | Reacciones random |

**Regla anti-overlap:** Flag `ttsPlaying` previene que dos TTS suenen al mismo tiempo.

**TTS en combos:** Solo se reproduce al subir de tier, no en cada hit del combo.

### Capa 3: SFX Musicales (ElevenLabs Sound Effects v2)

Generados con la API `text-to-sound-effects` de ElevenLabs.

| Archivo | Uso | Duracion | Loop | Volumen |
|---------|-----|----------|------|---------|
| `sfx_battle_loop.mp3` | Musica de fondo durante la batalla | 30s | Si | 25% |
| `sfx_round_win_fanfare.mp3` | Trompetas al ganar ronda | 3s | No | 50% |
| `sfx_glory_anthem.mp3` | Himno de victoria Glory | 8s | No | 60% |
| `sfx_drum_roll.mp3` | Redoble cuando alguien esta en danger | 5s | Si | 40% |
| `sfx_countdown_tick.mp3` | Tick tock de tension | 3s | Si | - |
| `sfx_comeback_hit.mp3` | Impacto dramatico en comeback | 2s | No | 60% |

**Variantes de battle loop:** Se generaron 12 variantes (`v1` a `v12`) con diferentes estilos. La activa es `v3` (arcade fighting game). Las demas se conservan en `audio/sfx/` para pruebas.

---

## Categorias Disponibles

El prototipo incluye 8 categorias predefinidas. Solo se usa una por sesion de live (no rota entre rondas).

| Categoria | Titulo | Emojis | Colores |
|-----------|--------|--------|---------|
| Genero | HOMBRES vs MUJERES | 👨 vs 👩 | Azul / Rosa |
| Deporte | MESSI vs CR7 | 🇦🇷 vs 🇵🇹 | Azul / Rojo |
| Generacion | GEN Z vs MILLENNIALS | 📱 vs 💻 | Purpura / Naranja |
| Mascota | PERRO vs GATO | 🐕 vs 🐈 | Naranja / Purpura |
| Paises | MEXICO vs COLOMBIA | 🇲🇽 vs 🇨🇴 | Verde / Amarillo |
| Estacion | VERANO vs INVIERNO | ☀️ vs ❄️ | Naranja / Azul |
| Opinion | PIZZA vs HAMBURGUESA | 🍕 vs 🍔 | Rojo / Naranja |
| Personalidad | INTROVERTIDOS vs EXTROVERTIDOS | 📖 vs 🎉 | Indigo / Rosa |

Para cambiar la categoria activa, modificar `currentCategory` en el codigo (indice 0-7).

---

## Generacion de Audio

### Script: `generate_audio.py`

Script Python standalone que genera todos los clips de audio usando las APIs de ElevenLabs.

#### Uso

```bash
# Generar todos los clips (TTS + SFX)
python generate_audio.py TU_API_KEY

# Regenerar todos (sobreescribe existentes)
python generate_audio.py TU_API_KEY --force

# Listar voces disponibles
python generate_audio.py TU_API_KEY --list-voices

# Listar modelos disponibles
python generate_audio.py TU_API_KEY --list-models
```

#### Requisitos

- Python 3
- `requests` (`pip install requests`)
- API key de ElevenLabs con permiso `text_to_speech`

#### APIs Utilizadas

| API | Modelo | Uso |
|-----|--------|-----|
| Text-to-Speech | `eleven_v3` | Voces TTS con audio tags |
| Sound Generation | `eleven_text_to_sound_v2` | SFX musicales |

#### Estructura de Salida

```
audio/
├── male/           # 26 clips voz masculina (Josh)
├── female/         # 26 clips voz femenina (Rachel)
├── sfx/            # 6 clips SFX + 12 variantes de battle loop
└── manifest.json   # Indice de todos los clips
```

---

## Estructura de Archivos

```
prototypes/
├── tug-of-war.html          # Prototipo principal (HTML/CSS/JS)
├── generate_audio.py         # Script generador de audio
├── README.md                 # Esta documentacion
├── audio/
│   ├── male/                 # TTS voz masculina (26 clips)
│   ├── female/               # TTS voz femenina (26 clips)
│   ├── sfx/                  # Efectos de sonido y musica
│   │   ├── sfx_battle_loop.mp3      # Musica de fondo activa
│   │   ├── sfx_battle_loop_v1-v12.mp3  # Variantes
│   │   ├── sfx_round_win_fanfare.mp3
│   │   ├── sfx_glory_anthem.mp3
│   │   ├── sfx_drum_roll.mp3
│   │   ├── sfx_countdown_tick.mp3
│   │   └── sfx_comeback_hit.mp3
│   └── manifest.json
└── img/
    └── gifts/                # Iconos reales de regalos TikTok
        ├── gg.webp
        ├── maracas.webp
        ├── fireworks.webp
        ├── star.webp
        ├── ice_cream.webp
        ├── love_you.webp
        ├── korean_heart.webp
        └── rosa.webp
```

---

## Configuracion Rapida

Constantes al inicio del script JS en `tug-of-war.html`:

```javascript
const ROUND_SECONDS = 180;    // Duracion maxima de ronda (3 min)
const WIN_DIFF = 50;          // Diferencia de puntos para ganar
const GLORY_ROUNDS = 5;       // Rondas para Glory Moment
const GLORY_DELAY = 6000;     // Duracion del Glory en pantalla (ms)
const AUTO_RESTART_DELAY = 2500; // Pausa entre ronda ganada y siguiente (ms)
```

---

## Principios de Diseño

Basados en el documento `docs/tiktok-farm/juegos-interactivos.md`:

1. **Enganche en 3 segundos**: Pantalla de inicio rapida, accion inmediata
2. **Identidad involuntaria**: Los regalos asignan bando automaticamente
3. **Competencia visible**: Barra, personajes, combos - todo es visual
4. **Ciclos cortos**: Rondas de 1-3 min, Glory cada 5 rondas
5. **Dopamina visual**: Particulas, llamas, combos escalantes
6. **Sin solicitud de donaciones**: JAMAS se pide donar en TTS ni en texto
7. **Audio diferenciado**: Voz masculina grave, femenina aguda - identidad sonora por bando

---

## Integracion con Django (Pendiente)

El prototipo esta diseñado para ser portado al sistema Django existente:

1. Servir el HTML como OBS Browser Source via Django view
2. Reemplazar los botones por eventos SSE desde `EventDispatcher`
3. El `TikTokLiveClient` captura el regalo → mapea nombre a bando → envia via SSE
4. El frontend recibe el evento y llama a `donate(bando, valor)` automaticamente
5. Los TTS y SFX se pueden servir como static files de Django
