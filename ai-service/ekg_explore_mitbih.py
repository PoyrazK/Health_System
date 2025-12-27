"""
MIT-BIH EKG Data Analysis & Preprocessing
Enhanced version with urgency scoring and SHAP explainability
"""

import pandas as pd
import numpy as np
import os

print("=" * 80)
print("🔍 MIT-BIH ARRHYTHMIA DATABASE - DATA EXPLORATION")
print("=" * 80)

# Load data
csv_path = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\MIT-BIH Arrhythmia Database.csv"
print(f"\n📂 Loading data from: MIT-BIH Arrhythmia Database.csv")

df = pd.read_csv(csv_path)

print(f"\n📊 Dataset Overview:")
print(f"  Total samples: {len(df):,}")
print(f"  Total features: {len(df.columns)}")
print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Column analysis
print(f"\n📋 Columns ({len(df.columns)} total):")
print(f"  {df.columns.tolist()[:10]}...")  # First 10 columns

# Check for signal columns
signal_cols = [col for col in df.columns if 'signal' in col.lower() or col.isdigit()]
label_col = None
for col in df.columns:
    if 'label' in col.lower() or 'class' in col.lower() or 'type' in col.lower():
        label_col = col
        break

print(f"\n🎯 Detected structure:")
print(f"  Signal columns: {len(signal_cols)}")
print(f"  Label column: {label_col}")

# Data quality
print(f"\n🔍 Data Quality:")
print(f"  Missing values: {df.isnull().sum().sum()}")
print(f"  Duplicates: {df.duplicated().sum()}")

# Label distribution
if label_col:
    print(f"\n🏷 Class Distribution:")
    label_counts = df[label_col].value_counts()
    for label, count in label_counts.items():
        print(f"    {label}: {count:,} ({count/len(df)*100:.1f}%)")
    
    # Check for imbalance
    max_count = label_counts.max()
    min_count = label_counts.min()
    imbalance_ratio = max_count / min_count
    print(f"\n  ⚖️ Imbalance ratio: {imbalance_ratio:.1f}x")
    if imbalance_ratio > 5:
        print(f"  ⚠️ HIGH IMBALANCE - SMOTE recommended")

# Signal statistics
print(f"\n📈 Signal Statistics:")
if signal_cols:
    sample_signals = df[signal_cols].iloc[:1000]
    print(f"  Mean length: ~{len(signal_cols)} samples")
    print(f"  Value range: [{sample_signals.min().min():.2f}, {sample_signals.max().max():.2f}]")
    print(f"  Contains NaN: {sample_signals.isnull().any().any()}")

# Sample data
print(f"\n📝 First 3 rows:")
print(df.head(3))

# Recommendations
print(f"\n" + "=" * 80)
print(f"✅ ANALYSIS COMPLETE")
print(f"=" * 80)
print(f"\n💡 Next steps:")
print(f"  1. Map labels to 5-class system (N, S, V, F, Q)")
print(f"  2. Clean data (remove duplicates, handle NaN)")
print(f"  3. Filter by signal length (100 < len < 5000)")
print(f"  4. Apply SMOTE balancing")
print(f"  5. Train models with urgency scoring")
