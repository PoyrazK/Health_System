package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// -- Database Models --

type PatientData struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	CreatedAt   time.Time `json:"created_at"`
	Age         int       `json:"age"`
	Gender      string    `json:"gender"`
	SystolicBP  int       `json:"systolic_bp"`
	DiastolicBP int       `json:"diastolic_bp"`
	Glucose     int       `json:"glucose"`
	BMI         float64   `json:"bmi"`
	Cholesterol int       `json:"cholesterol"`
	HeartRate   int       `json:"heart_rate"`
	Steps       int       `json:"steps"`
	Smoking     string    `json:"smoking"`
	Alcohol     string    `json:"alcohol"`
	Medications string    `json:"medications"` // Comma-separated
}

type Feedback struct {
	ID             uint      `gorm:"primaryKey" json:"id"`
	CreatedAt      time.Time `json:"created_at"`
	AssessmentID   string    `json:"assessment_id"`
	DoctorApproved bool      `json:"doctor_approved"`
	DoctorNotes    string    `json:"doctor_notes"`
	RiskProfile    string    `gorm:"type:text" json:"risk_profile"` // JSON string of risks
}

// -- API Communication Structs --

type PredictResponse struct {
	HeartRisk          float64 `json:"heart_risk_score"`
	DiabetesRisk       float64 `json:"diabetes_risk_score"`
	StrokeRisk         float64 `json:"stroke_risk_score"`
	KidneyRisk         float64 `json:"kidney_risk_score"`
	GeneralHealthScore float64 `json:"general_health_score"`
	ClinicalConfidence float64 `json:"clinical_confidence"`
	ModelPrecisions    map[string]float64 `json:"model_precisions"`
}

type DiagnosisRequest struct {
	Patient     PatientData     `json:"patient"`
	RiskScores  PredictResponse `json:"risk_scores"`
	PastContext string          `json:"past_context"` // RAG-Lite: Past doctor feedbacks
}

type DiagnosisResponse struct {
	Diagnosis string `json:"diagnosis"`
	Status    string `json:"status"`
}

type FullAssessmentResponse struct {
	ID              uint            `json:"id"`
	Risks           PredictResponse `json:"risks"`
	Diagnosis       string          `json:"diagnosis"`
	DiagnosisStatus string          `json:"diagnosis_status"` // "pending", "ready", "error"
	Emergency       bool            `json:"emergency"`
	Patient         PatientData     `json:"patient"`
	Medications     InteractionResult `json:"medication_analysis"`
	ModelPrecisions []ModelPrecision  `json:"model_precisions"`
}

type InteractionResult struct {
	Risky []string `json:"risky"`
	Safe  []string `json:"safe"`
}

type ModelPrecision struct {
	ModelName  string  `json:"model_name"`
	Confidence float64 `json:"confidence"`
}

// Helper to check medications
func checkMedications(medStr string) InteractionResult {
	if medStr == "" {
		return InteractionResult{Risky: []string{}, Safe: []string{}}
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
	
	return InteractionResult{Risky: risky, Safe: safe}
}

// In-memory cache for async diagnosis results
type DiagnosisCache struct {
	mu      sync.RWMutex
	results map[uint]string // patientID -> diagnosis
	status  map[uint]string // patientID -> status (pending/ready/error)
}

var diagCache = &DiagnosisCache{
	results: make(map[uint]string),
	status:  make(map[uint]string),
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


var db *gorm.DB

func initDB() {
	var err error
	db, err = gorm.Open(sqlite.Open("clinical.db"), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database")
	}
	db.AutoMigrate(&PatientData{}, &Feedback{})
	log.Println("✅ Database Migrated")
	seedDemoData()
}

func seedDemoData() {
	var count int64
	db.Model(&PatientData{}).Count(&count)
	if count == 0 {
		// 1. Ahmet Amca - The Emergency Case
		ahmet := PatientData{Age: 67, Gender: "Male", SystolicBP: 185, DiastolicBP: 110, Glucose: 240, BMI: 32.5, Cholesterol: 245, HeartRate: 98, Steps: 1200, Smoking: "Yes"}
		db.Create(&ahmet)
		
		// 2. Zeynep Hanim - The Stable Case
		zeynep := PatientData{Age: 42, Gender: "Female", SystolicBP: 118, DiastolicBP: 78, Glucose: 95, BMI: 22.1, Cholesterol: 180, HeartRate: 72, Steps: 8500, Smoking: "No"}
		db.Create(&zeynep)
		
		log.Println("🚀 Demo Patients Seeded: Ahmet Amca & Zeynep Hanim")
	}
}

func main() {
	initDB()
	app := fiber.New()

	app.Use(cors.New())
	app.Use(logger.New())

	ML_SERVICE_URL := "http://127.0.0.1:8000"

	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("🏥 Healthcare Clinical Copilot | Phase 4 Production Ready")
	})

	// Get All Patients for the Sidebar Queue
	app.Get("/api/patients", func(c *fiber.Ctx) error {
		var patients []PatientData
		db.Order("created_at desc").Find(&patients)
		return c.JSON(patients)
	})

	// Get Default Form Values for New Patient Intake
	app.Get("/api/defaults", func(c *fiber.Ctx) error {
		defaults := fiber.Map{
			"age":          45,
			"gender":       "Male",
			"systolic_bp":  120,
			"diastolic_bp": 80,
			"glucose":      100,
			"bmi":          24.5,
			"cholesterol":  190,
			"heart_rate":   72,
			"steps":        6000,
			"smoking":      "No",
			"alcohol":      "No",
			"medications":  "Lisinopril, Atorvastatin",
		}
		return c.JSON(defaults)
	})

	// 1. Assessment + RAG Logic
	app.Post("/api/assess", func(c *fiber.Ctx) error {
		totalStart := time.Now()
		
		var patient PatientData
		if err := c.BodyParser(&patient); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Save Patient Record
		dbStart := time.Now()
		db.Create(&patient)
		log.Printf("⏱️ DB Write: %v", time.Since(dbStart))

		// RAG-Lite: Fetch last 3 approved feedbacks for similar age group to inject context
		ragStart := time.Now()
		var pastFeedbacks []Feedback
		db.Where("doctor_approved = ?", true).Limit(3).Order("created_at desc").Find(&pastFeedbacks)
		
		contextStr := "PAST CLINICAL DECISIONS:\n"
		for _, f := range pastFeedbacks {
			contextStr += fmt.Sprintf("- Doctor Note: %s\n", f.DoctorNotes)
		}
		log.Printf("⏱️ RAG Query: %v", time.Since(ragStart))

		// 2. Call ML Predict
		mlStart := time.Now()
		predictPayload, _ := json.Marshal(patient)
		resp, err := http.Post(ML_SERVICE_URL+"/predict", "application/json", bytes.NewBuffer(predictPayload))
		if err != nil {
			return c.Status(503).JSON(fiber.Map{"error": "ML Service Offline"})
		}
		defer resp.Body.Close()

		var risks PredictResponse
		json.NewDecoder(resp.Body).Decode(&risks)
		log.Printf("⏱️ ML Predict: %v", time.Since(mlStart))

		// Emergency Logic
		isEmergency := risks.HeartRisk > 85 || patient.SystolicBP > 180

		// Logic for Medications
		medAnalysis := checkMedications(patient.Medications)

		// Logic for Model Precisions
		precisions := []ModelPrecision{}
		for name, conf := range risks.ModelPrecisions {
			precisions = append(precisions, ModelPrecision{ModelName: name, Confidence: conf})
		}

		// 3. Start LLM Diagnosis ASYNC (non-blocking)
		diagCache.Set(patient.ID, "", "pending")
		go func(patientID uint, diagReq DiagnosisRequest) {
			llmStart := time.Now()
			diagPayload, _ := json.Marshal(diagReq)
			
			diagRespRaw, err := http.Post(ML_SERVICE_URL+"/diagnose", "application/json", bytes.NewBuffer(diagPayload))
			if err != nil {
				diagCache.Set(patientID, "Diagnosis unavailable - LLM service error", "error")
				log.Printf("⏱️ LLM Diagnose ASYNC ERROR: %v", err)
				return
			}
			defer diagRespRaw.Body.Close()
			
			var diagRes DiagnosisResponse
			json.NewDecoder(diagRespRaw.Body).Decode(&diagRes)
			diagCache.Set(patientID, diagRes.Diagnosis, "ready")
			log.Printf("⏱️ LLM Diagnose ASYNC COMPLETE: %v", time.Since(llmStart))
		}(patient.ID, DiagnosisRequest{
			Patient:     patient,
			RiskScores:  risks,
			PastContext: contextStr,
		})

		log.Printf("⏱️ FAST RESPONSE (no LLM wait): %v", time.Since(totalStart))

		return c.JSON(FullAssessmentResponse{
			ID:              patient.ID,
			Risks:           risks,
			Diagnosis:       "", // Will be fetched via polling
			DiagnosisStatus: "pending",
			Emergency:       isEmergency,
			Patient:         patient,
			Medications:     medAnalysis,
			ModelPrecisions: precisions,
		})
	})

	// 4. Poll for Diagnosis (async result)
	app.Get("/api/diagnosis/:id", func(c *fiber.Ctx) error {
		id, err := c.ParamsInt("id")
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid patient ID"})
		}
		
		diagnosis, status := diagCache.Get(uint(id))
		return c.JSON(fiber.Map{
			"id":        id,
			"diagnosis": diagnosis,
			"status":    status,
		})
	})

	// 5. Feedback Endpoint
	app.Post("/api/feedback", func(c *fiber.Ctx) error {
		var fb Feedback
		if err := c.BodyParser(&fb); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid feedback"})
		}
		db.Create(&fb)
		return c.JSON(fiber.Map{"status": "recorded", "id": fb.ID})
	})

	log.Fatal(app.Listen(":3000"))
}
