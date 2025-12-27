import pytest
from src.api.ml_api.services.golden_hour import GoldenHourService
import numpy as np

def test_urgency_mapping():
    svc = GoldenHourService()
    # Level 5
    assert svc.urgency_descriptions[5] == "Critical - Immediate"
    # Level 1
    assert svc.urgency_descriptions[1] == "Elective - Scheduled"

def test_transform_vitals():
    svc = GoldenHourService()
    patient = {
        "age": 70,
        "systolic_bp": 190,
        "diastolic_bp": 100,
        "glucose": 200,
        "bmi": 30.0,
        "cholesterol": 250,
        "heart_rate": 110,
        "history_heart_disease": "Yes",
        "smoking": "Yes"
    }
    # Mocking the predict method to avoid loading pickle
    class MockModel:
        def predict_proba(self, X):
            # Return fake probabilities for 5 classes
            return np.array([[0.05, 0.05, 0.1, 0.2, 0.6]])
        
        feature_names_in_ = svc.feature_names

    svc.model = MockModel()
    
    result = svc.predict_urgency(["Chest pain", "Shortness of breath"], patient)
    
    assert result["urgency_level"] == 5
    assert result["urgency_name"] == "Critical - Immediate"
    assert result["probability"] == 0.6
    assert result["confidence"] == "medium" # 0.6 < 0.7 (high threshold)

def test_symptom_handling():
    svc = GoldenHourService()
    # Mock model
    class MockModel:
        def predict_proba(self, X):
            return np.array([[1.0, 0, 0, 0, 0]])
        feature_names_in_ = svc.feature_names
    svc.model = MockModel()

    # Test with string symptoms instead of list
    result = svc.predict_urgency("cough, fever", {"age": 30})
    assert result["urgency_level"] == 1
