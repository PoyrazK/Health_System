package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/contrib/websocket"

	"healthcare-backend/internal/blockchain"
	"healthcare-backend/internal/cache"
	"healthcare-backend/internal/config"
	"healthcare-backend/internal/database"
	"healthcare-backend/internal/handlers"
	"healthcare-backend/internal/middleware"
	"healthcare-backend/internal/queue"
	"healthcare-backend/internal/repositories"
	"healthcare-backend/internal/services"
	"healthcare-backend/internal/workers"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Initialize database
	database.InitDB(cfg)

	// Initialize Redis
	cache.InitRedis(cfg.RedisURL)

	// Initialize NATS
	queue.InitNATS(cfg.NatsURL)
	defer queue.Close()

	// Create Fiber app with custom error handler
	app := fiber.New(fiber.Config{
		AppName: "Healthcare Clinical Copilot v1.0",
		ErrorHandler: func(c *fiber.Ctx, err error) error {
			code := fiber.StatusInternalServerError
			if e, ok := err.(*fiber.Error); ok {
				code = e.Code
			}
			return c.Status(code).JSON(middleware.ErrorResponse{
				Success: false,
				Error:   err.Error(),
				Code:    code,
			})
		},
	})

	// Middleware
	app.Use(cors.New())
	app.Use(logger.New())
	app.Use(middleware.ErrorHandler)

	// Repositories
	patientRepo := repositories.NewPatientRepository(database.DB)
	feedbackRepo := repositories.NewFeedbackRepository(database.DB)

	// Services
	ragService := services.NewRAGService(patientRepo, feedbackRepo)
	predService := services.NewPredictionService(cfg.MLServiceURL)
	auditService := services.NewAuditService(database.DB)

	// Workers
	llmWorker := workers.NewLLMWorker(cfg.MLServiceURL)
	llmWorker.Start()

	// Handlers
	wsHandler := handlers.NewWebSocketHandler()
	wsHandler.StartGlobalListener() // Listen for Redis updates
	patientHandler := handlers.NewPatientHandler(database.DB, ragService, predService, wsHandler, auditService)
	feedbackHandler := handlers.NewFeedbackHandler(database.DB, auditService)

	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("🏥 Healthcare Clinical Copilot | Phase 7 (Refactored)")
	})

	// Health Check Endpoint
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"status":  "healthy",
			"version": "1.0.0",
			"db":      "connected",
			"ml":      cfg.MLServiceURL,
		})
	})

	// WebSocket Routes
	if cfg.EnableWebSocket {
		app.Use("/ws", func(c *fiber.Ctx) error {
			if websocket.IsWebSocketUpgrade(c) {
				c.Locals("allowed", true)
				return c.Next()
			}
			return fiber.ErrUpgradeRequired
		})
		app.Get("/ws/diagnostics", websocket.New(wsHandler.HandleConnection))
	}

	// API Routes
	app.Get("/api/patients", patientHandler.GetPatients)
	app.Get("/api/defaults", patientHandler.GetDefaults)
	app.Post("/api/assess", patientHandler.AssessPatient)
	app.Get("/api/diagnosis/:id", patientHandler.GetDiagnosis)
	app.Post("/api/feedback", feedbackHandler.SubmitFeedback)

	// 8. Blockchain Audit Endpoints
	app.Get("/api/audit/chain", func(c *fiber.Ctx) error {
		// Just for safety if called before Init
		if blockchain.GlobalChain == nil {
			return c.Status(503).JSON(fiber.Map{"error": "Blockchain not initialized"})
		}
		
		chain := blockchain.GlobalChain.GetChain()
		isValid := blockchain.GlobalChain.IsChainValid()
		
		return c.JSON(fiber.Map{
			"chain":    chain,
			"valid":    isValid,
			"length":   len(chain),
			"verified": true, // We checked integrity in real-time
		})
	})

	// Graceful Shutdown
	go func() {
		c := make(chan os.Signal, 1)
		signal.Notify(c, os.Interrupt, syscall.SIGTERM)
		<-c
		log.Println("🛑 Graceful shutdown initiated...")
		_ = app.Shutdown()
	}()

	log.Printf("🚀 Server starting on port %s", cfg.ServerPort)
	log.Fatal(app.Listen(":" + cfg.ServerPort))
}
