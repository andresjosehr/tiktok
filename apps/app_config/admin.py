from django.contrib import admin
from django.utils.html import format_html
from .models import Config


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['meta_key', 'meta_value_preview', 'updated_at', 'created_at']
    search_fields = ['meta_key', 'meta_value']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['meta_key']

    def meta_value_preview(self, obj):
        """Muestra preview del valor"""
        if len(obj.meta_value) > 100:
            return format_html(
                '<span title="{}">{}</span>',
                obj.meta_value,
                obj.meta_value[:100] + '...'
            )
        return obj.meta_value
    meta_value_preview.short_description = 'Valor'

    fieldsets = (
        ('Configuración', {
            'fields': ('meta_key', 'meta_value')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
