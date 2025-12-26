# 📡 API Reference - Clinical Copilot

This document provides complete API documentation for all Clinical Copilot services.

---

## Service Overview

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| **Go Backend** | 3000 | Fiber (Go) | Orchestration, persistence, RAG-Lite |
| **ML API** | 8000 | FastAPI (Python) | Risk prediction, LLM integration |
| **Frontend** | 3001 | Next.js | Web interface |

---

## Go Backend API (Port 3000)

Base URL: `http://localhost:3000`

### Health Check

```http
GET /
```

**Response:**
```
🏥 Healthcare Clinical Copilot | Phase 4 Production Ready
```

---

### List All Patients

```http
GET /api/patients
```

Returns all patients ordered by creation date (newest first).

**Response:**
```json
[
  {
    "id": 1,
    "created_at": "2025-12-26T10:30:00Z",
    "age": 67,
    "gender": "Male",
    "systolic_bp": 185,
    "diastolic_bp": 110,
    "glucose": 240,
    "bmi": 32.5,
    "cholesterol": 245,
    "heart_rate": 98,
    "steps": 1200,
    "smoking": "Yes",
    "alcohol": "No",
    "medications": "Lisinopril, Metformin"
  }
]
```

---

### Get Default Form Values

```http
GET /api/defaults
```

Returns sensible defaults for new patient intake forms.

**Response:**
```json
{
  "age": 45,
  "gender": "Male",
  "systolic_bp": 120,
  "diastolic_bp": 80,
  "glucose": 100,
  "bmi": 24.5,
  "cholesterol": 190,
  "heart_rate": 72,
  "steps": 6000,
  "smoking": "No",
  "alcohol": "No",
  "medications": "Lisinopril, Atorvastatin"
}
```

---

### Full Patient Assessment

```http
POST /api/assess
Content-Type: application/json
```

Triggers a complete patient assessment including:
1. Patient record persistence
2. ML risk predictions (via ML API)
3. Medication interaction check
4. Async LLM diagnosis (non-blocking)

**Request Body:**
```json
{
  "age": 55,
  "gender": "Male",
  "systolic_bp": 145,
  "diastolic_bp": 92,
  "glucose": 128,
  "bmi": 29.5,
  "cholesterol": 220,
  "heart_rate": 82,
  "steps": 4500,
  "smoking": "No",
  "alcohol": "No",
  "medications": "Lisinopril, Metformin"
}
```

**Response:**
```json
{
  "id": 3,
  "risks": {
    "heart_risk_score": 42.5,
    "diabetes_risk_score": 8.7,
    "stroke_risk_score": 5.2,
    "kidney_risk_score": 12.0,
    "general_health_score": 82.9,
    "clinical_confidence": 94.2,
    "model_precisions": {
      "XGBoost Heart": 87.0,
      "RF Diabetes": 91.5,
      "GBM Stroke": 89.3
    }
  },
  "diagnosis": "",
  "diagnosis_status": "pending",
  "emergency": false,
  "patient": { /* PatientData object */ },
  "medication_analysis": {
    "risky": ["Metformin"],
    "safe": ["Lisinopril"]
  },
  "model_precisions": [
    {"model_name": "XGBoost Heart", "confidence": 87.0}
  ]
}
```

**Emergency Logic:**
- `emergency: true` if `heart_risk > 85` OR `systolic_bp > 180`

---

### Poll Diagnosis Status

```http
GET /api/diagnosis/:id
```

Polls the async LLM diagnosis result.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `id` | integer | Patient ID |

**Response:**
```json
{
  "id": 3,
  "diagnosis": "## Clinical Assessment\n\nBased on the patient's elevated BP...",
  "status": "ready"
}
```

**Status Values:**
| Status | Meaning |
|--------|---------|
| `pending` | LLM is still generating |
| `ready` | Diagnosis available |
| `error` | LLM service failed |

---

### Submit Doctor Feedback

```http
POST /api/feedback
Content-Type: application/json
```

Records doctor approval/correction for RAG-Lite learning.

**Request Body:**
```json
{
  "assessment_id": "assess_12345",
  "doctor_approved": true,
  "doctor_notes": "Accurate assessment. Patient referred to cardiology.",
  "risk_profile": "{\"heart\": 42.5, \"diabetes\": 8.7}"
}
```

**Response:**
```json
{
  "status": "recorded",
  "id": 7
}
```

---

## Python ML API (Port 8000)

Base URL: `http://localhost:8000`

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "models_loaded": ["heart", "diabetes", "stroke", "kidney"]
}
```

---

### Risk Prediction

```http
POST /predict
Content-Type: application/json
```

Runs all 4 ML models and returns risk scores.

**Request Body:**
```json
{
  "age": 55,
  "gender": "Male",
  "systolic_bp": 145,
  "diastolic_bp": 92,
  "glucose": 128,
  "bmi": 29.5,
  "cholesterol": 220,
  "heart_rate": 82,
  "steps": 4500,
  "smoking": "No",
  "alcohol": "No",
  "medications": ""
}
```

**Response:**
```json
{
  "heart_risk_score": 42.5,
  "diabetes_risk_score": 8.7,
  "stroke_risk_score": 5.2,
  "kidney_risk_score": 12.0,
  "general_health_score": 82.9,
  "clinical_confidence": 94.2,
  "model_precisions": {
    "XGBoost Heart": 87.0,
    "RF Diabetes": 91.5,
    "GBM Stroke": 89.3
  }
}
```

**Score Interpretation:**
| Risk Score | Clinical Meaning |
|------------|------------------|
| 0-20% | Low risk |
| 20-50% | Moderate risk |
| 50-80% | High risk |
| 80-100% | Critical risk |

---

### Medication Interaction Check

```http
POST /check-medication
Content-Type: application/json
```

Checks for drug-drug interactions.

**Request Body:**
```json
["Metformin", "Warfarin"]
```

**Response:**
```json
{
  "interactions": [
    {
      "med": "Metformin",
      "conflicts": ["Contrast Dye", "Excessive Alcohol"]
    },
    {
      "med": "Warfarin",
      "conflicts": ["Aspirin", "Vitamin K", "Leafy Greens"]
    }
  ]
}
```

---

### Neural Differential Diagnosis

```http
POST /diagnose
Content-Type: application/json
```

Generates LLM-powered clinical synthesis using Google Gemini.

**Request Body:**
```json
{
  "patient": {
    "age": 55,
    "gender": "Male",
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "glucose": 128,
    "bmi": 29.5,
    "cholesterol": 220,
    "heart_rate": 82,
    "steps": 4500,
    "smoking": "No",
    "alcohol": "No",
    "medications": ""
  },
  "risk_scores": {
    "heart_risk_score": 42.5,
    "diabetes_risk_score": 8.7,
    "stroke_risk_score": 5.2,
    "kidney_risk_score": 12.0
  },
  "past_context": "PAST CLINICAL DECISIONS:\n- Doctor Note: Patient responded well to lifestyle intervention."
}
```

**Response (Success):**
```json
{
  "diagnosis": "## Clinical Assessment\n\n### Primary Findings\nThe patient presents with **Stage 1 Hypertension** (BP 145/92)...",
  "status": "success"
}
```

**Response (Mock - No API Key):**
```json
{
  "diagnosis": "⚠️ **Mock Diagnosis (No API Key)**\n\n...",
  "status": "mock"
}
```

---

## Data Models

### PatientData

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `age` | integer | ✅ | Patient age in years |
| `gender` | string | ✅ | "Male" or "Female" |
| `systolic_bp` | integer | ✅ | Systolic blood pressure (mmHg) |
| `diastolic_bp` | integer | ✅ | Diastolic blood pressure (mmHg) |
| `glucose` | integer | ✅ | Blood glucose level (mg/dL) |
| `bmi` | float | ✅ | Body Mass Index |
| `cholesterol` | integer | ❌ | Total cholesterol (default: 190) |
| `heart_rate` | integer | ❌ | Resting heart rate (default: 72) |
| `steps` | integer | ❌ | Daily step count (default: 5000) |
| `smoking` | string | ❌ | "Yes", "No", or "Former" |
| `alcohol` | string | ❌ | "Yes" or "No" |
| `medications` | string | ❌ | Comma-separated list |

### Feedback

| Field | Type | Description |
|-------|------|-------------|
| `assessment_id` | string | Reference to the assessment |
| `doctor_approved` | boolean | Whether doctor approved the AI output |
| `doctor_notes` | string | Doctor's corrections or comments |
| `risk_profile` | string | JSON string of risk scores |

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 503 | Service Unavailable (ML API offline) |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for LLM |

---

## Quick Start Examples

### cURL - Full Assessment

```bash
curl -X POST http://localhost:3000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "gender": "Male",
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "glucose": 128,
    "bmi": 29.5,
    "cholesterol": 220,
    "heart_rate": 82,
    "steps": 4500,
    "smoking": "No"
  }'
```

### JavaScript Fetch

```javascript
const response = await fetch('http://localhost:3000/api/assess', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    age: 55,
    gender: 'Male',
    systolic_bp: 145,
    // ... other fields
  })
});
const data = await response.json();
```

### Python Requests

```python
import requests

response = requests.post(
    'http://localhost:8000/predict',
    json={
        'age': 55,
        'gender': 'Male',
        'systolic_bp': 145,
        'diastolic_bp': 92,
        'glucose': 128,
        'bmi': 29.5,
        'cholesterol': 220,
        'heart_rate': 82,
        'steps': 4500,
        'smoking': 'No'
    }
)
risks = response.json()
```

---

*Last updated: December 26, 2025*
