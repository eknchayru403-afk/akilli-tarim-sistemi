"""
Güvenlik Testleri — HTTPS, Token Güvenliği, Header'lar.

HTTPS zorunluluk middleware'i, süresi dolmuş/manipüle edilmiş token'lar,
blacklisted token erişimi ve güvenlik header'ları testleri.

Çalıştır:
    pytest apps/api/v1/tests/test_security.py -v
"""

import time
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# HTTPS Zorunluluk Testleri
# ---------------------------------------------------------------------------

class TestHTTPSEnforcement:
    """RequireHTTPSMiddleware testleri."""

    LOGIN_URL = reverse('auth_login')
    ME_URL = reverse('auth_me')

    @override_settings(DEBUG=False)
    def test_http_request_rejected_in_production(self, api_client, farmer_user):
        """Production'da HTTP isteği reddedilir → 403."""
        payload = {
            'username': 'test_farmer',
            'password': 'TestSifre123!',
        }
        # APIClient varsayılan olarak HTTP kullanır
        response = api_client.post(self.LOGIN_URL, payload, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['code'] == 'https_required'

    @override_settings(DEBUG=False)
    def test_https_request_accepted_in_production(self, farmer_user):
        """Production'da HTTPS isteği kabul edilir → 200."""
        client = APIClient()
        payload = {
            'username': 'test_farmer',
            'password': 'TestSifre123!',
        }
        # HTTPS simülasyonu
        response = client.post(
            self.LOGIN_URL, payload, format='json',
            **{'wsgi.url_scheme': 'https'},
        )
        assert response.status_code == status.HTTP_200_OK

    @override_settings(DEBUG=False)
    def test_proxy_forwarded_https_accepted(self, farmer_user):
        """Proxy arkasında X-Forwarded-Proto: https kabul edilir."""
        client = APIClient()
        payload = {
            'username': 'test_farmer',
            'password': 'TestSifre123!',
        }
        response = client.post(
            self.LOGIN_URL, payload, format='json',
            HTTP_X_FORWARDED_PROTO='https',
        )
        assert response.status_code == status.HTTP_200_OK

    @override_settings(DEBUG=True)
    def test_http_allowed_in_debug_mode(self, api_client, farmer_user):
        """DEBUG=True iken HTTP istekler kabul edilir."""
        payload = {
            'username': 'test_farmer',
            'password': 'TestSifre123!',
        }
        response = api_client.post(self.LOGIN_URL, payload, format='json')
        # DEBUG modda HTTPS kontrolü yapılmaz
        assert response.status_code != status.HTTP_403_FORBIDDEN

    @override_settings(DEBUG=False)
    def test_non_api_path_not_affected(self):
        """API dışı path'ler HTTPS zorunluluğundan etkilenmez."""
        client = APIClient()
        # /admin/ gibi bir path (var olmayabilir ama 403 değil)
        response = client.get('/accounts/login/')
        # 200 veya 302 beklenir — 403 (HTTPS) olmamalı
        assert response.status_code != status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Token Güvenliği Testleri
# ---------------------------------------------------------------------------

class TestTokenSecurity:
    """Token manipülasyonu ve süresi dolmuş token testleri."""

    ME_URL = reverse('auth_me')

    def test_invalid_token_rejected(self, api_client):
        """Manipüle edilmiş token reddedilir → 401."""
        api_client.credentials(
            HTTP_AUTHORIZATION='Bearer invalid.token.string'
        )
        response = api_client.get(self.ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_tampered_token_rejected(self, api_client, farmer_tokens):
        """Token'ın son karakteri değiştirildiğinde reddedilir → 401."""
        tampered = farmer_tokens['access'][:-1] + ('A' if farmer_tokens['access'][-1] != 'A' else 'B')
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tampered}'
        )
        response = api_client.get(self.ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(
        SIMPLE_JWT={
            'ACCESS_TOKEN_LIFETIME': timedelta(seconds=1),
            'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
            'ROTATE_REFRESH_TOKENS': True,
            'BLACKLIST_AFTER_ROTATION': True,
            'UPDATE_LAST_LOGIN': True,
            'ALGORITHM': 'HS256',
            'AUTH_HEADER_TYPES': ('Bearer',),
            'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
            'TOKEN_TYPE_CLAIM': 'token_type',
            'TOKEN_OBTAIN_SERIALIZER': 'apps.accounts.token_serializers.CustomTokenObtainPairSerializer',
        }
    )
    def test_expired_token_rejected(self, db):
        """Süresi dolmuş access token reddedilir → 401."""
        user = User.objects.create_user(
            username='expire_test',
            email='expire@test.com',
            password='ExpireSifre123!',
            role='farmer',
        )
        refresh = RefreshToken.for_user(user)
        expired_access = str(refresh.access_token)

        # Token süresinin dolmasını bekle
        time.sleep(2)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_access}')
        response = client.get(self.ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_bearer_prefix_rejected(self, api_client, farmer_tokens):
        """Bearer prefix'i olmadan token gönderildiğinde → 401."""
        api_client.credentials(
            HTTP_AUTHORIZATION=farmer_tokens['access']
        )
        response = api_client.get(self.ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_authorization_header(self, api_client):
        """Boş Authorization header → 401."""
        api_client.credentials(HTTP_AUTHORIZATION='')
        response = api_client.get(self.ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenBlacklist:
    """Token blacklist mekanizması testleri."""

    ME_URL = reverse('auth_me')
    REFRESH_URL = reverse('auth_refresh')

    def test_blacklisted_refresh_cannot_get_access(self, api_client, farmer_tokens):
        """Blacklisted refresh token ile yeni access alınamaz."""
        # Refresh token'ı blacklist'e al
        token = RefreshToken(farmer_tokens['refresh'])
        token.blacklist()

        # Blacklisted token ile refresh dene
        response = api_client.post(
            self.REFRESH_URL,
            {'refresh': farmer_tokens['refresh']},
            format='json',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_token_still_works_until_expiry(self, farmer_client, farmer_tokens):
        """
        Refresh blacklisted olsa da mevcut access token süresi
        dolana kadar çalışmaya devam eder (JWT doğal davranışı).
        """
        # Refresh token'ı blacklist'e al
        token = RefreshToken(farmer_tokens['refresh'])
        token.blacklist()

        # Mevcut access token hala geçerli
        response = farmer_client.get(self.ME_URL)
        assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# Güvenlik Header'ları Testleri
# ---------------------------------------------------------------------------

class TestSecurityHeaders:
    """HTTP güvenlik header'ları testleri."""

    def test_x_frame_options_deny(self, farmer_client):
        """X-Frame-Options: DENY header'ı mevcut olmalı."""
        response = farmer_client.get(reverse('auth_me'))
        assert response.get('X-Frame-Options') == 'DENY'

    def test_x_content_type_nosniff(self, farmer_client):
        """X-Content-Type-Options: nosniff header'ı mevcut olmalı."""
        response = farmer_client.get(reverse('auth_me'))
        assert response.get('X-Content-Type-Options') == 'nosniff'

    def test_content_type_is_json(self, farmer_client):
        """API yanıtları application/json formatında olmalı."""
        response = farmer_client.get(reverse('auth_me'))
        assert 'application/json' in response.get('Content-Type', '')


# ---------------------------------------------------------------------------
# Inactive User Testleri
# ---------------------------------------------------------------------------

class TestInactiveUser:
    """Devre dışı bırakılmış kullanıcı erişim testleri."""

    LOGIN_URL = reverse('auth_login')

    def test_inactive_user_cannot_login(self, db, api_client):
        """is_active=False olan kullanıcı giriş yapamaz → 401."""
        user = User.objects.create_user(
            username='inactive_user',
            email='inactive@test.com',
            password='InactiveSifre123!',
            role='farmer',
            is_active=False,
        )
        payload = {
            'username': 'inactive_user',
            'password': 'InactiveSifre123!',
        }
        response = api_client.post(self.LOGIN_URL, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
