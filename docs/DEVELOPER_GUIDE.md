# 💻 Developer & Contributor Guide

This guide is for developers looking to extend Clinical Copilot, add new ML models, or modify the dashboard.

---

## 🛠️ Project Structure

```
Healthcare System/
├── backend/            # Go Fiber Orchestrator (Main API)
│   ├── cmd/server/     # Entry point
│   ├── internal/       # Business logic (Clean Arch)
│   └── clinical.db     # SQLite (Dev Only)
├── src/api/ml_api/     # Python FastAPI (ML Inference)
├── src/features/       # Data Engineering Pipe
├── frontend/           # Next.js 14 Dashboard
├── models/             # Serialized .pkl files & metadata
├── data/               # Raw & Processed clinical data
└── docs/               # Technical documentation
```

---

## 🧠 Adding a New ML Model

To integrate a new condition (e.g., "Lung Disease"):

1. **Training**: Train your model and save it as `models/lung_model.pkl`.
2. **Metadata**: Add the required feature list to `models/model_metadata.json`.
3. **ML API**: Update `src/api/ml_api/main.py`:
   - Load the new pickle in the startup block.
   - Add a transformation block in `transform_features()`.
   - Update `predict_risk()` to include the new score.
4. **Backend**: Update `backend/internal/models/models.go` to include the new field in `PredictResponse`.

---

## 🖥️ UI Development

The frontend is built with **Tailwind CSS** and **Framer Motion**.

### Adding a New Gauge
1. Navigate to `frontend/components/dashboard/RiskAnalysis.tsx`.
2. Add a new object to the `riskItems` array with the appropriate **Lucide Icon** and color.
3. The grid will automatically scale to accommodate the new gauge.

### Modifying the Intake Form
- Update `backend/internal/models/models.go` (PatientData struct).
- The `IntakeModal.tsx` automatically pulls defaults from the `/api/defaults` endpoint. Update `handlers/patient_handler.go` to add new fields.

---

## 🧪 Development Workflow

### 1. Hot Reloading
- **Go**: Use `air` (if installed) or just `go run cmd/server/main.go`.
- **Frontend**: `npm run dev` handles HMR.
- **ML API**: `uvicorn --reload` for automatic Python refreshes.

### 2. Database Migrations
We use **GORM AutoMigrate**. If you add a field to `PatientData` in Go, simply restart the backend; the SQLite/Postgres schema will update automatically.

---

## 📡 Messaging Protocols

### REST
Mainly used for patient intake and feedback submission.

### WebSocket
Used for the **Diagnosis Broadcast**. Ensure any new async clinical results are piped through `handlers/ws_handler.go`.

---
*Coding for the future of healthcare.*
