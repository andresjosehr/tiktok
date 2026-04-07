from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='analytics-dashboard'),
    path('api/session/<int:session_id>/', views.session_detail_api, name='analytics-session-detail'),
    path('api/compare/', views.compare_sessions_api, name='analytics-compare'),
]
