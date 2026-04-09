# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based system for capturing TikTok Live events and processing them through a queue system with multiple interactive game services. Designed for running multiple simultaneous TikTok Live streams ("live farming") with automated interactive content that reacts to viewer gifts in real-time.

Business documentation in `docs/tiktok-farm/` (business model, infrastructure, games, risks, execution plan).

## Key Commands

```bash
# Docker (production)
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py populate_initial_data
docker-compose exec web python manage.py start_event_system [--session-name NAME] [--verbose]
docker-compose exec web python manage.py capture_tiktok_live [--username NAME]
docker-compose exec web python manage.py run_queue_workers [--service SLUG]

# Local development (SQLite - no .env or DB_ENGINE=sqlite)
python manage.py migrate
python manage.py runserver 8080

# Analytics dashboard
# http://localhost:8080/analytics/

# Download music from Google Drive (requires gdown or Google Drive API key)
python manage.py download_music
```

## Architecture

### Three-Layer System

1. **Capture Layer** (`apps/tiktok_events`):
   - `TikTokEventCapture` connects to TikTok Live using `TikTokLiveClient`
   - Captures: GiftEvent, CommentEvent, LikeEvent, ShareEvent, FollowEvent, JoinEvent, SubscribeEvent, **ViewerCountEvent** (via RoomUserSeqEvent)
   - Events grouped into `LiveSession` instances linked to `TikTokAccount`
   - Auto-links session to TikTokAccount by matching `streamer_unique_id`

2. **Distribution Layer** (`apps/queue_system/dispatcher.py`):
   - `EventDispatcher.dispatch()` routes events to subscribed services
   - Priority system with gift-based overrides (Rosa P:10, Rose P:9, Ice Cream P:8)
   - Queue overflow handling: discards low-priority events when full

3. **Processing Layer** (`apps/queue_system/worker.py`):
   - `ServiceWorker` per active service (SYNC or ASYNC mode)
   - Services process events via `process_event(live_event, queue_item) -> bool`

### Critical Flow

```
TikTok Event → LiveEvent.create() → EventDispatcher.dispatch()
    → ServiceEventConfig lookup → EventQueue.create() per service
    → ServiceWorker pulls by priority → service.process_event()
```

## Core Models

### `apps/tiktok_events/models.py`
- **TikTokAccount**: Account management (country, agency, proxy, purchase_price, follower_count)
- **LiveSession**: Capture session (account FK, game_type, started_at, ended_at, status)
- **LiveEvent**: Individual events (event_type, user_*, event_data JSON, streak fields)
  - `ViewerCountEvent`: viewer_count (concurrent), total_unique_viewers, anonymous

### `apps/queue_system/models.py`
- **Service**: Service definition (slug, service_class, max_queue_size, is_active)
- **ServiceEventConfig**: Per-service event config (priority 1-10, is_async, is_discardable)
- **EventQueue**: Queued events (status: pending → processing → completed/failed/discarded)

## Django Apps Structure

- `apps/tiktok_events`: Event capture + **TikTokAccount** + **Analytics dashboard** (`/analytics/`)
- `apps/queue_system`: Generic queue system with dispatcher, workers, base service
- `apps/app_config`: Key-value config store (Config model)
- `apps/services/dinochrome`: Chrome automation with DinoChrome game (SYNC)
- `apps/services/overlays`: Visual overlays (ASYNC)
- `apps/services/music`: **Local MP3 playback from media/music/** (gift GG = next track)
- `apps/integrations/elevenlabs`: ElevenLabs TTS (text-to-speech + VLC playback)
- `apps/integrations/llm`: Generic LLM client (OpenAI-compatible)
- `apps/integrations/obs`: OBS WebSocket control
- `apps/audio_player`: Web-based audio player with dual channels (music/voice)
- `apps/simulator`: Event simulator for testing without live TikTok
- `apps/base_models`: Abstract BaseModel with timestamps

## Music Service

Music service was refactored from YouTube-based (with credits system) to local MP3 playback:
- Plays MP3s from `media/music/` sequentially (shuffled on start)
- Gift "GG" = skip to next track (no credits, no conditions)
- Music sourced from Epidemic Sound (royalty-free, legal for TikTok Live)
- `scripts/epidemic_downloader.js` - Browser console script for bulk downloading from Epidemic Sound
- Music files stored in Google Drive, downloadable via `python manage.py download_music`

## Analytics Dashboard

Available at `/analytics/` with:
- KPIs per session: revenue, $/hr, peak viewers, conversion rate, avg watch time
- Viewer timeline chart (concurrent + unique accumulated, dual axis)
- Activity by minute (stacked bar: joins, gifts, comments, likes)
- Gift breakdown + top gifters
- Session comparison mode
- API endpoints: `/analytics/api/session/<id>/`, `/analytics/api/compare/?ids=1,2,3`

## Creating New Services (Games)

1. Create class inheriting from `BaseQueueService`
2. Implement `process_event(live_event, queue_item) -> bool`
3. Optional hooks: `on_start()`, `on_stop()`
4. Register in admin with service_class path
5. Configure event subscriptions via ServiceEventConfig

New games should be web-based (HTML/CSS/JS as OBS browser source) receiving events via SSE from Django. NOT Selenium-based like DinoChrome.

## Important Patterns

### ViewerCountEvent
- Captured via `RoomUserSeqEvent` from TikTokLive library
- Fields: `m_total` = concurrent viewers, `total_user` = unique accumulated, `anonymous` = anonymous count
- Stored as LiveEvent with event_type='ViewerCountEvent'
- NOT dispatched to service queues (informational only)

### Session-Account Linking
- `TikTokAccount` stores account metadata (country, proxy, agency, purchase info)
- `LiveSession.account` auto-linked on connect by matching `unique_id`
- `LiveSession.game_type` tracks which game/service was active

### Audio Playback
- VLC used for both TTS (ElevenLabs) and music playback
- Windows: `--directx-audio-device` flag for per-instance audio routing
- Music at `--gain=0.1` (10%) to not compete with voice

## Common Pitfalls

- EventDispatcher must be called AFTER LiveEvent.create()
- Service class path must be importable (check INSTALLED_APPS)
- Workers must be running for events to be processed
- MySQL utf8mb3 charset limits emoji support - use clean_text()
- ElevenLabs playback: use `wait=True` in SYNC services
- ViewerCountEvent uses `m_total` for concurrent viewers (NOT `m_popularity` which is always 0)
- Copyright music is NOT allowed on TikTok Live - use Epidemic Sound or royalty-free only
- TikTok Live Studio requires 3 lives of 25 min each to unlock virtual camera
