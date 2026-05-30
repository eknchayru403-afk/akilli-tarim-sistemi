"""
API v1 Throttle Sınıfları — Rate Limiting.

Brute-force saldırılarına karşı özel rate limit kuralları.
Django REST Framework'ün ScopedRateThrottle altyapısı kullanılır;
throttle scope'ları settings.py'daki DEFAULT_THROTTLE_RATES ile eşleşir.
"""

from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle


class LoginRateThrottle(ScopedRateThrottle):
    """
    Login endpoint için özel throttle.

    Kural: Dakikada 5 deneme (ayarlanabilir — settings: 'auth_login').
    Brute-force şifre tahmin saldırılarını engeller.
    IP tabanlı: Anonim istekler IP adresine göre izlenir.
    """
    scope = 'auth_login'


class RegisterRateThrottle(ScopedRateThrottle):
    """
    Kayıt endpoint için özel throttle.

    Kural: Saatte 3 kayıt denemesi (settings: 'auth_register').
    Toplu hesap oluşturma saldırılarını engeller.
    """
    scope = 'auth_register'


class TokenRefreshRateThrottle(ScopedRateThrottle):
    """
    Token yenileme endpoint için özel throttle.

    Kural: Dakikada 10 yenileme (settings: 'token_refresh').
    Token çalma senaryolarında servis istismarını önler.
    """
    scope = 'token_refresh'


class PasswordChangeRateThrottle(ScopedRateThrottle):
    """
    Şifre değiştirme endpoint için özel throttle.

    Kural: Saatte 5 deneme (settings: 'password_change').
    """
    scope = 'password_change'


class StrictAnonThrottle(AnonRateThrottle):
    """
    Anonim kullanıcılar için sıkı rate limit.

    Sadece public endpoint'lere (ör: token/verify) uygulanır.
    Kural: Saatte 30 istek.
    """
    rate = '30/hour'
