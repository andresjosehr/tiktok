from django.urls import path
from . import views

urlpatterns = [
    path('', views.player_page, name='audio_player'),
    path('current/', views.get_current_audio, name='get_current_audio'),
    path('events/', views.event_stream, name='audio_events'),
    path('stop/', views.stop_audio, name='stop_audio'),
]
