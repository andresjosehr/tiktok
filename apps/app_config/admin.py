from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django import forms
from .models import Config


class ConfigAdminForm(forms.ModelForm):
    """Custom form for Config admin with LLM URL dropdown"""

    LLM_PROVIDER_CHOICES = [
        ('https://api.openai.com/v1/chat/completions', 'OpenAI (ChatGPT)'),
        ('https://api.anthropic.com/v1/messages', 'Anthropic (Claude)'),
        ('https://api.deepseek.com/chat/completions', 'DeepSeek'),
        ('http://localhost:1234/v1/chat/completions', 'LMStudio (Local)'),
        ('', 'Custom URL'),
    ]

    class Meta:
        model = Config
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Check if this is llm_url (editing existing or data from GET/POST)
        is_llm_url = False

        if self.instance and self.instance.pk and self.instance.meta_key == 'llm_url':
            # Editing existing llm_url config
            is_llm_url = True
        elif self.data and self.data.get('meta_key') == 'llm_url':
            # Creating/submitting with meta_key = llm_url
            is_llm_url = True
        elif not self.instance.pk and self.initial.get('meta_key') == 'llm_url':
            # Initial data has meta_key = llm_url
            is_llm_url = True

        if is_llm_url:
            current_value = ''
            if self.instance and self.instance.pk:
                current_value = self.instance.meta_value
            elif self.data:
                current_value = self.data.get('meta_value', '')

            # Convert to dropdown
            self.fields['meta_value'] = forms.ChoiceField(
                choices=self.LLM_PROVIDER_CHOICES,
                initial=current_value if current_value else self.LLM_PROVIDER_CHOICES[0][0],
                widget=forms.Select(attrs={
                    'style': 'width: 100%;',
                    'id': 'id_meta_value',
                }),
                label='Provider URL',
                help_text='Select LLM provider. Choose "Custom URL" to enter your own.',
                required=False
            )

            # Add JavaScript to make meta_value editable when "Custom URL" is selected
            self.fields['meta_value'].widget.attrs['onchange'] = """
                if(this.value === '') {
                    var input = document.createElement('input');
                    input.type = 'text';
                    input.name = 'meta_value';
                    input.id = 'id_meta_value';
                    input.value = '';
                    input.style.width = '100%';
                    input.placeholder = 'Enter custom LLM API URL';
                    this.parentNode.replaceChild(input, this);
                    input.focus();
                }
            """


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    form = ConfigAdminForm
    change_list_template = 'admin/app_config/config/change_list.html'
    list_display = ['meta_key', 'meta_value_preview', 'updated_at', 'created_at']
    search_fields = ['meta_key', 'meta_value']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['meta_key']

    def get_urls(self):
        custom_urls = [
            path('refresh-obs/', self.admin_site.admin_view(self.refresh_obs_view), name='refresh_obs'),
            path('toggle-debug/', self.admin_site.admin_view(self.toggle_debug_view), name='toggle_debug'),
        ]
        return custom_urls + super().get_urls()

    def refresh_obs_view(self, request):
        from apps.integrations.obs.client import OBSClient
        client = OBSClient()
        result = client.refresh_all_browser_sources()

        if result['success']:
            names = ', '.join(result['refreshed'])
            messages.success(request, f"OBS: {result['total']} browser sources refrescados ({names})")
        else:
            messages.error(request, f"OBS Error: {result['error']}")

        return redirect('..')

    def toggle_debug_view(self, request):
        config, created = Config.objects.get_or_create(
            meta_key='overlays_debug',
            defaults={'meta_value': '0'}
        )
        # Toggle
        new_value = '0' if config.meta_value == '1' else '1'
        config.meta_value = new_value
        config.save()

        state = 'ACTIVADO' if new_value == '1' else 'DESACTIVADO'
        messages.success(request, f"Modo debug overlays: {state}")

        # Refrescar OBS para que tome el cambio
        from apps.integrations.obs.client import OBSClient
        client = OBSClient()
        result = client.refresh_all_browser_sources()
        if result['success']:
            messages.info(request, f"OBS refrescado ({result['total']} fuentes)")
        else:
            messages.warning(request, f"No se pudo refrescar OBS: {result.get('error', '')}")

        return redirect('..')

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
