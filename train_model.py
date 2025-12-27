"""
Healthcare AI System - ML Model Training
Disease Risk Prediction Model using XGBoost
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import xgboost as xgb
import joblib
import json
import os

print("=" * 60)
print("🤖 HEALTHCARE AI - MODEL EĞİTİMİ")
print("=" * 60)

# ============================================
# 1. Veriyi yükle
# ============================================
print("\n📂 Veri yükleniyor...")
df = pd.read_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\cleaned_dataset.csv")

# Target ve features
target_col = 'diseases'
exclude_cols = ['diseases', 'disease_label']
feature_cols = [col for col in df.columns if col not in exclude_cols]

X = df[feature_cols]
y = df['disease_label']

print(f"  Feature sayısı: {len(feature_cols)}")
print(f"  Toplam örnek: {len(X):,}")
print(f"  Sınıf sayısı: {y.nunique()}")

# ============================================
# 2. Train/Test Split (Stratified)
# ============================================
print("\n📊 Train/Test split yapılıyor...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42,
    stratify=y
)

print(f"  Train set: {len(X_train):,} örnek")
print(f"  Test set: {len(X_test):,} örnek")

# ============================================
# 3. XGBoost Model Eğitimi
# ============================================
print("\n🚀 XGBoost model eğitimi başlıyor...")
print("  Bu işlem birkaç dakika sürebilir...")

# Model parametreleri
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective='multi:softprob',
    num_class=y.nunique(),
    random_state=42,
    n_jobs=-1,
    verbosity=1,
    tree_method='hist'  # Hızlı eğitim
)

# Eğitim
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=True
)

print("\n✅ Model eğitimi tamamlandı!")

# ============================================
# 4. Model Değerlendirme
# ============================================
print("\n📈 MODEL DEĞERLENDİRME:")

# Tahminler
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

# Top-5 Accuracy
y_pred_proba = model.predict_proba(X_test)
top5_accuracy = np.mean([
    y_test.iloc[i] in np.argsort(y_pred_proba[i])[-5:]
    for i in range(len(y_test))
])
print(f"  Top-5 Accuracy: {top5_accuracy:.4f} ({top5_accuracy*100:.2f}%)")

# ============================================
# 5. Feature Importance
# ============================================
print("\n🔍 EN ÖNEMLİ SEMPTOMLAR (Top 20):")
importance = model.feature_importances_
importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': importance
}).sort_values('importance', ascending=False)

for i, row in importance_df.head(20).iterrows():
    print(f"  {row['importance']:.4f} - {row['feature']}")

# ============================================
# 6. Modeli Kaydet
# ============================================
print("\n💾 Model kaydediliyor...")

# Model klasörü oluştur
model_dir = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models"
os.makedirs(model_dir, exist_ok=True)

# Model kaydet
model_path = os.path.join(model_dir, "disease_classifier.joblib")
joblib.dump(model, model_path)
print(f"  ✅ Model: {model_path}")

# Feature listesi kaydet
with open(os.path.join(model_dir, "feature_columns.json"), 'w') as f:
    json.dump(feature_cols, f, indent=2)
print(f"  ✅ Feature listesi kaydedildi")

# Disease encoding kaydet
disease_encoding = pd.read_csv(r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\disease_encoding.csv")
disease_encoding.to_json(os.path.join(model_dir, "disease_encoding.json"), orient='records', indent=2)
print(f"  ✅ Disease encoding kaydedildi")

# Model bilgisi kaydet
model_info = {
    "model_type": "XGBClassifier",
    "n_estimators": 100,
    "max_depth": 6,
    "num_features": len(feature_cols),
    "num_classes": int(y.nunique()),
    "accuracy": float(accuracy),
    "top5_accuracy": float(top5_accuracy),
    "train_samples": len(X_train),
    "test_samples": len(X_test)
}

with open(os.path.join(model_dir, "model_info.json"), 'w') as f:
    json.dump(model_info, f, indent=2)
print(f"  ✅ Model bilgisi kaydedildi")

# Importance kaydet
importance_df.to_csv(os.path.join(model_dir, "feature_importance.csv"), index=False)
print(f"  ✅ Feature importance kaydedildi")

print("\n" + "=" * 60)
print("🎉 MODEL EĞİTİMİ TAMAMLANDI!")
print("=" * 60)
print(f"""
📊 SONUÇLAR:
  • Model: XGBoost Classifier
  • Accuracy: {accuracy*100:.2f}%
  • Top-5 Accuracy: {top5_accuracy*100:.2f}%
  • Hastalık Sayısı: {y.nunique()}
  • Feature Sayısı: {len(feature_cols)}

📁 KAYDEDILEN DOSYALAR:
  • ai-service/models/disease_classifier.joblib
  • ai-service/models/feature_columns.json
  • ai-service/models/disease_encoding.json
  • ai-service/models/model_info.json
  • ai-service/models/feature_importance.csv
""")
