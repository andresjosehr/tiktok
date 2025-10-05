from django.contrib import admin
from django.utils.html import format_html
from .models import Service, ServiceEventConfig, EventQueue


class ServiceEventConfigInline(admin.TabularInline):
    model = ServiceEventConfig
    extra = 1
    fields = ['event_type', 'is_enabled', 'priority', 'is_async', 'is_discardable', 'is_stackable']
    ordering = ['-priority', 'event_type']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'is_active_badge',
        'max_queue_size',
        'pending_count',
        'processing_count',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'service_class', 'description']
    readonly_fields = ['id', 'created_at', 'pending_count', 'processing_count']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceEventConfigInline]

    fieldsets = (
        ('Información General', {
            'fields': ('id', 'name', 'slug', 'description')
        }),
        ('Configuración Técnica', {
            'fields': ('service_class', 'is_active', 'max_queue_size')
        }),
        ('Estadísticas', {
            'fields': ('pending_count', 'processing_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def is_active_badge(self, obj):
        """Muestra badge de estado activo/inactivo"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">ACTIVO</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">INACTIVO</span>'
        )
    is_active_badge.short_description = 'Estado'

    def pending_count(self, obj):
        """Muestra eventos pendientes"""
        count = obj.get_pending_count()
        if count > obj.max_queue_size * 0.8:  # Alerta si está al 80%
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{}</span>',
                count
            )
        return count
    pending_count.short_description = 'Pendientes'

    def processing_count(self, obj):
        """Muestra eventos en procesamiento"""
        return obj.get_processing_count()
    processing_count.short_description = 'Procesando'


@admin.register(ServiceEventConfig)
class ServiceEventConfigAdmin(admin.ModelAdmin):
    list_display = [
        'service',
        'event_type',
        'enabled_badge',
        'priority_badge',
        'mode_badge',
        'discardable_badge',
        'stackable_badge'
    ]
    list_filter = ['service', 'event_type', 'is_enabled', 'is_async', 'is_discardable', 'is_stackable', 'priority']
    search_fields = ['service__name', 'event_type']
    ordering = ['service', '-priority', 'event_type']

    fieldsets = (
        ('Configuración Básica', {
            'fields': ('service', 'event_type', 'is_enabled')
        }),
        ('Configuración de Procesamiento', {
            'fields': ('priority', 'is_async', 'is_discardable', 'is_stackable')
        }),
    )

    def enabled_badge(self, obj):
        """Badge de habilitado/deshabilitado"""
        if obj.is_enabled:
            return format_html('<span style="color: #28a745;">✅ Habilitado</span>')
        return format_html('<span style="color: #6c757d;">❌ Deshabilitado</span>')
    enabled_badge.short_description = 'Estado'

    def priority_badge(self, obj):
        """Badge de prioridad con color"""
        if obj.priority >= 8:
            color = '#dc3545'  # Rojo (alta)
        elif obj.priority >= 5:
            color = '#ffc107'  # Amarillo (media)
        else:
            color = '#28a745'  # Verde (baja)

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.priority
        )
    priority_badge.short_description = 'Prioridad'

    def mode_badge(self, obj):
        """Badge de modo async/sync"""
        if obj.is_async:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">ASYNC</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">SYNC</span>'
        )
    mode_badge.short_description = 'Modo'

    def discardable_badge(self, obj):
        """Badge de descartable"""
        if obj.is_discardable:
            return format_html('<span style="color: #ffc107;">⚠️ Descartable</span>')
        return format_html('<span style="color: #dc3545;">🔒 No descartable</span>')
    discardable_badge.short_description = 'Descarte'

    def stackable_badge(self, obj):
        """Badge de stackable"""
        if obj.is_stackable:
            return format_html('<span style="color: #28a745;">📚 Stackable</span>')
        return format_html('<span style="color: #007bff;">🎯 Solo al finalizar</span>')
    stackable_badge.short_description = 'Racha'


@admin.register(EventQueue)
class EventQueueAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'service',
        'event_type_display',
        'status_badge',
        'priority_badge',
        'mode_badge',
        'session',
        'created_at',
        'processed_at'
    ]
    list_filter = ['service', 'status', 'priority', 'is_async', 'created_at']
    search_fields = ['service__name', 'live_event__event_type', 'live_event__user_unique_id']
    readonly_fields = [
        'id',
        'service',
        'live_event',
        'session',
        'priority',
        'is_async',
        'created_at',
        'processed_at',
        'event_details'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información de la Cola', {
            'fields': ('id', 'service', 'status', 'created_at', 'processed_at')
        }),
        ('Evento Relacionado', {
            'fields': ('live_event', 'session', 'event_details')
        }),
        ('Configuración', {
            'fields': ('priority', 'is_async')
        }),
    )

    def event_type_display(self, obj):
        """Muestra el tipo de evento"""
        return obj.live_event.event_type
    event_type_display.short_description = 'Tipo de Evento'

    def status_badge(self, obj):
        """Badge de estado"""
        color_map = {
            'pending': '#ffc107',
            'processing': '#007bff',
            'completed': '#28a745',
            'failed': '#dc3545',
            'discarded': '#6c757d'
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Estado'

    def priority_badge(self, obj):
        """Badge de prioridad"""
        if obj.priority >= 8:
            color = '#dc3545'
        elif obj.priority >= 5:
            color = '#ffc107'
        else:
            color = '#28a745'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.priority
        )
    priority_badge.short_description = 'Prioridad'

    def mode_badge(self, obj):
        """Badge de modo"""
        if obj.is_async:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">ASYNC</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">SYNC</span>'
        )
    mode_badge.short_description = 'Modo'

    def event_details(self, obj):
        """Muestra detalles del evento"""
        event = obj.live_event
        details = f"""
        <strong>Tipo:</strong> {event.event_type}<br>
        <strong>Usuario:</strong> {event.user_nickname or 'N/A'} (@{event.user_unique_id or 'N/A'})<br>
        <strong>Timestamp:</strong> {event.timestamp}<br>
        <strong>Room ID:</strong> {event.room_id}
        """
        return format_html(details)
    event_details.short_description = 'Detalles del Evento'
