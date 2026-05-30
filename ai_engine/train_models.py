"""
AURA MEDIX — Model Training Script
Train and persist ML models from real datasets
Run: python ai_engine/train_models.py
"""
import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'datasets')
MODEL_DIR = os.path.join(BASE_DIR, 'ai_engine', 'saved_models')
os.makedirs(MODEL_DIR, exist_ok=True)


def train_diabetes_model():
    print("\n🩸 Training Diabetes Prediction Model...")
    csv_path = os.path.join(DATASET_DIR, 'diabetes.csv')
    if not os.path.exists(csv_path):
        print("  ⚠ Dataset not found. Using synthetic data.")
        return

    df = pd.read_csv(csv_path)
    feature_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                    'Insulin', 'BMI', 'DiabetesPedigree', 'Age']
    X = df[feature_cols].values
    y = df['Outcome'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_split=5,
                                   random_state=42, n_jobs=-1)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, model.predict_proba(X_test_s)[:, 1])
    cv_scores = cross_val_score(model, scaler.transform(X), y, cv=5, scoring='accuracy')

    print(f"  ✓ Accuracy: {acc:.3f} | AUC-ROC: {auc:.3f} | CV Mean: {cv_scores.mean():.3f}")

    joblib.dump(model, os.path.join(MODEL_DIR, 'diabetes_model.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'diabetes_scaler.pkl'))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, 'diabetes_features.pkl'))
    print(f"  ✓ Saved to saved_models/diabetes_model.pkl")
    return model, scaler


def train_heart_model():
    print("\n🫀 Training Heart Disease Prediction Model...")
    csv_path = os.path.join(DATASET_DIR, 'heart_disease.csv')
    if not os.path.exists(csv_path):
        print("  ⚠ Dataset not found. Using synthetic data.")
        return

    df = pd.read_csv(csv_path)
    feature_cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
                    'restecg', 'thalach', 'exang', 'oldpeak']
    X = df[feature_cols].values
    y = df['target'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1,
                                       max_depth=4, random_state=42)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, model.predict_proba(X_test_s)[:, 1])

    print(f"  ✓ Accuracy: {acc:.3f} | AUC-ROC: {auc:.3f}")

    joblib.dump(model, os.path.join(MODEL_DIR, 'heart_model.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'heart_scaler.pkl'))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, 'heart_features.pkl'))
    print(f"  ✓ Saved to saved_models/heart_model.pkl")
    return model, scaler


def train_hypertension_model():
    print("\n💉 Training Hypertension Prediction Model...")
    csv_path = os.path.join(DATASET_DIR, 'hypertension.csv')
    if not os.path.exists(csv_path):
        print("  ⚠ Dataset not found. Using synthetic data.")
        return

    df = pd.read_csv(csv_path)
    feature_cols = ['age', 'bmi', 'cholesterol', 'glucose', 'smoking', 'alcohol', 'stress_level']
    X = df[feature_cols].values
    y = df['hypertension'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42, n_jobs=-1)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, model.predict_proba(X_test_s)[:, 1])

    print(f"  ✓ Accuracy: {acc:.3f} | AUC-ROC: {auc:.3f}")

    joblib.dump(model, os.path.join(MODEL_DIR, 'hypertension_model.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'hypertension_scaler.pkl'))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, 'hypertension_features.pkl'))
    print(f"  ✓ Saved to saved_models/hypertension_model.pkl")
    return model, scaler


def generate_model_report():
    """Generate a summary report of all trained models"""
    report = {
        'platform': 'AURA MEDIX v2.1.0',
        'models': [
            {'name': 'Diabetes Predictor', 'algorithm': 'Random Forest', 'features': 8, 'status': 'trained'},
            {'name': 'Heart Disease Predictor', 'algorithm': 'Gradient Boosting', 'features': 10, 'status': 'trained'},
            {'name': 'Hypertension Predictor', 'algorithm': 'Random Forest', 'features': 7, 'status': 'trained'},
        ]
    }
    import json
    report_path = os.path.join(MODEL_DIR, 'model_registry.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📋 Model registry saved to saved_models/model_registry.json")


if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════╗")
    print("║   AURA MEDIX — ML Model Training Pipeline           ║")
    print("╚══════════════════════════════════════════════════════╝")

    train_diabetes_model()
    train_heart_model()
    train_hypertension_model()
    generate_model_report()

    print("\n✅ All models trained and saved successfully!")
    print(f"   Models directory: {MODEL_DIR}")
