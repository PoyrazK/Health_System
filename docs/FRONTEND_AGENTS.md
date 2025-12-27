# 🤖 Frontend Agents Guide

This document provides guidance for AI agents (like Gemini in IDE or custom agentic pipelines) when working on the Clinical Copilot **Frontend**.

---

## 🎯 Agent Scope

### Primary Responsibilities
- **UI Component Creation**: Building React/Next.js components for clinical data display.
- **State Management**: Handling patient data, API responses, and UI states.
- **API Integration**: Fetching from GoFiber (`/api/*`) and optionally ML API.

### File Locations
- **Pages**: `frontend/app/page.tsx`
- **Dashboard Components**: `frontend/components/dashboard/`
- **Modals**: `frontend/components/modals/`
- **Global Styles**: `frontend/app/globals.css`

---

## 📐 Design System

Agents must follow the established **"X-Terminal"** dark-mode aesthetic.

### Color Tokens (CSS Variables)
```css
--bg-primary: #0a0a0f;
--surface: rgba(255,255,255,0.03);
--border: rgba(255,255,255,0.1);
--text-primary: #ffffff;
--text-muted: #94a3b8;
--accent-blue: #3b82f6;
--accent-red: #ef4444;
--accent-green: #10b981;
```

### Typography
- **Headings**: `font-black`, `uppercase`, `tracking-widest`
- **Labels**: `text-[10px]`, `uppercase`, `tracking-[0.2em]`
- **Body**: `text-sm` or `text-xs`

### Animation Library
Use `framer-motion` for all transitions. Key patterns:
- `initial={{ opacity: 0, y: 10 }}`
- `animate={{ opacity: 1, y: 0 }}`

---

## 🛠️ Component Creation Rules

### 1. File Naming
- Use `PascalCase.tsx` for all components.
- Suffix UI state components with `Panel`, `Modal`, `Card`, etc.

### 2. Props Interface
Always define a TypeScript interface:
```typescript
interface RiskGaugeProps {
    label: string;
    value: number;
    icon: React.ElementType;
    colorClass: string;
}
```

### 3. API Calls
- Use `fetch()` with error handling.
- Base URL: `http://localhost:3000` (Go Backend).
- Fallback ML URL: `http://localhost:8000` (Python API).

Example:
```typescript
const fetchAssessment = async (patientData: any) => {
    const res = await fetch("http://localhost:3000/api/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patientData),
    });
    return res.json();
};
```

---

## 🧩 Existing Components Reference

| Component | Location | Purpose |
|-----------|----------|---------|
| `PatientSidebar` | `dashboard/` | Patient queue list |
| `VitalsGrid` | `dashboard/` | Biometric tiles |
| `RiskAnalysis` | `dashboard/` | Four risk gauges |
| `DiagnosisPanel` | `dashboard/` | LLM-generated differential |
| `FeedbackPanel` | `dashboard/` | Doctor validation terminal |
| `IntakeModal` | `modals/` | New patient form |
| `DiseaseCheckerModal` | `modals/` | Symptom-based AI diagnostics |
| `EKGPanel` | `dashboard/` | Signal waveform & EKG analysis |

---

## 🚨 Agent Constraints

1. **No Tailwind v4 Features**: Use Tailwind CSS v3 syntax only.
2. **No `next/image`**: Use standard `<img>` for simplicity.
3. **Icons**: Import from `lucide-react` only.
4. **Charts**: Use `recharts` if charting needed; avoid D3 complexity.
5. **No Inline Styles**: Use Tailwind utility classes or CSS variables.

---

## 📡 API Response Shapes

### Patient Assessment Response
```json
{
  "id": 1,
  "risks": {
    "heart_risk_score": 75.2,
    "diabetes_risk_score": 12.5
  },
  "diagnosis": "Markdown text...",
  "emergency": false,
  "medication_analysis": {
    "risky": ["Metformin"],
    "safe": ["Lisinopril"]
  }
}
```

### Disease Prediction Response (NEW)
```json
{
  "top_predictions": [
    {"disease": "Influenza", "probability": 78.5},
    {"disease": "Common Cold", "probability": 12.2}
  ],
  "risk_level": "MEDIUM"
}
```

### EKG Analysis Response (NEW)
```json
{
  "predictions": [
    {"condition": "Normal Sinus Rhythm", "probability": 0.85}
  ],
  "features": {
    "heart_rate": 72,
    "rr_mean": 833.5
  }
}
```

---

*Guide for AI Frontend Agents working on Clinical Copilot.*
