"""
Weather servisleri — Statik hava durumu verisi (v1).

v2'de OpenWeatherMap API entegrasyonu planlanıyor.
"""

import logging

logger = logging.getLogger(__name__)

# Şehir bazlı statik hava durumu verileri
STATIC_WEATHER_DATA = {
    'İstanbul': {'temp': 18, 'humidity': 65, 'condition': 'Parçalı Bulutlu', 'icon': 'cloud-sun'},
    'Ankara': {'temp': 15, 'humidity': 45, 'condition': 'Güneşli', 'icon': 'sun'},
    'İzmir': {'temp': 22, 'humidity': 55, 'condition': 'Açık', 'icon': 'sun'},
    'Bursa': {'temp': 17, 'humidity': 60, 'condition': 'Bulutlu', 'icon': 'cloud'},
    'Antalya': {'temp': 25, 'humidity': 50, 'condition': 'Güneşli', 'icon': 'sun'},
    'Adana': {'temp': 24, 'humidity': 55, 'condition': 'Açık', 'icon': 'sun'},
    'Konya': {'temp': 14, 'humidity': 40, 'condition': 'Güneşli', 'icon': 'sun'},
    'Gaziantep': {'temp': 20, 'humidity': 35, 'condition': 'Açık', 'icon': 'sun'},
    'Diyarbakır': {'temp': 22, 'humidity': 30, 'condition': 'Güneşli', 'icon': 'sun'},
    'Elazığ': {'temp': 16, 'humidity': 42, 'condition': 'Parçalı Bulutlu', 'icon': 'cloud-sun'},
    'Trabzon': {'temp': 15, 'humidity': 75, 'condition': 'Yağmurlu', 'icon': 'cloud-rain'},
    'Samsun': {'temp': 16, 'humidity': 70, 'condition': 'Bulutlu', 'icon': 'cloud'},
}

DEFAULT_WEATHER = {'temp': 18, 'humidity': 50, 'condition': 'Parçalı Bulutlu', 'icon': 'cloud-sun'}


class WeatherService:
    """Statik hava durumu servisi."""

    @staticmethod
    def get_weather(user) -> dict:
        """
        Kullanıcının şehrine göre hava durumu verisini döndürür.

        Args:
            user: Mevcut kullanıcı.

        Returns:
            Hava durumu dict: temp, humidity, condition, icon, city.
        """
        city = getattr(user, 'city', '') or ''
        weather = STATIC_WEATHER_DATA.get(city, DEFAULT_WEATHER).copy()
        weather['city'] = city if city else 'Türkiye'
        return weather

    @staticmethod
    def get_weather_by_city(city: str) -> dict:
        """Şehir adına göre hava durumu döndürür."""
        weather = STATIC_WEATHER_DATA.get(city, DEFAULT_WEATHER).copy()
        weather['city'] = city
        return weather
