"""
Backup y restauracion de escenas de OBS
Exporta/importa configuracion completa: escenas, fuentes, posiciones, URLs
"""

import json
import os
from datetime import datetime
from django.conf import settings
from .client import OBSClient


BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups', 'obs')


def export_scene(scene_name=None):
    """
    Exporta la configuracion de una escena de OBS a JSON

    Args:
        scene_name: Nombre de la escena (None = todas)

    Returns:
        dict: {'success': bool, 'file': str, 'error': str}
    """
    try:
        obs_client = OBSClient()
        client = obs_client._connect()

        scenes = client.get_scene_list()
        scene_names = [s['sceneName'] for s in scenes.scenes]

        if scene_name and scene_name not in scene_names:
            client.disconnect()
            return {'success': False, 'error': f'Escena "{scene_name}" no encontrada'}

        target_scenes = [scene_name] if scene_name else scene_names

        backup = {
            'exported_at': datetime.now().isoformat(),
            'scenes': []
        }

        for sname in target_scenes:
            scene_data = {
                'name': sname,
                'items': []
            }

            items = client.get_scene_item_list(sname)
            for item in items.scene_items:
                source_name = item.get('sourceName', '')
                item_id = item['sceneItemId']
                input_kind = item.get('inputKind', '')

                # Guardar transform COMPLETO tal como OBS lo devuelve
                transform = client.get_scene_item_transform(sname, item_id)

                item_data = {
                    'source_name': source_name,
                    'input_kind': input_kind,
                    'enabled': item.get('sceneItemEnabled', True),
                    'transform': transform.scene_item_transform,
                }

                # Settings del input (URLs, dimensiones, etc.)
                if input_kind:
                    try:
                        input_settings = client.get_input_settings(source_name)
                        item_data['input_settings'] = input_settings.input_settings
                        item_data['input_kind'] = input_settings.input_kind
                    except Exception:
                        pass

                scene_data['items'].append(item_data)

            backup['scenes'].append(scene_data)

        client.disconnect()

        # Guardar archivo
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'obs_backup_{timestamp}.json'
        filepath = os.path.join(BACKUP_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup, f, indent=2, ensure_ascii=False)

        return {
            'success': True,
            'file': filepath,
            'scenes': len(backup['scenes']),
            'items': sum(len(s['items']) for s in backup['scenes'])
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def import_scene(filepath):
    """
    Importa configuracion de escena desde un backup JSON.
    Crea las fuentes y aplica posiciones/settings.

    Args:
        filepath: Ruta al archivo JSON de backup

    Returns:
        dict: {'success': bool, 'restored': list, 'error': str}
    """
    # Campos editables de transform (los demas son read-only)
    WRITABLE_TRANSFORM_FIELDS = {
        'positionX', 'positionY',
        'scaleX', 'scaleY',
        'rotation',
        'boundsType', 'boundsWidth', 'boundsHeight', 'boundsAlignment',
        'cropTop', 'cropBottom', 'cropLeft', 'cropRight',
        'cropToBounds',
        'alignment',
    }

    # Campos que requieren boundsType != OBS_BOUNDS_NONE
    BOUNDS_FIELDS = {'boundsWidth', 'boundsHeight', 'boundsAlignment'}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            backup = json.load(f)

        obs_client = OBSClient()
        client = obs_client._connect()

        restored = []

        for scene_data in backup['scenes']:
            scene_name = scene_data['name']

            # Crear escena si no existe
            try:
                scenes = client.get_scene_list()
                existing = [s['sceneName'] for s in scenes.scenes]
                if scene_name not in existing:
                    client.create_scene(scene_name)
                    print(f"[OBS] Escena creada: {scene_name}")
            except Exception:
                pass

            for item_data in scene_data['items']:
                source_name = item_data['source_name']
                input_kind = item_data.get('input_kind', '')
                input_settings = item_data.get('input_settings', {})

                try:
                    # Crear input si no existe
                    try:
                        client.get_input_settings(source_name)
                    except Exception:
                        if input_kind and input_settings:
                            client.create_input(
                                scene_name, source_name, input_kind,
                                input_settings, True
                            )
                            print(f"[OBS] Input creado: {source_name}")

                    # Buscar el item en la escena
                    items = client.get_scene_item_list(scene_name)
                    item_id = None
                    for item in items.scene_items:
                        if item.get('sourceName') == source_name:
                            item_id = item['sceneItemId']
                            break

                    if item_id is None:
                        try:
                            result = client.create_scene_item(scene_name, source_name)
                            item_id = result.scene_item_id
                        except Exception:
                            pass

                    if item_id:
                        # Aplicar settings del input PRIMERO (para que sourceWidth/Height se calculen)
                        if input_settings:
                            client.set_input_settings(source_name, input_settings, True)

                        # Filtrar solo campos editables del transform
                        full_transform = item_data.get('transform', {})
                        bounds_type = full_transform.get('boundsType', 'OBS_BOUNDS_NONE')

                        writable_transform = {}
                        for k, v in full_transform.items():
                            if k not in WRITABLE_TRANSFORM_FIELDS:
                                continue
                            # No enviar bounds fields si boundsType es NONE
                            if bounds_type == 'OBS_BOUNDS_NONE' and k in BOUNDS_FIELDS:
                                continue
                            writable_transform[k] = v

                        # Aplicar transform
                        client.set_scene_item_transform(scene_name, item_id, writable_transform)

                        # Aplicar visibilidad
                        enabled = item_data.get('enabled', True)
                        client.set_scene_item_enabled(scene_name, item_id, enabled)

                        restored.append(source_name)
                        print(f"[OBS] Restaurado: {source_name}")

                except Exception as e:
                    print(f"[OBS] Error restaurando '{source_name}': {e}")

        client.disconnect()

        return {
            'success': True,
            'restored': restored,
            'total': len(restored)
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}
