"""
Field (Tarla) modeli.

Kullanıcıların tarla bilgilerini yönetmek için kullanılır.
"""

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model — created_at ve updated_at alanları sağlar."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme')

    class Meta:
        abstract = True


class Field(TimeStampedModel):
    """Kullanıcıya ait tarla. Boş veya ekili durumda olabilir."""

    SOIL_TYPE_CHOICES = [
        ('killi', 'Killi'),
        ('kumlu', 'Kumlu'),
        ('tinli', 'Tınlı'),
        ('killi_tinli', 'Killi-Tınlı'),
        ('kumlu_tinli', 'Kumlu-Tınlı'),
        ('limolu', 'Limolu'),
    ]

    STATUS_CHOICES = [
        ('empty', 'Boş'),
        ('planted', 'Ekili'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fields',
        verbose_name='Kullanıcı',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Tarla Adı',
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Konum',
    )
    area_decar = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Alan (Dekar)',
    )
    soil_type = models.CharField(
        max_length=50,
        choices=SOIL_TYPE_CHOICES,
        default='tinli',
        verbose_name='Toprak Tipi',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='empty',
        verbose_name='Durum',
    )
    current_crop = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Mevcut Ürün',
    )

    class Meta:
        verbose_name = 'Tarla'
        verbose_name_plural = 'Tarlalar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_field_user_status'),
            models.Index(fields=['user', '-created_at'], name='idx_field_user_created'),
        ]

    def __str__(self) -> str:
        """Tarla adı ve durumunu döndürür."""
        return f"{self.name} ({self.get_status_display()})"

    @property
    def area_hectare(self) -> float:
        """Dekar cinsinden alanı hektara çevirir."""
        return float(self.area_decar) / 10
