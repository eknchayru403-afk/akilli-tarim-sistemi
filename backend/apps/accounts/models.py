"""
CustomUser modeli — Django AbstractUser extend.

Kullanıcı yönetimi için temel model.
Rol tabanlı yetkilendirme (farmer/admin/agronomist) destekler.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Sistem kullanıcısı. Django AbstractUser üzerine ek alanlar."""

    # Kullanıcı rolleri
    ROLE_FARMER = 'farmer'
    ROLE_ADMIN = 'admin'
    ROLE_AGRONOMIST = 'agronomist'

    ROLE_CHOICES = [
        (ROLE_FARMER, 'Çiftçi'),
        (ROLE_ADMIN, 'Yönetici'),
        (ROLE_AGRONOMIST, 'Agronomist'),
    ]

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

    # Rol tabanlı yetkilendirme
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_FARMER,
        verbose_name='Rol',
        db_index=True,
    )

    # Hesap doğrulama durumu
    is_verified = models.BooleanField(
        default=False,
        verbose_name='E-posta Doğrulandı',
    )

    # Güvenlik loglaması
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Son Giriş IP',
    )

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        ordering = ['-date_joined']

    def __str__(self) -> str:
        """Kullanıcı tam adı veya username döndürür."""
        full_name = self.get_full_name()
        return full_name if full_name else self.username

    @property
    def is_farmer(self) -> bool:
        """Kullanıcı çiftçi rolüne sahipse True döner."""
        return self.role == self.ROLE_FARMER

    @property
    def is_admin_role(self) -> bool:
        """Kullanıcı yönetici rolüne sahipse True döner."""
        return self.role == self.ROLE_ADMIN or self.is_staff

    @property
    def is_agronomist(self) -> bool:
        """Kullanıcı agronomist rolüne sahipse True döner."""
        return self.role == self.ROLE_AGRONOMIST
