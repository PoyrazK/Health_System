"""
EKG Router - API endpoints for EKG signal analysis
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
import base64
import json

from ..services.ekg_service import get_ekg_service

router = APIRouter(prefix="/api/v1/ekg", tags=["EKG Analysis"])


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class EKGAnalysisRequest(BaseModel):
    """Request model for EKG analysis"""
    signal: List[float]  # EKG signal as list of values
    sampling_rate: int = 360  # Hz
    
    class Config:
        json_schema_extra = {
            "example": {
                "signal": [0.1, 0.2, 0.5, 0.8, 0.6, 0.3, 0.1] * 100,
                "sampling_rate": 360
            }
        }

class EKGFeedbackRequest(BaseModel):
    """Request model for EKG feedback"""
    signal: List[float]
    model_prediction: str
    confirmed_diagnosis: str
    doctor_id: Optional[str] = None


# ==========================================
# ENDPOINTS
# ==========================================

@router.post("/analyze")
async def analyze_ekg(request: EKGAnalysisRequest):
    """
    Analyze EKG signal for cardiac anomalies
    Returns predictions for arrhythmia, MI, etc.
    """
    try:
        service = get_ekg_service()
        signal = np.array(request.signal)
        
        if len(signal) < 100:
            raise HTTPException(
                status_code=400,
                detail="Signal too short. Minimum 100 samples required."
            )
        
        result = service.analyze(signal, request.sampling_rate)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-file")
async def analyze_ekg_file(file: UploadFile = File(...)):
    """
    Analyze EKG from uploaded file (CSV, TXT, or binary)
    """
    try:
        content = await file.read()
        
        # Try to parse as CSV/TXT
        try:
            text = content.decode('utf-8')
            signal = np.array([float(x.strip()) for x in text.split('\n') if x.strip()])
        except:
            # Try as binary numpy array
            signal = np.frombuffer(content, dtype=np.float32)
        
        service = get_ekg_service()
        result = service.analyze(signal)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def log_ekg_feedback(request: EKGFeedbackRequest):
    """
    Log physician feedback for EKG analysis
    """
    try:
        service = get_ekg_service()
        signal = np.array(request.signal)
        
        success = service.log_feedback(
            signal=signal,
            model_prediction=request.model_prediction,
            confirmed_diagnosis=request.confirmed_diagnosis,
            doctor_id=request.doctor_id
        )
        
        return {
            "success": success,
            "message": "EKG feedback logged successfully",
            "confirmed_diagnosis": request.confirmed_diagnosis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo")
async def get_demo_signal():
    """
    Get a demo EKG signal for testing
    """
    # Generate synthetic normal sinus rhythm
    t = np.linspace(0, 3, 1080)  # 3 seconds at 360 Hz
    
    # P wave, QRS complex, T wave pattern
    signal = np.zeros_like(t)
    for i in range(3):  # 3 heartbeats
        beat_start = i * 360
        # P wave
        signal[beat_start+50:beat_start+100] = 0.2 * np.sin(np.linspace(0, np.pi, 50))
        # QRS complex
        signal[beat_start+150:beat_start+180] = np.array([0, 0.3, 1.0, -0.4, 0.1] * 6)[:30]
        # T wave
        signal[beat_start+220:beat_start+300] = 0.3 * np.sin(np.linspace(0, np.pi, 80))
    
    # Add noise
    signal += np.random.normal(0, 0.05, len(signal))
    
    return {
        "signal": signal.tolist(),
        "sampling_rate": 360,
        "duration_seconds": 3,
        "description": "Demo normal sinus rhythm"
    }

@router.get("/health")
async def ekg_health_check():
    """Check if EKG service is available"""
    service = get_ekg_service()
    
    return {
        "status": "available",
        "model_loaded": service.model is not None,
        "mode": "ML" if service.model else "rule-based"
    }
