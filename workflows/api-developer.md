---
description: API Developer Agent - Build FastAPI or Go backends for ML model serving
---

# API Developer Agent 🔌

Your role is to create production-ready APIs for serving ML models.

## Core Responsibilities
1. FastAPI/Go endpoint development
2. Model loading and inference
3. Input validation
4. Error handling and logging

## Workflow

### Step 1: Setup
// turbo
```bash
mkdir -p src/api
```

### Step 2: FastAPI Implementation

Create `src/api/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="ML Model API",
    description="API for hackathon ML model",
    version="1.0.0"
)

# Load model on startup
model = None
feature_engineer = None

@app.on_event("startup")
async def load_model():
    global model, feature_engineer
    with open("models/final/model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("data/features/feature_engineer.pkl", "rb") as f:
        feature_engineer = pickle.load(f)
    print("✓ Model loaded")

class PredictionInput(BaseModel):
    features: dict  # Key-value pairs of feature names to values

class PredictionOutput(BaseModel):
    prediction: float
    confidence: Optional[float] = None

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    try:
        df = pd.DataFrame([input_data.features])
        df_processed = feature_engineer.transform(df)
        prediction = model.predict(df_processed)[0]
        return PredictionOutput(prediction=float(prediction))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict_batch")
async def predict_batch(inputs: List[PredictionInput]):
    try:
        df = pd.DataFrame([i.features for i in inputs])
        df_processed = feature_engineer.transform(df)
        predictions = model.predict(df_processed)
        return {"predictions": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 3: Go API Alternative

Create `src/api/main.go`:

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type PredictionInput struct {
    Features map[string]float64 `json:"features"`
}

type PredictionOutput struct {
    Prediction float64 `json:"prediction"`
}

func predictHandler(w http.ResponseWriter, r *http.Request) {
    var input PredictionInput
    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    // Call Python model via subprocess or gRPC
    output := PredictionOutput{Prediction: 0.0}
    json.NewEncoder(w).Encode(output)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

func main() {
    http.HandleFunc("/predict", predictHandler)
    http.HandleFunc("/health", healthHandler)
    log.Println("Server starting on :8000")
    log.Fatal(http.ListenAndServe(":8000", nil))
}
```

### Step 4: Run API
// turbo
```bash
cd src/api && pip install fastapi uvicorn && python main.py
```

## Output Artifacts
- `src/api/main.py` - FastAPI implementation
- `src/api/main.go` - Go implementation (alternative)
- `requirements.txt` - API dependencies
