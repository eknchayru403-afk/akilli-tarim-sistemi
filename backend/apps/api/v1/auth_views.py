"""
Auth API View'ları — Kayıt, Giriş, Çıkış, Profil.

Mobil istemcilerin kullanıcı yönetimi için tüm endpoint'leri barındırır.

Endpoint'ler:
    POST /api/v1/auth/register/         → Yeni kullanıcı kaydı
    POST /api/v1/auth/login/            → JWT token al (özel claim'li)
    POST /api/v1/auth/refresh/          → Access token yenile
    POST /api/v1/auth/verify/           → Token geçerlilik doğrula
    POST /api/v1/auth/logout/           → Refresh token blacklist'e al
    GET  /api/v1/auth/me/               → Profil görüntüle
    PATCH /api/v1/auth/me/              → Profil güncelle
    POST /api/v1/auth/change-password/  → Şifre değiştir
    GET  /api/v1/auth/users/            → Kullanıcı listesi (sadece admin)
    GET  /api/v1/auth/users/{id}/       → Kullanıcı detayı (sadece admin)
"""

import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.token_serializers import CustomTokenObtainPairSerializer

from .auth_serializers import (
    ChangePasswordSerializer,
    UserAdminSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from .permissions import IsAdminRole
from .throttles import (
    LoginRateThrottle,
    PasswordChangeRateThrottle,
    RegisterRateThrottle,
    TokenRefreshRateThrottle,
)

User = get_user_model()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Kayıt
# ---------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    """
    Yeni kullanıcı kaydı.

    POST /api/v1/auth/register/

    Body:
    {
        "username": "ahmet_farmer",
        "email": "ahmet@example.com",
        "password": "Guclu1Sifre!",
        "password_confirm": "Guclu1Sifre!",
        "first_name": "Ahmet",
        "last_name": "Yılmaz",
        "city": "Konya",
        "phone": "+905551234567",
        "role": "farmer"
    }

    Yanıt (201):
    {
        "user": { ... },
        "access": "eyJ...",
        "refresh": "eyJ..."
    }
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Kayıt sonrası otomatik token üret
        refresh = RefreshToken.for_user(user)
        # Custom claim'leri ekle
        refresh['role'] = user.role
        refresh['username'] = user.username
        refresh['full_name'] = user.get_full_name() or user.username
        refresh['is_verified'] = user.is_verified

        return Response(
            {
                'message': 'Hesabınız başarıyla oluşturuldu.',
                'user': UserProfileSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Giriş — Custom Claim'li
# ---------------------------------------------------------------------------

class CustomLoginView(TokenObtainPairView):
    """
    JWT token alma (özel claim'li).

    POST /api/v1/auth/login/

    Body: { "username": "...", "password": "..." }

    Yanıt:
    {
        "access": "eyJ...",
        "refresh": "eyJ...",
        "user": {
            "id": 1,
            "username": "...",
            "role": "farmer",
            ...
        }
    }

    Token payload'ında: role, username, full_name, is_verified, email
    """

    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        # IP adresini logla
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # Başarılı girişte son IP'yi güncelle
            username = request.data.get('username', '')
            try:
                user = User.objects.get(username=username)
                ip = self._get_client_ip(request)
                user.last_login_ip = ip
                user.save(update_fields=['last_login_ip'])
            except User.DoesNotExist:
                pass

        return response

    def _get_client_ip(self, request) -> str:
        """İstemci IP adresini güvenli şekilde çıkar."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


# ---------------------------------------------------------------------------
# Token Yenileme
# ---------------------------------------------------------------------------

class CustomTokenRefreshView(TokenRefreshView):
    """
    Access token yenileme.

    POST /api/v1/auth/refresh/

    Body: { "refresh": "eyJ..." }
    Yanıt: { "access": "eyJ..." }
    """

    throttle_classes = [TokenRefreshRateThrottle]


# ---------------------------------------------------------------------------
# Çıkış — Blacklist
# ---------------------------------------------------------------------------

class LogoutView(APIView):
    """
    Kullanıcı çıkışı — Refresh token blacklist'e alınır.

    POST /api/v1/auth/logout/

    Body: { "refresh": "eyJ..." }

    Refresh token geçersiz kılındıktan sonra yeni access token
    alınamaz; mevcut (kısa ömürlü) access token süresi dolana dek
    teknik olarak geçerli kalır — bu JWT'nin doğal davranışıdır.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token gereklidir.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(
                "JWT: Kullanıcı çıkış yaptı — %s",
                request.user.username,
            )

            return Response(
                {'detail': 'Başarıyla çıkış yapıldı.'},
                status=status.HTTP_200_OK,
            )

        except TokenError as exc:
            return Response(
                {'detail': f'Geçersiz token: {exc}'},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ---------------------------------------------------------------------------
# Profil
# ---------------------------------------------------------------------------

class MeView(generics.RetrieveUpdateAPIView):
    """
    Kullanıcı profili görüntüleme ve güncelleme.

    GET  /api/v1/auth/me/   → Profil bilgileri
    PATCH /api/v1/auth/me/  → Profil güncelle (kısmi)

    Güncellenebilir alanlar: first_name, last_name, email, city, phone
    Değiştirilemez alanlar: username, role, is_verified
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# Şifre Değiştirme
# ---------------------------------------------------------------------------

class ChangePasswordView(APIView):
    """
    Şifre değiştirme.

    POST /api/v1/auth/change-password/

    Body:
    {
        "old_password": "EskiSifre1!",
        "new_password": "YeniGuclu2!",
        "new_password_confirm": "YeniGuclu2!"
    }
    """

    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [PasswordChangeRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Şifreniz başarıyla güncellendi. Lütfen yeniden giriş yapın.'},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Admin — Kullanıcı Yönetimi
# ---------------------------------------------------------------------------

class UserListView(generics.ListAPIView):
    """
    Tüm kullanıcı listesi — Sadece admin.

    GET /api/v1/auth/users/

    Query params:
        role=farmer|admin|agronomist  → Rol filtresi
        is_active=true|false           → Aktiflik filtresi
        search=<metin>                 → Username/email arama
    """

    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = User.objects.all().order_by('-date_joined')

        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(username__icontains=search) | qs.filter(email__icontains=search)

        return qs


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Kullanıcı detayı ve güncelleme — Sadece admin.

    GET   /api/v1/auth/users/{id}/  → Kullanıcı detayı
    PATCH /api/v1/auth/users/{id}/  → Kullanıcı güncelle (rol, is_active)
    """

    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = User.objects.all()
    http_method_names = ['get', 'patch', 'head', 'options']
