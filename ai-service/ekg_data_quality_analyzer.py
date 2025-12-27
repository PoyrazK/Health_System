"""
EKG Data Quality Analyzer
Comprehensive analysis of EKG dataset for ML readiness
"""

import pandas as pd
import numpy as np
from scipy import stats, signal
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🔬 EKG VERİ KALİTESİ ANALİZİ")
print("=" * 80)

# ==========================================
# CONFIGURATION
# ==========================================

class AnalysisConfig:
    # Paths to check
    POSSIBLE_PATHS = [
        r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\notebooks\ekg\MIT-BIH Arrhythmia Database.csv",
        r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\notebooks\ekg\MIT-BIH Supraventricular Arrhythmia Database.csv",
        r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\notebooks\ekg\INCART 2-lead Arrhythmia Database.csv",
        r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\Sudden Cardiac Death Holter Database.csv",
    ]
    
    # Quality thresholds
    NOISE_THRESHOLD = 3.0  # Z-score for outliers
    MIN_SIGNAL_LENGTH = 100
    MAX_SIGNAL_LENGTH = 5000
    MISSING_THRESHOLD = 0.05  # 5% max missing
    IMBALANCE_THRESHOLD = 10  # Max class ratio

# ==========================================
# DATA LOADER
# ==========================================

def find_and_load_data():
    """Find and load EKG data from possible paths"""
    
    # First, scan directory for CSV files
    base_dir = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon"
    
    print("\n📂 Mevcut CSV dosyaları aranıyor...")
    
    csv_files = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.csv') and ('mit' in f.lower() or 'ekg' in f.lower() or 'ecg' in f.lower() or 'arrhythmia' in f.lower()):
                csv_files.append(os.path.join(root, f))
    
    if csv_files:
        print(f"  Bulunan EKG CSV dosyaları:")
        for f in csv_files:
            size = os.path.getsize(f) / (1024*1024)
            print(f"    • {os.path.basename(f)} ({size:.1f} MB)")
    
    # Try to load
    for path in AnalysisConfig.POSSIBLE_PATHS + csv_files:
        if os.path.exists(path):
            try:
                print(f"\n📥 Yükleniyor: {os.path.basename(path)}")
                df = pd.read_csv(path)
                print(f"   ✅ Başarılı: {len(df):,} satır, {len(df.columns)} sütun")
                return df, path
            except Exception as e:
                print(f"   ❌ Hata: {e}")
    
    return None, None

# ==========================================
# DATA QUALITY CHECKS
# ==========================================

class DataQualityChecker:
    """Comprehensive data quality analysis"""
    
    def __init__(self, df: pd.DataFrame, filepath: str):
        self.df = df
        self.filepath = filepath
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "file": os.path.basename(filepath) if filepath else "unknown",
            "checks": {}
        }
    
    def analyze_all(self):
        """Run all quality checks"""
        self.check_basic_stats()
        self.check_missing_values()
        self.check_duplicates()
        self.check_data_types()
        self.check_class_distribution()
        self.check_signal_quality()
        self.check_noise_levels()
        self.check_outliers()
        self.generate_summary()
        return self.report
    
    def check_basic_stats(self):
        """Basic dataset statistics"""
        print("\n📊 1. TEMEL İSTATİSTİKLER")
        
        stats = {
            "total_samples": len(self.df),
            "total_features": len(self.df.columns),
            "memory_mb": round(self.df.memory_usage(deep=True).sum() / 1024**2, 2),
            "columns": list(self.df.columns)[:20]  # First 20 columns
        }
        
        print(f"   • Toplam örnek: {stats['total_samples']:,}")
        print(f"   • Toplam özellik: {stats['total_features']}")
        print(f"   • Bellek kullanımı: {stats['memory_mb']:.2f} MB")
        
        self.report["checks"]["basic"] = stats
    
    def check_missing_values(self):
        """Check for missing values"""
        print("\n📊 2. EKSİK VERİ ANALİZİ")
        
        missing_count = self.df.isnull().sum().sum()
        total_cells = self.df.size
        missing_ratio = missing_count / total_cells
        
        cols_with_missing = self.df.columns[self.df.isnull().any()].tolist()
        
        result = {
            "total_missing": int(missing_count),
            "total_cells": int(total_cells),
            "missing_ratio": round(missing_ratio * 100, 4),
            "columns_with_missing": cols_with_missing[:10],
            "status": "✅ PASS" if missing_ratio < AnalysisConfig.MISSING_THRESHOLD else "❌ FAIL"
        }
        
        print(f"   • Eksik hücre: {missing_count:,} / {total_cells:,}")
        print(f"   • Eksik oran: %{result['missing_ratio']:.4f}")
        print(f"   • Durum: {result['status']}")
        
        self.report["checks"]["missing"] = result
    
    def check_duplicates(self):
        """Check for duplicate rows"""
        print("\n📊 3. TEKRARLANAN VERİ ANALİZİ")
        
        duplicates = self.df.duplicated().sum()
        dup_ratio = duplicates / len(self.df) * 100
        
        result = {
            "duplicate_rows": int(duplicates),
            "duplicate_ratio": round(dup_ratio, 2),
            "status": "✅ PASS" if dup_ratio < 1 else "⚠️ WARN" if dup_ratio < 5 else "❌ FAIL"
        }
        
        print(f"   • Tekrarlanan satır: {duplicates:,}")
        print(f"   • Tekrar oranı: %{dup_ratio:.2f}")
        print(f"   • Durum: {result['status']}")
        
        self.report["checks"]["duplicates"] = result
    
    def check_data_types(self):
        """Analyze data types"""
        print("\n📊 4. VERİ TİPİ ANALİZİ")
        
        dtypes = self.df.dtypes.value_counts().to_dict()
        dtypes = {str(k): int(v) for k, v in dtypes.items()}
        
        print(f"   • Veri tipleri:")
        for dtype, count in dtypes.items():
            print(f"     - {dtype}: {count} sütun")
        
        # Identify potential label column
        label_candidates = []
        for col in self.df.columns:
            if 'label' in col.lower() or 'class' in col.lower() or 'type' in col.lower():
                label_candidates.append(col)
        
        # Last column often is label
        if not label_candidates and len(self.df.columns) > 0:
            last_col = self.df.columns[-1]
            if self.df[last_col].nunique() < 10:
                label_candidates.append(last_col)
        
        result = {
            "dtypes": dtypes,
            "label_candidates": label_candidates,
            "numeric_columns": len(self.df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(self.df.select_dtypes(include=['object']).columns)
        }
        
        print(f"   • Olası etiket sütunları: {label_candidates}")
        
        self.report["checks"]["dtypes"] = result
    
    def check_class_distribution(self):
        """Check class balance"""
        print("\n📊 5. SINIF DAĞILIMI ANALİZİ")
        
        label_col = None
        for col in self.df.columns:
            if 'label' in col.lower() or 'class' in col.lower():
                label_col = col
                break
        
        if label_col is None and len(self.df.columns) > 0:
            last_col = self.df.columns[-1]
            if self.df[last_col].nunique() < 20:
                label_col = last_col
        
        if label_col:
            distribution = self.df[label_col].value_counts().to_dict()
            distribution = {str(k): int(v) for k, v in distribution.items()}
            
            max_count = max(distribution.values())
            min_count = min(distribution.values())
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
            
            print(f"   • Etiket sütunu: {label_col}")
            print(f"   • Sınıf sayısı: {len(distribution)}")
            print(f"   • Dağılım:")
            for label, count in sorted(distribution.items(), key=lambda x: -x[1])[:10]:
                pct = count / len(self.df) * 100
                print(f"     - {label}: {count:,} ({pct:.1f}%)")
            print(f"   • Dengesizlik oranı: {imbalance_ratio:.1f}x")
            
            status = "✅ PASS" if imbalance_ratio < AnalysisConfig.IMBALANCE_THRESHOLD else "⚠️ WARN - SMOTE GEREKLİ"
            print(f"   • Durum: {status}")
            
            result = {
                "label_column": label_col,
                "num_classes": len(distribution),
                "distribution": distribution,
                "imbalance_ratio": round(imbalance_ratio, 2),
                "status": status
            }
        else:
            result = {"label_column": None, "status": "❌ ETİKET SÜTUNU BULUNAMADI"}
            print(f"   • ❌ Etiket sütunu bulunamadı!")
        
        self.report["checks"]["class_distribution"] = result
    
    def check_signal_quality(self):
        """Check signal quality metrics"""
        print("\n📊 6. SİNYAL KALİTESİ ANALİZİ")
        
        # Identify signal columns (numeric, many values)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Exclude likely label column
        signal_cols = [c for c in numeric_cols if 
                       'label' not in c.lower() and 
                       'class' not in c.lower() and
                       c != self.df.columns[-1]][:187]  # MIT-BIH has 187 signal samples
        
        if len(signal_cols) < 10:
            # Try all numeric except last
            signal_cols = numeric_cols[:-1] if len(numeric_cols) > 1 else numeric_cols
        
        if len(signal_cols) > 0:
            sample_data = self.df[signal_cols].iloc[:1000]
            
            # Signal statistics
            signal_mean = sample_data.mean().mean()
            signal_std = sample_data.std().mean()
            signal_min = sample_data.min().min()
            signal_max = sample_data.max().max()
            
            # Check for flat signals (zero variance)
            flat_signals = (sample_data.std(axis=1) == 0).sum()
            
            print(f"   • Sinyal sütun sayısı: {len(signal_cols)}")
            print(f"   • Ortalama değer: {signal_mean:.4f}")
            print(f"   • Std sapma: {signal_std:.4f}")
            print(f"   • Değer aralığı: [{signal_min:.2f}, {signal_max:.2f}]")
            print(f"   • Düz sinyaller (varyans=0): {flat_signals}")
            
            result = {
                "signal_columns": len(signal_cols),
                "signal_length": len(signal_cols),
                "mean": round(signal_mean, 4),
                "std": round(signal_std, 4),
                "min": round(signal_min, 4),
                "max": round(signal_max, 4),
                "flat_signals": int(flat_signals),
                "status": "✅ PASS" if flat_signals < 100 else "⚠️ WARN"
            }
        else:
            result = {"status": "❌ SİNYAL SÜTUNU BULUNAMADI"}
            print(f"   • ❌ Sinyal sütunları bulunamadı!")
        
        self.report["checks"]["signal_quality"] = result
    
    def check_noise_levels(self):
        """Check for noisy signals"""
        print("\n📊 7. GÜRÜLTÜ SEVİYESİ ANALİZİ")
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        signal_cols = numeric_cols[:-1] if len(numeric_cols) > 1 else numeric_cols
        
        if len(signal_cols) > 10:
            sample_data = self.df[signal_cols[:187]].iloc[:1000]
            
            # Calculate noise metrics per signal
            noise_scores = []
            for idx in range(min(1000, len(sample_data))):
                sig = sample_data.iloc[idx].values
                
                # High-frequency content ratio (noise indicator)
                if len(sig) > 10:
                    fft = np.fft.fft(sig)
                    freqs = np.fft.fftfreq(len(sig))
                    
                    # High freq = last 30% of spectrum
                    high_freq_start = int(len(fft) * 0.7)
                    high_freq_power = np.abs(fft[high_freq_start:]).sum()
                    total_power = np.abs(fft).sum()
                    
                    noise_ratio = high_freq_power / total_power if total_power > 0 else 0
                    noise_scores.append(noise_ratio)
            
            avg_noise = np.mean(noise_scores) if noise_scores else 0
            high_noise_count = sum(1 for n in noise_scores if n > 0.3)
            
            print(f"   • Ortalama gürültü oranı: {avg_noise:.3f}")
            print(f"   • Yüksek gürültülü sinyal: {high_noise_count}/{len(noise_scores)}")
            
            status = "✅ PASS" if high_noise_count / len(noise_scores) < 0.1 else "⚠️ WARN - FİLTRELEME GEREKLİ"
            print(f"   • Durum: {status}")
            
            result = {
                "avg_noise_ratio": round(avg_noise, 4),
                "high_noise_signals": int(high_noise_count),
                "analyzed_signals": len(noise_scores),
                "status": status
            }
        else:
            result = {"status": "⚠️ Analiz edilemedi"}
        
        self.report["checks"]["noise"] = result
    
    def check_outliers(self):
        """Check for outliers using Z-score"""
        print("\n📊 8. AYKIRI DEĞER ANALİZİ")
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        signal_cols = numeric_cols[:-1] if len(numeric_cols) > 1 else numeric_cols
        
        if len(signal_cols) > 10:
            sample_data = self.df[signal_cols[:187]].iloc[:1000]
            
            # Z-score outliers
            z_scores = np.abs(stats.zscore(sample_data, nan_policy='omit'))
            outliers = (z_scores > AnalysisConfig.NOISE_THRESHOLD).sum().sum()
            total = sample_data.size
            outlier_ratio = outliers / total * 100
            
            print(f"   • Aykırı değer sayısı: {outliers:,}")
            print(f"   • Aykırı değer oranı: %{outlier_ratio:.2f}")
            
            status = "✅ PASS" if outlier_ratio < 1 else "⚠️ WARN" if outlier_ratio < 5 else "❌ FAIL"
            print(f"   • Durum: {status}")
            
            result = {
                "outlier_count": int(outliers),
                "outlier_ratio": round(outlier_ratio, 2),
                "z_threshold": AnalysisConfig.NOISE_THRESHOLD,
                "status": status
            }
        else:
            result = {"status": "⚠️ Analiz edilemedi"}
        
        self.report["checks"]["outliers"] = result
    
    def generate_summary(self):
        """Generate overall quality summary"""
        print("\n" + "=" * 80)
        print("📋 GENEL DEĞERLENDİRME")
        print("=" * 80)
        
        # Count pass/warn/fail
        status_counts = {"pass": 0, "warn": 0, "fail": 0}
        recommendations = []
        
        for check_name, check_result in self.report["checks"].items():
            if isinstance(check_result, dict) and "status" in check_result:
                status = check_result["status"].lower()
                if "pass" in status:
                    status_counts["pass"] += 1
                elif "warn" in status:
                    status_counts["warn"] += 1
                    if "smote" in status.lower():
                        recommendations.append("⚖️ SMOTE ile sınıf dengeleme uygula")
                    if "filtre" in status.lower():
                        recommendations.append("🔊 Bandpass filter ile gürültü temizliği yap")
                else:
                    status_counts["fail"] += 1
                    recommendations.append(f"❌ {check_name} kontrolünü düzelt")
        
        # Calculate readiness score
        total = sum(status_counts.values())
        readiness = (status_counts["pass"] / total * 100) if total > 0 else 0
        
        print(f"\n📊 Kontrol Sonuçları:")
        print(f"   ✅ PASS: {status_counts['pass']}")
        print(f"   ⚠️ WARN: {status_counts['warn']}")
        print(f"   ❌ FAIL: {status_counts['fail']}")
        print(f"\n🎯 Veri Hazırlık Skoru: %{readiness:.0f}")
        
        if readiness >= 80:
            overall = "✅ VERİ EĞİTİME HAZIR"
        elif readiness >= 60:
            overall = "⚠️ KÜÇÜK DÜZELTMELERLE EĞİTİME HAZIR"
        else:
            overall = "❌ VERİ TEMİZLİĞİ GEREKLİ"
        
        print(f"\n🏁 Sonuç: {overall}")
        
        if recommendations:
            print(f"\n💡 Öneriler:")
            for rec in recommendations:
                print(f"   {rec}")
        
        self.report["summary"] = {
            "readiness_score": round(readiness, 2),
            "overall_status": overall,
            "status_counts": status_counts,
            "recommendations": recommendations
        }


# ==========================================
# MAIN
# ==========================================

def main():
    # Load data
    df, filepath = find_and_load_data()
    
    if df is None:
        print("\n" + "=" * 80)
        print("❌ VERİ BULUNAMADI")
        print("=" * 80)
        print("\n💡 Çözüm:")
        print("   1. MIT-BIH CSV dosyasını proje klasörüne kopyalayın")
        print("   2. Veya ai-service/data/ekg/ klasörüne taşıyın")
        print("\n   Beklenen dosya adları:")
        print("     • mitbih_arrhythmia.csv")
        print("     • MIT-BIH Arrhythmia Database.csv")
        print("     • mitbih_train.csv / mitbih_test.csv")
        return
    
    # Run analysis
    checker = DataQualityChecker(df, filepath)
    report = checker.analyze_all()
    
    # Save report
    report_path = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg\data_quality_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Rapor kaydedildi: data_quality_report.json")


if __name__ == "__main__":
    main()
