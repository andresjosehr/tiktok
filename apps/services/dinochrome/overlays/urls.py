from django.urls import path
from . import views

app_name = 'dinochrome'

urlpatterns = [
    # Pagina unificada (juego + overlays + audio)
    path('', views.dinochrome_view, name='game'),

    # SSE endpoint unico
    path('events/', views.dinochrome_events, name='events'),

    # Cancion actual (para browsers que se conectan tarde)
    path('current-music/', views.dinochrome_current_music, name='current_music'),
]
