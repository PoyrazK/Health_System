package workers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"healthcare-backend/internal/cache"
	"healthcare-backend/internal/models"
	"healthcare-backend/internal/queue"
	"github.com/nats-io/nats.go"
)

type LLMWorker struct {
	MLServiceURL string
}

func NewLLMWorker(mlURL string) *LLMWorker {
	return &LLMWorker{MLServiceURL: mlURL}
}

func (w *LLMWorker) Start() {
	_, err := queue.Subscribe("llm.tasks", func(m *nats.Msg) {
		var req models.DiagnosisRequest
		if err := json.Unmarshal(m.Data, &req); err != nil {
			log.Printf("❌ LLM Worker: Failed to unmarshal request: %v", err)
			return
		}

		log.Printf("🤖 LLM Worker: Processing diagnosis for patient %d", req.PatientID)
		
		llmStart := time.Now()
		diagPayload, _ := json.Marshal(req)
		
		resp, err := http.Post(w.MLServiceURL+"/diagnose", "application/json", bytes.NewBuffer(diagPayload))
		if err != nil {
			log.Printf("❌ LLM Worker: HTTP error: %v", err)
			w.updateStatus(req.PatientID, "Diagnosis unavailable - LLM service error", "error")
			return
		}
		defer resp.Body.Close()

		var diagRes models.DiagnosisResponse
		if err := json.NewDecoder(resp.Body).Decode(&diagRes); err != nil {
			log.Printf("❌ LLM Worker: Decode error: %v", err)
			w.updateStatus(req.PatientID, "Diagnosis unavailable - Decode error", "error")
			return
		}

		log.Printf("✅ LLM Worker: Completed diagnosis for patient %d in %v", req.PatientID, time.Since(llmStart))
		w.updateStatus(req.PatientID, diagRes.Diagnosis, "ready")
	})

	if err != nil {
		log.Printf("❌ LLM Worker: Failed to subscribe: %v", err)
	} else {
		log.Println("👷 LLM Worker started and listening on llm.tasks")
	}
}

func (w *LLMWorker) updateStatus(patientID uint, diagnosis string, status string) {
	// Update Redis cache for polling/state
	// We use a JSON string or separate keys. Let's use what PredictionService uses if possible.
	// PredictionService uses internal map, which is BAD for scalability.
	// We should move that to Redis too.
	
	// Update Redis (Phase 3 already set up some Redis, let's use it here)
	cacheData := map[string]string{
		"diagnosis": diagnosis,
		"status":    status,
	}
	jsonData, _ := json.Marshal(cacheData)
	cache.Set(fmt.Sprintf("diag:status:%d", patientID), jsonData, 1*time.Hour)
	
	// Phase 6 will add Redis Pub/Sub broadcast here
}
