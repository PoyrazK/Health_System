"""
Golden Hour Model - Data Leak & Overfit Audit
Comprehensive check for data leakage and overfitting
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_predict, StratifiedKFold
import sys

BASE_DIR = Path('c:/Users/muham/OneDrive/Masaüstü/AdvanceUp2')
DATA_PATH = BASE_DIR / 'cleaned_dataset.csv'
MODEL_DIR = BASE_DIR / 'golden_hour_model' / 'models'

sys.path.insert(0, str(BASE_DIR))
from golden_hour_model.config.urgency_mapping import get_urgency

print("="*70)
print("   DATA LEAK & OVERFIT AUDIT")
print("="*70)

# Load model and data
model = joblib.load(MODEL_DIR / 'golden_hour_model.pkl')
scaler = joblib.load(MODEL_DIR / 'golden_hour_scaler.pkl')
artifacts = joblib.load(MODEL_DIR / 'golden_hour_artifacts.pkl')

feature_names = artifacts['feature_names']
label_map = artifacts['label_map']
reverse_map = {v: k for k, v in label_map.items()}

df = pd.read_csv(DATA_PATH)
df['urgency_level'] = df['diseases'].str.lower().apply(get_urgency)

print(f"\n[1] VERI SETI BILGISI")
print("-"*50)
print(f"Toplam kayit: {len(df):,}")
print(f"Feature sayisi: {len(feature_names)}")
print(f"Sinif sayisi: {len(label_map)}")

# Check 1: Duplicate rows
print(f"\n[2] DUPLICATE KONTROLU")
print("-"*50)

# Full row duplicates
full_duplicates = df.duplicated().sum()
print(f"Tam satir duplicate: {full_duplicates} ({full_duplicates/len(df)*100:.2f}%)")

# Feature-only duplicates
feature_duplicates = df.duplicated(subset=feature_names).sum()
print(f"Feature duplicate: {feature_duplicates} ({feature_duplicates/len(df)*100:.2f}%)")

# Same features, different labels (data inconsistency)
df_features = df[feature_names + ['urgency_level']]
grouped = df_features.groupby(feature_names)['urgency_level'].nunique()
inconsistent = (grouped > 1).sum()
print(f"Ayni feature, farkli label: {inconsistent} grup")

if feature_duplicates > len(df) * 0.05:
    print("  WARNING: High duplicate rate - potential leakage risk!")
else:
    print("  OK: Duplicate rate acceptable")

# Check 2: Train/Test Overlap with same split
print(f"\n[3] TRAIN/TEST OVERLAP KONTROLU")
print("-"*50)

X = df[feature_names].values
y = df['urgency_level'].values

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, stratify=y, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.176, stratify=y_temp, random_state=42)

# Convert to hashable for comparison
train_hashes = set([tuple(row) for row in X_train])
test_hashes = set([tuple(row) for row in X_test])
val_hashes = set([tuple(row) for row in X_val])

train_test_overlap = len(train_hashes.intersection(test_hashes))
train_val_overlap = len(train_hashes.intersection(val_hashes))

print(f"Train-Test overlap: {train_test_overlap} samples")
print(f"Train-Val overlap: {train_val_overlap} samples")

if train_test_overlap > 0 or train_val_overlap > 0:
    print("  WARNING: Train/Test overlap detected - DATA LEAKAGE!")
else:
    print("  OK: No train/test overlap")

# Check 3: Overfit Analysis
print(f"\n[4] OVERFIT ANALIZI")
print("-"*50)

X_train_scaled = scaler.transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

y_train_adj = np.array([label_map[y] for y in y_train])
y_val_adj = np.array([label_map[y] for y in y_val])
y_test_adj = np.array([label_map[y] for y in y_test])

train_pred = model.predict(X_train_scaled)
val_pred = model.predict(X_val_scaled)
test_pred = model.predict(X_test_scaled)

train_f1 = f1_score(y_train_adj, train_pred, average='macro')
val_f1 = f1_score(y_val_adj, val_pred, average='macro')
test_f1 = f1_score(y_test_adj, test_pred, average='macro')

train_acc = accuracy_score(y_train_adj, train_pred)
val_acc = accuracy_score(y_val_adj, val_pred)
test_acc = accuracy_score(y_test_adj, test_pred)

print(f"Train F1: {train_f1:.4f}, Accuracy: {train_acc:.4f}")
print(f"Val F1:   {val_f1:.4f}, Accuracy: {val_acc:.4f}")
print(f"Test F1:  {test_f1:.4f}, Accuracy: {test_acc:.4f}")

overfit_gap_train_val = train_f1 - val_f1
overfit_gap_train_test = train_f1 - test_f1

print(f"\nOverfit Gap (Train-Val): {overfit_gap_train_val:.4f}")
print(f"Overfit Gap (Train-Test): {overfit_gap_train_test:.4f}")

if overfit_gap_train_test > 0.10:
    print("  WARNING: Significant overfitting detected!")
elif overfit_gap_train_test > 0.05:
    print("  CAUTION: Mild overfitting detected")
else:
    print("  OK: No significant overfitting")

# Negatif gap = validation/test > train (unusual)
if overfit_gap_train_test < -0.05:
    print("  NOTE: Negative gap - test better than train (synthetic data effect)")

# Check 4: Cross-validation stability
print(f"\n[5] CROSS-VALIDATION STABILITY")
print("-"*50)

from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier

# Quick CV check on raw data
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_model = XGBClassifier(
    max_depth=6, n_estimators=100, learning_rate=0.1,
    random_state=42, n_jobs=-1, verbosity=0
)

X_all = df[feature_names].values
y_all = np.array([label_map[y] for y in df['urgency_level'].values])

cv_scores = cross_val_score(cv_model, X_all, y_all, cv=cv, scoring='f1_macro', n_jobs=-1)
print(f"CV F1 Scores: {cv_scores.round(4)}")
print(f"CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

cv_variance = cv_scores.std()
if cv_variance > 0.05:
    print("  WARNING: High CV variance - model unstable across folds")
else:
    print("  OK: Low CV variance - model stable")

# Check 5: Per-class performance
print(f"\n[6] PER-CLASS PERFORMANS")
print("-"*50)

for idx in sorted(label_map.values()):
    mask = y_test_adj == idx
    if mask.sum() > 0:
        class_pred = test_pred[mask]
        class_true = y_test_adj[mask]
        class_acc = accuracy_score(class_true, class_pred)
        print(f"Urgency {reverse_map[idx]}: Accuracy={class_acc:.4f} (n={mask.sum()})")

# Check 6: Confusion matrix analysis
print(f"\n[7] CONFUSION MATRIX ANALIZI")
print("-"*50)

cm = confusion_matrix(y_test_adj, test_pred)
print("Confusion Matrix:")
print(f"         Predicted: {[f'U{reverse_map[i]}' for i in sorted(label_map.values())]}")
for i in sorted(label_map.values()):
    print(f"True U{reverse_map[i]}: {cm[i]}")

# Check for class collapse
diagonal = np.diag(cm)
off_diagonal_max = cm.max(axis=1) - diagonal
if any(off_diagonal_max > diagonal * 0.5):
    print("  WARNING: Some classes have high confusion with others")
else:
    print("  OK: Classes are well separated")

# Final summary
print("\n" + "="*70)
print("   SONUC OZETI")
print("="*70)

issues = []
if train_test_overlap > 0:
    issues.append("Train/Test overlap (DATA LEAKAGE)")
if overfit_gap_train_test > 0.10:
    issues.append("Significant overfitting")
if cv_variance > 0.05:
    issues.append("High CV variance")
if feature_duplicates > len(df) * 0.10:
    issues.append("High duplicate rate")

if issues:
    print("\nTESPIT EDILEN SORUNLAR:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\n  OK: Model data leak ve overfit kontrollerini gecti!")
    print(f"\n  Final Metrics:")
    print(f"    Test F1 (Macro): {test_f1:.4f}")
    print(f"    Test Accuracy: {test_acc:.4f}")
    print(f"    Overfit Gap: {overfit_gap_train_test:.4f}")
    print(f"    CV Stability: +/- {cv_variance*2:.4f}")
