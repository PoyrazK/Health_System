# Golden Hour AI Model

Hastalıkların kritik hale gelme süresini (Altın Saat) ve aciliyet seviyesini tahmin eden gelişmiş Yapay Zeka modeli.

## 🚀 Model Özellikleri

- **Kapsam:** 537 farklı hastalık
- **Sınıflandırma:** 5 Seviyeli Aciliyet Derecelendirmesi (Urgency 1-5)
- **Model:** XGBoost Classifier (Multi-Class)
- **Performans:** 
  - Test Accuracy: **%92.3**
  - Test F1 Score: **%92.3**
  - CV F1 Score: **%89.2**
- **Güvenilirlik:** Strict Anti-Leak önlemleri ve Overfit koruması

## 🏥 Aciliyet Seviyeleri

| Seviye | Tanım | Müdahale Süresi | Örnekler |
|--------|-------|-----------------|----------|
| **5** | Critical | Dakikalar içinde | Kalp krizi, İnme, Sepsis |
| **4** | Emergent | Saatler içinde | Apandisit, Diyabetik Ketoasidoz |
| **3** | Urgent | 24 saat içinde | Pnömoni, Böbrek Taşı |
| **2** | Standard | 2-3 gün içinde | İYE, Bronşit |
| **1** | Elective | Planlanabilir | Kronik ağrılar, Cilt sorunları |

## 🛠️ Kurulum

```bash
pip install -r requirements.txt
```

## 💻 Kullanım / Eğitim

Modeli eğitmek için:

```bash
python train_golden_hour.py
```

Model metriklerini ve data leak kontrolünü yapmak için:

```bash
python audit_leak_overfit.py
```

Modelin karar mekanizmasını (SHAP/Feature Importance) görmek için:

```bash
python explain_model.py
```

## 📂 Proje Yapısı

```
.
├── train_golden_hour.py      # Ana eğitim scripti
├── audit_leak_overfit.py     # Metrik doğrulama ve audit
├── explain_model.py          # Model yorumlanabilirlik analizi
├── cleaned_dataset.csv       # (Git'e eklenmez) Temizlenmiş veri seti
├── disease_list.csv          # (Git'e eklenmez) Hastalık listesi
└── golden_hour_model/
    ├── config/
    │   └── urgency_mapping.py  # 537 hastalık için urgency mapping
    └── models/
        ├── golden_hour_model.pkl      # Eğitilmiş Model
        ├── golden_hour_scaler.pkl     # Ölçekleyici
        ├── golden_hour_artifacts.pkl  # Metadata
        └── golden_hour_metadata.json  # Detaylı metrikler
```

## 🔒 Güvenlik ve Doğrulama
Bu model **Hash-based Deduplication** ve **Strict Train/Test Split** yöntemleri ile veri sızıntısına (data leakage) karşı korunmuştur. Eğitim sürecinde synthetic data'ya noise eklenerek overfitting önlenmiştir.
