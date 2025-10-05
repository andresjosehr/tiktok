from django.contrib import admin
from django.utils.html import format_html
import json
from .models import LiveEvent, LiveSession


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name_or_id',
        'streamer_unique_id',
        'status_badge',
        'started_at',
        'ended_at',
        'duration_display',
        'total_events'
    ]
    list_filter = [
        'status',
        'started_at',
        'streamer_unique_id'
    ]
    search_fields = [
        'name',
        'streamer_unique_id',
        'room_id',
        'notes'
    ]
    readonly_fields = [
        'id',
        'started_at',
        'total_events',
        'duration_display'
    ]
    ordering = ['-started_at']
    date_hierarchy = 'started_at'

    def name_or_id(self, obj):
        """Muestra el nombre o ID de la sesión"""
        return obj.name if obj.name else f"Session #{obj.id}"
    name_or_id.short_description = 'Sesión'

    def status_badge(self, obj):
        """Muestra badge de estado"""
        color_map = {
            'active': '#28a745',
            'completed': '#007bff',
            'aborted': '#dc3545'
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Estado'

    def duration_display(self, obj):
        """Muestra la duración"""
        return obj.get_duration_display()
    duration_display.short_description = 'Duración'

    fieldsets = (
        ('Información General', {
            'fields': ('id', 'name', 'status')
        }),
        ('Contexto del Live', {
            'fields': ('room_id', 'streamer_unique_id')
        }),
        ('Tiempo', {
            'fields': ('started_at', 'ended_at', 'duration_display')
        }),
        ('Estadísticas', {
            'fields': ('total_events',)
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(LiveEvent)
class LiveEventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'event_type',
        'user_info',
        'timestamp',
        'session',
        'room_id',
        'streak_badge',
        'created_at'
    ]
    list_filter = [
        'event_type',
        'is_streaking',
        'streak_status',
        'timestamp',
        'streamer_unique_id',
        'session'
    ]
    search_fields = [
        'user_unique_id',
        'user_nickname',
        'streamer_unique_id',
        'room_id'
    ]
    readonly_fields = [
        'id',
        'event_type',
        'timestamp',
        'session',
        'room_id',
        'streamer_unique_id',
        'user_id',
        'user_unique_id',
        'user_nickname',
        'is_streaking',
        'streak_id',
        'streak_status',
        'formatted_event_data',
        'created_at'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

    def user_info(self, obj):
        """Muestra información del usuario"""
        return f"{obj.user_nickname or 'N/A'} (@{obj.user_unique_id or 'N/A'})"
    user_info.short_description = 'Usuario'

    def streak_badge(self, obj):
        """Muestra badge de racha"""
        if obj.streak_status:  # Cambiado: mostrar si tiene streak_status, no solo si is_streaking
            color_map = {
                'start': '#28a745',
                'continue': '#ffc107',
                'end': '#dc3545'
            }
            color = color_map.get(obj.streak_status, '#6c757d')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
                color,
                obj.streak_status.upper()
            )
        return '-'
    streak_badge.short_description = 'Racha'

    def formatted_event_data(self, obj):
        """Muestra el JSON formateado"""
        if obj.event_data:
            formatted_json = json.dumps(obj.event_data, indent=2, ensure_ascii=False)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    formatted_event_data.short_description = 'Event Data (JSON)'

    fieldsets = (
        ('Información del Evento', {
            'fields': ('id', 'event_type', 'timestamp', 'created_at')
        }),
        ('Sesión', {
            'fields': ('session',)
        }),
        ('Contexto del Live', {
            'fields': ('room_id', 'streamer_unique_id')
        }),
        ('Usuario', {
            'fields': ('user_id', 'user_unique_id', 'user_nickname')
        }),
        ('Control de Rachas', {
            'fields': ('is_streaking', 'streak_id', 'streak_status'),
            'classes': ('collapse',)
        }),
        ('Datos del Evento', {
            'fields': ('formatted_event_data',)
        }),
    )
