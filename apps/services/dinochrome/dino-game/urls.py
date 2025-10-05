from django.urls import path
from . import views

app_name = 'dinogame'

urlpatterns = [
    path('', views.game_view, name='game'),
]
