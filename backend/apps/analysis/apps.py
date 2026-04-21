"""Analysis app configuration."""

from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    """Toprak analizi ve ML önerileri uygulaması."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analysis'
    verbose_name = 'Toprak Analizi'
