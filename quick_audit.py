import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split

BASE_DIR = Path('c:/Users/muham/OneDrive/Masaüstü/AdvanceUp2')
DATA_PATH = BASE_DIR / 'cleaned_dataset.csv'
MODEL_DIR = BASE_DIR / 'golden_hour_model' / 'models'

GOLDEN_HOUR_MAPPING = {
    'heart attack': 5, 'cardiac arrest': 5, 'stroke': 5, 
    'intracerebral hemorrhage': 5, 'subarachnoid hemorrhage': 5, 
    'sepsis': 5, 'pulmonary embolism': 5, 'pneumothorax': 5,
    'acute respiratory distress syndrome (ards)': 5,
    'gastrointestinal hemorrhage': 5, 'meningitis': 5, 'ectopic pregnancy': 5,
    'transient ischemic attack': 4, 'acute glaucoma': 4, 
    'diabetic ketoacidosis': 4, 'appendicitis': 4, 
    'acute pancreatitis': 4, 'testicular torsion': 4, 'asthma': 4,
}

df = pd.read_csv(DATA_PATH)
golden_hour_names = list(GOLDEN_HOUR_MAPPING.keys())
df_filtered = df[df['diseases'].str.lower().isin(golden_hour_names)].copy()
df_filtered['urgency_level'] = df_filtered['diseases'].str.lower().map(GOLDEN_HOUR_MAPPING)

print('='*60)
print('URGENCY DAGILIMI:')
uc = df_filtered['urgency_level'].value_counts().sort_index()
for lvl, cnt in uc.items():
    print(f'  Urgency {lvl}: {cnt} ({cnt/len(df_filtered)*100:.1f}%)')
print(f'  Toplam: {len(df_filtered)}')

# Class imbalance
ratio = uc.max() / uc.min()
print(f'\nImbalance Ratio: {ratio:.2f}:1')

model = joblib.load(MODEL_DIR / 'golden_hour_model.pkl')
scaler = joblib.load(MODEL_DIR / 'golden_hour_scaler.pkl')
artifacts = joblib.load(MODEL_DIR / 'golden_hour_artifacts.pkl')

feature_names = artifacts['feature_names']
label_map = artifacts['label_map']
reverse_map = {v: k for k, v in label_map.items()}

X = df_filtered[feature_names].values
y = df_filtered['urgency_level'].values

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, stratify=y, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.176, stratify=y_temp, random_state=42)

print(f'\n  Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}')

# Test
X_test_s = scaler.transform(X_test)
y_test_adj = np.array([label_map[x] for x in y_test])
y_pred = model.predict(X_test_s)

print('='*60)
print('TEST SONUCLARI (GERCEK VERI):')
acc = accuracy_score(y_test_adj, y_pred)
f1 = f1_score(y_test_adj, y_pred, average='macro')
print(f'  Accuracy: {acc:.4f} ({acc*100:.2f}%)')
print(f'  F1 Macro: {f1:.4f}')
print(f'\nConfusion Matrix:')
cm = confusion_matrix(y_test_adj, y_pred)
for i, row in enumerate(cm):
    print(f'  Urgency {reverse_map[i]}: {list(row)}')

# Train vs Val
X_train_s = scaler.transform(X_train)
X_val_s = scaler.transform(X_val)
y_train_adj = np.array([label_map[x] for x in y_train])
y_val_adj = np.array([label_map[x] for x in y_val])

train_f1 = f1_score(y_train_adj, model.predict(X_train_s), average='macro')
val_f1 = f1_score(y_val_adj, model.predict(X_val_s), average='macro')
print(f'\n  Train F1: {train_f1:.4f}')
print(f'  Val F1: {val_f1:.4f}')
print(f'  Overfit Gap: {train_f1 - val_f1:.4f}')

# Duplicate check
dup = df_filtered.duplicated(subset=feature_names).sum()
print(f'\nDuplicate samples: {dup} ({dup/len(df_filtered)*100:.1f}%)')
if dup > 0:
    print('  WARNING: DUPLICATES EXIST - potential data leakage!')
