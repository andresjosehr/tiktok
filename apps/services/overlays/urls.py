from django.urls import path
from . import views

app_name = 'overlays'

urlpatterns = [
    path('', views.overlay_view, name='overlay'),
    path('events/', views.overlay_events, name='events'),
]
