package services

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"healthcare-backend/pkg/cache"
	"healthcare-backend/pkg/models"
	"healthcare-backend/pkg/queue"
	"healthcare-backend/pkg/resilience"

	"github.com/sony/gobreaker"
)

// -- Diagnosis Cache (HYBRID: In-Memory + Redis) --

type DiagnosisCache struct{
	memCache map[uint]map[string]string
}

func NewDiagnosisCache() *DiagnosisCache {
	return &DiagnosisCache{
		memCache: make(map[uint]map[string]string),
	}
}

func (c *DiagnosisCache) Set(id uint, diagnosis string, status string) {
	data := map[string]string{
		"diagnosis": diagnosis,
		"status":    status,
	}
	
	// Store in memory (always works)
	c.memCache[id] = data
	
	// Try Redis as secondary (may fail silently)
	jsonData, _ := json.Marshal(data)
	cache.Set(fmt.Sprintf("diag:status:%d", id), jsonData, 1*time.Hour)
}

func (c *DiagnosisCache) Get(id uint) (string, string) {
	// Try memory first
	if data, ok := c.memCache[id]; ok {
		return data["diagnosis"], data["status"]
	}
	
	// Try Redis as fallback
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

func (s *PredictionService) HashVitals(p models.PatientData) string {
	raw := fmt.Sprintf("%d|%d|%d|%.2f|%d|%s", p.Age, p.SystolicBP, p.Glucose, p.BMI, p.Cholesterol, p.Smoking)
	h := sha256.Sum256([]byte(raw))
	return fmt.Sprintf("%x", h)
}

func (s *PredictionService) PredictRisks(patient models.PatientData) (*models.PredictResponse, error) {
	mlStart := time.Now()

	// 1. Check Cache
	cacheKey := fmt.Sprintf("predict:%d:%s", patient.ID, s.HashVitals(patient))
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

func (s *PredictionService) PredictDisease(req models.DiseaseRequest) (*models.DiseaseResponse, error) {
	body, err := s.CB.Execute(func() (interface{}, error) {
		payload, _ := json.Marshal(req)
		resp, err := http.Post(s.MLServiceURL+"/disease/predict", "application/json", bytes.NewBuffer(payload))
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()

		var result models.DiseaseResponse
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			return nil, err
		}
		return &result, nil
	})

	if err != nil {
		return nil, err
	}
	return body.(*models.DiseaseResponse), nil
}

func (s *PredictionService) AnalyzeEKG(req models.EKGRequest) (*models.EKGResponse, error) {
	body, err := s.CB.Execute(func() (interface{}, error) {
		payload, _ := json.Marshal(req)
		resp, err := http.Post(s.MLServiceURL+"/ekg/analyze", "application/json", bytes.NewBuffer(payload))
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()

		var result models.EKGResponse
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			return nil, err
		}
		return &result, nil
	})

	if err != nil {
		return nil, err
	}
	return body.(*models.EKGResponse), nil
}

func (s *PredictionService) StartAsyncDiagnosis(patientID uint, req models.DiagnosisRequest, onComplete func(uint, string, string)) {
	// 1. Mark as pending in Redis
	s.Cache.Set(patientID, "", "pending")
	
	// 2. Try to publish to NATS for Worker pick-up
	reqData, _ := json.Marshal(req)
	if err := queue.Publish("llm.tasks", reqData); err != nil {
		log.Printf("⚠️ NATS unavailable, falling back to sync LLM call for patient %d", patientID)
		// Fallback: Call LLM directly in a goroutine
		go s.callLLMDirectly(patientID, req, onComplete)
		return
	}

	log.Printf("🚀 LLM Task Published to NATS for patient %d", patientID)
}

// callLLMDirectly is a fallback when NATS is unavailable
func (s *PredictionService) callLLMDirectly(patientID uint, req models.DiagnosisRequest, onComplete func(uint, string, string)) {
	llmStart := time.Now()
	diagPayload, _ := json.Marshal(req)
	
	resp, err := http.Post(s.MLServiceURL+"/diagnose", "application/json", bytes.NewBuffer(diagPayload))
	if err != nil {
		log.Printf("❌ LLM Direct Call Error: %v", err)
		s.Cache.Set(patientID, "Diagnosis unavailable - LLM service error", "error")
		if onComplete != nil {
			onComplete(patientID, "Diagnosis unavailable - LLM service error", "error")
		}
		return
	}
	defer resp.Body.Close()

	var diagRes models.DiagnosisResponse
	if err := json.NewDecoder(resp.Body).Decode(&diagRes); err != nil {
		log.Printf("❌ LLM Direct Decode Error: %v", err)
		s.Cache.Set(patientID, "Diagnosis unavailable - Decode error", "error")
		if onComplete != nil {
			onComplete(patientID, "Diagnosis unavailable - Decode error", "error")
		}
		return
	}

	log.Printf("✅ LLM Direct Call completed for patient %d in %v", patientID, time.Since(llmStart))
	s.Cache.Set(patientID, diagRes.Diagnosis, "ready")
	if onComplete != nil {
		onComplete(patientID, diagRes.Diagnosis, "ready")
	}
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
