package mcp

import (
	"context"
	"encoding/json"
	"fmt"
	"healthcare-backend/internal/models"
	"healthcare-backend/internal/services"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"gorm.io/gorm"
)

type MCPServer struct {
	DB   *gorm.DB
	RAG  *services.RAGService
	serv *server.MCPServer
}

func NewMCPServer(db *gorm.DB, rag *services.RAGService) *MCPServer {
	s := server.NewMCPServer(
		"Healthcare clinical Context Server",
		"1.0.0",
	)

	m := &MCPServer{
		DB:   db,
		RAG:  rag,
		serv: s,
	}

	m.registerTools()
	return m
}

func (m *MCPServer) registerTools() {
	// 1. Tool: Get Similar Patients
	getSimilarPatientsTool := mcp.NewTool("get_similar_patients",
		mcp.WithDescription("Find historical patient cases with similar clinical vitals (Age, BP, Glucose, BMI)"),
		mcp.WithNumber("age", mcp.Required()),
		mcp.WithNumber("systolic_bp", mcp.Required()),
		mcp.WithNumber("glucose", mcp.Required()),
		mcp.WithNumber("bmi", mcp.Required()),
	)
	m.serv.AddTool(getSimilarPatientsTool, m.handleGetSimilarPatients)

	// 2. Tool: Search Feedback
	searchFeedbackTool := mcp.NewTool("search_feedback",
		mcp.WithDescription("Search through historical doctor notes for specific symptoms or keywords"),
		mcp.WithString("query", mcp.Required()),
	)
	m.serv.AddTool(searchFeedbackTool, m.handleSearchFeedback)
}

func (m *MCPServer) handleGetSimilarPatients(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	// mcp-go 0.43.2 uses any for Arguments. We marshal/unmarshal to get it into our struct.
	argData, err := json.Marshal(request.Params.Arguments)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("Failed to marshal arguments: %v", err)), nil
	}

	var input struct {
		Age         int     `json:"age"`
		SystolicBP  int     `json:"systolic_bp"`
		Glucose     int     `json:"glucose"`
		BMI         float64 `json:"bmi"`
	}

	if err := json.Unmarshal(argData, &input); err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("Invalid arguments: %v", err)), nil
	}

	patient := models.PatientData{
		Age:        input.Age,
		SystolicBP: input.SystolicBP,
		Glucose:    input.Glucose,
		BMI:        input.BMI,
	}

	contextStr := m.RAG.FindSimilarCases(patient)

	return mcp.NewToolResultText(contextStr), nil
}

func (m *MCPServer) handleSearchFeedback(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	argData, err := json.Marshal(request.Params.Arguments)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("Failed to marshal arguments: %v", err)), nil
	}

	var input struct {
		Query string `json:"query"`
	}

	if err := json.Unmarshal(argData, &input); err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("Invalid arguments: %v", err)), nil
	}

	var feedbacks []models.Feedback
	m.DB.Where("doctor_notes LIKE ?", "%"+input.Query+"%").Limit(5).Find(&feedbacks)

	if len(feedbacks) == 0 {
		return mcp.NewToolResultText("No relevant feedback found for query: " + input.Query), nil
	}

	result := "Found historical clinical feedback:\n"
	for _, f := range feedbacks {
		result += fmt.Sprintf("- [Case %s]: %s\n", f.AssessmentID, f.DoctorNotes)
	}

	return mcp.NewToolResultText(result), nil
}

func (m *MCPServer) Serve() error {
	return server.ServeStdio(m.serv)
}
