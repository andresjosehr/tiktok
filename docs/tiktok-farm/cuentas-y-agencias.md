# Cuentas y Agencias

## Como hacer live con OBS (sin TikTok Studio)

TikTok Studio solo permite 1 instancia. Para multiples lives simultaneos se usa OBS con stream keys via RTMP.

### Obtener stream key

Desde 2025/2026, TikTok **solo otorga stream keys a traves de Creator Networks (agencias)**. No hay forma oficial de obtenerlo sin agencia.

**Proceso:**
1. Unirse a una agencia verificada (gratis)
2. La agencia desbloquea TikTok LIVE Producer para tu cuenta
3. Antes de cada live: entrar a `livecenter.tiktok.com/producer`
4. Generar stream key + Server URL (cambia cada sesion)
5. Pegar en OBS → Settings → Stream → Custom

**Importante**: El stream key es **nuevo cada sesion**. No se puede reutilizar.

### Alternativa sin stream key: SE.Live

**SE.Live** (StreamElements) es un plugin gratuito para OBS que permite streamear a TikTok sin stream key manual:
- Se instala como plugin de OBS
- Login directo con cuenta TikTok
- Recuerda la sesion automaticamente
- Soporta multistreaming a varias plataformas
- **Requiere**: 1,000+ followers + 25 min previos de live

Util para la cuenta principal. Para cuentas adicionales se necesita RTMP via agencia.

## Agencias de TikTok (Creator Networks)

### Como funcionan economicamente

```
Sin agencia:
  Viewer paga $100 → TikTok se queda ~$50 → Tu recibes ~$50

Con agencia:
  Viewer paga $100 → TikTok se queda ~$35 → Agencia recibe ~$15 → Tu recibes ~$50
  (La agencia cobra del corte de TikTok, NO del tuyo)
```

### Requisitos tipicos
- Streamear 10-20 horas/mes minimo
- Seguir guidelines de TikTok
- Gratis para unirse
- Puedes salirte cuando quieras (en agencias legitimas)

### Agencias verificadas recomendadas (para PC streamers)

| Agencia | Enfoque | Region |
|---------|---------|--------|
| Atomik | PC streamers, stream keys | Global |
| Purly | PC streamers con OBS | Global |
| FTTV | Grande, acepta <1K followers | US/CA |
| Doves4Love | Global | US-based |

Lista completa: https://www.toktutorials.com/list-of-agencies

### Como verificar si una agencia es legitima

| Senal | Legitima | Estafa |
|-------|----------|--------|
| Te cobra por unirte? | NUNCA | "Cuota de activacion" |
| Toca tu % de diamonds? | NO | "Comision del 20-30%" |
| Penalizacion por salir? | No | Multas/penalizaciones |
| Pide password/acceso? | JAMAS | "Necesitamos acceso" |
| Quien contacto a quien? | Tu a ella | Te busco por DM random |
| Verificable? | En LIVE Backstage | No aparece |

**Metodo oficial de verificacion**: Ir a @tiktoklive_us y escribir "Teleport" para ver agencias verificadas por TikTok.

## TikTokStreamKeyGenerator (NO RECOMENDADO)

Herramienta open source que genera stream keys via Selenium: https://github.com/Loukious/TikTokStreamKeyGenerator

**Analisis de seguridad del codigo**: Limpio, no envia datos a terceros, solo habla con servidores de TikTok.

**PERO**: TikTok lo detecta y aplica:
- "Integrity and authenticity violation" inmediatamente al empezar live
- Shadow ban - no apareces en FYP
- Visibilidad restringida

**Veredicto**: Codigo seguro pero **inutil para negocio** porque nadie te encuentra.

## Verificacion de identidad y retiro de diamonds

### Proceso de retiro

1. Acumular minimo $50 en diamonds
2. Verificar identidad (gobierno ID + selfie en algunos casos)
3. Vincular PayPal verificado
4. **Nombre en TikTok debe coincidir EXACTAMENTE con nombre en PayPal**
5. Retirar a PayPal (max $1,000/dia, 1 retiro/dia, hasta 15 dias procesamiento)

### Limites de verificacion por ID

| Contexto | Limite confirmado | Fuente |
|----------|-------------------|--------|
| TikTok Shop (comisiones) | 5 cuentas por ID | Documentacion oficial |
| Diamonds de lives | **No documentado oficialmente** | No hay limite publicado |

**Nota**: El limite de 5 cuentas/ID esta confirmado solo para TikTok Shop. Para diamonds de lives no hay documentacion oficial del limite, pero el sistema de verificacion es compartido.

### Reglas de PayPal

- Cada cuenta TikTok necesita **email unico** (obligatorio)
- El nombre en TikTok **debe coincidir** con el nombre en PayPal
- No puedes retirar a PayPal de otra persona
- Mismo telefono: hasta 5 cuentas (permitido pero es senal de vinculacion)

### Riesgo de cuentas compradas y retiro

Si compras una cuenta de otra persona:
- El nombre en TikTok es del dueno original
- Tu PayPal tiene tu nombre
- **No coinciden → No puedes retirar**
- Solucion: Cambiar nombre en TikTok a tu nombre real (pero cambia el perfil visible)

### Compartimentalizacion de identidades (CRITICO)

```
NUNCA pongas todas las cuentas bajo el mismo ID.

Bloque A (tu ID):           2-3 cuentas → PayPal tuyo
Bloque B (familiar/socio):  2-3 cuentas → PayPal de esa persona
Bloque C (otro socio):      2-3 cuentas → PayPal del tercero

Beneficios:
- Si cae un bloque, los otros siguen operando
- Limita "blast radius" de cualquier ban
- Nunca llenes los 5 slots de un ID (dejar margen)
```

### Que pasa si te banean una cuenta?

**No confirmado oficialmente, pero la evidencia sugiere:**
- TikTok retiene todos los datos de verificacion post-ban
- El sistema cruza datos entre cuentas (ID, telefono, banco, device)
- Una cuenta baneada podria afectar la verificacion de cuentas futuras con el mismo ID
- Diamonds pendientes de retiro podrian perderse con un ban

**Por eso la compartimentalizacion es critica**: si pierdes 1 bloque de 2-3 cuentas, no pierdes todo.
