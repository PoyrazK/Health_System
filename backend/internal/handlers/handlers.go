package handlers

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"

	"healthcare-backend/internal/middleware"
	"healthcare-backend/internal/models"
)

// In-memory storage (replace with PostgreSQL in production)
var (
	users    = make(map[string]models.User)
	patients = make(map[string]models.Patient)
	reports  = make(map[string][]models.AIReport)
	labResults = make(map[string][]models.LabResult)
	mu       sync.RWMutex
)

// AI Service URL
var aiServiceURL = getAIServiceURL()

func getAIServiceURL() string {
	url := os.Getenv("AI_SERVICE_URL")
	if url == "" {
		return "http://localhost:8001"
	}
	return url
}

// ========================================
// Auth Handlers
// ========================================

// Register creates a new user
func Register(c *gin.Context) {
	var req models.RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	mu.Lock()
	defer mu.Unlock()

	// Check if user exists
	for _, u := range users {
		if u.Email == req.Email {
			c.JSON(http.StatusConflict, gin.H{"error": "Email already registered"})
			return
		}
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	// Create user
	user := models.User{
		ID:           uuid.New(),
		Email:        req.Email,
		PasswordHash: string(hashedPassword),
		Role:         req.Role,
		FullName:     req.FullName,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	users[user.ID.String()] = user

	// Generate token
	token, err := middleware.GenerateToken(user.ID.String(), user.Email, user.Role, user.FullName)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusCreated, models.TokenResponse{
		AccessToken: token,
		TokenType:   "Bearer",
		ExpiresIn:   86400,
		User:        user,
	})
}

// Login authenticates a user
func Login(c *gin.Context) {
	var req models.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	mu.RLock()
	defer mu.RUnlock()

	// Find user by email
	var foundUser *models.User
	for _, u := range users {
		if u.Email == req.Email {
			foundUser = &u
			break
		}
	}

	if foundUser == nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	// Verify password
	if err := bcrypt.CompareHashAndPassword([]byte(foundUser.PasswordHash), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	// Generate token
	token, err := middleware.GenerateToken(foundUser.ID.String(), foundUser.Email, foundUser.Role, foundUser.FullName)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, models.TokenResponse{
		AccessToken: token,
		TokenType:   "Bearer",
		ExpiresIn:   86400,
		User:        *foundUser,
	})
}

// GetCurrentUser returns the authenticated user
func GetCurrentUser(c *gin.Context) {
	userID := c.GetString("userID")
	
	mu.RLock()
	defer mu.RUnlock()

	user, exists := users[userID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, user)
}

// ========================================
// Patient Handlers
// ========================================

// GetPatients returns all patients
func GetPatients(c *gin.Context) {
	mu.RLock()
	defer mu.RUnlock()

	patientList := make([]models.Patient, 0, len(patients))
	for _, p := range patients {
		patientList = append(patientList, p)
	}

	c.JSON(http.StatusOK, gin.H{
		"patients": patientList,
		"total":    len(patientList),
	})
}

// GetPatient returns a single patient
func GetPatient(c *gin.Context) {
	id := c.Param("id")

	mu.RLock()
	defer mu.RUnlock()

	patient, exists := patients[id]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Patient not found"})
		return
	}

	c.JSON(http.StatusOK, patient)
}

// CreatePatient creates a new patient
func CreatePatient(c *gin.Context) {
	var patient models.Patient
	if err := c.ShouldBindJSON(&patient); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	patient.ID = uuid.New()
	patient.CreatedAt = time.Now()
	patient.UpdatedAt = time.Now()

	mu.Lock()
	patients[patient.ID.String()] = patient
	mu.Unlock()

	c.JSON(http.StatusCreated, patient)
}

// UpdatePatient updates a patient
func UpdatePatient(c *gin.Context) {
	id := c.Param("id")

	mu.Lock()
	defer mu.Unlock()

	_, exists := patients[id]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Patient not found"})
		return
	}

	var patient models.Patient
	if err := c.ShouldBindJSON(&patient); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	patient.ID = uuid.MustParse(id)
	patient.UpdatedAt = time.Now()
	patients[id] = patient

	c.JSON(http.StatusOK, patient)
}

// DeletePatient deletes a patient
func DeletePatient(c *gin.Context) {
	id := c.Param("id")

	mu.Lock()
	defer mu.Unlock()

	if _, exists := patients[id]; !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Patient not found"})
		return
	}

	delete(patients, id)
	c.JSON(http.StatusOK, gin.H{"message": "Patient deleted"})
}

// ========================================
// Lab Results Handlers
// ========================================

func GetLabResults(c *gin.Context) {
	patientID := c.Param("id")

	mu.RLock()
	defer mu.RUnlock()

	results, exists := labResults[patientID]
	if !exists {
		results = []models.LabResult{}
	}

	c.JSON(http.StatusOK, gin.H{"lab_results": results})
}

func CreateLabResult(c *gin.Context) {
	patientID := c.Param("id")
	userID := c.GetString("userID")

	var result models.LabResult
	if err := c.ShouldBindJSON(&result); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	result.ID = uuid.New()
	result.PatientID = uuid.MustParse(patientID)
	result.CreatedBy = uuid.MustParse(userID)
	result.CreatedAt = time.Now()

	mu.Lock()
	labResults[patientID] = append(labResults[patientID], result)
	mu.Unlock()

	c.JSON(http.StatusCreated, result)
}

// ========================================
// AI Integration Handlers
// ========================================

// PredictDisease calls AI service for disease prediction
func PredictDisease(c *gin.Context) {
	var req models.AIPredictRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Call AI service
	jsonData, _ := json.Marshal(req)
	resp, err := http.Post(aiServiceURL+"/api/v1/predict/disease", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "AI service unavailable"})
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	c.JSON(resp.StatusCode, result)
}

// AssessRisk calls AI service for risk assessment
func AssessRisk(c *gin.Context) {
	var req models.AIRiskRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Call AI service
	jsonData, _ := json.Marshal(req)
	resp, err := http.Post(aiServiceURL+"/api/v1/predict/risk", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "AI service unavailable"})
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	c.JSON(resp.StatusCode, result)
}

// GenerateReport calls AI service for LLM report generation
func GenerateReport(c *gin.Context) {
	var req map[string]interface{}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Call AI service
	jsonData, _ := json.Marshal(req)
	resp, err := http.Post(aiServiceURL+"/api/v1/llm/diagnose", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "AI service unavailable"})
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	c.JSON(resp.StatusCode, result)
}

// ========================================
// Report Handlers
// ========================================

func GetReports(c *gin.Context) {
	patientID := c.Param("id")

	mu.RLock()
	defer mu.RUnlock()

	patientReports, exists := reports[patientID]
	if !exists {
		patientReports = []models.AIReport{}
	}

	c.JSON(http.StatusOK, gin.H{"reports": patientReports})
}

func CreateReport(c *gin.Context) {
	patientID := c.Param("id")
	doctorID := c.GetString("userID")

	var report models.AIReport
	if err := c.ShouldBindJSON(&report); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	report.ID = uuid.New()
	report.PatientID = uuid.MustParse(patientID)
	report.DoctorID = uuid.MustParse(doctorID)
	report.CreatedAt = time.Now()
	report.UpdatedAt = time.Now()

	mu.Lock()
	reports[patientID] = append(reports[patientID], report)
	mu.Unlock()

	c.JSON(http.StatusCreated, report)
}
