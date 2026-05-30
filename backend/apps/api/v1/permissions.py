"""
API v1 İzinler (Permissions).

Kullanıcı sahipliği kontrolü ve rol tabanlı yetkilendirme.

Rol Hiyerarşisi:
  admin       → Tüm kaynaklara erişim (staff dahil)
  agronomist  → Kendi verileri + analiz sonuçlarını okuma
  farmer      → Sadece kendi tarlalarını ve verileri yönetir
"""

from rest_framework import permissions


# ---------------------------------------------------------------------------
# Sahiplik Tabanlı İzinler
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Rol Tabanlı İzinler
# ---------------------------------------------------------------------------

class IsFarmer(permissions.BasePermission):
    """
    Sadece çiftçi (farmer) rolüne sahip kullanıcılar.

    Kullanım: permission_classes = [IsAuthenticated, IsFarmer]
    """
    message = "Bu işlem için çiftçi rolüne sahip olmanız gerekir."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'farmer'
        )


class IsAdminRole(permissions.BasePermission):
    """
    Admin rolü veya Django staff yetkisi.

    is_staff=True olan kullanıcılar da bu izne sahiptir.
    Kullanım: permission_classes = [IsAuthenticated, IsAdminRole]
    """
    message = "Bu işlem için yönetici yetkisi gerekir."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin' or request.user.is_staff


class IsFarmerOrAdmin(permissions.BasePermission):
    """
    Çiftçi veya admin rolü.

    Genel API erişimi — agronomist hariç tümüne açık endpoint'ler için.
    """
    message = "Bu işlem için çiftçi veya yönetici rolü gerekir."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('farmer', 'admin') or request.user.is_staff


class IsAgronomist(permissions.BasePermission):
    """
    Sadece agronomist (tarım uzmanı) rolüne sahip kullanıcılar.

    Kullanım: permission_classes = [IsAuthenticated, IsAgronomist]
    """
    message = "Bu işlem için agronomist rolüne sahip olmanız gerekir."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'agronomist'
        )


class IsAgronomistOrAdmin(permissions.BasePermission):
    """Agronomist veya admin rolü (analiz sonuçlarına erişim için)."""
    message = "Bu işlem için agronomist veya yönetici rolü gerekir."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('agronomist', 'admin') or request.user.is_staff


class IsVerifiedUser(permissions.BasePermission):
    """
    Sadece e-posta doğrulaması tamamlanmış kullanıcılar.

    Hassas işlemler için ek güvenlik katmanı.
    """
    message = "Bu işlem için hesabınızı doğrulamanız gerekir."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_verified or request.user.is_staff)
        )
