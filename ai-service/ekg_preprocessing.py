"""
EKG Data Preprocessing Pipeline
Complete pipeline for cleaning, preprocessing, and preparing EKG data for ML models
Supports: Arrhythmia classification (N, S, V, F, Q)
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Optional
import os
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from scipy import signal, stats
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🏥 EKG DATA PREPROCESSING PIPELINE")
print("=" * 80)


# ==========================================
# CONFIGURATION
# ==========================================

class Config:
    """Configuration for EKG preprocessing"""
    
    # Paths
    DATA_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\data\ekg"
    MODEL_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg"
    
    # Signal processing
    SIGNAL_LENGTH = 256  # Fixed window size
    SAMPLING_RATE = 360  # Hz (MIT-BIH standard)
    MIN_SIGNAL_LENGTH = 100  # Minimum samples to keep
    
    # Data split
    TRAIN_RATIO = 0.70
    VAL_RATIO = 0.15
    TEST_RATIO = 0.15
    
    # Class mapping
    LABEL_MAP = {
        'N': 0,  # Normal
        'S': 1,  # SVEB (Supraventricular Ectopic Beat)
        'V': 2,  # VEB (Ventricular Ectopic Beat)
        'F': 3,  # VF/Flutter
        'Q': 4   # Noise/Unclassifiable
    }
    
    # Class weights for imbalanced data
    USE_SMOTE = True
    SMOTE_STRATEGY = 'auto'  # or dict like {0: 1000, 1: 800, ...}
    
    # Outlier detection
    Z_SCORE_THRESHOLD = 3.0


# ==========================================
# 1. DATA CLEANING
# ==========================================

class DataCleaner:
    """Handles data cleaning operations"""
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        print(f"  • Duplicates removed: {before - after}")
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values"""
        # Drop rows with missing labels
        before = len(df)
        df = df.dropna(subset=['label'])
        print(f"  • Rows with missing labels removed: {before - len(df)}")
        
        # For signal columns, interpolate or drop
        signal_cols = [col for col in df.columns if col.startswith('signal_')]
        if signal_cols:
            df[signal_cols] = df[signal_cols].interpolate(method='linear', axis=1)
        
        return df
    
    @staticmethod
    def filter_by_length(df: pd.DataFrame, min_length: int) -> pd.DataFrame:
        """Filter signals shorter than minimum length"""
        # Assuming signal is stored as array or multiple columns
        before = len(df)
        # This depends on your data structure - adjust accordingly
        # For now, keep all rows
        after = len(df)
        print(f"  • Short signals removed: {before - after}")
        return df
    
    @staticmethod
    def clean(df: pd.DataFrame, config: Config) -> pd.DataFrame:
        """Complete cleaning pipeline"""
        print("\n🧹 1. DATA CLEANING")
        print(f"  Initial samples: {len(df)}")
        
        df = DataCleaner.remove_duplicates(df)
        df = DataCleaner.handle_missing_values(df)
        df = DataCleaner.filter_by_length(df, config.MIN_SIGNAL_LENGTH)
        
        print(f"  Final samples: {len(df)}")
        return df


# ==========================================
# 2. SIGNAL PREPROCESSING
# ==========================================

class SignalPreprocessor:
    """Signal-level preprocessing operations"""
    
    @staticmethod
    def normalize_signal(sig: np.ndarray) -> np.ndarray:
        """Z-norm normalization"""
        mean = np.mean(sig)
        std = np.std(sig)
        if std == 0:
            return sig - mean
        return (sig - mean) / std
    
    @staticmethod
    def resample_signal(sig: np.ndarray, target_length: int) -> np.ndarray:
        """Resample signal to fixed length"""
        current_length = len(sig)
        
        if current_length == target_length:
            return sig
        elif current_length > target_length:
            # Downsample using scipy
            return signal.resample(sig, target_length)
        else:
            # Upsample or pad with zeros
            padded = np.zeros(target_length)
            padded[:current_length] = sig
            return padded
    
    @staticmethod
    def remove_baseline_wander(sig: np.ndarray, fs: int = 360) -> np.ndarray:
        """Remove baseline wander using high-pass filter"""
        nyquist = fs / 2
        cutoff = 0.5 / nyquist
        b, a = signal.butter(2, cutoff, btype='high')
        return signal.filtfilt(b, a, sig)
    
    @staticmethod
    def detect_outliers(sig: np.ndarray, threshold: float = 3.0) -> bool:
        """Detect if signal contains outliers"""
        z_scores = np.abs(stats.zscore(sig))
        return np.any(z_scores > threshold)
    
    @staticmethod
    def preprocess_signal(
        sig: np.ndarray,
        target_length: int,
        sampling_rate: int,
        remove_baseline: bool = True,
        normalize: bool = True
    ) -> np.ndarray:
        """Complete signal preprocessing"""
        
        # Remove baseline wander
        if remove_baseline:
            sig = SignalPreprocessor.remove_baseline_wander(sig, sampling_rate)
        
        # Resample to fixed length
        sig = SignalPreprocessor.resample_signal(sig, target_length)
        
        # Normalize
        if normalize:
            sig = SignalPreprocessor.normalize_signal(sig)
        
        return sig


# ==========================================
# 3. FEATURE ENGINEERING
# ==========================================

class FeatureEngineer:
    """Extract features from EKG signals"""
    
    @staticmethod
    def extract_statistical_features(sig: np.ndarray) -> Dict[str, float]:
        """Extract statistical features"""
        return {
            'mean': np.mean(sig),
            'std': np.std(sig),
            'min': np.min(sig),
            'max': np.max(sig),
            'rms': np.sqrt(np.mean(sig**2)),
            'skewness': stats.skew(sig),
            'kurtosis': stats.kurtosis(sig),
            'peak_to_peak': np.ptp(sig)
        }
    
    @staticmethod
    def extract_frequency_features(sig: np.ndarray, fs: int = 360) -> Dict[str, float]:
        """Extract frequency domain features"""
        # FFT
        fft_vals = np.fft.fft(sig)
        fft_freq = np.fft.fftfreq(len(sig), 1/fs)
        
        # Power spectral density
        psd = np.abs(fft_vals)**2
        
        return {
            'dominant_freq': fft_freq[np.argmax(psd[:len(psd)//2])],
            'spectral_energy': np.sum(psd)
        }
    
    @staticmethod
    def extract_heart_rate(sig: np.ndarray, fs: int = 360) -> Dict[str, float]:
        """Extract heart rate features"""
        # Find peaks (R-peaks)
        peaks, _ = signal.find_peaks(sig, distance=fs//3)
        
        if len(peaks) < 2:
            return {'heart_rate': 0, 'hrv': 0}
        
        # RR intervals
        rr_intervals = np.diff(peaks) / fs * 1000  # ms
        
        # Heart rate
        hr = 60000 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0
        
        # Heart rate variability
        hrv = np.std(rr_intervals) if len(rr_intervals) > 0 else 0
        
        return {
            'heart_rate': hr,
            'hrv': hrv
        }
    
    @staticmethod
    def extract_all_features(sig: np.ndarray, fs: int = 360) -> Dict[str, float]:
        """Extract all features"""
        features = {}
        features.update(FeatureEngineer.extract_statistical_features(sig))
        features.update(FeatureEngineer.extract_frequency_features(sig, fs))
        features.update(FeatureEngineer.extract_heart_rate(sig, fs))
        return features


# ==========================================
# 4. DATA PIPELINE
# ==========================================

class EKGDataPipeline:
    """Main data processing pipeline"""
    
    def __init__(self, config: Config):
        self.config = config
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load EKG data from CSV"""
        print(f"\n📂 Loading data from: {filepath}")
        df = pd.read_csv(filepath)
        print(f"  Loaded {len(df)} samples")
        return df
    
    def process_labels(self, labels: np.ndarray) -> np.ndarray:
        """Map and encode labels"""
        print("\n🏷 5. LABEL PROCESSING")
        
        # Map to 5-class system
        mapped_labels = []
        for label in labels:
            label_str = str(label).upper()
            # Map variations to standard 5 classes
            if label_str in ['N', 'NORMAL']:
                mapped_labels.append('N')
            elif label_str in ['S', 'SVEB', 'A']:
                mapped_labels.append('S')
            elif label_str in ['V', 'VEB']:
                mapped_labels.append('V')
            elif label_str in ['F', 'VF', 'FLUTTER']:
                mapped_labels.append('F')
            else:
                mapped_labels.append('Q')
        
        # Encode
        encoded = self.label_encoder.fit_transform(mapped_labels)
        
        # Show distribution
        unique, counts = np.unique(mapped_labels, return_counts=True)
        print("  Class distribution:")
        for label, count in zip(unique, counts):
            print(f"    {label}: {count} ({count/len(labels)*100:.1f}%)")
        
        return encoded
    
    def balance_data(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Balance dataset using SMOTE"""
        if not self.config.USE_SMOTE:
            return X, y
        
        print("\n⚖️ 3. CLASS BALANCING (SMOTE)")
        print(f"  Before SMOTE: {X.shape}")
        
        # Reshape if needed for SMOTE (2D required)
        original_shape = X.shape
        if len(X.shape) > 2:
            X_2d = X.reshape(X.shape[0], -1)
        else:
            X_2d = X
        
        smote = SMOTE(sampling_strategy=self.config.SMOTE_STRATEGY, random_state=42)
        X_balanced, y_balanced = smote.fit_resample(X_2d, y)
        
        # Reshape back
        if len(original_shape) > 2:
            X_balanced = X_balanced.reshape(-1, *original_shape[1:])
        
        print(f"  After SMOTE: {X_balanced.shape}")
        unique, counts = np.unique(y_balanced, return_counts=True)
        for label, count in zip(unique, counts):
            print(f"    Class {label}: {count} samples")
        
        return X_balanced, y_balanced
    
    def split_data(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split into train/val/test with stratification"""
        print("\n🚀 6. TRAIN/VAL/TEST SPLIT")
        
        # First split: train + val / test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=self.config.TEST_RATIO,
            stratify=y,
            random_state=42
        )
        
        # Second split: train / val
        val_ratio_adjusted = self.config.VAL_RATIO / (self.config.TRAIN_RATIO + self.config.VAL_RATIO)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_ratio_adjusted,
            stratify=y_temp,
            random_state=42
        )
        
        print(f"  Train: {X_train.shape[0]} samples ({self.config.TRAIN_RATIO*100:.0f}%)")
        print(f"  Val:   {X_val.shape[0]} samples ({self.config.VAL_RATIO*100:.0f}%)")
        print(f"  Test:  {X_test.shape[0]} samples ({self.config.TEST_RATIO*100:.0f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def save_processed_data(
        self,
        X_train, X_val, X_test,
        y_train, y_val, y_test,
        features_df: Optional[pd.DataFrame] = None
    ):
        """Save processed data for model training"""
        print("\n💾 7. SAVING PROCESSED DATA")
        
        os.makedirs(self.config.MODEL_DIR, exist_ok=True)
        
        # Save as numpy arrays
        np.savez_compressed(
            os.path.join(self.config.MODEL_DIR, 'ekg_data.npz'),
            X_train=X_train,
            X_val=X_val,
            X_test=X_test,
            y_train=y_train,
            y_val=y_val,
            y_test=y_test
        )
        print(f"  ✅ Saved: ekg_data.npz")
        
        # Save label mapping
        label_map = dict(enumerate(self.label_encoder.classes_))
        with open(os.path.join(self.config.MODEL_DIR, 'label_map.json'), 'w') as f:
            json.dump(label_map, f, indent=2)
        print(f"  ✅ Saved: label_map.json")
        
        # Save features if provided
        if features_df is not None:
            features_df.to_csv(
                os.path.join(self.config.MODEL_DIR, 'ekg_features.csv'),
                index=False
            )
            print(f"  ✅ Saved: ekg_features.csv")
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'signal_length': self.config.SIGNAL_LENGTH,
            'sampling_rate': self.config.SAMPLING_RATE,
            'num_classes': len(self.label_encoder.classes_),
            'classes': list(self.label_encoder.classes_),
            'train_samples': int(len(X_train)),
            'val_samples': int(len(X_val)),
            'test_samples': int(len(X_test)),
            'smote_used': self.config.USE_SMOTE
        }
        
        with open(os.path.join(self.config.MODEL_DIR, 'preprocessing_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✅ Saved: preprocessing_metadata.json")


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """Run complete preprocessing pipeline"""
    
    config = Config()
    pipeline = EKGDataPipeline(config)
    
    # Note: You need to provide your EKG CSV file
    # For demonstration, creating synthetic data
    print("\n⚠️ WARNING: No CSV file provided. Creating synthetic demo data...")
    
    # Create synthetic data for demonstration
    n_samples = 1000
    signal_length = config.SIGNAL_LENGTH
    
    # Generate synthetic signals
    X_signals = []
    y_labels = []
    
    for i in range(n_samples):
        # Random signal
        t = np.linspace(0, 2, signal_length)
        sig = np.sin(2 * np.pi * 1.2 * t) + 0.5 * np.sin(2 * np.pi * 2.5 * t)
        sig += np.random.normal(0, 0.1, signal_length)
        
        # Preprocess
        sig = SignalPreprocessor.preprocess_signal(
            sig,
            config.SIGNAL_LENGTH,
            config.SAMPLING_RATE
        )
        
        X_signals.append(sig)
        
        # Random label
        y_labels.append(np.random.choice(['N', 'S', 'V', 'F', 'Q']))
    
    X = np.array(X_signals)
    
    print(f"\n📊 2. PREPROCESSING")
    print(f"  Signals preprocessed: {len(X)}")
    print(f"  Signal shape: {X.shape}")
    
    # Process labels
    y = pipeline.process_labels(y_labels)
    
    # Balance data
    X_balanced, y_balanced = pipeline.balance_data(X, y)
    
    # Extract features (for XGBoost)
    print("\n🔢 4. FEATURE ENGINEERING")
    features_list = []
    for sig in X_balanced[:100]:  # Demo: first 100 samples
        features = FeatureEngineer.extract_all_features(sig, config.SAMPLING_RATE)
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    print(f"  Extracted features: {features_df.shape[1]}")
    print(f"  Feature names: {list(features_df.columns)}")
    
    # Split data
    X_train, X_val, X_test, y_train, y_val, y_test = pipeline.split_data(
        X_balanced, y_balanced
    )
    
    # Save
    pipeline.save_processed_data(
        X_train, X_val, X_test,
        y_train, y_val, y_test,
        features_df
    )
    
    print("\n" + "=" * 80)
    print("✅ PREPROCESSING COMPLETE")
    print("=" * 80)
    print(f"\nReady for model training!")
    print(f"  • XGBoost: Use ekg_features.csv")
    print(f"  • CNN/LSTM: Use ekg_data.npz (signals)")


if __name__ == "__main__":
    main()
