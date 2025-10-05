import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from django.utils import timezone
from asgiref.sync import sync_to_async
from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    CommentEvent,
    GiftEvent,
    LikeEvent,
    ShareEvent,
    FollowEvent,
    JoinEvent,
    SubscribeEvent,
)
from .models import LiveEvent, LiveSession


def clean_text(text: str) -> str:
    """Limpia texto de emojis y caracteres especiales que causan problemas en MySQL"""
    if not text:
        return text
    # Elimina caracteres de 4 bytes (emojis) que MySQL utf8mb3 no soporta
    # Solo permite caracteres BMP (Basic Multilingual Plane)
    return ''.join(char for char in text if ord(char) < 0x10000)


class StreakTracker:
    """Trackea las rachas activas de regalos y likes"""

    def __init__(self):
        self.active_streaks: Dict[str, Dict[str, Any]] = {}

    def generate_streak_id(self, user_id: int, event_type: str, gift_id: Optional[int] = None) -> str:
        """Genera ID único para la racha"""
        key = f"{user_id}_{event_type}"
        if gift_id:
            key += f"_{gift_id}"
        return f"{key}_{int(time.time())}"

    def get_streak_key(self, user_id: int, gift_id: Optional[int] = None) -> str:
        """Genera clave única para trackear la racha"""
        if gift_id:
            return f"{user_id}_{gift_id}"
        return f"{user_id}"

    def process_streak(self, user_id: int, is_streaking: bool, repeat_count: int, gift_id: Optional[int] = None):
        """Procesa el estado de una racha y retorna (streak_id, streak_status, total_count)"""
        streak_key = self.get_streak_key(user_id, gift_id)

        if is_streaking:
            if streak_key not in self.active_streaks:
                # INICIO de racha
                event_type = 'GiftEvent' if gift_id else 'LikeEvent'
                streak_id = self.generate_streak_id(user_id, event_type, gift_id)
                self.active_streaks[streak_key] = {
                    'id': streak_id,
                    'total_count': repeat_count
                }
                return streak_id, 'start', repeat_count
            else:
                # CONTINUACIÓN de racha
                streak_id = self.active_streaks[streak_key]['id']
                self.active_streaks[streak_key]['total_count'] += repeat_count
                return streak_id, 'continue', self.active_streaks[streak_key]['total_count']
        else:
            if streak_key in self.active_streaks:
                # FIN de racha
                streak_id = self.active_streaks[streak_key]['id']
                self.active_streaks[streak_key]['total_count'] += repeat_count
                total_count = self.active_streaks[streak_key]['total_count']
                del self.active_streaks[streak_key]
                return streak_id, 'end', total_count
            else:
                # Evento SIN racha
                return None, None, repeat_count


class TikTokEventCapture:
    """Servicio para capturar eventos de TikTok Live y guardarlos en la BD"""

    def __init__(self, streamer_username: str, session_name: Optional[str] = None):
        self.streamer_username = streamer_username
        self.session_name = session_name
        self.client = TikTokLiveClient(unique_id=f"@{streamer_username}")
        self.room_id = None
        self.streak_tracker = StreakTracker()
        self.session = None  # Se creará al conectar

        # Registrar eventos
        self._register_handlers()

    def _register_handlers(self):
        """Registra los handlers para cada tipo de evento"""
        self.client.on(ConnectEvent)(self.on_connect)
        self.client.on(CommentEvent)(self.on_comment)
        self.client.on(GiftEvent)(self.on_gift)
        self.client.on(LikeEvent)(self.on_like)
        self.client.on(ShareEvent)(self.on_share)
        self.client.on(FollowEvent)(self.on_follow)
        self.client.on(JoinEvent)(self.on_join)
        self.client.on(SubscribeEvent)(self.on_subscribe)

    async def on_connect(self, event: ConnectEvent):
        """Se ejecuta al conectarse al live"""
        self.room_id = event.room_id

        # Crear nueva sesión
        self.session = await sync_to_async(LiveSession.objects.create)(
            name=self.session_name,
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username
        )

        print(f"✅ Conectado a @{event.unique_id} - Room ID: {event.room_id}")
        print(f"📝 Sesión creada: #{self.session.id} - {self.session.name or 'Sin nombre'}")

    async def on_comment(self, event: CommentEvent):
        """Captura eventos de comentarios"""
        # get_all_badges es una propiedad, no un método
        badges = getattr(event.user, 'get_all_badges', [])
        if callable(badges):
            badges = badges()

        event_data = {
            'comment': event.comment,
            'user': {
                'is_super_fan': getattr(event, 'user_is_super_fan', False),
                'is_moderator': event.user.is_moderator,
                'member_level': event.user.member_level,
                'gifter_level': event.user.gifter_level,
                'badges': badges if isinstance(badges, list) else []
            }
        }

        await sync_to_async(LiveEvent.objects.create)(
            session=self.session,
            event_type='CommentEvent',
            timestamp=timezone.now(),
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username,
            user_id=getattr(event.user, 'user_id', None),
            user_unique_id=event.user.unique_id,
            user_nickname=clean_text(event.user.nickname),
            event_data=event_data
        )
        print(f"💬 {event.user.unique_id}: {event.comment}")

    async def on_gift(self, event: GiftEvent):
        """Captura eventos de regalos con soporte de rachas"""
        user_id = getattr(event.user, 'user_id', None)
        gift_id = getattr(event.gift, 'gift_id', None)
        is_streaking = event.streaking
        repeat_count = event.repeat_count

        # Procesar racha
        streak_id, streak_status, total_count = self.streak_tracker.process_streak(
            user_id, is_streaking, repeat_count, gift_id
        )

        event_data = {
            'gift': {
                'id': gift_id,
                'name': event.gift.name,
                'diamond_count': getattr(event.gift, 'diamond_count', None),
                'streakable': getattr(event.gift, 'streakable', False)
            },
            'repeat_count': repeat_count,
            'streak_total_count': total_count,
            'is_streaking': is_streaking,
            'value_usd': getattr(event, 'value', None),
            'from_user': {
                'id': getattr(event.from_user, 'user_id', None),
                'unique_id': event.from_user.unique_id,
                'nickname': event.from_user.nickname
            },
            'to_user': {
                'id': getattr(event.to_user, 'user_id', None) if hasattr(event, 'to_user') else None,
                'unique_id': getattr(event.to_user, 'unique_id', None) if hasattr(event, 'to_user') else None
            }
        }

        await sync_to_async(LiveEvent.objects.create)(
            session=self.session,
            event_type='GiftEvent',
            timestamp=timezone.now(),
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username,
            user_id=user_id,
            user_unique_id=event.user.unique_id,
            user_nickname=clean_text(event.user.nickname),
            is_streaking=is_streaking,
            streak_id=streak_id,
            streak_status=streak_status,
            event_data=event_data
        )

        status_emoji = "🔄" if is_streaking else "✅"
        print(f"{status_emoji} {event.user.unique_id} envió {event.gift.name} x{repeat_count} (Total racha: {total_count})")

    async def on_like(self, event: LikeEvent):
        """Captura eventos de likes"""
        event_data = {
            'like_count': getattr(event, 'count', 1),
            'total_likes': getattr(event, 'total_likes', None),
            'user': {
                'unique_id': event.user.unique_id,
                'nickname': event.user.nickname
            }
        }

        await sync_to_async(LiveEvent.objects.create)(
            session=self.session,
            event_type='LikeEvent',
            timestamp=timezone.now(),
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username,
            user_id=getattr(event.user, 'user_id', None),
            user_unique_id=event.user.unique_id,
            user_nickname=clean_text(event.user.nickname),
            event_data=event_data
        )
        print(f"❤️ {event.user.unique_id} dio like")

    async def on_share(self, event: ShareEvent):
        """Captura eventos de compartir"""
        event_data = {
            'users_joined': getattr(event, 'users_joined', 0),
            'user': {
                'unique_id': event.user.unique_id,
                'nickname': event.user.nickname
            }
        }

        await sync_to_async(LiveEvent.objects.create)(
            session=self.session,
            event_type='ShareEvent',
            timestamp=timezone.now(),
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username,
            user_id=getattr(event.user, 'user_id', None),
            user_unique_id=event.user.unique_id,
            user_nickname=clean_text(event.user.nickname),
            event_data=event_data
        )
        print(f"📤 {event.user.unique_id} compartió el live")

    async def on_follow(self, event: FollowEvent):
        """Captura eventos de follow"""
        event_data = {
            'user': {
                'unique_id': event.user.unique_id,
                'nickname': event.user.nickname
            }
        }

        await sync_to_async(LiveEvent.objects.create)(
            session=self.session,
            event_type='FollowEvent',
            timestamp=timezone.now(),
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username,
            user_id=getattr(event.user, 'user_id', None),
            user_unique_id=event.user.unique_id,
            user_nickname=clean_text(event.user.nickname),
            event_data=event_data
        )
        print(f"👤 {event.user.unique_id} siguió al streamer")

    async def on_join(self, event: JoinEvent):
        """Captura eventos de usuarios uniéndose"""
        event_data = {
            'user': {
                'unique_id': event.user.unique_id,
                'nickname': event.user.nickname
            }
        }

        await sync_to_async(LiveEvent.objects.create)(
            session=self.session,
            event_type='JoinEvent',
            timestamp=timezone.now(),
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username,
            user_id=getattr(event.user, 'user_id', None),
            user_unique_id=event.user.unique_id,
            user_nickname=clean_text(event.user.nickname),
            event_data=event_data
        )
        print(f"🚪 {event.user.unique_id} se unió al live")

    async def on_subscribe(self, event: SubscribeEvent):
        """Captura eventos de suscripciones"""
        event_data = {
            'user': {
                'unique_id': event.user.unique_id,
                'nickname': event.user.nickname
            }
        }

        await sync_to_async(LiveEvent.objects.create)(
            session=self.session,
            event_type='SubscribeEvent',
            timestamp=timezone.now(),
            room_id=self.room_id,
            streamer_unique_id=self.streamer_username,
            user_id=getattr(event.user, 'user_id', None),
            user_unique_id=event.user.unique_id,
            user_nickname=clean_text(event.user.nickname),
            event_data=event_data
        )
        print(f"⭐ {event.user.unique_id} se suscribió")

    def start(self):
        """Inicia la captura de eventos"""
        print(f"🎬 Iniciando captura de eventos para @{self.streamer_username}...")
        try:
            self.client.run()
        except KeyboardInterrupt:
            # Finalizar la sesión al detener
            if self.session:
                self.session.end_session(status='completed')
                print(f"\n✅ Sesión #{self.session.id} finalizada - Duración: {self.session.get_duration_display()}")
            raise
        except Exception as e:
            # Marcar sesión como abortada si hay error
            if self.session:
                self.session.end_session(status='aborted')
                print(f"\n❌ Sesión #{self.session.id} abortada por error")
            raise
