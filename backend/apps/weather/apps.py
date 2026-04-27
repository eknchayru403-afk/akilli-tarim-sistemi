"""Weather app configuration."""

from django.apps import AppConfig


class WeatherConfig(AppConfig):
    """Hava durumu uygulaması (v1: statik veri)."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.weather'
    verbose_name = 'Hava Durumu'
