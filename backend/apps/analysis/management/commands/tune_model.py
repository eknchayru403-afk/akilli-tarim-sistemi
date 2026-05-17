import logging
from django.core.management.base import BaseCommand
from ml.hyperparameter_tuner import HyperparameterTuner

class Command(BaseCommand):
    help = 'Belirtilen model için hiperparametre optimizasyonu yapar.'

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str, choices=['crop', 'irrigation', 'all'], default='all', help='Hangi modelin optimize edileceği')
        parser.add_argument('--cv', type=int, default=5, help='K-Fold cross-validation katman sayısı')

    def handle(self, *args, **options):
        model_choice = options['model']
        cv_folds = options['cv']
        tuner = HyperparameterTuner()

        if model_choice in ['crop', 'all']:
            self.stdout.write(self.style.SUCCESS(f"Crop model optimizasyonu (CV={cv_folds}) baslatiliyor..."))
            res = tuner.tune_crop_model(cv_folds=cv_folds)
            self.stdout.write(self.style.SUCCESS(f"Crop Model Basarili! En iyi skor: {res['score']:.4f}"))

        if model_choice in ['irrigation', 'all']:
            self.stdout.write(self.style.SUCCESS(f"Irrigation model optimizasyonu (CV={cv_folds}) baslatiliyor..."))
            res = tuner.tune_irrigation_model(cv_folds=cv_folds)
            self.stdout.write(self.style.SUCCESS(f"Irrigation Model Basarili! En iyi skor: {res['score']:.4f}"))
