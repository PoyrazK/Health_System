# 🩺 Clinical Copilot: User Manual

Welcome to Clinical Copilot, your AI-powered decision support terminal. This guide will help you navigate the system and leverage its real-time predictive capabilities.

---

## 1. The Clinical Dashboard (Overview)

The dashboard is designed as a "Medical Command Center," prioritizing high-density information with zero visual clutter.

### Key Sections:
- **Left Panel (Patient Queue):** A real-time list of patients. High-risk cases are flagged with status indicators.
- **Center Panel (Command Center):** Displays vitals, risk gauges, and the neural assessment.
- **Right Panel (Medication & Feedback):** Shows active medication safety analysis and allows you to record clinical decisions.

---

## 2. Understanding Risk Gauges

The system calculates risk for 4 major conditions in real-time.

| Condition | Indicator | Meaning |
|-----------|-----------|---------|
| **Heart Risk** | 0-100% | Statistical probability of cardiovascular events. |
| **Diabetes** | 0-100% | Risk based on biometric trends and glucose levels. |
| **Stroke** | 0-100% | Vascular health assessment. |
| **Kidney** | 0-100% | Chronic kidney disease screening logic. |

> [!IMPORTANT]
> **Clinical Confidence Score:** Located near the gauges. This indicates the statistical reliability of the models based on the available data quality.

---

## 3. Emergency Triage

The system automatically flags emergencies based on critical biometric thresholds.

- **Trigger:** Systolic BP > 180 mmHg or Heart Risk > 85%.
- **Response:** The dashboard will display a **CRITICAL ALERT** banner and the status indicators will turn red.

---

## 4. Medication Safety HUD

The HUD proactively scans for conflicts as you enter patient data.

- **✅ SAFE:** Medications with no known conflicts in our database.
- **⚠️ RISKY:** Medications flagged for potential interactions (e.g., Metformin + Alcohol, lisinopril + NSAIDs).

---

## 5. Neural Differential Assessment

The system uses Gemini 1.5 Flash to synthesize all data into a clinical narrative.

1. **Wait for Synthesis:** Results appear 2-5 seconds after assessment.
2. **Read the Differential:** The AI identifies paradoxes (e.g., "High BP but low reported stress") and suggests follow-up questions.
3. **Approve/Notes:** Use the Feedback panel to record your approval. This "trains" the system's [RAG-Lite Engine](./ARCHITECTURE.md) for future similar cases.

---

## 6. Entering New Patients

To analyze a new patient:
1. Click the **"Add New Patient"** button (or similar triage action).
2. Enter biometrics (BP, Glucose, BMI).
3. List medications separated by commas.
4. Click **"Execute Assessment."**

---

## 🚑 Clinical Support & Safety
- **CDST Disclaimer:** This tool is for decision support only. 
- **Data Privacy:** Local clinical data is stored in the encrypted `clinical.db`.
- **Latency:** Check the telemetry indicator (bottom right) to ensure the system is responding in real-time.

---
*Clinical Copilot - Empowering Clinicians with Neural Intelligence.*
