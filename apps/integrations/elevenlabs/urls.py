from django.urls import path
from . import views

app_name = 'elevenlabs'

urlpatterns = [
    path('test/', views.test_tts_view, name='test_tts'),
]
