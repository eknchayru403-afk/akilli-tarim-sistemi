"""Reports app configuration."""

from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Tarımsal raporlama uygulaması."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reports'
    verbose_name = 'Raporlar'
