from django.contrib import admin
from django.utils.html import format_html
import json
from .models import LiveEvent


@admin.register(LiveEvent)
class LiveEventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'event_type',
        'user_info',
        'timestamp',
        'room_id',
        'streak_badge',
        'created_at'
    ]
    list_filter = [
        'event_type',
        'is_streaking',
        'streak_status',
        'timestamp',
        'streamer_unique_id'
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
