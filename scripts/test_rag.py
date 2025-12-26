import requests
import time

BASE_URL = "http://localhost:3000/api"

def run_test():
    # 1. Create Patient A (The "History" Case)
    print("creating patient A...")
    patient_a = {
        "age": 65, "gender": "Male", "systolic_bp": 180, "diastolic_bp": 110,
        "glucose": 150, "bmi": 30, "cholesterol": 240, "heart_rate": 90,
        "steps": 2000, "smoking": "Yes", "alcohol": "No", "medications": ""
    }
    
    # Assess to get ID
    resp = requests.post(f"{BASE_URL}/assess", json=patient_a)
    data_a = resp.json()
    id_a = data_a['id']
    print(f"Patient A created with ID: {id_a}")
    
    # 2. Add APPROVED feedback for Patient A
    feedback = {
        "assessment_id": id_a,
        "approved": True,
        "notes": "TEST_RAG_MATCH: Patient needs immediate cardiology referral due to hypertensive crisis.",
        "risks": {}
    }
    requests.post(f"{BASE_URL}/feedback", json=feedback)
    print("Feedback added for Patient A.")
    
    # 3. Create Patient B (Similar to A)
    print("Assess Patient B (Similar to A)...")
    patient_b = {
        "age": 63, "gender": "Male", "systolic_bp": 178, "diastolic_bp": 105, # Very similar
        "glucose": 155, "bmi": 31, "cholesterol": 235, "heart_rate": 88,
        "steps": 2100, "smoking": "Yes", "alcohol": "No", "medications": ""
    }
    
    # This assessment should trigger RAG search in backend logs
    resp_b = requests.post(f"{BASE_URL}/assess", json=patient_b)
    print(f"Patient B assessed. Status: {resp_b.status_code}")
    print("Check backend logs for 'TEST_RAG_MATCH' in RAG context.")

if __name__ == "__main__":
    run_test()
