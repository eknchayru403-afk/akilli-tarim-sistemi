"""
Mobil entegrasyon testleri — responsive web istemcisi ve veri senkronizasyonu.

Not: Repoda ayrı bir native mobil uygulama (Flutter/React Native) yoktur.
Bu testler mobil tarayıcıdan erişilen Django web arayüzünü doğrular.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser
from apps.analysis.models import SoilAnalysis
from apps.dashboard.services import DashboardService, _CACHE_KEY_DASHBOARD
from apps.fields.models import Field

# Yaygın mobil / tablet User-Agent dizisi
MOBILE_DEVICES = {
    'iphone_safari': (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ),
    'android_chrome': (
        'Mozilla/5.0 (Linux; Android 14; SM-S911B) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    ),
    'ipad_safari': (
        'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ),
    'pixel_chrome': (
        'Mozilla/5.0 (Linux; Android 14; Pixel 8) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
    ),
}

AUTHENTICATED_ROUTES = [
    ('dashboard:index', {}),
    ('fields:list', {}),
    ('analysis:history', {}),
    ('weather:index', {}),
    ('prices:list', {}),
    ('accounts:profile', {}),
]

PUBLIC_ROUTES = [
    ('accounts:login', {}),
    ('accounts:register', {}),
]


class MobileDataSyncTestCase(TestCase):
    """Veri senkronizasyonu — CRUD ve analiz akışı."""

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username='mobile_user',
            password='MobileTest123!',
        )
        self.client = Client(
            HTTP_USER_AGENT=MOBILE_DEVICES['android_chrome'],
        )
        self.client.login(username='mobile_user', password='MobileTest123!')
        cache.clear()

    def test_field_create_appears_in_list_and_invalidates_dashboard_cache(self) -> None:
        """Tarla oluşturma → liste ve dashboard önbelleği güncellenir."""
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=self.user.pk)
        DashboardService.get_dashboard_data(self.user)
        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.post(reverse('fields:create'), {
            'name': 'Mobil Test Tarlası',
            'location': 'Konya',
            'area_decar': '15',
            'soil_type': 'tinli',
            'status': 'empty',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(cache.get(cache_key))

        list_response = self.client.get(reverse('fields:list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Mobil Test Tarlası')

    def test_simulation_creates_soil_analysis(self) -> None:
        """Simülasyon POST → SoilAnalysis kaydı oluşur (mobil senkron)."""
        field = Field.objects.create(
            user=self.user,
            name='Simülasyon Tarlası',
            area_decar=Decimal('8'),
        )
        before = SoilAnalysis.objects.filter(field=field).count()
        response = self.client.post(reverse('analysis:simulate', kwargs={'field_pk': field.pk}))
        self.assertIn(response.status_code, (302, 200))
        after = SoilAnalysis.objects.filter(field=field).count()
        self.assertGreater(after, before)

    def test_field_update_reflected_in_detail(self) -> None:
        """Tarla güncelleme detay sayfasına yansır."""
        field = Field.objects.create(
            user=self.user,
            name='Eski Ad',
            area_decar=Decimal('5'),
        )
        response = self.client.post(
            reverse('fields:update', kwargs={'pk': field.pk}),
            {
                'name': 'Yeni Mobil Ad',
                'location': 'Ankara',
                'area_decar': '12',
                'soil_type': 'kumlu',
                'status': 'planted',
                'current_crop': 'bugday',
            },
        )
        self.assertEqual(response.status_code, 302)
        detail = self.client.get(reverse('fields:detail', kwargs={'pk': field.pk}))
        self.assertContains(detail, 'Yeni Mobil Ad')


class MobileDeviceCompatibilityTestCase(TestCase):
    """Farklı cihaz User-Agent'ları ile sayfa erişilebilirliği."""

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username='device_user',
            password='DeviceTest123!',
        )

    def _client_for(self, user_agent: str) -> Client:
        return Client(HTTP_USER_AGENT=user_agent)

    def test_public_pages_on_all_devices(self) -> None:
        for device_name, ua in MOBILE_DEVICES.items():
            with self.subTest(device=device_name):
                client = self._client_for(ua)
                for route_name, kwargs in PUBLIC_ROUTES:
                    response = client.get(reverse(route_name, kwargs=kwargs))
                    self.assertEqual(
                        response.status_code,
                        200,
                        f'{route_name} failed on {device_name}',
                    )
                    self.assertIn(
                        b'width=device-width',
                        response.content,
                        f'viewport meta missing on {device_name}',
                    )

    def test_authenticated_pages_on_all_devices(self) -> None:
        for device_name, ua in MOBILE_DEVICES.items():
            with self.subTest(device=device_name):
                client = self._client_for(ua)
                self.assertTrue(
                    client.login(username='device_user', password='DeviceTest123!'),
                )
                for route_name, kwargs in AUTHENTICATED_ROUTES:
                    response = client.get(reverse(route_name, kwargs=kwargs))
                    self.assertEqual(
                        response.status_code,
                        200,
                        f'{route_name} failed on {device_name}',
                    )
                    self.assertIn(
                        b'sidebar-toggle',
                        response.content,
                        f'mobile sidebar toggle missing on {device_name}',
                    )

    def test_login_flow_on_mobile(self) -> None:
        for device_name, ua in MOBILE_DEVICES.items():
            with self.subTest(device=device_name):
                client = self._client_for(ua)
                response = client.post(reverse('accounts:login'), {
                    'username': 'device_user',
                    'password': 'DeviceTest123!',
                }, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Dashboard')

    def test_unauthenticated_redirect_to_login(self) -> None:
        client = self._client_for(MOBILE_DEVICES['iphone_safari'])
        response = client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
