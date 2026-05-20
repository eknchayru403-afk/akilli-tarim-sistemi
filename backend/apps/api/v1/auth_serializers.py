"""
Auth API Serializer'ları — Kayıt, Profil ve Şifre İşlemleri.

Mobil istemcilerin kullanıcı yönetimi için endpoint serializer'ları.
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Yeni kullanıcı kaydı serializer'ı.

    Örnek istek:
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
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'city', 'phone', 'role',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, attrs):
        """Şifre eşleşme ve e-posta benzersizlik kontrolü."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Şifreler eşleşmiyor.',
            })

        # E-posta benzersizlik
        email = attrs.get('email', '')
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({
                'email': 'Bu e-posta adresi zaten kullanımda.',
            })

        # Sadece izin verilen roller kabul edilir
        role = attrs.get('role', User.ROLE_FARMER)
        if role not in (User.ROLE_FARMER, User.ROLE_AGRONOMIST):
            # Admin rolünü API üzerinden almayı engelle
            raise serializers.ValidationError({
                'role': 'Geçersiz rol. İzin verilen değerler: farmer, agronomist.',
            })

        return attrs

    def create(self, validated_data):
        """Kullanıcı oluştur, şifreyi hash'le."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        logger.info(
            "Yeni kullanıcı kaydı: %s (rol: %s, email: %s)",
            user.username, user.role, user.email,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Kullanıcı profili okuma/güncelleme serializer'ı.

    Hassas alanlar (şifre, is_staff, is_superuser) dahil edilmez.
    """

    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'city', 'phone', 'role', 'is_verified', 'date_joined', 'last_login',
        )
        read_only_fields = ('id', 'username', 'role', 'is_verified', 'date_joined', 'last_login')

    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username


class ChangePasswordSerializer(serializers.Serializer):
    """
    Şifre değiştirme serializer'ı.

    Kullanıcının mevcut şifresini doğrular, ardından yeni şifreyi ayarlar.
    """

    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password],
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_old_password(self, value):
        """Mevcut şifre doğruluğunu kontrol et."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mevcut şifre hatalı.')
        return value

    def validate(self, attrs):
        """Yeni şifre eşleşme kontrolü."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Yeni şifreler eşleşmiyor.',
            })
        return attrs

    def save(self, **kwargs):
        """Şifreyi güncelle ve tüm oturumları geçersiz kıl."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])

        logger.info(
            "Şifre değiştirildi — kullanıcı: %s",
            user.username,
        )

        return user


class UserAdminSerializer(serializers.ModelSerializer):
    """
    Admin kullanıcı yönetim serializer'ı.

    Sadece admin rolündeki kullanıcılar erişebilir.
    Kullanıcı listesi, detay ve rol değiştirme işlemleri için.
    """

    full_name = serializers.SerializerMethodField(read_only=True)
    field_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'full_name', 'first_name', 'last_name',
            'role', 'is_verified', 'is_active', 'is_staff',
            'city', 'phone', 'date_joined', 'last_login', 'last_login_ip',
            'field_count',
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'last_login_ip')

    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username

    def get_field_count(self, obj) -> int:
        """Kullanıcıya ait tarla sayısı."""
        return getattr(obj, 'field_count', obj.field_set.count())
