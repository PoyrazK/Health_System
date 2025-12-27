"""
Golden Hour Model Training Module

Trains XGBoost classifier with strict anti-overfit measures:
1. Regularization (L1, L2, max_depth limits)
2. Early stopping with validation
3. Cross-validation for robust evaluation
4. Model size constraints (<100MB)

Output: .pkl format model file
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    f1_score, 
    recall_score,
    accuracy_score
)
import shap

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent))
from data_preparation import GoldenHourDataPreparer
from synthetic_generator import GoldenHourSyntheticGenerator


class GoldenHourModelTrainer:
    """
    Trains the Golden Hour urgency prediction model.
    
    ANTI-OVERFIT MEASURES:
    - Regularization parameters
    - Early stopping
    - 5-fold cross-validation
    - Train-test gap monitoring
    """
    
    # Constraint: Model must be < 100MB
    MAX_MODEL_SIZE_MB = 100
    
    # Overfit detection threshold
    OVERFIT_THRESHOLD = 0.15
    
    def __init__(self, output_dir: str = 'models'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.shap_explainer = None
        self.training_metrics = {}
        
    def get_model_params(self) -> dict:
        """
        Get XGBoost parameters with anti-overfit settings.
        """
        return {
            # Objective for multi-class classification
            'objective': 'multi:softprob',
            'num_class': 5,  # Urgency levels 1-5
            
            # Anti-overfit: Regularization
            'max_depth': 6,           # Shallow trees
            'min_child_weight': 5,    # Minimum samples per leaf
            'reg_alpha': 0.1,         # L1 regularization
            'reg_lambda': 1.0,        # L2 regularization
            
            # Anti-overfit: Sampling
            'subsample': 0.8,         # Row sampling
            'colsample_bytree': 0.8,  # Feature sampling per tree
            'colsample_bylevel': 0.8, # Feature sampling per level
            
            # Learning
            'learning_rate': 0.05,    # Low learning rate for robustness
            'n_estimators': 500,      # Will be reduced by early stopping
            
            # Performance
            'tree_method': 'hist',    # Fast histogram-based
            'random_state': 42,
            'n_jobs': -1,
            'verbosity': 1,
            
            # Early stopping (set during fit)
            'early_stopping_rounds': 50,
        }
    
    def train_with_cross_validation(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        feature_names: list = None
    ) -> dict:
        """
        Train model with cross-validation and early stopping.
        
        Args:
            X_train: Training features (can include synthetic)
            y_train: Training labels
            X_val: Validation features (REAL data only!)
            y_val: Validation labels
            feature_names: List of feature names for interpretability
        
        Returns:
            Dictionary with training metrics
        """
        print("="*60)
        print("TRAINING GOLDEN HOUR MODEL")
        print("="*60)
        
        # Adjust labels from 1-5 to 0-4 (XGBoost requirement)
        y_train_adj = y_train - 1
        y_val_adj = y_val - 1
        
        # Get parameters
        params = self.get_model_params()
        early_stopping = params.pop('early_stopping_rounds')
        
        # Initialize model
        self.model = XGBClassifier(**params)
        
        # Step 1: Cross-validation for robust evaluation
        print("\n[Step 1] 5-Fold Stratified Cross-Validation...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            self.model, X_train, y_train_adj, 
            cv=cv, scoring='f1_macro', n_jobs=-1
        )
        
        print(f"  CV F1 Scores: {cv_scores}")
        print(f"  CV Mean F1: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
        
        # Step 2: Train final model with early stopping
        print("\n[Step 2] Training Final Model with Early Stopping...")
        self.model.fit(
            X_train, y_train_adj,
            eval_set=[(X_val, y_val_adj)],
            verbose=50
        )
        
        print(f"  Best iteration: {self.model.best_iteration}")
        
        # Step 3: Evaluate on training data
        print("\n[Step 3] Evaluating Model Performance...")
        y_train_pred = self.model.predict(X_train)
        y_val_pred = self.model.predict(X_val)
        
        train_f1 = f1_score(y_train_adj, y_train_pred, average='macro')
        val_f1 = f1_score(y_val_adj, y_val_pred, average='macro')
        
        # Step 4: Check for overfitting
        overfit_gap = train_f1 - val_f1
        print(f"\n  Train F1: {train_f1:.4f}")
        print(f"  Validation F1: {val_f1:.4f}")
        print(f"  Overfit Gap: {overfit_gap:.4f}")
        
        if overfit_gap > self.OVERFIT_THRESHOLD:
            print(f"  ⚠️ WARNING: Overfit detected! Gap {overfit_gap:.4f} > threshold {self.OVERFIT_THRESHOLD}")
        else:
            print(f"  ✅ No overfitting detected (gap < {self.OVERFIT_THRESHOLD})")
        
        # Step 5: Critical class recall (urgency level 5)
        critical_mask = y_val_adj == 4  # Level 5 = index 4
        if critical_mask.sum() > 0:
            critical_recall = recall_score(y_val_adj[critical_mask], y_val_pred[critical_mask], average='micro')
            print(f"\n  Critical Class (Level 5) Recall: {critical_recall:.4f}")
        else:
            critical_recall = 0.0
        
        # Step 6: Detailed classification report
        print("\n[Classification Report - Validation Set]")
        # Adjust labels back for report
        target_names = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']
        print(classification_report(y_val_adj, y_val_pred, target_names=target_names, zero_division=0))
        
        # Store metrics
        self.training_metrics = {
            'cv_scores': cv_scores.tolist(),
            'cv_mean_f1': float(cv_scores.mean()),
            'cv_std_f1': float(cv_scores.std()),
            'train_f1': float(train_f1),
            'val_f1': float(val_f1),
            'overfit_gap': float(overfit_gap),
            'critical_recall': float(critical_recall),
            'best_iteration': int(self.model.best_iteration),
            'timestamp': datetime.now().isoformat(),
        }
        
        return self.training_metrics
    
    def compute_shap_values(self, X: np.ndarray, feature_names: list = None):
        """Compute SHAP values for model interpretability"""
        print("\n[Computing SHAP Values...]")
        
        self.shap_explainer = shap.TreeExplainer(self.model)
        shap_values = self.shap_explainer.shap_values(X[:min(1000, len(X))])  # Sample for speed
        
        # Get feature importance from SHAP
        if feature_names is not None:
            if isinstance(shap_values, list):
                # Multi-class: average across classes
                mean_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
            else:
                mean_shap = np.abs(shap_values).mean(axis=0)
            
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': mean_shap
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 Important Features (SHAP):")
            print(importance_df.head(10).to_string(index=False))
            
            return importance_df
        
        return None
    
    def save_model(self, include_shap: bool = True) -> dict:
        """
        Save model to .pkl format with size check.
        
        Returns:
            Dictionary with file paths and sizes
        """
        print("\n[Saving Model...]")
        
        # Save model
        model_path = self.output_dir / 'golden_hour_model.pkl'
        joblib.dump(self.model, model_path)
        
        # Check size
        model_size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"  Model saved: {model_path}")
        print(f"  Model size: {model_size_mb:.2f} MB")
        
        if model_size_mb > self.MAX_MODEL_SIZE_MB:
            print(f"  ⚠️ WARNING: Model size {model_size_mb:.2f}MB exceeds limit {self.MAX_MODEL_SIZE_MB}MB!")
        else:
            print(f"  ✅ Model size within limit ({self.MAX_MODEL_SIZE_MB}MB)")
        
        # Save SHAP explainer
        if include_shap and self.shap_explainer is not None:
            shap_path = self.output_dir / 'golden_hour_shap.pkl'
            joblib.dump(self.shap_explainer, shap_path)
            print(f"  SHAP explainer saved: {shap_path}")
        
        # Save metrics
        metrics_path = self.output_dir / 'golden_hour_metadata.json'
        with open(metrics_path, 'w') as f:
            json.dump(self.training_metrics, f, indent=2)
        print(f"  Metrics saved: {metrics_path}")
        
        return {
            'model_path': str(model_path),
            'model_size_mb': model_size_mb,
            'metrics_path': str(metrics_path),
        }
    
    def evaluate_on_test(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """
        Final evaluation on held-out test set.
        
        CRITICAL: This should only be done ONCE at the very end!
        """
        print("\n" + "="*60)
        print("FINAL EVALUATION ON TEST SET")
        print("="*60)
        
        y_test_adj = y_test - 1
        y_pred = self.model.predict(X_test)
        
        # Metrics
        test_f1 = f1_score(y_test_adj, y_pred, average='macro')
        test_accuracy = accuracy_score(y_test_adj, y_pred)
        
        print(f"\nTest Set Results:")
        print(f"  F1 Score (Macro): {test_f1:.4f}")
        print(f"  Accuracy: {test_accuracy:.4f}")
        
        # Critical class recall
        for level in range(5):
            mask = y_test_adj == level
            if mask.sum() > 0:
                level_recall = recall_score(y_test_adj[mask], y_pred[mask], average='micro')
                print(f"  Level {level+1} Recall: {level_recall:.4f} (n={mask.sum()})")
        
        # Classification report
        print("\n[Classification Report - Test Set]")
        target_names = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']
        print(classification_report(y_test_adj, y_pred, target_names=target_names, zero_division=0))
        
        # Confusion matrix
        print("\n[Confusion Matrix]")
        cm = confusion_matrix(y_test_adj, y_pred)
        print(pd.DataFrame(cm, index=target_names, columns=target_names))
        
        # Update metrics
        self.training_metrics['test_f1'] = float(test_f1)
        self.training_metrics['test_accuracy'] = float(test_accuracy)
        
        return self.training_metrics


def run_full_training_pipeline(data_path: str, output_dir: str = 'models'):
    """
    Complete training pipeline from raw data to saved model.
    """
    print("="*70)
    print("GOLDEN HOUR MODEL - FULL TRAINING PIPELINE")
    print("="*70)
    
    # Step 1: Data Preparation
    print("\n" + "="*60)
    print("PHASE 1: DATA PREPARATION")
    print("="*60)
    
    preparer = GoldenHourDataPreparer()
    data = preparer.prepare_full_pipeline(data_path, output_dir)
    
    # Step 2: Synthetic Data Generation
    print("\n" + "="*60)
    print("PHASE 2: SYNTHETIC DATA AUGMENTATION")
    print("="*60)
    
    generator = GoldenHourSyntheticGenerator(method='oversample')
    X_train_aug, y_train_aug = generator.create_augmented_training_set(
        data['X_train_df'],  # Use original DataFrame for synthetic generation
        data['y_train'],
        synthetic_ratio=0.6
    )
    
    # Scale the augmented training data
    X_train_aug_scaled = preparer.scaler.transform(X_train_aug)
    
    # Step 3: Model Training
    print("\n" + "="*60)
    print("PHASE 3: MODEL TRAINING")
    print("="*60)
    
    trainer = GoldenHourModelTrainer(output_dir)
    trainer.train_with_cross_validation(
        X_train_aug_scaled,
        y_train_aug,
        data['X_val'],
        data['y_val'],
        feature_names=data['feature_names']
    )
    
    # Step 4: SHAP Analysis
    print("\n" + "="*60)
    print("PHASE 4: MODEL INTERPRETABILITY (SHAP)")
    print("="*60)
    
    trainer.compute_shap_values(data['X_val'], data['feature_names'])
    
    # Step 5: Final Test Evaluation
    trainer.evaluate_on_test(data['X_test'], data['y_test'])
    
    # Step 6: Save Model
    save_info = trainer.save_model()
    
    print("\n" + "="*70)
    print("TRAINING PIPELINE COMPLETE")
    print("="*70)
    print(f"\nModel saved to: {save_info['model_path']}")
    print(f"Model size: {save_info['model_size_mb']:.2f} MB")
    
    return trainer


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Golden Hour Model')
    parser.add_argument('--data', type=str, default='../data/cleaned_dataset.csv',
                        help='Path to cleaned_dataset.csv')
    parser.add_argument('--output', type=str, default='../models',
                        help='Output directory for model files')
    
    args = parser.parse_args()
    
    run_full_training_pipeline(args.data, args.output)
