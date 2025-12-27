"""
Golden Hour Model Training Configuration
Contains all hyperparameters, constraints, and anti-overfit settings
"""

# =============================================================================
# MODEL CONSTRAINTS (ZORUNLU)
# =============================================================================
MODEL_CONSTRAINTS = {
    'max_size_mb': 100,           # Maximum model size in MB
    'format': 'pkl',              # Output format
    'prevent_overfit': True,      # Enable anti-overfit measures
    'prevent_data_leak': True,    # Enable anti-data-leak measures
}

# =============================================================================
# DATA SPLIT CONFIGURATION
# =============================================================================
DATA_SPLIT = {
    'train_ratio': 0.70,          # 70% for training
    'validation_ratio': 0.15,     # 15% for validation (REAL data only)
    'test_ratio': 0.15,           # 15% for testing (REAL data only)
    'random_state': 42,
    'stratify': True,             # Maintain class distribution
}

# =============================================================================
# SYNTHETIC DATA CONFIGURATION
# =============================================================================
SYNTHETIC_CONFIG = {
    'enabled': True,
    'method': 'ctgan',            # Options: 'ctgan', 'gaussian_copula', 'tvae'
    'train_real_ratio': 0.40,     # 40% real data in augmented train set
    'train_synthetic_ratio': 0.60, # 60% synthetic data in augmented train set
    'epochs': 300,                # CTGAN training epochs
    'batch_size': 500,
    'quality_threshold': 0.80,    # Minimum quality score to accept
}

# =============================================================================
# ANTI-OVERFIT CONFIGURATION
# =============================================================================
ANTI_OVERFIT = {
    # Cross-validation settings
    'cv_folds': 5,
    'cv_shuffle': True,
    
    # Early stopping
    'early_stopping_rounds': 50,
    'eval_metric': 'mlogloss',
    
    # Regularization parameters
    'max_depth': 6,               # Shallow trees prevent memorization
    'min_child_weight': 5,        # Minimum samples in leaf
    'reg_alpha': 0.1,             # L1 regularization
    'reg_lambda': 1.0,            # L2 regularization
    'subsample': 0.8,             # Row sampling (bagging)
    'colsample_bytree': 0.8,      # Feature sampling per tree
    'colsample_bylevel': 0.8,     # Feature sampling per level
    
    # Learning rate
    'learning_rate': 0.05,        # Lower = more robust
    'n_estimators': 500,          # Will be truncated by early stopping
    
    # Dropout equivalent
    'tree_method': 'hist',        # Faster, uses histogram
}

# =============================================================================
# ANTI-DATA-LEAK CHECKLIST
# =============================================================================
ANTI_LEAK_CHECKLIST = """
✅ Data Leak Prevention Checklist:

1. [SPLIT FIRST] Always split BEFORE any preprocessing
   - train_test_split() → THEN fit scaler/encoder
   
2. [PIPELINE] Use sklearn Pipeline for all transforms
   - Scaler, Encoder, Imputer inside pipeline
   - Pipeline.fit(X_train) only
   
3. [SYNTHETIC] Generate from TRAIN split only
   - Never generate synthetic from full dataset
   - Never use validation/test for synthetic generation
   
4. [VALIDATION] Real data only
   - Validation set = 100% real data
   - Test set = 100% real data
   
5. [TEMPORAL] If time-based data exists
   - Use temporal split (older → train, newer → test)
   - Never shuffle time-series data
   
6. [METRICS] Calculate on held-out data only
   - Cross-validation on train split
   - Final metrics on test split
"""

# =============================================================================
# XGBOOST MODEL PARAMETERS
# =============================================================================
XGBOOST_PARAMS = {
    'objective': 'multi:softprob',
    'num_class': 5,               # 5 urgency levels
    'max_depth': ANTI_OVERFIT['max_depth'],
    'min_child_weight': ANTI_OVERFIT['min_child_weight'],
    'learning_rate': ANTI_OVERFIT['learning_rate'],
    'n_estimators': ANTI_OVERFIT['n_estimators'],
    'subsample': ANTI_OVERFIT['subsample'],
    'colsample_bytree': ANTI_OVERFIT['colsample_bytree'],
    'colsample_bylevel': ANTI_OVERFIT['colsample_bylevel'],
    'reg_alpha': ANTI_OVERFIT['reg_alpha'],
    'reg_lambda': ANTI_OVERFIT['reg_lambda'],
    'tree_method': ANTI_OVERFIT['tree_method'],
    'random_state': 42,
    'n_jobs': -1,
    'verbosity': 1,
}

# =============================================================================
# FEATURE SELECTION (to keep model < 100MB)
# =============================================================================
FEATURE_SELECTION = {
    'enabled': True,
    'method': 'shap',             # Use SHAP for interpretable selection
    'max_features': 50,           # Maximum features to keep
    'min_importance': 0.001,      # Minimum SHAP importance
    'remove_correlated': True,    # Remove highly correlated features
    'correlation_threshold': 0.95,
}

# =============================================================================
# MODEL QUALITY THRESHOLDS
# =============================================================================
QUALITY_THRESHOLDS = {
    # Performance metrics (on test set)
    'min_macro_f1': 0.75,         # Minimum acceptable F1
    'min_critical_recall': 0.90,  # Recall for critical class (urgency=5)
    'max_train_test_gap': 0.10,   # Max gap between train/test performance
    
    # Overfit detection
    'overfit_threshold': 0.15,    # If train_f1 - test_f1 > 0.15 = overfit
    
    # Model size
    'max_model_size_mb': 100,
}

# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================
OUTPUT_CONFIG = {
    'model_path': 'models/golden_hour_model.pkl',
    'scaler_path': 'models/golden_hour_scaler.pkl',
    'encoder_path': 'models/golden_hour_encoder.pkl',
    'metadata_path': 'models/golden_hour_metadata.json',
    'shap_path': 'models/golden_hour_shap.pkl',
}
