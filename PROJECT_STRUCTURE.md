# Healthcare AI System - Proje Dosya Düzeni

```
AdvanceUpHackhathon/
│
├── 📁 ai-service/                   # Python FastAPI AI Service
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point ✅
│   │   ├── services/
│   │   │   ├── ml_service.py       # Disease classifier ✅
│   │   │   ├── ekg_service.py      # EKG analysis 🆕
│   │   │   └── llm_service.py      # LLM integration ✅
│   │   └── routers/
│   │       ├── feedback_router.py  # Feedback endpoints ✅
│   │       ├── llm_router.py       # LLM endpoints ✅
│   │       └── ekg_router.py       # EKG endpoints 🆕
│   ├── data/
│   │   └── ekg/                    # EKG datasets 🆕
│   ├── models/
│   │   ├── disease_classifier.joblib ✅
│   │   ├── feature_columns.json    ✅
│   │   ├── disease_encoding.json   ✅
│   │   └── ekg/                    # EKG models 🆕
│   ├── notebooks/
│   │   └── ekg/                    # Jupyter notebooks 🆕
│   ├── requirements.txt            ✅
│   ├── requirements_ekg.txt        🆕
│   └── EKG_README.md               🆕
│
├── 📁 backend/                      # Go Backend (hazır ama Go kurulu değil)
│   ├── cmd/main.go
│   ├── internal/
│   │   ├── handlers/
│   │   ├── middleware/
│   │   └── models/
│   └── go.mod
│
├── 📁 frontend/                     # React + Vite (henüz oluşturulmadı)
│
├── 📄 cleaned_dataset.csv           # Temizlenmiş hastalık verisi ✅
├── 📄 Disease and symptoms dataset.csv # Raw dataset ✅
├── 📄 data_cleaning.py              # Veri temizleme ✅
├── 📄 eda_analysis.py               # Keşifsel veri analizi ✅
├── 📄 train_model.py                # Model eğitimi ✅
└── 📄 evaluate_model.py             # Model değerlendirme ✅
```

## 🎯 Aktif Özellikler

### ✅ Çalışan Modüller
1. **Disease Classifier** - 527 hastalık, 85% accuracy
2. **Feedback Loop** - Doktor geri bildirimi + incremental learning
3. **LLM Service** - Fallback mode (Gemini API bekliyor)
4. **EKG Service** - Scaffold hazır 🆕

### 🆕 EKG Modülü
- Signal preprocessing ✅
- Feature extraction ✅
- API endpoints ✅
- Model training bekleniyor

### ⏳ Bekleyen
- Go backend (Go kurulumu gerekli)
- React frontend
- Docker containerization

## 📡 API Endpoints (Port 8001)

### Disease Prediction
- `POST /api/v1/predict/disease`
- `POST /api/v1/predict/risk`
- `POST /api/v1/feedback/predict-top3`
- `POST /api/v1/feedback/log`

### EKG Analysis 🆕
- `POST /api/v1/ekg/analyze`
- `POST /api/v1/ekg/analyze-file`
- `POST /api/v1/ekg/feedback`
- `GET /api/v1/ekg/demo`

### LLM
- `POST /api/v1/llm/diagnose`
- `POST /api/v1/llm/explain-lab-results`
