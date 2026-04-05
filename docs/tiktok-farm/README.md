# TikTok Live Farm - Documentacion del Proyecto

Documentacion de investigacion y planificacion para operar multiples lives interactivos de TikTok simultaneamente, generando ingresos a traves de gifts/diamonds.

## Indice

| Documento | Contenido |
|-----------|-----------|
| [Modelo de Negocio](modelo-de-negocio.md) | Meta financiera, proyecciones de ingresos, costos, ROI por cuenta |
| [Infraestructura](infraestructura.md) | Hardware disponible, capacidad por PC, encoding, audio, OBS multi-instancia |
| [Cuentas y Agencias](cuentas-y-agencias.md) | Agencias, stream keys, verificacion de identidad, retiro de diamonds, PayPal |
| [Estrategia de Contenido](estrategia-de-contenido.md) | Catalogo de juegos interactivos, rotacion, TTS, optimizacion de lives |
| [Riesgos y Mitigacion](riesgos-y-mitigacion.md) | Shadow ban, deteccion IP, vinculacion de cuentas, compartimentalizacion |
| [Plan de Ejecucion](plan-de-ejecucion.md) | Fases de escalamiento, validacion, timeline |

## Contexto

- **Fecha de investigacion**: Abril 2026
- **Estado**: Fase de planificacion - aun no se ha realizado el primer live de prueba
- **Hardware disponible**: PC de mesa (Ryzen 9 + RTX 4070), Laptop Windows (i7 + RTX 2070S), MacBook M4 Pro
- **Cuenta actual**: 1 cuenta propia, sin agencia aun

## Sistema Tecnico

El sistema Django ya implementado captura eventos de TikTok Live en tiempo real y los procesa a traves de un queue system con servicios modulares (juegos, TTS, musica, overlays). Ver `CLAUDE.md` para documentacion tecnica del codigo.
