# 🏥 Clinical Copilot Frontend

This is the **Clinical Cockpit**, a high-density X-Terminal UI for the Clinical Copilot AI Healthcare System. Built with Next.js 14, it prioritizes rapid data interpretation and real-time clinical decision support.

## 🚀 Key Features

- **X-Terminal Dashboard:** High-contrast, dark-mode UI designed for clinical high-pressure environments.
- **Micro-Animations:** Driven by `framer-motion` for state-aware telemetry updates.
- **Full-Spectrum Connectivity:** Dual-link status monitoring for both the Go Backend and Python ML Microservice.

## 🏗️ Core Components

Located in `components/dashboard/`:

| Component | Description |
|-----------|-------------|
| **PatientSidebar** | Semantic patient queue with status indicators. |
| **VitalsGrid** | Real-time biometric telemetry display. |
| **RiskAnalysis** | Visual risk gauges with Clinical Confidence metrics. |
| **DiagnosisPanel** | Neural Differential synthesis (Gemini) with Markdown support. |
| **FeedbackPanel** | Clinician confirmation and notes for RAG-Lite learning. |

## 🛠️ Getting Started

### 1. Installation
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev -- -p 3001
```

Access the dashboard at `http://localhost:3001`.

## 📡 Port Configuration
The frontend communicates with:
- **Go Backend:** `http://localhost:3000` (Main Orchestrator)
- **ML API:** `http://localhost:8000` (Fallback/Diagnostic)

---
*Clinical Intelligence, Delivered.*

