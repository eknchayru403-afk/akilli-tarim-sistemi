"""
LSTM tabanlı toprak nemi ve sulama tahmini modeli.
"""

import os
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from django.conf import settings
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

logger = logging.getLogger(__name__)

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import load_model

from apps.fields.models import SensorData

MODEL_DIR = settings.ML_MODELS_DIR / 'lstm_irrigation'
SCALER_PATH = settings.ML_MODELS_DIR / 'lstm_scaler.pkl'


def fetch_data(field_id: int) -> pd.DataFrame:
    """Veritabanından geçmiş sensör verilerini çeker."""
    queryset = SensorData.objects.filter(field_id=field_id).order_by('created_at')
    
    data = list(queryset.values(
        'created_at', 'soil_moisture', 'temperature', 'plant_water_consumption'
    ))
    
    if not data:
        raise ValueError(f"Tarla ID {field_id} için sensör verisi bulunamadı.")
        
    df = pd.DataFrame(data)
    df.set_index('created_at', inplace=True)
    # Gerekirse eksik verileri doldurma (forward fill)
    df.ffill(inplace=True)
    # Eğer hala NaN varsa 0 ile doldur
    df.fillna(0, inplace=True)
    return df

def create_sequences(data: np.ndarray, lookback: int = 24):
    """LSTM için zaman serisi pencereleri oluşturur."""
    X, y = [], []
    # data[:, 0] varsayılan olarak soil_moisture olsun (hedef değişken)
    for i in range(len(data) - lookback):
        X.append(data[i:(i + lookback), :])
        y.append(data[i + lookback, 0])
    return np.array(X), np.array(y)

def train_lstm_model(field_id: int, lookback: int = 24, epochs: int = 50, batch_size: int = 32):
    """LSTM modelini eğitir ve kaydeder."""
    df = fetch_data(field_id)
    
    if len(df) < lookback * 2:
        raise ValueError("Eğitim için yeterli veri yok. Daha fazla sensör verisi ekleyin.")
        
    # Sütun sırası: soil_moisture (0), temperature (1), plant_water_consumption (2)
    features = ['soil_moisture', 'temperature', 'plant_water_consumption']
    dataset = df[features].values
    
    # Ölçeklendirme
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)
    
    # Train/Validation/Test Split (%70, %15, %15)
    n = len(scaled_data)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)
    
    train_data = scaled_data[:train_end]
    val_data = scaled_data[train_end:val_end]
    test_data = scaled_data[val_end:]
    
    X_train, y_train = create_sequences(train_data, lookback)
    X_val, y_val = create_sequences(val_data, lookback)
    X_test, y_test = create_sequences(test_data, lookback)
    
    if len(X_train) == 0 or len(X_val) == 0 or len(X_test) == 0:
        raise ValueError("Pencereleme sonrası yeterli veri kalmadı. Lookback değerini küçültün veya veriyi artırın.")
    
    # Model Mimarisi
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    # Eğitim
    logger.info("LSTM eğitimi başlıyor...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        verbose=1
    )
    
    # Test Değerlendirmesi
    y_pred = model.predict(X_test)
    
    # Ters ölçeklendirme (sadece hedef değişken için)
    dummy_pred = np.zeros((len(y_pred), len(features)))
    dummy_pred[:, 0] = y_pred.flatten()
    y_pred_rescaled = scaler.inverse_transform(dummy_pred)[:, 0]
    
    dummy_test = np.zeros((len(y_test), len(features)))
    dummy_test[:, 0] = y_test.flatten()
    y_test_rescaled = scaler.inverse_transform(dummy_test)[:, 0]
    
    mae = mean_absolute_error(y_test_rescaled, y_pred_rescaled)
    rmse = np.sqrt(mean_squared_error(y_test_rescaled, y_pred_rescaled))
    
    logger.info(f"Model Test Sonuçları - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
    
    # Kaydetme
    os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)
    model.save(MODEL_DIR)
    joblib.dump(scaler, SCALER_PATH)
    logger.info(f"Model başarıyla kaydedildi: {MODEL_DIR}")
    
    return {
        'mae': mae,
        'rmse': rmse,
        'model_path': str(MODEL_DIR),
        'history': history.history
    }

def predict_irrigation_need(recent_data: pd.DataFrame, threshold: float = 30.0):
    """
    Kaydedilmiş modeli kullanarak bir sonraki adımı tahmin eder ve sınıflandırır.
    
    Args:
        recent_data: En az 'lookback' uzunluğunda geçmiş veri DataFrame'i.
        threshold: Sulama başlatma eşiği (% toprak nemi).
    """
    if not os.path.exists(MODEL_DIR) or not os.path.exists(SCALER_PATH):
        raise FileNotFoundError("Eğitilmiş model veya scaler bulunamadı.")
        
    model = load_model(MODEL_DIR)
    scaler = joblib.load(SCALER_PATH)
    
    features = ['soil_moisture', 'temperature', 'plant_water_consumption']
    
    # Eksik sütun kontrolü
    for f in features:
        if f not in recent_data.columns:
            raise ValueError(f"Eksik sütun: {f}")
            
    dataset = recent_data[features].values
    scaled_data = scaler.transform(dataset)
    
    lookback = model.input_shape[1]
    if len(scaled_data) < lookback:
        raise ValueError(f"Tahmin için en az {lookback} satır veri gerekli.")
        
    # Sadece son lookback penceresini al
    X_input = scaled_data[-lookback:].reshape(1, lookback, len(features))
    
    scaled_pred = model.predict(X_input)
    
    dummy_pred = np.zeros((1, len(features)))
    dummy_pred[0, 0] = scaled_pred[0, 0]
    predicted_moisture = scaler.inverse_transform(dummy_pred)[0, 0]
    
    # Eşiğe göre sınıflandırma kararı
    decision = "Sulama Başlat" if predicted_moisture < threshold else "Nem Yeterli"
    
    return {
        'predicted_soil_moisture': float(predicted_moisture),
        'decision': decision,
        'threshold': threshold
    }
