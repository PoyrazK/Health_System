# 🧪 Testing Suite & Validation Logic

This document describes the automated test scripts and validation procedures used to ensure the reliability of the Clinical Copilot system.

---

## 🛠️ Automated Python Scripts

Located in the `/scripts/` directory, these utilities provide stress testing, data generation, and logical validation for the AI models.

### 1. RAG-Lite Validation (`test_rag.py`)
This script verifies the "Learning Loop" logic where doctor feedback informs future AI diagnoses.
- **Workflow**:
    1. Creates a "Patient A" with a high-risk profile.
    2. Submits an **Approved** feedback with a specific keyword (`TEST_RAG_MATCH`) in the notes.
    3. Creates a "Patient B" with a very similar biometric profile.
    4. **Expected Result**: Backend logs should show a successful RAG retrieval of Patient A's notes when assessing Patient B.
- **Run**: `python scripts/test_rag.py`

### 2. Large Scale Evaluation (`generate_test_patients.py`)
Stress tests the system by generating a synthetic cohort and documenting model accuracy.
- **Logic**:
    - Generates 100 realistic patients with correlated biometrics (e.g., higher Age correlates with higher BP).
    - Checks for **Clinical Correlation**: Ensures that heart risk scores actually increase with age and cholesterol (r > 0.1).
    - Saves results to `data/evaluation_results.csv` for audit.
- **Run**: `python scripts/generate_test_patients.py`

---

## 🏗️ Backend System Tests

The Go backend uses structured integration checks within its service layer.

### Health Probes
The backend exposes two major health endpoints for K8s/Infrastructure monitoring:
- `GET /health/live`: Basic liveness check.
- `GET /health/ready`: Deep readiness check verifying connections to **PostgreSQL**, **Redis**, and **NATS**.

### Circuit Breaker Testing
The `PredictionService` is protected by a **Sony Gobreaker** circuit breaker.
- **Test Pattern**: Rapidly trigger failures in the ML API (port 8000) and verify the Go backend returns a `503 Service Unavailable` instead of hanging, eventually "opening" the circuit to protect the system.

---

## 🖥️ Frontend Verification

Manual UI/UX validation checklists:
1. **Intake Modal**: Verify all 15+ fields correctly map to the backend `PatientData` struct.
2. **WebSocket Sync**: Confirm the `DiagnosisPanel` updates *without* page refresh when the AI completes its analysis.
3. **EKG Telemetry**: Generate a demo signal and verify the `EKGPanel` correctly extracts Heart Rate and R-R intervals.

---

## 📡 Live Integration Test

To run a full system integration test:
1. Start all services: `docker-compose up -d`
2. Run the RAG test: `python scripts/test_rag.py`
3. Verify metrics: Check `http://localhost:3001/` for updated patient cards.

---
*Last updated: December 27, 2025*
