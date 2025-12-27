package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/limiter"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/contrib/websocket"

	"healthcare-backend/pkg/blockchain"
	"healthcare-backend/pkg/cache"
	"healthcare-backend/pkg/config"
	"healthcare-backend/pkg/database"
	"healthcare-backend/pkg/handlers"
	"healthcare-backend/pkg/middleware"
	"healthcare-backend/pkg/queue"
	"healthcare-backend/pkg/repositories"
	"healthcare-backend/pkg/services"
	"healthcare-backend/pkg/workers"

	"github.com/ansrivas/fiberprometheus/v2"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Initialize database (SQLite for local dev)
	database.InitDB()

	// Initialize Redis (optional - will fail gracefully)
	cache.InitRedis(cfg.RedisURL)

	// Initialize NATS (optional - will fail gracefully)
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
	app.Use(middleware.PerformanceMiddleware)

	// Prometheus Metrics
	prometheus := fiberprometheus.New("healthcare-backend")
	prometheus.RegisterAt(app, "/metrics")
	app.Use(prometheus.Middleware)

	// Rate Limiting (Global)
	app.Use(limiter.New(limiter.Config{
		Max:        cfg.RateLimitGlobalMax,
		Expiration: 1 * time.Minute,
		KeyGenerator: func(c *fiber.Ctx) string {
			return c.IP() // Explicitly key by IP
		},
		LimitReached: func(c *fiber.Ctx) error {
			return c.Status(429).JSON(fiber.Map{
				"success": false,
				"error":   "Too many global requests, slow down!",
			})
		},
	}))

	// Specific Limiter: ML Inference (Expensive)
	mlLimiter := limiter.New(limiter.Config{
		Max:        cfg.RateLimitMLMax,
		Expiration: 1 * time.Minute,
		KeyGenerator: func(c *fiber.Ctx) string {
			return c.IP()
		},
		LimitReached: func(c *fiber.Ctx) error {
			return c.Status(429).JSON(fiber.Map{
				"success": false,
				"error":   "ML Service rate limit exceeded. Please wait.",
			})
		},
	})

	// Specific Limiter: Feedback (Spam Prevention)
	feedbackLimiter := limiter.New(limiter.Config{
		Max:        cfg.RateLimitFeedbackMax,
		Expiration: 1 * time.Minute,
		KeyGenerator: func(c *fiber.Ctx) string {
			return c.IP()
		},
		LimitReached: func(c *fiber.Ctx) error {
			return c.Status(429).JSON(fiber.Map{
				"success": false,
				"error":   "Feedback submission rate limit exceeded.",
			})
		},
	})

	// Repositories
	patientRepo := repositories.NewPatientRepository(database.DB)
	feedbackRepo := repositories.NewFeedbackRepository(database.DB)

	// Services
	ragService := services.NewRAGService(patientRepo, feedbackRepo)
	predService := services.NewPredictionService(cfg.MLServiceURL)
	auditService := services.NewAuditService(database.DB)
	ipfsService := services.NewIPFSService()

	// Workers
	llmWorker := workers.NewLLMWorker(cfg.MLServiceURL)
	llmWorker.Start()

	// Handlers
	wsHandler := handlers.NewWebSocketHandler()
	wsHandler.StartGlobalListener() // Listen for Redis updates
	patientHandler := handlers.NewPatientHandler(database.DB, ragService, predService, wsHandler, auditService)
	feedbackHandler := handlers.NewFeedbackHandler(database.DB, auditService)
	diseaseHandler := handlers.NewDiseaseHandler(predService)
	ekgHandler := handlers.NewEKGHandler(predService)
	vitalsHandler := handlers.NewVitalsHandler(predService) // [NEW] Vitals Handler
	blockchainHandler := handlers.NewBlockchainHandler(auditService, ipfsService)
	dashboardHandler := handlers.NewDashboardHandler(database.DB, predService, auditService)

	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("🏥 Healthcare Clinical Copilot | Phase 8 (Scalability Stack)")
	})

	// 7. Health Probes (K8s Ready)
	app.Get("/health/live", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"status": "live", "uptime": "ok"})
	})

	app.Get("/health/ready", func(c *fiber.Ctx) error {
		ready := true
		dependencies := fiber.Map{}

		// DB Check
		sqlDB, _ := database.DB.DB()
		if err := sqlDB.Ping(); err != nil {
			ready = false
			dependencies["db"] = "unhealthy"
		} else {
			dependencies["db"] = "healthy"
		}

		// Redis Check
		if err := cache.Ping(); err != nil {
			ready = false
			dependencies["redis"] = "unhealthy"
		} else {
			dependencies["redis"] = "healthy"
		}

		// NATS Check
		if !queue.IsConnected() {
			ready = false
			dependencies["nats"] = "unhealthy"
		} else {
			dependencies["nats"] = "healthy"
		}

		status := 200
		if !ready {
			status = 503
		}

		return c.Status(status).JSON(fiber.Map{
			"status":       map[bool]string{true: "ready", false: "not ready"}[ready],
			"dependencies": dependencies,
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
	app.Post("/api/assess", mlLimiter, patientHandler.AssessPatient)
	app.Get("/api/diagnosis/:id", patientHandler.GetDiagnosis)
	app.Post("/api/feedback", feedbackLimiter, feedbackHandler.SubmitFeedback)
	app.Get("/api/dashboard/summary", dashboardHandler.GetSummary)

	// New AI Services
	app.Post("/api/disease/predict", diseaseHandler.Predict)
	app.Post("/api/ekg/analyze", ekgHandler.Analyze)
	app.Post("/api/vitals/analyze", vitalsHandler.Analyze) // [NEW] Route

	// 8. Blockchain Audit Endpoints (AI Act Compliance)
	app.Get("/api/blockchain/verify", blockchainHandler.VerifyChain)
	app.Post("/api/blockchain/backup", blockchainHandler.BackupChain)
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
