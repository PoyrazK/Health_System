import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("WARNING: SHAP not installed. Skipping SHAP analysis.")

# Add project root to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from golden_hour_model.config.urgency_mapping import get_urgency

# Paths
DATA_PATH = BASE_DIR / 'cleaned_dataset.csv'
MODEL_DIR = BASE_DIR / 'golden_hour_model' / 'models'

print("="*70)
print("   MODEL INTERPRETABILITY ANALYSIS")
print("="*70)

# 1. Load Model and Artifacts
print("\n[1] Loading Model...")
model = joblib.load(MODEL_DIR / 'golden_hour_model.pkl')
scaler = joblib.load(MODEL_DIR / 'golden_hour_scaler.pkl')
artifacts = joblib.load(MODEL_DIR / 'golden_hour_artifacts.pkl')

feature_names = list(artifacts['feature_names'])
label_map = artifacts['label_map']
reverse_map = artifacts.get('reverse_map', {v: k for k, v in label_map.items()})

print(f"  Model loaded. Features: {len(feature_names)}")

# 2. XGBoost Native Feature Importance
print("\n[2] XGBoost Built-in Feature Importance (Gain)...")
importance = model.feature_importances_
indices = np.argsort(importance)[::-1]

print("\n  Top 20 Most Important Features:")
print("  " + "-"*50)
for f in range(20):
    if f >= len(indices): break
    idx = int(indices[f])
    print(f"  {f+1:2d}. {feature_names[idx]:<40} : {importance[idx]:.4f}")

# 3. SHAP Analysis (Sample)
if SHAP_AVAILABLE:
    print("\n[3] SHAP Analysis (TreeExplainer)...")
    print("  Loading data for SHAP calculation...")

    df = pd.read_csv(DATA_PATH)
    df['urgency_level'] = df['diseases'].str.lower().apply(get_urgency)

    # Prepare data same as training
    X = df[feature_names].values
    X_scaled = scaler.transform(X)

    # Sample 500 instances for speed
    X_sample = X_scaled[:500]
    print(f"  Calculating SHAP values for 500 samples...")

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # Summary of SHAP importance
    # For multi-class, shap_values is a list of arrays (one per class)
    if isinstance(shap_values, list):
        # Take mean absolute SHAP value across all classes and samples
        mean_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
    else:
        mean_shap = np.abs(shap_values).mean(axis=0)

    shap_indices = np.argsort(mean_shap)[::-1]

    print("\n  Top 20 Features by SHAP Value (Global Impact):")
    print("  " + "-"*50)
    for f in range(20):
        if f >= len(shap_indices): break
        try:
            idx = shap_indices[f]
            if isinstance(idx, np.ndarray):
                idx = idx.item()
            idx = int(idx)
            print(f"  {f+1:2d}. {feature_names[idx]:<40} : {mean_shap[idx]:.4f}")
        except Exception as e:
            print(f"  Error printing feature {f}: {e}")
else:
    print("\n[3] SHAP Analysis skipped (library not found)")

print("\n" + "="*70)
print("   ANALYSIS COMPLETE")
print("="*70)
