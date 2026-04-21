"""
Accounts admin configuration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """CustomUser admin paneli konfigürasyonu."""

    list_display = ('username', 'email', 'first_name', 'last_name', 'city', 'is_active')
    list_filter = ('is_active', 'is_staff', 'city')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Ek Bilgiler', {
            'fields': ('city', 'phone'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ek Bilgiler', {
            'fields': ('city', 'phone'),
        }),
    )
