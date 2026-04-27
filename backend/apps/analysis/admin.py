"""Analysis admin configuration."""

from django.contrib import admin

from .models import CareRecommendation, CropPrice, CropRecommendation, SoilAnalysis


@admin.register(SoilAnalysis)
class SoilAnalysisAdmin(admin.ModelAdmin):
    """Toprak analizi admin."""

    list_display = ('field', 'nitrogen', 'phosphorus', 'potassium', 'ph', 'source', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('field__name',)


@admin.register(CropRecommendation)
class CropRecommendationAdmin(admin.ModelAdmin):
    """Ürün önerisi admin."""

    list_display = ('analysis', 'crop_name_tr', 'confidence', 'estimated_yield_kg', 'estimated_revenue_tl', 'rank')
    list_filter = ('crop_name',)


@admin.register(CareRecommendation)
class CareRecommendationAdmin(admin.ModelAdmin):
    """Bakım tavsiyesi admin."""

    list_display = ('field', 'recommendation_type', 'priority', 'is_done', 'created_at')
    list_filter = ('recommendation_type', 'priority', 'is_done')
    list_editable = ('is_done',)


@admin.register(CropPrice)
class CropPriceAdmin(admin.ModelAdmin):
    """Ürün fiyatları admin."""

    list_display = ('crop_name_tr', 'crop_name', 'price_per_kg', 'avg_yield_per_hectare', 'updated_at')
    list_editable = ('price_per_kg',)
    search_fields = ('crop_name', 'crop_name_tr')
