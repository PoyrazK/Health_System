# 🔍 ML Explainability: Understanding the Risks

In Clinical Copilot v3.0, we have transitioned from "Black Box" predictions to **Explainable AI (XAI)**. Clinicians can now see exactly which biometric features are driving a patient's risk scores.

---

## 🚀 SHAP Integration

We utilize **SHAP (SHapley Additive exPlanations)** to decompose each model's prediction into individual feature contributions. 

### How it Works
1. **Per-Prediction Analysis**: For every patient assessment, the ML API calculates the contribution of each input feature to the final risk score.
2. **Feature Impact**: The system identifies the top 5 most influential features for each condition (Heart, Diabetes, Stroke).
3. **Clinical Translation**: These abstract mathematical values are returned to the frontend and displayed as "Key Risk Drivers."

### Example Output
If a patient has a **72% Heart Risk**, the SHAP analysis might reveal:
- **Systolic BP (+0.12)**: High blood pressure is the primary driver.
- **Age (+0.08)**: Patient age is a significant risk factor.
- **Cholesterol (+0.05)**: Elevated lipids contributing to vascular risk.
- **Heart Rate (-0.02)**: Healthy resting heart rate is slightly lowering the risk.

---

## 📈 Key Risk Drivers Panel

The dashboard now features a dynamic "Explainability HUD" that lists the top drivers for the selected risk profile.

| Driver | Impact | Clinical Significance |
|--------|--------|-----------------------|
| **Glucose** | High | Critical for Diabetes & Kidney risk assessments. |
| **Systolic BP** | High | Primary driver for Heart and Stroke risk. |
| **BMI** | Moderate | Modulates risk across all condition-specific models. |
| **History Flags** | Variable | New medical history markers (Stroke/Heart) provide baseline risk offsets. |

---

## 🧬 Why Explainability Matters?

1. **Clinician Trust**: Doctors are more likely to act on AI suggestions if they can verify the underlying logic.
2. **Targeted Intervention**: If the SHAP analysis shows "Glucose" is the top driver for a Heart risk, the clinician can focus specifically on metabolic control.
3. **Error Detection**: Helps identify cases where an outlier biometric (e.g., a data entry error) is skewing the result.

---
*Powered by XGBoost Contrib and SHAP values.*
