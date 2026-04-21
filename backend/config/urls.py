"""Root URL configuration for ATYS project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('fields/', include('apps.fields.urls')),
    path('analysis/', include('apps.analysis.urls')),
    path('weather/', include('apps.weather.urls')),
    path('prices/', include('apps.analysis.price_urls')),
]
