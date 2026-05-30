"""
Rate Limiting (Throttle) Testleri.

Login, Register, Token Refresh ve Anonim rate limit kurallarının
fonksiyonel testleri. Cache temizlenerek izole test ortamı sağlanır.

Çalıştır:
    pytest apps/api/v1/tests/test_throttling.py -v
"""

import pytest
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

# URL'leri string olarak tanımla
LOGIN_URL = '/api/v1/auth/login/'
REGISTER_URL = '/api/v1/auth/register/'
REFRESH_URL = '/api/v1/auth/refresh/'
CHANGE_PASSWORD_URL = '/api/v1/auth/change-password/'

# ---------------------------------------------------------------------------
# Test için sıkıştırılmış throttle rate'leri
# ---------------------------------------------------------------------------
STRICT_THROTTLE_RATES = {
    'anon': '3/minute',
    'user': '100/minute',
    'auth_login': '3/minute',
    'auth_register': '2/minute',
    'token_refresh': '3/minute',
    'password_change': '2/minute',
}


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """Her test öncesi throttle cache'ini temizle."""
    cache.clear()
    yield
    cache.clear()


# ---------------------------------------------------------------------------
# Login Throttle
# ---------------------------------------------------------------------------

class TestLoginThrottle:
    """Login endpoint rate limiting testleri."""

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
            'DEFAULT_THROTTLE_CLASSES': [
                'rest_framework.throttling.AnonRateThrottle',
                'rest_framework.throttling.UserRateThrottle',
            ],
            'DEFAULT_THROTTLE_RATES': STRICT_THROTTLE_RATES,
        }
    )
    def test_login_throttle_after_limit(self, farmer_user):
        """Limit aşıldığında → 429 Too Many Requests."""
        client = APIClient()
        payload = {
            'username': 'test_farmer',
            'password': 'YanlisSifre!',
        }

        # İlk 3 deneme geçmeli (hatalı şifre → 401, throttle değil)
        for i in range(3):
            response = client.post(LOGIN_URL, payload, format='json')
            assert response.status_code in (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ), f"Deneme {i + 1}: Beklenmeyen status {response.status_code}"

        # 4. deneme throttle olmalı
        response = client.post(LOGIN_URL, payload, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ---------------------------------------------------------------------------
# Register Throttle
# ---------------------------------------------------------------------------

class TestRegisterThrottle:
    """Register endpoint rate limiting testleri."""

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
            'DEFAULT_THROTTLE_CLASSES': [
                'rest_framework.throttling.AnonRateThrottle',
                'rest_framework.throttling.UserRateThrottle',
            ],
            'DEFAULT_THROTTLE_RATES': STRICT_THROTTLE_RATES,
        }
    )
    def test_register_throttle_after_limit(self):
        """Limit aşıldığında kayıt reddedilir → 429."""
        client = APIClient()

        for i in range(3):
            payload = {
                'username': f'throttle_user_{i}',
                'email': f'throttle{i}@test.com',
                'password': 'GucluSifre123!',
                'password_confirm': 'GucluSifre123!',
                'role': 'farmer',
            }
            response = client.post(REGISTER_URL, payload, format='json')
            # İlk 2 deneme başarılı olabilir, sonra throttle
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        # Son deneme kesinlikle throttle
        payload = {
            'username': 'throttle_user_final',
            'email': 'throttle_final@test.com',
            'password': 'GucluSifre123!',
            'password_confirm': 'GucluSifre123!',
            'role': 'farmer',
        }
        response = client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ---------------------------------------------------------------------------
# Token Refresh Throttle
# ---------------------------------------------------------------------------

class TestTokenRefreshThrottle:
    """Token refresh endpoint rate limiting testleri."""

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
            'DEFAULT_THROTTLE_CLASSES': [
                'rest_framework.throttling.AnonRateThrottle',
                'rest_framework.throttling.UserRateThrottle',
            ],
            'DEFAULT_THROTTLE_RATES': STRICT_THROTTLE_RATES,
        }
    )
    def test_refresh_throttle_after_limit(self, farmer_user):
        """Token yenileme limiti aşıldığında → 429."""
        from rest_framework_simplejwt.tokens import RefreshToken

        client = APIClient()

        for i in range(4):
            # Her seferinde yeni token üret (ROTATE_REFRESH_TOKENS aktif)
            refresh = RefreshToken.for_user(farmer_user)
            payload = {'refresh': str(refresh)}
            response = client.post(REFRESH_URL, payload, format='json')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        # Son deneme throttle olmalı
        refresh = RefreshToken.for_user(farmer_user)
        payload = {'refresh': str(refresh)}
        response = client.post(REFRESH_URL, payload, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ---------------------------------------------------------------------------
# Password Change Throttle
# ---------------------------------------------------------------------------

class TestPasswordChangeThrottle:
    """Şifre değiştirme rate limiting testleri."""

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
            'DEFAULT_THROTTLE_CLASSES': [
                'rest_framework.throttling.AnonRateThrottle',
                'rest_framework.throttling.UserRateThrottle',
            ],
            'DEFAULT_THROTTLE_RATES': STRICT_THROTTLE_RATES,
        }
    )
    def test_password_change_throttle(self, farmer_client):
        """Şifre değiştirme limiti aşıldığında → 429."""
        payload = {
            'old_password': 'YanlisSifre!',
            'new_password': 'YeniSifre123!',
            'new_password_confirm': 'YeniSifre123!',
        }

        for i in range(3):
            response = farmer_client.post(CHANGE_PASSWORD_URL, payload, format='json')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        response = farmer_client.post(CHANGE_PASSWORD_URL, payload, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
