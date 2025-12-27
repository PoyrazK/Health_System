"""
Golden Hour Model - Audit Script
Supheli metrikleri detayli analiz eder
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix
)
from sklearn.model_selection import train_test_split, StratifiedKFold

# Paths
BASE_DIR = Path('c:/Users/muham/OneDrive/Masaüstü/AdvanceUp2')
DATA_PATH = BASE_DIR / 'cleaned_dataset.csv'
MODEL_DIR = BASE_DIR / 'golden_hour_model' / 'models'

# Golden Hour Diseases
GOLDEN_HOUR_MAPPING = {
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
    'appendicitis': {'minutes': 1440, 'urgency': 4},
    'acute pancreatitis': {'minutes': 360, 'urgency': 4},
    'testicular torsion': {'minutes': 360, 'urgency': 4},
    'asthma': {'minutes': 30, 'urgency': 4},
}

print("=" * 70)
print("   GOLDEN HOUR MODEL - AUDIT")
print("=" * 70)

# 1. Load and analyze data
print("\n[1] VERI ANALIZI")
print("-" * 50)

df = pd.read_csv(DATA_PATH)
print(f"Toplam kayit: {len(df):,}")

# Filter for golden hour diseases
golden_hour_names = list(GOLDEN_HOUR_MAPPING.keys())
df_filtered = df[df['diseases'].str.lower().isin(golden_hour_names)].copy()
print(f"Golden Hour hastalik kayitlari: {len(df_filtered):,}")

# Add urgency labels
df_filtered['urgency_level'] = df_filtered['diseases'].str.lower().map(
    lambda x: GOLDEN_HOUR_MAPPING.get(x, {}).get('urgency', 3)
)

print(f"\nHastalik dagilimi:")
disease_counts = df_filtered['diseases'].str.lower().value_counts()
for disease, count in disease_counts.items():
    urgency = GOLDEN_HOUR_MAPPING.get(disease, {}).get('urgency', '?')
    print(f"  {disease}: {count} (Urgency {urgency})")

print(f"\nUrgency Level Dagilimi:")
urgency_counts = df_filtered['urgency_level'].value_counts().sort_index()
for level, count in urgency_counts.items():
    pct = count / len(df_filtered) * 100
    print(f"  Urgency {level}: {count:,} ({pct:.1f}%)")

# 2. Calculate class imbalance ratio
print("\n[2] CLASS IMBALANCE ANALIZI")
print("-" * 50)

if len(urgency_counts) == 2:
    min_class = urgency_counts.min()
    max_class = urgency_counts.max()
    imbalance_ratio = max_class / min_class
    print(f"Imbalance Ratio: {imbalance_ratio:.2f}:1")
    if imbalance_ratio > 10:
        print("WARNING: SIDDETLI DENGESIZLIK - Modelin cogunluk sinifina bias olabilir!")

# 3. Load model and test
print("\n[3] MODEL TESTI")
print("-" * 50)

model = joblib.load(MODEL_DIR / 'golden_hour_model.pkl')
scaler = joblib.load(MODEL_DIR / 'golden_hour_scaler.pkl')
artifacts = joblib.load(MODEL_DIR / 'golden_hour_artifacts.pkl')

feature_names = artifacts['feature_names']
label_map = artifacts['label_map']
reverse_map = {v: k for k, v in label_map.items()}

print(f"Feature sayisi: {len(feature_names)}")
print(f"Label mapping: {label_map}")

# Prepare features
available_features = [f for f in feature_names if f in df_filtered.columns]
print(f"Using {len(available_features)}/{len(feature_names)} features")

X = df_filtered[available_features].values
y = df_filtered['urgency_level'].values

# Use same split as training
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=42
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.176, stratify=y_temp, random_state=42
)

print(f"\nVeri Bolunmesi (GERCEK VERI - sentetik yok):")
print(f"  Train: {len(X_train)}")
print(f"  Validation: {len(X_val)}")
print(f"  Test: {len(X_test)}")

# Scale
X_train_scaled = scaler.transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Predict
y_train_adj = np.array([label_map[y] for y in y_train])
y_val_adj = np.array([label_map[y] for y in y_val])
y_test_adj = np.array([label_map[y] for y in y_test])

y_train_pred = model.predict(X_train_scaled)
y_val_pred = model.predict(X_val_scaled)
y_test_pred = model.predict(X_test_scaled)

# 4. Calculate ALL metrics
print("\n[4] DETAYLI METRIKLER")
print("-" * 50)

for name, y_true, y_pred in [
    ('Train', y_train_adj, y_train_pred),
    ('Validation', y_val_adj, y_val_pred),
    ('Test', y_test_adj, y_test_pred)
]:
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='macro')
    precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
    recall = recall_score(y_true, y_pred, average='macro', zero_division=0)
    
    print(f"\n{name}:")
    print(f"  Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
    print(f"  F1 Macro:  {f1:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print(f"  Confusion Matrix:")
    for i, row in enumerate(cm):
        print(f"    Urgency {reverse_map[i]}: {row}")

# 5. Check for data leakage indicators
print("\n[5] DATA LEAKAGE KONTROLU")
print("-" * 50)

# Check if there are duplicate rows
n_duplicates = df_filtered.duplicated(subset=available_features).sum()
pct_duplicates = n_duplicates / len(df_filtered) * 100
print(f"Duplicate satir sayisi: {n_duplicates} ({pct_duplicates:.1f}%)")

if pct_duplicates > 5:
    print("WARNING: YUKSEK DUPLICATE - Train/Test arasinda overlap olabilir!")

# Check feature variance
from sklearn.feature_selection import VarianceThreshold
selector = VarianceThreshold(threshold=0.01)
selector.fit(X)
low_variance_count = sum(~selector.get_support())
print(f"Dusuk varyansli feature: {low_variance_count}/{len(available_features)}")

# 6. Final assessment
print("\n" + "=" * 70)
print("   SONUC DEGERLENDIRMESI")
print("=" * 70)

test_acc = accuracy_score(y_test_adj, y_test_pred)
test_f1 = f1_score(y_test_adj, y_test_pred, average='macro')
train_f1 = f1_score(y_train_adj, y_train_pred, average='macro')
val_f1 = f1_score(y_val_adj, y_val_pred, average='macro')

overfit_gap = train_f1 - val_f1

print(f"\nHesaplanan Metrikler:")
print(f"   Test Accuracy: {test_acc:.4f}")
print(f"   Test F1:       {test_f1:.4f}")
print(f"   Overfit Gap:   {overfit_gap:.4f}")

if test_f1 >= 0.99:
    print("\nWARNING: TEST F1 > 0.99 - Potansiyel sorunlar:")
    print("   1. Veri cok basit veya dagilim dar olabilir")
    print("   2. Data leakage olabilir")
    print("   3. Sinif sayisi cok az (sadece 2)")
    
if overfit_gap < 0:
    print("\nWARNING: NEGATIF OVERFIT GAP - Olasi nedenler:")
    print("   1. Validation seti train'e cok benzer")
    print("   2. Sentetik veri augmentation sorunu")
    print("   3. Tesadufi varyans")

print("\nONERILER:")
print("   1. Daha fazla urgency seviyesi ekleyin (3-level yerine)")
print("   2. Daha dengeli veri seti olusturun")
print("   3. Farkli random seed ile tekrar test edin")
print("   4. Holdout validation ile capraz dogrulayin")
