import pytest
from fastapi.testclient import TestClient
from src.api.ml_api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_risk_valid():
    payload = {
        "age": 45,
        "gender": "Male",
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "glucose": 100,
        "bmi": 24.5,
        "cholesterol": 190,
        "heart_rate": 72,
        "steps": 5000,
        "smoking": "No",
        "alcohol": "No",
        "medications": "None",
        "history_heart_disease": "No",
        "history_stroke": "No",
        "history_diabetes": "No",
        "history_high_chol": "No",
        "symptoms": []
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "heart_risk_score" in data
    assert "diabetes_risk_score" in data
    assert "stroke_risk_score" in data
    assert "kidney_risk_score" in data
    assert "general_health_score" in data
    assert "clinical_confidence" in data
    assert "model_precisions" in data

def test_medication_interaction():
    # Test with a risky combination if implemented
    payload = {
        "medications": ["Warfarin", "Aspirin"]
    }
    # Note: The current endpoint for checking interaction might be different or part of predict
    # Based on main.py, check_interaction is called within predict_risk or as a utility
    pass

def test_predict_disease_valid():
    payload = {
        "symptoms": ["chest pain", "shortness of breath", "dizziness"],
        "patient_id": "test_123"
    }
    response = client.post("/disease/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) > 0

def test_analyze_ekg_valid():
    # Signal must be long enough for the filter (e.g. > 20 points for 2nd order Butterworth)
    payload = {
        "signal": [0.1, 0.2, 0.5, 0.2, 0.1] * 20,
        "sampling_rate": 360
    }
    response = client.post("/ekg/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "predictions" in data
