from django.contrib import admin
from apps.services.music.models import MusicCredit, MusicHistory


@admin.register(MusicCredit)
class MusicCreditAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'session',
        'total_gifts',
        'credits_used',
        'get_credits_available',
        'last_gift_at',
        'last_request_at'
    )
    list_filter = ('session', 'last_gift_at', 'last_request_at')
    search_fields = ('username',)
    readonly_fields = ('created_at', 'updated_at', 'get_credits_available')
    ordering = ('-total_gifts', 'username')

    def get_credits_available(self, obj):
        return obj.credits_available
    get_credits_available.short_description = 'Creditos Disponibles'

    fieldsets = (
        ('Informacion del Usuario', {
            'fields': ('session', 'username')
        }),
        ('Creditos', {
            'fields': ('total_gifts', 'credits_used', 'get_credits_available')
        }),
        ('Historial', {
            'fields': ('last_gift_at', 'last_request_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(MusicHistory)
class MusicHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'title',
        'query',
        'duration',
        'started_at',
        'was_interrupted',
        'session'
    )
    list_filter = ('session', 'was_interrupted', 'started_at')
    search_fields = ('username', 'title', 'query', 'youtube_id')
    readonly_fields = (
        'session',
        'username',
        'query',
        'youtube_url',
        'youtube_id',
        'title',
        'duration',
        'file_path',
        'started_at',
        'finished_at',
        'was_interrupted',
        'created_at',
        'updated_at'
    )
    ordering = ('-started_at',)

    fieldsets = (
        ('Informacion del Usuario', {
            'fields': ('session', 'username')
        }),
        ('Busqueda', {
            'fields': ('query',)
        }),
        ('Video de YouTube', {
            'fields': ('youtube_url', 'youtube_id', 'title', 'duration')
        }),
        ('Reproduccion', {
            'fields': ('file_path', 'started_at', 'finished_at', 'was_interrupted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Deshabilitar agregar manualmente"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Permitir solo eliminar"""
        return True
