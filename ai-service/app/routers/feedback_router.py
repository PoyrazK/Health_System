"""
Feedback Router - API endpoints for physician feedback and model retraining
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..services.ml_service import get_ml_service

router = APIRouter(prefix="/api/v1/feedback", tags=["Feedback & Learning"])


# ============================================
# Request/Response Models
# ============================================

class Top3PredictionRequest(BaseModel):
    symptoms: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["fever", "cough", "headache", "fatigue"]
            }
        }

class Top3PredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    timestamp: str

class FeedbackRequest(BaseModel):
    patient_data: Dict[str, Any]
    model_predictions: List[str]
    confirmed_diagnosis: str
    doctor_id: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_data": {"symptoms": ["fever", "cough", "headache"]},
                "model_predictions": ["white blood cell disease", "mononucleosis", "strep throat"],
                "confirmed_diagnosis": "mononucleosis",
                "doctor_id": "dr_001",
                "notes": "Patient had additional symptoms not captured"
            }
        }

class RetrainRequest(BaseModel):
    min_samples: int = 50
    test_size: float = 0.2
    save_new_version: bool = True


# ============================================
# Endpoints
# ============================================

@router.post("/predict-top3", response_model=Top3PredictionResponse)
async def predict_top3(request: Top3PredictionRequest):
    """
    Get top 3 disease predictions with probabilities.
    Returns ranked list of most likely diagnoses.
    """
    try:
        service = get_ml_service()
        top3 = service.predict_top3({"symptoms": request.symptoms})
        
        predictions = [
            {"rank": i+1, "disease": disease, "probability": prob}
            for i, (disease, prob) in enumerate(top3)
        ]
        
        return Top3PredictionResponse(
            predictions=predictions,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-topk")
async def predict_topk(request: Top3PredictionRequest, k: int = 5):
    """
    Get top K disease predictions with probabilities.
    """
    try:
        service = get_ml_service()
        topk = service.predict_topk({"symptoms": request.symptoms}, k=k)
        
        predictions = [
            {"rank": i+1, "disease": disease, "probability": prob}
            for i, (disease, prob) in enumerate(topk)
        ]
        
        return {
            "predictions": predictions,
            "k": k,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log")
async def log_feedback(request: FeedbackRequest):
    """
    Log physician feedback for learning loop.
    Records the confirmed diagnosis against model predictions.
    """
    try:
        service = get_ml_service()
        success = service.log_feedback(
            patient_data=request.patient_data,
            model_prediction=request.model_predictions,
            confirmed_diagnosis=request.confirmed_diagnosis,
            doctor_id=request.doctor_id,
            notes=request.notes
        )
        
        return {
            "success": success,
            "message": "Feedback logged successfully",
            "confirmed_diagnosis": request.confirmed_diagnosis,
            "model_was_correct": request.confirmed_diagnosis in request.model_predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_feedback_stats():
    """
    Get statistics from feedback log.
    Shows model accuracy based on physician corrections.
    """
    try:
        service = get_ml_service()
        stats = service.get_feedback_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain")
async def retrain_model(request: RetrainRequest):
    """
    Retrain model using accumulated feedback data.
    Requires minimum samples to prevent overfitting.
    """
    try:
        service = get_ml_service()
        result = service.retrain_from_feedback(
            min_samples=request.min_samples,
            test_size=request.test_size,
            save_new_version=request.save_new_version
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions")
async def list_model_versions():
    """
    List all available model versions for rollback.
    """
    try:
        service = get_ml_service()
        versions = service.list_versions()
        return {
            "versions": versions,
            "total": len(versions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback/{version_name}")
async def rollback_model(version_name: str):
    """
    Rollback to a previous model version.
    """
    try:
        service = get_ml_service()
        success = service.rollback_model(version_name)
        
        if success:
            return {
                "success": True,
                "message": f"Rolled back to {version_name}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Version not found: {version_name}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
