import logging
import time
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from .data_loader import get_prepared_data
from .constants import FEATURE_COLUMNS
from .irrigation_sklearn import generate_irrigation_training_data
from apps.analysis.models import ModelLog

logger = logging.getLogger(__name__)

class HyperparameterTuner:
    """Scikit-learn modelleri için hiperparametre optimizasyonu."""

    def tune_crop_model(self, cv_folds=5) -> dict:
        """GridSearchCV ile crop prediction model optimizasyonu."""
        logger.info("Crop Prediction (RandomForest) optimizasyonu başlıyor...")
        df = get_prepared_data()
        X = df[FEATURE_COLUMNS].values
        y = df['label'].values

        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5],
        }

        model = RandomForestClassifier(random_state=42)
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            cv=cv,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )

        start_time = time.time()
        grid_search.fit(X, y)
        training_time = time.time() - start_time

        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_
        
        cv_results = grid_search.cv_results_
        best_index = grid_search.best_index_
        std_score = cv_results['std_test_score'][best_index]

        # Log to DB
        ModelLog.objects.create(
            model_name='Crop Prediction',
            model_type='RandomForest',
            parameters=best_params,
            accuracy=best_score,
            cv_mean_score=best_score,
            cv_std_score=std_score,
            training_time_seconds=training_time,
            notes=f'Tuned with {cv_folds}-fold CV. Best index: {best_index}'
        )

        logger.info(f"Crop model optimizasyonu tamamlandı. Best Score: {best_score:.4f}")
        return {
            'model': best_model,
            'params': best_params,
            'score': best_score,
            'std': std_score,
            'time': training_time
        }

    def tune_irrigation_model(self, cv_folds=5) -> dict:
        """Sulama tahmin modeli (GradientBoosting) optimizasyonu."""
        logger.info("Irrigation Prediction (GradientBoosting) optimizasyonu başlıyor...")
        X, y = generate_irrigation_training_data(n_samples=2000)

        param_grid = {
            'n_estimators': [100, 200],
            'learning_rate': [0.05, 0.1],
            'max_depth': [3, 5],
        }

        model = GradientBoostingClassifier(random_state=42)
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)

        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            cv=cv,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )

        start_time = time.time()
        grid_search.fit(X, y)
        training_time = time.time() - start_time

        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_
        
        cv_results = grid_search.cv_results_
        best_index = grid_search.best_index_
        std_score = cv_results['std_test_score'][best_index]

        # Log to DB
        ModelLog.objects.create(
            model_name='Irrigation Prediction',
            model_type='GradientBoosting',
            parameters=best_params,
            accuracy=best_score,
            cv_mean_score=best_score,
            cv_std_score=std_score,
            training_time_seconds=training_time,
            notes=f'Tuned with {cv_folds}-fold CV. Synthetic data (2000 samples).'
        )

        logger.info(f"Irrigation model optimizasyonu tamamlandı. Best Score: {best_score:.4f}")
        return {
            'model': best_model,
            'params': best_params,
            'score': best_score,
            'std': std_score,
            'time': training_time
        }
