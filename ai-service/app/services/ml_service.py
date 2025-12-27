"""
Healthcare AI System - Enhanced ML Service
Features:
1. Top-3 Ranked Disease Prediction
2. Physician Feedback Logging (Learning Loop)
3. Incremental Learning Support
4. Modular Interface Functions
"""

import joblib
import json
import numpy as np
import pandas as pd
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import shutil


class EnhancedMLService:
    """
    Enhanced ML Service with feedback loop and incremental learning
    """
    
    def __init__(self, model_dir: str = None):
        """Initialize the ML service with model directory"""
        if model_dir is None:
            # services -> app -> ai-service -> models -> disease
            current_dir = os.path.dirname(os.path.abspath(__file__))  # services
            app_dir = os.path.dirname(current_dir)  # app
            ai_service_dir = os.path.dirname(app_dir)  # ai-service
            models_dir = os.path.join(ai_service_dir, "models")
            model_dir = os.path.join(models_dir, "disease")  # disease subfolder
        
        self.model_dir = model_dir
        self.model = None
        self.feature_columns = None
        self.label_to_disease = None
        self.disease_to_label = None
        
        # Feedback log path
        self.feedback_log_path = os.path.join(model_dir, "feedback_log.csv")
        
        # Model versions directory
        self.versions_dir = os.path.join(model_dir, "versions")
        os.makedirs(self.versions_dir, exist_ok=True)
        
        # Load model and configs
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and configurations"""
        # Use pruned model (28.6 MB) instead of full model (103.7 MB) - same accuracy
        model_path = os.path.join(self.model_dir, "disease_classifier_pruned.joblib")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.model = joblib.load(model_path)
        
        # Load feature columns
        with open(os.path.join(self.model_dir, "feature_columns.json"), 'r') as f:
            self.feature_columns = json.load(f)
        
        # Load disease encoding
        with open(os.path.join(self.model_dir, "disease_encoding.json"), 'r') as f:
            disease_encoding = json.load(f)
        
        self.label_to_disease = {item['label']: item['disease'] for item in disease_encoding}
        self.disease_to_label = {item['disease']: item['label'] for item in disease_encoding}
        
        print(f"✅ Model loaded: {len(self.feature_columns)} features, {len(self.label_to_disease)} diseases")
    
    # ========================================
    # 1. TOP-3 RANKED DISEASE PREDICTION
    # ========================================
    
    def predict_top3(self, patient_data: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        Predict top 3 most likely diseases with probabilities.
        
        Args:
            patient_data: Dictionary containing symptoms as keys with binary values (0/1)
                          OR list of symptom names
        
        Returns:
            List of tuples: [(Disease_1, Confidence_1), (Disease_2, Confidence_2), (Disease_3, Confidence_3)]
        """
        # Create feature vector
        feature_vector = self._create_feature_vector(patient_data)
        
        # Get probabilities
        probabilities = self.model.predict_proba([feature_vector])[0]
        
        # Get top 3 indices
        top3_indices = np.argsort(probabilities)[-3:][::-1]
        
        # Create result
        results = []
        for idx in top3_indices:
            disease = self.label_to_disease.get(idx, f"Unknown-{idx}")
            prob = float(probabilities[idx])
            results.append((disease, round(prob * 100, 2)))
        
        return results
    
    def predict_topk(self, patient_data: Dict[str, Any], k: int = 5) -> List[Tuple[str, float]]:
        """
        Predict top K most likely diseases with probabilities.
        
        Args:
            patient_data: Dictionary containing symptoms
            k: Number of top predictions to return
        
        Returns:
            List of tuples: [(Disease, Confidence), ...]
        """
        feature_vector = self._create_feature_vector(patient_data)
        probabilities = self.model.predict_proba([feature_vector])[0]
        
        topk_indices = np.argsort(probabilities)[-k:][::-1]
        
        results = []
        for idx in topk_indices:
            disease = self.label_to_disease.get(idx, f"Unknown-{idx}")
            prob = float(probabilities[idx])
            results.append((disease, round(prob * 100, 2)))
        
        return results
    
    def _create_feature_vector(self, patient_data: Dict[str, Any]) -> np.ndarray:
        """
        Create feature vector from patient data.
        
        Args:
            patient_data: Can be:
                - {"symptoms": ["fever", "cough"]} - list of symptom names
                - {"fever": 1, "cough": 1} - binary symptom values
        """
        feature_vector = np.zeros(len(self.feature_columns))
        
        # Check if symptoms are provided as a list
        if "symptoms" in patient_data:
            symptoms = patient_data["symptoms"]
            for symptom in symptoms:
                symptom_lower = symptom.lower().strip()
                for i, col in enumerate(self.feature_columns):
                    if symptom_lower in col.lower() or col.lower() in symptom_lower:
                        feature_vector[i] = 1
                        break
        else:
            # Symptoms provided as binary dictionary
            for i, col in enumerate(self.feature_columns):
                if col in patient_data:
                    feature_vector[i] = patient_data[col]
        
        return feature_vector
    
    # ========================================
    # 2. PHYSICIAN FEEDBACK LOGGING
    # ========================================
    
    def log_feedback(
        self,
        patient_data: Dict[str, Any],
        model_prediction: List[str],
        confirmed_diagnosis: str,
        doctor_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Log physician feedback for learning loop.
        
        Args:
            patient_data: Original input features
            model_prediction: List of model's top predictions
            confirmed_diagnosis: Doctor's confirmed diagnosis
            doctor_id: Optional doctor identifier
            notes: Optional notes from doctor
        
        Returns:
            True if logged successfully
        """
        # Create feature vector for storage
        feature_vector = self._create_feature_vector(patient_data)
        
        # Build log entry
        log_entry = {}
        
        # Add all features
        for i, col in enumerate(self.feature_columns):
            log_entry[col] = int(feature_vector[i])
        
        # Add metadata
        log_entry["model_top_prediction"] = model_prediction[0] if model_prediction else ""
        log_entry["model_predictions_json"] = json.dumps(model_prediction)
        log_entry["confirmed_diagnosis"] = confirmed_diagnosis
        log_entry["doctor_id"] = doctor_id or ""
        log_entry["notes"] = notes or ""
        log_entry["timestamp"] = datetime.now().isoformat()
        log_entry["model_correct"] = 1 if confirmed_diagnosis in model_prediction else 0
        
        # Create or append to feedback log
        log_df = pd.DataFrame([log_entry])
        
        if os.path.exists(self.feedback_log_path):
            log_df.to_csv(self.feedback_log_path, mode='a', header=False, index=False)
        else:
            log_df.to_csv(self.feedback_log_path, index=False)
        
        print(f"✅ Feedback logged: {confirmed_diagnosis} (Model correct: {log_entry['model_correct']})")
        return True
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get statistics from feedback log.
        
        Returns:
            Dictionary with feedback statistics
        """
        if not os.path.exists(self.feedback_log_path):
            return {"total_feedbacks": 0, "message": "No feedback data yet"}
        
        df = pd.read_csv(self.feedback_log_path)
        
        total = len(df)
        correct = df["model_correct"].sum()
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Top confirmed diagnoses
        top_diagnoses = df["confirmed_diagnosis"].value_counts().head(10).to_dict()
        
        # Recent feedbacks
        recent = df.tail(5)[["confirmed_diagnosis", "model_top_prediction", "model_correct", "timestamp"]].to_dict('records')
        
        return {
            "total_feedbacks": total,
            "correct_predictions": int(correct),
            "feedback_accuracy": round(accuracy, 2),
            "top_confirmed_diagnoses": top_diagnoses,
            "recent_feedbacks": recent
        }
    
    # ========================================
    # 3. INCREMENTAL LEARNING SUPPORT
    # ========================================
    
    def retrain_from_feedback(
        self,
        feedback_path: Optional[str] = None,
        min_samples: int = 50,
        test_size: float = 0.2,
        save_new_version: bool = True
    ) -> Dict[str, Any]:
        """
        Retrain or fine-tune model based on feedback data.
        
        Args:
            feedback_path: Path to feedback CSV (uses default if None)
            min_samples: Minimum samples required for retraining
            test_size: Test split ratio for validation
            save_new_version: Whether to save as new version
        
        Returns:
            Dictionary with retraining results
        """
        feedback_path = feedback_path or self.feedback_log_path
        
        if not os.path.exists(feedback_path):
            return {"success": False, "error": "No feedback data available"}
        
        # Load feedback data
        feedback_df = pd.read_csv(feedback_path)
        
        if len(feedback_df) < min_samples:
            return {
                "success": False,
                "error": f"Insufficient samples ({len(feedback_df)} < {min_samples})"
            }
        
        print(f"📊 Retraining with {len(feedback_df)} feedback samples...")
        
        # Prepare features and labels
        X_feedback = feedback_df[self.feature_columns].values
        
        # Encode confirmed diagnoses
        y_feedback = []
        valid_indices = []
        
        for i, diagnosis in enumerate(feedback_df["confirmed_diagnosis"]):
            if diagnosis in self.disease_to_label:
                y_feedback.append(self.disease_to_label[diagnosis])
                valid_indices.append(i)
            else:
                print(f"⚠️ Unknown diagnosis skipped: {diagnosis}")
        
        if len(y_feedback) < min_samples:
            return {
                "success": False,
                "error": f"Insufficient valid samples after filtering ({len(y_feedback)} < {min_samples})"
            }
        
        X_feedback = X_feedback[valid_indices]
        y_feedback = np.array(y_feedback)
        
        # Split for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X_feedback, y_feedback,
            test_size=test_size,
            random_state=42,
            stratify=y_feedback if len(np.unique(y_feedback)) > 1 else None
        )
        
        # Save current model as backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.versions_dir, f"model_backup_{timestamp}.joblib")
        joblib.dump(self.model, backup_path)
        print(f"💾 Backup saved: {backup_path}")
        
        # Get current model accuracy on feedback data
        old_predictions = self.model.predict(X_test)
        old_accuracy = accuracy_score(y_test, old_predictions)
        print(f"📈 Old model accuracy on feedback: {old_accuracy:.4f}")
        
        # Fine-tune model (incremental training)
        # For XGBoost, we'll continue training from existing model
        self.model.fit(
            X_train, y_train,
            xgb_model=self.model.get_booster(),  # Continue from existing model
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate new model
        new_predictions = self.model.predict(X_test)
        new_accuracy = accuracy_score(y_test, new_predictions)
        print(f"📈 New model accuracy on feedback: {new_accuracy:.4f}")
        
        improvement = new_accuracy - old_accuracy
        
        # Save new version if improvement or requested
        if save_new_version:
            new_version_path = os.path.join(self.versions_dir, f"model_v_{timestamp}.joblib")
            joblib.dump(self.model, new_version_path)
            
            # Also update main model
            main_model_path = os.path.join(self.model_dir, "disease_classifier.joblib")
            joblib.dump(self.model, main_model_path)
            
            print(f"✅ New model saved: {new_version_path}")
        
        # Update model info
        model_info_path = os.path.join(self.model_dir, "model_info.json")
        with open(model_info_path, 'r') as f:
            model_info = json.load(f)
        
        model_info["last_retrained"] = timestamp
        model_info["feedback_samples_used"] = len(y_feedback)
        model_info["feedback_accuracy"] = float(new_accuracy)
        
        with open(model_info_path, 'w') as f:
            json.dump(model_info, f, indent=2)
        
        return {
            "success": True,
            "old_accuracy": round(old_accuracy * 100, 2),
            "new_accuracy": round(new_accuracy * 100, 2),
            "improvement": round(improvement * 100, 2),
            "samples_used": len(y_feedback),
            "new_version": f"model_v_{timestamp}.joblib" if save_new_version else None,
            "backup": backup_path
        }
    
    def rollback_model(self, version_name: str) -> bool:
        """
        Rollback to a previous model version.
        
        Args:
            version_name: Name of the version file to rollback to
        
        Returns:
            True if rollback successful
        """
        version_path = os.path.join(self.versions_dir, version_name)
        
        if not os.path.exists(version_path):
            print(f"❌ Version not found: {version_name}")
            return False
        
        # Load the old version
        self.model = joblib.load(version_path)
        
        # Save as main model
        main_path = os.path.join(self.model_dir, "disease_classifier.joblib")
        joblib.dump(self.model, main_path)
        
        print(f"✅ Rolled back to: {version_name}")
        return True
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all available model versions"""
        versions = []
        
        for filename in os.listdir(self.versions_dir):
            if filename.endswith(".joblib"):
                filepath = os.path.join(self.versions_dir, filename)
                stat = os.stat(filepath)
                versions.append({
                    "name": filename,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(versions, key=lambda x: x["created"], reverse=True)


# ========================================
# SINGLETON INSTANCE
# ========================================

_ml_service = None

def get_ml_service(model_dir: str = None) -> EnhancedMLService:
    """Get or create the ML service singleton"""
    global _ml_service
    if _ml_service is None:
        _ml_service = EnhancedMLService(model_dir)
    return _ml_service


# ========================================
# INTERFACE FUNCTIONS (For API wrapping)
# ========================================

def predict_top3(patient_data: Dict[str, Any]) -> List[Tuple[str, float]]:
    """
    Predict top 3 diseases with probabilities.
    
    Example:
        >>> predict_top3({"symptoms": ["fever", "cough", "headache"]})
        [("Influenza", 75.5), ("Common Cold", 12.3), ("COVID-19", 8.2)]
    """
    return get_ml_service().predict_top3(patient_data)


def log_feedback(
    patient_data: Dict[str, Any],
    model_prediction: List[str],
    confirmed_diagnosis: str,
    doctor_id: str = None,
    notes: str = None
) -> bool:
    """
    Log physician feedback for learning loop.
    
    Example:
        >>> log_feedback(
        ...     patient_data={"symptoms": ["fever", "cough"]},
        ...     model_prediction=["Influenza", "Common Cold", "COVID-19"],
        ...     confirmed_diagnosis="Influenza"
        ... )
        True
    """
    return get_ml_service().log_feedback(
        patient_data, model_prediction, confirmed_diagnosis, doctor_id, notes
    )


def retrain_from_feedback(feedback_path: str = None) -> Dict[str, Any]:
    """
    Retrain model using accumulated feedback data.
    
    Example:
        >>> result = retrain_from_feedback()
        >>> print(result)
        {"success": True, "old_accuracy": 85.0, "new_accuracy": 87.5, ...}
    """
    return get_ml_service().retrain_from_feedback(feedback_path)


# ========================================
# QUICK TEST
# ========================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ENHANCED ML SERVICE TEST")
    print("=" * 60)
    
    # Initialize service
    service = get_ml_service()
    
    # Test 1: Top-3 prediction
    print("\n📊 Test 1: Top-3 Prediction")
    test_data = {"symptoms": ["fever", "cough", "headache", "fatigue"]}
    top3 = predict_top3(test_data)
    print(f"Input: {test_data}")
    print(f"Top 3 Predictions:")
    for i, (disease, prob) in enumerate(top3, 1):
        print(f"  {i}. {disease}: {prob}%")
    
    # Test 2: Feedback logging
    print("\n📝 Test 2: Feedback Logging")
    log_feedback(
        patient_data=test_data,
        model_prediction=[d for d, p in top3],
        confirmed_diagnosis=top3[0][0],  # Simulating doctor confirming top prediction
        doctor_id="test_doctor",
        notes="Test feedback entry"
    )
    
    # Test 3: Get feedback stats
    print("\n📈 Test 3: Feedback Statistics")
    stats = service.get_feedback_stats()
    print(json.dumps(stats, indent=2))
    
    # Test 4: List versions
    print("\n📁 Test 4: Model Versions")
    versions = service.list_versions()
    for v in versions[:5]:
        print(f"  {v['name']} ({v['size_mb']} MB) - {v['created']}")
    
    print("\n✅ All tests completed!")
