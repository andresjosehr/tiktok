import json
import time
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.tiktok_events.models import LiveSession, LiveEvent
from apps.queue_system.dispatcher import EventDispatcher


def panel_page(request):
    return render(request, 'simulator/panel.html')


def _get_or_create_session():
    """Obtiene o crea una session de simulacion activa"""
    session = LiveSession.objects.filter(
        status='active',
        name__startswith='[SIMULATOR]'
    ).first()

    if not session:
        session = LiveSession.objects.create(
            name=f"[SIMULATOR] Web Panel - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            status='active',
            room_id=888888888,
            streamer_unique_id='simulator_streamer',
        )

    return session


def _build_event_data(event_type, data):
    """Construye event_data segun el tipo de evento"""
    username = data.get('username', 'TestUser')
    # user_id consistente por username (para que rachas del mismo usuario funcionen)
    user_id = abs(hash(username)) % 10000000000
    user_info = {
        'unique_id': username.lower().replace(' ', '_'),
        'nickname': username,
        'user_id': user_id,
    }

    if event_type == 'GiftEvent':
        gift_name = data.get('gift_name', 'Rose')
        gift_count = int(data.get('gift_count', 1))
        diamond_count = int(data.get('diamond_count', 1))
        return {
            'gift': {
                'id': abs(hash(gift_name)) % 10000,
                'name': gift_name,
                'count': gift_count,
                'diamond_count': diamond_count,
                'streakable': False,
            },
            'repeat_count': gift_count,
            'user': user_info,
        }, user_id

    elif event_type == 'CommentEvent':
        return {
            'comment': data.get('comment', 'Hola!'),
            'user': user_info,
        }, user_id

    elif event_type == 'LikeEvent':
        return {
            'like_count': int(data.get('like_count', 1)),
            'total_likes': int(data.get('like_count', 1)),
            'user': user_info,
        }, user_id

    else:
        # ShareEvent, FollowEvent, JoinEvent, SubscribeEvent
        return {
            'user': user_info,
        }, user_id


@csrf_exempt
@require_http_methods(["POST"])
def send_event(request):
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type', 'GiftEvent')
        username = data.get('username', 'TestUser')

        session = _get_or_create_session()
        event_data, user_id = _build_event_data(event_type, data)

        # Streak fields (del frontend)
        is_streaking = data.get('is_streaking', False)
        streak_id = data.get('streak_id', None)
        streak_status = data.get('streak_status', 'end' if event_type == 'GiftEvent' else None)

        event = LiveEvent.objects.create(
            session=session,
            event_type=event_type,
            timestamp=timezone.now(),
            room_id=session.room_id,
            streamer_unique_id=session.streamer_unique_id,
            user_id=user_id,
            user_unique_id=username.lower().replace(' ', '_'),
            user_nickname=username,
            is_streaking=is_streaking,
            streak_id=streak_id,
            streak_status=streak_status,
            event_data=event_data,
        )
        session.increment_events()

        result = EventDispatcher.dispatch(event)

        return JsonResponse({
            'success': True,
            'event_id': event.id,
            'event_type': event_type,
            'username': username,
            'session_id': session.id,
            'session_total_events': session.total_events,
            'dispatch_result': result,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
def session_status(request):
    session = LiveSession.objects.filter(
        status='active',
        name__startswith='[SIMULATOR]'
    ).first()

    if session:
        return JsonResponse({
            'active': True,
            'id': session.id,
            'name': session.name,
            'total_events': session.total_events,
            'started_at': session.started_at.isoformat(),
        })

    return JsonResponse({'active': False})


@csrf_exempt
@require_http_methods(["POST"])
def end_session(request):
    session = LiveSession.objects.filter(
        status='active',
        name__startswith='[SIMULATOR]'
    ).first()

    if session:
        session.end_session(status='completed')
        return JsonResponse({
            'success': True,
            'total_events': session.total_events,
        })

    return JsonResponse({
        'success': False,
        'error': 'No hay session activa',
    })
