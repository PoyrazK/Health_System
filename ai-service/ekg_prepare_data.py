"""
MIT-BIH EKG Data Preparation for Model Training
Optimizes data for maximum model performance
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
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
print("🔧 MIT-BIH VERİ HAZIRLAMA - OPTİMAL EĞİTİM VERİSİ")
print("=" * 80)

# ==========================================
# CONFIGURATION
# ==========================================

DATA_PATH = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\notebooks\ekg\MIT-BIH Arrhythmia Database.csv"
OUTPUT_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# MIT-BIH label mapping to 5 classes
# Based on AAMI standard
LABEL_MAPPING = {
    # Normal beats (N class)
    'N': 'N',      # Normal beat
    'L': 'N',      # Left bundle branch block beat
    'R': 'N',      # Right bundle branch block beat
    'e': 'N',      # Atrial escape beat
    'j': 'N',      # Nodal (junctional) escape beat
    
    # SVEB - Supraventricular Ectopic Beats (S class)
    'A': 'S',      # Atrial premature beat
    'a': 'S',      # Aberrated atrial premature beat
    'J': 'S',      # Nodal (junctional) premature beat
    'S': 'S',      # Supraventricular premature beat
    
    # VEB - Ventricular Ectopic Beats (V class)
    'V': 'V',      # Premature ventricular contraction
    'E': 'V',      # Ventricular escape beat
    
    # Fusion beats (F class)
    'F': 'F',      # Fusion of ventricular and normal beat
    
    # Unknown/Noise (Q class)
    '/': 'Q',      # Paced beat
    'f': 'Q',      # Fusion of paced and normal beat
    'Q': 'Q',      # Unclassifiable beat
    '!': 'Q',      # Ventricular flutter wave
    '+': 'Q',      # Rhythm change
    '|': 'Q',      # Isolated QRS-like artifact
    '~': 'Q',      # Signal quality change
    'x': 'Q',      # Non-conducted P-wave
}

# 5-class urgency levels
URGENCY_LEVELS = {
    'N': {'level': 0, 'name': 'Normal', 'urgency': 'Düşük'},
    'S': {'level': 1, 'name': 'SVEB', 'urgency': 'Orta'},
    'F': {'level': 2, 'name': 'Fusion', 'urgency': 'Orta-Yüksek'},
    'V': {'level': 3, 'name': 'VEB', 'urgency': 'Yüksek'},
    'Q': {'level': 4, 'name': 'Belirsiz', 'urgency': 'Değerlendirme Gerekli'}
}

# ==========================================
# 1. DATA LOADING
# ==========================================

print("\n📂 1. VERİ YÜKLEME")
df = pd.read_csv(DATA_PATH)
print(f"   • Yüklenen örnek: {len(df):,}")
print(f"   • Özellik sayısı: {len(df.columns)}")

# Identify columns
print(f"\n   Sütunlar: {df.columns.tolist()[:10]}...")

# ==========================================
# 2. LABEL PROCESSING
# ==========================================

print("\n🏷️ 2. ETİKET İŞLEME")

# Find label column
label_col = 'type' if 'type' in df.columns else df.columns[-1]
print(f"   • Etiket sütunu: {label_col}")

# Show original distribution
print(f"\n   Orijinal dağılım:")
original_dist = df[label_col].value_counts()
for label, count in original_dist.items():
    pct = count / len(df) * 100
    print(f"     {label}: {count:,} ({pct:.1f}%)")

# Map to 5 classes
print(f"\n   5-sınıf mapping uygulanıyor...")
df['label_5class'] = df[label_col].map(lambda x: LABEL_MAPPING.get(str(x), 'Q'))

# Show new distribution
print(f"\n   Yeni dağılım (5 sınıf):")
new_dist = df['label_5class'].value_counts()
for label, count in new_dist.items():
    pct = count / len(df) * 100
    urgency = URGENCY_LEVELS[label]['urgency']
    print(f"     {label} ({URGENCY_LEVELS[label]['name']}): {count:,} ({pct:.1f}%) - Aciliyet: {urgency}")

# ==========================================
# 3. FEATURE SELECTION & CLEANING
# ==========================================

print("\n🔧 3. ÖZELLİK SEÇİMİ VE TEMİZLİK")

# Select feature columns (all numeric except labels)
exclude_cols = ['record', 'type', 'label_5class']
feature_cols = [col for col in df.columns if col not in exclude_cols]

print(f"   • Özellik sütunları: {len(feature_cols)}")
print(f"   • Kullanılacak özellikler: {feature_cols[:10]}...")

# Extract features and labels
X = df[feature_cols].values
y = df['label_5class'].values

print(f"\n   • X shape: {X.shape}")
print(f"   • y shape: {y.shape}")

# Handle any NaN values
nan_count = np.isnan(X).sum()
if nan_count > 0:
    print(f"   ⚠️ NaN değerler bulundu: {nan_count}")
    print(f"      → Ortalama ile doldurma uygulanıyor...")
    col_means = np.nanmean(X, axis=0)
    nan_indices = np.where(np.isnan(X))
    X[nan_indices] = np.take(col_means, nan_indices[1])
    print(f"      ✅ NaN değerler düzeltildi")
else:
    print(f"   ✅ NaN değer yok")

# ==========================================
# 4. FEATURE ENGINEERING (Additional)
# ==========================================

print("\n🔬 4. EK ÖZELLİK MÜHENDİSLİĞİ")

# Create additional ratio features for better discrimination
original_feature_count = X.shape[1]

# Get column indices for specific features
lead0_cols = [i for i, col in enumerate(feature_cols) if col.startswith('0_')]
lead1_cols = [i for i, col in enumerate(feature_cols) if col.startswith('1_')]

# If we have both leads, create cross-lead features
if lead0_cols and lead1_cols:
    print(f"   • 2-lead correlation özellikleri ekleniyor...")
    
    # Create new features list
    new_features = []
    
    # RR interval ratio
    pre_rr_0_idx = feature_cols.index('0_pre-RR') if '0_pre-RR' in feature_cols else None
    post_rr_0_idx = feature_cols.index('0_post-RR') if '0_post-RR' in feature_cols else None
    
    if pre_rr_0_idx and post_rr_0_idx:
        rr_ratio = X[:, pre_rr_0_idx] / (X[:, post_rr_0_idx] + 1e-6)
        new_features.append(rr_ratio.reshape(-1, 1))
    
    # QRS interval x RR ratio (arrhythmia indicator)
    qrs_idx = feature_cols.index('0_qrs_interval') if '0_qrs_interval' in feature_cols else None
    if qrs_idx and pre_rr_0_idx:
        qrs_rr_ratio = X[:, qrs_idx] / (X[:, pre_rr_0_idx] + 1e-6)
        new_features.append(qrs_rr_ratio.reshape(-1, 1))
    
    # QT / RR ratio (corrected QT proxy)
    qt_idx = feature_cols.index('0_qt_interval') if '0_qt_interval' in feature_cols else None
    if qt_idx and pre_rr_0_idx:
        qt_rr_ratio = X[:, qt_idx] / np.sqrt(X[:, pre_rr_0_idx] + 1e-6)
        new_features.append(qt_rr_ratio.reshape(-1, 1))
    
    if new_features:
        X = np.hstack([X] + new_features)
        print(f"   → {len(new_features)} yeni özellik eklendi")

print(f"   • Final özellik sayısı: {X.shape[1]} (orijinal: {original_feature_count})")

# ==========================================
# 5. NORMALIZATION
# ==========================================

print("\n📏 5. NORMALİZASYON")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"   • Z-score normalizasyon uygulandı")
print(f"   • Mean: {X_scaled.mean():.6f}")
print(f"   • Std: {X_scaled.std():.6f}")

# Save scaler
scaler_path = os.path.join(OUTPUT_DIR, 'ekg_scaler.joblib')
joblib.dump(scaler, scaler_path)
print(f"   ✅ Scaler kaydedildi: ekg_scaler.joblib")

# ==========================================
# 6. LABEL ENCODING
# ==========================================

print("\n🔢 6. ETİKET KODLAMA")

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

print(f"   • Sınıflar: {label_encoder.classes_}")
print(f"   • Kodlama: {dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))}")

# ==========================================
# 7. TRAIN/VAL/TEST SPLIT
# ==========================================

print("\n📊 7. VERİ BÖLME (70/15/15)")

# First split: train+val / test
X_temp, X_test, y_temp, y_test = train_test_split(
    X_scaled, y_encoded,
    test_size=0.15,
    stratify=y_encoded,
    random_state=42
)

# Second split: train / val
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp,
    test_size=0.176,  # 0.15/0.85 ≈ 0.176
    stratify=y_temp,
    random_state=42
)

print(f"   • Train: {len(X_train):,} örnek ({len(X_train)/len(X_scaled)*100:.1f}%)")
print(f"   • Val:   {len(X_val):,} örnek ({len(X_val)/len(X_scaled)*100:.1f}%)")
print(f"   • Test:  {len(X_test):,} örnek ({len(X_test)/len(X_scaled)*100:.1f}%)")

# ==========================================
# 8. SMOTE BALANCING (Train only)
# ==========================================

print("\n⚖️ 8. SMOTE SINIF DENGELEMESİ")

print(f"   SMOTE öncesi train dağılımı:")
before_dist = Counter(y_train)
for label, count in sorted(before_dist.items()):
    class_name = label_encoder.inverse_transform([label])[0]
    print(f"     {class_name}: {count:,}")

# Apply SMOTE
smote = SMOTE(sampling_strategy='auto', random_state=42, k_neighbors=3)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

print(f"\n   SMOTE sonrası train dağılımı:")
after_dist = Counter(y_train_balanced)
for label, count in sorted(after_dist.items()):
    class_name = label_encoder.inverse_transform([label])[0]
    print(f"     {class_name}: {count:,}")

print(f"\n   • SMOTE öncesi: {len(X_train):,} örnek")
print(f"   • SMOTE sonrası: {len(X_train_balanced):,} örnek")

# ==========================================
# 9. SAVE PROCESSED DATA
# ==========================================

print("\n💾 9. VERİ KAYDETME")

# Save as numpy arrays
np.savez_compressed(
    os.path.join(OUTPUT_DIR, 'ekg_data.npz'),
    X_train=X_train_balanced,
    X_val=X_val,
    X_test=X_test,
    y_train=y_train_balanced,
    y_val=y_val,
    y_test=y_test
)
print(f"   ✅ ekg_data.npz")

# Save label mapping
label_map = {int(i): str(label) for i, label in enumerate(label_encoder.classes_)}
with open(os.path.join(OUTPUT_DIR, 'label_map.json'), 'w') as f:
    json.dump(label_map, f, indent=2)
print(f"   ✅ label_map.json")

# Save urgency mapping
with open(os.path.join(OUTPUT_DIR, 'urgency_levels.json'), 'w') as f:
    json.dump(URGENCY_LEVELS, f, indent=2, ensure_ascii=False)
print(f"   ✅ urgency_levels.json")

# Save feature names
feature_names = feature_cols + ['rr_ratio', 'qrs_rr_ratio', 'qt_rr_ratio'][:X.shape[1] - original_feature_count]
with open(os.path.join(OUTPUT_DIR, 'feature_names.json'), 'w') as f:
    json.dump(feature_names, f, indent=2)
print(f"   ✅ feature_names.json")

# Save preprocessing metadata
metadata = {
    'timestamp': datetime.now().isoformat(),
    'source_file': 'MIT-BIH Arrhythmia Database.csv',
    'original_samples': len(df),
    'train_samples': len(X_train_balanced),
    'val_samples': len(X_val),
    'test_samples': len(X_test),
    'num_features': X_train_balanced.shape[1],
    'num_classes': len(label_encoder.classes_),
    'classes': list(label_encoder.classes_),
    'smote_applied': True,
    'normalization': 'StandardScaler'
}

with open(os.path.join(OUTPUT_DIR, 'preprocessing_metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   ✅ preprocessing_metadata.json")

# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 80)
print("✅ VERİ HAZIRLAMA TAMAMLANDI")
print("=" * 80)

print(f"""
📊 ÖZET:
   • Orijinal veri: {len(df):,} örnek
   • Train (balanced): {len(X_train_balanced):,} örnek
   • Validation: {len(X_val):,} örnek
   • Test: {len(X_test):,} örnek
   • Özellik sayısı: {X_train_balanced.shape[1]}
   • Sınıf sayısı: {len(label_encoder.classes_)}

🎯 SINIFLAR:
   0: N (Normal) - Düşük Aciliyet
   1: S (SVEB) - Orta Aciliyet
   2: V (VEB) - Yüksek Aciliyet
   3: F (Fusion) - Orta-Yüksek Aciliyet
   4: Q (Belirsiz) - Değerlendirme Gerekli

📁 KAYDEDLEN DOSYALAR:
   • ekg_data.npz - Hazır eğitim verisi
   • ekg_scaler.joblib - Normalizasyon scaler
   • label_map.json - Etiket eşleme
   • urgency_levels.json - Aciliyet seviyeleri
   • feature_names.json - Özellik isimleri

🚀 SONRAKİ ADIM:
   python ai-service/ekg_train_xgboost.py
""")
