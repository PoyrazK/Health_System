import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
import joblib
import json
from pathlib import Path

# Config
DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")
METADATA_FILE = MODEL_DIR / "model_metadata.json"

metadata = {}

def train_heart():
    print("🫀 Training Heart Model...")
    df = pd.read_parquet(DATA_DIR / "heart.parquet")
    X = df.drop('target_heart', axis=1)
    y = df['target_heart']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBClassifier(eval_metric='logloss')
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"   Heart Acc: {acc:.4f}")
    
    joblib.dump(model, MODEL_DIR / "heart_model.pkl")
    metadata['heart'] = {'features': list(X.columns), 'type': 'xgboost'}

def train_diabetes():
    print("🍬 Training Diabetes Model...")
    df = pd.read_parquet(DATA_DIR / "diabetes.parquet")
    X = df.drop('target_diabetes', axis=1)
    y = df['target_diabetes']
    
    # Verify glucose is in features
    if 'glucose' in X.columns:
        print(f"   ✅ Glucose feature present (corr with target: {df['glucose'].corr(y):.3f})")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Handle class imbalance (14% diabetics)
    scale_pos_weight = (len(y) - y.sum()) / y.sum()
    
    model = xgb.XGBClassifier(
        eval_metric='logloss',
        scale_pos_weight=scale_pos_weight,
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1
    )
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, preds)
    auc = roc_auc_score(y_test, probs)
    print(f"   Diabetes Acc: {acc:.4f}, AUC: {auc:.4f}")
    
    # Feature importance check
    importance = dict(zip(X.columns, model.feature_importances_))
    top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"   Top features: {[f[0] for f in top_features]}")
    
    joblib.dump(model, MODEL_DIR / "diabetes_model.pkl")
    metadata['diabetes'] = {'features': list(X.columns), 'type': 'xgboost'}

def train_stroke():
    print("🧠 Training Stroke Model...")
    df = pd.read_parquet(DATA_DIR / "stroke.parquet")
    X = df.drop('target_stroke', axis=1)
    y = df['target_stroke']
    
    # Handle Imbalance
    scale_pos_weight = (len(y) - y.sum()) / y.sum()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBClassifier(scale_pos_weight=scale_pos_weight, eval_metric='auc')
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    roc = roc_auc_score(y_test, preds)
    print(f"   Stroke ROC-AUC: {roc:.4f}")
    
    joblib.dump(model, MODEL_DIR / "stroke_model.pkl")
    metadata['stroke'] = {'features': list(X.columns), 'type': 'xgboost'}

def train_kidney():
    print("🧪 Training Kidney Model...")
    df = pd.read_parquet(DATA_DIR / "kidney.parquet")
    X = df.drop('target_kidney', axis=1)
    y = df['target_kidney']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Use RF for small data
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"   Kidney Acc: {acc:.4f}")
    
    joblib.dump(model, MODEL_DIR / "kidney_model.pkl")
    metadata['kidney'] = {'features': list(X.columns), 'type': 'sklearn_rf'}

def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    train_heart()
    train_diabetes()
    train_stroke()
    train_kidney()
    
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"\n✅ All models trained and saved to {MODEL_DIR}")

if __name__ == "__main__":
    main()
