# 🏥 EKG Arrhythmia Classification Pipeline

## 📋 Overview

Complete modular pipeline for EKG arrhythmia classification supporting 5 classes:
- **N** - Normal Sinus Rhythm
- **S** - SVEB (Supraventricular Ectopic Beat)
- **V** - VEB (Ventricular Ectopic Beat)  
- **F** - VF/Flutter
- **Q** - Noise/Unclassifiable

## 🎯 Pipeline Components

### 1. **ekg_preprocessing.py** - Data Preprocessing
**Features:**
- ✅ Data cleaning (duplicates, missing values, length filtering)
- ✅ Signal preprocessing (baseline wander removal, Z-norm)
- ✅ Resampling to fixed length (256 samples)
- ✅ SMOTE balancing for imbalanced classes
- ✅ Feature engineering (statistical, frequency, heart rate)
- ✅ Stratified train/val/test split (70/15/15)

**Usage:**
```bash
python ekg_preprocessing.py
```

**Output:**
- `ekg_data.npz` - Signals for CNN
- `ekg_features.csv` - Features for XGBoost
- `label_map.json` - Class mapping
- `preprocessing_metadata.json` - Config

### 2. **ekg_train_xgboost.py** - XGBoost Model
**Features:**
- ✅ Class-weighted training
- ✅ Early stopping on validation
- ✅ Top-3 accuracy metric
- ✅ Per-class performance

**Usage:**
```bash
python ekg_train_xgboost.py
```

**Output:**
- `ekg_xgboost.json` - Trained model
- `ekg_xgboost_metrics.json` - Performance

### 3. **ekg_train_cnn.py** - 1D CNN Model  
**Features:**
- ✅ 3-block Conv1D architecture
- ✅ BatchNorm + Dropout
- ✅ Learning rate reduction
- ✅ Model checkpointing

**Usage:**
```bash
python ekg_train_cnn.py
```

**Output:**
- `ekg_cnn_classifier.h5` - Trained model
- `ekg_cnn_metrics.json` - Performance
- `ekg_cnn_history.json` - Training history

## 🔧 Installation

```bash
# Core dependencies (already in requirements.txt)
pip install numpy pandas scikit-learn xgboost

# For CNN training
pip install tensorflow scipy

# For SMOTE balancing
pip install imbalanced-learn
```

## 📊 Expected Performance

| Model | Top-1 Accuracy | Top-3 Accuracy |
|-------|----------------|----------------|
| XGBoost | ~80-85% | ~92-95% |
| 1D-CNN | ~85-90% | ~95-97% |

## 🗂️ Data Format

Input CSV should have:
- `signal_0`, `signal_1`, ... `signal_N` columns (raw EKG values)
- `label` column (N, S, V, F, Q)

Or use MIT-BIH / PTB-XL dataset format.

## 🚀 Quick Start

```bash
# 1. Preprocess data
python ekg_preprocessing.py

# 2. Train XGBoost (fast, good baseline)
python ekg_train_xgboost.py

# 3. Train CNN (better accuracy)
python ekg_train_cnn.py

# 4. Models ready in models/ekg/
```

## 🎓 Pipeline Design Principles

1. **Modular** - Each component independent
2. **Reusable** - Easy to adapt for other datasets
3. **Production-Ready** - Class weights, validation, versioning
4. **Bias-Free** - SMOTE balancing, stratified splits
5. **Unbiased** - No data leakage, proper preprocessing order

## 📈 Model Comparison

**XGBoost:**
- ✅ Fast training (minutes)
- ✅ Good interpretability (feature importance)
- ✅ Works well with engineered features
- ⚠️ May miss temporal patterns

**1D-CNN:**
- ✅ Learns temporal patterns automatically
- ✅ Higher accuracy
- ✅ No manual feature engineering
- ⚠️ Slower training (GPU recommended)

## 🔄 Next Steps

1. Download real EKG dataset (MIT-BIH, PTB-XL)
2. Run preprocessing pipeline
3. Train both models
4. Compare performance
5. Deploy best model to `ekg_service.py`
6. Integrate with frontend

---

**Status:** ✅ Pipeline Ready | ⏳ Needs Dataset
