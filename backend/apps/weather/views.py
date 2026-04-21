"""Weather views — Hava durumu sayfası."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import STATIC_WEATHER_DATA, WeatherService


@login_required
def weather_view(request):
    """Hava durumu sayfası."""
    weather = WeatherService.get_weather(request.user)
    all_weather = STATIC_WEATHER_DATA
    return render(request, 'weather/index.html', {
        'weather': weather,
        'all_weather': all_weather,
    })
