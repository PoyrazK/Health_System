# Healthcare AI - Organized File Structure

## 📁 Data Organization

### Disease Module
```
ai-service/data/disease/
├── raw/
│   └── Disease_and_symptoms_dataset.csv  # Original 190MB dataset
└── processed/
    └── cleaned_dataset.csv                # Cleaned 242,837 samples
```

### EKG Module
```
ai-service/data/ekg/
├── mit-bih/       # MIT-BIH Arrhythmia Database
├── ptb-xl/        # PTB-XL Database  
└── processed/     # Preprocessed signals
```

## 🤖 Model Organization

### Disease Models
```
ai-service/models/disease/
├── disease_classifier.joblib      # XGBoost model (85.08% acc)
├── feature_columns.json           # 316 feature names
├── disease_encoding.json          # 527 disease labels
├── model_info.json                # Metrics & metadata
├── feature_importance.csv         # Feature rankings
├── feedback_log.csv               # Doctor feedback
└── versions/                       # Model versions
    ├── model_backup_YYYYMMDD.joblib
    └── model_v_YYYYMMDD.joblib
```

### EKG Models
```
ai-service/models/ekg/
├── ekg_classifier.h5              # TensorFlow/Keras CNN model
├── ekg_classes.json               # Arrhythmia classes
├── ekg_feedback.csv               # Feedback log
└── versions/                       # Model versions
```

## 🔧 Service Path Updates

**ml_service.py** → Uses `models/disease/`
**ekg_service.py** → Uses `models/ekg/`

## 📊 Benefits

✅ **Modular** - Each module isolated
✅ **Scalable** - Easy to add new modules (X-ray, MRI, etc.)
✅ **Clean** - Clear separation of concerns
✅ **Version Control** - Each module has own versions
