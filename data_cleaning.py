"""
Healthcare AI System - Data Cleaning & Preprocessing
Dataset: Disease and symptoms dataset.csv
"""

import pandas as pd
import numpy as np
from collections import Counter

print("=" * 60)
print("🧹 HEALTHCARE AI - VERİ TEMİZLEME")
print("=" * 60)

# Load dataset
df = pd.read_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\Disease and symptoms dataset.csv")

print(f"\n📊 BAŞLANGIÇ:")
print(f"  • Toplam satır: {df.shape[0]:,}")
print(f"  • Toplam sütun: {df.shape[1]}")
print(f"  • Toplam hastalık: {df['diseases'].nunique()}")

# ============================================
# 1. Hedef sütun kontrolü
# ============================================
target_col = 'diseases'
feature_cols = [col for col in df.columns if col != target_col]

print(f"\n🎯 HEDEF SÜTUN: '{target_col}'")
print(f"🔬 FEATURE SAYISI: {len(feature_cols)}")

# ============================================
# 2. Sınıf dağılımı analizi
# ============================================
class_counts = df[target_col].value_counts()

print("\n📊 SINIF DAĞILIMI ANALİZİ:")
print(f"  Min örnek/sınıf: {class_counts.min()}")
print(f"  Max örnek/sınıf: {class_counts.max()}")
print(f"  Ortalama: {class_counts.mean():.1f}")
print(f"  Median: {class_counts.median():.1f}")

# ============================================
# 3. Nadir sınıfları tespit et
# ============================================
MIN_SAMPLES = 50  # Minimum örnek sayısı eşik değeri

rare_classes = class_counts[class_counts < MIN_SAMPLES]
common_classes = class_counts[class_counts >= MIN_SAMPLES]

print(f"\n⚠️ NADİR SINIFLAR (<{MIN_SAMPLES} örnek):")
print(f"  Nadir sınıf sayısı: {len(rare_classes)}")
print(f"  Nadir sınıflardaki toplam satır: {rare_classes.sum():,}")
print(f"\n✅ YETERLI SINILIFLAR (>={MIN_SAMPLES} örnek):")
print(f"  Yeterli sınıf sayısı: {len(common_classes)}")
print(f"  Bu sınıflardaki toplam satır: {common_classes.sum():,}")

# ============================================
# 4. Temizleme işlemi
# ============================================
print("\n🧹 TEMİZLEME İŞLEMİ:")

# Option A: Nadir sınıfları sil
df_cleaned = df[df[target_col].isin(common_classes.index)].copy()

print(f"  Silinen satır sayısı: {len(df) - len(df_cleaned):,}")
print(f"  Kalan satır sayısı: {len(df_cleaned):,}")
print(f"  Kalan hastalık sayısı: {df_cleaned[target_col].nunique()}")

# ============================================
# 5. Feature analizi - kullanılmayan sütunları tespit
# ============================================
print("\n🔍 FEATURE ANALİZİ:")

# Hiç kullanılmayan symptom'ları bul
zero_variance_cols = []
for col in feature_cols:
    if df_cleaned[col].nunique() == 1:
        zero_variance_cols.append(col)

print(f"  Tek değerli sütunlar: {len(zero_variance_cols)}")

# Çok nadir kullanılan symptom'lar (<%1)
low_usage_cols = []
for col in feature_cols:
    if col not in zero_variance_cols:
        usage_pct = df_cleaned[col].mean() * 100
        if usage_pct < 1:  # %1'den az kullanılıyor
            low_usage_cols.append((col, usage_pct))

print(f"  Nadir kullanılan symptomlar (<%1): {len(low_usage_cols)}")

# Zero variance sütunları sil
if zero_variance_cols:
    df_cleaned = df_cleaned.drop(columns=zero_variance_cols)
    print(f"  Silinen tek değerli sütunlar: {len(zero_variance_cols)}")

# ============================================
# 6. Final özet
# ============================================
print("\n" + "=" * 60)
print("✅ TEMİZLENMİŞ VERİ SETİ ÖZETİ:")
print("=" * 60)
print(f"  • Satır sayısı: {df_cleaned.shape[0]:,}")
print(f"  • Sütun sayısı: {df_cleaned.shape[1]}")
print(f"  • Hastalık sayısı: {df_cleaned[target_col].nunique()}")
print(f"  • Feature sayısı: {df_cleaned.shape[1] - 1}")

# Yeni sınıf dağılımı
new_class_counts = df_cleaned[target_col].value_counts()
print(f"\n  • Min örnek/sınıf: {new_class_counts.min()}")
print(f"  • Max örnek/sınıf: {new_class_counts.max()}")
print(f"  • Ortalama: {new_class_counts.mean():.1f}")

# ============================================
# 7. Temiz veriyi kaydet
# ============================================
output_path = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\cleaned_dataset.csv"
df_cleaned.to_csv(output_path, index=False)
print(f"\n💾 Temiz veri kaydedildi: cleaned_dataset.csv")

# ============================================
# 8. Hastalık listesi kaydet
# ============================================
disease_list = df_cleaned[target_col].unique().tolist()
disease_df = pd.DataFrame({
    'disease': disease_list,
    'sample_count': [new_class_counts[d] for d in disease_list]
}).sort_values('sample_count', ascending=False)

disease_df.to_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\disease_list.csv", index=False)
print(f"💾 Hastalık listesi kaydedildi: disease_list.csv")

# ============================================
# 9. Label Encoding için mapping
# ============================================
disease_to_label = {disease: idx for idx, disease in enumerate(sorted(disease_list))}
df_cleaned['disease_label'] = df_cleaned[target_col].map(disease_to_label)

# Encoding bilgisini kaydet
encoding_df = pd.DataFrame([
    {'disease': k, 'label': v} 
    for k, v in disease_to_label.items()
])
encoding_df.to_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\disease_encoding.csv", index=False)
print(f"💾 Label encoding kaydedildi: disease_encoding.csv")

print("\n✅ Veri temizleme tamamlandı!")

# Son hali kaydet
df_cleaned.to_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\cleaned_dataset.csv", index=False)
