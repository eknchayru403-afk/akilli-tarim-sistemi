"""
Pytest fixture'ları — JWT Auth güvenlik testleri.

Test kullanıcıları (farmer/admin/agronomist), JWT token'ları
ve authenticated API client helper'ları sağlar.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ---------------------------------------------------------------------------
# Test Kullanıcıları
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    """DRF APIClient instance'ı."""
    return APIClient()


@pytest.fixture
def farmer_user(db):
    """Çiftçi rolünde test kullanıcısı."""
    return User.objects.create_user(
        username='test_farmer',
        email='farmer@test.com',
        password='TestSifre123!',
        first_name='Ahmet',
        last_name='Yılmaz',
        role='farmer',
        city='Konya',
        phone='+905551234567',
        is_verified=True,
    )


@pytest.fixture
def admin_user(db):
    """Yönetici rolünde test kullanıcısı."""
    return User.objects.create_user(
        username='test_admin',
        email='admin@test.com',
        password='AdminSifre123!',
        first_name='Yönetici',
        last_name='Kullanıcı',
        role='admin',
        is_staff=True,
        is_verified=True,
    )


@pytest.fixture
def agronomist_user(db):
    """Agronomist rolünde test kullanıcısı."""
    return User.objects.create_user(
        username='test_agronomist',
        email='agro@test.com',
        password='AgroSifre123!',
        first_name='Tarım',
        last_name='Uzmanı',
        role='agronomist',
        is_verified=True,
    )


@pytest.fixture
def unverified_user(db):
    """E-posta doğrulanmamış test kullanıcısı."""
    return User.objects.create_user(
        username='test_unverified',
        email='unverified@test.com',
        password='UnverifiedSifre123!',
        role='farmer',
        is_verified=False,
    )


# ---------------------------------------------------------------------------
# JWT Token'ları
# ---------------------------------------------------------------------------

@pytest.fixture
def farmer_tokens(farmer_user):
    """Farmer kullanıcısı için access ve refresh token çifti."""
    refresh = RefreshToken.for_user(farmer_user)
    refresh['role'] = farmer_user.role
    refresh['username'] = farmer_user.username
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@pytest.fixture
def admin_tokens(admin_user):
    """Admin kullanıcısı için access ve refresh token çifti."""
    refresh = RefreshToken.for_user(admin_user)
    refresh['role'] = admin_user.role
    refresh['username'] = admin_user.username
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@pytest.fixture
def agronomist_tokens(agronomist_user):
    """Agronomist kullanıcısı için access ve refresh token çifti."""
    refresh = RefreshToken.for_user(agronomist_user)
    refresh['role'] = agronomist_user.role
    refresh['username'] = agronomist_user.username
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


# ---------------------------------------------------------------------------
# Authenticated Client Helper'ları
# ---------------------------------------------------------------------------

@pytest.fixture
def farmer_client(api_client, farmer_tokens):
    """Farmer olarak authenticate edilmiş API client."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer_tokens['access']}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_tokens):
    """Admin olarak authenticate edilmiş API client."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_tokens['access']}")
    return api_client


@pytest.fixture
def agronomist_client(api_client, agronomist_tokens):
    """Agronomist olarak authenticate edilmiş API client."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {agronomist_tokens['access']}")
    return api_client
