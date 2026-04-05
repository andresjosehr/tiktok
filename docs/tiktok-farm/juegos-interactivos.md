# Juegos Interactivos - Catalogo y Diseno

## Modelo de audiencia

Este sistema NO depende de audiencia fija ni seguidores. Los viewers llegan por FYP, se enganchan un rato, donan, se van y no vuelven. Cada viewer es nuevo. Esto significa:

- No existe fatiga de contenido (cada viewer lo ve 1 sola vez)
- No hay que rotar juegos por "psicologia" sino por datos de revenue
- El enganche instantaneo (3 segundos) es lo mas importante
- Rondas cortas (3-5 min) porque el viewer promedio no se queda mucho

## Principios de diseno

Todos los juegos deben cumplir estos principios, ordenados por importancia para el modelo FYP:

```
P1: ENGANCHE EN 3 SEGUNDOS
    Se entiende sin audio, sin contexto, sin leer.
    Viewer cae del FYP y en 1-3 segundos sabe que esta pasando.

P2: IDENTIDAD INVOLUNTARIA
    El viewer ya pertenece a un bando por lo que ES
    (genero, signo, nacionalidad, edad). No tiene que elegir nada.

P3: COMPETENCIA VISIBLE
    Algo se mueve, alguien va ganando. El resultado esta siempre
    en duda. Genera urgencia de donar AHORA.

P4: COBERTURA TOTAL
    Toda la audiencia tiene bando. No hay neutrales.
    100% de los viewers son participantes potenciales.

P5: CICLOS CORTOS
    Rondas de 3-5 minutos. El viewer que cae a mitad de ronda
    ve que falta poco, dona rapido, ve resultado, se queda para
    la siguiente.

P6: DOPAMINA VISUAL
    Cada gift genera movimiento/efecto inmediato en pantalla.
    El viewer VE su impacto al instante.

P7: HUMILLACION COMICA (opcional pero poderoso)
    El bando perdedor recibe castigo visual/sonoro comico.
    Genera clips virales que atraen mas viewers al live.
```

## Por que estos principios son mejores que juegos individuales

```
Juegos individuales (Slot Machine, Plinko, etc.):
  - Motivacion: "Quiero ver que pasa" (individual)
  - Dona 1 vez, ya vio el resultado
  - Se aburre rapido

Juegos tribales (Tug of War, Race, etc.):
  - Motivacion: "MI GRUPO tiene que ganar" (tribal)
  - Dona N veces porque la pelea sigue
  - Se queda hasta que su grupo gane
  - Presion social: "mi grupo pierde POR MI CULPA si no dono"
```

## Banco de categorias (compartido entre todos los juegos)

La mecanica del juego se mantiene, lo que cambia por ronda es la categoria:

| Tipo | Ejemplos | Cobertura audiencia |
|---|---|---|
| Genero | Hombres vs Mujeres | 100% |
| Zodiaco | Aries vs Libra, Fuego vs Agua | 100% |
| Nacionalidad | Mexico vs Colombia, US vs UK | ~100% |
| Generacion | Gen Z vs Millennials vs Boomers | 100% |
| Opinion | Perro vs Gato, Messi vs CR7 | ~100% |
| Comida | Pizza vs Hamburguesa, Tacos vs Sushi | ~100% |
| Musica | Reggaeton vs Rock, Bad Bunny vs Shakira | ~100% |
| Deporte | Futbol vs Basketball | Alto |
| Series | Netflix vs Disney+, Anime vs Series | Alto |
| Estaciones | Verano vs Invierno | 100% |
| Personalidad | Introvertidos vs Extrovertidos | 100% |
| Hora del dia | Madrugadores vs Nocturnos | 100% |
| Relacion | Solteros vs En relacion | 100% |
| Cafe | Cafe vs Te | ~100% |
| Gaming | PlayStation vs Xbox, PC vs Consola | Alto |

Las categorias rotan entre rondas automaticamente. Esto da contenido infinito sin cambiar de juego.

## Arquitectura tecnica (todos los juegos)

Diferencia fundamental con DinoChrome:

```
DinoChrome (complejo):
  Selenium → controla Chrome externo → webdriver → xvfb
  Pesado, fragil, muchas dependencias

Juegos nuevos (simples):
  OBS Browser Source → apunta a localhost:8000/games/nombre/
  Pagina HTML/CSS/JS propia
  Recibe eventos via SSE desde Django
  0 dependencias externas, ligero, estable
```

Cada juego es:
1. **Frontend**: HTML + CSS + JS (browser source para OBS)
2. **Service**: Clase que hereda de `BaseQueueService`
3. **process_event()**: Recibe gift → envia evento al frontend via SSE
4. **Admin**: ServiceEventConfig con prioridades por gift

---

## Catalogo de juegos

### Ranking por potencial FYP

| Tier | Juegos | Razon |
|------|--------|-------|
| **S** | Tug of War, Termometro | 2 bandos, enganche instantaneo, ultra simple |
| **A** | Race, Barra de Generaciones | Rapido de entender, multiples bandos claros |
| **B** | King of the Hill, Ruleta de Castigo, Zodiaco War | Requieren 5-10 seg para entender |
| **C** | Battle Royale, Torre de Babel, Invasion | Mucha info visual, enganche lento |

---

### S TIER

#### 1. Tug of War (Guerra de Empuje)

```
Visual:     Dos personajes/iconos empujando una pared vertical central.
            Barra de progreso abajo mostrando quien va ganando.
            Colores claros por bando (azul vs rosa, rojo vs verde, etc.)

Bandos:     Siempre 2 bandos. Cambia por ronda:
            - Hombres vs Mujeres
            - Aries vs Libra
            - Mexico vs Colombia
            - Gen Z vs Millennials
            - Perro vs Gato
            - (cualquier categoria del banco)

Mecanica:   Cada gift para un bando mueve la pared hacia el lado contrario.
            Gifts mas caros = mas movimiento.
            La pared se mueve en tiempo real con cada donacion.

Final:      Un lado empuja al otro fuera del escenario.
            Animacion de victoria + sonido.
            Opcional: TTS comico burlandose del perdedor (P7).

Reset:      Nueva ronda automatica con nueva categoria.
            3-5 minutos por ronda.

Engagement: El viewer cae del FYP, ve una barra moviendose entre
            HOMBRES y MUJERES. En 1 segundo entiende todo.
            "Soy hombre, no puedo dejar que pierdan" → dona.
```

**Principios**: P1 (instantaneo), P2, P3, P4, P5, P6, P7
**Complejidad de desarrollo**: Baja
**Prioridad**: #1

---

#### 2. Termometro de Popularidad

```
Visual:     Dos termometros/barras verticales lado a lado llenandose.
            Cada uno con su etiqueta y color.
            Porcentaje visible en cada barra.

Bandos:     Siempre 2 opciones. Cambia por ronda:
            - Messi vs CR7
            - Pizza vs Hamburguesa
            - Verano vs Invierno
            - Introvertidos vs Extrovertidos
            - (cualquier categoria del banco)

Mecanica:   Gifts llenan el termometro de tu opcion.
            Gifts mas caros = mas llenado.
            Ambas barras se llenan en paralelo.

Final:      Primero en llenar al 100% explota en celebracion.
            Confetti, sonido de victoria.
            Opcional: TTS anuncia ganador.

Reset:      Nueva pregunta/tema automatico.
            3-5 minutos por ronda.

Engagement: Dos barras llenandose lado a lado.
            Se entiende en 1 segundo. "Messi o CR7? Obvio Messi" → dona.
```

**Principios**: P1 (instantaneo), P3, P4, P5, P6
**Nota**: P2 parcial (es opinion, no identidad fija, pero genera tribalismo igual)
**Complejidad de desarrollo**: Baja
**Prioridad**: #1

---

### A TIER

#### 3. Race (Carrera)

```
Visual:     4-6 carriles horizontales con entidades avanzando
            hacia una linea de meta a la derecha.
            Cada carril tiene icono + nombre + barra de progreso.

Bandos:     4-6 opciones. Cambia por ronda:
            - 6 signos zodiacales (agrupados de a 6)
            - 4-5 paises (Mexico, Colombia, Argentina, Peru, Chile)
            - 4 generaciones
            - 4-6 equipos de futbol

Mecanica:   Cada gift para tu carril lo avanza.
            Gifts mas caros = mas avance.
            Los carriles avanzan a ritmos diferentes segun donaciones.

Final:      Primero en cruzar la meta gana.
            Animacion de llegada + podio.
            Opcional: TTS anuncia top 3.

Reset:      Nueva carrera con nueva categoria.
            3-5 minutos por carrera.

Engagement: Carriles avanzando como una carrera. Se entiende en
            2-3 segundos. "Mi pais va tercero, tengo que donar" → dona.
```

**Principios**: P1 (rapido), P2, P3, P4, P5, P6
**Complejidad de desarrollo**: Baja-Media
**Prioridad**: #2

---

#### 4. Barra de Generaciones

```
Visual:     Barra horizontal dividida en secciones de colores.
            Cada seccion = una generacion.
            La barra crece/encoge por seccion segun donaciones.

Bandos:     Gen Z vs Millennials vs Gen X vs Boomers
            (o simplificado: Gen Z vs Millennials)

Mecanica:   Donas para tu generacion → tu seccion crece.
            Las otras secciones se comprimen proporcionalmente.

Final:      La generacion con mayor seccion al terminar la ronda gana.
            Opcional: TTS "Ok boomer..." si Boomers pierden.

Reset:      Nueva ronda. 3-5 minutos.

Engagement: Barra de colores moviendose. Se entiende rapido.
            "Gen Z va perdiendo contra Millennials?? No!" → dona.
```

**Principios**: P1, P2 (edad), P3, P4, P5, P6, P7
**Complejidad de desarrollo**: Baja
**Prioridad**: #2

---

### B TIER

#### 5. King of the Hill (Rey de la Colina)

```
Visual:     Trono/podio central con avatar y nombre del "rey" actual.
            Contador de "precio" para destronar al rey.
            Historial de reyes anteriores.

Bandos:     Individual - no grupal.
            Cada viewer compite por ser el rey.

Mecanica:   Gift mas caro que el ultimo = te conviertes en rey.
            Tu nombre aparece en grande en el trono.
            Cada nuevo rey sube el precio minimo para destronarlo.

Final:      Al terminar la ronda (timer), el rey actual gana.
            TTS shoutout al ganador.

Reset:      Nueva ronda. 5-10 minutos.

Engagement: Guerra de egos individual. "Ese tipo es el rey?
            Con una Rosa lo destrono" → dona.
```

**Principios**: P3, P4 (parcial), P5, P6
**Nota**: NO cumple P2 (no es identidad, es ego individual). Funciona diferente: apela a la competitividad personal, no tribal. Puede ser menos efectivo para FYP pero genera donaciones altas por individuo.
**Complejidad de desarrollo**: Baja
**Prioridad**: #3

---

#### 6. Ruleta de Castigo

```
Visual:     Ruleta grande con secciones de colores.
            Cada seccion = un grupo (signo, pais, etc.)
            Indicador de "SPIN" parpadeando.

Bandos:     Todos. La ruleta tiene los grupos de la ronda actual.

Mecanica:   Gifts hacen girar la ruleta.
            Donde cae = ese grupo recibe "castigo" comico:
              - TTS burlandose de ese signo/pais/generacion
              - Animacion comica
            El grupo castigado dona para "defenderse" y girar de nuevo.

Final:      No hay final fijo. Rondas continuas.
            Cada spin es un micro-evento.

Engagement: Mecanica inversa: donas para NO ser castigado.
            "Le cayo a Aries, jajaja... espera, ahora va a caer en
            Escorpio, tengo que girar!" → dona.
```

**Principios**: P2, P3, P4, P5, P6, P7
**Nota**: P1 parcial - requiere ~5-10 seg para entender la mecanica de castigo.
**Complejidad de desarrollo**: Media
**Prioridad**: #3

---

#### 7. Zodiaco War

```
Visual:     Barra horizontal o arena circular con 12 signos (o 4 elementos).
            Cada signo tiene icono y barra de poder.

Bandos:     12 signos individualmente, o agrupados:
            - Fuego (Aries, Leo, Sagitario) vs Agua (Cancer, Escorpio, Piscis)
              vs Tierra (Tauro, Virgo, Capricornio) vs Aire (Geminis, Libra, Acuario)

Mecanica:   Gifts para tu signo/elemento aumentan su poder.
            Version simplificada: 4 barras (elementos) empujandose.
            Version compleja: 12 signos en battle royale por eliminacion.

Final:      El elemento/signo dominante gana.
            TTS se burla del signo perdedor.

Reset:      Nueva ronda. 5-10 minutos.

Engagement: Zodiaco genera tribalismo fuerte ("Yo soy Escorpio
            y somos los mejores"). Pero 12 opciones es mucha info visual.
            Mejor usar la version de 4 elementos para FYP.
```

**Principios**: P1 (si es 4 elementos; lento si son 12 signos), P2, P3, P4, P5, P6, P7
**Complejidad de desarrollo**: Media
**Prioridad**: #3

---

### C TIER

#### 8. Battle Royale de Paises

```
Visual:     Arena con banderas de paises.
            Cada pais tiene barra de vida.
            Paises van siendo eliminados.

Bandos:     Paises de los viewers (8-12 paises por ronda).

Mecanica:   Gifts = puntos de vida para tu pais.
            Paises atacan al mas debil periodicamente.
            Si tu pais llega a 0 → eliminado con animacion.

Final:      Ultimo pais en pie gana.

Reset:      Nueva ronda con diferentes paises. 10-20 minutos.

Engagement: Fuerte tribalismo nacional pero demasiada info visual
            para FYP. Rondas largas. Mejor para audiencia que se queda.
```

**Principios**: P2, P3, P4, P6, P7
**Nota**: Falla P1 (mucha info) y P5 (rondas largas)
**Complejidad de desarrollo**: Media-Alta
**Prioridad**: #4

---

#### 9. Torre de Babel

```
Visual:     Torre vertical construyendose bloque a bloque.
            Cada bloque tiene la bandera/icono del donante.
            La torre se tambalea mas a medida que crece.

Bandos:     Todos contribuyen. Compiten por quien puso mas bloques.

Mecanica:   Cada gift = un bloque con la identidad del donante.
            La torre se vuelve inestable y eventualmente colapsa.
            Al colapsar, el grupo con mas bloques "gana".

Final:      Colapso de la torre → conteo → ganador.

Reset:      Nueva torre. 5-10 minutos.

Engagement: Tension visual interesante (va a caer?) pero el concepto
            de "competir por bloques" no es instantaneo de entender.
```

**Principios**: P2, P3, P4, P6
**Nota**: Falla P1 (concepto abstracto) y P3 parcial (no es competencia directa)
**Complejidad de desarrollo**: Media
**Prioridad**: #4

---

#### 10. Invasion: Defiende tu Pais

```
Visual:     Mapa simplificado con paises.
            Aliens/monstruos atacando paises.
            Cada pais tiene barra de defensa.

Bandos:     Paises de los viewers.

Mecanica:   Gifts = disparos que defienden TU pais.
            Si nadie dona, tu pais cae (aliens lo conquistan).
            Animacion de invasion.

Final:      Ultimo pais en pie gana. Los demas fueron invadidos.

Reset:      Nueva ronda. 10-15 minutos.

Engagement: Concepto interesante pero mucha info visual.
            Rondas largas. Mecanica no obvia en 3 segundos.
```

**Principios**: P2, P3, P4, P6, P7
**Nota**: Falla P1 (complejo visualmente) y P5 (rondas largas)
**Complejidad de desarrollo**: Alta
**Prioridad**: #5

---

## Estrategia de rotacion

No se rotan juegos por sesion. Se rota la **categoria** dentro del mismo juego por ronda.

```
1 sesion de live con Tug of War:
  Ronda 1: Hombres vs Mujeres        (3-5 min)
  Ronda 2: Mexico vs Colombia         (3-5 min)
  Ronda 3: Gen Z vs Millennials       (3-5 min)
  Ronda 4: Perro vs Gato              (3-5 min)
  Ronda 5: Messi vs CR7               (3-5 min)
  ...
```

No hay necesidad de rotar juegos frecuentemente porque la audiencia es 100% FYP (cada viewer es nuevo). Se rota juego solo si los **datos de revenue** muestran que otro juego genera mas $/hora.

## Prioridad de desarrollo

```
Fase 1:  Tug of War + Termometro (S tier, desarrollo rapido, mayor ROI)
Fase 2:  Race + Barra de Generaciones (A tier)
Fase 3:  King of the Hill + Ruleta de Castigo (B tier)
Fase 4:  Resto segun datos de revenue de los primeros juegos
```

## DinoChrome vs juegos nuevos

```
DinoChrome:                          Juegos nuevos:
  Selenium + Chrome + webdriver        HTML/CSS/JS puro
  Juego externo con AI                 Pagina propia simple
  LLM + TTS + musica + GIFs           SSE + animaciones CSS
  SYNC blocking complejo               Evento llega, barra se mueve
  ~500MB RAM + mucho CPU              ~50MB RAM, casi 0 CPU
  Fragil (Chrome puede crashear)       Ultra estable
  Enganche lento (que es esto?)        Enganche en 3 segundos
  Sin tribalismo                       Tribalismo puro
```

DinoChrome sirvio para construir la infraestructura (queue system, dispatcher, workers, TTS, overlays). Esa infraestructura ahora se reutiliza para juegos mucho mas simples pero mas rentables.
