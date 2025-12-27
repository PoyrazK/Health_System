package services

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"healthcare-backend/internal/cache"
	"healthcare-backend/internal/models"
	"healthcare-backend/internal/queue"
	"healthcare-backend/internal/resilience"

	"github.com/sony/gobreaker"
)

// -- Diagnosis Cache (RESTORED AS STATELESS REDIS WRAPPER) --

type DiagnosisCache struct{}

func NewDiagnosisCache() *DiagnosisCache {
	return &DiagnosisCache{}
}

func (c *DiagnosisCache) Set(id uint, diagnosis string, status string) {
	data := map[string]string{
		"diagnosis": diagnosis,
		"status":    status,
	}
	jsonData, _ := json.Marshal(data)
	cache.Set(fmt.Sprintf("diag:status:%d", id), jsonData, 1*time.Hour)
}

func (c *DiagnosisCache) Get(id uint) (string, string) {
	val, err := cache.Get(fmt.Sprintf("diag:status:%d", id))
	if err != nil {
		return "", ""
	}
	var data map[string]string
	if err := json.Unmarshal([]byte(val), &data); err != nil {
		return "", ""
	}
	return data["diagnosis"], data["status"]
}

// -- Service --

type PredictionService struct {
	MLServiceURL string
	Cache        *DiagnosisCache
	CB           *gobreaker.CircuitBreaker
}

func NewPredictionService(mlURL string) *PredictionService {
	return &PredictionService{
		MLServiceURL: mlURL,
		Cache:        NewDiagnosisCache(),
		CB:           resilience.NewCircuitBreaker("ML-Service"),
	}
}

func (s *PredictionService) hashVitals(p models.PatientData) string {
	raw := fmt.Sprintf("%d|%.2f|%.2f|%.2f|%.2f|%s", p.Age, p.SystolicBP, p.Glucose, p.BMI, p.Cholesterol, p.Smoking)
	h := sha256.Sum256([]byte(raw))
	return fmt.Sprintf("%x", h)
}

func (s *PredictionService) PredictRisks(patient models.PatientData) (*models.PredictResponse, error) {
	mlStart := time.Now()

	// 1. Check Cache
	cacheKey := fmt.Sprintf("predict:%d:%s", patient.ID, s.hashVitals(patient))
	if cached, err := cache.Get(cacheKey); err == nil {
		var risks models.PredictResponse
		if err := json.Unmarshal([]byte(cached), &risks); err == nil {
			log.Printf("🚀 ML Predict (CACHED): %v", time.Since(mlStart))
			return &risks, nil
		}
	}

	// 2. Cache Miss - Call ML API (with Circuit Breaker)
	body, err := s.CB.Execute(func() (interface{}, error) {
		predictPayload, err := json.Marshal(patient)
		if err != nil {
			return nil, err
		}

		resp, err := http.Post(s.MLServiceURL+"/predict", "application/json", bytes.NewBuffer(predictPayload))
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()

		var risks models.PredictResponse
		if err := json.NewDecoder(resp.Body).Decode(&risks); err != nil {
			return nil, err
		}
		return &risks, nil
	})

	if err != nil {
		log.Printf("🔌 ML Service Error (CB): %v", err)
		// Fallback: If we have an older cache, it would be returned in step 1.
		// If not, we return an error or empty risks with warning
		return nil, fmt.Errorf("ML service is currently unavailable")
	}

	risks := body.(*models.PredictResponse)

	// 3. Set Cache (TTL: 5 minutes)
	if risksData, err := json.Marshal(risks); err == nil {
		cache.Set(cacheKey, risksData, 5*time.Minute)
	}

	log.Printf("⏱️ ML Predict (LIVE): %v", time.Since(mlStart))
	return risks, nil
}

func (s *PredictionService) StartAsyncDiagnosis(patientID uint, req models.DiagnosisRequest, onComplete func(uint, string, string)) {
	// 1. Mark as pending in Redis
	s.Cache.Set(patientID, "", "pending")
	
	// 2. Publish to NATS for Worker pick-up
	reqData, _ := json.Marshal(req)
	if err := queue.Publish("llm.tasks", reqData); err != nil {
		log.Printf("❌ Failed to publish LLM task to NATS: %v", err)
		s.Cache.Set(patientID, "System overloaded - please retry", "error")
		return
	}

	log.Printf("🚀 LLM Task Published to NATS for patient %d", patientID)
	// onComplete is now slightly trickier in distributed system, 
	// typically handled via WS Pub/Sub in later phase.
}

func (s *PredictionService) CheckMedications(medStr string) models.InteractionResult {
	if medStr == "" {
		return models.InteractionResult{Risky: []string{}, Safe: []string{}}
	}
	
	meds := strings.Split(medStr, ",")
	for i, m := range meds {
		meds[i] = strings.TrimSpace(m)
	}

	conflicts := []string{"Metformin", "Contrast", "Alcohol", "NSAIDs"}
	risky := []string{}
	safe := []string{}

	for _, m := range meds {
		if m == "" { continue }
		isRisky := false
		for _, c := range conflicts {
			if strings.Contains(strings.ToLower(m), strings.ToLower(c)) {
				isRisky = true
				break
			}
		}
		if isRisky {
			risky = append(risky, m)
		} else {
			safe = append(safe, m)
		}
	}
	
	return models.InteractionResult{Risky: risky, Safe: safe}
}
