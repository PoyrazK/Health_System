"""
EKG XGBoost Training - OPTIMIZED VERSION
Sorunları düzeltilmiş versiyon:
1. F sınıfı için agresif SMOTE
2. Overfit için güçlü regularization
3. Q sınıfı için cost-sensitive learning
"""

import numpy as np
import json
import os
import joblib
from datetime import datetime
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from collections import Counter
import xgboost as xgb
import pandas as pd

print("=" * 80)
print("EKG XGBOOST EGITIMI - OPTIMIZE EDILMIS")
print("=" * 80)

# ==========================================
# CONFIGURATION
# ==========================================

MODEL_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg"
DATA_PATH = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\notebooks\ekg\MIT-BIH Arrhythmia Database.csv"

# Label mapping
LABEL_MAPPING = {
    'N': 'N', 'L': 'N', 'R': 'N', 'e': 'N', 'j': 'N',
    'A': 'S', 'a': 'S', 'J': 'S', 'S': 'S',
    'V': 'V', 'E': 'V',
    'F': 'F',
    '/': 'Q', 'f': 'Q', 'Q': 'Q', '!': 'Q', '+': 'Q', '|': 'Q', '~': 'Q', 'x': 'Q',
}

# ==========================================
# 1. LOAD AND PREPARE DATA
# ==========================================

print("\n[1/6] VERI HAZIRLAMA")

df = pd.read_csv(DATA_PATH)
print(f"   Toplam ornek: {len(df):,}")

# Label mapping
label_col = 'type'
df['label_5class'] = df[label_col].map(lambda x: LABEL_MAPPING.get(str(x), 'Q'))

# Patient-level split
patients = df['record'].unique()
np.random.seed(42)
np.random.shuffle(patients)

n = len(patients)
train_patients = patients[:int(n*0.7)]
val_patients = patients[int(n*0.7):int(n*0.85)]
test_patients = patients[int(n*0.85):]

print(f"   Hastalar: Train={len(train_patients)}, Val={len(val_patients)}, Test={len(test_patients)}")

df_train = df[df['record'].isin(train_patients)].copy()
df_val = df[df['record'].isin(val_patients)].copy()
df_test = df[df['record'].isin(test_patients)].copy()

# Feature extraction
exclude_cols = ['record', 'type', 'label_5class']
feature_cols = [c for c in df.columns if c not in exclude_cols]

X_train = df_train[feature_cols].values
X_val = df_val[feature_cols].values
X_test = df_test[feature_cols].values

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_train = le.fit_transform(df_train['label_5class'].values)
y_val = le.transform(df_val['label_5class'].values)
y_test = le.transform(df_test['label_5class'].values)

print(f"   Siniflar: {le.classes_}")

# ==========================================
# 2. SCALER (TRAIN ONLY)
# ==========================================

print("\n[2/6] NORMALIZASYON")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

print(f"   [OK] Scaler sadece train uzerinde fit edildi")

# ==========================================
# 3. AGGRESSIVE SMOTE FOR F CLASS
# ==========================================

print("\n[3/6] AGRESIF SMOTE (F sinifi icin)")

print(f"   SMOTE oncesi:")
for label, count in sorted(Counter(y_train).items()):
    print(f"     {le.classes_[label]}: {count:,}")

# Calculate target ratios - boost minority classes more
class_counts = Counter(y_train)
max_count = max(class_counts.values())

# Custom strategy: minority classes get 50% of majority
sampling_strategy = {}
for class_idx, count in class_counts.items():
    if count < max_count * 0.5:
        sampling_strategy[class_idx] = int(max_count * 0.5)  # At least 50% of majority

if sampling_strategy:
    smote = SMOTE(sampling_strategy=sampling_strategy, random_state=42, k_neighbors=3)
else:
    smote = SMOTE(sampling_strategy='auto', random_state=42, k_neighbors=3)

X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)

print(f"\n   SMOTE sonrasi:")
for label, count in sorted(Counter(y_train_balanced).items()):
    print(f"     {le.classes_[label]}: {count:,}")

# ==========================================
# 4. COST-SENSITIVE CLASS WEIGHTS
# ==========================================

print("\n[4/6] COST-SENSITIVE CLASS WEIGHTS")

# Give more weight to critical classes (V, F) and less to N
# V (ventricular) and F (fusion) are life-threatening
class_weight_map = {
    'N': 1.0,    # Normal - baseline
    'S': 2.0,    # SVEB - moderate
    'V': 5.0,    # VEB - CRITICAL (life-threatening)
    'F': 8.0,    # Fusion - VERY CRITICAL (rare, important)
    'Q': 1.5     # Noise - some weight
}

# Convert to sample weights
sample_weights = np.array([
    class_weight_map[le.classes_[label]] 
    for label in y_train_balanced
])

print(f"   Class weights:")
for cls, weight in class_weight_map.items():
    print(f"     {cls}: {weight}")

# ==========================================
# 5. REGULARIZED XGBOOST TRAINING
# ==========================================

print("\n[5/6] REGULARIZED XGBOOST EGITIMI")

# Stronger regularization to reduce overfitting
params = {
    'objective': 'multi:softprob',
    'num_class': len(le.classes_),
    
    # REGULARIZATION (overfiti azaltmak icin)
    'max_depth': 4,           # 6 -> 4 (daha sade model)
    'min_child_weight': 5,    # 1 -> 5 (daha az split)
    'gamma': 0.3,             # 0 -> 0.3 (split icin min gain)
    'reg_alpha': 0.5,         # L1 regularization
    'reg_lambda': 2.0,        # L2 regularization
    
    # LEARNING
    'eta': 0.05,              # 0.1 -> 0.05 (daha yavas ogrenme)
    'subsample': 0.7,         # 0.8 -> 0.7 (daha az veri)
    'colsample_bytree': 0.7,  # 0.8 -> 0.7 (daha az feature)
    
    'eval_metric': 'mlogloss',
    'seed': 42
}

print(f"   Regularization parametreleri:")
print(f"     max_depth: {params['max_depth']}")
print(f"     min_child_weight: {params['min_child_weight']}")
print(f"     gamma: {params['gamma']}")
print(f"     reg_alpha: {params['reg_alpha']}")
print(f"     reg_lambda: {params['reg_lambda']}")

# Create DMatrix
dtrain = xgb.DMatrix(X_train_balanced, label=y_train_balanced, weight=sample_weights)
dval = xgb.DMatrix(X_val_scaled, label=y_val)
dtest = xgb.DMatrix(X_test_scaled, label=y_test)

# Train
evals = [(dtrain, 'train'), (dval, 'val')]
model = xgb.train(
    params,
    dtrain,
    num_boost_round=1000,
    evals=evals,
    early_stopping_rounds=100,
    verbose_eval=100
)

print(f"\n   Best iteration: {model.best_iteration}")

# ==========================================
# 6. EVALUATION
# ==========================================

print("\n[6/6] MODEL DEGERLENDIRME")

# Predictions
y_train_pred = model.predict(dtrain).argmax(axis=1)
y_val_pred = model.predict(dval).argmax(axis=1)
y_test_pred = model.predict(dtest).argmax(axis=1)

train_acc = accuracy_score(y_train_balanced, y_train_pred)
val_acc = accuracy_score(y_val, y_val_pred)
test_acc = accuracy_score(y_test, y_test_pred)

gap = train_acc - test_acc

print(f"\n   ACCURACY:")
print(f"     Train: {train_acc*100:.2f}%")
print(f"     Val:   {val_acc*100:.2f}%")
print(f"     Test:  {test_acc*100:.2f}%")
print(f"     Gap:   {gap*100:.2f}%")

if gap < 0.05:
    print(f"   [OK] Gap kabul edilebilir (<5%)")
elif gap < 0.10:
    print(f"   [!] Gap orta (5-10%)")
else:
    print(f"   [!!] Gap hala yuksek (>10%)")

# F1 scores
print(f"\n   F1-SCORES:")
class_names = list(le.classes_)
report = classification_report(y_test, y_test_pred, target_names=class_names, output_dict=True)

for cls in class_names:
    if cls in report:
        f1 = report[cls]['f1-score']
        prec = report[cls]['precision']
        rec = report[cls]['recall']
        sup = report[cls]['support']
        print(f"     {cls}: F1={f1:.3f} (P={prec:.3f}, R={rec:.3f}, n={sup})")

# Macro F1
macro_f1 = f1_score(y_test, y_test_pred, average='macro')
print(f"\n   Macro F1: {macro_f1:.3f}")

# Confusion Matrix
print(f"\n   CONFUSION MATRIX:")
print(confusion_matrix(y_test, y_test_pred))

# ==========================================
# SAVE
# ==========================================

print("\n" + "=" * 80)
print("KAYDETME")
print("=" * 80)

# Save model
model.save_model(os.path.join(MODEL_DIR, 'ekg_xgboost_optimized.json'))
print(f"   [OK] ekg_xgboost_optimized.json")

# Save scaler
joblib.dump(scaler, os.path.join(MODEL_DIR, 'ekg_scaler_optimized.joblib'))
print(f"   [OK] ekg_scaler_optimized.joblib")

# Save label encoder
joblib.dump(le, os.path.join(MODEL_DIR, 'ekg_label_encoder.joblib'))
print(f"   [OK] ekg_label_encoder.joblib")

# Save metrics
metrics = {
    'timestamp': datetime.now().isoformat(),
    'version': 'OPTIMIZED_v3_regularized',
    'train_accuracy': float(train_acc),
    'val_accuracy': float(val_acc),
    'test_accuracy': float(test_acc),
    'train_test_gap': float(gap),
    'macro_f1': float(macro_f1),
    'per_class_f1': {cls: float(report[cls]['f1-score']) for cls in class_names if cls in report},
    'regularization': {
        'max_depth': params['max_depth'],
        'min_child_weight': params['min_child_weight'],
        'gamma': params['gamma'],
        'reg_alpha': params['reg_alpha'],
        'reg_lambda': params['reg_lambda']
    },
    'class_weights': class_weight_map,
    'best_iteration': int(model.best_iteration)
}

with open(os.path.join(MODEL_DIR, 'ekg_xgboost_metrics_optimized.json'), 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"   [OK] ekg_xgboost_metrics_optimized.json")

# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 80)
print("OPTIMIZASYON TAMAMLANDI")
print("=" * 80)

print(f"""
SONUC KARSILASTIRMASI:

                    ONCEKI      SIMDI       DEGISIM
Train Accuracy:     99.99%      {train_acc*100:.2f}%
Val Accuracy:       98.19%      {val_acc*100:.2f}%
Test Accuracy:      92.47%      {test_acc*100:.2f}%
Train-Test Gap:     7.52%       {gap*100:.2f}%

IYILESTIRMELER:
- [OK] Regularization artirildi (max_depth 6->4)
- [OK] Cost-sensitive weights eklendi
- [OK] F sinifi icin aggressive SMOTE

MODEL DOSYALARI:
- ekg_xgboost_optimized.json
- ekg_scaler_optimized.joblib
- ekg_label_encoder.joblib
""")
