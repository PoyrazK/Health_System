package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
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
	ID        uint            `json:"id"`
	Risks     PredictResponse `json:"risks"`
	Diagnosis string          `json:"diagnosis"`
	Emergency bool            `json:"emergency"`
	Patient   PatientData     `json:"patient"` // Added full patient data to response
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

	// 1. Assessment + RAG Logic
	app.Post("/api/assess", func(c *fiber.Ctx) error {
		var patient PatientData
		if err := c.BodyParser(&patient); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Save Patient Record
		db.Create(&patient)

		// RAG-Lite: Fetch last 3 approved feedbacks for similar age group to inject context
		var pastFeedbacks []Feedback
		db.Where("doctor_approved = ?", true).Limit(3).Order("created_at desc").Find(&pastFeedbacks)
		
		contextStr := "PAST CLINICAL DECISIONS:\n"
		for _, f := range pastFeedbacks {
			contextStr += fmt.Sprintf("- Doctor Note: %s\n", f.DoctorNotes)
		}

		// 2. Call ML Predict
		predictPayload, _ := json.Marshal(patient)
		resp, err := http.Post(ML_SERVICE_URL+"/predict", "application/json", bytes.NewBuffer(predictPayload))
		if err != nil {
			return c.Status(503).JSON(fiber.Map{"error": "ML Service Offline"})
		}
		defer resp.Body.Close()

		var risks PredictResponse
		json.NewDecoder(resp.Body).Decode(&risks)

		// Emergency Logic
		isEmergency := risks.HeartRisk > 85 || patient.SystolicBP > 180

		// 3. Call LLM Diagnosis with Context
		diagReq := DiagnosisRequest{
			Patient:     patient,
			RiskScores:  risks,
			PastContext: contextStr,
		}
		diagPayload, _ := json.Marshal(diagReq)
		
		diagRespRaw, _ := http.Post(ML_SERVICE_URL+"/diagnose", "application/json", bytes.NewBuffer(diagPayload))
		var diagRes DiagnosisResponse
		if diagRespRaw != nil {
			defer diagRespRaw.Body.Close()
			json.NewDecoder(diagRespRaw.Body).Decode(&diagRes)
		}

		return c.JSON(FullAssessmentResponse{
			ID:        patient.ID,
			Risks:     risks,
			Diagnosis: diagRes.Diagnosis,
			Emergency: isEmergency,
			Patient:   patient,
		})
	})

	// 4. Feedback Endpoint
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
