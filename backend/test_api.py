import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.fields.models import Field

User = get_user_model()

def run_test():
    # 1. Create a test user
    user, created = User.objects.get_or_create(username='test_api_user', defaults={'email': 'test@api.com'})
    if created:
        user.set_password('testpass123')
        user.save()

    # 2. Create a test field
    field, f_created = Field.objects.get_or_create(user=user, name='Test Tarla', defaults={
        'location': 'Ankara',
        'area_decar': 10,
        'soil_type': 'tınlı',
        'status': 'aktif'
    })

    client = APIClient()

    # 3. Get Token
    response = client.post('/api/v1/auth/login/', {'username': 'test_api_user', 'password': 'testpass123'}, format='json')
    if response.status_code != 200:
        print("Login failed:", response.data)
        return
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # 4. POST /api/v1/sensors/data/
    post_data = {
        "field": field.id,
        "humidity": 45.5,
        "temperature": 22.1,
        "soil_moisture": 30.0,
        "plant_water_consumption": 2.5,
        "soil_ph": 6.5,
        "light_intensity": 10000
    }
    print("--- POST /api/v1/sensors/data/ ---")
    post_resp = client.post('/api/v1/sensors/data/', post_data, format='json')
    print("Status:", post_resp.status_code)
    print("Response:", post_resp.data)
    print()

    # 5. GET /api/v1/sensors/
    print("--- GET /api/v1/sensors/ ---")
    get_sens_resp = client.get('/api/v1/sensors/')
    print("Status:", get_sens_resp.status_code)
    print("Response:", get_sens_resp.data)
    print()

    # 6. GET /api/v1/fields/
    print("--- GET /api/v1/fields/ ---")
    get_fields_resp = client.get('/api/v1/fields/')
    print("Status:", get_fields_resp.status_code)
    print("Response:", get_fields_resp.data)
    print()

if __name__ == '__main__':
    run_test()
