import pytest
from src.api.ml_api.services.disease_classifier import DiseaseClassifier
import numpy as np

def test_disease_logic():
    svc = DiseaseClassifier()
    # Mock symptoms and data
    svc.disease_data = {
        "Common Cold": ["cough", "fever", "sneezing"],
        "Flu": ["fever", "chills", "muscle_pain"]
    }
    svc.all_symptoms = ["cough", "fever", "sneezing", "chills", "muscle_pain"]
    
    # Mock model
    class MockModel:
        def predict_proba(self, X):
            # Return high prob for "Flu" if fever is present
            return np.array([[0.1, 0.9]])
        
        @property
        def classes_(self):
            return ["Common Cold", "Flu"]

    svc.model = MockModel()
    svc.label_to_disease = {0: "Common Cold", 1: "Flu"}
    
    results = svc.predict_topk(["fever", "chills"])
    
    assert len(results) > 0
    assert results[0]["disease"] == "Flu"
    assert results[0]["probability"] == 90.0 # Implementation scales by 100

def test_empty_symptoms():
    svc = DiseaseClassifier()
    # It will still predict something based on priors, but we check it doesn't crash
    results = svc.predict_topk([])
    assert len(results) == 3
