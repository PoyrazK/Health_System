package handlers

import (
	"healthcare-backend/internal/models"
	"healthcare-backend/internal/services"

	"github.com/gofiber/fiber/v2"
)

type DiseaseHandler struct {
	PredictionService *services.PredictionService
}

func NewDiseaseHandler(ps *services.PredictionService) *DiseaseHandler {
	return &DiseaseHandler{PredictionService: ps}
}

func (h *DiseaseHandler) Predict(c *fiber.Ctx) error {
	var req models.DiseaseRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Invalid request body"})
	}

	if len(req.Symptoms) == 0 {
		return c.Status(400).JSON(fiber.Map{"error": "Symptoms are required"})
	}

	result, err := h.PredictionService.PredictDisease(req)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(result)
}
