# Estrategia de Contenido

## Principio fundamental

El sistema automatizado con juegos interactivos es la ventaja competitiva. Cada gift dispara una accion visible en tiempo real, lo que genera un loop de dopamina: viewer regala → ve reaccion → quiere regalar mas.

Esto replica el modelo NPC que ha demostrado ser extremadamente rentable en TikTok Live.

## Catalogo de juegos interactivos (20 ideas)

### Tier 1: Faciles (1-2 dias desarrollo)

| # | Juego | Que ve el viewer | Que hacen los gifts | Potencial gifting |
|---|-------|-----------------|--------------------|-|
| 1 | **Dino Chrome** (existente) | Dino corriendo auto-play | Rosa=restart+TTS, Ice cream=GIFs | Medio |
| 2 | **Ruleta de la fortuna** | Ruleta girando | Gift=spin, resultado genera TTS comico | Alto |
| 3 | **Acuario** | Pecera con peces | Gift=nuevo pez con nombre del viewer | Medio |
| 4 | **Jardin/Arbol** | Planta creciendo | Gift=crece, florece, cambia estacion | Medio |
| 5 | **Contador de metas** | Barra de progreso | Gift=avanza, al llegar a meta pasa algo epico | Alto |
| 6 | **Plinko/Pachinko** | Tablero con clavos | Gift=suelta bolita, cae en premio/castigo | Alto |

### Tier 2: Complejidad media (2-4 dias)

| # | Juego | Que ve el viewer | Que hacen los gifts | Potencial gifting |
|---|-------|-----------------|--------------------|-|
| 7 | **Flappy Bird** | Pajaro volando | Gift=obstaculo o power-up | Medio |
| 8 | **Snake** | Serpiente clasica | Gift=comida o bomba | Medio |
| 9 | **Tetris inverso** | Tablero tetris | Gift=lanza pieza al azar | Medio-Alto |
| 10 | **Slot Machine** | Tragamonedas | Gift=spin, 3 iguales=explosion | Muy alto |
| 11 | **Tower Stacker** | Torre de bloques | Gift=nuevo bloque, si cae colapsa | Alto |
| 12 | **Batallas de viewers** | Arena 2D | Gift=spawnea luchador con tu nombre | Muy alto |
| 13 | **Mascota virtual** | Tamagotchi | Gift=alimentar, se muere si nadie dona | Alto |

### Tier 3: Complejos (4-7 dias)

| # | Juego | Que ve el viewer | Que hacen los gifts | Potencial gifting |
|---|-------|-----------------|--------------------|-|
| 14 | **Battle Royale** | Mapa con personajes | Gift=tu personaje, ultimo en pie gana | Muy alto |
| 15 | **Carrera de obstaculos** | Pista con corredores | Gift=tu corredor, comments=power-ups | Alto |
| 16 | **Subastas locas** | Objeto ridiculo | Gifts=pujas, mayor gana TTS | Muy alto |
| 17 | **Dungeon crawler** | Mazmorras 2D | Gift=avanza, TTS narra | Alto |
| 18 | **Piano/DJ** | Teclado musical | Gifts=tocan notas | Medio-Alto |
| 19 | **Invasion alien** | Naves atacando | Gifts=disparo, Rose=bomba nuclear | Alto |
| 20 | **Trivia (Millonario)** | Preguntas trivia | Comments=respuestas, gifts=comodines, LLM genera preguntas | Muy alto |

### TOP 5 por potencial de gifting

1. **Slot Machine** - Dopamina pura, "una mas, una mas"
2. **Batallas de viewers** - Competencia = viewers regalando para ganar
3. **Plinko/Pachinko** - Visual + azar, adictivo
4. **Contador de metas** - "Faltan $5 para la meta!" = presion social
5. **Ruleta de fortuna** - Simple, visual, impredecible

**Patron comun**: Azar + resultado visible + nombre del viewer en pantalla = gifting compulsivo.

## Arquitectura tecnica de los juegos

Cada juego nuevo requiere:

```
1. Frontend web (HTML/JS/CSS) → Browser Source en OBS
2. Service class que hereda de BaseQueueService
3. process_event(live_event, queue_item) → reacciona a gifts/comments
4. ServiceEventConfig en admin → prioridades por evento
```

El queue system, dispatcher, workers, TTS, LLM y overlays ya existen. Cada juego solo cambia el frontend y la logica en `process_event()`.

## Rotacion de juegos por cuenta

```
Cuenta 1 (US):     Slot Machine + TTS ingles americano
Cuenta 2 (US):     Battle Royale + TTS ingles diferente voz
Cuenta 3 (UK):     Plinko + TTS ingles britanico
Cuenta 4 (Arabia): Ruleta + TTS arabe
Cuenta 5 (US):     Trivia + LLM generando preguntas

Cada cuenta = juego diferente + voz diferente + tematica diferente
Para TikTok: cuentas completamente distintas
Para ti: mismo sistema, diferente frontend
```

## Optimizacion de lives

### Duracion optima de live

Las guias genericas dicen 30-90 minutos, pero eso es para streamers "normales" (persona hablando a camara). El contenido interactivo automatizado puede funcionar con duraciones mas largas porque:
- No depende de la energia del streamer
- Cada gift genera novedad
- Es mas parecido a un arcade que a un vlog

**Recomendacion**: Testear duraciones incrementales con la primera cuenta (1hr, 2hr, 4hr) y medir en que minuto caen los viewers usando `ViewerCountEvent`.

### Frecuencia de lives

**Lo que NO funcionar (experiencia propia):**
- 4 lives/dia x 2-3 hrs = viewers cayendo dia a dia
- Causa: fatiga algoritmica + fatiga de audiencia + notificaciones ignoradas

**Lo recomendado (por la investigacion):**
- 1 live/dia por cuenta
- Horario fijo (misma hora cada dia)
- 5-6 dias por semana (1-2 dias descanso)
- Peak hours del pais target

**Pero para contenido interactivo**: estos limites podrian ser menos estrictos. Validar con datos reales.

### Horarios pico por region

| Region | Peak hours (hora local) |
|--------|------------------------|
| US East | 7-11 PM EST |
| US West | 7-11 PM PST |
| UK | 7-10 PM GMT |
| Arabia | 9 PM - 1 AM AST |

### Cosas que causan shadow ban en lives (EVITAR)

| Accion | Consecuencia |
|--------|-------------|
| Pedir gifts repetidamente | Throttling inmediato |
| Mostrar Cash App / PayPal en overlays | Restriccion de alcance |
| Contenido de baja energia / camara fija | Visibilidad reducida |
| Contenido en loop / pre-grabado | Penalizacion |
| Reiniciar el live multiples veces | Reduce promocion algoritmica |
| Musica con copyright | Mute o fin del stream |
| Contenido sexual/violento | Ban |

**Tip critico**: Si algo falla en el live, NO reinicies. Usa la funcion de pausa. Reiniciar mata el momentum algoritmico.

## Datos de analytics implementados

El sistema ahora captura `ViewerCountEvent` (via `RoomUserSeqEvent` de TikTokLive) que registra:
- `viewer_count` (viewers concurrentes)
- `total_viewers` (acumulado)
- `total_user` (usuarios unicos)
- `anonymous` (viewers anonimos)

Combinado con `LiveSession.game_type` y `LiveSession.account` (FK a `TikTokAccount`), se pueden hacer queries como:
- Revenue por pais
- Que juego genera mas en US
- A que minuto del live empieza a caer la audiencia
- Comparar sesiones por duracion, horario, dia de la semana
