from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.fields.models import Field, SensorData, IrrigationLog
from apps.analysis.models import SoilAnalysis, CareRecommendation, CropRecommendation
from apps.reports.services import ReportService
from datetime import datetime

User = get_user_model()


class ReportTestCase(TestCase):
    """Raporlama modülü için test durumları."""

    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testfarmer',
            email='testfarmer@example.com',
            password='TestPassword123!',
            role='farmer',
            is_verified=True
        )

        # Test tarlası oluştur
        self.field = Field.objects.create(
            user=self.user,
            name='Test Tarlası',
            area_decar=10.5,
            soil_type='tinli',
            status='planted',
            current_crop='Bugday'
        )

        # Test toprak analizi oluştur
        self.soil_analysis = SoilAnalysis.objects.create(
            field=self.field,
            nitrogen=50.0,
            phosphorus=30.0,
            potassium=200.0,
            ph=6.5,
            temperature=22.0,
            humidity=45.0,
            rainfall=15.0,
            source='manual'
        )

        # Test sensör verisi oluştur
        self.sensor_data = SensorData.objects.create(
            field=self.field,
            humidity=40.0,
            temperature=25.0,
            soil_moisture=35.0,
            plant_water_consumption=5.2,
            soil_ph=6.2,
            light_intensity=600.0
        )

        # Test sulama kaydı oluştur
        self.irrigation_log = IrrigationLog.objects.create(
            field=self.field,
            log_type='irrigation',
            amount=500.0,
            details='Sabah sulaması yapıldı.'
        )

        # Test bakım önerisi oluştur
        self.care_recommendation = CareRecommendation.objects.create(
            field=self.field,
            recommendation_type='irrigation',
            message='Toprak nemi düşük, sulama yapın.',
            priority='high',
            is_done=False
        )

    def test_get_report_data_general(self):
        """Genel rapor verisinin düzgün toplandığını test eder."""
        data = ReportService.get_report_data(self.user, report_type='general')

        self.assertEqual(data['user_name'], 'testfarmer')
        self.assertEqual(data['field_name'], 'Tüm Tarlalar')
        self.assertEqual(len(data['care_records']), 1)
        self.assertEqual(len(data['soil_analyses']), 1)
        self.assertEqual(len(data['sensor_data']), 1)
        self.assertEqual(len(data['irrigation_logs']), 1)

    def test_get_report_data_irrigation(self):
        """Sulama raporu için sadece sulama ile ilgili verilerin geldiğini test eder."""
        data = ReportService.get_report_data(self.user, report_type='irrigation')

        self.assertEqual(data['report_type'], 'irrigation')
        self.assertEqual(len(data['care_records']), 1)
        self.assertEqual(data['care_records'][0]['type'], 'irrigation')
        self.assertEqual(len(data['sensor_data']), 1)
        self.assertEqual(len(data['irrigation_logs']), 1)
        self.assertEqual(data['irrigation_logs'][0]['type'], 'irrigation')
        # Fertilization and yield fields should be empty
        self.assertEqual(len(data['soil_analyses']), 0)
        self.assertEqual(len(data['recommendations']), 0)

    def test_get_report_data_fertilization(self):
        """Gübreleme raporu verilerini test eder."""
        # Ek bir gübreleme logu ekleyelim
        IrrigationLog.objects.create(
            field=self.field,
            log_type='fertilization',
            amount=50.0,
            details='DAP gübresi uygulandı.'
        )

        data = ReportService.get_report_data(self.user, report_type='fertilization')

        self.assertEqual(data['report_type'], 'fertilization')
        self.assertEqual(len(data['soil_analyses']), 1)
        self.assertEqual(len(data['irrigation_logs']), 1)
        self.assertEqual(data['irrigation_logs'][0]['type'], 'fertilization')
        # Sensor data should be empty in fertilization report
        self.assertEqual(len(data['sensor_data']), 0)

    def test_download_report_pdf(self):
        """PDF indirme view'ının HTTP 200 döndürdüğünü test eder."""
        self.client.force_login(self.user)
        response = self.client.get('/reports/download/?report_type=general&export_format=pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment;'))

    def test_download_report_csv(self):
        """CSV indirme view'ının HTTP 200 döndürdüğünü test eder."""
        self.client.force_login(self.user)
        response = self.client.get('/reports/download/?report_type=general&export_format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response['Content-Disposition'].startswith('attachment;'))
