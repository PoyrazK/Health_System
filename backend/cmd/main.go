package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"

	"healthcare-backend/internal/handlers"
	"healthcare-backend/internal/middleware"
)

func main() {
	// Load .env file
	godotenv.Load()

	// Set Gin mode
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create router
	r := gin.Default()

	// CORS middleware
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "Healthcare Backend API",
			"time":    time.Now().Format(time.RFC3339),
		})
	})

	// Public routes (no auth required)
	public := r.Group("/api/v1")
	{
		public.POST("/auth/register", handlers.Register)
		public.POST("/auth/login", handlers.Login)
	}

	// Protected routes (auth required)
	protected := r.Group("/api/v1")
	protected.Use(middleware.AuthMiddleware())
	{
		// User routes
		protected.GET("/me", handlers.GetCurrentUser)

		// Patient routes
		protected.GET("/patients", handlers.GetPatients)
		protected.GET("/patients/:id", handlers.GetPatient)
		protected.POST("/patients", handlers.CreatePatient)
		protected.PUT("/patients/:id", handlers.UpdatePatient)
		protected.DELETE("/patients/:id", handlers.DeletePatient)

		// Lab results routes
		protected.GET("/patients/:id/lab-results", handlers.GetLabResults)
		protected.POST("/patients/:id/lab-results", handlers.CreateLabResult)

		// AI Integration routes
		protected.POST("/ai/predict-disease", handlers.PredictDisease)
		protected.POST("/ai/assess-risk", handlers.AssessRisk)
		protected.POST("/ai/generate-report", handlers.GenerateReport)

		// Reports routes
		protected.GET("/patients/:id/reports", handlers.GetReports)
		protected.POST("/patients/:id/reports", handlers.CreateReport)
	}

	// Get port
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 Healthcare Backend running on port %s", port)
	r.Run(":" + port)
}
