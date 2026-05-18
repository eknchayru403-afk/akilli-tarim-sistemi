from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from apps.accounts.models import CustomUser
from apps.fields.models import Field
from apps.dashboard.services import DashboardService, _CACHE_KEY_DASHBOARD


class CacheConsistencyTestCase(TestCase):
    """Önbellek tutarlılık mekanizmasını doğrulayan test senaryoları."""

    def setUp(self):
        # Test kullanıcısını oluştur ve giriş yap
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        
        # Testler arası izolasyon için önbelleği temizle
        cache.clear()

    def test_dashboard_service_caches_stats(self):
        """DashboardService.get_dashboard_data'nın istatistikleri önbelleğe aldığını doğrula."""
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=self.user.pk)
        
        # 1. Başlangıçta önbellek boş olmalı
        self.assertIsNone(cache.get(cache_key))
        
        # 2. Veriyi çek (bu işlem istatistikleri önbelleğe almalı)
        DashboardService.get_dashboard_data(self.user)
        
        # 3. Önbellekte veri olmalı
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertIn('total_fields', cached_data)
        self.assertIn('empty_fields', cached_data)

    def test_invalidate_cache_clears_cache(self):
        """DashboardService.invalidate_cache metodunun önbelleği temizlediğini doğrula."""
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=self.user.pk)
        
        # 1. Veriyi önbelleğe al
        DashboardService.get_dashboard_data(self.user)
        self.assertIsNotNone(cache.get(cache_key))
        
        # 2. Cache'i manuel olarak temizle
        DashboardService.invalidate_cache(self.user)
        
        # 3. Önbellek boş olmalı
        self.assertIsNone(cache.get(cache_key))

    def test_field_create_invalidates_cache(self):
        """Yeni bir tarla oluşturulduğunda dashboard önbelleğinin temizlendiğini doğrula."""
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=self.user.pk)
        
        # 1. Veriyi önbelleğe al
        DashboardService.get_dashboard_data(self.user)
        self.assertIsNotNone(cache.get(cache_key))
        
        # 2. Yeni tarla oluştur (POST isteği)
        response = self.client.post(reverse('fields:create'), {
            'name': 'Yeni Tarla',
            'location': 'Adana',
            'area_decar': '10.5',
            'soil_type': 'tinli',
            'status': 'empty',
        })
        
        self.assertEqual(response.status_code, 302, "Tarla oluşturma başarılı olmalı (redirect)")
        
        # 3. Önbellek temizlenmiş olmalı
        self.assertIsNone(cache.get(cache_key))

    def test_field_update_invalidates_cache(self):
        """Tarla güncellendiğinde dashboard önbelleğinin temizlendiğini doğrula."""
        # 1. Test için tarla oluştur
        field = Field.objects.create(
            user=self.user,
            name='Eski Tarla',
            area_decar=Decimal('10.0')
        )
        
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=self.user.pk)
        
        # 2. Veriyi önbelleğe al
        DashboardService.get_dashboard_data(self.user)
        self.assertIsNotNone(cache.get(cache_key))
        
        # 3. Tarlayı güncelle (POST isteği)
        response = self.client.post(reverse('fields:update', kwargs={'pk': field.pk}), {
            'name': 'Güncellenmiş Tarla',
            'location': '',
            'area_decar': '15.0',
            'soil_type': 'tinli',
            'status': 'empty',
        })
        
        self.assertEqual(response.status_code, 302, "Tarla güncelleme başarılı olmalı (redirect)")
        
        # 4. Önbellek temizlenmiş olmalı
        self.assertIsNone(cache.get(cache_key))

    def test_field_delete_invalidates_cache(self):
        """Tarla silindiğinde dashboard önbelleğinin temizlendiğini doğrula."""
        # 1. Test için tarla oluştur
        field = Field.objects.create(
            user=self.user,
            name='Silinecek Tarla',
            area_decar=Decimal('10.0')
        )
        
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=self.user.pk)
        
        # 2. Veriyi önbelleğe al
        DashboardService.get_dashboard_data(self.user)
        self.assertIsNotNone(cache.get(cache_key))
        
        # 3. Tarlayı sil (POST isteği)
        response = self.client.post(reverse('fields:delete', kwargs={'pk': field.pk}))
        
        self.assertEqual(response.status_code, 302, "Tarla silme başarılı olmalı (redirect)")
        
        # 4. Önbellek temizlenmiş olmalı
        self.assertIsNone(cache.get(cache_key))
