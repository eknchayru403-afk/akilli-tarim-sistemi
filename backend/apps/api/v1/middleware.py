"""
HTTPS Zorunluluk Middleware'i.

API endpoint'lerine (/api/) gelen HTTP isteklerini üretim ortamında reddeder.
Geliştirme modunda (DEBUG=True) devre dışıdır.

Proxy arkasında çalışırken X-Forwarded-Proto header'ını kontrol eder.
"""

import logging

from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequireHTTPSMiddleware:
    """
    API istekleri için HTTPS zorunluluğu uygular.

    - Sadece /api/ ile başlayan path'lere uygulanır.
    - DEBUG=True iken devre dışıdır (geliştirme kolaylığı).
    - X-Forwarded-Proto header'ı desteklenir (nginx, load balancer).
    - HTTP isteği geldiğinde 403 Forbidden yanıt döner.
    """

    API_PATH_PREFIX = '/api/'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Geliştirme modunda devre dışı
        if getattr(settings, 'DEBUG', False):
            return self.get_response(request)

        # Sadece API path'lerini kontrol et
        if not request.path.startswith(self.API_PATH_PREFIX):
            return self.get_response(request)

        # HTTPS kontrolü
        if not self._is_secure(request):
            logger.warning(
                "HTTPS zorunluluğu: HTTP isteği reddedildi — path=%s, IP=%s",
                request.path,
                self._get_client_ip(request),
            )
            return JsonResponse(
                {
                    'detail': 'HTTPS zorunludur. Lütfen güvenli bağlantı kullanın.',
                    'code': 'https_required',
                },
                status=403,
            )

        return self.get_response(request)

    def _is_secure(self, request) -> bool:
        """
        İsteğin HTTPS üzerinden gelip gelmediğini kontrol eder.

        Django'nun is_secure() metodu + proxy header desteği.
        """
        if request.is_secure():
            return True

        # Proxy arkasında X-Forwarded-Proto kontrolü
        x_forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO', '')
        if x_forwarded_proto.lower() == 'https':
            return True

        return False

    def _get_client_ip(self, request) -> str:
        """İstemci IP adresini güvenli şekilde çıkar."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
