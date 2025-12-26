import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Configuration
RAW_DIR = Path("data/raw")
REPORT_DIR = Path("experiments")
REPORT_FILE = REPORT_DIR / "eda_report.md"

# Standardized Column Map
COLUMN_MAP = {
    # Heart Dataset
    'trtbps': 'systolic_bp',
    'chol': 'cholesterol',
    'thalachh': 'heart_rate',
    'fbs': 'fasting_bs',
    'output': 'target_heart',
    
    # Diabetes Dataset
    'HighBP': 'hypertension_history', # Not exact BP value
    'HighChol': 'high_chol_history', # Not exact chold value
    'GenHlth': 'general_health',
    'PhysHlth': 'physical_health_days',
    'MentHlth': 'mental_health_days',
    'Diabetes_binary': 'target_diabetes',
    
    # Stroke Dataset
    'avg_glucose_level': 'glucose_avg',
    'stroke': 'target_stroke',
    
    # Kidney Dataset
    'bp': 'diastolic_bp', # Usually Diastolic in this dataset context or general
    'sc': 'creatinine',
    'classification': 'target_kidney',
    'dm': 'has_diabetes',
    'htn': 'has_hypertension'
}

class HealthcareEDA:
    def __init__(self):
        self.datasets = {}
        self.report_buffer = []

    def log(self, text, level=1):
        """Append text to markdown report buffer"""
        prefix = "#" * level + " "
        self.report_buffer.append(f"{prefix}{text}\n")
        print(text)

    def load_data(self):
        self.log("Dataset Loading & Overview")
        
        try:
            self.datasets['heart'] = pd.read_csv(RAW_DIR / "heart.csv")
            self.datasets['diabetes'] = pd.read_csv(RAW_DIR / "diabetes.csv")
            self.datasets['stroke'] = pd.read_csv(RAW_DIR / "stroke.csv")
            self.datasets['kidney'] = pd.read_csv(RAW_DIR / "kidney.csv")
            
            for name, df in self.datasets.items():
                self.log(f"Dataset: {name.upper()}", level=3)
                self.log(f"- Shape: {df.shape}")
                self.log(f"- Columns: {', '.join(df.columns[:5])}...")
                self.log(f"- Missing Values: {df.isnull().sum().sum()}")
                self.report_buffer.append(f"\n```\n{df.head(2).to_string()}\n```\n")

        except Exception as e:
            self.log(f"Error loading datasets: {e}")

    def clean_kidney_data(self):
        """Special cleaning for messy Kidney dataset"""
        df = self.datasets.get('kidney')
        if df is not None:
            # Drop id
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
            
            # Convert tabular/text based numbers to floats
            numeric_cols = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Clean categorical
            df = df.replace(to_replace={'\tno': 'no', '\tyes': 'yes', ' yes': 'yes'})
            df['classification'] = df['classification'].replace('ckd\t', 'ckd')
            
            # Encode Target: ckd=1, notckd=0
            df['target_kidney'] = df['classification'].map({'ckd': 1, 'notckd': 0})
            df = df.drop('classification', axis=1)
            
            self.datasets['kidney'] = df
            self.log("Cleaned Kidney Dataset (Fixed numeric parsing and tabular junk)", level=4)

    def analyze_overlap(self):
        self.log("Feature Overlap Analysis", level=2)
        
        common_concepts = {
            'Age': {'heart': 'age', 'diabetes': 'Age', 'stroke': 'age', 'kidney': 'age'},
            'Sex/Gender': {'heart': 'sex', 'diabetes': 'Sex', 'stroke': 'gender', 'kidney': None},
            'BMI': {'heart': None, 'diabetes': 'BMI', 'stroke': 'bmi', 'kidney': None},
            'Blood Pressure': {'heart': 'trtbps', 'diabetes': 'HighBP', 'stroke': 'hypertension', 'kidney': 'bp'},
            'Glucose': {'heart': 'fbs', 'diabetes': 'Diabetes_binary', 'stroke': 'avg_glucose_level', 'kidney': 'bgr'},
            'Cholesterol': {'heart': 'chol', 'diabetes': 'HighChol', 'stroke': None, 'kidney': None}
        }
        
        table = "| Concept | Heart | Diabetes | Stroke | Kidney |\n|---|---|---|---|---|\n"
        for concept, map_dict in common_concepts.items():
            row = f"| **{concept}** | "
            for ds in ['heart', 'diabetes', 'stroke', 'kidney']:
                col = map_dict.get(ds)
                status = f"`{col}`" if col and col in self.datasets.get(ds, pd.DataFrame()).columns else "❌"
                # Kidney special check
                if ds == 'kidney' and concept == 'Blood Pressure' and 'bp' in self.datasets['kidney'].columns:
                     status = "`bp`"
                row += f"{status} | "
            table += row + "\n"
        
        self.report_buffer.append(table)

    def generate_report(self):
        self.load_data()
        self.clean_kidney_data()
        self.analyze_overlap()
        
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        with open(REPORT_FILE, "w") as f:
            f.writelines(self.report_buffer)
        
        print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    eda = HealthcareEDA()
    eda.generate_report()
