"""
TugOfWar Service - Juego interactivo Tug of War para TikTok Live

Mapea regalos de TikTok a equipos y envia eventos al frontend via SSE.
El frontend muestra el juego en un browser source de OBS.
"""

from apps.queue_system.base_service import BaseQueueService


class TugOfWarService(BaseQueueService):
    """
    Servicio que procesa regalos de TikTok y los convierte en
    donaciones para el juego Tug of War.

    Solo procesa GiftEvent. Mapea cada regalo a un equipo (men/women)
    y un valor en monedas, luego envia el evento via SSE al frontend.
    """

    # Mapeo de regalo TikTok -> (equipo, valor en monedas)
    GIFT_TEAM_MAP = {
        # Equipo Hombres
        'gg': ('men', 1),
        'maracas': ('men', 1),
        'fireworks': ('men', 5),
        'star': ('men', 10),
        # Equipo Mujeres
        'ice cream cone': ('women', 1),
        'ice cream': ('women', 1),
        'cone': ('women', 1),
        'love you': ('women', 1),
        'te adoro': ('women', 1),
        'korean heart': ('women', 5),
        'rosa': ('women', 10),
        'rose': ('women', 10),
    }

    def on_start(self):
        print("[TUGOFWAR] Servicio Tug of War iniciado")

    def on_stop(self):
        print("[TUGOFWAR] Servicio Tug of War detenido")

    def process_event(self, live_event, queue_item):
        try:
            event_type = live_event.event_type

            if event_type == 'GiftEvent':
                return self._process_gift(live_event, queue_item)

            # Otros eventos no se procesan en este servicio
            return True

        except Exception as e:
            print(f"[TUGOFWAR] Error procesando evento: {e}")
            return False

    def _process_gift(self, live_event, queue_item):
        """Procesa un regalo y lo envia como donacion al frontend"""
        try:
            from apps.services.tugofwar.game.views import send_tugofwar_event

            # Ignorar evento de fin de racha (evita contar doble)
            if live_event.streak_status == 'end':
                return True

            event_data = live_event.event_data
            gift_name = event_data.get('gift', {}).get('name', '').lower()
            username = live_event.user_nickname or live_event.user_unique_id or 'Anonimo'

            # Buscar el regalo en el mapa
            team_info = self.GIFT_TEAM_MAP.get(gift_name)

            if not team_info:
                print(f"[TUGOFWAR] Regalo '{gift_name}' no mapeado, ignorando")
                return True

            team, amount = team_info

            send_tugofwar_event('donation', {
                'team': team,
                'amount': amount,
                'username': username,
                'gift_name': gift_name,
            })

            print(f"[TUGOFWAR] {username} dono {gift_name} -> {team} +{amount}")
            return True

        except Exception as e:
            print(f"[TUGOFWAR] Error procesando regalo: {e}")
            import traceback
            traceback.print_exc()
            return False
