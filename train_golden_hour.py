"""
Golden Hour Model - Multi-Class Training Script (FIXED v2)
Correct overfit calculation: uses REAL training data, not augmented/noisy data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.utils import resample
from sklearn.metrics import classification_report, f1_score, recall_score, accuracy_score, confusion_matrix
import sys

# Add project root to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from golden_hour_model.config.urgency_mapping import URGENCY_MAPPING, get_urgency, DEFAULT_URGENCY

# Paths
DATA_PATH = BASE_DIR / 'cleaned_dataset.csv'
OUTPUT_DIR = BASE_DIR / 'golden_hour_model' / 'models'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_and_prepare_data(data_path):
    """Load dataset and assign urgency levels to ALL diseases"""
    print("="*60)
    print("PHASE 1: DATA LOADING")
    print("="*60)
    
    df = pd.read_csv(data_path)
    print(f"  Original dataset: {df.shape}")
    
    # Assign urgency levels using mapping
    df['urgency_level'] = df['diseases'].str.lower().apply(get_urgency)
    
    print(f"\n  Urgency Level Distribution:")
    urgency_counts = df['urgency_level'].value_counts().sort_index()
    for level, count in urgency_counts.items():
        pct = count / len(df) * 100
        print(f"    Level {level}: {count:,} ({pct:.1f}%)")
    
    return df


def remove_duplicates(df, feature_cols):
    """Remove duplicate rows to prevent data leakage"""
    print("\n" + "="*60)
    print("PHASE 1.5: DUPLICATE REMOVAL (Anti-Leak)")
    print("="*60)
    
    original_len = len(df)
    
    # Remove exact duplicate rows (same features AND label)
    df_unique = df.drop_duplicates(subset=feature_cols + ['urgency_level'])
    
    removed = original_len - len(df_unique)
    print(f"  Original samples: {original_len:,}")
    print(f"  Removed duplicates: {removed:,} ({removed/original_len*100:.2f}%)")
    print(f"  Remaining samples: {len(df_unique):,}")
    
    return df_unique


def prepare_features(df):
    """Prepare features and remove low variance"""
    print("\n" + "="*60)
    print("PHASE 2: FEATURE PREPARATION")
    print("="*60)
    
    feature_cols = [col for col in df.columns if col not in ['diseases', 'urgency_level']]
    X = df[feature_cols]
    y = df['urgency_level']
    
    # Remove low variance features
    selector = VarianceThreshold(threshold=0.01)
    X_selected = selector.fit_transform(X)
    selected_features = [col for col, selected in zip(feature_cols, selector.get_support()) if selected]
    
    print(f"  Features before: {len(feature_cols)}")
    print(f"  Features after variance filter: {len(selected_features)}")
    
    return pd.DataFrame(X_selected, columns=selected_features, index=df.index), y, selected_features


def split_data_strict(df, X, y, feature_names):
    """Split data with STRICT anti-leak measures"""
    print("\n" + "="*60)
    print("PHASE 3: DATA SPLITTING (Strict Anti-Leak)")
    print("="*60)
    
    # Create hash of each row for uniqueness check
    row_hashes = pd.util.hash_pandas_object(X)
    
    # Keep only first occurrence of each unique row
    unique_mask = ~row_hashes.duplicated()
    X_unique = X[unique_mask].copy()
    y_unique = y[unique_mask].copy()
    
    print(f"  After hash-based dedup: {len(X_unique):,} unique samples")
    
    # Split BEFORE any transforms
    X_temp, X_test, y_temp, y_test = train_test_split(
        X_unique, y_unique, test_size=0.15, stratify=y_unique, random_state=42
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, stratify=y_temp, random_state=42
    )
    
    # Verify NO overlap
    train_hashes = set(pd.util.hash_pandas_object(X_train))
    test_hashes = set(pd.util.hash_pandas_object(X_test))
    val_hashes = set(pd.util.hash_pandas_object(X_val))
    
    train_test_overlap = len(train_hashes.intersection(test_hashes))
    train_val_overlap = len(train_hashes.intersection(val_hashes))
    
    print(f"\n  Train: {len(X_train):,} samples")
    print(f"  Validation: {len(X_val):,} samples")
    print(f"  Test: {len(X_test):,} samples")
    print(f"\n  Train-Test overlap: {train_test_overlap}")
    print(f"  Train-Val overlap: {train_val_overlap}")
    
    if train_test_overlap > 0 or train_val_overlap > 0:
        print("  WARNING: Overlap detected!")
    else:
        print("  OK: No overlap - strict separation confirmed")
    
    return X_train.values, X_val.values, X_test.values, y_train.values, y_val.values, y_test.values


def generate_synthetic_no_noise(X_train, y_train, synthetic_ratio=0.25):
    """Generate balanced synthetic data WITHOUT noise (for proper overfit measurement)"""
    print("\n" + "="*60)
    print("PHASE 4: SYNTHETIC DATA GENERATION (No Noise)")
    print("="*60)
    
    n_real = len(X_train)
    n_synthetic = int(n_real * synthetic_ratio / (1 - synthetic_ratio))
    unique_classes = np.unique(y_train)
    samples_per_class = n_synthetic // len(unique_classes)
    
    # Convert to DataFrame
    train_df = pd.DataFrame(X_train)
    train_df['urgency_level'] = y_train
    
    synthetic_dfs = []
    for urgency in unique_classes:
        class_data = train_df[train_df['urgency_level'] == urgency]
        
        if len(class_data) > 0:
            # Resample with replacement - NO NOISE ADDED
            n_samples = min(samples_per_class, len(class_data) * 2)
            resampled = resample(class_data, n_samples=n_samples, random_state=42)
            synthetic_dfs.append(resampled)
    
    synthetic_df = pd.concat(synthetic_dfs, ignore_index=True)
    
    # Combine real + synthetic
    combined_df = pd.concat([train_df, synthetic_df], ignore_index=True)
    
    # Shuffle
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    X_aug = combined_df.drop(columns=['urgency_level']).values
    y_aug = combined_df['urgency_level'].values
    
    print(f"  Real samples: {n_real:,}")
    print(f"  Synthetic samples: {len(synthetic_df):,}")
    print(f"  Total augmented: {len(X_aug):,}")
    print(f"\n  Augmented class distribution:")
    for level in sorted(np.unique(y_aug)):
        count = (y_aug == level).sum()
        print(f"    Level {level}: {count:,}")
    
    return X_aug, y_aug


def scale_data(X_train, X_val, X_test, X_train_real=None):
    """Scale data - fit only on training. Also scale real train if provided."""
    print("\n" + "="*60)
    print("PHASE 5: SCALING (Anti-Leak)")
    print("="*60)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Scale real training data (for proper overfit calculation)
    X_train_real_scaled = None
    if X_train_real is not None:
        X_train_real_scaled = scaler.transform(X_train_real)
        print("  Scaler fitted on augmented training data")
        print("  Real training data also scaled for overfit calculation")
    else:
        print("  Scaler fitted on training data only")
    
    return X_train_scaled, X_val_scaled, X_test_scaled, scaler, X_train_real_scaled


def train_model(X_train_aug, y_train_aug, X_val, y_val, X_train_real, y_train_real):
    """
    Train XGBoost multi-class classifier
    
    IMPORTANT: Overfit gap is calculated using REAL training data (X_train_real),
    not the augmented/synthetic data (X_train_aug).
    """
    print("\n" + "="*60)
    print("PHASE 6: MODEL TRAINING (Multi-Class)")
    print("="*60)
    
    # Map labels to 0-indexed
    all_labels = np.concatenate([y_train_aug, y_val, y_train_real])
    unique_labels = sorted(np.unique(all_labels))
    label_map = {label: idx for idx, label in enumerate(unique_labels)}
    
    y_train_adj = np.array([label_map[y] for y in y_train_aug])
    y_val_adj = np.array([label_map[y] for y in y_val])
    y_train_real_adj = np.array([label_map[y] for y in y_train_real])
    
    n_classes = len(unique_labels)
    print(f"\n  Classes: {unique_labels} (n={n_classes})")
    
    # Calculate class weights for imbalance
    class_counts = np.bincount(y_train_adj)
    total = len(y_train_adj)
    class_weights = {i: total / (n_classes * count) for i, count in enumerate(class_counts)}
    sample_weights = np.array([class_weights[y] for y in y_train_adj])
    
    print(f"  Class weights: {[f'{w:.2f}' for w in class_weights.values()]}")
    
    # XGBoost parameters
    model = XGBClassifier(
        objective='multi:softprob',
        num_class=n_classes,
        max_depth=6,
        min_child_weight=5,
        reg_alpha=0.2,
        reg_lambda=2.0,
        subsample=0.8,
        colsample_bytree=0.8,
        learning_rate=0.05,
        n_estimators=300,
        tree_method='hist',
        random_state=42,
        n_jobs=-1,
        eval_metric='mlogloss',
        early_stopping_rounds=30,
    )
    
    # Cross-validation on REAL data (not augmented)
    print("\n  [1] 5-Fold Stratified CV on REAL data...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    cv_model = XGBClassifier(
        objective='multi:softprob', num_class=n_classes,
        max_depth=6, min_child_weight=5, reg_alpha=0.2, reg_lambda=2.0,
        subsample=0.8, colsample_bytree=0.8, learning_rate=0.05,
        n_estimators=200, random_state=42, n_jobs=-1, verbosity=0
    )
    cv_scores = cross_val_score(cv_model, X_train_real, y_train_real_adj, cv=cv, scoring='f1_macro', n_jobs=-1)
    print(f"      CV F1 Scores: {cv_scores.round(4)}")
    print(f"      CV Mean F1: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    # Train on augmented data with early stopping
    print("\n  [2] Training on AUGMENTED data with Early Stopping...")
    eval_set = [(X_val, y_val_adj)]
    
    model.fit(
        X_train_aug, y_train_adj,
        sample_weight=sample_weights,
        eval_set=eval_set,
        verbose=50
    )
    
    best_iteration = model.best_iteration if hasattr(model, 'best_iteration') and model.best_iteration else model.n_estimators
    print(f"      Best iteration: {best_iteration}")
    
    # Evaluate on REAL training data (not augmented) for proper overfit calculation
    print("\n  [3] Overfit Calculation (REAL train data vs validation):")
    
    y_train_real_pred = model.predict(X_train_real)
    y_val_pred = model.predict(X_val)
    
    train_f1_real = f1_score(y_train_real_adj, y_train_real_pred, average='macro')
    val_f1 = f1_score(y_val_adj, y_val_pred, average='macro')
    overfit_gap = train_f1_real - val_f1
    
    train_acc_real = accuracy_score(y_train_real_adj, y_train_real_pred)
    val_acc = accuracy_score(y_val_adj, y_val_pred)
    
    print(f"      Train F1 (REAL data): {train_f1_real:.4f}")
    print(f"      Validation F1: {val_f1:.4f}")
    print(f"      Overfit Gap: {overfit_gap:.4f}")
    print(f"      Train Accuracy (REAL): {train_acc_real:.4f}")
    print(f"      Validation Accuracy: {val_acc:.4f}")
    
    if overfit_gap > 0.10:
        print(f"      WARNING: Significant overfit! (gap > 0.10)")
    elif overfit_gap > 0.05:
        print(f"      CAUTION: Mild overfit (gap > 0.05)")
    elif overfit_gap < 0:
        print(f"      WARNING: Negative gap detected! Check for issues.")
    else:
        print(f"      OK: Healthy overfit gap (0 < gap < 0.05)")
    
    return model, label_map, {
        'cv_scores': cv_scores.tolist(),
        'cv_mean_f1': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'train_f1_real': float(train_f1_real),
        'train_acc_real': float(train_acc_real),
        'val_f1': float(val_f1),
        'val_acc': float(val_acc),
        'overfit_gap': float(overfit_gap),
        'best_iteration': int(best_iteration),
        'n_classes': n_classes,
    }


def evaluate_test(model, X_test, y_test, label_map):
    """Final evaluation on test set"""
    print("\n" + "="*60)
    print("PHASE 7: FINAL TEST EVALUATION")
    print("="*60)
    
    y_test_adj = np.array([label_map[y] for y in y_test])
    y_pred = model.predict(X_test)
    
    test_f1 = f1_score(y_test_adj, y_pred, average='macro')
    test_f1_weighted = f1_score(y_test_adj, y_pred, average='weighted')
    test_acc = accuracy_score(y_test_adj, y_pred)
    
    print(f"\n  Test F1 Score (Macro): {test_f1:.4f}")
    print(f"  Test F1 Score (Weighted): {test_f1_weighted:.4f}")
    print(f"  Test Accuracy: {test_acc:.4f}")
    
    # Per-class metrics
    print("\n  Per-Class Metrics:")
    reverse_map = {v: k for k, v in label_map.items()}
    for idx in sorted(label_map.values()):
        mask = y_test_adj == idx
        if mask.sum() > 0:
            class_recall = recall_score(y_test_adj[mask], y_pred[mask], average='micro')
            print(f"      Urgency {reverse_map[idx]}: Recall={class_recall:.4f} (n={mask.sum()})")
    
    print("\n  Classification Report:")
    target_names = [f"Urgency {reverse_map[i]}" for i in sorted(label_map.values())]
    print(classification_report(y_test_adj, y_pred, target_names=target_names, zero_division=0))
    
    return {
        'test_f1_macro': float(test_f1),
        'test_f1_weighted': float(test_f1_weighted),
        'test_accuracy': float(test_acc),
    }


def save_model(model, scaler, feature_names, label_map, metrics, output_dir):
    """Save model and artifacts"""
    print("\n" + "="*60)
    print("PHASE 8: SAVING MODEL")
    print("="*60)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = output_dir / 'golden_hour_model.pkl'
    joblib.dump(model, model_path)
    model_size_mb = model_path.stat().st_size / (1024 * 1024)
    print(f"  Model saved: {model_path}")
    print(f"  Model size: {model_size_mb:.2f} MB")
    
    if model_size_mb > 100:
        print(f"  WARNING: Model exceeds 100MB limit!")
    else:
        print(f"  OK: Model size within limit")
    
    # Save scaler
    scaler_path = output_dir / 'golden_hour_scaler.pkl'
    joblib.dump(scaler, scaler_path)
    print(f"  Scaler saved: {scaler_path}")
    
    # Save features and label map
    artifacts_path = output_dir / 'golden_hour_artifacts.pkl'
    reverse_map = {v: k for k, v in label_map.items()}
    urgency_descriptions = {
        5: 'Critical - Immediate',
        4: 'Emergent - Hours',
        3: 'Urgent - 24 hours',
        2: 'Standard - 2-3 days',
        1: 'Elective - Scheduled'
    }
    joblib.dump({
        'feature_names': feature_names,
        'label_map': label_map,
        'reverse_map': reverse_map,
        'urgency_descriptions': urgency_descriptions,
        'n_classes': len(label_map),
    }, artifacts_path)
    print(f"  Artifacts saved: {artifacts_path}")
    
    # Save metrics
    metrics['model_size_mb'] = model_size_mb
    metrics['timestamp'] = datetime.now().isoformat()
    metrics['overfit_calculation'] = 'real_train_data_vs_validation'
    metrics_path = output_dir / 'golden_hour_metadata.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics saved: {metrics_path}")
    
    return model_size_mb


def main():
    """Main training pipeline with correct overfit calculation"""
    print("\n" + "="*70)
    print("   GOLDEN HOUR MODEL - MULTI-CLASS (FIXED OVERFIT CALCULATION)")
    print("="*70 + "\n")
    
    # Determine paths
    script_dir = Path(__file__).parent
    data_path = script_dir / 'cleaned_dataset.csv'
    output_dir = script_dir / 'golden_hour_model' / 'models'
    
    if not data_path.exists():
        data_path = Path('cleaned_dataset.csv')
    if not data_path.exists():
        data_path = Path('c:/Users/muham/OneDrive/Masaüstü/AdvanceUp2/cleaned_dataset.csv')
    
    print(f"Data path: {data_path}")
    print(f"Output dir: {output_dir}")
    
    # 1. Load Data
    df = load_and_prepare_data(data_path)
    
    # 2. Prepare Features (before dedup to get feature cols)
    feature_cols = [col for col in df.columns if col not in ['diseases', 'urgency_level']]
    
    # 2.5 Remove duplicates
    df = remove_duplicates(df, feature_cols)
    
    # 3. Prepare Features
    X, y, feature_names = prepare_features(df)
    
    # 4. Split (Strict Anti-Leak)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data_strict(df, X, y, feature_names)
    
    # KEEP REAL TRAINING DATA for proper overfit calculation
    X_train_real = X_train.copy()
    y_train_real = y_train.copy()
    
    # 5. Generate Synthetic (NO NOISE - proper augmentation)
    X_train_aug, y_train_aug = generate_synthetic_no_noise(X_train, y_train, synthetic_ratio=0.25)
    
    # 6. Scale (Anti-Leak) - also scale real training data
    X_train_scaled, X_val_scaled, X_test_scaled, scaler, X_train_real_scaled = scale_data(
        X_train_aug, X_val, X_test, X_train_real
    )
    
    # 7. Train - pass both augmented data AND real data
    model, label_map, train_metrics = train_model(
        X_train_scaled, y_train_aug, 
        X_val_scaled, y_val,
        X_train_real_scaled, y_train_real
    )
    
    # 8. Test
    test_metrics = evaluate_test(model, X_test_scaled, y_test, label_map)
    
    # 9. Save
    all_metrics = {**train_metrics, **test_metrics}
    save_model(model, scaler, feature_names, label_map, all_metrics, output_dir)
    
    print("\n" + "="*70)
    print("   TRAINING COMPLETE!")
    print("="*70)
    print(f"\n  Train F1 (Real Data): {train_metrics['train_f1_real']:.4f}")
    print(f"  Validation F1: {train_metrics['val_f1']:.4f}")
    print(f"  Test F1 (Macro): {test_metrics['test_f1_macro']:.4f}")
    print(f"  Test Accuracy: {test_metrics['test_accuracy']:.4f}")
    print(f"  Overfit Gap: {train_metrics['overfit_gap']:.4f}")
    print(f"  Model saved to: {output_dir / 'golden_hour_model.pkl'}")
    
    # Validation
    gap = train_metrics['overfit_gap']
    if gap < 0:
        print("\n  ERROR: Negative overfit gap - something is wrong!")
    elif gap > 0.15:
        print("\n  WARNING: High overfit gap (>0.15) - consider more regularization")
    elif gap > 0.05:
        print("\n  OK: Mild overfit - acceptable for production")
    else:
        print("\n  EXCELLENT: Low overfit gap - well generalized model")
    
    return model, all_metrics


if __name__ == "__main__":
    main()
