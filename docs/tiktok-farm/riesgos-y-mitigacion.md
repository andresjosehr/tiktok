# Riesgos y Mitigacion

## Resumen de riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Shadow ban por misma IP | Alta (sin proxy) | Alto | Proxy por cuenta |
| TikTok vincula cuentas por ID | Media | Alto | Compartimentalizar IDs |
| Ban de cuenta individual | Baja-Media | Medio | Contenido limpio + distribuir riesgo |
| Efecto domino (ban cascada) | Baja | Muy alto | Bloques separados por ID/PayPal |
| Audiencia no llega/no dona | Media | Alto | Validar con 1 cuenta primero |
| Stream key revocado (agencia) | Baja | Medio | Cumplir horas minimas |
| TikTok cambia politicas | Incierta | Variable | No sobre-invertir al inicio |

## Deteccion de multiples cuentas por TikTok

### Que detecta TikTok (capas de deteccion)

```
Capa 1: IP Address          → Multiples cuentas misma IP = red flag
Capa 2: Device Fingerprint  → Hardware, navegador, sensores
Capa 3: Behavioral Patterns → Mismos horarios, mismos patrones
Capa 4: Account Linking      → Si una cae, las vinculadas pueden caer
Capa 5: Identity (KYC)       → Mismo ID verificado en varias cuentas
```

### Mitigacion por capa

| Capa | Solucion | Costo |
|------|----------|-------|
| IP | Proxy residencial/4G por cuenta | $20-30/cuenta/mes |
| Fingerprint | Perfiles de navegador separados (Chrome profiles) | $0 |
| Behavioral | Horarios diferentes, contenido diferente por cuenta | $0 (disciplina) |
| Account Linking | No compartir telefono/email/banco entre bloques | $0 |
| Identity | Multiples IDs (socios/familiares) | Depende |

## Shadow ban: causas y prevencion

### Causas confirmadas de shadow ban

1. **Multiples cuentas misma IP sin proxy** - TikTok las vincula
2. **Pedir gifts agresivamente** - Throttling inmediato
3. **Copyright de musica** - Mute o fin del stream
4. **Contenido pre-grabado/loop** - Deteccion automatica
5. **Reiniciar lives repetidamente** - Reduce algoritmo
6. **Demasiados lives por dia** - Fatiga de audiencia + algoritmo

### Causas que NO causan shadow ban

- Tener multiples cuentas (si estan bien aisladas)
- Hacer live con OBS via RTMP (si tienes stream key oficial)
- Usar agencia para stream key
- Contenido interactivo automatizado (si es de calidad)

## Politica oficial de TikTok sobre multi-cuentas

### Creator Network Multi-Account Policy

Documento oficial: https://sf16-draftcdn-sg.ibytedtos.com/obj/ies-hotsoon-draft-sg/webcast-union-platform-i18n/multiple_account_policy.html

Puntos clave:
- Un creador elegible debe usar **una cuenta** para unirse a **una agencia**
- No puedes tener "side accounts" haciendo live en otra agencia
- Si detectan side accounts: remocion + deduccion de bonos a la agencia
- Penalizaciones escalan con el numero de violaciones

**Nota**: Esta politica aplica a cuentas DENTRO del sistema de agencias. No prohibe tener multiples cuentas en la misma agencia (depende de la agencia).

## Riesgo de cuentas compradas

| Riesgo | Detalle |
|--------|---------|
| Comprar/vender cuentas viola ToS | Ban permanente si TikTok lo detecta |
| Cambio brusco de ubicacion | Cuenta activa en NY, de repente en LA = sospechoso |
| Cambio de dispositivo | TikTok ve device completamente nuevo |
| Vendedor estafa | Cuenta reportada, en cooldown, o con violations ocultas |
| Nombre no coincide con tu PayPal | No puedes retirar diamonds |

### Mitigacion para cuentas compradas

1. **Verificar antes de pagar** que la cuenta puede hacer live
2. **Calentamiento post-compra**: 3-7 dias de uso normal antes de live
3. **Proxy de la misma region** donde la cuenta fue usada originalmente
4. **Cambiar nombre** a tu nombre real (necesario para retiros)

## Compartimentalizacion (ESTRATEGIA PRINCIPAL)

```
ESTRUCTURA RECOMENDADA:

Bloque A (tu ID):
  - 2-3 cuentas (NUNCA 5, dejar margen)
  - PayPal tuyo
  - Proxy set A
  - Agencia X

Bloque B (socio/familiar #1):
  - 2-3 cuentas
  - PayPal de esa persona
  - Proxy set B
  - Agencia Y (puede ser la misma u otra)

Bloque C (socio/familiar #2):
  - 2-3 cuentas
  - PayPal del tercero
  - Proxy set C

REGLAS:
  - NUNCA compartir PayPal entre bloques
  - NUNCA auto-gifting entre cuentas propias
  - NUNCA llenar los 5 slots de un ID
  - Cada bloque es independiente: si uno cae, los otros siguen
```

## Que hacer si te banean una cuenta

1. **NO crear cuenta nueva inmediatamente** desde el mismo dispositivo/IP
2. **Apelar el ban** si fue injustificado (Settings → Report a Problem)
3. **NO intentar verificar nueva cuenta** con el mismo ID hasta entender por que fue el ban
4. **Evaluar si el ban afecta las otras cuentas** del mismo bloque
5. **Los diamonds pendientes podrian perderse** - retirar regularmente, no acumular

## Escenarios de peor caso

| Escenario | Probabilidad | Que pierdes | Que mantienes |
|-----------|-------------|-------------|---------------|
| Ban 1 cuenta por copyright | Media | 1 cuenta + diamonds pendientes | Resto de cuentas |
| Ban cascada en 1 bloque | Baja | 2-3 cuentas del bloque | Otros bloques |
| ID bloqueado permanentemente | Muy baja | No puedes verificar nuevas cuentas con ese ID | Cuentas ya verificadas (no confirmado) |
| Cambio de politicas TikTok | Incierta | Variable | Adaptarse |
| TikTok deja de operar (ban pais, etc) | Muy baja | Todo | Nada |

## Regla de oro

**No inviertas mas de lo que puedes perder.** Escala gradualmente, valida con datos reales, y nunca pongas todos los huevos en una sola canasta (ni un solo ID, ni un solo PayPal, ni una sola agencia).
