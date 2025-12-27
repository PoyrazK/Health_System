"""
EKG Analysis Service
Analyzes ECG signals for arrhythmia detection and cardiac anomalies
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import joblib
import json
import os
from datetime import datetime

# Try to import deep learning libraries
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️ TensorFlow not installed. EKG analysis will use fallback mode.")

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not installed.")


class EKGService:
    """
    EKG signal analysis service with deep learning
    Detects: Arrhythmia, MI, QT prolongation, etc.
    """
    
    def __init__(self, model_dir: str = None):
        """Initialize EKG service"""
        if model_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(current_dir)
            ai_service_dir = os.path.dirname(app_dir)
            model_dir = os.path.join(ai_service_dir, "models", "ekg")
        
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.model = None
        self.classes = None
        self.sampling_rate = 360  # Hz (MIT-BIH standard)
        
        # Try to load model if exists
        self._load_model()
    
    def _load_model(self):
        """Load trained EKG model"""
        model_path = os.path.join(self.model_dir, "ekg_classifier.h5")
        classes_path = os.path.join(self.model_dir, "ekg_classes.json")
        
        if os.path.exists(model_path) and TF_AVAILABLE:
            try:
                self.model = keras.models.load_model(model_path)
                with open(classes_path, 'r') as f:
                    self.classes = json.load(f)
                print(f"✅ EKG model loaded: {len(self.classes)} classes")
            except Exception as e:
                print(f"⚠️ Could not load EKG model: {e}")
        else:
            print("ℹ️ EKG model not found. Train model first or use demo mode.")
    
    # ==========================================
    # SIGNAL PREPROCESSING
    # ==========================================
    
    def preprocess_signal(
        self, 
        signal: np.ndarray,
        sampling_rate: int = 360,
        target_length: int = 1000
    ) -> np.ndarray:
        """
        Preprocess EKG signal
        
        Args:
            signal: Raw EKG signal
            sampling_rate: Signal sampling rate in Hz
            target_length: Target length after resampling
        
        Returns:
            Preprocessed signal
        """
        # Remove baseline wander (high-pass filter)
        from scipy.signal import butter, filtfilt
        
        # High-pass filter at 0.5 Hz
        nyquist = sampling_rate / 2
        cutoff = 0.5 / nyquist
        b, a = butter(2, cutoff, btype='high')
        signal = filtfilt(b, a, signal)
        
        # Normalize
        signal = (signal - np.mean(signal)) / (np.std(signal) + 1e-8)
        
        # Resample to target length
        if len(signal) != target_length:
            from scipy.interpolate import interp1d
            x_old = np.linspace(0, 1, len(signal))
            x_new = np.linspace(0, 1, target_length)
            f = interp1d(x_old, signal, kind='cubic')
            signal = f(x_new)
        
        return signal
    
    # ==========================================
    # FEATURE EXTRACTION
    # ==========================================
    
    def extract_features(self, signal: np.ndarray) -> Dict[str, float]:
        """
        Extract clinical features from EKG signal
        
        Returns:
            Dictionary of features (RR interval, QRS duration, etc.)
        """
        features = {}
        
        # Heart rate estimation
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(signal, distance=self.sampling_rate//3)
        
        if len(peaks) > 1:
            rr_intervals = np.diff(peaks) / self.sampling_rate * 1000  # ms
            features['heart_rate'] = 60000 / np.mean(rr_intervals)
            features['rr_mean'] = np.mean(rr_intervals)
            features['rr_std'] = np.std(rr_intervals)
            features['rr_min'] = np.min(rr_intervals)
            features['rr_max'] = np.max(rr_intervals)
        else:
            features['heart_rate'] = 0
            features['rr_mean'] = 0
            features['rr_std'] = 0
        
        # Signal statistics
        features['signal_mean'] = np.mean(signal)
        features['signal_std'] = np.std(signal)
        features['signal_min'] = np.min(signal)
        features['signal_max'] = np.max(signal)
        
        return features
    
    # ==========================================
    # PREDICTION
    # ==========================================
    
    def analyze(
        self, 
        signal: np.ndarray,
        sampling_rate: int = 360
    ) -> Dict[str, Any]:
        """
        Analyze EKG signal and return diagnosis
        
        Args:
            signal: EKG signal (1D array)
            sampling_rate: Sampling rate in Hz
        
        Returns:
            Analysis results with diagnosis and features
        """
        # Preprocess
        processed = self.preprocess_signal(signal, sampling_rate)
        
        # Extract features
        features = self.extract_features(processed)
        
        # Predict if model available
        if self.model and TF_AVAILABLE:
            # Reshape for CNN input: (1, length, 1)
            input_signal = processed.reshape(1, -1, 1)
            predictions = self.model.predict(input_signal, verbose=0)[0]
            
            # Get top 3 predictions
            top3_idx = np.argsort(predictions)[-3:][::-1]
            top3_results = [
                {
                    "condition": self.classes[idx],
                    "probability": float(predictions[idx]),
                    "confidence": "high" if predictions[idx] > 0.7 else "medium" if predictions[idx] > 0.4 else "low"
                }
                for idx in top3_idx
            ]
        else:
            # Fallback: Rule-based detection
            top3_results = self._rule_based_analysis(features)
        
        return {
            "status": "success",
            "predictions": top3_results,
            "features": features,
            "timestamp": datetime.now().isoformat()
        }
    
    def _rule_based_analysis(self, features: Dict[str, float]) -> List[Dict[str, Any]]:
        """Rule-based EKG analysis when model not available"""
        results = []
        hr = features.get('heart_rate', 0)
        
        # Bradycardia
        if 0 < hr < 60:
            results.append({
                "condition": "Bradycardia",
                "probability": 0.8,
                "confidence": "medium"
            })
        # Tachycardia
        elif hr > 100:
            results.append({
                "condition": "Tachycardia",
                "probability": 0.8,
                "confidence": "medium"
            })
        # Normal sinus rhythm
        elif 60 <= hr <= 100:
            results.append({
                "condition": "Normal Sinus Rhythm",
                "probability": 0.7,
                "confidence": "medium"
            })
        
        # Add uncertainty if only rule-based
        results.append({
            "condition": "Requires Expert Review",
            "probability": 0.5,
            "confidence": "low"
        })
        
        return results[:3]
    
    # ==========================================
    # FEEDBACK & LEARNING
    # ==========================================
    
    def log_feedback(
        self,
        signal: np.ndarray,
        model_prediction: str,
        confirmed_diagnosis: str,
        doctor_id: str = None
    ) -> bool:
        """Log physician feedback for EKG analysis"""
        feedback_path = os.path.join(self.model_dir, "ekg_feedback.csv")
        
        # Extract features
        features = self.extract_features(signal)
        
        log_entry = {
            "model_prediction": model_prediction,
            "confirmed_diagnosis": confirmed_diagnosis,
            "doctor_id": doctor_id or "",
            "timestamp": datetime.now().isoformat(),
            "model_correct": 1 if model_prediction == confirmed_diagnosis else 0,
            **features
        }
        
        df = pd.DataFrame([log_entry])
        
        if os.path.exists(feedback_path):
            df.to_csv(feedback_path, mode='a', header=False, index=False)
        else:
            df.to_csv(feedback_path, index=False)
        
        print(f"✅ EKG feedback logged: {confirmed_diagnosis}")
        return True


# ==========================================
# SINGLETON INSTANCE
# ==========================================

_ekg_service = None

def get_ekg_service(model_dir: str = None):
    """Get or create EKG service singleton"""
    global _ekg_service
    if _ekg_service is None:
        _ekg_service = EKGService(model_dir)
    return _ekg_service
