package handlers

import (
	"log"
	"time"

	"healthcare-backend/internal/models"
	"healthcare-backend/internal/services"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

type PatientHandler struct {
	DB         *gorm.DB
	RAG        *services.RAGService
	Prediction *services.PredictionService
}

func NewPatientHandler(db *gorm.DB, rag *services.RAGService, pred *services.PredictionService) *PatientHandler {
	return &PatientHandler{
		DB:         db,
		RAG:        rag,
		Prediction: pred,
	}
}

// Get All Patients for the Sidebar Queue
func (h *PatientHandler) GetPatients(c *fiber.Ctx) error {
	var patients []models.PatientData
	h.DB.Order("created_at desc").Find(&patients)
	return c.JSON(patients)
}

// Get Default Form Values for New Patient Intake
func (h *PatientHandler) GetDefaults(c *fiber.Ctx) error {
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
}

// Assessment + RAG Logic
func (h *PatientHandler) AssessPatient(c *fiber.Ctx) error {
	totalStart := time.Now()

	var patient models.PatientData
	if err := c.BodyParser(&patient); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
	}

	// Save Patient Record
	patient.ID = 0 // Force new record
	dbStart := time.Now()
	h.DB.Create(&patient)
	log.Printf("⏱️ DB Write: %v", time.Since(dbStart))

	// RAG Enhancement: Semantic Search for Similar Cases
	ragStart := time.Now()
	contextStr := h.RAG.FindSimilarCases(patient)
	log.Printf("⏱️ RAG Semantic Search: %v", time.Since(ragStart))

	// 2. Call ML Predict
	risks, err := h.Prediction.PredictRisks(patient)
	if err != nil {
		return c.Status(503).JSON(fiber.Map{"error": "ML Service Offline"})
	}

	// Emergency Logic
	isEmergency := risks.HeartRisk > 85 || patient.SystolicBP > 180

	// Logic for Medications
	medAnalysis := h.Prediction.CheckMedications(patient.Medications)

	// Logic for Model Precisions
	precisions := []models.ModelPrecision{}
	for name, conf := range risks.ModelPrecisions {
		precisions = append(precisions, models.ModelPrecision{ModelName: name, Confidence: conf})
	}

	// 3. Start LLM Diagnosis ASYNC (non-blocking)
	h.Prediction.StartAsyncDiagnosis(patient.ID, models.DiagnosisRequest{
		Patient:     patient,
		RiskScores:  *risks,
		PastContext: contextStr,
	})

	log.Printf("⏱️ FAST RESPONSE (no LLM wait): %v", time.Since(totalStart))

	return c.JSON(models.FullAssessmentResponse{
		ID:              patient.ID,
		Risks:           *risks,
		Diagnosis:       "", // Will be fetched via polling
		DiagnosisStatus: "pending",
		Emergency:       isEmergency,
		Patient:         patient,
		Medications:     medAnalysis,
		ModelPrecisions: precisions,
	})
}

// Poll for Diagnosis (async result)
func (h *PatientHandler) GetDiagnosis(c *fiber.Ctx) error {
	id, err := c.ParamsInt("id")
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Invalid patient ID"})
	}

	diagnosis, status := h.Prediction.Cache.Get(uint(id))
	return c.JSON(fiber.Map{
		"id":        id,
		"diagnosis": diagnosis,
		"status":    status,
	})
}
