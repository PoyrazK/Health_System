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
	// Try Redis first as workers update Redis
	val, err := cache.Get(fmt.Sprintf("diag:status:%d", id))
	if err == nil {
		var data map[string]string
		if err := json.Unmarshal([]byte(val), &data); err == nil {
			// Update local memory for faster subsequent hits
			c.memCache[id] = data
			return data["diagnosis"], data["status"]
		}
	}
	
	// Fallback to memory
	if data, ok := c.memCache[id]; ok {
		return data["diagnosis"], data["status"]
	}
	
	return "", ""
}

// -- Service --

type PredictionService struct {
	MLServiceURL  string
	Cache         *DiagnosisCache
	CB            *gobreaker.CircuitBreaker
	LastMLLatency int64 // Ms
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
		// Convert patient to map to handle symptoms as list
		symptomsSlice := []string{}
		if patient.Symptoms != "" {
			parts := strings.Split(patient.Symptoms, ",")
			for _, p := range parts {
				symptomsSlice = append(symptomsSlice, strings.TrimSpace(p))
			}
		}

		predictPayload, _ := json.Marshal(map[string]interface{}{
			"age":                   patient.Age,
			"gender":                patient.Gender,
			"systolic_bp":           patient.SystolicBP,
			"diastolic_bp":          patient.DiastolicBP,
			"glucose":               patient.Glucose,
			"bmi":                   patient.BMI,
			"cholesterol":           patient.Cholesterol,
			"heart_rate":            patient.HeartRate,
			"steps":                 patient.Steps,
			"smoking":               patient.Smoking,
			"alcohol":               patient.Alcohol,
			"medications":           patient.Medications,
			"history_heart_disease": patient.HistoryHeartDisease,
			"history_stroke":        patient.HistoryStroke,
			"history_diabetes":      patient.HistoryDiabetes,
			"history_high_chol":     patient.HistoryHighChol,
			"symptoms":              symptomsSlice,
		})

		resp, err := http.Post(s.MLServiceURL+"/predict", "application/json", bytes.NewBuffer(predictPayload))
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			return nil, fmt.Errorf("ML API returned status %d", resp.StatusCode)
		}

		var risks models.PredictResponse
		if err := json.NewDecoder(resp.Body).Decode(&risks); err != nil {
			return nil, err
		}
		return &risks, nil
	})

	if err != nil {
		log.Printf("🔌 ML Service Error (CB): %v. Activating Rule-Based Fallback!", err)
		return s.ruleBasedPredictRisks(patient), nil
	}

	risks := body.(*models.PredictResponse)

	// 3. Set Cache (TTL: 5 minutes)
	if risksData, err := json.Marshal(risks); err == nil {
		cache.Set(cacheKey, risksData, 5*time.Minute)
	}

	s.LastMLLatency = time.Since(mlStart).Milliseconds()
	log.Printf("⏱️ ML Predict (LIVE): %v", time.Since(mlStart))
	return risks, nil
}

// ruleBasedPredictRisks provides a clinical heuristic fallback when ML service is down
func (s *PredictionService) ruleBasedPredictRisks(p models.PatientData) *models.PredictResponse {
	risks := &models.PredictResponse{
		ModelPrecisions: map[string]float64{
			"Heart_Model":    0.0, // Indicated as rule-based
			"Diabetes_Model": 0.0,
			"Stroke_Model":   0.0,
			"Kidney_Model":   0.0,
		},
		Explanations: make(map[string]map[string]float64),
	}

	// Heuristic 1: Heart Risk
	if p.SystolicBP > 160 || p.Cholesterol > 240 {
		risks.HeartRisk = 0.85
	} else if p.SystolicBP > 140 || p.Cholesterol > 200 {
		risks.HeartRisk = 0.45
	} else {
		risks.HeartRisk = 0.15
	}

	// Heuristic 2: Diabetes Risk
	if p.Glucose > 200 || p.BMI > 35 {
		risks.DiabetesRisk = 0.90
	} else if p.Glucose > 125 || p.BMI > 30 {
		risks.DiabetesRisk = 0.50
	} else {
		risks.DiabetesRisk = 0.10
	}

	// Heuristic 3: Stroke Risk
	if p.Age > 65 && p.SystolicBP > 160 {
		risks.StrokeRisk = 0.75
	} else if p.Age > 50 && p.SystolicBP > 140 {
		risks.StrokeRisk = 0.35
	} else {
		risks.StrokeRisk = 0.05
	}

	// Global Stats
	risks.GeneralHealthScore = 1.0 - (risks.HeartRisk+risks.DiabetesRisk+risks.StrokeRisk)/3.0
	risks.ClinicalConfidence = 0.50 // Low confidence since it's rule-based
	
	return risks
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

func (s *PredictionService) PredictUrgency(symptoms []string, patient models.PatientData) (*models.UrgencyResponse, error) {
	body, err := s.CB.Execute(func() (interface{}, error) {
		// Prepare patient data as map for the ML API
		patientMap := map[string]interface{}{
			"age":          patient.Age,
			"systolic_bp":  patient.SystolicBP,
			"diastolic_bp": patient.DiastolicBP,
			"glucose":      patient.Glucose,
			"bmi":          patient.BMI,
			"cholesterol":  patient.Cholesterol,
			"heart_rate":   patient.HeartRate,
		}

		req := models.MLUrgencyRequest{
			Symptoms:    symptoms,
			PatientData: patientMap,
		}

		payload, _ := json.Marshal(req)
		resp, err := http.Post(s.MLServiceURL+"/urgency/predict", "application/json", bytes.NewBuffer(payload))
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()

		var urgency models.UrgencyResponse
		if err := json.NewDecoder(resp.Body).Decode(&urgency); err != nil {
			return nil, err
		}
		return &urgency, nil
	})

	if err != nil {
		return nil, err
	}
	return body.(*models.UrgencyResponse), nil
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

func (s *PredictionService) AnalyzeVitals(filePath string) (*models.VitalsResponse, error) {
	// Call ML API /vitals/analyze?file_path=...
	url := fmt.Sprintf("%s/vitals/analyze?file_path=%s", s.MLServiceURL, filePath)
	
	resp, err := http.Post(url, "application/json", nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ML API returned status %d", resp.StatusCode)
	}

	var result models.VitalsResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return &result, nil
}
