import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import LiveSession, LiveEvent


def _parse_event_data(event):
    """Helper para parsear event_data sea dict o string"""
    d = event.event_data
    return d if isinstance(d, dict) else json.loads(d)


def _session_metrics(session):
    """Calcula todas las metricas de una sesion"""
    events = LiveEvent.objects.filter(session=session)
    vc_events = events.filter(event_type='ViewerCountEvent').order_by('timestamp')
    gift_events = events.filter(event_type='GiftEvent')

    # Viewer stats
    viewer_counts = [_parse_event_data(vc).get('viewer_count', 0) for vc in vc_events]
    peak = max(viewer_counts) if viewer_counts else 0
    avg = round(sum(viewer_counts) / len(viewer_counts), 1) if viewer_counts else 0

    # Unique viewers
    last_vc = vc_events.last()
    total_unique = _parse_event_data(last_vc).get('total_unique_viewers', 0) if last_vc else 0

    # Joins
    total_joins = events.filter(event_type='JoinEvent').count()

    # Gifts & revenue
    total_diamonds = 0
    total_gifts = 0
    gifters = set()
    for g in gift_events:
        d = _parse_event_data(g)
        diamonds = d.get('gift', {}).get('diamond_count', 0) or 0
        repeat = d.get('repeat_count', 1) or 1
        total_diamonds += diamonds * repeat
        total_gifts += repeat
        if g.user_unique_id:
            gifters.add(g.user_unique_id)

    revenue = round(total_diamonds * 0.005, 2)

    # Duration
    duration_sec = session.get_duration() if session.ended_at else 0
    duration_min = round(duration_sec / 60, 1)
    hours = duration_sec / 3600 if duration_sec > 0 else 1
    revenue_per_hour = round(revenue / hours, 2) if hours > 0 else 0

    # Conversion rate (gifters / unique viewers)
    conversion = round((len(gifters) / total_unique * 100), 1) if total_unique > 0 else 0

    # Engagement (events excluding viewer count / unique viewers)
    interaction_events = events.exclude(event_type='ViewerCountEvent').count()
    engagement_per_viewer = round(interaction_events / total_unique, 1) if total_unique > 0 else 0

    # Avg watch time estimate (total viewer-seconds / unique viewers)
    # Using viewer count snapshots as proxy
    if len(viewer_counts) >= 2 and total_unique > 0:
        total_viewer_seconds = sum(viewer_counts) * (duration_sec / len(viewer_counts))
        avg_watch_sec = total_viewer_seconds / total_unique
        avg_watch_min = round(avg_watch_sec / 60, 1)
    else:
        avg_watch_min = 0

    return {
        'id': session.id,
        'name': session.name or f'Session #{session.id}',
        'streamer': session.streamer_unique_id,
        'status': session.status,
        'started_at': session.started_at,
        'duration_display': session.get_duration_display() if session.ended_at else 'Activa',
        'duration_min': duration_min,
        'game_type': session.game_type or '-',
        'account': str(session.account) if session.account else '-',
        # KPIs
        'revenue': revenue,
        'revenue_per_hour': revenue_per_hour,
        'peak_viewers': peak,
        'avg_viewers': avg,
        'total_unique': total_unique,
        'total_joins': total_joins,
        'conversion_rate': conversion,
        'engagement_per_viewer': engagement_per_viewer,
        'avg_watch_min': avg_watch_min,
        # Counts
        'total_gifts': total_gifts,
        'total_diamonds': total_diamonds,
        'gifters_count': len(gifters),
        'total_comments': events.filter(event_type='CommentEvent').count(),
        'total_likes': events.filter(event_type='LikeEvent').count(),
        'total_follows': events.filter(event_type='FollowEvent').count(),
    }


def dashboard(request):
    """Dashboard de analytics post-live"""
    sessions = LiveSession.objects.filter(
        status='completed'
    ).order_by('-started_at')

    sessions_data = [_session_metrics(s) for s in sessions]

    # Aggregates
    total_revenue = sum(s['revenue'] for s in sessions_data)
    avg_revenue_hr = round(
        sum(s['revenue_per_hour'] for s in sessions_data) / len(sessions_data), 2
    ) if sessions_data else 0
    avg_peak = round(
        sum(s['peak_viewers'] for s in sessions_data) / len(sessions_data), 1
    ) if sessions_data else 0
    avg_conversion = round(
        sum(s['conversion_rate'] for s in sessions_data) / len(sessions_data), 1
    ) if sessions_data else 0

    # JSON-safe version for JS (dates as strings)
    sessions_json = json.dumps([
        {**s, 'started_at': s['started_at'].isoformat() if s['started_at'] else None}
        for s in sessions_data
    ])

    return render(request, 'tiktok_events/dashboard.html', {
        'sessions': sessions_data,
        'sessions_json': sessions_json,
        'total_revenue': total_revenue,
        'avg_revenue_hr': avg_revenue_hr,
        'avg_peak': avg_peak,
        'avg_conversion': avg_conversion,
        'total_sessions': len(sessions_data),
    })


def session_detail_api(request, session_id):
    """API: datos detallados de una sesion para graficos"""
    try:
        session = LiveSession.objects.get(id=session_id)
    except LiveSession.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    events = LiveEvent.objects.filter(session=session).order_by('timestamp')

    # Viewer timeline (sampled every ~10 seconds to reduce noise)
    viewer_raw = []
    for vc in events.filter(event_type='ViewerCountEvent'):
        d = _parse_event_data(vc)
        elapsed = (vc.timestamp - session.started_at).total_seconds()
        viewer_raw.append({
            'sec': round(elapsed),
            'min': round(elapsed / 60, 2),
            'viewers': d.get('viewer_count', 0),
            'unique': d.get('total_unique_viewers', 0),
            'time': vc.timestamp.strftime('%H:%M:%S'),
        })

    # Sample: keep 1 point per 10 seconds
    viewer_timeline = []
    last_sec = -10
    for v in viewer_raw:
        if v['sec'] - last_sec >= 10:
            viewer_timeline.append(v)
            last_sec = v['sec']

    # Events by minute (stacked)
    duration_min = int(session.get_duration() / 60) + 1 if session.ended_at else 1
    events_by_min = {m: {'joins': 0, 'gifts': 0, 'comments': 0, 'likes': 0} for m in range(duration_min)}

    for e in events.exclude(event_type='ViewerCountEvent'):
        m = int((e.timestamp - session.started_at).total_seconds() / 60)
        m = min(m, duration_min - 1)
        etype = e.event_type.replace('Event', '').lower() + 's'
        if etype in events_by_min.get(m, {}):
            events_by_min[m][etype] += 1

    # Gift breakdown
    gifts = {}
    top_gifters = {}
    for g in events.filter(event_type='GiftEvent'):
        d = _parse_event_data(g)
        name = d.get('gift', {}).get('name', '?')
        diamonds = d.get('gift', {}).get('diamond_count', 0) or 0
        repeat = d.get('repeat_count', 1) or 1
        user = g.user_nickname or g.user_unique_id or '?'

        gifts.setdefault(name, {'count': 0, 'diamonds': 0})
        gifts[name]['count'] += repeat
        gifts[name]['diamonds'] += diamonds * repeat

        top_gifters.setdefault(user, {'count': 0, 'diamonds': 0})
        top_gifters[user]['count'] += repeat
        top_gifters[user]['diamonds'] += diamonds * repeat

    top_gifters = dict(sorted(top_gifters.items(), key=lambda x: x[1]['diamonds'], reverse=True)[:10])

    return JsonResponse({
        'viewer_timeline': viewer_timeline,
        'events_by_min': [{'min': m, **d} for m, d in sorted(events_by_min.items())],
        'gifts': gifts,
        'top_gifters': top_gifters,
    })


def compare_sessions_api(request):
    """API: comparar sesiones"""
    ids = [int(i) for i in request.GET.get('ids', '').split(',') if i.strip().isdigit()]
    if len(ids) < 2:
        return JsonResponse({'error': 'Need 2+ session IDs'}, status=400)

    sessions = []
    for sid in ids:
        try:
            s = LiveSession.objects.get(id=sid)
            sessions.append(_session_metrics(s))
        except LiveSession.DoesNotExist:
            continue

    return JsonResponse({'sessions': sessions})
