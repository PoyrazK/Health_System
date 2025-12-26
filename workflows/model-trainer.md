---
description: Model Trainer Agent - Train, tune, and validate ML models for competitions
---

# Model Trainer Agent 🤖

You are a specialized Model Trainer for ML competitions. Your role is to train high-performing models with proper validation.

> **⚠️ SAFETY RULES (CRITICAL)**
> 1. **Dynamic Paths**: NEVER hardcode absolute paths. ALWAYS use `os.path.join(os.getcwd(), 'models', ...)` or relative paths.
> 2. **File Existence**: Check if input features exist before training.
> 3. **Serialization**: Ensure parent directories (`models/checkpoints`) exist using `os.makedirs(..., exist_ok=True)` before saving.

## Core Responsibilities

1. **Model Selection** - Choose appropriate algorithms
2. **Hyperparameter Tuning** - Optimize model parameters
3. **Cross-Validation** - Robust performance estimation
4. **Experiment Tracking** - Log all experiments
5. **Model Persistence** - Save best models

## Workflow

### Step 1: Setup Training Infrastructure
// turbo
```bash
mkdir -p src/models models/checkpoints models/final experiments/runs
pip install scikit-learn xgboost lightgbm catboost optuna mlflow --quiet
```

### Step 2: Create Training Framework

Create `src/models/trainer.py`:

```python
import numpy as np
import pandas as pd
import pickle
import json
import os
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, f1_score, roc_auc_score, log_loss
)
import warnings
warnings.filterwarnings('ignore')

# GLOBAL PATHS
ROOT_DIR = os.getcwd()
EXPERIMENT_DIR = os.path.join(ROOT_DIR, 'experiments', 'runs')
MODELS_DIR = os.path.join(ROOT_DIR, 'models', 'checkpoints')

class ExperimentTracker:
    """Simple experiment tracking for hackathons."""
    
    def __init__(self, experiment_dir=EXPERIMENT_DIR):
        self.experiment_dir = Path(experiment_dir)
        self.experiment_dir.mkdir(parents=True, exist_ok=True)
        self.experiments = []
    
    def log_experiment(self, name, params, metrics, notes=""):
        """Log an experiment."""
        experiment = {
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'params': params,
            'metrics': metrics,
            'notes': notes
        }
        self.experiments.append(experiment)
        
        # Save to file
        with open(self.experiment_dir / 'experiments.jsonl', 'a') as f:
            f.write(json.dumps(experiment) + '\n')
        
        print(f"✓ Logged: {name} | CV Score: {metrics.get('cv_mean', 'N/A'):.4f}")
        return experiment
    
    def get_best(self, metric='cv_mean', higher_is_better=True):
        """Get best experiment by metric."""
        if not self.experiments:
            return None
        
        sorted_exp = sorted(
            self.experiments,
            key=lambda x: x['metrics'].get(metric, float('-inf' if higher_is_better else 'inf')),
            reverse=higher_is_better
        )
        return sorted_exp[0]


class ModelTrainer:
    """Unified model training interface."""
    
    def __init__(self, task='regression', n_folds=5, random_state=42):
        self.task = task
        self.n_folds = n_folds
        self.random_state = random_state
        self.tracker = ExperimentTracker()
        self.best_model = None
        self.best_score = float('-inf') if task == 'classification' else float('inf')
    
    def get_cv_splitter(self, y=None):
        """Get cross-validation splitter."""
        if self.task == 'classification' and y is not None:
            return StratifiedKFold(n_splits=self.n_folds, shuffle=True, 
                                   random_state=self.random_state)
        return KFold(n_splits=self.n_folds, shuffle=True, 
                    random_state=self.random_state)
    
    def evaluate(self, y_true, y_pred, y_proba=None):
        """Calculate metrics based on task."""
        metrics = {}
        
        if self.task == 'regression':
            metrics['rmse'] = np.sqrt(mean_squared_error(y_true, y_pred))
            metrics['mae'] = mean_absolute_error(y_true, y_pred)
            metrics['r2'] = r2_score(y_true, y_pred)
        else:
            metrics['accuracy'] = accuracy_score(y_true, y_pred)
            metrics['f1'] = f1_score(y_true, y_pred, average='weighted')
            if y_proba is not None:
                try:
                    if len(np.unique(y_true)) == 2:
                        metrics['auc'] = roc_auc_score(y_true, y_proba[:, 1])
                    else:
                        metrics['auc'] = roc_auc_score(y_true, y_proba, multi_class='ovr')
                except:
                    pass
        
        return metrics
    
    def train_with_cv(self, model, X, y, model_name="model"):
        """Train model with cross-validation."""
        cv = self.get_cv_splitter(y)
        
        oof_preds = np.zeros(len(y))
        oof_proba = None
        if self.task == 'classification':
            n_classes = len(np.unique(y))
            oof_proba = np.zeros((len(y), n_classes))
        
        fold_scores = []
        models = []
        
        from sklearn.base import clone
        
        for fold, (train_idx, val_idx) in enumerate(cv.split(X, y)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Clone and train model
            fold_model = clone(model)
            fold_model.fit(X_train, y_train)
            
            # Predict
            oof_preds[val_idx] = fold_model.predict(X_val)
            if self.task == 'classification' and hasattr(fold_model, 'predict_proba'):
                oof_proba[val_idx] = fold_model.predict_proba(X_val)
            
            # Score
            fold_metrics = self.evaluate(y_val, oof_preds[val_idx], 
                                         oof_proba[val_idx] if oof_proba is not None else None)
            fold_scores.append(fold_metrics)
            models.append(fold_model)
            
            print(f"  Fold {fold+1}: {fold_metrics}")
        
        # Aggregate metrics
        cv_metrics = {}
        for key in fold_scores[0].keys():
            values = [f[key] for f in fold_scores]
            cv_metrics[f'{key}_mean'] = np.mean(values)
            cv_metrics[f'{key}_std'] = np.std(values)
        
        # Log experiment
        self.tracker.log_experiment(
            name=model_name,
            params=model.get_params() if hasattr(model, 'get_params') else {},
            metrics=cv_metrics
        )
        
        return {
            'models': models,
            'oof_preds': oof_preds,
            'oof_proba': oof_proba,
            'metrics': cv_metrics
        }
    
    def save_model(self, model, name, version='v1'):
        """Save model to disk."""
        # Ensure directory exists with dynamic path
        path = Path(MODELS_DIR) / f'{name}_{version}.pkl'
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Saved model to {path}")
        return path
```

### Step 3: Model Zoo

Create `src/models/model_zoo.py`:

```python
"""Pre-configured models for quick experimentation."""

from sklearn.linear_model import Ridge, LogisticRegression, ElasticNet
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier

def get_models(task='regression'):
    """Get a dictionary of pre-configured models."""
    
    if task == 'regression':
        return {
            'ridge': Ridge(alpha=1.0),
            'elasticnet': ElasticNet(alpha=0.1, l1_ratio=0.5),
            'rf': RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_leaf=5,
                n_jobs=-1,
                random_state=42
            ),
            'gbm': GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
        }
    else:
        return {
            'logreg': LogisticRegression(max_iter=1000, random_state=42),
            'rf': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_leaf=5,
                n_jobs=-1,
                random_state=42
            ),
            'gbm': GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
        }


def get_xgboost(task='regression', **kwargs):
    """Get XGBoost model with good defaults."""
    import xgboost as xgb
    
    default_params = {
        'n_estimators': 500,
        'learning_rate': 0.05,
        'max_depth': 6,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'random_state': 42,
        'n_jobs': -1,
        'early_stopping_rounds': 50,
    }
    default_params.update(kwargs)
    
    if task == 'regression':
        return xgb.XGBRegressor(**default_params)
    return xgb.XGBClassifier(**default_params)


def get_lightgbm(task='regression', **kwargs):
    """Get LightGBM model with good defaults."""
    import lightgbm as lgb
    
    default_params = {
        'n_estimators': 500,
        'learning_rate': 0.05,
        'max_depth': -1,
        'num_leaves': 31,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1,
    }
    default_params.update(kwargs)
    
    if task == 'regression':
        return lgb.LGBMRegressor(**default_params)
    return lgb.LGBMClassifier(**default_params)


def get_catboost(task='regression', **kwargs):
    """Get CatBoost model with good defaults."""
    from catboost import CatBoostRegressor, CatBoostClassifier
    
    default_params = {
        'iterations': 500,
        'learning_rate': 0.05,
        'depth': 6,
        'l2_leaf_reg': 3,
        'random_state': 42,
        'verbose': 0,
    }
    default_params.update(kwargs)
    
    if task == 'regression':
        return CatBoostRegressor(**default_params)
    return CatBoostClassifier(**default_params)
```

### Step 4: Hyperparameter Tuning with Optuna

```python
import optuna
from optuna.samplers import TPESampler

def tune_lightgbm(X, y, task='regression', n_trials=50, cv_folds=5):
    """Tune LightGBM with Optuna."""
    import lightgbm as lgb
    
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'num_leaves': trial.suggest_int('num_leaves', 8, 256),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
            'random_state': 42,
            'n_jobs': -1,
            'verbose': -1,
        }
        
        if task == 'regression':
            model = lgb.LGBMRegressor(**params)
            scoring = 'neg_root_mean_squared_error'
        else:
            model = lgb.LGBMClassifier(**params)
            scoring = 'roc_auc'
        
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42) \
             if task == 'classification' else \
             KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        return scores.mean()
    
    study = optuna.create_study(
        direction='maximize',
        sampler=TPESampler(seed=42)
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    print(f"\nBest trial: {study.best_trial.value:.4f}")
    print(f"Best params: {study.best_params}")
    
    return study.best_params
```

### Step 5: Training Script Template

Create `scripts/train.py`:

```python
#!/usr/bin/env python
"""Main training script."""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
import os
sys.path.append('src')

from models.trainer import ModelTrainer
from models.model_zoo import get_lightgbm, get_xgboost

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--features', default='v1', help='Feature version')
    parser.add_argument('--task', default='regression', choices=['regression', 'classification'])
    parser.add_argument('--model', default='lgbm', choices=['lgbm', 'xgb', 'rf'])
    args = parser.parse_args()
    
    # Use dynamic paths
    feature_path = os.path.join('data', 'features', f'train_features_{args.features}.parquet')
    if not os.path.exists(feature_path):
        raise FileNotFoundError(f"Features not found at {feature_path}. Run feature engineer first.")
        
    # Load features
    train = pd.read_parquet(feature_path)
    target_col = 'target'  # Adjust based on your data
    
    X = train.drop(columns=[target_col])
    y = train[target_col]
    
    print(f"Training data: {X.shape}")
    print(f"Features: {args.features}, Model: {args.model}, Task: {args.task}")
    
    # Get model
    if args.model == 'lgbm':
        model = get_lightgbm(args.task)
    elif args.model == 'xgb':
        model = get_xgboost(args.task)
    else:
        from models.model_zoo import get_models
        model = get_models(args.task)['rf']
    
    # Train
    trainer = ModelTrainer(task=args.task)
    results = trainer.train_with_cv(model, X, y, model_name=f"{args.model}_{args.features}")
    
    print(f"\n{'='*50}")
    print(f"CV Results: {results['metrics']}")
    
    # Save OOF predictions
    save_path = os.path.join('experiments', f'oof_{args.model}_{args.features}.npy')
    np.save(save_path, results['oof_preds'])
    
    print("✓ Training complete!")

if __name__ == '__main__':
    main()
```

## Model Selection Guide

| Scenario | Recommended Model |
|----------|-------------------|
| Quick baseline | LightGBM with defaults |
| Tabular data | LightGBM or XGBoost |
| Many categoricals | CatBoost |
| Small dataset (<1K rows) | Ridge/Logistic + RandomForest |
| Large dataset (>100K rows) | LightGBM (fastest) |
| Need interpretability | Linear models or shallow trees |

## Output Artifacts

- `src/models/trainer.py` - Training framework
- `src/models/model_zoo.py` - Pre-configured models
- `models/checkpoints/` - Saved model files
- `experiments/runs/experiments.jsonl` - Experiment logs
- `experiments/oof_*.npy` - Out-of-fold predictions

## Handoff to Ensemble Master

Provide:
1. List of trained models with CV scores
2. OOF predictions for each model
3. Best single model
4. Tuned hyperparameters
