"""
JWT Token Serializer'ları — Özelleştirilmiş claim'ler.

Mobil istemciler için token payload'ına rol, kullanıcı adı ve
doğrulama durumu eklenir; istemci tarafında UI yönlendirmesi için kullanılır.
"""

import logging

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Özelleştirilmiş JWT token üretici.

    Standart access/refresh token'a ek olarak payload'a:
    - role     : Kullanıcı rolü (farmer/admin/agronomist)
    - username : Kullanıcı adı
    - full_name: Tam ad (varsa)
    - is_verified: E-posta doğrulama durumu
    alanları eklenir.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Özel claim'ler
        token['role'] = user.role
        token['username'] = user.username
        token['full_name'] = user.get_full_name() or user.username
        token['is_verified'] = user.is_verified
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Response'a ek kullanıcı bilgileri ekle
        data['user'] = {
            'id': self.user.pk,
            'username': self.user.username,
            'email': self.user.email,
            'full_name': self.user.get_full_name() or self.user.username,
            'role': self.user.role,
            'is_verified': self.user.is_verified,
        }

        logger.info(
            "JWT: Kullanıcı giriş yaptı — %s (rol: %s)",
            self.user.username,
            self.user.role,
        )

        return data
