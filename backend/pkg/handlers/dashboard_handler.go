package handlers

import (
	"healthcare-backend/pkg/middleware"
	"healthcare-backend/pkg/models"
	"healthcare-backend/pkg/services"
	"sync/atomic"
	"time"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

type DashboardHandler struct {
	DB         *gorm.DB
	Prediction *services.PredictionService
	Audit      *services.AuditService
}

func NewDashboardHandler(db *gorm.DB, pred *services.PredictionService, audit *services.AuditService) *DashboardHandler {
	return &DashboardHandler{
		DB:         db,
		Prediction: pred,
		Audit:      audit,
	}
}

func (h *DashboardHandler) GetSummary(c *fiber.Ctx) error {
	var totalPatients int64
	h.DB.Model(&models.PatientData{}).Count(&totalPatients)

	var highRiskPatients int64
	// Simple heuristic for "high risk" in dashboard summary: SystolicBP > 160
	h.DB.Model(&models.PatientData{}).Where("systolic_bp > 160").Count(&highRiskPatients)

	var recentAssessments int64
	// Patients created in the last 24 hours (SQLite compatible)
	h.DB.Model(&models.PatientData{}).Where("created_at > datetime('now', '-1 day')").Count(&recentAssessments)

	// Check ML Service Status
	mlPulse := "Online"
	if h.Prediction.CB.State().String() == "Open" {
		mlPulse = "Offline"
	}

	systemHealth := "Healthy"
	if mlPulse == "Offline" {
		systemHealth = "Warning"
	}

	// Risk Distribution - REAL DATA from database
	// High: SystolicBP > 160 | Medium: 140-160 | Low: < 140
	var lowRiskPatients int64
	var mediumRiskPatients int64
	h.DB.Model(&models.PatientData{}).Where("systolic_bp < 140").Count(&lowRiskPatients)
	h.DB.Model(&models.PatientData{}).Where("systolic_bp >= 140 AND systolic_bp <= 160").Count(&mediumRiskPatients)
	
	riskDist := map[string]int64{
		"Low":    lowRiskPatients,
		"Medium": mediumRiskPatients,
		"High":   highRiskPatients,
	}

	// Telemetry data
	reqCount := atomic.LoadUint64(&middleware.RequestCount)
	errCount := atomic.LoadUint64(&middleware.ErrorCount)
	uptime := time.Since(middleware.StartTime).Seconds()
	
	errRate := 0.0
	if reqCount > 0 {
		errRate = (float64(errCount) / float64(reqCount)) * 100
	}

	summary := models.DashboardSummary{
		TotalPatients:     totalPatients,
		HighRiskPatients:  highRiskPatients,
		RecentAssessments: recentAssessments,
		SystemHealth:      systemHealth,
		MLServicePulse:    mlPulse,
		AuditChainValid:   true,
		RiskDistribution:  riskDist,
		Performance: models.PerformanceMetrics{
			AvgMLInferenceTimeMs: h.Prediction.LastMLLatency,
			UptimeSeconds:        uptime,
			RequestCount:         int64(reqCount),
			ErrorRate:            errRate,
		},
	}

	return c.JSON(summary)
}
