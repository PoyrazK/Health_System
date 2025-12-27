"""
Healthcare AI Service - FastAPI Application
Main entry point with ML prediction and LLM integration endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import joblib
import json
import numpy as np
import os

# Initialize FastAPI
app = FastAPI(
    title="Healthcare AI API",
    description="Hibrit Zeka - ML Risk Engine & LLM Diagnosis Assistant",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .routers.llm_router import router as llm_router
from .routers.feedback_router import router as feedback_router
from .routers.ekg_router import router as ekg_router
from .routers.ekg_image_router import router as ekg_image_router

app.include_router(llm_router)
app.include_router(feedback_router)
app.include_router(ekg_router)
app.include_router(ekg_image_router)

# Model paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Load model and configs at startup
model = None
feature_columns = None
disease_encoding = None
label_to_disease = None

@app.on_event("startup")
async def load_model():
    global model, feature_columns, disease_encoding, label_to_disease
    
    model_path = os.path.join(MODEL_DIR, "disease_classifier.joblib")
    model = joblib.load(model_path)
    
    with open(os.path.join(MODEL_DIR, "feature_columns.json"), 'r') as f:
        feature_columns = json.load(f)
    
    with open(os.path.join(MODEL_DIR, "disease_encoding.json"), 'r') as f:
        disease_encoding = json.load(f)
    
    # Reverse mapping: label -> disease
    label_to_disease = {item['label']: item['disease'] for item in disease_encoding}
    
    print(f"✅ Model loaded: {len(feature_columns)} features, {len(label_to_disease)} diseases")


# ============================================
# Request/Response Models
# ============================================

class SymptomInput(BaseModel):
    """Input model for symptom-based prediction"""
    symptoms: List[str]  # List of symptom names
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["fever", "cough", "headache", "fatigue"]
            }
        }

class PredictionResult(BaseModel):
    """Output model for disease prediction"""
    top_predictions: List[Dict[str, Any]]
    risk_level: str
    confidence: float
    recommended_action: str

class HealthRiskInput(BaseModel):
    """Input model for risk assessment"""
    age: int
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    glucose: Optional[float] = None
    cholesterol: Optional[float] = None
    bmi: Optional[float] = None
    smoking: bool = False
    diabetes_history: bool = False
    symptoms: Optional[List[str]] = []

class RiskAssessmentResult(BaseModel):
    """Output model for risk assessment"""
    overall_risk_score: float
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]
    disease_predictions: Optional[List[Dict[str, Any]]] = None


# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Healthcare AI API",
        "version": "1.0.0"
    }

@app.get("/api/v1/model/info")
async def get_model_info():
    """Get model information"""
    model_info_path = os.path.join(MODEL_DIR, "model_info.json")
    with open(model_info_path, 'r') as f:
        info = json.load(f)
    return info

@app.get("/api/v1/symptoms")
async def get_available_symptoms():
    """Get list of available symptoms"""
    return {
        "total": len(feature_columns),
        "symptoms": feature_columns
    }

@app.post("/api/v1/predict/disease", response_model=PredictionResult)
async def predict_disease(input_data: SymptomInput):
    """
    Predict disease based on symptoms
    Returns top 5 most likely diseases with confidence scores
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Create feature vector
    feature_vector = np.zeros(len(feature_columns))
    
    matched_symptoms = []
    for symptom in input_data.symptoms:
        symptom_lower = symptom.lower().strip()
        for i, col in enumerate(feature_columns):
            if symptom_lower in col.lower() or col.lower() in symptom_lower:
                feature_vector[i] = 1
                matched_symptoms.append(col)
                break
    
    if len(matched_symptoms) == 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No matching symptoms found. Available symptoms: {feature_columns[:20]}..."
        )
    
    # Predict
    probabilities = model.predict_proba([feature_vector])[0]
    
    # Get top 5 predictions
    top_indices = np.argsort(probabilities)[-5:][::-1]
    top_predictions = []
    
    for idx in top_indices:
        disease = label_to_disease.get(idx, f"Unknown-{idx}")
        prob = float(probabilities[idx])
        top_predictions.append({
            "disease": disease,
            "probability": round(prob * 100, 2),
            "confidence": "high" if prob > 0.5 else "medium" if prob > 0.2 else "low"
        })
    
    # Determine overall risk level
    max_prob = probabilities[top_indices[0]]
    if max_prob > 0.7:
        risk_level = "HIGH"
        recommended_action = "Acil tıbbi değerlendirme önerilir"
    elif max_prob > 0.4:
        risk_level = "MEDIUM"
        recommended_action = "Doktor muayenesi önerilir"
    else:
        risk_level = "LOW"
        recommended_action = "Semptomları izlemeye devam edin"
    
    return PredictionResult(
        top_predictions=top_predictions,
        risk_level=risk_level,
        confidence=round(max_prob * 100, 2),
        recommended_action=recommended_action
    )

@app.post("/api/v1/predict/risk", response_model=RiskAssessmentResult)
async def assess_health_risk(input_data: HealthRiskInput):
    """
    Assess overall health risk based on vitals and symptoms
    Returns risk score and recommendations
    """
    risk_factors = []
    risk_score = 0.0
    
    # Age risk
    if input_data.age > 60:
        risk_score += 0.15
        risk_factors.append("Yaş 60 üzeri")
    elif input_data.age > 45:
        risk_score += 0.08
        risk_factors.append("Yaş 45-60 arası")
    
    # Blood pressure risk
    if input_data.blood_pressure_systolic:
        if input_data.blood_pressure_systolic > 140:
            risk_score += 0.2
            risk_factors.append("Yüksek tansiyon (sistolik > 140)")
        elif input_data.blood_pressure_systolic > 130:
            risk_score += 0.1
            risk_factors.append("Sınırda yüksek tansiyon")
    
    # Glucose risk
    if input_data.glucose:
        if input_data.glucose > 126:
            risk_score += 0.2
            risk_factors.append("Yüksek kan şekeri (Diyabet riski)")
        elif input_data.glucose > 100:
            risk_score += 0.1
            risk_factors.append("Pre-diyabet riski")
    
    # Cholesterol risk
    if input_data.cholesterol:
        if input_data.cholesterol > 240:
            risk_score += 0.15
            risk_factors.append("Yüksek kolesterol")
        elif input_data.cholesterol > 200:
            risk_score += 0.08
            risk_factors.append("Sınırda yüksek kolesterol")
    
    # BMI risk
    if input_data.bmi:
        if input_data.bmi > 30:
            risk_score += 0.15
            risk_factors.append("Obezite (BMI > 30)")
        elif input_data.bmi > 25:
            risk_score += 0.08
            risk_factors.append("Fazla kilo (BMI 25-30)")
    
    # Lifestyle risks
    if input_data.smoking:
        risk_score += 0.2
        risk_factors.append("Sigara kullanımı")
    
    if input_data.diabetes_history:
        risk_score += 0.15
        risk_factors.append("Diyabet öyküsü")
    
    # Cap at 1.0
    risk_score = min(risk_score, 1.0)
    
    # Determine risk level
    if risk_score > 0.6:
        risk_level = "HIGH"
    elif risk_score > 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Generate recommendations
    recommendations = []
    if "tansiyon" in str(risk_factors).lower():
        recommendations.append("Tuz tüketimini azaltın, düzenli egzersiz yapın")
    if "şeker" in str(risk_factors).lower() or "diyabet" in str(risk_factors).lower():
        recommendations.append("Şekerli gıdalardan kaçının, düzenli kan şekeri kontrolü yapın")
    if "kolesterol" in str(risk_factors).lower():
        recommendations.append("Doymuş yağ tüketimini azaltın, omega-3 alımını artırın")
    if "obezite" in str(risk_factors).lower() or "kilo" in str(risk_factors).lower():
        recommendations.append("Kalori alımını düzenleyin, haftada 150 dk aerobik egzersiz yapın")
    if "sigara" in str(risk_factors).lower():
        recommendations.append("Sigarayı bırakın - en önemli risk faktörlerinden biri")
    
    if len(recommendations) == 0:
        recommendations.append("Mevcut sağlıklı yaşam tarzınızı sürdürün")
    
    # Disease prediction if symptoms provided
    disease_predictions = None
    if input_data.symptoms and len(input_data.symptoms) > 0:
        try:
            symptom_input = SymptomInput(symptoms=input_data.symptoms)
            prediction_result = await predict_disease(symptom_input)
            disease_predictions = prediction_result.top_predictions
        except:
            pass
    
    return RiskAssessmentResult(
        overall_risk_score=round(risk_score * 100, 1),
        risk_level=risk_level,
        risk_factors=risk_factors if risk_factors else ["Risk faktörü tespit edilmedi"],
        recommendations=recommendations,
        disease_predictions=disease_predictions
    )


# ============================================
# Run server
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
