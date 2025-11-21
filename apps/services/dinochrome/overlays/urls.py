from django.urls import path
from . import views

app_name = 'dinochrome_overlays'

urlpatterns = [
    # Rosa overlay
    path('rose/', views.rose_overlay_view, name='rose'),

    # GIF overlays (slots 1-5)
    path('gif/<int:slot>/', views.gif_overlay_view, name='gif_slot'),

    # SSE endpoints
    path('events/<str:overlay_type>/', views.overlay_events, name='events'),
]
