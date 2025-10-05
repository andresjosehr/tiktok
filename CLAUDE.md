# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based system for capturing TikTok Live events and processing them through a queue system with multiple services. The system uses Docker for containerization.

## Key Commands

All commands must be run through Docker Compose:

```bash
# Database operations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py makemigrations

# Initialize system with default services (DinoChrome, Overlays) and config
docker-compose exec web python manage.py populate_initial_data

# Capture TikTok Live events (creates new session each run)
docker-compose exec web python manage.py capture_tiktok_live [--username NAME] [--session-name NAME]

# Process queued events with workers
docker-compose exec web python manage.py run_queue_workers [--service SLUG] [--verbose]

# Database reset (drops all tables)
docker-compose exec db bash -c "mysql -u root -p\${MYSQL_ROOT_PASSWORD} tiktok_db -e 'DROP DATABASE tiktok_db; CREATE DATABASE tiktok_db;'"
```

## Architecture

### Three-Layer System

1. **Capture Layer** (`apps/tiktok_events`):
   - `TikTokEventCapture` connects to TikTok Live using `TikTokLiveClient`
   - Each event handler (on_gift, on_comment, etc.) creates a `LiveEvent`
   - Immediately calls `EventDispatcher.dispatch()` to distribute to service queues
   - Events are grouped into `LiveSession` instances (one per capture run)

2. **Distribution Layer** (`apps/queue_system/dispatcher.py`):
   - `EventDispatcher.dispatch()` receives a `LiveEvent`
   - Queries `ServiceEventConfig` to find active services subscribed to that event type
   - For each service: checks queue size, handles overflow by discarding low-priority events
   - Creates `EventQueue` items with priority from config

3. **Processing Layer** (`apps/queue_system/worker.py`):
   - `ServiceWorker` runs in separate thread per active service
   - Pulls events from `EventQueue` ordered by priority DESC, created_at ASC
   - SYNC mode: processes one at a time (waits for completion)
   - ASYNC mode: spawns thread per event (parallel processing)
   - Marks events as completed/failed/discarded

### Critical Flow

```
TikTok Event → LiveEvent.create() → EventDispatcher.dispatch()
    ↓
ServiceEventConfig lookup (active services subscribed to event type)
    ↓
EventQueue.create() per service (with priority, is_async from config)
    ↓
ServiceWorker pulls by priority → service_instance.process_event()
```

## Core Models

### `apps/tiktok_events/models.py`
- **LiveSession**: Groups events by capture period (started_at, ended_at, status)
- **LiveEvent**: Individual TikTok events (event_type, user_*, event_data JSON, streak fields)
  - Foreign key to LiveSession
  - event_data is JSONField with event-specific structure

### `apps/queue_system/models.py`
- **Service**: Service definition (slug, service_class path, max_queue_size, is_active)
- **ServiceEventConfig**: Per-service event settings (event_type, priority 1-10, is_async, is_discardable)
  - Unique constraint: (service, event_type)
- **EventQueue**: Queued events per service (service FK, live_event FK, priority, is_async, status)
  - Status: pending → processing → completed/failed/discarded
  - priority and is_async copied from ServiceEventConfig at enqueue time

## Creating New Services

1. Create class inheriting from `BaseQueueService` in `apps/yourservice/services.py`
2. Implement required `process_event(live_event, queue_item) -> bool`
3. Optional hooks: `on_start()`, `on_stop()`, `on_event_received()`, `on_event_processed()`
4. Register in admin: slug, service_class path (e.g., `apps.yourservice.services.YourService`)
5. Configure event subscriptions via ServiceEventConfig inline in admin

**Key points:**
- `process_event()` must return True/False for success/failure
- Service class is loaded dynamically via importlib by ServiceWorker
- Worker automatically handles SYNC vs ASYNC based on EventQueue.is_async field
- Django DB connections closed in worker threads via `close_old_connections()`

## Important Patterns

### Event Distribution Logic

When queue is full (size >= max_queue_size):
1. If new event is discardable: try to discard lower-priority discardable event, else drop new event
2. If new event is NOT discardable: discard lower-priority discardable event if exists, else drop new event
3. Priority comparison: only discard if existing event priority < new event priority

### Worker Threading Model

- Main thread per service runs `_run_loop()`
- SYNC events: processed in main thread (blocking)
- ASYNC events: spawned in separate daemon thread (non-blocking)
- Async threads tracked in list, cleaned up periodically
- Graceful shutdown: stops loop, joins threads with timeout

### Session Management

- Session created in `TikTokEventCapture.on_connect()`
- All subsequent events link to that session
- Session ended on KeyboardInterrupt (status='completed') or Exception (status='aborted')
- `end_session()` sets ended_at and status

## Django Apps Structure

- `apps/tiktok_events`: Event capture from TikTok Live
- `apps/queue_system`: Generic queue system (independent from TikTok)
- `apps/app_config`: Key-value config store (Config model with meta_key/meta_value)
- `apps/test_service`: Example services (DummyService, SlowService, VerboseService)

## Data Population

`populate_initial_data` command creates:
- Config entry: tiktok_user (empty)
- Service: DinoChrome (SYNC for all events, max_queue_size=50)
- Service: Overlays (ASYNC for all events, max_queue_size=100)
- 7 ServiceEventConfig per service with priorities:
  - GiftEvent: P10 (never discardable)
  - SubscribeEvent: P9/P8
  - FollowEvent: P8/P7
  - ShareEvent: P7/P6
  - CommentEvent: P6/P5 (discardable)
  - LikeEvent: P3/P2 (discardable)
  - JoinEvent: P2/P3 (DinoChrome disabled, Overlays enabled, discardable)

## Common Pitfalls

- EventDispatcher must be called AFTER LiveEvent.create() to ensure event has ID
- Service class path must be importable (check INSTALLED_APPS and module structure)
- Workers must be running (`run_queue_workers`) for events to be processed
- Queue items remain in 'pending' state if no workers are running
- SYNC services can create bottlenecks if process_event() is slow
- MySQL utf8mb3 charset limits emoji support - use clean_text() for user input
