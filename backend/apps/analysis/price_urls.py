"""Price URL patterns."""

from django.urls import path

from . import price_views

app_name = 'prices'

urlpatterns = [
    path('', price_views.price_list, name='list'),
]
