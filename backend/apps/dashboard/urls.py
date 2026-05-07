"""Dashboard URL patterns."""

from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('realtime/', views.realtime_dashboard, name='realtime'),
    path('api/realtime-data/', views.api_realtime_data, name='api_realtime_data'),
]
