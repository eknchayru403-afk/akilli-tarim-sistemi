"""Fields admin configuration."""

from django.contrib import admin

from .models import Field


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    """Tarla admin paneli konfigürasyonu."""

    list_display = ('name', 'user', 'location', 'area_decar', 'soil_type', 'status', 'current_crop')
    list_filter = ('status', 'soil_type')
    search_fields = ('name', 'location', 'user__username')
    list_editable = ('status',)
