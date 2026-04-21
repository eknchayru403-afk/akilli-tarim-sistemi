"""Analysis URL patterns."""

from django.urls import path

from . import views

app_name = 'analysis'

urlpatterns = [
    path('<int:field_pk>/analyze/', views.analyze_form, name='analyze'),
    path('<int:field_pk>/simulate/', views.simulate_data, name='simulate'),
    path('<int:pk>/result/', views.analysis_result, name='result'),
    path('history/', views.analysis_history, name='history'),
    path('<int:analysis_pk>/plant/<int:rec_pk>/', views.plant_crop, name='plant'),
]
