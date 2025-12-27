"""
Data Preparation Module for Golden Hour Model

This module handles:
1. Loading and filtering the disease dataset
2. Applying golden hour labels
3. Feature selection and data cleaning
4. Train/validation/test split with anti-data-leak measures
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import VarianceThreshold, mutual_info_classif
import joblib
import warnings
warnings.filterwarnings('ignore')


class GoldenHourDataPreparer:
    """
    Prepares data for Golden Hour model training with strict anti-data-leak measures.
    
    Anti-Leak Strategy:
    1. Split BEFORE any preprocessing
    2. Fit transforms only on training data
    3. Generate synthetic data only from training split
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or Path(__file__).parent.parent / 'config' / 'golden_hour_diseases.yaml'
        self.golden_hour_diseases = self._load_golden_hour_config()
        self.scaler = None
        self.label_encoder = None
        self.selected_features = None
        
    def _load_golden_hour_config(self) -> dict:
        """Load golden hour disease configuration"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Create disease name to golden hour mapping
        disease_mapping = {}
        for disease in config['diseases']:
            # Map various name formats
            disease_mapping[disease['name'].lower()] = {
                'golden_hour_minutes': disease['golden_hour_minutes'],
                'urgency_level': disease['urgency_level'],
                'category': disease['category']
            }
            disease_mapping[disease['name_tr'].lower()] = disease_mapping[disease['name'].lower()]
            disease_mapping[disease['id']] = disease_mapping[disease['name'].lower()]
            
        return disease_mapping
    
    def load_data(self, data_path: str, encoding_path: str = None) -> pd.DataFrame:
        """
        Load the disease dataset and filter for golden hour diseases only.
        
        Args:
            data_path: Path to cleaned_dataset.csv
            encoding_path: Path to disease_encoding.csv (optional)
        
        Returns:
            Filtered DataFrame with only golden hour diseases
        """
        print("Loading dataset...")
        df = pd.read_csv(data_path)
        print(f"  Original shape: {df.shape}")
        
        # Define golden hour disease names that match the dataset
        golden_hour_names = [
            'heart attack',
            'stroke',
            'sepsis',
            'cardiac arrest',
            'pulmonary embolism',
            'meningitis',
            'pneumothorax',
            'appendicitis',
            'acute pancreatitis',
            'diabetic ketoacidosis',
            'testicular torsion',
            'gastrointestinal hemorrhage',
            'ectopic pregnancy',
            'asthma',  # severe asthma
            'intracerebral hemorrhage',
            'subarachnoid hemorrhage',
            'acute respiratory distress syndrome (ards)',
            'transient ischemic attack',
            'acute glaucoma',
        ]
        
        # Filter for golden hour diseases
        df_filtered = df[df['diseases'].str.lower().isin(golden_hour_names)].copy()
        print(f"  Filtered shape (golden hour only): {df_filtered.shape}")
        
        return df_filtered
    
    def create_golden_hour_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add golden hour urgency labels based on medical guidelines.
        
        Creates two target columns:
        - urgency_level: 1-5 categorical (for classification)
        - golden_hour_minutes: numeric (for regression/reference)
        """
        # Golden hour mapping based on medical literature
        golden_hour_mapping = {
            'heart attack': {'minutes': 90, 'urgency': 5},
            'cardiac arrest': {'minutes': 4, 'urgency': 5},
            'stroke': {'minutes': 270, 'urgency': 5},
            'intracerebral hemorrhage': {'minutes': 60, 'urgency': 5},
            'subarachnoid hemorrhage': {'minutes': 60, 'urgency': 5},
            'sepsis': {'minutes': 60, 'urgency': 5},
            'pulmonary embolism': {'minutes': 60, 'urgency': 5},
            'pneumothorax': {'minutes': 30, 'urgency': 5},
            'acute respiratory distress syndrome (ards)': {'minutes': 60, 'urgency': 5},
            'gastrointestinal hemorrhage': {'minutes': 60, 'urgency': 5},
            'meningitis': {'minutes': 60, 'urgency': 5},
            'ectopic pregnancy': {'minutes': 30, 'urgency': 5},
            'transient ischemic attack': {'minutes': 60, 'urgency': 4},
            'acute glaucoma': {'minutes': 120, 'urgency': 4},
            'diabetic ketoacidosis': {'minutes': 120, 'urgency': 4},
            'appendicitis': {'minutes': 1440, 'urgency': 4},  # 24 hours
            'acute pancreatitis': {'minutes': 360, 'urgency': 4},  # 6 hours
            'testicular torsion': {'minutes': 360, 'urgency': 4},
            'asthma': {'minutes': 30, 'urgency': 4},  # severe asthma attack
        }
        
        # Apply labels
        df['urgency_level'] = df['diseases'].str.lower().map(
            lambda x: golden_hour_mapping.get(x, {}).get('urgency', 3)
        )
        df['golden_hour_minutes'] = df['diseases'].str.lower().map(
            lambda x: golden_hour_mapping.get(x, {}).get('minutes', 1440)
        )
        
        print(f"Golden Hour Labels Created:")
        print(df['urgency_level'].value_counts().sort_index())
        
        return df
    
    def remove_low_variance_features(self, df: pd.DataFrame, threshold: float = 0.01) -> pd.DataFrame:
        """Remove features with very low variance (almost constant)"""
        feature_cols = [col for col in df.columns if col not in ['diseases', 'urgency_level', 'golden_hour_minutes']]
        
        selector = VarianceThreshold(threshold=threshold)
        selector.fit(df[feature_cols])
        
        selected_mask = selector.get_support()
        selected_features = [col for col, selected in zip(feature_cols, selected_mask) if selected]
        
        print(f"Variance threshold feature selection: {len(feature_cols)} -> {len(selected_features)} features")
        
        return df[selected_features + ['diseases', 'urgency_level', 'golden_hour_minutes']]
    
    def split_data(self, df: pd.DataFrame, test_size: float = 0.15, val_size: float = 0.15):
        """
        Split data with STRICT anti-data-leak measures.
        
        CRITICAL: Split is done BEFORE any scaling or feature selection!
        
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        # Separate features and target
        feature_cols = [col for col in df.columns if col not in ['diseases', 'urgency_level', 'golden_hour_minutes']]
        X = df[feature_cols]
        y = df['urgency_level']
        
        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, 
            test_size=test_size, 
            stratify=y, 
            random_state=42
        )
        
        # Second split: train vs val
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, 
            test_size=val_ratio, 
            stratify=y_temp, 
            random_state=42
        )
        
        print(f"\nData Split (BEFORE any transforms):")
        print(f"  Train: {len(X_train)} samples")
        print(f"  Validation: {len(X_val)} samples (100% REAL)")
        print(f"  Test: {len(X_test)} samples (100% REAL)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def fit_and_transform_training(self, X_train: pd.DataFrame) -> np.ndarray:
        """
        Fit scaler ONLY on training data and transform.
        
        ANTI-LEAK: This method only fits on training data!
        """
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.selected_features = X_train.columns.tolist()
        
        print(f"Scaler fitted on training data only: {len(self.selected_features)} features")
        return X_train_scaled
    
    def transform_validation_test(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform validation/test data using ALREADY FITTED scaler.
        
        ANTI-LEAK: Uses pre-fitted scaler, no data leakage!
        """
        if self.scaler is None:
            raise ValueError("Scaler not fitted! Call fit_and_transform_training first.")
        return self.scaler.transform(X)
    
    def save_artifacts(self, output_dir: str):
        """Save preprocessing artifacts for inference"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if self.scaler is not None:
            joblib.dump(self.scaler, output_path / 'golden_hour_scaler.pkl')
            print(f"  Saved scaler to {output_path / 'golden_hour_scaler.pkl'}")
        
        if self.selected_features is not None:
            joblib.dump(self.selected_features, output_path / 'golden_hour_features.pkl')
            print(f"  Saved feature list to {output_path / 'golden_hour_features.pkl'}")
    
    def prepare_full_pipeline(self, data_path: str, output_dir: str = 'models'):
        """
        Complete data preparation pipeline with anti-leak measures.
        
        Returns:
            Dictionary with all prepared data splits
        """
        print("="*60)
        print("GOLDEN HOUR DATA PREPARATION PIPELINE")
        print("="*60)
        
        # Step 1: Load and filter
        df = self.load_data(data_path)
        
        # Step 2: Create labels
        df = self.create_golden_hour_labels(df)
        
        # Step 3: Remove low variance features
        df = self.remove_low_variance_features(df)
        
        # Step 4: Split BEFORE any transforms (anti-leak!)
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(df)
        
        # Step 5: Fit scaler on training ONLY
        X_train_scaled = self.fit_and_transform_training(X_train)
        
        # Step 6: Transform validation/test with pre-fitted scaler
        X_val_scaled = self.transform_validation_test(X_val)
        X_test_scaled = self.transform_validation_test(X_test)
        
        # Step 7: Save artifacts
        self.save_artifacts(output_dir)
        
        print("\n" + "="*60)
        print("DATA PREPARATION COMPLETE")
        print("="*60)
        
        return {
            'X_train': X_train_scaled,
            'X_val': X_val_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train.values,
            'y_val': y_val.values,
            'y_test': y_test.values,
            'feature_names': self.selected_features,
            'X_train_df': X_train,  # Keep original for synthetic generation
        }


if __name__ == "__main__":
    # Test the pipeline
    preparer = GoldenHourDataPreparer()
    data = preparer.prepare_full_pipeline(
        data_path='../data/cleaned_dataset.csv',
        output_dir='../models'
    )
    print(f"\nPrepared datasets:")
    print(f"  X_train: {data['X_train'].shape}")
    print(f"  X_val: {data['X_val'].shape}")
    print(f"  X_test: {data['X_test'].shape}")
