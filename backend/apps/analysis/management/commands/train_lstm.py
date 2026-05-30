from django.core.management.base import BaseCommand
from ml.lstm_model import train_lstm_model

class Command(BaseCommand):
    help = "LSTM tabanlı toprak nemi tahmin modelini eğitir."

    def add_arguments(self, parser):
        parser.add_argument('field_id', type=int, help="Eğitim verisi alınacak Tarla (Field) ID'si")
        parser.add_argument('--epochs', type=int, default=50, help="Eğitim için epoch sayısı")
        parser.add_argument('--lookback', type=int, default=24, help="Zaman serisi pencere (sequence) boyutu")
        parser.add_argument('--batch-size', type=int, default=32, help="Eğitim için batch boyutu")

    def handle(self, *args, **options):
        field_id = options['field_id']
        epochs = options['epochs']
        lookback = options['lookback']
        batch_size = options['batch_size']

        self.stdout.write(self.style.NOTICE(f"Tarla ID {field_id} için LSTM modeli eğitimi başlatılıyor..."))
        self.stdout.write(f"Parametreler -> Epoch: {epochs}, Pencere Boyutu: {lookback}, Batch: {batch_size}")

        try:
            results = train_lstm_model(
                field_id=field_id,
                lookback=lookback,
                epochs=epochs,
                batch_size=batch_size
            )
            self.stdout.write(self.style.SUCCESS("Eğitim başarıyla tamamlandı!"))
            self.stdout.write(self.style.SUCCESS(f"Metrikler -> MAE: {results['mae']:.4f}, RMSE: {results['rmse']:.4f}"))
            self.stdout.write(f"Model şuraya kaydedildi: {results['model_path']}")
            
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Veri hazırlık hatası: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Beklenmeyen bir hata oluştu: {e}"))
