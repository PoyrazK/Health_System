package main

import (
	"log"
	"healthcare-backend/internal/config"
	"healthcare-backend/internal/database"
	"healthcare-backend/internal/mcp"
	"healthcare-backend/internal/repositories"
	"healthcare-backend/internal/services"
)

func main() {
	cfg := config.Load()
	database.InitDB(cfg)

	// Repositories
	patientRepo := repositories.NewPatientRepository(database.DB)
	feedbackRepo := repositories.NewFeedbackRepository(database.DB)

	// Services
	ragService := services.NewRAGService(patientRepo, feedbackRepo)

	// MCP Server
	mcpServer := mcp.NewMCPServer(database.DB, ragService)

	log.Println("🚀 Healthcare Clinical MCP Server starting on stdio...")
	if err := mcpServer.Serve(); err != nil {
		log.Fatalf("MCP Server error: %v", err)
	}
}
