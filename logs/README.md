# Logs del Sistema

Este directorio contiene todos los archivos de log del sistema.

## Archivos de Log

### `general.log`
Logs generales de Django (errores, warnings, info del framework)

### `dinochrome.log`
Logs específicos del servicio **DinoChrome**:
- Inicio/detención del servicio
- Procesamiento de eventos (regalos, comentarios, likes, etc.)
- Errores en el procesamiento

### `overlays.log`
Logs específicos del servicio **Overlays**:
- Inicio/detención del servicio
- Procesamiento de overlays visuales
- Errores en el procesamiento

### `tiktok_events.log`
Logs de captura de eventos de TikTok Live:
- Conexión al stream
- Creación de sesiones
- Captura de eventos
- Errores de conexión

### `queue_system.log`
Logs del sistema de colas:
- Distribución de eventos
- Gestión de colas
- Workers activos
- Errores en el dispatcher

## Formato de Logs

Los logs siguen el formato:
```
[NIVEL] FECHA_HORA NOMBRE_LOGGER - MENSAJE
```

Ejemplo:
```
[INFO] 2025-10-05 12:30:45 dinochrome - Procesando regalo: Rosa (1 diamantes) de usuario123
```

## Niveles de Log

- **DEBUG**: Información detallada (eventos de baja prioridad como likes)
- **INFO**: Información general (eventos procesados, inicio/detención)
- **WARNING**: Advertencias (eventos no manejados, colas llenas)
- **ERROR**: Errores (fallos en procesamiento, excepciones)

## Rotación de Logs

Los logs NO rotan automáticamente. Puedes limpiarlos manualmente:

```bash
# Limpiar todos los logs
rm /var/www/tiktok/logs/*.log

# Limpiar un log específico
> /var/www/tiktok/logs/dinochrome.log
```

## Consultar Logs en Tiempo Real

```bash
# Ver logs de DinoChrome en tiempo real
tail -f /var/www/tiktok/logs/dinochrome.log

# Ver logs de Overlays en tiempo real
tail -f /var/www/tiktok/logs/overlays.log

# Ver todos los logs
tail -f /var/www/tiktok/logs/*.log
```
