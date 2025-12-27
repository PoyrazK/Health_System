package handlers

import (
	"fmt"
	"healthcare-backend/pkg/models"
	"healthcare-backend/pkg/services"
	"os"
	"path/filepath"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

type VitalsHandler struct {
	predictionService *services.PredictionService
}

func NewVitalsHandler(p *services.PredictionService) *VitalsHandler {
	return &VitalsHandler{
		predictionService: p,
	}
}

// Analyze handles the POST /api/vitals/analyze request (multipart/form-data)
func (h *VitalsHandler) Analyze(c *fiber.Ctx) error {
	// 1. Get file from form
	file, err := c.FormFile("video")
	if err != nil {
		return fiber.NewError(fiber.StatusBadRequest, "No video file uploaded (use field name 'video')")
	}

	// 2. Validate file (Simple size/ext check)
	if file.Size > 50*1024*1024 { // 50MB limit
		return fiber.NewError(fiber.StatusBadRequest, "File too large (max 50MB)")
	}
	
	ext := filepath.Ext(file.Filename)
	if ext != ".mp4" && ext != ".mov" && ext != ".avi" {
		return fiber.NewError(fiber.StatusBadRequest, "Unsupported format (only .mp4, .mov, .avi)")
	}

	// 3. Save to shared uploads volume
	uploadDir := "/app/uploads"
	// Ensure dir exists (though docker should handle it)
	_ = os.MkdirAll(uploadDir, 0755)

	uniqueFilename := fmt.Sprintf("%d-%s%s", time.Now().Unix(), uuid.New().String()[:8], ext)
	savePath := filepath.Join(uploadDir, uniqueFilename)

	if err := c.SaveFile(file, savePath); err != nil {
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to save upload: "+err.Error())
	}

	// 4. Call Service Proxy (Pass the path as seen inside the container)
	result, err := h.predictionService.AnalyzeVitals(savePath)
	if err != nil {
		// Cleanup on failure
		_ = os.Remove(savePath)
		return fiber.NewError(fiber.StatusInternalServerError, "Analysis failed: "+err.Error())
	}

	return c.JSON(models.APIResponse{
		Success: true,
		Data:    result,
	})
}
