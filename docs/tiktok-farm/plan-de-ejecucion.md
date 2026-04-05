# Plan de Ejecucion

## Principio rector

Validar antes de escalar. Cada fase depende de los resultados de la anterior.

## Fase 0: Validacion del modelo (Semana 1-4)

**Objetivo**: Responder "cuanto genera mi sistema por hora con viewers reales?"

### Acciones
- [ ] Registrar cuenta actual en TikTok Accounts (Django admin)
- [ ] Hacer live de prueba de 60-90 min con sistema actual (DinoChrome)
- [ ] Analizar datos: ViewerCountEvent, gifts, revenue
- [ ] Iterar contenido: que juego engancha, que TTS genera reaccion
- [ ] Probar diferentes horarios
- [ ] Medir $/hora real

### Criterio de exito
- $/hora >= $5 → Modelo funciona, avanzar a Fase 1
- $/hora = $2-5 → Iterar contenido antes de escalar
- $/hora < $2 → Cambiar estrategia de contenido

### Costo: $0
### Hardware: Laptop Windows actual

---

## Fase 1: Primer escalamiento (Mes 2-3)

**Objetivo**: 2-3 cuentas generando revenue consistente

### Pre-requisitos
- Fase 0 exitosa ($/hora validado)
- Unirse a agencia verificada (Atomik, Purly, o similar)

### Acciones
- [ ] Unirse a agencia para obtener stream keys
- [ ] Comprar 1-2 cuentas adicionales (US, engordadas, live habilitado)
- [ ] Contratar 1-2 proxies residenciales US
- [ ] Configurar OBS multi-instancia en laptop Windows
- [ ] Instalar Virtual Audio Cables
- [ ] Desarrollar 2-3 juegos nuevos (Slot Machine, Ruleta, Plinko)
- [ ] Cada cuenta: juego diferente, voz TTS diferente
- [ ] Comparar ingresos US vs cuenta propia LATAM

### Criterio de exito
- Revenue consistente > $800/mes con 3 cuentas
- Sistema estable corriendo 3+ horas sin crashes

### Costo estimado
- Cuentas: ~$120-180
- Proxies: ~$60/mes
- APIs: ~$15/mes
- Total primer mes: ~$255

### Hardware: Laptop Windows (3-4 instancias)

---

## Fase 2: Escala media (Mes 4-6)

**Objetivo**: 5-8 cuentas, meta $2K/mes

### Pre-requisitos
- Fase 1 exitosa (revenue positivo con 3 cuentas)
- Datos suficientes para saber duracion/horario optimo

### Acciones
- [ ] Agregar PC de mesa como nodo principal (7-8 instancias)
- [ ] Comprar 3-5 cuentas adicionales (US/UK)
- [ ] Contratar proxies adicionales
- [ ] Involucrar 1 socio/familiar para segundo bloque de verificacion
- [ ] Desarrollar mas juegos del catalogo
- [ ] Implementar cambios de multi-instancia en codigo (audio_device, multi-puerto)
- [ ] Parametrizar .env por instancia

### Criterio de exito
- Revenue > $2,000/mes neto
- 5+ cuentas operando establemente

### Costo estimado mensual
- Proxies: ~$150/mes
- APIs: ~$30/mes
- Total: ~$180/mes

### Hardware: PC de mesa + Laptop Windows

---

## Fase 3: Escala completa (Mes 7+)

**Objetivo**: 10-12 cuentas, maximizar revenue

### Pre-requisitos
- Fase 2 exitosa
- Modelo de negocio validado y repetible

### Acciones
- [ ] Usar MacBook como cerebro/orquestador
- [ ] Implementar dashboard centralizado
- [ ] Todas las cuentas distribuidas en PC mesa + Laptop
- [ ] 3 bloques de identidad (3 personas, 3 PayPals)
- [ ] Automatizar lo que se pueda (health checks, alertas, rotacion de juegos)
- [ ] Catalogo de 10+ juegos para rotacion

### Criterio de exito
- Revenue > $4,000/mes neto
- Operacion semi-autonoma (pocas horas de gestion diaria)

### Hardware: PC de mesa + Laptop + MacBook (orquestador)

---

## Desarrollo de juegos (paralelo a todas las fases)

### Prioridad de desarrollo

```
Semana 1-2:  Slot Machine + Ruleta (mayor ROI estimado)
Semana 3-4:  Plinko + Contador de metas
Semana 5-6:  Batallas de viewers + Mascota virtual
Semana 7-8:  Tower Stacker + Trivia
Semana 9+:   Resto del catalogo segun feedback de lives
```

Cada juego comparte: queue system, TTS, LLM, overlays. Solo cambia el frontend + `process_event()`.

### Template base

Crear un template base reutilizable que incluya:
- HTML/JS skeleton para browser source en OBS
- Service class boilerplate
- Conexion con TTS y LLM
- Sistema de overlays
- SSE para comunicacion en tiempo real

---

## Cambios tecnicos pendientes en el codigo

### Ya implementados
- [x] Modelo `TikTokAccount` (info de cuentas)
- [x] `LiveSession.account` (FK a TikTokAccount)
- [x] `LiveSession.game_type` (que juego se uso)
- [x] Captura de `RoomUserSeqEvent` / `ViewerCountEvent`
- [x] Django Admin para TikTokAccount

### Pendientes para multi-instancia
- [ ] Parametro `audio_device` en Config para VLC routing
- [ ] Soporte multi-puerto (Django en 8000, 8001, 8002...)
- [ ] Template `.env` para facilitar N instancias
- [ ] Script de arranque para levantar N instancias

### Pendientes para analytics
- [ ] Vista/query de revenue por sesion
- [ ] Vista/query de viewer count timeline por sesion
- [ ] Comparativa entre juegos/paises/horarios

---

## Resumen financiero del plan

| Fase | Cuentas | Inversion inicial | Costo mensual | Revenue esperado/mes |
|------|---------|-------------------|---------------|---------------------|
| 0 | 1 | $0 | $0 | $0-300 (validacion) |
| 1 | 3 | ~$255 | ~$75 | $500-1,500 |
| 2 | 5-8 | ~$400 | ~$180 | $2,000-4,000 |
| 3 | 10-12 | ~$600 | ~$350 | $4,000-6,000+ |

**Break-even estimado**: Mes 2-3 (si el contenido genera >$5/hr).
