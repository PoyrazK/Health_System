"""
🔍 CRITICAL MODEL AUDIT - OVERFITTING & DATA LEAKAGE DETECTION
Katı ve dürüst değerlendirme

Bu script şunları kontrol eder:
1. Overfitting belirtileri
2. Data leakage türleri
3. Cross-validation tutarlılığı
4. Feature-based leakage
5. Record/patient-level leakage
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🔴 KRİTİK MODEL DENETİMİ - OVERFIT & DATA LEAKAGE")
print("=" * 80)
print("\n⚠️ Bu denetim KATALI ve DÜRÜST olacaktır.\n")

# ==========================================
# CONFIGURATION
# ==========================================

MODEL_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg"
DATA_PATH = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\notebooks\ekg\MIT-BIH Arrhythmia Database.csv"

# Load data
data = np.load(os.path.join(MODEL_DIR, 'ekg_data.npz'))
X_train = data['X_train']
X_val = data['X_val']
X_test = data['X_test']
y_train = data['y_train']
y_val = data['y_val']
y_test = data['y_test']

# Load original data for leakage check
df_original = pd.read_csv(DATA_PATH)

print(f"📊 Veri Boyutları:")
print(f"   Train: {X_train.shape}")
print(f"   Val: {X_val.shape}")
print(f"   Test: {X_test.shape}")

issues_found = []
warnings_found = []

# ==========================================
# 1. OVERFIT KONTROLÜ - Train vs Test Gap
# ==========================================

print("\n" + "=" * 80)
print("🔍 1. OVERFİT KONTROLÜ - Train vs Test Gap")
print("=" * 80)

# Train a fresh model to check train accuracy
model = xgb.XGBClassifier(
    max_depth=6,
    eta=0.1,
    n_estimators=343,
    random_state=42,
    use_label_encoder=False,
    eval_metric='mlogloss'
)

# Fit and check accuracies
model.fit(X_train, y_train)

train_acc = accuracy_score(y_train, model.predict(X_train))
val_acc = accuracy_score(y_val, model.predict(X_val))
test_acc = accuracy_score(y_test, model.predict(X_test))

print(f"\n   📈 Accuracy Karşılaştırması:")
print(f"   • Train Accuracy:  {train_acc*100:.2f}%")
print(f"   • Val Accuracy:    {val_acc*100:.2f}%")
print(f"   • Test Accuracy:   {test_acc*100:.2f}%")

train_test_gap = train_acc - test_acc
train_val_gap = train_acc - val_acc

print(f"\n   📊 Gap Analizi:")
print(f"   • Train-Test Gap:  {train_test_gap*100:.2f}%")
print(f"   • Train-Val Gap:   {train_val_gap*100:.2f}%")

if train_test_gap > 0.05:
    issues_found.append(f"❌ OVERFIT: Train-Test gap {train_test_gap*100:.2f}% (>5%)")
    print(f"\n   ❌ OVERFIT TESPİT EDİLDİ!")
elif train_test_gap > 0.02:
    warnings_found.append(f"⚠️ Hafif overfit: Train-Test gap {train_test_gap*100:.2f}%")
    print(f"\n   ⚠️ HAFİF OVERFİT")
else:
    print(f"\n   ✅ Train-Test gap kabul edilebilir")

# ==========================================
# 2. CROSS-VALIDATION TUTARLILIĞI
# ==========================================

print("\n" + "=" * 80)
print("🔍 2. CROSS-VALIDATION TUTARLILIĞI")
print("=" * 80)

# Combine train and val for proper CV
X_combined = np.vstack([X_train, X_val])
y_combined = np.concatenate([y_train, y_val])

print(f"\n   5-Fold Stratified CV yapılıyor...")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(
    xgb.XGBClassifier(max_depth=6, eta=0.1, n_estimators=100, use_label_encoder=False, eval_metric='mlogloss'),
    X_combined[:10000],  # Subset for speed
    y_combined[:10000],
    cv=cv,
    scoring='accuracy'
)

print(f"\n   📊 CV Sonuçları:")
print(f"   • Fold Scores: {[f'{s*100:.1f}%' for s in cv_scores]}")
print(f"   • Mean: {cv_scores.mean()*100:.2f}%")
print(f"   • Std:  {cv_scores.std()*100:.2f}%")

if cv_scores.std() > 0.05:
    issues_found.append(f"❌ CV varyansı yüksek: std={cv_scores.std()*100:.2f}%")
    print(f"\n   ❌ YÜKSEK VARYANS - Model tutarsız")
elif cv_scores.std() > 0.02:
    warnings_found.append(f"⚠️ CV varyansı orta: std={cv_scores.std()*100:.2f}%")
    print(f"\n   ⚠️ ORTA VARYANS")
else:
    print(f"\n   ✅ CV tutarlı")

# ==========================================
# 3. DATA LEAKAGE - RECORD LEVEL
# ==========================================

print("\n" + "=" * 80)
print("🔍 3. DATA LEAKAGE - RECORD LEVEL")
print("=" * 80)

# Check if same records appear in train and test
# This requires checking the original 'record' column

if 'record' in df_original.columns:
    print(f"\n   📋 Record-based leakage kontrolü...")
    
    # Get unique records
    unique_records = df_original['record'].unique()
    print(f"   • Unique records: {len(unique_records)}")
    
    # Check if we did patient-level split
    # Since we used stratified split on samples, same patient could be in both sets
    print(f"\n   ⚠️ UYARI: Stratified split örnek bazlı yapıldı!")
    print(f"      Aynı HASTA farklı split'lerde olabilir.")
    print(f"      Bu DATA LEAKAGE riski oluşturur!")
    
    warnings_found.append("⚠️ Patient-level split yapılmadı - aynı hasta train/test'te olabilir")
else:
    print(f"\n   ℹ️ Record kolonu bulunamadı")

# ==========================================
# 4. FEATURE LEAKAGE - Şüpheli Korelasyonlar
# ==========================================

print("\n" + "=" * 80)
print("🔍 4. FEATURE LEAKAGE - ŞÜPHELİ KORELASYONLAR")
print("=" * 80)

# Check feature importances
feature_importance = model.feature_importances_

print(f"\n   📊 En Etkili 10 Özellik:")
top_features = np.argsort(feature_importance)[-10:][::-1]

# Load feature names
try:
    with open(os.path.join(MODEL_DIR, 'feature_names.json'), 'r') as f:
        feature_names = json.load(f)
except:
    feature_names = [f'feature_{i}' for i in range(len(feature_importance))]

for idx in top_features:
    fname = feature_names[idx] if idx < len(feature_names) else f'feature_{idx}'
    imp = feature_importance[idx]
    print(f"   • {fname}: {imp:.4f}")
    
    # Check for suspiciously high importance
    if imp > 0.5:
        issues_found.append(f"❌ Tek özellik çok baskın: {fname} ({imp:.2f})")
        print(f"      ❌ ŞÜPHELİ: Tek özellik çok baskın!")

# Check if any feature has >0.9 correlation with target
print(f"\n   📊 Feature-Target Korelasyonu:")
for i in range(min(5, X_train.shape[1])):
    corr = np.corrcoef(X_train[:, i], y_train)[0, 1]
    if abs(corr) > 0.8:
        issues_found.append(f"❌ Yüksek feature-target korelasyonu: feature_{i} ({corr:.2f})")
        print(f"   ❌ feature_{i}: {corr:.3f} - ŞÜPHELİ!")
    elif abs(corr) > 0.5:
        print(f"   ⚠️ feature_{i}: {corr:.3f}")
    else:
        print(f"   ✅ feature_{i}: {corr:.3f}")

# ==========================================
# 5. SMOTE LEAKAGE KONTROLÜ
# ==========================================

print("\n" + "=" * 80)
print("🔍 5. SMOTE LEAKAGE KONTROLÜ")
print("=" * 80)

# SMOTE was applied AFTER split - this is correct
# But let's verify

print(f"\n   📊 SMOTE Kontrol:")
print(f"   • Train boyutu (SMOTE sonrası): {len(X_train)}")
print(f"   • Val boyutu: {len(X_val)}")
print(f"   • Test boyutu: {len(X_test)}")

# Check class distribution in test (should be original, not SMOTE'd)
unique, counts = np.unique(y_test, return_counts=True)
print(f"\n   Test Set Dağılımı (SMOTE uygulanMAMALI):")
for u, c in zip(unique, counts):
    print(f"   • Class {u}: {c} ({c/len(y_test)*100:.1f}%)")

# If test is balanced, that's a problem
test_imbalance = max(counts) / min(counts)
if test_imbalance < 2:
    issues_found.append("❌ Test set dengeli - SMOTE leakage olabilir!")
    print(f"\n   ❌ TEST SET DENGELİ! SMOTE test'e sızmış olabilir!")
else:
    print(f"\n   ✅ Test set orijinal dağılımda (imbalance: {test_imbalance:.1f}x)")

# ==========================================
# 6. SCALER LEAKAGE KONTROLÜ
# ==========================================

print("\n" + "=" * 80)
print("🔍 6. SCALER LEAKAGE KONTROLÜ")
print("=" * 80)

# Check if scaler was fit on all data (leakage) or just train
print(f"\n   📊 Scaler analizi:")

# Load scaler
try:
    scaler = joblib.load(os.path.join(MODEL_DIR, 'ekg_scaler.joblib'))
    print(f"   • Scaler türü: {type(scaler).__name__}")
    print(f"   • Mean: {scaler.mean_[:3]}...")
    print(f"   • Scale: {scaler.scale_[:3]}...")
    
    # Can't directly verify if it was fit on all data or just train
    # But we can warn about it
    warnings_found.append("⚠️ Scaler fit verisi doğrulanamıyor - ekg_prepare_data.py'yi kontrol et")
    print(f"\n   ⚠️ Scaler tüm veri üzerinde mi sadece train üzerinde mi fit edilmiş?")
    print(f"      → ekg_prepare_data.py'yi manuel kontrol et!")
except Exception as e:
    print(f"   ❌ Scaler yüklenemedi: {e}")

# ==========================================
# 7. %99 ACCURACY GERÇEKÇI Mİ?
# ==========================================

print("\n" + "=" * 80)
print("🔍 7. %99 ACCURACY GERÇEKÇİ Mİ?")
print("=" * 80)

print(f"""
   📚 MIT-BIH Benchmark Karşılaştırması:

   Literatürde MIT-BIH 5-sınıf performansları:
   • Inter-patient split: ~85-92%
   • Intra-patient split: ~95-99%

   Bizim sonuç: {test_acc*100:.2f}%

   🤔 YORUM:
""")

if test_acc > 0.98:
    print(f"   ❌ %99+ accuracy ŞÜPHELİ!")
    print(f"      Olası nedenler:")
    print(f"      1. Intra-patient split (aynı hasta train/test'te)")
    print(f"      2. Feature leakage (hedef sızmış)")
    print(f"      3. Test set çok kolay")
    
    issues_found.append("❌ %99+ accuracy literatür ortalamasının ÜZERİNDE - leakage şüphesi")
elif test_acc > 0.95:
    warnings_found.append("⚠️ %95+ accuracy yüksek ama intra-patient split ile mümkün")
else:
    print(f"   ✅ Accuracy literatür ile uyumlu")

# ==========================================
# 8. ÖNERİLER
# ==========================================

print("\n" + "=" * 80)
print("📋 SONUÇ VE ÖNERİLER")
print("=" * 80)

print(f"\n   ❌ HATALAR: {len(issues_found)}")
for issue in issues_found:
    print(f"      {issue}")

print(f"\n   ⚠️ UYARILAR: {len(warnings_found)}")
for warning in warnings_found:
    print(f"      {warning}")

if issues_found:
    print(f"\n   🚨 SONUÇ: MODEL GÜVENİLİR DEĞİL!")
    print(f"""
   📌 YAPILMASI GEREKENLER:
   
   1. PATIENT-LEVEL SPLIT:
      → Aynı hastanın TÜM kayıtları ya train'de ya test'te olmalı
      → 'record' kolonuna göre split yap
   
   2. SCALER FIX:
      → Scaler SADECE train verisi üzerinde fit edilmeli
      → Sonra test'e transform uygulanmalı
   
   3. SMOTE FIX:
      → SMOTE sadece train'e uygulandığından emin ol
   
   4. RE-TRAIN:
      → Yukarıdaki düzeltmelerle modeli yeniden eğit
      → Beklenen accuracy: %85-92 (inter-patient)
""")
elif warnings_found:
    print(f"\n   ⚠️ SONUÇ: MODEL KABUL EDİLEBİLİR ama dikkat gerekli")
else:
    print(f"\n   ✅ SONUÇ: Model güvenilir görünüyor")

print("\n" + "=" * 80)
print("DENETİM TAMAMLANDI")
print("=" * 80)

# Save audit report
audit_report = {
    "train_accuracy": float(train_acc),
    "val_accuracy": float(val_acc),
    "test_accuracy": float(test_acc),
    "train_test_gap": float(train_test_gap),
    "cv_mean": float(cv_scores.mean()),
    "cv_std": float(cv_scores.std()),
    "test_imbalance_ratio": float(test_imbalance),
    "issues": issues_found,
    "warnings": warnings_found,
    "verdict": "FAIL" if issues_found else "WARN" if warnings_found else "PASS"
}

report_path = os.path.join(MODEL_DIR, 'audit_report.json')
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(audit_report, f, indent=2, ensure_ascii=False)

print(f"\nRapor kaydedildi: audit_report.json")
