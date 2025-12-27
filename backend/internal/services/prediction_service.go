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
)

// -- Diagnosis Cache --

type DiagnosisCache struct {
	mu      sync.RWMutex
	results map[uint]string // patientID -> diagnosis
	status  map[uint]string // patientID -> status (pending/ready/error)
}

func NewDiagnosisCache() *DiagnosisCache {
	return &DiagnosisCache{
		results: make(map[uint]string),
		status:  make(map[uint]string),
	}
}

func (c *DiagnosisCache) Set(id uint, diagnosis string, status string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.results[id] = diagnosis
	c.status[id] = status
}

func (c *DiagnosisCache) Get(id uint) (string, string) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.results[id], c.status[id]
}

// -- Service --

type PredictionService struct {
	MLServiceURL string
	Cache        *DiagnosisCache
}

func NewPredictionService(mlURL string) *PredictionService {
	return &PredictionService{
		MLServiceURL: mlURL,
		Cache:        NewDiagnosisCache(),
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

	// 2. Cache Miss - Call ML API
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

	// 3. Set Cache (TTL: 5 minutes)
	if risksData, err := json.Marshal(risks); err == nil {
		cache.Set(cacheKey, risksData, 5*time.Minute)
	}

	log.Printf("⏱️ ML Predict (LIVE): %v", time.Since(mlStart))
	return &risks, nil
}

func (s *PredictionService) StartAsyncDiagnosis(patientID uint, req models.DiagnosisRequest, onComplete func(uint, string, string)) {
	s.Cache.Set(patientID, "", "pending")
	
	go func() {
		llmStart := time.Now()
		diagPayload, _ := json.Marshal(req)
		
		diagRespRaw, err := http.Post(s.MLServiceURL+"/diagnose", "application/json", bytes.NewBuffer(diagPayload))
		if err != nil {
			s.Cache.Set(patientID, "Diagnosis unavailable - LLM service error", "error")
			if onComplete != nil {
				onComplete(patientID, "Diagnosis unavailable - LLM service error", "error")
			}
			log.Printf("⏱️ LLM Diagnose ASYNC ERROR: %v", err)
			return
		}
		defer diagRespRaw.Body.Close()
		
		var diagRes models.DiagnosisResponse
		json.NewDecoder(diagRespRaw.Body).Decode(&diagRes)
		s.Cache.Set(patientID, diagRes.Diagnosis, "ready")
		if onComplete != nil {
			onComplete(patientID, diagRes.Diagnosis, "ready")
		}
		log.Printf("⏱️ LLM Diagnose ASYNC COMPLETE: %v", time.Since(llmStart))
	}()
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
