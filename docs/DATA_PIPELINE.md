# 🛠️ Data Engineering & Feature Pipeline

The reliability of clinical predictions depends on high-quality data. Clinical Copilot v3.0 introduces a robust automated pipeline to handle heterogeneous healthcare datasets.

---

## 🏗️ The Unified Feature Pipeline

Located in `src/features/feature_pipeline.py`, this engine transforms raw, messy clinical datasets into standardized training and inference artifacts.

### 1. Data Cleaning & Standardization
- **Naming Alignment**: Maps varied column names (e.g., `trestbps`, `trtbps`, `bp`) to a unified clinical standard (`systolic_bp`).
- **Label Correction**: Automates the inversion of labels where needed (e.g., UCI Heart dataset healthy/disease correction).
- **Type Safety**: Forces numeric conversion and handles non-numeric "garbage" strings in clinical notes.

### 2. Advanced Imputation (IterativeImputer)
We use **Scikit-Learn's IterativeImputer** (MICE - Multivariate Imputation by Chained Equations) instead of simple mean/median fills.
- **Context-Aware**: BMI is imputed based on the relationship between Age and Glucose, rather than a global average.
- **Kidney Dataset Cleaning**: Handles the extremely sparse columns characteristic of CKD patient records.

### 3. Synthetic Clinical Feature Generation
To enhance model performance in data-sparse environments, the pipeline generates high-fidelity synthetic features:
- **Synthetic Glucose**: For the BRFSS Diabetes dataset (which lacks glucose), we generate realistic values based on a mathematical model of BMI, Age, HighBP history, and Diabetes status.
- **Normalization**: Scales features like Age from categorical brackets (1-13) to realistic continuous estimates (18-80+).

---

## 📋 Extended Clinical Profile

We have expanded the patient data model to include **Medical History Flags**, allowing for more nuanced assessments.

| New Feature | Description |
|-------------|-------------|
| `history_heart_disease` | Prior diagnosis of CAD or Heart Attack. |
| `history_stroke` | History of TIA or ischemic/hemorrhagic stroke. |
| `history_diabetes` | Established diabetic diagnosis. |
| `history_high_chol` | Chronic hyperlipidemia status. |

---

## 🔄 Execution Flow

```mermaid
graph LR
    A[Raw CSVs] --> B[Standardize Names]
    B --> C[Iterative Imputation]
    C --> D[Synthetic Feature Gen]
    D --> E[Parquet Artifacts]
    E --> F[Model Training]
```

### Usage
To refresh the training data:
```bash
python src/features/feature_pipeline.py
```

---
*Ensuring clinical data integrity through automated engineering.*
