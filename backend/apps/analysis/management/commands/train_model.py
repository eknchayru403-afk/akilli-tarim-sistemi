"""Management command: train_model — ML modelini eğitir."""

import logging

from django.core.management.base import BaseCommand

from ml.trainer import train_crop_model

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """RandomForest modelini eğitir ve kaydeder."""

    help = 'Kaggle CSV verisiyle ürün tahmin modelini eğitir.'

    def handle(self, *args, **options) -> None:
        """Model eğitimini başlat."""
        self.stdout.write('Model eğitimi başlıyor...')

        results = train_crop_model()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nModel eğitimi tamamlandı!\n"
                f"  Accuracy: {results['accuracy']:.4f}\n"
                f"  Samples: {results['n_samples']}\n"
                f"  Features: {results['n_features']}\n"
                f"  Classes: {results['n_classes']}\n"
                f"  Model: {results['model_path']}\n"
            )
        )
        self.stdout.write(f"\nClassification Report:\n{results['report']}")
