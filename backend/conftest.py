"""
Root-level pytest configuration.

Django settings modülünü ayarlar ve ortak fixture'ları sağlar.
"""

import django
from django.conf import settings

# Django settings ayarla — pytest-django otomatik yapar ama
# erken import durumları için burada da belirtiyoruz.


def pytest_configure(config):
    """pytest başlatılırken Django settings'i ayarla."""
    settings.DJANGO_SETTINGS_MODULE = 'config.settings'
