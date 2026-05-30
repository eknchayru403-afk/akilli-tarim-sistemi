"""Reports URL patterns."""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index, name='index'),
    path('download/', views.download_report, name='download'),
    path('preview/', views.report_preview, name='preview'),
    path('pdf/', views.download_report, name='download_pdf'),  # legacy support
    path('excel/', views.download_report, name='download_excel'),  # legacy support
]
