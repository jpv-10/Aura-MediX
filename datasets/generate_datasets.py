"""
AURA MEDIX — Sample Dataset Generator
Generates realistic synthetic medical datasets for training and demo
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs(os.path.dirname(__file__), exist_ok=True)

# ── Diabetes Dataset ──────────────────────────────────────────────────────
def generate_diabetes(n=1000):
    data = {
        'Pregnancies':       np.random.randint(0, 18, n),
        'Glucose':           np.random.normal(120, 30, n).clip(50, 250).astype(int),
        'BloodPressure':     np.random.normal(72, 12, n).clip(40, 130).astype(int),
        'SkinThickness':     np.random.normal(23, 10, n).clip(0, 80).astype(int),
        'Insulin':           np.random.exponential(80, n).clip(0, 900).astype(int),
        'BMI':               np.random.normal(32, 7, n).clip(15, 60).round(1),
        'DiabetesPedigree':  np.random.exponential(0.5, n).clip(0.07, 2.5).round(3),
        'Age':               np.random.randint(21, 82, n),
    }
    df = pd.DataFrame(data)
    # Outcome based on clinical thresholds
    df['Outcome'] = (
        (df['Glucose'] > 140).astype(int) |
        (df['BMI'] > 30).astype(int) |
        (df['Age'] > 50).astype(int)
    ).clip(0, 1)
    # Add noise
    flip_idx = np.random.choice(n, size=int(n * 0.08), replace=False)
    df.loc[flip_idx, 'Outcome'] = 1 - df.loc[flip_idx, 'Outcome']
    df.to_csv(os.path.join(os.path.dirname(__file__), 'diabetes.csv'), index=False)
    print(f"✓ diabetes.csv — {n} records, {df['Outcome'].sum()} positive cases")
    return df

# ── Heart Disease Dataset ─────────────────────────────────────────────────
def generate_heart_disease(n=1000):
    data = {
        'age':         np.random.randint(29, 78, n),
        'sex':         np.random.randint(0, 2, n),
        'cp':          np.random.randint(0, 4, n),
        'trestbps':    np.random.normal(130, 18, n).clip(90, 200).astype(int),
        'chol':        np.random.normal(245, 50, n).clip(120, 570).astype(int),
        'fbs':         np.random.randint(0, 2, n),
        'restecg':     np.random.randint(0, 3, n),
        'thalach':     np.random.normal(150, 22, n).clip(70, 202).astype(int),
        'exang':       np.random.randint(0, 2, n),
        'oldpeak':     np.random.exponential(1.0, n).clip(0, 6.2).round(1),
        'slope':       np.random.randint(0, 3, n),
        'ca':          np.random.randint(0, 4, n),
        'thal':        np.random.choice([1, 2, 3], n),
    }
    df = pd.DataFrame(data)
    df['target'] = (
        (df['trestbps'] > 140).astype(int) |
        (df['chol'] > 240).astype(int) |
        (df['oldpeak'] > 2).astype(int) |
        (df['age'] > 55).astype(int)
    ).clip(0, 1)
    flip_idx = np.random.choice(n, size=int(n * 0.08), replace=False)
    df.loc[flip_idx, 'target'] = 1 - df.loc[flip_idx, 'target']
    df.to_csv(os.path.join(os.path.dirname(__file__), 'heart_disease.csv'), index=False)
    print(f"✓ heart_disease.csv — {n} records, {df['target'].sum()} positive cases")
    return df

# ── Hypertension Dataset ──────────────────────────────────────────────────
def generate_hypertension(n=1000):
    data = {
        'age':           np.random.randint(20, 80, n),
        'bmi':           np.random.normal(27, 6, n).clip(15, 50).round(1),
        'cholesterol':   np.random.normal(200, 40, n).clip(100, 400).astype(int),
        'glucose':       np.random.normal(95, 20, n).clip(60, 200).astype(int),
        'smoking':       np.random.randint(0, 2, n),
        'alcohol':       np.random.randint(0, 2, n),
        'stress_level':  np.random.randint(1, 11, n),
        'physical_activity': np.random.randint(0, 8, n),
        'salt_intake':   np.random.choice(['low', 'medium', 'high'], n),
    }
    df = pd.DataFrame(data)
    df['hypertension'] = (
        (df['age'] > 50).astype(int) |
        (df['bmi'] > 30).astype(int) |
        (df['stress_level'] > 7).astype(int) |
        (df['smoking'] == 1).astype(int)
    ).clip(0, 1)
    flip_idx = np.random.choice(n, size=int(n * 0.08), replace=False)
    df.loc[flip_idx, 'hypertension'] = 1 - df.loc[flip_idx, 'hypertension']
    df.to_csv(os.path.join(os.path.dirname(__file__), 'hypertension.csv'), index=False)
    print(f"✓ hypertension.csv — {n} records, {df['hypertension'].sum()} positive cases")
    return df

# ── Mental Health Dataset ─────────────────────────────────────────────────
def generate_mental_health(n=800):
    data = {
        'age':              np.random.randint(18, 70, n),
        'gender':           np.random.choice(['Male', 'Female', 'Other'], n),
        'stress_level':     np.random.randint(1, 11, n),
        'anxiety_score':    np.random.randint(1, 11, n),
        'depression_score': np.random.randint(1, 11, n),
        'sleep_hours':      np.random.normal(6.5, 1.5, n).clip(3, 10).round(1),
        'exercise_days':    np.random.randint(0, 8, n),
        'social_support':   np.random.randint(1, 11, n),
        'work_life_balance':np.random.randint(1, 11, n),
    }
    df = pd.DataFrame(data)
    df['wellness_index'] = (
        100 -
        df['stress_level'] * 4 -
        df['anxiety_score'] * 3 -
        df['depression_score'] * 3 +
        df['sleep_hours'] * 2 +
        df['exercise_days'] * 1.5 +
        df['social_support'] * 1
    ).clip(0, 100).round(1)
    df['risk_category'] = pd.cut(
        df['wellness_index'],
        bins=[0, 40, 65, 100],
        labels=['high_risk', 'moderate', 'low_risk']
    )
    df.to_csv(os.path.join(os.path.dirname(__file__), 'mental_health.csv'), index=False)
    print(f"✓ mental_health.csv — {n} records")
    return df

# ── Vitals Time Series ────────────────────────────────────────────────────
def generate_vitals_timeseries(n_patients=10, days=90):
    records = []
    from datetime import datetime, timedelta
    base_date = datetime(2024, 1, 1)
    for patient_id in range(1, n_patients + 1):
        base_hr = np.random.randint(65, 80)
        base_bp = np.random.randint(110, 130)
        for day in range(days):
            date = base_date + timedelta(days=day)
            records.append({
                'patient_id':    patient_id,
                'date':          date.strftime('%Y-%m-%d'),
                'heart_rate':    round(base_hr + np.random.normal(0, 5), 1),
                'bp_systolic':   round(base_bp + np.random.normal(0, 8), 0),
                'bp_diastolic':  round(base_bp * 0.65 + np.random.normal(0, 5), 0),
                'temperature':   round(36.6 + np.random.normal(0, 0.3), 1),
                'oxygen_sat':    round(97.5 + np.random.normal(0, 1), 1),
                'glucose':       round(90 + np.random.normal(0, 15), 1),
                'weight':        round(70 + np.random.normal(0, 0.5), 1),
            })
    df = pd.DataFrame(records)
    df.to_csv(os.path.join(os.path.dirname(__file__), 'vitals_timeseries.csv'), index=False)
    print(f"✓ vitals_timeseries.csv — {len(df)} records ({n_patients} patients × {days} days)")
    return df

# ── Symptom-Disease Mapping ───────────────────────────────────────────────
def generate_symptom_disease(n=500):
    symptoms_pool = [
        'headache', 'fever', 'chest pain', 'shortness of breath', 'fatigue',
        'nausea', 'vomiting', 'dizziness', 'joint pain', 'back pain',
        'abdominal pain', 'cough', 'sore throat', 'rash', 'numbness',
        'blurred vision', 'palpitations', 'swelling', 'anxiety', 'insomnia',
        'weight loss', 'frequent urination', 'excessive thirst', 'sweating'
    ]
    diseases = ['Common Cold', 'Influenza', 'Diabetes', 'Hypertension',
                'Anxiety Disorder', 'Migraine', 'GERD', 'Anemia',
                'Hypothyroidism', 'Cardiac Arrhythmia']
    records = []
    for _ in range(n):
        n_symptoms = np.random.randint(2, 6)
        selected = np.random.choice(symptoms_pool, n_symptoms, replace=False).tolist()
        disease = np.random.choice(diseases)
        records.append({
            'symptoms': ', '.join(selected),
            'symptom_count': n_symptoms,
            'disease': disease,
            'severity': np.random.choice(['mild', 'moderate', 'severe'], p=[0.5, 0.35, 0.15])
        })
    df = pd.DataFrame(records)
    df.to_csv(os.path.join(os.path.dirname(__file__), 'symptom_disease.csv'), index=False)
    print(f"✓ symptom_disease.csv — {n} records")
    return df

if __name__ == '__main__':
    print("\n🧬 AURA MEDIX — Dataset Generator\n" + "="*45)
    generate_diabetes()
    generate_heart_disease()
    generate_hypertension()
    generate_mental_health()
    generate_vitals_timeseries()
    generate_symptom_disease()
    print("\n✅ All datasets generated in /datasets/")
