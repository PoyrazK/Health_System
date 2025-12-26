package main

import (
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"

	"healthcare-backend/internal/database"
	"healthcare-backend/internal/handlers"
	"healthcare-backend/internal/services"
)

func main() {
	database.InitDB()

	app := fiber.New()

	app.Use(cors.New())
	app.Use(logger.New())

	ML_SERVICE_URL := "http://127.0.0.1:8000"

	// Services
	ragService := services.NewRAGService(database.DB)
	predService := services.NewPredictionService(ML_SERVICE_URL)

	// Handlers
	patientHandler := handlers.NewPatientHandler(database.DB, ragService, predService)
	feedbackHandler := handlers.NewFeedbackHandler(database.DB)

	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("🏥 Healthcare Clinical Copilot | Phase 4 Production Ready (Refactored)")
	})

	// Get All Patients for the Sidebar Queue
	app.Get("/api/patients", patientHandler.GetPatients)

	// Get Default Form Values for New Patient Intake
	app.Get("/api/defaults", patientHandler.GetDefaults)

	// 1. Assessment + RAG Logic
	app.Post("/api/assess", patientHandler.AssessPatient)

	// 4. Poll for Diagnosis (async result)
	app.Get("/api/diagnosis/:id", patientHandler.GetDiagnosis)

	// 5. Feedback Endpoint
	app.Post("/api/feedback", feedbackHandler.SubmitFeedback)

	log.Fatal(app.Listen(":3000"))
}
