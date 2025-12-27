package handlers

import (
	"fmt"
	"log"
	"time"

	"healthcare-backend/pkg/models"
	"healthcare-backend/pkg/services"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

type FeedbackHandler struct {
	DB    *gorm.DB
	Audit *services.AuditService
}

func NewFeedbackHandler(db *gorm.DB, audit *services.AuditService) *FeedbackHandler {
	return &FeedbackHandler{DB: db, Audit: audit}
}

func (h *FeedbackHandler) SubmitFeedback(c *fiber.Ctx) error {
	type FeedbackRequest struct {
		AssessmentID int    `json:"assessment_id"` // Matches Patient ID in our simplified model
		Approved     bool   `json:"approved"`
		Notes        string `json:"notes"`
		Risks        any    `json:"risks"`
	}

	var req FeedbackRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Invalid feedback"})
	}

	// Map simplified request to DB model
	fb := models.Feedback{
		CreatedAt:      time.Now(),
		AssessmentID:   fmt.Sprintf("%d", req.AssessmentID),
		PatientID:      uint(req.AssessmentID), // Linking directly for RAG
		DoctorApproved: req.Approved,
		DoctorNotes:    req.Notes,
	}

	h.DB.Create(&fb)

	// 📜 Audit: Log Doctor Feedback
	if _, err := h.Audit.LogEvent("DOCTOR_FEEDBACK", fb.PatientID, req, "doctor"); err != nil {
		log.Printf("⚠️ Failed to log audit event: %v", err)
	}

	return c.JSON(fiber.Map{"status": "recorded", "id": fb.ID})
}
