"""
EKG Model Training - 1D CNN Classifier
Train 1D CNN model for arrhythmia classification using raw signals
"""

import numpy as np
import json
import os
from datetime import datetime

# Check if TensorFlow is available
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, callbacks
    TF_AVAILABLE = True
except ImportError:
    print("⚠️ TensorFlow not installed. Install with: pip install tensorflow")
    TF_AVAILABLE = False
    exit(1)

from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, top_k_accuracy_score
)

print("=" * 80)
print("🧠 EKG 1D-CNN MODEL TRAINING")
print("=" * 80)

# ==========================================
# CONFIGURATION
# ==========================================

MODEL_DIR = r"c:\Users\muham\OneDrive\Masaüstü\AdvanceUpHackhathon\ai-service\models\ekg"
os.makedirs(MODEL_DIR, exist_ok=True)

# ==========================================
# 1. LOAD PREPROCESSED DATA
# ==========================================

print("\n📂 1. LOADING DATA")

data = np.load(os.path.join(MODEL_DIR, 'ekg_data.npz'))
X_train = data['X_train']
X_val = data['X_val']
X_test = data['X_test']
y_train = data['y_train']
y_val = data['y_val']
y_test = data['y_test']

print(f"  Train: {X_train.shape}")
print(f"  Val:   {X_val.shape}")
print(f"  Test:  {X_test.shape}")

# Reshape for CNN (batch, length, channels)
if len(X_train.shape) == 2:
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_val = X_val.reshape(X_val.shape[0], X_val.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

signal_length = X_train.shape[1]

# Load label mapping
with open(os.path.join(MODEL_DIR, 'label_map.json'), 'r') as f:
    label_map = json.load(f)

num_classes = len(label_map)
print(f"\n  Classes: {num_classes}")
print(f"  Signal length: {signal_length}")

# Class weights
unique, counts = np.unique(y_train, return_counts=True)
class_weights = dict(zip(unique, len(y_train) / (num_classes * counts)))
print(f"\n  Class weights: {class_weights}")

# ==========================================
# 2. BUILD 1D CNN MODEL
# ==========================================

print("\n🔧 2. BUILDING 1D-CNN ARCHITECTURE")

def build_1d_cnn(input_shape, num_classes):
    """Build 1D CNN for EKG classification"""
    model = models.Sequential([
        # Conv Block 1
        layers.Conv1D(64, kernel_size=7, activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.2),
        
        # Conv Block 2
        layers.Conv1D(128, kernel_size=5, activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.2),
        
        # Conv Block 3
        layers.Conv1D(256, kernel_size=3, activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.3),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        
        # Output
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

model = build_1d_cnn((signal_length, 1), num_classes)

# Compile
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(f"\n  Model architecture:")
model.summary()

# ==========================================
# 3. TRAIN MODEL
# ==========================================

print("\n🚀 3. TRAINING CNN")

# Callbacks
checkpoint_cb = callbacks.ModelCheckpoint(
    os.path.join(MODEL_DIR, 'ekg_cnn_best.h5'),
    save_best_only=True,
    monitor='val_accuracy',
    mode='max'
)

early_stop_cb = callbacks.EarlyStopping(
    monitor='val_loss',
    patience=20,
    restore_best_weights=True
)

reduce_lr_cb = callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=10,
    min_lr=1e-6
)

# Train
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=32,
    class_weight=class_weights,
    callbacks=[checkpoint_cb, early_stop_cb, reduce_lr_cb],
    verbose=1
)

print(f"\n  ✅ Training complete!")

# ==========================================
# 4. EVALUATION
# ==========================================

print("\n📊 4. MODEL EVALUATION")

# Predictions
y_pred_proba = model.predict(X_test, verbose=0)
y_pred = np.argmax(y_pred_proba, axis=1)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
top3_acc = top_k_accuracy_score(y_test, y_pred_proba, k=3)

print(f"\n  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  Top-3 Accuracy: {top3_acc:.4f} ({top3_acc*100:.2f}%)")

# Classification report
print(f"\n  Classification Report:")
class_names = [label_map[str(i)] for i in range(num_classes)]
print(classification_report(y_test, y_pred, target_names=class_names))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\n  Confusion Matrix:")
print(cm)

# ==========================================
# 5. SAVE MODEL
# ==========================================

print("\n💾 5. SAVING MODEL")

# Save model
model.save(os.path.join(MODEL_DIR, 'ekg_cnn_classifier.h5'))
print(f"  ✅ Saved: ekg_cnn_classifier.h5")

# Save metrics
metrics = {
    'timestamp': datetime.now().isoformat(),
    'model_type': '1D-CNN',
    'architecture': 'Conv1D-3blocks + Dense',
    'accuracy': float(accuracy),
    'top3_accuracy': float(top3_acc),
    'signal_length': int(signal_length),
    'num_classes': int(num_classes),
    'train_samples': int(len(X_train)),
    'val_samples': int(len(X_val)),
    'test_samples': int(len(X_test)),
    'epochs_trained': len(history.history['loss']),
    'final_train_acc': float(history.history['accuracy'][-1]),
    'final_val_acc': float(history.history['val_accuracy'][-1])
}

with open(os.path.join(MODEL_DIR, 'ekg_cnn_metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"  ✅ Saved: ekg_cnn_metrics.json")

# Save training history
history_dict = {
    'loss': [float(x) for x in history.history['loss']],
    'accuracy': [float(x) for x in history.history['accuracy']],
    'val_loss': [float(x) for x in history.history['val_loss']],
    'val_accuracy': [float(x) for x in history.history['val_accuracy']]
}

with open(os.path.join(MODEL_DIR, 'ekg_cnn_history.json'), 'w') as f:
    json.dump(history_dict, f, indent=2)
print(f"  ✅ Saved: ekg_cnn_history.json")

print("\n" + "=" * 80)
print("✅ CNN TRAINING COMPLETE")
print("=" * 80)
print(f"\nModel ready for deployment!")
print(f"  Accuracy: {accuracy*100:.2f}%")
print(f"  Top-3: {top3_acc*100:.2f}%")
print(f"\nNext steps:")
print(f"  1. Update ekg_service.py to use trained model")
print(f"  2. Test with real EKG data")
print(f"  3. Deploy to production")
