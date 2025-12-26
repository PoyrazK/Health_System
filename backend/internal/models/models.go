package models

import (
	"time"
)

// -- Database Models --

type PatientData struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	CreatedAt   time.Time `json:"created_at"`
	Age         int       `json:"age"`
	Gender      string    `json:"gender"`
	SystolicBP  int       `json:"systolic_bp"`
	DiastolicBP int       `json:"diastolic_bp"`
	Glucose     int       `json:"glucose"`
	BMI         float64   `json:"bmi"`
	Cholesterol int       `json:"cholesterol"`
	HeartRate   int       `json:"heart_rate"`
	Steps       int       `json:"steps"`
	Smoking     string    `json:"smoking"`
	Alcohol     string    `json:"alcohol"`
	Medications string    `json:"medications"` // Comma-separated
}

type Feedback struct {
	ID             uint      `gorm:"primaryKey" json:"id"`
	CreatedAt      time.Time `json:"created_at"`
	AssessmentID   string    `json:"assessment_id"` // Frontend ID
	PatientID      uint      `json:"patient_id"`    // Foreign Key for RAG
	DoctorApproved bool      `json:"doctor_approved"`
	DoctorNotes    string    `json:"doctor_notes"`
	RiskProfile    string    `gorm:"type:text" json:"risk_profile"` // JSON string of risks
}

// -- API Communication Structs --

type PredictResponse struct {
	HeartRisk          float64                       `json:"heart_risk_score"`
	DiabetesRisk       float64                       `json:"diabetes_risk_score"`
	StrokeRisk         float64                       `json:"stroke_risk_score"`
	KidneyRisk         float64                       `json:"kidney_risk_score"`
	GeneralHealthScore float64                       `json:"general_health_score"`
	ClinicalConfidence float64                       `json:"clinical_confidence"`
	ModelPrecisions    map[string]float64            `json:"model_precisions"`
	Explanations       map[string]map[string]float64 `json:"explanations"`
}

type DiagnosisRequest struct {
	Patient     PatientData     `json:"patient"`
	RiskScores  PredictResponse `json:"risk_scores"`
	PastContext string          `json:"past_context"` // RAG-Lite: Past doctor feedbacks
}

type DiagnosisResponse struct {
	Diagnosis string `json:"diagnosis"`
	Status    string `json:"status"`
}

type FullAssessmentResponse struct {
	ID              uint              `json:"id"`
	Risks           PredictResponse   `json:"risks"`
	Diagnosis       string            `json:"diagnosis"`
	DiagnosisStatus string            `json:"diagnosis_status"` // "pending", "ready", "error"
	Emergency       bool              `json:"emergency"`
	Patient         PatientData       `json:"patient"`
	Medications     InteractionResult `json:"medication_analysis"`
	ModelPrecisions []ModelPrecision  `json:"model_precisions"`
}

type InteractionResult struct {
	Risky []string `json:"risky"`
	Safe  []string `json:"safe"`
}

type ModelPrecision struct {
	ModelName  string  `json:"model_name"`
	Confidence float64 `json:"confidence"`
}
