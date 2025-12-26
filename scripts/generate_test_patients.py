"""
Generate 100 realistic test patients and evaluate model performance.
"""
import sqlite3
import random
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "backend" / "clinical.db"
API_URL = "http://localhost:8000/predict"

def generate_patient():
    """Generate a realistic patient profile with correlated features."""
    # Base demographics
    age = random.randint(18, 85)
    gender = random.choice(["Male", "Female"])
    
    # Risk factors increase with age
    age_factor = (age - 18) / 67  # 0 to 1 based on age
    
    # BMI: Normal distribution centered around 25, but higher for older
    bmi = max(18, min(45, random.gauss(25 + age_factor * 5, 5)))
    
    # Blood pressure: Increases with age and BMI
    base_systolic = 110 + age_factor * 30 + (bmi - 25) * 1.5
    systolic_bp = int(max(90, min(200, random.gauss(base_systolic, 15))))
    diastolic_bp = int(max(60, min(120, systolic_bp * 0.6 + random.gauss(0, 8))))
    
    # Glucose: Higher for obese and older
    base_glucose = 90 + age_factor * 20 + max(0, (bmi - 30) * 3)
    glucose = int(max(70, min(300, random.gauss(base_glucose, 20))))
    
    # Cholesterol: Increases with age
    cholesterol = int(max(150, min(350, random.gauss(180 + age_factor * 40, 30))))
    
    # Heart rate
    heart_rate = int(max(55, min(110, random.gauss(72, 12))))
    
    # Steps: Younger and healthier people walk more
    base_steps = 8000 - age_factor * 4000 - max(0, (bmi - 28) * 200)
    steps = int(max(500, min(15000, random.gauss(base_steps, 2000))))
    
    # Lifestyle
    smoking_prob = 0.15 + age_factor * 0.1  # Slightly higher for older
    smoking = "Yes" if random.random() < smoking_prob else "No"
    
    alcohol_prob = 0.2
    alcohol = "Yes" if random.random() < alcohol_prob else "No"
    
    # Medications based on conditions
    meds = []
    if systolic_bp > 140:
        meds.append("Lisinopril")
    if cholesterol > 240:
        meds.append("Atorvastatin")
    if glucose > 140:
        meds.append("Metformin")
    if random.random() < 0.1:
        meds.append("Aspirin")
    
    medications = ", ".join(meds) if meds else ""
    
    return {
        "age": age,
        "gender": gender,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "glucose": glucose,
        "bmi": round(bmi, 1),
        "cholesterol": cholesterol,
        "heart_rate": heart_rate,
        "steps": steps,
        "smoking": smoking,
        "alcohol": alcohol,
        "medications": medications
    }

def insert_patients(n=100):
    """Insert n patients into the database."""
    print(f"📝 Generating {n} test patients...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing test data (keep first 10 as demo)
    cursor.execute("DELETE FROM patient_data WHERE id > 10")
    conn.commit()
    
    patients = []
    for i in range(n):
        p = generate_patient()
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        cursor.execute("""
            INSERT INTO patient_data 
            (created_at, age, gender, systolic_bp, diastolic_bp, glucose, bmi, 
             cholesterol, heart_rate, steps, smoking, alcohol, medications)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at, p['age'], p['gender'], p['systolic_bp'], p['diastolic_bp'],
            p['glucose'], p['bmi'], p['cholesterol'], p['heart_rate'], p['steps'],
            p['smoking'], p['alcohol'], p['medications']
        ))
        
        p['id'] = cursor.lastrowid
        patients.append(p)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Inserted {n} patients into database")
    return patients

def evaluate_models(patients):
    """Run predictions and evaluate model performance."""
    print("\n🔬 Running predictions on all patients...")
    
    results = []
    for i, p in enumerate(patients):
        try:
            response = requests.post(API_URL, json=p, timeout=5)
            pred = response.json()
            
            results.append({
                'patient_id': p['id'],
                'age': p['age'],
                'gender': p['gender'],
                'systolic_bp': p['systolic_bp'],
                'glucose': p['glucose'],
                'bmi': p['bmi'],
                'cholesterol': p['cholesterol'],
                'smoking': p['smoking'],
                'heart_risk': pred.get('heart_risk_score', 0),
                'diabetes_risk': pred.get('diabetes_risk_score', 0),
                'stroke_risk': pred.get('stroke_risk_score', 0),
                'kidney_risk': pred.get('kidney_risk_score', 0),
                'health_score': pred.get('general_health_score', 0)
            })
            
            if (i + 1) % 20 == 0:
                print(f"   Processed {i + 1}/{len(patients)} patients...")
                
        except Exception as e:
            print(f"   Error for patient {p['id']}: {e}")
    
    df = pd.DataFrame(results)
    return df

def analyze_results(df):
    """Analyze and display model performance."""
    print("\n" + "="*60)
    print("📊 MODEL PERFORMANCE ANALYSIS")
    print("="*60)
    
    # Overall statistics
    print("\n📈 Risk Score Distribution:")
    print("-" * 40)
    for col in ['heart_risk', 'diabetes_risk', 'stroke_risk', 'kidney_risk']:
        print(f"   {col:15s}: Mean={df[col].mean():5.1f}%, "
              f"Min={df[col].min():5.1f}%, Max={df[col].max():5.1f}%")
    
    print(f"\n   Health Score  : Mean={df['health_score'].mean():.1f}%")
    
    # Correlation Analysis - Does the model respond to risk factors?
    print("\n🔗 Clinical Correlation Analysis:")
    print("-" * 40)
    
    # Heart risk should correlate with age, BP, cholesterol
    corr_heart_age = df['heart_risk'].corr(df['age'])
    corr_heart_bp = df['heart_risk'].corr(df['systolic_bp'])
    corr_heart_chol = df['heart_risk'].corr(df['cholesterol'])
    
    print(f"   Heart Risk ~ Age:        r = {corr_heart_age:+.3f} {'✅' if corr_heart_age > 0.1 else '⚠️'}")
    print(f"   Heart Risk ~ BP:         r = {corr_heart_bp:+.3f} {'✅' if corr_heart_bp > 0.1 else '⚠️'}")
    print(f"   Heart Risk ~ Cholesterol:r = {corr_heart_chol:+.3f} {'✅' if corr_heart_chol > 0.1 else '⚠️'}")
    
    # Diabetes should correlate with glucose, BMI
    corr_diabetes_glucose = df['diabetes_risk'].corr(df['glucose'])
    corr_diabetes_bmi = df['diabetes_risk'].corr(df['bmi'])
    print(f"   Diabetes ~ Glucose:      r = {corr_diabetes_glucose:+.3f} {'✅' if corr_diabetes_glucose > 0.1 else '⚠️'}")
    print(f"   Diabetes ~ BMI:          r = {corr_diabetes_bmi:+.3f} {'✅' if corr_diabetes_bmi > 0.1 else '⚠️'}")
    
    # Stroke should correlate with age, BP
    corr_stroke_age = df['stroke_risk'].corr(df['age'])
    corr_stroke_bp = df['stroke_risk'].corr(df['systolic_bp'])
    print(f"   Stroke ~ Age:            r = {corr_stroke_age:+.3f} {'✅' if corr_stroke_age > 0.1 else '⚠️'}")
    print(f"   Stroke ~ BP:             r = {corr_stroke_bp:+.3f} {'✅' if corr_stroke_bp > 0.1 else '⚠️'}")
    
    # Risk stratification
    print("\n🎯 Risk Stratification:")
    print("-" * 40)
    
    high_risk = df[df['heart_risk'] > 50]
    low_risk = df[df['heart_risk'] < 20]
    
    print(f"   High Heart Risk (>50%): {len(high_risk)} patients ({len(high_risk)/len(df)*100:.1f}%)")
    if len(high_risk) > 0:
        print(f"      Avg Age: {high_risk['age'].mean():.1f}, Avg BP: {high_risk['systolic_bp'].mean():.1f}")
    
    print(f"   Low Heart Risk (<20%):  {len(low_risk)} patients ({len(low_risk)/len(df)*100:.1f}%)")
    if len(low_risk) > 0:
        print(f"      Avg Age: {low_risk['age'].mean():.1f}, Avg BP: {low_risk['systolic_bp'].mean():.1f}")
    
    # Gender analysis
    print("\n👥 Gender Analysis:")
    print("-" * 40)
    for gender in ['Male', 'Female']:
        g_df = df[df['gender'] == gender]
        print(f"   {gender}: Avg Heart Risk = {g_df['heart_risk'].mean():.1f}%, "
              f"Avg Health Score = {g_df['health_score'].mean():.1f}%")
    
    # Sample predictions
    print("\n📋 Sample Predictions (5 random patients):")
    print("-" * 60)
    sample = df.sample(min(5, len(df)))
    for _, row in sample.iterrows():
        print(f"   ID {row['patient_id']:3d}: {row['age']}y {row['gender']:6s} | "
              f"BP {row['systolic_bp']:3d} | "
              f"Heart {row['heart_risk']:5.1f}% | "
              f"Health {row['health_score']:5.1f}%")
    
    print("\n" + "="*60)
    
    # Save results
    output_path = Path(__file__).parent.parent / "data" / "evaluation_results.csv"
    df.to_csv(output_path, index=False)
    print(f"💾 Results saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    # 1. Generate and insert patients
    patients = insert_patients(100)
    
    # 2. Run predictions
    results_df = evaluate_models(patients)
    
    # 3. Analyze performance
    if len(results_df) > 0:
        analyze_results(results_df)
    else:
        print("❌ No results to analyze. Make sure ML API is running on port 8000.")
