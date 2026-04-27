"""Fields URL patterns."""

from django.urls import path

from . import views

app_name = 'fields'

urlpatterns = [
    path('', views.field_list, name='list'),
    path('create/', views.field_create, name='create'),
    path('<int:pk>/', views.field_detail, name='detail'),
    path('<int:pk>/edit/', views.field_update, name='update'),
    path('<int:pk>/delete/', views.field_delete, name='delete'),
]
