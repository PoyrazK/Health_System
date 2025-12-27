"""
Healthcare AI System - Data Preprocessing & EDA
Dataset: Disease and symptoms dataset.csv
"""

import pandas as pd
import numpy as np
from collections import Counter

# Load dataset
print("=" * 60)
print("🔍 HEALTHCARE AI - VERİ SETİ ANALİZİ")
print("=" * 60)

df = pd.read_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\Disease and symptoms dataset.csv")

# 1. Basic Info
print("\n📊 TEMEL BİLGİLER:")
print(f"  • Satır sayısı: {df.shape[0]:,}")
print(f"  • Sütun sayısı: {df.shape[1]}")

# 2. Column overview
print("\n📋 SÜTUN LİSTESİ:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:3}. {col}")

# 3. Data types
print("\n🔢 VERİ TİPLERİ:")
print(df.dtypes.value_counts())

# 4. First few rows
print("\n👀 İLK 5 SATIR:")
print(df.head())

# 5. Null/Missing values
print("\n❓ EKSİK VERİ ANALİZİ:")
null_counts = df.isnull().sum()
null_cols = null_counts[null_counts > 0]
if len(null_cols) > 0:
    print("  Eksik veri içeren sütunlar:")
    for col, count in null_cols.items():
        pct = (count / len(df)) * 100
        print(f"    • {col}: {count:,} ({pct:.2f}%)")
else:
    print("  ✅ Eksik veri yok!")

# 6. Identify target column
print("\n🎯 HEDEF SÜTUN TESPİTİ:")
possible_targets = ['diagnosis', 'prognosis', 'disease', 'Disease', 'label', 'target']
target_col = None
for pt in possible_targets:
    if pt in df.columns:
        target_col = pt
        break

if target_col is None:
    # Check for any column with fewer unique values (likely target)
    for col in df.columns:
        if df[col].dtype == 'object' and df[col].nunique() < 100:
            if 'symptom' not in col.lower():
                target_col = col
                print(f"  Olası hedef sütun: '{target_col}'")
                break

if target_col:
    print(f"  🎯 Hedef sütun: '{target_col}'")
    print(f"  📈 Benzersiz değer sayısı: {df[target_col].nunique()}")
else:
    print("  ⚠️ Hedef sütun bulunamadı, manuel kontrol gerekli!")

# 7. Class distribution (if target found)
if target_col:
    print("\n📊 SINIF DAĞILIMI (Hastalıklar):")
    class_counts = df[target_col].value_counts()
    print(f"  Toplam sınıf sayısı: {len(class_counts)}")
    print("\n  En yaygın 20 sınıf:")
    for disease, count in class_counts.head(20).items():
        pct = (count / len(df)) * 100
        print(f"    • {disease}: {count:,} ({pct:.2f}%)")
    
    print("\n  En nadir 10 sınıf:")
    for disease, count in class_counts.tail(10).items():
        pct = (count / len(df)) * 100
        print(f"    • {disease}: {count:,} ({pct:.2f}%)")
    
    # Check for class imbalance
    print("\n⚖️ SINIF DENGESİ ANALİZİ:")
    min_count = class_counts.min()
    max_count = class_counts.max()
    imbalance_ratio = max_count / min_count
    print(f"  En az örnek: {min_count}")
    print(f"  En çok örnek: {max_count}")
    print(f"  Dengesizlik oranı: {imbalance_ratio:.2f}x")
    
    # Rare classes (< 10 samples)
    rare_classes = class_counts[class_counts < 10]
    if len(rare_classes) > 0:
        print(f"\n  ⚠️ Nadir sınıflar (<10 örnek): {len(rare_classes)} adet")
        for disease, count in rare_classes.items():
            print(f"    • {disease}: {count}")

# 8. Feature columns
print("\n🔬 FEATURE SÜTUNLARI:")
feature_cols = [col for col in df.columns if col != target_col]
print(f"  Toplam feature sayısı: {len(feature_cols)}")

# Check unique values in features
print("\n  Feature değer analizi (ilk 10 feature):")
for col in feature_cols[:10]:
    unique_vals = df[col].nunique()
    sample_vals = df[col].dropna().unique()[:3]
    print(f"    • {col}: {unique_vals} benzersiz değer, örnek: {list(sample_vals)}")

# 9. Recommendations
print("\n" + "=" * 60)
print("💡 ÖNERİLER:")
print("=" * 60)
print("""
1. Hedef sütunu kontrol edin ve onaylayın
2. Nadir sınıfları (<10 örnek) temizleyin veya birleştirin
3. Eksik verileri doldurun veya ilgili satırları silin
4. Feature encoding yapın (Label/One-Hot)
5. Train/Test split için stratified sampling kullanın
""")

# Save summary to file
summary = {
    'rows': df.shape[0],
    'columns': df.shape[1],
    'target_column': target_col,
    'num_classes': df[target_col].nunique() if target_col else 0,
    'num_features': len(feature_cols),
    'null_columns': len(null_cols)
}

print("\n✅ Analiz tamamlandı!")
