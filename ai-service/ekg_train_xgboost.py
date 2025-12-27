"""
EKG Model Training - XGBoost Classifier
Train XGBoost model for arrhythmia classification using extracted features
"""

import numpy as np
import pandas as pd
import joblib
import json
from datetime import datetime
import os

from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    classification_report, confusion_matrix,
    top_k_accuracy_score
)
import xgboost as xgb
from xgboost import XGBClassifier

print("=" * 80)
print("🤖 EKG XGBOOST MODEL TRAINING")
print("=" * 80)

# ==========================================
# CONFIGURATION
# ==========================================

MODEL_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg"
os.makedirs(MODEL_DIR, exist_ok=True)

# ==========================================
# 1. LOAD PREPROCESSED DATA
# ==========================================

print("\n📂 1. LOADING DATA")

# Load data
data = np.load(os.path.join(MODEL_DIR, 'ekg_data.npz'))
X_train = data['X_train']
X_val = data['X_val']
X_test = data['X_test']
y_train = data['y_train']
y_val = data['y_val']
y_test = data['y_test']

print(f"  Train: {X_train.shape}")
print(f"  Val:   {X_val.shape}")
print(f"  Test:  {X_test.shape}")

# Load features (if available)
features_path = os.path.join(MODEL_DIR, 'ekg_features.csv')
if os.path.exists(features_path):
    features_df = pd.read_csv(features_path)
    X_train_features = features_df.iloc[:len(X_train)].values
    print(f"\n  Using extracted features: {X_train_features.shape}")
    USE_FEATURES = True
else:
    # Use flattened signals
    X_train_features = X_train.reshape(len(X_train), -1)
    X_val_features = X_val.reshape(len(X_val), -1)
    X_test_features = X_test.reshape(len(X_test), -1)
    print(f"\n  Using flattened signals: {X_train_features.shape}")
    USE_FEATURES = False

# Load label mapping
with open(os.path.join(MODEL_DIR, 'label_map.json'), 'r') as f:
    label_map = json.load(f)

num_classes = len(label_map)
print(f"\n  Classes: {num_classes}")
for idx, name in label_map.items():
    count = np.sum(y_train == int(idx))
    print(f"    {name}: {count} samples")

# ==========================================
# 2. TRAIN XGBOOST MODEL
# ==========================================

print("\n🔧 2. TRAINING XGBOOST")

# Calculate class weights for imbalanced data
unique, counts = np.unique(y_train, return_counts=True)
class_weights = len(y_train) / (num_classes * counts)
sample_weights = class_weights[y_train]

# XGBoost configuration
params = {
    'objective': 'multi:softprob',
    'num_class': num_classes,
    'max_depth': 6,
    'eta': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'eval_metric': 'mlogloss',
    'seed': 42
}

# Train with early stopping
dtrain = xgb.DMatrix(X_train_features, label=y_train, weight=sample_weights)
dval = xgb.DMatrix(X_val.reshape(len(X_val), -1), label=y_val)

evals = [(dtrain, 'train'), (dval, 'val')]
model = xgb.train(
    params,
    dtrain,
    num_boost_round=500,
    evals=evals,
    early_stopping_rounds=50,
    verbose_eval=50
)

print(f"\n  ✅ Training complete!")
print(f"  Best iteration: {model.best_iteration}")
print(f"  Best score: {model.best_score:.4f}")

# ==========================================
# 3. EVALUATION
# ==========================================

print("\n📊 3. MODEL EVALUATION")

# Predictions
dtest = xgb.DMatrix(X_test.reshape(len(X_test), -1))
y_pred_proba = model.predict(dtest)
y_pred = np.argmax(y_pred_proba, axis=1)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
top3_acc = top_k_accuracy_score(y_test, y_pred_proba, k=3)

print(f"\n  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  Top-3 Accuracy: {top3_acc:.4f} ({top3_acc*100:.2f}%)")

# Per-class metrics
precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_pred, average=None, zero_division=0
)

print(f"\n  Per-Class Performance:")
for idx in range(num_classes):
    label_name = label_map[str(idx)]
    print(f"    {label_name}: P={precision[idx]:.3f} R={recall[idx]:.3f} F1={f1[idx]:.3f} (n={support[idx]})")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\n  Confusion Matrix:")
print(cm)

# ==========================================
# 4. SAVE MODEL
# ==========================================

print("\n💾 4. SAVING MODEL")

# Save XGBoost model
model_path = os.path.join(MODEL_DIR, 'ekg_xgboost.json')
model.save_model(model_path)
print(f"  ✅ Saved: ekg_xgboost.json")

# Save as sklearn-compatible
sklearn_model = XGBClassifier()
sklearn_model._Booster = model
joblib.dump(sklearn_model, os.path.join(MODEL_DIR, 'ekg_xgboost.joblib'))
print(f"  ✅ Saved: ekg_xgboost.joblib")

# Save classes
classes_info = {
    'classes': [label_map[str(i)] for i in range(num_classes)],
    'num_classes': num_classes
}
with open(os.path.join(MODEL_DIR, 'ekg_classes.json'), 'w') as f:
    json.dump(classes_info, f, indent=2)
print(f"  ✅ Saved: ekg_classes.json")

# Save metrics
metrics = {
    'timestamp': datetime.now().isoformat(),
    'model_type': 'XGBoost',
    'accuracy': float(accuracy),
    'top3_accuracy': float(top3_acc),
    'precision_macro': float(np.mean(precision)),
    'recall_macro': float(np.mean(recall)),
    'f1_macro': float(np.mean(f1)),
    'num_features': X_train_features.shape[1],
    'num_classes': num_classes,
    'train_samples': len(X_train),
    'test_samples': len(X_test),
    'best_iteration': int(model.best_iteration)
}

with open(os.path.join(MODEL_DIR, 'ekg_xgboost_metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"  ✅ Saved: ekg_xgboost_metrics.json")

print("\n" + "=" * 80)
print("✅ XGBOOST TRAINING COMPLETE")
print("=" * 80)
print(f"\nModel ready for deployment!")
print(f"  Accuracy: {accuracy*100:.2f}%")
print(f"  Top-3: {top3_acc*100:.2f}%")
