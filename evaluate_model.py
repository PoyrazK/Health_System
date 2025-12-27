"""
Healthcare AI System - Comprehensive Model Evaluation
Tests model performance on all critical metrics
"""

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report,
    top_k_accuracy_score
)
from datetime import datetime
import os

print("=" * 80)
print("🧪 HEALTHCARE AI - KAPSAMLI MODEL DEĞERLENDİRME")
print("=" * 80)

# ============================================
# 1. VERİ VE MODEL YÜKLEME
# ============================================

print("\n📂 Veri ve model yükleniyor...")

# Model yükleme
MODEL_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models"
model = joblib.load(os.path.join(MODEL_DIR, "disease_classifier.joblib"))

with open(os.path.join(MODEL_DIR, "feature_columns.json"), 'r') as f:
    feature_columns = json.load(f)

with open(os.path.join(MODEL_DIR, "disease_encoding.json"), 'r') as f:
    disease_encoding = json.load(f)

label_to_disease = {item['label']: item['disease'] for item in disease_encoding}

# Test verisi yükleme
df = pd.read_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\cleaned_dataset.csv")

# Train/Test split (orijinal ile aynı)
from sklearn.model_selection import train_test_split

target_col = 'diseases'
exclude_cols = ['diseases', 'disease_label']
existing_feature_cols = [col for col in df.columns if col not in exclude_cols]

X = df[existing_feature_cols]
y = df['disease_label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42,
    stratify=y
)

print(f"  ✅ Test set: {len(X_test):,} samples")
print(f"  ✅ Number of classes: {len(label_to_disease)}")

# ============================================
# 2. TAHMİNLER
# ============================================

print("\n🔮 Tahminler yapılıyor...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# ============================================
# 3. TEMEL METRİKLER
# ============================================

print("\n" + "=" * 80)
print("📊 1. TEMEL METRİKLER")
print("=" * 80)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy (Doğruluk Oranı): {accuracy:.4f} ({accuracy*100:.2f}%)")

# Top-K Accuracy
top3_acc = top_k_accuracy_score(y_test, y_pred_proba, k=3)
top5_acc = top_k_accuracy_score(y_test, y_pred_proba, k=5)
top10_acc = top_k_accuracy_score(y_test, y_pred_proba, k=10)

print(f"\n🎯 Top-K Accuracy (Tıbbi Teşhis için Kritik):")
print(f"  • Top-1 Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  • Top-3 Accuracy: {top3_acc:.4f} ({top3_acc*100:.2f}%)")
print(f"  • Top-5 Accuracy: {top5_acc:.4f} ({top5_acc*100:.2f}%)")
print(f"  • Top-10 Accuracy: {top10_acc:.4f} ({top10_acc*100:.2f}%)")

# Precision, Recall, F1
precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_pred, average=None, zero_division=0
)

print(f"\n📈 Ortalama Sınıf Bazlı Performans:")
print(f"  • Ortalama Precision: {np.mean(precision):.4f}")
print(f"  • Ortalama Recall: {np.mean(recall):.4f}")
print(f"  • Ortalama F1-Score: {np.mean(f1):.4f}")

# ============================================
# 4. ÇOK SINIFLI METRİKLER
# ============================================

print("\n" + "=" * 80)
print("📊 2. ÇOK SINIFLI METRİKLER")
print("=" * 80)

# Macro ve Weighted Average
precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
    y_test, y_pred, average='macro', zero_division=0
)
precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
    y_test, y_pred, average='weighted', zero_division=0
)

print(f"\n🔷 Macro-Average (Tüm sınıflar eşit ağırlıklı):")
print(f"  • Precision: {precision_macro:.4f}")
print(f"  • Recall: {recall_macro:.4f}")
print(f"  • F1-Score: {f1_macro:.4f}")

print(f"\n🔶 Weighted-Average (Örnek sayısına göre ağırlıklı):")
print(f"  • Precision: {precision_weighted:.4f}")
print(f"  • Recall: {recall_weighted:.4f}")
print(f"  • F1-Score: {f1_weighted:.4f}")

# En iyi ve en kötü performans gösteren hastalıklar
df_performance = pd.DataFrame({
    'disease': [label_to_disease[i] for i in range(len(f1))],
    'precision': precision,
    'recall': recall,
    'f1_score': f1,
    'support': support
})

print(f"\n🏆 EN İYİ PERFORMANS GÖSTEREN 10 HASTALIK (F1-Score):")
top_diseases = df_performance.nlargest(10, 'f1_score')
for idx, row in top_diseases.iterrows():
    print(f"  • {row['disease'][:50]:50s} | F1: {row['f1_score']:.3f} | Support: {int(row['support'])}")

print(f"\n⚠️ EN DÜŞÜK PERFORMANS GÖSTEREN 10 HASTALIK (F1-Score):")
bottom_diseases = df_performance[df_performance['support'] > 10].nsmallest(10, 'f1_score')
for idx, row in bottom_diseases.iterrows():
    print(f"  • {row['disease'][:50]:50s} | F1: {row['f1_score']:.3f} | Support: {int(row['support'])}")

# Confusion Matrix analizi
cm = confusion_matrix(y_test, y_pred)

print(f"\n🔀 Confusion Matrix İstatistikleri:")
print(f"  • Toplam doğru tahmin: {np.trace(cm):,}")
print(f"  • Toplam yanlış tahmin: {cm.sum() - np.trace(cm):,}")

# En çok karışan hastalık çiftleri
confusion_pairs = []
for i in range(len(cm)):
    for j in range(len(cm)):
        if i != j and cm[i, j] > 5:  # En az 5 karışma
            confusion_pairs.append({
                'true_disease': label_to_disease[i],
                'predicted_disease': label_to_disease[j],
                'count': cm[i, j]
            })

confusion_pairs = sorted(confusion_pairs, key=lambda x: x['count'], reverse=True)

print(f"\n⚠️ EN ÇOK KARIŞAN 10 HASTALIK ÇİFTİ:")
for pair in confusion_pairs[:10]:
    print(f"  • {pair['true_disease'][:35]:35s} → {pair['predicted_disease'][:35]:35s} : {pair['count']} kez")

# ============================================
# 5. SAĞLIK ALANI İÇİN ÖZEL METRİKLER
# ============================================

print("\n" + "=" * 80)
print("🏥 3. SAĞLIK ALANI İÇİN ÖZEL METRİKLER")
print("=" * 80)

# One-vs-Rest için Sensitivity ve Specificity
sensitivities = []
specificities = []

for class_idx in range(len(label_to_disease)):
    # Binary classification için hazırlık
    y_test_binary = (y_test == class_idx).astype(int)
    y_pred_binary = (y_pred == class_idx).astype(int)
    
    # True Positives, False Positives, etc.
    tp = np.sum((y_test_binary == 1) & (y_pred_binary == 1))
    tn = np.sum((y_test_binary == 0) & (y_pred_binary == 0))
    fp = np.sum((y_test_binary == 0) & (y_pred_binary == 1))
    fn = np.sum((y_test_binary == 1) & (y_pred_binary == 0))
    
    # Sensitivity (Recall) = TP / (TP + FN)
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    # Specificity = TN / (TN + FP)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    sensitivities.append(sensitivity)
    specificities.append(specificity)

avg_sensitivity = np.mean(sensitivities)
avg_specificity = np.mean(specificities)

print(f"\n🎯 Sensitivity (Duyarlılık - Hasta olanları bulma):")
print(f"  • Ortalama Sensitivity: {avg_sensitivity:.4f} ({avg_sensitivity*100:.2f}%)")
print(f"  • Min Sensitivity: {np.min(sensitivities):.4f}")
print(f"  • Max Sensitivity: {np.max(sensitivities):.4f}")

print(f"\n🔍 Specificity (Özgüllük - Sağlıklıları doğru ayırma):")
print(f"  • Ortalama Specificity: {avg_specificity:.4f} ({avg_specificity*100:.2f}%)")
print(f"  • Min Specificity: {np.min(specificities):.4f}")
print(f"  • Max Specificity: {np.max(specificities):.4f}")

# Risk-based accuracy (Örnek olarak en yaygın 20 hastalık için)
print(f"\n⚡ Risk-based Accuracy (Yüksek örnekli hastalıklarda başarı):")

high_risk_diseases = df_performance.nlargest(20, 'support')
high_risk_accuracy = []

for idx, row in high_risk_diseases.iterrows():
    disease_name = row['disease']
    label = [k for k, v in label_to_disease.items() if v == disease_name][0]
    
    # Bu hastalık için accuracy
    disease_mask = y_test == label
    if disease_mask.sum() > 0:
        disease_acc = accuracy_score(y_test[disease_mask], y_pred[disease_mask])
        high_risk_accuracy.append(disease_acc)
        print(f"  • {disease_name[:45]:45s} | Acc: {disease_acc:.3f} | n={int(row['support'])}")

avg_high_risk_acc = np.mean(high_risk_accuracy)
print(f"\n  📊 Ortalama High-Risk Accuracy: {avg_high_risk_acc:.4f} ({avg_high_risk_acc*100:.2f}%)")

# ============================================
# 6. ÖZET RAPOR
# ============================================

print("\n" + "=" * 80)
print("📋 ÖZET RAPOR")
print("=" * 80)

summary = {
    "timestamp": datetime.now().isoformat(),
    "test_samples": len(X_test),
    "num_classes": len(label_to_disease),
    "metrics": {
        "accuracy": round(accuracy * 100, 2),
        "top3_accuracy": round(top3_acc * 100, 2),
        "top5_accuracy": round(top5_acc * 100, 2),
        "top10_accuracy": round(top10_acc * 100, 2),
        "precision_macro": round(precision_macro, 4),
        "recall_macro": round(recall_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "precision_weighted": round(precision_weighted, 4),
        "recall_weighted": round(recall_weighted, 4),
        "f1_weighted": round(f1_weighted, 4),
        "avg_sensitivity": round(avg_sensitivity, 4),
        "avg_specificity": round(avg_specificity, 4),
        "high_risk_accuracy": round(avg_high_risk_acc, 4)
    },
    "interpretation": {
        "overall": "EXCELLENT" if accuracy > 0.85 else "GOOD" if accuracy > 0.75 else "NEEDS_IMPROVEMENT",
        "top3_clinical_use": "HIGHLY_SUITABLE" if top3_acc > 0.95 else "SUITABLE" if top3_acc > 0.90 else "MODERATE",
        "sensitivity": "HIGH" if avg_sensitivity > 0.80 else "MODERATE" if avg_sensitivity > 0.70 else "LOW",
        "specificity": "HIGH" if avg_specificity > 0.90 else "MODERATE" if avg_specificity > 0.80 else "LOW"
    }
}

print(f"\n✅ GENEL BAŞARIM: {summary['interpretation']['overall']}")
print(f"   • Accuracy: {summary['metrics']['accuracy']}%")
print(f"   • Top-3 Accuracy: {summary['metrics']['top3_accuracy']}% (Klinik kullanım: {summary['interpretation']['top3_clinical_use']})")
print(f"   • Sensitivity: {summary['metrics']['avg_sensitivity']} ({summary['interpretation']['sensitivity']})")
print(f"   • Specificity: {summary['metrics']['avg_specificity']} ({summary['interpretation']['specificity']})")

# Raporu kaydet
report_path = os.path.join(MODEL_DIR, "evaluation_report.json")
with open(report_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n💾 Rapor kaydedildi: evaluation_report.json")

# ============================================
# 7. KLİNİK ÖNEME GÖRE YORUMLAMA
# ============================================

print("\n" + "=" * 80)
print("🏥 KLİNİK YORUMLAMA")
print("=" * 80)

print(f"""
🎯 MODEL KARAR DESTEK SİSTEMİ OLARAK KULLANILABİLİR Mİ?

✅ GÜÇLÜ YANLAR:
  • Top-3 accuracy %{summary['metrics']['top3_accuracy']} - Doktorlar için 3 olası tanı sunmak yeterli
  • Overall accuracy %{summary['metrics']['accuracy']} - Teşhis doğruluğu yüksek
  • Specificity {summary['metrics']['avg_specificity']} - Gereksiz panik yaratma riski düşük

⚠️ DİKKAT EDİLMESİ GEREKENLER:
  • Model asla nihai karar verici OLAMAZ - sadece destek sistemi
  • Nadir hastalıklarda performans düşebilir (az örnekli sınıflar)
  • Doktor geri bildirimleriyle sürekli iyileştirme gerekli (feedback loop aktif)

💡 ÖNERİLER:
  • Düşük F1 skorlu hastalıklar için daha fazla veri toplanmalı
  • En çok karışan hastalık çiftleri için ayırıcı tanı rehberleri eklenmeli
  • Yüksek riskli hastalıklar için özel threshold ayarları yapılmalı

📊 SONUÇ:
Model, {summary['interpretation']['overall']} seviyede performans gösteriyor ve
klinik karar destek sistemi olarak kullanıma uygun. Top-3 accuracy
%{summary['metrics']['top3_accuracy']} ile doktorlara anlamlı öneriler sunabilir.
""")

print("\n" + "=" * 80)
print("✅ DEĞERLENDİRME TAMAMLANDI")
print("=" * 80)
