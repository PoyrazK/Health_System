# 🧠 ML Model Documentation - Clinical Copilot

This document provides detailed model cards for all machine learning models deployed in Clinical Copilot.

---

## Model Overview

| Model | Target Condition | Algorithm | Features | Training Samples |
|-------|------------------|-----------|----------|------------------|
| [Heart Disease](#heart-disease-model) | Coronary Heart Disease | XGBoost | 13 | 1,025 |
| [Diabetes](#diabetes-risk-model) | Type 2 Diabetes | XGBoost | 22 | 253,680 |
| [Stroke](#stroke-risk-model) | Stroke Event | XGBoost | 10 | 5,110 |
| [Kidney Disease](#kidney-disease-model) | Chronic Kidney Disease | Random Forest | 24 | 400 |
| [Disease Classifier](#disease-classifier-model) | Multi-Disease Diagnosis | XGBoost | 316 | ~100,000 |
| [EKG Analyzer](#ekg-analyzer-model) | Arrhythmia Classification | XGBoost | 32 | 109,440 |
| [Golden Hour](#golden-hour-model) | Medical Urgency (1-5) | XGBoost | 15+ | ~50,000 |


---


## Heart Disease Model

### Model Card

| Attribute | Value |
|-----------|-------|
| **File** | `models/heart_model.pkl` |
| **Algorithm** | XGBoost Classifier |
| **Training Data** | Cleveland Clinic Heart Disease Dataset |
| **Samples** | 1,025 |
| **Features** | 13 |
| **Target** | Binary (0 = No Disease, 1 = Disease) |

### Features

| Feature | Description | Type | Range/Values |
|---------|-------------|------|--------------|
| `age` | Patient age in years | Numeric | 29-77 |
| `sex` | Biological sex | Binary | 0=Female, 1=Male |
| `cp` | Chest pain type | Categorical | 0-3 |
| `systolic_bp` | Resting blood pressure | Numeric | 94-200 mmHg |
| `cholesterol` | Serum cholesterol | Numeric | 126-564 mg/dL |
| `fasting_bs` | Fasting blood sugar > 120 | Binary | 0/1 |
| `restecg` | Resting ECG results | Categorical | 0-2 |
| `heart_rate` | Maximum heart rate achieved | Numeric | 71-202 bpm |
| `exang` | Exercise induced angina | Binary | 0/1 |
| `oldpeak` | ST depression | Numeric | 0-6.2 |
| `slope` | Slope of peak exercise ST | Categorical | 0-2 |
| `ca` | Number of major vessels | Numeric | 0-4 |
| `thal` | Thalassemia | Categorical | 0-3 |

### Clinical Interpretation

| Risk Score | Interpretation | Recommended Action |
|------------|----------------|-------------------|
| 0-20% | Low risk | Routine monitoring |
| 20-50% | Moderate risk | Lifestyle intervention |
| 50-80% | High risk | Cardiology referral |
| 80-100% | Critical risk | **Immediate evaluation** |

### Limitations

- Dataset is from a single institution (Cleveland Clinic)
- Predominately Caucasian population
- Does not account for genetic markers
- Electrocardiogram features (ECG) require clinical assessment

---

## Diabetes Risk Model

### Model Card

| Attribute | Value |
|-----------|-------|
| **File** | `models/diabetes_model.pkl` |
| **Algorithm** | XGBoost Classifier |
| **Training Data** | BRFSS 2015 (CDC Behavioral Risk Factor Survey) |
| **Samples** | 253,680 |
| **Features** | 22 |
| **Target** | Binary (0 = No Diabetes, 1 = Diabetes/Pre-diabetes) |

### Features

| Feature | Description | Type | Notes |
|---------|-------------|------|-------|
| `history_bp` | History of high blood pressure | Binary | Derived from systolic_bp |
| `history_chol` | History of high cholesterol | Binary | Derived from cholesterol |
| `CholCheck` | Cholesterol check in 5 years | Binary | Default: 1 |
| `bmi` | Body Mass Index | Numeric | Range: 12-98 |
| `Smoker` | Smoking status | Binary | 0/1 |
| `history_stroke` | History of stroke | Binary | Default: 0 |
| `history_heart_disease` | History of heart disease | Binary | Default: 0 |
| `PhysActivity` | Physical activity in past 30 days | Binary | Derived from steps |
| `Fruits` | Fruit consumption | Binary | Default: 1 |
| `Veggies` | Vegetable consumption | Binary | Default: 1 |
| `HvyAlcoholConsump` | Heavy alcohol consumption | Binary | Default: 0 |
| `AnyHealthcare` | Any healthcare coverage | Binary | Default: 1 |
| `NoDocbcCost` | Couldn't see doctor due to cost | Binary | Default: 0 |
| `general_health` | General health (1-5 scale) | Numeric | Default: 3 |
| `MentHlth` | Days of poor mental health | Numeric | 0-30 |
| `physical_health_days` | Days of poor physical health | Numeric | 0-30 |
| `DiffWalk` | Difficulty walking | Binary | Default: 0 |
| `sex` | Biological sex | Binary | 0=Female, 1=Male |
| `Age` | Age category (1-13) | Numeric | Encoded |
| `Education` | Education level | Numeric | 1-6 |
| `Income` | Income level | Numeric | 1-8 |
| `age` | Actual age in years | Numeric | Used in transform |

### Feature Engineering Notes

```python
# Age category encoding
age_cat = max(1, min(13, (age - 18) // 5 + 1))

# Physical activity derived from daily steps
PhysActivity = 1 if steps > 3000 else 0

# Blood pressure history
history_bp = 1 if systolic_bp >= 130 else 0

# Cholesterol history
history_chol = 1 if cholesterol >= 200 else 0
```

### Clinical Interpretation

This model is **conservative** (low false positive rate), which means:
- Low scores (< 5%) indicate minimal metabolic risk
- Moderate scores (5-20%) warrant lifestyle discussion
- High scores (> 20%) suggest pre-diabetic screening

---

## Stroke Risk Model

### Model Card

| Attribute | Value |
|-----------|-------|
| **File** | `models/stroke_model.pkl` |
| **Algorithm** | XGBoost Classifier |
| **Training Data** | Kaggle Stroke Prediction Dataset |
| **Samples** | 5,110 |
| **Features** | 10 |
| **Target** | Binary (0 = No Stroke, 1 = Stroke) |

### Features

| Feature | Description | Type | Encoding |
|---------|-------------|------|----------|
| `gender` | Patient gender | Binary | 0=Female, 1=Male |
| `age` | Patient age | Numeric | Years |
| `hypertension` | Hypertension status | Binary | Derived: systolic_bp > 140 |
| `heart_disease` | Heart disease history | Binary | Default: 0 |
| `ever_married` | Marital status | Binary | Default: 1 |
| `work` | Work type | Categorical | Encoded (0-4) |
| `Residence_type` | Urban/Rural | Binary | Default: 1 (Urban) |
| `glucose` | Average glucose level | Numeric | mg/dL |
| `bmi` | Body Mass Index | Numeric | kg/m² |
| `smoking` | Smoking status | Binary | Encoded |

### Class Imbalance Handling

The original dataset has severe class imbalance:
- Stroke events: ~4.9% (249 cases)
- Non-stroke: ~95.1% (4,861 cases)

**Mitigation:** SMOTE (Synthetic Minority Over-sampling Technique) applied during training.

### Clinical Interpretation

| Risk Score | 10-Year Risk | Action |
|------------|--------------|--------|
| 0-5% | Very Low | Standard preventive care |
| 5-20% | Low | Blood pressure monitoring |
| 20-50% | Moderate | Vascular assessment |
| 50-100% | High | **Neurology referral** |

---

## Kidney Disease Model

### Model Card

| Attribute | Value |
|-----------|-------|
| **File** | `models/kidney_model.pkl` |
| **Algorithm** | Random Forest Classifier |
| **Training Data** | UCI Chronic Kidney Disease Dataset |
| **Samples** | 400 |
| **Features** | 24 |
| **Target** | Binary (0 = No CKD, 1 = CKD) |

### Features

| Feature | Description | Type | Normal Range |
|---------|-------------|------|--------------|
| `age` | Patient age | Numeric | - |
| `diastolic_bp` | Diastolic blood pressure | Numeric | 60-90 mmHg |
| `sg` | Specific gravity (urine) | Numeric | 1.005-1.030 |
| `al` | Albumin in urine | Numeric | 0-5 |
| `su` | Sugar in urine | Numeric | 0-5 |
| `rbc` | Red blood cells | Binary | 0=Abnormal, 1=Normal |
| `pc` | Pus cell | Binary | 0=Abnormal, 1=Normal |
| `pcc` | Pus cell clumps | Binary | 0=Present, 1=Not present |
| `ba` | Bacteria | Binary | 0=Present, 1=Not present |
| `glucose` | Blood glucose | Numeric | 70-140 mg/dL |
| `bu` | Blood urea | Numeric | 7-20 mg/dL |
| `creatinine` | Serum creatinine | Numeric | 0.7-1.3 mg/dL |
| `sod` | Sodium | Numeric | 136-145 mEq/L |
| `pot` | Potassium | Numeric | 3.5-5.0 mEq/L |
| `hemo` | Hemoglobin | Numeric | 12-17 g/dL |
| `pcv` | Packed cell volume | Numeric | 36-48% |
| `wc` | White blood cell count | Numeric | 4,500-11,000 |
| `rc` | Red blood cell count | Numeric | 4.5-5.5 million |
| `history_bp` | Hypertension history | Binary | - |
| `history_diabetes` | Diabetes history | Binary | Derived: glucose > 140 |
| `cad` | Coronary artery disease | Binary | Default: 0 |
| `appet` | Appetite | Binary | 0=Poor, 1=Good |
| `pe` | Pedal edema | Binary | - |
| `ane` | Anemia | Binary | - |

### Missing Data Strategy

The UCI CKD dataset has significant missing values (1,009 total). Imputation strategy:
- Numeric: Median imputation
- Categorical: Mode imputation
- Lab values: Clinical normal defaults when unavailable

### Clinical Interpretation

| Risk Score | CKD Stage Correlation | Notes |
|------------|----------------------|-------|
| 0-10% | Stage 1 (Normal) | eGFR > 90 |
| 10-30% | Stage 2 (Mild) | Monitor annually |
| 30-60% | Stage 3 (Moderate) | Nephrology referral |
| 60-100% | Stage 4-5 (Severe) | **Urgent nephrology** |

---

## Model Confidence Scoring

### Clinical Confidence Calculation

```python
# Distance from decision boundary (50%)
risks = [heart_risk, diabetes_risk, stroke_risk, kidney_risk]
confidence = mean([abs(risk - 50) * 2 for risk in risks])
clinical_confidence = max(85, min(99.8, confidence))
```

### Per-Model Precision

```python
model_precisions = {
    'XGBoost Heart': 80 + abs(heart_risk - 50) * 0.4,
    'RF Diabetes': 85 + abs(diabetes_risk - 50) * 0.3,
    'GBM Stroke': 82 + abs(stroke_risk - 50) * 0.35
}
```

**Interpretation:** Models show higher confidence when predictions are far from 50% (either clearly positive or clearly negative).

---

## Evaluation Results

Based on 100-patient evaluation cohort (`data/evaluation_results.csv`):

### Risk Score Distributions

| Model | Min (%) | Max (%) | Mean (%) | Std Dev |
|-------|---------|---------|----------|---------|
| Heart | 2.68 | 95.30 | 35.2 | 24.1 |
| Diabetes | 0.13 | 30.55 | 3.5 | 5.2 |
| Stroke | 0.00 | 96.57 | 12.1 | 21.3 |
| Kidney | 8 | 64 | 19.1 | 12.4 |

### Health Score Distribution

- **Mean:** 83.2
- **Min:** 49.75 (critical patient)
- **Max:** 96.75 (healthy young patient)

---

## Model Retraining Recommendations

### When to Retrain

1. **Data Drift:** If patient demographics shift significantly
2. **Performance Degradation:** If clinical feedback shows consistent errors
3. **New Features:** When new biomarkers become available
4. **Regulatory Updates:** When clinical thresholds change

### Feedback Loop Integration

Doctor feedback stored in the `feedbacks` table can be used to:
1. Identify systematic model errors
2. Create curated validation datasets
3. Fine-tune decision thresholds
4. Generate retraining datasets

---

## Ethical Considerations

### Bias Assessment

| Concern | Status | Mitigation |
|---------|--------|------------|
| Age Bias | ⚠️ Potential | Elderly overrepresented in heart data |
| Gender Bias | ⚠️ Potential | Some datasets have gender imbalance |
| Racial Bias | ⚠️ Potential | Cleveland data is predominantly Caucasian |
| Socioeconomic | ✅ Addressed | BRFSS includes diverse income levels |

### Recommendations

1. **Validation** on diverse patient populations before clinical deployment
2. **Explainability** via SHAP values for each prediction
3. **Human oversight** - all predictions require clinician review
4. **Regular audits** of prediction accuracy across demographics

---

## Disease Classifier Model

### Model Card

| Attribute | Value |
|-----------|-------|
| **File** | `models/disease/disease_classifier_pruned.joblib` |
| **Algorithm** | XGBoost Classifier (Pruned) |
| **Training Data** | Kaggle Disease-Symptom Dataset |
| **Samples** | ~100,000 |
| **Features** | 316 (symptom columns) |
| **Target** | Multi-class (527 diseases) |

### Features

The model uses **316 binary symptom features**, including:

| Category | Examples |
|----------|----------|
| Cardiovascular | chest pain, palpitations, irregular heartbeat |
| Respiratory | cough, shortness of breath, wheezing |
| Neurological | headache, dizziness, seizures |
| Gastrointestinal | nausea, vomiting, diarrhea |
| Dermatological | skin rash, itching, swelling |

### Output

Returns **Top-K** predictions with:
- Disease name
- Probability (0-100%)
- Confidence level (high/medium/low)

### Clinical Interpretation

| Probability | Meaning | Action |
|-------------|---------|--------|
| >70% | Highly likely | Primary consideration |
| 30-70% | Possible | Differential diagnosis |
| <30% | Unlikely | Rule-out consideration |

### Feedback Loop

- Physicians can log confirmed diagnoses via `/disease/feedback`
- Feedback stored in `models/disease/feedback_log.csv`
- Supports incremental model retraining

---

## EKG Analyzer Model

### Model Card

| Attribute | Value |
|-----------|-------|
| **File** | `models/ekg/ekg_xgboost.joblib` |
| **Algorithm** | XGBoost Classifier |
| **Training Data** | MIT-BIH Arrhythmia Database |
| **Samples** | 109,440 annotated beats |
| **Features** | 32 (signal features) |
| **Target** | Multi-class (N, S, V - 3 classes) |

### Classes

| Class | Name | Description | Urgency |
|-------|------|-------------|---------|
| N | Normal | Normal sinus rhythm | Low |
| S | SVEB | Supraventricular ectopic beat | Medium |
| V | VEB | Ventricular ectopic beat | **High** |

### Features Extracted

| Feature Group | Features |
|---------------|----------|
| RR Intervals | pre-RR, post-RR, RR ratio |
| Peak Amplitudes | pPeak, qPeak, rPeak, sPeak, tPeak |
| Intervals | QRS, PQ, QT, ST intervals |
| Morphology | qrs_morph0-4 (5 coefficients) |

### Signal Preprocessing

1. **High-pass filter** (0.5 Hz) - Remove baseline wander
2. **Z-score normalization** - Standardize amplitude
3. **Resampling** - Fixed window extraction

### Performance Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 99.2% |
| Top-3 Accuracy | 100% |
| Macro F1 | 94.0% |
| Train-Test Gap | <5% |

### Clinical Interpretation

| Prediction | Meaning | Recommended Action |
|------------|---------|-------------------|
| Normal Sinus Rhythm | Healthy rhythm | Routine monitoring |
| SVEB (Supraventricular) | Atrial origin ectopy | Cardiology follow-up |
| VEB (Ventricular) | **Life-threatening risk** | **Immediate evaluation** |

---

## Golden Hour Model

### Model Card

| Attribute | Value |
|-----------|-------|
| **File** | `src/api/ml_api/models/golden_hour/golden_hour_model.pkl` |
| **Algorithm** | XGBoost Multi-Class Classifier |
| **Training Data** | Synthetic Emergency Triage Dataset |
| **Samples** | ~50,000 |
| **Features** | 15+ (Vitals + Select Symptoms) |
| **Target** | Triage Category (1-5) |

### Urgency levels

| Level | Name | Description | Golden Hour |
|-------|------|-------------|-------------|
| 5 | Critical | Life-threatening, immediate intervention required | < 15 mins |
| 4 | Emergent | Severe condition, high risk of deterioration | < 60 mins |
| 3 | Urgent | Stable but requires evaluation within 24h | < 24 hours |
| 2 | Standard | Non-urgent, routine care | N/A |
| 1 | Elective | Preventive or scheduled care | N/A |

### Features

- **Vitals**: Age, Systolic BP, Diastolic BP, Glucose, BMI, Cholesterol, Heart Rate.
- **Critical Symptoms**: Chest pain, shortness of breath, dizziness, sudden weakness, severe pain.

### Clinical Interpretation

The model predicts the probability of each triage level. The highest probability level is returned as the primary recommendation.

| Probability | Interpretation |
|-------------|----------------|
| >0.7 | High Confidence Triage |
| 0.4 - 0.7 | Moderate Confidence - Monitor closely |
| <0.4 | Low Confidence - Human triage required |

---

## File Locations



```
/models/
├── heart_model.pkl           # 140 KB - XGBoost
├── diabetes_model.pkl        # 437 KB - XGBoost  
├── stroke_model.pkl          # 259 KB - XGBoost
├── kidney_model.pkl          # 195 KB - Random Forest
├── model_metadata.json       # Feature specifications
├── disease/
│   ├── disease_classifier_pruned.joblib  # 28 MB - XGBoost
│   ├── feature_columns.json              # Symptom list
│   └── disease_encoding.json             # Disease labels
└── ekg/
    ├── ekg_xgboost.joblib    # 3.7 MB - XGBoost
    ├── ekg_scaler.joblib     # Normalization scaler
    └── ekg_classes.json      # Class labels
```


---

*Last updated: December 26, 2025*
