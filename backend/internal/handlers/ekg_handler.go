package handlers

import (
	"healthcare-backend/internal/models"
	"healthcare-backend/internal/services"

	"github.com/gofiber/fiber/v2"
)

type EKGHandler struct {
	PredictionService *services.PredictionService
}

func NewEKGHandler(ps *services.PredictionService) *EKGHandler {
	return &EKGHandler{PredictionService: ps}
}

func (h *EKGHandler) Analyze(c *fiber.Ctx) error {
	var req models.EKGRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Invalid request body"})
	}

	if len(req.Signal) == 0 {
		return c.Status(400).JSON(fiber.Map{"error": "Signal data is required"})
	}

	result, err := h.PredictionService.AnalyzeEKG(req)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(result)
}
