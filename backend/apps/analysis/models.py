"""
Analysis modelleri — Toprak analizi, ürün önerisi, bakım tavsiyesi, fiyat.

Bu modül analiz sürecinin tüm veri modellerini içerir.
"""

from django.db import models

from apps.fields.models import Field, TimeStampedModel


class SoilAnalysis(TimeStampedModel):
    """Toprak analizi verileri. Manuel giriş veya simülasyon kaynaklı."""

    SOURCE_CHOICES = [
        ('manual', 'Manuel Giriş'),
        ('simulation', 'Simülasyon'),
    ]

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='soil_analyses',
        verbose_name='Tarla',
    )
    nitrogen = models.DecimalField(
        max_digits=6, decimal_places=2,
        verbose_name='Azot (N)',
    )
    phosphorus = models.DecimalField(
        max_digits=6, decimal_places=2,
        verbose_name='Fosfor (P)',
    )
    potassium = models.DecimalField(
        max_digits=6, decimal_places=2,
        verbose_name='Potasyum (K)',
    )
    temperature = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Sıcaklık (°C)',
    )
    humidity = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Nem (%)',
    )
    ph = models.DecimalField(
        max_digits=4, decimal_places=2,
        verbose_name='pH',
    )
    rainfall = models.DecimalField(
        max_digits=6, decimal_places=2,
        verbose_name='Yağış (mm)',
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='manual',
        verbose_name='Kaynak',
    )

    class Meta:
        verbose_name = 'Toprak Analizi'
        verbose_name_plural = 'Toprak Analizleri'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', '-created_at'], name='idx_soil_field_created'),
        ]

    def __str__(self) -> str:
        """Tarla adı ve analiz tarihi döndürür."""
        return f"{self.field.name} — {self.created_at:%d.%m.%Y %H:%M}"


class CropRecommendation(TimeStampedModel):
    """ML modeli tarafından üretilen ürün önerisi."""

    analysis = models.ForeignKey(
        SoilAnalysis,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='Analiz',
    )
    crop_name = models.CharField(
        max_length=50,
        verbose_name='Ürün (EN)',
    )
    crop_name_tr = models.CharField(
        max_length=50,
        verbose_name='Ürün (TR)',
    )
    confidence = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Güven Skoru (%)',
    )
    estimated_yield_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name='Tahmini Verim (kg)',
    )
    estimated_revenue_tl = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name='Tahmini Kazanç (TL)',
    )
    rank = models.IntegerField(
        default=1,
        verbose_name='Sıralama',
    )

    class Meta:
        verbose_name = 'Ürün Önerisi'
        verbose_name_plural = 'Ürün Önerileri'
        ordering = ['rank']
        indexes = [
            models.Index(fields=['analysis', 'rank'], name='idx_rec_analysis_rank'),
        ]

    def __str__(self) -> str:
        """Ürün adı ve güven skoru döndürür."""
        return f"{self.crop_name_tr} (%{self.confidence})"


class CareRecommendation(TimeStampedModel):
    """Ekili tarlalar için bakım tavsiyesi (kural tabanlı)."""

    TYPE_CHOICES = [
        ('irrigation', 'Sulama'),
        ('fertilization', 'Gübreleme'),
        ('pesticide', 'İlaçlama'),
        ('soil_amendment', 'Toprak Düzenleme'),
        ('temperature', 'Sıcaklık Uyarısı'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('critical', 'Kritik'),
    ]

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='care_recommendations',
        verbose_name='Tarla',
    )
    recommendation_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name='Tavsiye Tipi',
    )
    message = models.TextField(
        verbose_name='Mesaj',
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Öncelik',
    )
    is_done = models.BooleanField(
        default=False,
        verbose_name='Tamamlandı',
    )

    class Meta:
        verbose_name = 'Bakım Tavsiyesi'
        verbose_name_plural = 'Bakım Tavsiyeleri'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', 'is_done', 'priority'], name='idx_care_field_done_prio'),
        ]

    def __str__(self) -> str:
        """Tavsiye tipi ve öncelik döndürür."""
        return f"{self.get_recommendation_type_display()} ({self.get_priority_display()})"


class CropPrice(models.Model):
    """Ürün fiyatları. Admin tarafından güncellenebilir."""

    crop_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Ürün (EN)',
    )
    crop_name_tr = models.CharField(
        max_length=50,
        verbose_name='Ürün (TR)',
    )
    price_per_kg = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name='Fiyat (TL/kg)',
    )
    avg_yield_per_hectare = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name='Ort. Verim (kg/ha)',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Güncellenme',
    )

    class Meta:
        verbose_name = 'Ürün Fiyatı'
        verbose_name_plural = 'Ürün Fiyatları'
        ordering = ['crop_name_tr']

    def __str__(self) -> str:
        """Ürün adı ve fiyat döndürür."""
        return f"{self.crop_name_tr} — {self.price_per_kg} TL/kg"
