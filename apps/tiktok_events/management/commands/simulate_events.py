"""
Comando para simular eventos de TikTok de manera continua para testing

Uso:
    python manage.py simulate_events --duration 120 --interval 3
    python manage.py simulate_events --duration 60 --interval 2 --verbose
    python manage.py simulate_events --forever --interval 5

Eventos simulados:
    - Ice Cream Cone: LLM + TTS + restart (P:10)
    - Rose: TTS simple (P:9)
    - You're Awesome: GIF overlay (P:8)
    - GG: Créditos de música
    - Comentarios !cancion: Solicitud de música
    - Enjoy Music: GIF overlay (P:8)

Validación:
    Revisar logs/event_system.log para verificar:
    - [DISPATCHER] Regalo 'X' → Prioridad: Y
    - [DINOCHROME] procesando...
    - [MUSIC] reproduciendo...
    - [ELEVENLABS] Audio reproducido
    - [LLM] Response received
"""

import time
import random
import signal
import sys
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tiktok_events.models import LiveSession, LiveEvent
from apps.queue_system.dispatcher import EventDispatcher


class Command(BaseCommand):
    help = 'Simula eventos de TikTok de manera continua para testing integral'

    def __init__(self):
        super().__init__()
        self.running = True
        self.session = None
        self.stats = {
            'ice_cream': 0,
            'rose': 0,
            'awesome': 0,
            'gg': 0,
            'music_comment': 0,
            'enjoy_music': 0,
            'total': 0,
        }
        # Nombres de usuario aleatorios para simular variedad
        self.usernames = [
            'Carlos_Gaming', 'Maria_Live', 'Pedro_TikTok', 'Ana_Streamer',
            'Luis_Viewer', 'Sofia_Fan', 'Diego_Pro', 'Laura_VIP',
            'Miguel_Boss', 'Carmen_Queen', 'Pablo_King', 'Elena_Star',
            'Andres_Dev', 'Lucia_Cool', 'Roberto_Gamer', 'Patricia_Fun'
        ]
        # Canciones para solicitar
        self.songs = [
            '!despacito', '!shakira', '!bad bunny', '!karol g',
            '!dua lipa', '!taylor swift', '!reggaeton', '!salsa'
        ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='Duración del test en segundos (default: 60)'
        )
        parser.add_argument(
            '--interval',
            type=float,
            default=3.0,
            help='Segundos entre eventos (default: 3.0)'
        )
        parser.add_argument(
            '--forever',
            action='store_true',
            help='Ejecutar indefinidamente hasta Ctrl+C'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar detalles de cada evento'
        )
        parser.add_argument(
            '--weights',
            type=str,
            default='ice_cream:1,rose:3,awesome:4,gg:2,music:1,enjoy:2',
            help='Pesos de probabilidad para cada tipo de evento'
        )

    def handle(self, *args, **options):
        # Configurar señal para Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        duration = options['duration']
        interval = options['interval']
        forever = options['forever']
        verbose = options['verbose']

        # Parsear pesos
        weights = self._parse_weights(options['weights'])

        # Banner
        self._show_banner(duration, interval, forever, weights)

        # Crear sesión de prueba
        self.session = self._create_session()

        start_time = time.time()
        event_count = 0

        try:
            while self.running:
                # Verificar duración (si no es forever)
                if not forever:
                    elapsed = time.time() - start_time
                    if elapsed >= duration:
                        break

                # Generar evento aleatorio
                event_type = self._choose_event_type(weights)
                event = self._create_event(event_type, verbose)

                if event:
                    # Despachar evento
                    result = EventDispatcher.dispatch(event)
                    event_count += 1
                    self.stats['total'] += 1
                    self.stats[event_type] += 1

                    if verbose:
                        self._show_dispatch_result(event_type, result)
                    else:
                        self._show_progress(event_count, duration if not forever else None, start_time)

                # Esperar intervalo
                time.sleep(interval)

        except KeyboardInterrupt:
            pass

        # Resumen final
        self._show_summary(time.time() - start_time)

    def _signal_handler(self, signum, frame):
        self.stdout.write("\n⚠️  Deteniendo simulación...")
        self.running = False

    def _parse_weights(self, weights_str):
        """Parsea string de pesos a diccionario"""
        weights = {}
        default_weights = {
            'ice_cream': 1,
            'rose': 3,
            'awesome': 4,
            'gg': 2,
            'music_comment': 1,
            'enjoy_music': 2
        }

        try:
            for part in weights_str.split(','):
                key, value = part.split(':')
                key = key.strip()
                # Mapear nombres cortos
                key_map = {
                    'ice_cream': 'ice_cream',
                    'ice': 'ice_cream',
                    'rose': 'rose',
                    'awesome': 'awesome',
                    'gg': 'gg',
                    'music': 'music_comment',
                    'enjoy': 'enjoy_music',
                    'enjoy_music': 'enjoy_music'
                }
                if key in key_map:
                    weights[key_map[key]] = int(value)
        except:
            weights = default_weights

        # Completar con defaults
        for key, value in default_weights.items():
            if key not in weights:
                weights[key] = value

        return weights

    def _show_banner(self, duration, interval, forever, weights):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("🧪 SIMULADOR CONTINUO DE EVENTOS TIKTOK"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        if forever:
            self.stdout.write(f"⏱️  Duración: INFINITA (Ctrl+C para detener)")
        else:
            self.stdout.write(f"⏱️  Duración: {duration} segundos")

        self.stdout.write(f"⏳ Intervalo: {interval} segundos entre eventos")
        self.stdout.write("")
        self.stdout.write("📊 Probabilidades de eventos:")
        total_weight = sum(weights.values())
        for event_type, weight in weights.items():
            pct = (weight / total_weight) * 100
            emoji = {
                'ice_cream': '🍦',
                'rose': '🌹',
                'awesome': '💃',
                'gg': '🎮',
                'music_comment': '🎵',
                'enjoy_music': '🎶'
            }.get(event_type, '📦')
            self.stdout.write(f"   {emoji} {event_type}: {pct:.0f}%")

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("📝 Los eventos se loguean en: logs/event_system.log"))
        self.stdout.write(self.style.WARNING("💡 Presiona Ctrl+C para detener"))
        self.stdout.write("")
        self.stdout.write("-" * 60)

    def _create_session(self):
        """Crea sesión de prueba"""
        session = LiveSession.objects.create(
            name=f"[TEST] Simulación continua - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            status='active',
            room_id=999999999,
            streamer_unique_id='test_streamer',
            notes='Sesión de prueba generada por simulate_events'
        )
        self.stdout.write(f"📋 Sesión creada: ID {session.id}")
        self.stdout.write("-" * 60)
        return session

    def _choose_event_type(self, weights):
        """Elige tipo de evento basado en pesos"""
        choices = []
        for event_type, weight in weights.items():
            choices.extend([event_type] * weight)
        return random.choice(choices)

    def _create_event(self, event_type, verbose):
        """Crea el evento según el tipo"""
        username = random.choice(self.usernames)
        user_id = abs(hash(username + str(time.time()))) % 10000000000

        if event_type == 'ice_cream':
            return self._create_gift_event('Ice Cream Cone', username, user_id)
        elif event_type == 'rose':
            return self._create_gift_event('Rose', username, user_id)
        elif event_type == 'awesome':
            return self._create_gift_event("You're Awesome", username, user_id)
        elif event_type == 'gg':
            count = random.choice([1, 2, 3, 5])
            return self._create_gift_event('GG', username, user_id, count=count)
        elif event_type == 'enjoy_music':
            return self._create_gift_event('Enjoy Music', username, user_id)
        elif event_type == 'music_comment':
            song = random.choice(self.songs)
            return self._create_comment_event(song, username, user_id)

        return None

    def _create_gift_event(self, gift_name, username, user_id, count=1):
        """Crea un evento de regalo"""
        event = LiveEvent.objects.create(
            session=self.session,
            event_type='GiftEvent',
            timestamp=timezone.now(),
            room_id=self.session.room_id,
            streamer_unique_id=self.session.streamer_unique_id,
            user_id=user_id,
            user_unique_id=username.lower().replace(' ', '_'),
            user_nickname=username,
            is_streaking=False,
            streak_status='end',
            event_data={
                'gift': {
                    'id': abs(hash(gift_name)) % 10000,
                    'name': gift_name,
                    'count': count,
                    'diamond_count': 1,
                },
                'repeat_count': count,
                'user': {
                    'unique_id': username.lower().replace(' ', '_'),
                    'nickname': username,
                    'user_id': user_id,
                }
            }
        )
        self.session.increment_events()
        return event

    def _create_comment_event(self, comment, username, user_id):
        """Crea un evento de comentario"""
        event = LiveEvent.objects.create(
            session=self.session,
            event_type='CommentEvent',
            timestamp=timezone.now(),
            room_id=self.session.room_id,
            streamer_unique_id=self.session.streamer_unique_id,
            user_id=user_id,
            user_unique_id=username.lower().replace(' ', '_'),
            user_nickname=username,
            event_data={
                'comment': comment,
                'user': {
                    'unique_id': username.lower().replace(' ', '_'),
                    'nickname': username,
                    'user_id': user_id,
                }
            }
        )
        self.session.increment_events()
        return event

    def _show_dispatch_result(self, event_type, result):
        """Muestra resultado del dispatch en modo verbose"""
        emoji = {
            'ice_cream': '🍦',
            'rose': '🌹',
            'awesome': '💃',
            'gg': '🎮',
            'music_comment': '🎵',
            'enjoy_music': '🎶'
        }.get(event_type, '📦')

        enqueued = len(result.get('enqueued', []))

        if enqueued > 0:
            priorities = [str(e.get('priority', '?')) for e in result['enqueued']]
            self.stdout.write(
                f"{emoji} {event_type:15} → {enqueued} servicios (P:{','.join(priorities)})"
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"{emoji} {event_type:15} → No encolado")
            )

    def _show_progress(self, count, duration, start_time):
        """Muestra progreso en una línea"""
        if duration:
            elapsed = time.time() - start_time
            remaining = max(0, duration - elapsed)
            progress = min(100, (elapsed / duration) * 100)
            bar_len = 20
            filled = int(bar_len * progress / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"\r  [{bar}] {progress:.0f}% | Eventos: {count} | Restante: {remaining:.0f}s  ", end='', flush=True)
        else:
            print(f"\r  Eventos enviados: {count}  ", end='', flush=True)

    def _show_summary(self, elapsed_time):
        """Muestra resumen final"""
        self.stdout.write("")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN DE SIMULACIÓN"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")
        self.stdout.write(f"⏱️  Tiempo total: {elapsed_time:.1f} segundos")
        self.stdout.write(f"📦 Total eventos: {self.stats['total']}")
        self.stdout.write("")
        self.stdout.write("📈 Desglose por tipo:")
        self.stdout.write(f"   🍦 Ice Cream:    {self.stats['ice_cream']}")
        self.stdout.write(f"   🌹 Rose:         {self.stats['rose']}")
        self.stdout.write(f"   💃 Awesome:      {self.stats['awesome']}")
        self.stdout.write(f"   🎮 GG:           {self.stats['gg']}")
        self.stdout.write(f"   🎵 !cancion:     {self.stats['music_comment']}")
        self.stdout.write(f"   🎶 Enjoy Music:  {self.stats['enjoy_music']}")
        self.stdout.write("")
        self.stdout.write(f"📋 Session ID: {self.session.id}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("📝 Revisa logs/event_system.log para validar:"))
        self.stdout.write("   • [DISPATCHER] Regalo 'X' → Prioridad: Y")
        self.stdout.write("   • [DINOCHROME] procesando regalo...")
        self.stdout.write("   • [MUSIC] reproduciendo/créditos...")
        self.stdout.write("   • [ELEVENLABS] Audio reproducido")
        self.stdout.write("   • [LLM] Response received")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
