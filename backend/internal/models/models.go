package models

import (
	"time"

	"github.com/google/uuid"
)

// User represents a system user (doctor, patient, admin)
type User struct {
	ID           uuid.UUID `json:"id"`
	Email        string    `json:"email"`
	PasswordHash string    `json:"-"`
	Role         string    `json:"role"` // "doctor", "patient", "admin"
	FullName     string    `json:"full_name"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// Patient represents a patient record
type Patient struct {
	ID                uuid.UUID `json:"id"`
	UserID            uuid.UUID `json:"user_id,omitempty"`
	FullName          string    `json:"full_name"`
	BirthDate         string    `json:"birth_date"`
	Gender            string    `json:"gender"`
	BloodType         string    `json:"blood_type"`
	Phone             string    `json:"phone"`
	Email             string    `json:"email"`
	Address           string    `json:"address"`
	EmergencyContact  string    `json:"emergency_contact"`
	Allergies         []string  `json:"allergies"`
	ChronicConditions []string  `json:"chronic_conditions"`
	CurrentMedications []string `json:"current_medications"`
	CreatedAt         time.Time `json:"created_at"`
	UpdatedAt         time.Time `json:"updated_at"`
}

// LabResult represents a lab test result
type LabResult struct {
	ID        uuid.UUID              `json:"id"`
	PatientID uuid.UUID              `json:"patient_id"`
	TestType  string                 `json:"test_type"`
	TestDate  time.Time              `json:"test_date"`
	Values    map[string]interface{} `json:"values"`
	Notes     string                 `json:"notes"`
	CreatedBy uuid.UUID              `json:"created_by"`
	CreatedAt time.Time              `json:"created_at"`
}

// AIReport represents an AI-generated medical report
type AIReport struct {
	ID               uuid.UUID `json:"id"`
	PatientID        uuid.UUID `json:"patient_id"`
	DoctorID         uuid.UUID `json:"doctor_id"`
	Symptoms         []string  `json:"symptoms"`
	MLPredictions    []MLPrediction `json:"ml_predictions"`
	RiskScore        float64   `json:"risk_score"`
	RiskLevel        string    `json:"risk_level"`
	LLMDiagnosis     string    `json:"llm_diagnosis"`
	DoctorNotes      string    `json:"doctor_notes"`
	DoctorApproved   bool      `json:"doctor_approved"`
	CreatedAt        time.Time `json:"created_at"`
	UpdatedAt        time.Time `json:"updated_at"`
}

// MLPrediction represents a disease prediction from ML model
type MLPrediction struct {
	Disease     string  `json:"disease"`
	Probability float64 `json:"probability"`
	Confidence  string  `json:"confidence"`
}

// VitalSigns represents patient vital measurements
type VitalSigns struct {
	BloodPressureSystolic  int     `json:"blood_pressure_systolic"`
	BloodPressureDiastolic int     `json:"blood_pressure_diastolic"`
	HeartRate              int     `json:"heart_rate"`
	Temperature            float64 `json:"temperature"`
	OxygenSaturation       int     `json:"oxygen_saturation"`
	Weight                 float64 `json:"weight"`
	Height                 float64 `json:"height"`
	BMI                    float64 `json:"bmi"`
}

// LoginRequest for authentication
type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
}

// RegisterRequest for user registration
type RegisterRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
	FullName string `json:"full_name" binding:"required"`
	Role     string `json:"role" binding:"required,oneof=doctor patient"`
}

// TokenResponse for login response
type TokenResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	ExpiresIn   int    `json:"expires_in"`
	User        User   `json:"user"`
}

// AIRequest for disease prediction
type AIPredictRequest struct {
	Symptoms []string `json:"symptoms" binding:"required"`
}

// AIRiskRequest for risk assessment
type AIRiskRequest struct {
	Age                   int      `json:"age"`
	BloodPressureSystolic int      `json:"blood_pressure_systolic"`
	BloodPressureDiastolic int     `json:"blood_pressure_diastolic"`
	Glucose               float64  `json:"glucose"`
	Cholesterol           float64  `json:"cholesterol"`
	BMI                   float64  `json:"bmi"`
	Smoking               bool     `json:"smoking"`
	DiabetesHistory       bool     `json:"diabetes_history"`
	Symptoms              []string `json:"symptoms"`
}
