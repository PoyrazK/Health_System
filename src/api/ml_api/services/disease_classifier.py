import joblib
import json
import numpy as np
import pandas as pd
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

class DiseaseClassifier:
    """
    Symptom-based Disease Classifier with 527 diseases.
    Adapted from ai-models-v2 branch.
    """
    
    def __init__(self, model_dir: str = None):
        """Initialize the ML service with model directory"""
        if model_dir is None:
            # Assume models/disease relative to project root
            # Project Structure:
            # Healthcare System/
            #   models/
            #     disease/
            #   src/
            #     api/
            #       ml_api/
            #         services/
            #           disease_classifier.py
            
            # Use relative path from this file's location
            current_file = Path(__file__).resolve()
            # services/ -> ml_api/ -> api/ -> src/ -> ROOT/
            root_dir = current_file.parent.parent.parent.parent.parent
            model_dir = root_dir / "models" / "disease"
        
        self.model_dir = Path(model_dir)
        self.model = None
        self.feature_columns = None
        self.label_to_disease = None
        self.disease_to_label = None
        
        # Feedback log path
        self.feedback_log_path = self.model_dir / "feedback_log.csv"
        
        # Load model and configs
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and configurations"""
        model_path = self.model_dir / "disease_classifier_pruned.joblib"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Disease model not found at {model_path}")
        
        self.model = joblib.load(model_path)
        
        # Load feature columns
        with open(self.model_dir / "feature_columns.json", 'r') as f:
            self.feature_columns = json.load(f)
        
        # Load disease encoding
        with open(self.model_dir / "disease_encoding.json", 'r') as f:
            disease_encoding = json.load(f)
        
        self.label_to_disease = {item['label']: item['disease'] for item in disease_encoding}
        self.disease_to_label = {item['disease']: item['label'] for item in disease_encoding}
        
        print(f"✅ Disease Model loaded: {len(self.feature_columns)} features, {len(self.label_to_disease)} diseases")
    
    def predict_topk(self, symptoms: List[str], k: int = 3) -> List[Dict[str, Any]]:
        """
        Predict top K most likely diseases with probabilities.
        """
        # Create feature vector
        feature_vector = np.zeros(len(self.feature_columns))
        
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip()
            for i, col in enumerate(self.feature_columns):
                if symptom_lower in col.lower() or col.lower() in symptom_lower:
                    feature_vector[i] = 1
                    break
        
        # Get probabilities
        probabilities = self.model.predict_proba([feature_vector])[0]
        
        # Get top K indices
        topk_indices = np.argsort(probabilities)[-k:][::-1]
        
        # Create result
        results = []
        for idx in topk_indices:
            disease = self.label_to_disease.get(idx, f"Unknown-{idx}")
            prob = float(probabilities[idx])
            results.append({
                "disease": disease,
                "probability": round(prob * 100, 2),
                "confidence": "high" if prob > 0.5 else "medium" if prob > 0.2 else "low"
            })
        
        return results

    def log_feedback(
        self,
        symptoms: List[str],
        confirmed_diagnosis: str,
        doctor_id: str = None,
        notes: str = None
    ) -> bool:
        """Log doctor feedback for future retraining"""
        # Build log entry
        log_entry = {}
        
        # Minimal data for log - just symptoms and diagnosis
        log_entry["symptoms"] = json.dumps(symptoms)
        log_entry["confirmed_diagnosis"] = confirmed_diagnosis
        log_entry["doctor_id"] = doctor_id or ""
        log_entry["notes"] = notes or ""
        log_entry["timestamp"] = datetime.now().isoformat()
        
        # Append to CSV
        log_df = pd.DataFrame([log_entry])
        
        if self.feedback_log_path.exists():
            log_df.to_csv(self.feedback_log_path, mode='a', header=False, index=False)
        else:
            log_df.to_csv(self.feedback_log_path, index=False)
        
        return True
