"""
Auth API Endpoint Testleri.

Register, Login, Token Refresh, Logout, Me (profil) ve
Change Password endpoint'lerinin tam kapsamlı fonksiyonel testleri.

Çalıştır:
    pytest apps/api/v1/tests/test_auth_api.py -v
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

pytestmark = pytest.mark.django_db

# URL'leri string olarak tanımla (reverse() import-time'da çözümlenmez)
REGISTER_URL = '/api/v1/auth/register/'
LOGIN_URL = '/api/v1/auth/login/'
REFRESH_URL = '/api/v1/auth/refresh/'
LOGOUT_URL = '/api/v1/auth/logout/'
ME_URL = '/api/v1/auth/me/'
CHANGE_PASSWORD_URL = '/api/v1/auth/change-password/'


# ---------------------------------------------------------------------------
# Kayıt (Register)
# ---------------------------------------------------------------------------

class TestRegister:
    """POST /api/v1/auth/register/ testleri."""

    def test_register_success(self, api_client):
        """Geçerli bilgilerle başarılı kayıt → 201 + token çifti."""
        payload = {
            'username': 'yeni_ciftci',
            'email': 'yeni@test.com',
            'password': 'GucluSifre123!',
            'password_confirm': 'GucluSifre123!',
            'first_name': 'Yeni',
            'last_name': 'Çiftçi',
            'city': 'Ankara',
            'phone': '+905559876543',
            'role': 'farmer',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'yeni_ciftci'
        assert response.data['user']['role'] == 'farmer'

        # DB'de kullanıcının oluşturulduğunu doğrula
        assert User.objects.filter(username='yeni_ciftci').exists()

    def test_register_password_mismatch(self, api_client):
        """Şifre eşleşmezse → 400."""
        payload = {
            'username': 'fail_user',
            'email': 'fail@test.com',
            'password': 'Sifre123!',
            'password_confirm': 'FarkliSifre123!',
            'role': 'farmer',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_register_duplicate_email(self, api_client, farmer_user):
        """Aynı e-posta ile ikinci kayıt → 400."""
        payload = {
            'username': 'baska_user',
            'email': farmer_user.email,  # Mevcut e-posta
            'password': 'GucluSifre123!',
            'password_confirm': 'GucluSifre123!',
            'role': 'farmer',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_duplicate_username(self, api_client, farmer_user):
        """Aynı username ile ikinci kayıt → 400."""
        payload = {
            'username': farmer_user.username,
            'email': 'unique@test.com',
            'password': 'GucluSifre123!',
            'password_confirm': 'GucluSifre123!',
            'role': 'farmer',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_admin_role_blocked(self, api_client):
        """API üzerinden admin rolü alamaz → 400."""
        payload = {
            'username': 'hacker',
            'email': 'hacker@test.com',
            'password': 'GucluSifre123!',
            'password_confirm': 'GucluSifre123!',
            'role': 'admin',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data

    def test_register_weak_password(self, api_client):
        """Zayıf şifre → 400 (Django password validators)."""
        payload = {
            'username': 'weak_pass',
            'email': 'weak@test.com',
            'password': '123',
            'password_confirm': '123',
            'role': 'farmer',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_agronomist_role_allowed(self, api_client):
        """Agronomist rolü API üzerinden alınabilir."""
        payload = {
            'username': 'uzman_tarim',
            'email': 'uzman@test.com',
            'password': 'GucluSifre123!',
            'password_confirm': 'GucluSifre123!',
            'role': 'agronomist',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['role'] == 'agronomist'


# ---------------------------------------------------------------------------
# Giriş (Login)
# ---------------------------------------------------------------------------

class TestLogin:
    """POST /api/v1/auth/login/ testleri."""

    def test_login_success(self, api_client, farmer_user):
        """Geçerli credentials → 200 + access/refresh + user bilgisi."""
        payload = {
            'username': 'test_farmer',
            'password': 'TestSifre123!',
        }
        response = api_client.post(LOGIN_URL, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['role'] == 'farmer'
        assert response.data['user']['username'] == 'test_farmer'

    def test_login_wrong_password(self, api_client, farmer_user):
        """Hatalı şifre → 401."""
        payload = {
            'username': 'test_farmer',
            'password': 'YanlısSifre!',
        }
        response = api_client.post(LOGIN_URL, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        """Var olmayan kullanıcı → 401."""
        payload = {
            'username': 'ghost_user',
            'password': 'HerhangiBirSifre!',
        }
        response = api_client.post(LOGIN_URL, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_updates_last_login_ip(self, api_client, farmer_user):
        """Başarılı giriş last_login_ip'yi günceller."""
        payload = {
            'username': 'test_farmer',
            'password': 'TestSifre123!',
        }
        api_client.post(LOGIN_URL, payload, format='json')
        farmer_user.refresh_from_db()
        assert farmer_user.last_login_ip is not None

    def test_login_token_contains_custom_claims(self, api_client, farmer_user):
        """Token payload'ında özel claim'ler mevcut olmalı."""
        import jwt
        from django.conf import settings as django_settings

        payload = {
            'username': 'test_farmer',
            'password': 'TestSifre123!',
        }
        response = api_client.post(LOGIN_URL, payload, format='json')
        access_token = response.data['access']

        # Token decode et (doğrulama olmadan, claim kontrolü için)
        decoded = jwt.decode(
            access_token,
            django_settings.SECRET_KEY,
            algorithms=['HS256'],
        )

        assert decoded['role'] == 'farmer'
        assert decoded['username'] == 'test_farmer'
        assert 'full_name' in decoded
        assert 'is_verified' in decoded
        assert 'email' in decoded

    def test_login_admin_role_in_token(self, api_client, admin_user):
        """Admin girişinde token'da role=admin olmalı."""
        payload = {
            'username': 'test_admin',
            'password': 'AdminSifre123!',
        }
        response = api_client.post(LOGIN_URL, payload, format='json')
        assert response.data['user']['role'] == 'admin'


# ---------------------------------------------------------------------------
# Token Yenileme (Refresh)
# ---------------------------------------------------------------------------

class TestTokenRefresh:
    """POST /api/v1/auth/refresh/ testleri."""

    def test_refresh_success(self, api_client, farmer_tokens):
        """Geçerli refresh token ile yeni access token → 200."""
        payload = {'refresh': farmer_tokens['refresh']}
        response = api_client.post(REFRESH_URL, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_refresh_invalid_token(self, api_client):
        """Geçersiz refresh token → 401."""
        payload = {'refresh': 'invalid.token.value'}
        response = api_client.post(REFRESH_URL, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_missing_token(self, api_client):
        """Eksik refresh token → 400."""
        response = api_client.post(REFRESH_URL, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_after_blacklist(self, api_client, farmer_tokens):
        """Blacklist'e alınmış refresh token ile yenileme → 401."""
        from rest_framework_simplejwt.tokens import RefreshToken

        # Token'ı blacklist'e al
        token = RefreshToken(farmer_tokens['refresh'])
        token.blacklist()

        # Blacklisted token ile refresh dene
        payload = {'refresh': farmer_tokens['refresh']}
        response = api_client.post(REFRESH_URL, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Çıkış (Logout)
# ---------------------------------------------------------------------------

class TestLogout:
    """POST /api/v1/auth/logout/ testleri."""

    def test_logout_success(self, farmer_client, farmer_tokens):
        """Geçerli refresh token ile başarılı çıkış → 200."""
        payload = {'refresh': farmer_tokens['refresh']}
        response = farmer_client.post(LOGOUT_URL, payload, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_logout_double_logout(self, farmer_client, farmer_tokens):
        """Aynı token ile tekrar logout → 400 (zaten blacklisted)."""
        payload = {'refresh': farmer_tokens['refresh']}
        farmer_client.post(LOGOUT_URL, payload, format='json')

        # İkinci logout denemesi
        response = farmer_client.post(LOGOUT_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_missing_refresh(self, farmer_client):
        """Refresh token gönderilmezse → 400."""
        response = farmer_client.post(LOGOUT_URL, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self, api_client):
        """Yetkisiz kullanıcı logout yapamaz → 401."""
        response = api_client.post(LOGOUT_URL, {'refresh': 'dummy'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Profil (Me)
# ---------------------------------------------------------------------------

class TestMe:
    """GET/PATCH /api/v1/auth/me/ testleri."""

    def test_me_authenticated(self, farmer_client, farmer_user):
        """Authenticate edilmiş kullanıcı profilini görüntüler → 200."""
        response = farmer_client.get(ME_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == farmer_user.username
        assert response.data['role'] == 'farmer'
        assert response.data['email'] == farmer_user.email

    def test_me_unauthenticated(self, api_client):
        """Yetkisiz erişim → 401."""
        response = api_client.get(ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_update_profile(self, farmer_client, farmer_user):
        """Profil bilgilerini güncelleme → 200."""
        payload = {
            'first_name': 'Güncellenen',
            'city': 'İstanbul',
        }
        response = farmer_client.patch(ME_URL, payload, format='json')
        assert response.status_code == status.HTTP_200_OK

        farmer_user.refresh_from_db()
        assert farmer_user.first_name == 'Güncellenen'
        assert farmer_user.city == 'İstanbul'

    def test_me_cannot_change_role(self, farmer_client):
        """Kullanıcı kendi rolünü değiştiremez (read_only)."""
        payload = {'role': 'admin'}
        response = farmer_client.patch(ME_URL, payload, format='json')

        # Role read_only olduğu için güncellenmemeli
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == 'farmer'

    def test_me_cannot_change_username(self, farmer_client):
        """Kullanıcı username'ini değiştiremez (read_only)."""
        payload = {'username': 'hacked_username'}
        farmer_client.patch(ME_URL, payload, format='json')
        # username read_only — değişmemeli
        response = farmer_client.get(ME_URL)
        assert response.data['username'] == 'test_farmer'


# ---------------------------------------------------------------------------
# Şifre Değiştirme (Change Password)
# ---------------------------------------------------------------------------

class TestChangePassword:
    """POST /api/v1/auth/change-password/ testleri."""

    def test_change_password_success(self, farmer_client, farmer_user):
        """Geçerli eski şifre ile başarılı değişiklik → 200."""
        payload = {
            'old_password': 'TestSifre123!',
            'new_password': 'YeniGucluSifre456!',
            'new_password_confirm': 'YeniGucluSifre456!',
        }
        response = farmer_client.post(CHANGE_PASSWORD_URL, payload, format='json')
        assert response.status_code == status.HTTP_200_OK

        # Yeni şifre ile login
        farmer_user.refresh_from_db()
        assert farmer_user.check_password('YeniGucluSifre456!')

    def test_change_password_wrong_old(self, farmer_client):
        """Hatalı eski şifre → 400."""
        payload = {
            'old_password': 'YanlisSifre!',
            'new_password': 'YeniSifre123!',
            'new_password_confirm': 'YeniSifre123!',
        }
        response = farmer_client.post(CHANGE_PASSWORD_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatch(self, farmer_client):
        """Yeni şifreler eşleşmezse → 400."""
        payload = {
            'old_password': 'TestSifre123!',
            'new_password': 'YeniSifre123!',
            'new_password_confirm': 'FarkliSifre456!',
        }
        response = farmer_client.post(CHANGE_PASSWORD_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self, api_client):
        """Yetkisiz kullanıcı şifre değiştiremez → 401."""
        payload = {
            'old_password': 'any',
            'new_password': 'YeniSifre123!',
            'new_password_confirm': 'YeniSifre123!',
        }
        response = api_client.post(CHANGE_PASSWORD_URL, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
