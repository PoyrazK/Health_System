# 🏥 Clinical Copilot v1.8 - AI Decision Support Terminal

Clinical Copilot is a state-of-the-art medical decision support system designed for high-density clinical environments. It leverages multiple specialized ML models for risk prediction and a Large Language Model (Gemini 1.5 Flash) for clinical reasoning and diagnosis synthesis.

## 🚀 Key Features

- **X-Terminal Dashboard:** A high-density, Bloomberg-style UI designed for rapid data interpretation.
- **Multi-Model Risk Engine:**
  - **Heart Disease Risk:** XGBoost model trained on clinical cardiovascular data.
  - **Diabetes Risk:** Classifier based on long-term biometric trends.
  - **Stroke Assessment:** Predictive analysis of vascular health.
  - **Kidney Health AI:** Specialized indicators for chronic kidney disease risk.
- **Neural Differential Assessment:** LLM-powered (Gemini) synthesis that explains ML findings in clinical language, identifies paradoxes, and suggests next steps.
- **RAG-Lite Semantic Search:** Injects past doctor feedback and similar historical cases into the LLM prompt for context-aware reasoning.
- **Medication Safety HUD:** Real-time drug-drug and drug-condition interaction scanning with dynamic risk categorization.
- **Clinical Confidence Score:** Statistical confidence metrics for every prediction.
- **Live System Telemetry:** Real-time monitoring of network latency and microservice performance.
- **Biometric Telemetry:** Live streaming of BP, Glucose, BMI, Cholesterol, Heart Rate, and Steps.
- **New Triage System:** Seamless entry of new patient data with instant analysis.

> [!TIP]
> **New in v2.0**: See [System Upgrades](./docs/UPGRADES.md) for a deep dive into the latest architectural and feature enhancements.

## 🏗️ Architecture

The system follows a high-performance distributed architecture:

1.  **Frontend (Next.js 14 + Tailwind + Framer Motion):**
    *   Highly responsive viewport with glassmorphism aesthetics.
    *   Real-time state management for telemetry and risk updates.
2.  **Backend Orchestrator (Go Fiber):**
    *   Handles patient persistence (SQLite + GORM).
    *   Manages RAG-lite context retrieval.
    *   Coordinates requests between Frontend and ML microservices.
3.  **ML Microservice (Python FastAPI):**
    *   Serves multiple `joblib` serialized scikit-learn/XGBoost models.
    *   Handles feature transformation and alignment for inconsistent datasets.
    *   Integrates Google Generative AI (Gemini) for clinical reasoning.

## 🛠️ Technology Stack

- **Languages:** Go, Python, TypeScript (TSX)
- **Frameworks:** Fiber (Go), FastAPI (Python), Next.js (Web)
- **ML/DS:** Scikit-Learn, XGBoost, Pandas, Numpy
- **Database:** SQLite (Relational + Local Persistence)
- **LLM:** Google Gemini 1.5 Flash (Clinical Synthesis)
- **Styling:** Tailwind CSS, Lucide Icons, Framer Motion (Animations)

## 🏁 Getting Started

### 1. Prerequisites
- Go 1.21+
- Python 3.10+
- Node.js 18+
- Gemini API Key (stored in `.env`)

### 2. Environment Setup
Create a `.env` file in the root:
```env
GEMINI_API_KEY=your_key_here
```

### 3. Run ML API (Python)
```bash
cd src/api/ml_api
pip install -r requirements.txt
python main.py
```

### 4. Run Backend (Go)
```bash
cd backend
go run cmd/server/main.go
```

### 5. Run Frontend (Web)
```bash
cd frontend
npm install
npm run dev -- -p 4000
```
Access the terminal at `http://localhost:4000`.

---

## 👨‍⚕️ Clinical Disclaimer
Clinical Copilot is a clinical decision support tool (CDST) and should only be used as an auxiliary aid. Final diagnoses and decisions must be made by qualified medical professionals.
