import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

# Paths
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
MODEL_DIR = Path("models")

class FeaturePipeline:
    def __init__(self):
        self.imputer = IterativeImputer(random_state=42)
        self.scaler = StandardScaler()
        self.scalers = {} # One per dataset concept if needed, or global
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

    def load_heart(self):
        df = pd.read_csv(RAW_DIR / "heart.csv")
        # Rename standards
        # Note: In EDA we saw 'trestbps', not 'trtbps'
        rename_dict = {
            'trestbps': 'systolic_bp', 
            'trtbps': 'systolic_bp', # Handle both just in case
            'chol': 'cholesterol',
            'thalach': 'heart_rate',
            'trestbps': 'systolic_bp',
            'fbs': 'fasting_bs', # 1 if > 120 mg/dl
            'target': 'target_heart'
        }
        df = df.rename(columns=rename_dict)
        
        # FIX: In this UCI Heart dataset version, labels are INVERTED!
        # target=1 means healthy, target=0 means disease
        # We invert to: 1 = has disease, 0 = healthy
        df['target_heart'] = 1 - df['target_heart']
        
        return df

    def load_diabetes(self):
        df = pd.read_csv(RAW_DIR / "diabetes.csv")
        rename_dict = {
            'Diabetes_binary': 'target_diabetes',
            'HighBP': 'history_bp', # 0/1
            'HighChol': 'history_chol', # 0/1
            'HeartDiseaseorAttack': 'history_heart_disease',
            'Stroke': 'history_stroke',
            'GenHlth': 'general_health',
            'PhysHlth': 'physical_health_days'
        }
        df = df.rename(columns=rename_dict)
        
        # TRANSFORMATION: Convert Categorical Age (1-13) to Numeric Estimate
        # 1: 18-24, 2: 25-29 ... 13: 80+
        # Approx formula: Age * 5 + 17
        df['age'] = df['Age'] * 5 + 17
        
        # TRANSFORMATION: BMI is already numeric
        df = df.rename(columns={'BMI': 'bmi', 'Sex': 'sex'})
        
        # SYNTHETIC GLUCOSE FEATURE
        # Generate realistic glucose based on clinical correlations:
        # - Base: 90 mg/dL (healthy fasting)
        # - Diabetics have ~40-80 mg/dL higher average
        # - BMI > 30 adds ~10-20 mg/dL
        # - Older age adds ~5-15 mg/dL
        # - HighBP correlation adds ~5-10 mg/dL
        np.random.seed(42)  # Reproducibility
        
        base_glucose = 90
        diabetes_effect = df['target_diabetes'] * np.random.uniform(40, 80, len(df))
        bmi_effect = np.clip((df['bmi'] - 25) * 1.2, 0, 30)
        age_effect = (df['Age'] - 5) * 1.5  # Age category effect
        bp_effect = df['history_bp'] * np.random.uniform(5, 15, len(df))
        noise = np.random.normal(0, 12, len(df))
        
        df['glucose'] = np.clip(
            base_glucose + diabetes_effect + bmi_effect + age_effect + bp_effect + noise,
            70, 300  # Clinical range
        ).astype(int)
        
        print(f"   📊 Synthetic glucose generated: Mean={df['glucose'].mean():.1f}, "
              f"Diabetic avg={df[df['target_diabetes']==1]['glucose'].mean():.1f}, "
              f"Non-diabetic avg={df[df['target_diabetes']==0]['glucose'].mean():.1f}")
        
        return df

    def load_stroke(self):
        df = pd.read_csv(RAW_DIR / "stroke.csv")
        df = df.drop('id', axis=1)
        rename_dict = {
            'avg_glucose_level': 'glucose',
            'work_type': 'work',
            'smoking_status': 'smoking',
            'stroke': 'target_stroke'
        }
        df = df.rename(columns=rename_dict)
        
        # Encoding
        le = LabelEncoder()
        cats = ['gender', 'ever_married', 'work', 'Residence_type', 'smoking']
        for c in cats:
            if c in df.columns:
                df[c] = le.fit_transform(df[c].astype(str))
                
        return df

    def load_kidney(self):
        # We need the cleaned version logic from EDA again
        df = pd.read_csv(RAW_DIR / "kidney.csv")
        if 'id' in df.columns: df = df.drop('id', axis=1)
        
        # Fix numerics
        numeric_cols = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc']
        for col in numeric_cols:
             # Basic clean non-numeric chars
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fix categorical target
        df['classification'] = df['classification'].astype(str).str.replace('\t', '')
        df['target_kidney'] = df['classification'].map({'ckd': 1, 'notckd': 0})
        df = df.drop('classification', axis=1)
        
        # Rename
        rename_dict = {
            'bp': 'diastolic_bp', # CKD dataset usually lists Diastolic or Mean, let's treat as Diastolic for now or just 'bp'
            'bgr': 'glucose',
            'sc': 'creatinine',
            'htn': 'history_bp',
            'dm': 'history_diabetes'
        }
        df = df.rename(columns=rename_dict)
        
        # Encode yes/no
        for col in df.columns:
            if df[col].dtype == 'object':
                # Strip whitespace first (careful: turns NaN into 'nan')
                df[col] = df[col].astype(str).str.strip()
                # Replace values, including fixing the 'nan' string we just created
                df[col] = df[col].replace({
                    'yes': 1, 'no': 0, 
                    'present': 1, 'notpresent': 0,
                    'normal': 0, 'abnormal': 1,
                    'good': 0, 'poor': 1,
                    'nan': np.nan, 'None': np.nan
                })
                # Force numeric conversion where possible
                df[col] = pd.to_numeric(df[col], errors='coerce')
                    
        return df

    def process(self):
        print("🚀 Starting Feature Pipeline...")
        
        # 1. Load All
        heart_df = self.load_heart()
        diabetes_df = self.load_diabetes()
        stroke_df = self.load_stroke()
        kidney_df = self.load_kidney()
        
        # 2. Impute (Specific for each dataset to maintain local consistency)
        print("🧩 Imputing missing values...")
        
        # Stroke BMI is missing often. Impute BMI using Age and Glucose relationship.
        imputed_cols = ['bmi', 'age', 'glucose']
        stroke_df[imputed_cols] = self.imputer.fit_transform(stroke_df[imputed_cols])
        
        # Kidney is very messy
        # We impute numeric columns
        k_num_cols = kidney_df.select_dtypes(include=[np.number]).columns
        # Filter out columns that are completely empty (all NaNs)
        valid_k_cols = [c for c in k_num_cols if kidney_df[c].notna().sum() > 0]
        if valid_k_cols:
             kidney_df[valid_k_cols] = self.imputer.fit_transform(kidney_df[valid_k_cols])
        
        # 3. Save Processed Chunks
        print("💾 Saving parquet files...")
        heart_df.to_parquet(PROCESSED_DIR / "heart.parquet")
        diabetes_df.to_parquet(PROCESSED_DIR / "diabetes.parquet")
        stroke_df.to_parquet(PROCESSED_DIR / "stroke.parquet")
        kidney_df.to_parquet(PROCESSED_DIR / "kidney.parquet")
        
        print("✅ Feature Pipeline Complete. Data ready for training.")

if __name__ == "__main__":
    fp = FeaturePipeline()
    fp.process()
