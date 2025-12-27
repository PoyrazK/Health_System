"""
EKG Image Router - API endpoints for image-based EKG analysis
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import base64

from ..services.ekg_image_analyzer import get_image_analyzer

router = APIRouter(prefix="/api/v1/ekg-image", tags=["EKG Image Analysis"])


@router.post("/analyze")
async def analyze_ekg_image(file: UploadFile = File(...)):
    """
    EKG görselinden analiz yap
    
    Desteklenen formatlar: PNG, JPG, JPEG
    
    Returns:
        - Sinyal özellikleri (heart rate, RR intervals)
        - Tahmin (N/S/V/F/Q)
        - Aciliyet seviyesi
        - Öneri
    """
    # Dosya kontrolü
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Sadece gorsel dosyalari desteklenir (PNG, JPG)"
        )
    
    try:
        # Dosyayı oku
        content = await file.read()
        
        # Analiz yap
        analyzer = get_image_analyzer()
        result = analyzer.analyze_image_bytes(content)
        
        if result.get('status') == 'error':
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Analiz hatasi')
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-base64")
async def analyze_ekg_base64(data: dict):
    """
    Base64 encoded EKG görselinden analiz yap
    
    Request body:
    {
        "image": "base64_encoded_image_string"
    }
    """
    try:
        image_b64 = data.get('image', '')
        
        if not image_b64:
            raise HTTPException(
                status_code=400,
                detail="'image' alani gerekli"
            )
        
        # Base64 decode
        image_bytes = base64.b64decode(image_b64)
        
        # Analiz yap
        analyzer = get_image_analyzer()
        result = analyzer.analyze_image_bytes(image_bytes)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def image_analyzer_health():
    """Image analyzer sağlık kontrolü"""
    analyzer = get_image_analyzer()
    
    return {
        "status": "available",
        "model_loaded": analyzer.model is not None,
        "scaler_loaded": analyzer.scaler is not None,
        "supported_formats": ["PNG", "JPG", "JPEG"],
        "classes": list(analyzer.urgency_levels.keys()) if analyzer.urgency_levels else []
    }
