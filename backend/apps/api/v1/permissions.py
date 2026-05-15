"""
API v1 İzinler (Permissions).

Kullanıcı sahipliği kontrolü.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Nesne sahibi tam erişim, diğerleri sadece okuma.

    Field modeli → user alanı
    SoilAnalysis → field.user alanı
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS isteklerine izin ver
        if request.method in permissions.SAFE_METHODS:
            return True

        # Sahiplik kontrolü
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'field'):
            return obj.field.user == request.user
        if hasattr(obj, 'analysis'):
            return obj.analysis.field.user == request.user

        return False


class IsOwner(permissions.BasePermission):
    """Sadece nesne sahibi erişebilir (okuma dahil)."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'field'):
            return obj.field.user == request.user
        if hasattr(obj, 'analysis'):
            return obj.analysis.field.user == request.user
        return False
