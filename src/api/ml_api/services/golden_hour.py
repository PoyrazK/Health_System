import joblib
import json
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
from src.api.ml_api.config.urgency_mapping import get_urgency, get_golden_hour

class GoldenHourService:
    """
    Service for predicting medical urgency and golden hour intervention times.
    Uses XGBoost multi-class classifier.
    """
    
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            current_file = Path(__file__).resolve()
            root_dir = current_file.parent.parent.parent.parent.parent
            model_dir = root_dir / "src" / "api" / "ml_api" / "models" / "golden_hour"
        
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.artifacts = None
        self.feature_names = None
        self.reverse_label_map = None
        self.urgency_descriptions = None
        
        self._load_model()

    def _load_model(self):
        """Load XGBoost model and associated scaling artifacts"""
        model_path = self.model_dir / "golden_hour_model.pkl"
        scaler_path = self.model_dir / "golden_hour_scaler.pkl"
        artifacts_path = self.model_dir / "golden_hour_artifacts.pkl"
        
        if not all([p.exists() for p in [model_path, scaler_path, artifacts_path]]):
            raise FileNotFoundError(f"Golden Hour model components missing in {self.model_dir}")
            
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.artifacts = joblib.load(artifacts_path)
        
        self.feature_names = self.artifacts['feature_names']
        self.reverse_label_map = self.artifacts['reverse_map']
        self.urgency_descriptions = self.artifacts.get('urgency_descriptions', {
            5: 'Critical - Immediate',
            4: 'Emergent - Hours',
            3: 'Urgent - 24 hours',
            2: 'Standard - 2-3 days',
            1: 'Elective - Scheduled'
        })
        
        print(f"✅ Golden Hour Model loaded: {len(self.feature_names)} features, {len(self.reverse_label_map)} classes")

    def predict_urgency(self, symptoms: List[str], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict urgency level based on symptoms and vitals.
        Returns urgency level, name, and golden hour minutes.
        """
        # Handle string symptoms
        if isinstance(symptoms, str):
            symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]

        # 1. Prepare feature vector (same as training)
        X = pd.DataFrame(np.zeros((1, len(self.feature_names))), columns=self.feature_names)
        
        # Map patient_data (vitals) to features
        # Training feature names usually match PatientData fields (lowercase)
        vitals_mapping = {
            "age": "Age",
            "systolic_bp": "SystolicBP",
            "diastolic_bp": "DiastolicBP",
            "glucose": "Glucose",
            "bmi": "BMI",
            "cholesterol": "Cholesterol",
            "heart_rate": "HeartRate"
        }
        
        for key, feat in vitals_mapping.items():
            if key in patient_data and feat in self.feature_names:
                X.at[0, feat] = patient_data[key]
        
        # Map symptoms to binary features
        for symptom in symptoms:
            s_clean = symptom.lower().strip()
            # Find matching symptom columns
            for col in self.feature_names:
                if s_clean in col.lower() or col.lower() in s_clean:
                    X.at[0, col] = 1
                    
        # 2. Scale and Predict
        X_scaled = self.scaler.transform(X.values)
        probs = self.model.predict_proba(X_scaled)[0]
        label_idx = np.argmax(probs)
        prob = float(probs[label_idx])
        
        # 3. Handle label mapping
        # reverse_label_map maps 0-indexed to urgency levels (1-5)
        # Note: reverse_label_map keys might be strings in joblib
        urgency_level = int(self.reverse_label_map.get(label_idx, label_idx))
        
        return {
            "urgency_level": urgency_level,
            "urgency_name": self.urgency_descriptions.get(urgency_level, "Unknown"),
            "probability": round(prob, 4),
            "confidence": "high" if prob > 0.7 else "medium" if prob > 0.4 else "low"
        }

    def get_clinical_urgency(self, disease_name: str) -> Dict[str, Any]:
        """Get pre-mapped urgency and golden hour for a confirmed disease"""
        return {
            "urgency": get_urgency(disease_name),
            "golden_hour": get_golden_hour(disease_name),
            "description": self.urgency_descriptions.get(get_urgency(disease_name), "Unknown")
        }
