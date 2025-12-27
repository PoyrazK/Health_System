import numpy as np
import random
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class TriageEngine:
    def __init__(self):
        self.model = None
        self.risk_levels = {0: "GREEN (Normal)", 1: "YELLOW (Monitor)", 2: "RED (Emergency)"}

    def train_synthetic_model(self, num_samples=5000):
        """
        Generates synthetic patient data and trains a Triage AI.
        Features: [HeartRate, SpO2, AsymmetryScore, EAR, Age(Simulated)]
        """
        print("[Triage] Generating synthetic patient data...")
        X = []
        y = []

        for _ in range(num_samples):
            # 1. Base State (Healthy or Sick)
            scenario = random.choices(["healthy", "stroke", "cardiac", "critical"], weights=[0.4, 0.2, 0.2, 0.2])[0]
            
            # Defaults
            hr = random.randint(60, 90)
            spo2 = random.randint(95, 100)
            asym = random.uniform(0.0, 0.15) # Normal < 0.2
            ear = random.uniform(0.25, 0.35) # Normal > 0.2
            age = random.randint(20, 80)
            
            label = 0 # Green

            # 2. Modify based on scenario
            if scenario == "stroke":
                asym = random.uniform(0.15, 0.4) # Tuned: Made more sensitive (was 0.25)
                label = 2 # Red
                
            elif scenario == "cardiac":
                hr = random.randint(110, 160) # Tachycardia
                spo2 = random.randint(85, 94)
                label = 2 # Red
                if random.random() < 0.5: label = 1 # Sometimes just Yellow if young

            elif scenario == "critical":
                # Multi-symptom
                hr = random.randint(120, 150)
                asym = random.uniform(0.25, 0.5)
                spo2 = random.randint(80, 90)
                label = 2

            # Add noise
            hr += random.randint(-5, 5)
            
            X.append([hr, spo2, asym, ear, age])
            y.append(label)

        # Train
        print("[Triage] Training Random Forest Model...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        self.model = RandomForestClassifier(n_estimators=100)
        self.model.fit(X_train, y_train)
        
        score = self.model.score(X_test, y_test)
        print(f"[Triage] Model Accuracy: {score*100:.2f}%")
        print(classification_report(y_test, self.model.predict(X_test), target_names=["GREEN", "YELLOW", "RED"]))
        
        # Save Model
        with open("triage_model.pkl", "wb") as f:
            pickle.dump(self.model, f)
        print("[Triage] Model saved to 'triage_model.pkl'")
        
        return score

    def load_model(self):
        try:
            with open("triage_model.pkl", "rb") as f:
                self.model = pickle.load(f)
            print("[Triage] Model loaded successfully.")
            return True
        except FileNotFoundError:
            print("[Triage] No saved model found. Please train first.")
            return False

    def predict(self, hr, spo2, asymmetry, ear, age=30):
        """
        Interprets MediaPipe/Sensor data to return a Risk Level.
        """
        if self.model is None:
            if not self.load_model():
                return "UNKNOWN", 0.0
            
        features = [[hr, spo2, asymmetry, ear, age]]
        prediction_index = self.model.predict(features)[0]
        confidence = np.max(self.model.predict_proba(features))
        
        return self.risk_levels[prediction_index], confidence

    def predict_detailed(self, hr, spo2, asymmetry, ear, age=30):
        """
        Returns Risk Label and the 'Emergency Rate' (Probability of RED class).
        """
        if self.model is None:
            if not self.load_model():
                return "UNKNOWN", 0.0
            
        features = [[hr, spo2, asymmetry, ear, age]]
        prediction_index = self.model.predict(features)[0]
        
        # Get probability of RED class (Index 2)
        # Classes are usually [0, 1, 2] but let's be safe
        probs = self.model.predict_proba(features)[0]
        emergency_rate = probs[2] if len(probs) > 2 else 0.0
        
        return self.risk_levels[prediction_index], emergency_rate

if __name__ == "__main__":
    engine = TriageEngine()
    engine.train_synthetic_model()
    
    # Test Cases (Simulating MediaPipe Data)
    print("\n--- Testing 'Digital Doctor' ---")
    
    # Case 1: Healthy Person
    # MediaPipe says: HR=75, Asym=0.05
    res, conf = engine.predict(75, 98, 0.05, 0.30)
    print(f"Case 1 (HR=75, Sym): {res} ({conf:.2f})")
    
    # Case 2: Potential Stroke
    # MediaPipe says: HR=80, Asym=0.4 (Lip droop detected)
    res, conf = engine.predict(80, 96, 0.40, 0.30)
    print(f"Case 2 (HR=80, Asym!): {res} ({conf:.2f})")
    
    # Case 3: Cardiac Arrest
    # MediaPipe says: HR=140, SpO2=88
    res, conf = engine.predict(140, 88, 0.10, 0.25)
    print(f"Case 3 (HR=140, LowO2): {res} ({conf:.2f})")
