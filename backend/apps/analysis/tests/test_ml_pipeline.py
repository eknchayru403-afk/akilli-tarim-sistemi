from django.test import TestCase
from ml.hyperparameter_tuner import HyperparameterTuner
from apps.analysis.models import ModelLog

class MLPipelineTest(TestCase):
    def setUp(self):
        self.tuner = HyperparameterTuner()

    def test_tune_irrigation_model(self):
        # CV folds = 2 for faster testing
        res = self.tuner.tune_irrigation_model(cv_folds=2)
        
        self.assertIn('model', res)
        self.assertIn('score', res)
        self.assertIn('params', res)
        
        # Check if ModelLog was created
        log = ModelLog.objects.filter(model_type='GradientBoosting').first()
        self.assertIsNotNone(log)
        self.assertAlmostEqual(float(log.accuracy), float(res['score']), places=4)
