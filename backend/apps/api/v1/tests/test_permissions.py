"""
Rol Bazlı Yetkilendirme (Permission) Testleri.

IsFarmer, IsAdminRole, IsAgronomist, IsOwner ve IsVerifiedUser
permission sınıflarının fonksiyonel testleri.

Çalıştır:
    pytest apps/api/v1/tests/test_permissions.py -v
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

pytestmark = pytest.mark.django_db

# URL'leri string olarak tanımla
USER_LIST_URL = '/api/v1/auth/users/'


def user_detail_url(pk):
    return f'/api/v1/auth/users/{pk}/'


# ---------------------------------------------------------------------------
# Admin Rol Testleri
# ---------------------------------------------------------------------------

class TestAdminRoleAccess:
    """Admin-only endpoint'lere erişim testleri."""

    def test_admin_can_list_users(self, admin_client):
        """Admin kullanıcı listesine erişebilir → 200."""
        response = admin_client.get(USER_LIST_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_farmer_cannot_list_users(self, farmer_client):
        """Farmer kullanıcı listesine erişemez → 403."""
        response = farmer_client.get(USER_LIST_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agronomist_cannot_list_users(self, agronomist_client):
        """Agronomist kullanıcı listesine erişemez → 403."""
        response = agronomist_client.get(USER_LIST_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_list_users(self, api_client):
        """Yetkisiz erişim → 401."""
        response = api_client.get(USER_LIST_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_staff_user_can_list_users(self, db, api_client):
        """is_staff=True olan kullanıcı (admin rolü olmasa da) erişebilir."""
        staff_user = User.objects.create_user(
            username='staff_only',
            email='staff@test.com',
            password='StaffSifre123!',
            role='farmer',
            is_staff=True,
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(staff_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")

        response = api_client.get(USER_LIST_URL)
        assert response.status_code == status.HTTP_200_OK


class TestAdminUserDetail:
    """Admin kullanıcı detay endpoint'i testleri."""

    def test_admin_can_view_user_detail(self, admin_client, farmer_user):
        """Admin başka bir kullanıcının detayını görebilir → 200."""
        response = admin_client.get(user_detail_url(farmer_user.pk))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == farmer_user.username

    def test_admin_can_update_user_role(self, admin_client, farmer_user):
        """Admin kullanıcı rolünü değiştirebilir."""
        response = admin_client.patch(
            user_detail_url(farmer_user.pk),
            {'role': 'agronomist'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

        farmer_user.refresh_from_db()
        assert farmer_user.role == 'agronomist'

    def test_admin_can_deactivate_user(self, admin_client, farmer_user):
        """Admin kullanıcıyı devre dışı bırakabilir."""
        response = admin_client.patch(
            user_detail_url(farmer_user.pk),
            {'is_active': False},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

        farmer_user.refresh_from_db()
        assert farmer_user.is_active is False

    def test_farmer_cannot_view_other_user(self, farmer_client, admin_user):
        """Farmer başka kullanıcının detayını göremez → 403."""
        response = farmer_client.get(user_detail_url(admin_user.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Admin Kullanıcı Listesi Filtreleri
# ---------------------------------------------------------------------------

class TestAdminUserListFilters:
    """Admin kullanıcı listesi filtre testleri."""

    def test_filter_by_role(self, admin_client, farmer_user, agronomist_user):
        """Rol filtresi çalışıyor."""
        response = admin_client.get(f"{USER_LIST_URL}?role=farmer")
        assert response.status_code == status.HTTP_200_OK
        usernames = [u['username'] for u in response.data['results']]
        assert farmer_user.username in usernames
        assert agronomist_user.username not in usernames

    def test_filter_by_active_status(self, admin_client, farmer_user):
        """Aktiflik filtresi çalışıyor."""
        response = admin_client.get(f"{USER_LIST_URL}?is_active=true")
        assert response.status_code == status.HTTP_200_OK
        # Tüm test kullanıcıları aktif
        for user_data in response.data['results']:
            assert user_data['is_active'] is True

    def test_search_by_username(self, admin_client, farmer_user):
        """Username arama filtresi çalışıyor."""
        response = admin_client.get(f"{USER_LIST_URL}?search=test_farmer")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


# ---------------------------------------------------------------------------
# Permission Sınıfları — Birim Testleri
# ---------------------------------------------------------------------------

class TestPermissionClasses:
    """Permission sınıflarının doğrudan testleri."""

    def test_is_farmer_permission(self, farmer_user, admin_user):
        """IsFarmer: farmer True, admin False."""
        from apps.api.v1.permissions import IsFarmer

        perm = IsFarmer()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        assert perm.has_permission(MockRequest(farmer_user), None) is True
        assert perm.has_permission(MockRequest(admin_user), None) is False

    def test_is_admin_role_permission(self, admin_user, farmer_user):
        """IsAdminRole: admin True, farmer False."""
        from apps.api.v1.permissions import IsAdminRole

        perm = IsAdminRole()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        assert perm.has_permission(MockRequest(admin_user), None) is True
        assert perm.has_permission(MockRequest(farmer_user), None) is False

    def test_is_agronomist_permission(self, agronomist_user, farmer_user):
        """IsAgronomist: agronomist True, farmer False."""
        from apps.api.v1.permissions import IsAgronomist

        perm = IsAgronomist()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        assert perm.has_permission(MockRequest(agronomist_user), None) is True
        assert perm.has_permission(MockRequest(farmer_user), None) is False

    def test_is_verified_user_permission(self, farmer_user, unverified_user):
        """IsVerifiedUser: doğrulanmış True, doğrulanmamış False."""
        from apps.api.v1.permissions import IsVerifiedUser

        perm = IsVerifiedUser()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        assert perm.has_permission(MockRequest(farmer_user), None) is True
        assert perm.has_permission(MockRequest(unverified_user), None) is False

    def test_is_farmer_or_admin_permission(self, farmer_user, admin_user, agronomist_user):
        """IsFarmerOrAdmin: farmer/admin True, agronomist False."""
        from apps.api.v1.permissions import IsFarmerOrAdmin

        perm = IsFarmerOrAdmin()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        assert perm.has_permission(MockRequest(farmer_user), None) is True
        assert perm.has_permission(MockRequest(admin_user), None) is True
        assert perm.has_permission(MockRequest(agronomist_user), None) is False
