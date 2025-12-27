"""
LLM Router - API endpoints for LLM-based services
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ..services.llm_service import llm_service

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


# ============================================
# Request/Response Models
# ============================================

class DiagnosisReportRequest(BaseModel):
    patient_data: Dict[str, Any]
    symptoms: List[str]
    ml_predictions: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_data": {"age": 45, "gender": "male", "bmi": 28.5},
                "symptoms": ["chest pain", "shortness of breath", "fatigue"],
                "ml_predictions": [
                    {"disease": "Coronary artery disease", "probability": 65.2}
                ],
                "risk_assessment": {
                    "overall_risk_score": 72.5,
                    "risk_level": "HIGH",
                    "risk_factors": ["Yüksek tansiyon", "Sigara kullanımı"],
                    "recommendations": ["Kardiyoloji konsültasyonu"]
                }
            }
        }

class PatientExplanationRequest(BaseModel):
    lab_results: Dict[str, Any]
    language_level: str = "simple"
    
    class Config:
        json_schema_extra = {
            "example": {
                "lab_results": {
                    "glucose": 115,
                    "cholesterol": 210,
                    "creatinine": 1.1,
                    "hemoglobin": 14.2
                },
                "language_level": "simple"
            }
        }

class DrugInteractionRequest(BaseModel):
    current_medications: List[str]
    new_medication: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_medications": ["Aspirin", "Metformin", "Lisinopril"],
                "new_medication": "Warfarin"
            }
        }


# ============================================
# Endpoints
# ============================================

@router.post("/diagnose")
async def generate_diagnosis_report(request: DiagnosisReportRequest):
    """
    Generate AI-powered diagnosis report for doctors
    Combines ML predictions with LLM medical reasoning
    """
    result = await llm_service.generate_diagnosis_report(
        patient_data=request.patient_data,
        symptoms=request.symptoms,
        ml_predictions=request.ml_predictions,
        risk_assessment=request.risk_assessment
    )
    return result

@router.post("/explain-lab-results")
async def explain_lab_results(request: PatientExplanationRequest):
    """
    Translate lab results into patient-friendly language
    """
    result = await llm_service.generate_patient_explanation(
        lab_results=request.lab_results,
        patient_language_level=request.language_level
    )
    return result

@router.post("/check-drug-interaction")
async def check_drug_interaction(request: DrugInteractionRequest):
    """
    Check for potential drug interactions before prescribing
    """
    result = await llm_service.check_drug_interactions(
        current_medications=request.current_medications,
        new_medication=request.new_medication
    )
    return result

@router.get("/health")
async def llm_health_check():
    """Check if LLM service is available"""
    import os
    api_key_set = bool(os.getenv("GEMINI_API_KEY", ""))
    return {
        "status": "available" if api_key_set else "unavailable",
        "api_key_configured": api_key_set,
        "model": "gemini-1.5-flash"
    }
