from django.urls import path
from . import views

app_name = 'tugofwar'

urlpatterns = [
    path('', views.game_view, name='game'),
    path('events/', views.game_events, name='events'),
]
