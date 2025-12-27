package models

import (
	"time"
)

// -- Database Models --

type PatientData struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	CreatedAt   time.Time `json:"created_at"`
	Age         int       `json:"age" validate:"required,min=0,max=150"`
	Gender      string    `json:"gender" validate:"required,oneof=Male Female Other"`
	SystolicBP  int       `json:"systolic_bp" validate:"required,min=50,max=300"`
	DiastolicBP int       `json:"diastolic_bp" validate:"required,min=30,max=200"`
	Glucose     int       `json:"glucose" validate:"required,min=20,max=600"`
	BMI         float64   `json:"bmi" validate:"required,min=10,max=80"`
	Cholesterol int       `json:"cholesterol" validate:"min=50,max=500"`
	HeartRate   int       `json:"heart_rate" validate:"min=30,max=250"`
	Steps       int       `json:"steps" validate:"min=0,max=100000"`
	Smoking     string    `json:"smoking" validate:"oneof=Yes No Former"`
	Alcohol     string    `json:"alcohol" validate:"oneof=Yes No"`
	Medications string    `json:"medications"` // Comma-separated
	HistoryHeartDisease string `json:"history_heart_disease" validate:"oneof=Yes No"`
	HistoryStroke       string `json:"history_stroke" validate:"oneof=Yes No"`
	HistoryDiabetes     string `json:"history_diabetes" validate:"oneof=Yes No"`
	HistoryHighChol     string `json:"history_high_chol" validate:"oneof=Yes No"`
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
