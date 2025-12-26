package main

import (
	"log"
	"healthcare-backend/internal/database"
	"healthcare-backend/internal/mcp"
	"healthcare-backend/internal/services"
)

func main() {
	database.InitDB()

	// Services
	ragService := services.NewRAGService(database.DB)

	// MCP Server
	mcpServer := mcp.NewMCPServer(database.DB, ragService)

	log.Println("🚀 Healthcare Clinical MCP Server starting on stdio...")
	if err := mcpServer.Serve(); err != nil {
		log.Fatalf("MCP Server error: %v", err)
	}
}
