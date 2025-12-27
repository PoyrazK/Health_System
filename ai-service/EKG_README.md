# EKG Module README

## 📁 Dosya Yapısı

```
ai-service/
├── app/
│   ├── services/
│   │   └── ekg_service.py      # EKG analiz servisi
│   └── routers/
│       └── ekg_router.py       # API endpoints
├── data/
│   └── ekg/                    # EKG datasets (MIT-BIH, PTB-XL)
├── models/
│   └── ekg/                    # Trained EKG models
│       ├── ekg_classifier.h5
│       ├── ekg_classes.json
│       └── ekg_feedback.csv
└── notebooks/
    └── ekg/                    # Jupyter notebooks
        ├── 01_data_exploration.ipynb
        ├── 02_model_training.ipynb
        └── 03_evaluation.ipynb
```

## 🎯 Özellikler

✅ Signal preprocessing (baseline wander removal, normalization)
✅ Feature extraction (RR intervals, heart rate, QRS)
✅ Deep learning classification (CNN/LSTM)
✅ Rule-based fallback (bradycardia, tachycardia detection)
✅ Feedback logging for incremental learning

## 🚀 Kullanım

### API Endpoints

**1. EKG Analizi**
```bash
POST /api/v1/ekg/analyze
{
  "signal": [0.1, 0.2, ...],  # 1D array
  "sampling_rate": 360
}
```

**2. Dosyadan Analiz**
```bash
POST /api/v1/ekg/analyze-file
# Form-data: file=ekg_signal.csv
```

**3. Demo Signal**
```bash
GET /api/v1/ekg/demo
```

## 📊 Desteklenen Anomaliler

- Normal Sinus Rhythm
- Bradycardia (HR < 60)
- Tachycardia (HR > 100)
- Atrial Fibrillation
- Premature Ventricular Contractions (PVC)
- Myocardial Infarction (MI)

## 🔧 Kurulum

```bash
pip install -r requirements_ekg.txt
```

## 📚 Dataset Kaynakları

1. **MIT-BIH Arrhythmia Database** - PhysioNet
2. **PTB-XL Database** - 21,837 EKG kayıtları
3. **CPSC 2018** - China Physiological Signal Challenge
