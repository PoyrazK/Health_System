import pytest
from fastapi.testclient import TestClient
from src.api.ml_api.main import app
import os

client = TestClient(app)

def test_diagnose_patient_mock():
    # Ensure OPENAI_API_KEY is not set to test mock behavior if that's the intention, 
    # or just test that it returns a valid structure.
    payload = {
        "patient": {
            "age": 45,
            "gender": "Male",
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "glucose": 100,
            "bmi": 24.5
        },
        "risk_scores": {
            "heart_risk": 15.5,
            "diabetes_risk": 10.2
        },
        "past_context": "Previous stable readings."
    }
    response = client.post("/diagnose", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "diagnosis" in data
    assert "status" in data
    assert isinstance(data["diagnosis"], str)
    assert len(data["diagnosis"]) > 0

def test_diagnose_missing_fields():
    payload = {
        "patient": {
            "age": 45
        }
    }
    response = client.post("/diagnose", json=payload)
    # Depending on pydantic validation, this should fail or return 422
    assert response.status_code == 422
