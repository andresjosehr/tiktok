from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_llm, name='llm_test'),
    path('send/', views.send_message, name='llm_send'),
]
