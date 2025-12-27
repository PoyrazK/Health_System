"""
MIT-BIH EKG Data Preparation - FIXED VERSION
Patient-Level Split ile Data Leakage Önleme

DÜZELTMELER:
1. ✅ Patient-level split (aynı hasta sadece bir set'te)
2. ✅ Scaler SADECE train üzerinde fit
3. ✅ SMOTE sadece train'e uygulama
4. ✅ Test verisi ayrı tutuldu
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from collections import Counter
import os
import json
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("MIT-BIH VERI HAZIRLAMA - DUZELTILMIS VERSIYON")
print("Patient-Level Split ile Data Leakage Onleme")
print("=" * 80)

# ==========================================
# CONFIGURATION
# ==========================================

DATA_PATH = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\notebooks\ekg\MIT-BIH Arrhythmia Database.csv"
OUTPUT_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# MIT-BIH label mapping to 5 classes (AAMI standard)
LABEL_MAPPING = {
    'N': 'N', 'L': 'N', 'R': 'N', 'e': 'N', 'j': 'N',
    'A': 'S', 'a': 'S', 'J': 'S', 'S': 'S',
    'V': 'V', 'E': 'V',
    'F': 'F',
    '/': 'Q', 'f': 'Q', 'Q': 'Q', '!': 'Q', '+': 'Q', '|': 'Q', '~': 'Q', 'x': 'Q',
}

# ==========================================
# 1. DATA LOADING
# ==========================================

print("\n[1/8] VERI YUKLEME")
df = pd.read_csv(DATA_PATH)
print(f"   Yuklenen ornek: {len(df):,}")
print(f"   Sutunlar: {list(df.columns)[:10]}...")

# ==========================================
# 2. PATIENT ID EXTRACTION
# ==========================================

print("\n[2/8] HASTA BILGISI CIKARMA")

# 'record' column contains patient/record ID
if 'record' in df.columns:
    patient_col = 'record'
    unique_patients = df[patient_col].unique()
    print(f"   Hasta/Record sayisi: {len(unique_patients)}")
    print(f"   Record'lar: {unique_patients[:10]}...")
else:
    print("   UYARI: 'record' kolonu yok! Sample-level split yapilacak.")
    df['record'] = range(len(df))
    patient_col = 'record'
    unique_patients = df[patient_col].unique()

# ==========================================
# 3. LABEL MAPPING
# ==========================================

print("\n[3/8] ETIKET ESLEME (5 sinif)")

label_col = 'type' if 'type' in df.columns else df.columns[-1]
df['label_5class'] = df[label_col].map(lambda x: LABEL_MAPPING.get(str(x), 'Q'))

print(f"   Sinif dagilimi:")
for label, count in df['label_5class'].value_counts().items():
    pct = count / len(df) * 100
    print(f"     {label}: {count:,} ({pct:.1f}%)")

# ==========================================
# 4. PATIENT-LEVEL SPLIT (KRITIK!)
# ==========================================

print("\n[4/8] PATIENT-LEVEL SPLIT (DATA LEAKAGE ONLEME)")

# Get unique patients
patients = df[patient_col].unique()
n_patients = len(patients)

print(f"   Toplam hasta: {n_patients}")

# Shuffle patients
np.random.seed(42)
np.random.shuffle(patients)

# Split patients: 70% train, 15% val, 15% test
train_end = int(n_patients * 0.70)
val_end = int(n_patients * 0.85)

train_patients = patients[:train_end]
val_patients = patients[train_end:val_end]
test_patients = patients[val_end:]

print(f"   Train hastalari: {len(train_patients)}")
print(f"   Val hastalari: {len(val_patients)}")
print(f"   Test hastalari: {len(test_patients)}")

# Check NO overlap
assert len(set(train_patients) & set(test_patients)) == 0, "LEAKAGE: Train-Test overlap!"
assert len(set(train_patients) & set(val_patients)) == 0, "LEAKAGE: Train-Val overlap!"
assert len(set(val_patients) & set(test_patients)) == 0, "LEAKAGE: Val-Test overlap!"
print(f"   [OK] Hasta overlap YOK - Leakage onlendi!")

# Create masks
train_mask = df[patient_col].isin(train_patients)
val_mask = df[patient_col].isin(val_patients)
test_mask = df[patient_col].isin(test_patients)

df_train = df[train_mask].copy()
df_val = df[val_mask].copy()
df_test = df[test_mask].copy()

print(f"\n   Ornek sayilari:")
print(f"     Train: {len(df_train):,} ({len(df_train)/len(df)*100:.1f}%)")
print(f"     Val:   {len(df_val):,} ({len(df_val)/len(df)*100:.1f}%)")
print(f"     Test:  {len(df_test):,} ({len(df_test)/len(df)*100:.1f}%)")

# ==========================================
# 5. FEATURE EXTRACTION
# ==========================================

print("\n[5/8] OZELLIK CIKARMA")

exclude_cols = ['record', 'type', 'label_5class']
feature_cols = [col for col in df.columns if col not in exclude_cols]

print(f"   Ozellik sayisi: {len(feature_cols)}")

X_train = df_train[feature_cols].values
X_val = df_val[feature_cols].values
X_test = df_test[feature_cols].values

y_train = df_train['label_5class'].values
y_val = df_val['label_5class'].values
y_test = df_test['label_5class'].values

# Handle NaN
for X in [X_train, X_val, X_test]:
    if np.isnan(X).any():
        col_means = np.nanmean(X_train, axis=0)  # Use TRAIN means only!
        nan_idx = np.where(np.isnan(X))
        X[nan_idx] = np.take(col_means, nan_idx[1])

print(f"   [OK] NaN degerler duzeltildi (train ortalamasi ile)")

# ==========================================
# 6. NORMALIZATION (SADECE TRAIN UZERINDE FIT!)
# ==========================================

print("\n[6/8] NORMALIZASYON (Scaler sadece TRAIN uzerinde fit)")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # FIT sadece train!
X_val_scaled = scaler.transform(X_val)          # Transform only
X_test_scaled = scaler.transform(X_test)        # Transform only

print(f"   [OK] Scaler SADECE train uzerinde fit edildi")
print(f"   Train mean: {X_train_scaled.mean():.6f}")
print(f"   Val mean: {X_val_scaled.mean():.6f}")
print(f"   Test mean: {X_test_scaled.mean():.6f}")

# Save scaler
joblib.dump(scaler, os.path.join(OUTPUT_DIR, 'ekg_scaler_fixed.joblib'))

# ==========================================
# 7. LABEL ENCODING
# ==========================================

print("\n[7/8] ETIKET KODLAMA")

label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_val_encoded = label_encoder.transform(y_val)
y_test_encoded = label_encoder.transform(y_test)

print(f"   Siniflar: {label_encoder.classes_}")
print(f"   Kodlama: {dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))}")

# ==========================================
# 8. SMOTE (SADECE TRAIN'E!)
# ==========================================

print("\n[8/8] SMOTE SINIF DENGELEME (sadece TRAIN)")

print(f"   SMOTE oncesi train dagilimi:")
for label, count in Counter(y_train_encoded).items():
    print(f"     {label_encoder.classes_[label]}: {count:,}")

# Apply SMOTE only to train
smote = SMOTE(sampling_strategy='auto', random_state=42, k_neighbors=3)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train_encoded)

print(f"\n   SMOTE sonrasi train dagilimi:")
for label, count in Counter(y_train_balanced).items():
    print(f"     {label_encoder.classes_[label]}: {count:,}")

# Val and Test remain UNCHANGED
print(f"\n   [OK] Val ve Test degistirilMEDI (orijinal dagitim)")
print(f"   Test dagilimi:")
for label, count in Counter(y_test_encoded).items():
    print(f"     {label_encoder.classes_[label]}: {count:,}")

# ==========================================
# SAVE
# ==========================================

print("\n" + "=" * 80)
print("KAYDETME")
print("=" * 80)

# Save as numpy arrays
np.savez_compressed(
    os.path.join(OUTPUT_DIR, 'ekg_data_fixed.npz'),
    X_train=X_train_balanced,
    X_val=X_val_scaled,
    X_test=X_test_scaled,
    y_train=y_train_balanced,
    y_val=y_val_encoded,
    y_test=y_test_encoded
)
print(f"   [OK] ekg_data_fixed.npz")

# Save label mapping
label_map = {int(i): str(label) for i, label in enumerate(label_encoder.classes_)}
with open(os.path.join(OUTPUT_DIR, 'label_map_fixed.json'), 'w') as f:
    json.dump(label_map, f, indent=2)
print(f"   [OK] label_map_fixed.json")

# Save test patient IDs for verification
test_info = {
    'test_patients': test_patients.tolist(),
    'test_samples': len(X_test),
    'train_patients': train_patients.tolist(),
    'train_samples_original': len(X_train),
    'train_samples_smote': len(X_train_balanced)
}
with open(os.path.join(OUTPUT_DIR, 'split_info.json'), 'w') as f:
    json.dump(test_info, f, indent=2)
print(f"   [OK] split_info.json")

# Save metadata
metadata = {
    'timestamp': datetime.now().isoformat(),
    'version': 'FIXED_v2_patient_level_split',
    'source': 'MIT-BIH Arrhythmia Database',
    'total_patients': int(n_patients),
    'train_patients': int(len(train_patients)),
    'val_patients': int(len(val_patients)),
    'test_patients': int(len(test_patients)),
    'train_samples_original': int(len(X_train)),
    'train_samples_smote': int(len(X_train_balanced)),
    'val_samples': int(len(X_val)),
    'test_samples': int(len(X_test)),
    'features': int(X_train_balanced.shape[1]),
    'classes': list(label_encoder.classes_),
    'patient_overlap': False,
    'scaler_fit_on': 'train_only',
    'smote_applied_to': 'train_only'
}

with open(os.path.join(OUTPUT_DIR, 'preprocessing_metadata_fixed.json'), 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   [OK] preprocessing_metadata_fixed.json")

# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 80)
print("VERI HAZIRLAMA TAMAMLANDI - DUZELTILMIS VERSIYON")
print("=" * 80)

print(f"""
OZET:
   Toplam hasta: {n_patients}
   Train hastalari: {len(train_patients)} -> {len(X_train_balanced):,} ornek (SMOTE)
   Val hastalari: {len(val_patients)} -> {len(X_val):,} ornek
   Test hastalari: {len(test_patients)} -> {len(X_test):,} ornek (DEGISTIRILMEDI)

DUZELTMELER:
   [OK] Patient-level split (ayni hasta train/test'te OLMAZ)
   [OK] Scaler sadece train uzerinde fit edildi
   [OK] SMOTE sadece train'e uygulandi
   [OK] Test verisi orijinal dagitimda

BEKLENEN GERCEK ACCURACY: %85-92 (inter-patient)

SONRAKI ADIM:
   python ai-service/ekg_train_xgboost_fixed.py
""")
