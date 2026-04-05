from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_page, name='simulator_panel'),
    path('send/', views.send_event, name='simulator_send'),
    path('session/', views.session_status, name='simulator_session'),
    path('session/end/', views.end_session, name='simulator_end_session'),
]
