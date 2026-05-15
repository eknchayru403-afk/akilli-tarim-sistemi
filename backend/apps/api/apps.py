"""API app configuration."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Django REST Framework API uygulaması."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    verbose_name = 'API'
