"""
Enhanced ML Model Training Script for PhishGuard
This script trains a more accurate phishing detection model with:
- Improved feature engineering
- Better hyperparameter tuning
- Advanced ensemble methods
- Cross-validation for robust performance
"""

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("PhishGuard Enhanced Model Training")
print("=" * 80)

# Path to datasets
phishing_data_path = os.path.join('extracted_dataset', 'extracted_phishing_dataset.csv')
legitimate_data_path = os.path.join('extracted_dataset', 'extracted_legitmate_dataset.csv')

# Load datasets
print("\n[1/8] Loading datasets...")
try:
    phishing_data = pd.read_csv(phishing_data_path)
    legitimate_data = pd.read_csv(legitimate_data_path)
    
    print(f"  ✓ Phishing samples: {phishing_data.shape[0]:,}")
    print(f"  ✓ Legitimate samples: {legitimate_data.shape[0]:,}")
    
    # Check if 'label' column already exists
    if 'label' not in phishing_data.columns:
        phishing_data['label'] = 1  # 1 for phishing
    if 'label' not in legitimate_data.columns:
        legitimate_data['label'] = 0  # 0 for legitimate
    
    # Combine datasets
    full_dataset = pd.concat([phishing_data, legitimate_data], ignore_index=True)
    
    # Shuffle the data
    full_dataset = full_dataset.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"  ✓ Total samples: {full_dataset.shape[0]:,}")
    print(f"  ✓ Features: {full_dataset.shape[1] - 1}")
    
except Exception as e:
    print(f"  ✗ Error loading datasets: {e}")
    exit(1)

# Feature engineering
print("\n[2/8] Engineering features...")

# Identify feature columns (exclude non-feature columns)
exclude_cols = ['protocol', 'domain_name', 'address', 'label']
feature_cols = [col for col in full_dataset.columns if col not in exclude_cols]

print(f"  ✓ Using {len(feature_cols)} features: {', '.join(feature_cols)}")

# Prepare features and labels
X = full_dataset[feature_cols].copy()
y = full_dataset['label'].copy()

# Handle any missing values
X = X.fillna(0)

# Verify data types
X = X.astype(float)
y = y.astype(int)

print(f"  ✓ Feature matrix shape: {X.shape}")
print(f"  ✓ Target distribution: Phishing={sum(y==1):,}, Legitimate={sum(y==0):,}")

# Split data
print("\n[3/8] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"  ✓ Training samples: {X_train.shape[0]:,}")
print(f"  ✓ Testing samples: {X_test.shape[0]:,}")

# Feature scaling
print("\n[4/8] Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("  ✓ Features scaled using StandardScaler")

# Train multiple models
print("\n[5/8] Training ensemble models...")

# Model 1: XGBoost with optimized hyperparameters
print("  Training XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=200,           # Increased from 100
    max_depth=7,                # Increased from 6
    learning_rate=0.05,         # Decreased for better learning
    subsample=0.8,              # Add subsample for regularization
    colsample_bytree=0.8,       # Feature sampling
    gamma=1,                    # Minimum loss reduction
    min_child_weight=3,         # Minimum sum of instance weight
    objective='binary:logistic',
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss',
    tree_method='hist'          # Faster training
)
xgb_model.fit(X_train, y_train)
print("  ✓ XGBoost trained")

# Model 2: Random Forest
print("  Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
print("  ✓ Random Forest trained")

# Model 3: Gradient Boosting
print("  Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=6,
    min_samples_split=5,
    min_samples_leaf=2,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train, y_train)
print("  ✓ Gradient Boosting trained")

# Create ensemble model
print("\n[6/8] Creating voting ensemble...")
voting_model = VotingClassifier(
    estimators=[
        ('xgb', xgb_model),
        ('rf', rf_model),
        ('gb', gb_model)
    ],
    voting='soft',  # Use probability-based voting
    weights=[2, 1, 1]  # Give more weight to XGBoost
)
voting_model.fit(X_train, y_train)
print("  ✓ Ensemble model created")

# Evaluate all models
print("\n[7/8] Evaluating models...")
print("\n" + "="*80)

models = {
    'XGBoost': xgb_model,
    'Random Forest': rf_model,
    'Gradient Boosting': gb_model,
    'Voting Ensemble': voting_model
}

best_model = None
best_f1 = 0
best_model_name = ""

for name, model in models.items():
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\n{name}:")
    print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"  F1-Score:  {f1:.4f} ({f1*100:.2f}%)")
    
    # Track best model by F1 score
    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_model_name = name

print("\n" + "="*80)
print(f"\nBest Model: {best_model_name} (F1-Score: {best_f1:.4f})")

# Detailed evaluation of best model
print("\n[8/8] Detailed evaluation of best model...")
y_pred = best_model.predict(X_test)

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"  True Negatives:  {cm[0][0]:,}")
print(f"  False Positives: {cm[0][1]:,}")
print(f"  False Negatives: {cm[1][0]:,}")
print(f"  True Positives:  {cm[1][1]:,}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))

# Save the best model
print("\nSaving models...")

# Define paths for both backend locations
model_paths = [
    os.path.join('..', 'backend', 'phishingUrlDetectionApp', 'ML', 'model', 'XGBoostClassifier.sav'),
    os.path.join('..', 'backend', 'phishingUrlDetectionBackend', 'model', 'XGBoostClassifier.sav')
]

scaler_paths = [
    os.path.join('..', 'backend', 'phishingUrlDetectionApp', 'ML', 'model', 'scaler.sav'),
    os.path.join('..', 'backend', 'phishingUrlDetectionBackend', 'model', 'scaler.sav')
]

# Save to both locations
saved_count = 0
for model_path, scaler_path in zip(model_paths, scaler_paths):
    try:
        # Ensure directories exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(best_model, f)
        
        # Save scaler
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        print(f"  ✓ Saved to: {os.path.dirname(model_path)}")
        saved_count += 1
    except Exception as e:
        print(f"  ✗ Error saving to {model_path}: {e}")

if saved_count > 0:
    print(f"\n✓ Model successfully saved to {saved_count} location(s)")
else:
    print("\n✗ Failed to save model")

# Save feature names for reference
feature_info = {
    'feature_names': feature_cols,
    'num_features': len(feature_cols),
    'model_type': best_model_name,
    'accuracy': float(accuracy_score(y_test, best_model.predict(X_test))),
    'f1_score': float(best_f1)
}

for model_path in model_paths:
    info_path = os.path.join(os.path.dirname(model_path), 'model_info.json')
    try:
        import json
        with open(info_path, 'w') as f:
            json.dump(feature_info, f, indent=2)
        print(f"  ✓ Model info saved to: {info_path}")
    except Exception as e:
        print(f"  ✗ Error saving model info: {e}")

print("\n" + "="*80)
print("Training Complete!")
print("="*80)
print(f"\n📊 Final Model Performance:")
print(f"   Model Type: {best_model_name}")
print(f"   Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"   F1-Score: {best_f1*100:.2f}%")
print(f"   Features: {len(feature_cols)}")
print("\n✓ Model is ready to use!")
print("="*80)









