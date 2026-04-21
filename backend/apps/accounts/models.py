"""
CustomUser modeli — Django AbstractUser extend.

Kullanıcı yönetimi için temel model.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Sistem kullanıcısı. Django AbstractUser üzerine ek alanlar."""

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Şehir',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefon',
    )

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        ordering = ['-date_joined']

    def __str__(self) -> str:
        """Kullanıcı tam adı veya username döndürür."""
        full_name = self.get_full_name()
        return full_name if full_name else self.username
