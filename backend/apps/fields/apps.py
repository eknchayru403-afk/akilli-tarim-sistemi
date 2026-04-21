"""Fields app configuration."""

from django.apps import AppConfig


class FieldsConfig(AppConfig):
    """Tarla yönetimi uygulaması."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fields'
    verbose_name = 'Tarla Yönetimi'
