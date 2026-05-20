import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.dashboard.services import DashboardService
from django.contrib.auth import get_user_model
from apps.analysis.services import SimulationService, AnalysisService
from apps.fields.models import Field

def run_tests():
    User = get_user_model()
    user = User.objects.first()
    if user:
        print(f"Testing Dashboard Data for User: {user.username}")
        data = DashboardService.get_dashboard_data(user)
        print(f"Total fields: {data.get('total_fields')}")
        print(f"Empty fields: {data.get('empty_fields')}")
        print(f"Planted fields: {data.get('planted_fields')}")
        print(f"Total area: {data.get('total_area')}")
        print(f"Critical alerts: {data.get('critical_alerts')}")
        
        # Test simulation
        field = Field.objects.filter(user=user).first()
        if field:
            print(f"\nTesting Analysis Simulation on Field: {field.name}")
            analysis = SimulationService.simulate_sensor_data(field)
            print(f"Generated Analysis: N={analysis.nitrogen}, P={analysis.phosphorus}, K={analysis.potassium}")
            
            recs = AnalysisService.run_analysis(analysis)
            if recs:
                print(f"Generated Recommendations: {[(r.crop_name, r.confidence) for r in recs]}")
            else:
                print("No recommendations generated (maybe ML not ready).")
    else:
        print("No user found.")

if __name__ == '__main__':
    run_tests()
