import logging
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

logger = logging.getLogger(__name__)

def generate_irrigation_training_data(n_samples: int = 2000) -> tuple:
    np.random.seed(42)
    soil_moisture = np.random.uniform(10, 90, n_samples)
    temperature = np.random.uniform(5, 45, n_samples)
    humidity = np.random.uniform(20, 95, n_samples)
    rainfall = np.random.uniform(0, 300, n_samples)
    season = np.random.randint(0, 4, n_samples)
    soil_type = np.random.randint(0, 6, n_samples)

    X = np.column_stack([
        soil_moisture, temperature, humidity, rainfall, season, soil_type,
    ])

    y = np.zeros(n_samples)
    for i in range(n_samples):
        score = 0
        if soil_moisture[i] < 30:
            score += 3
        elif soil_moisture[i] < 45:
            score += 1
        if temperature[i] > 30:
            score += 2
        elif temperature[i] > 25:
            score += 1
        if rainfall[i] < 30:
            score += 2
        elif rainfall[i] < 80:
            score += 1
        if humidity[i] < 40:
            score += 1
        if season[i] == 1:  # yaz
            score += 1
        if soil_type[i] == 1:  # kumlu
            score += 1
        y[i] = 1 if score >= 4 else 0

    return X, y

def build_and_train_irrigation_model(params=None):
    if params is None:
        params = {'n_estimators': 100, 'learning_rate': 0.1, 'max_depth': 3}
    model = GradientBoostingClassifier(random_state=42, **params)
    return model
