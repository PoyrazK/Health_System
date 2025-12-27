package main

import (
	"log"
	"healthcare-backend/pkg/database"
	"healthcare-backend/pkg/mcp"
	"healthcare-backend/pkg/repositories"
	"healthcare-backend/pkg/services"
)

func main() {
	database.InitDB()

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
