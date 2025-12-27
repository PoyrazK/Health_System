package unit

import (
	"healthcare-backend/pkg/models"
	"healthcare-backend/pkg/services"
	"testing"
)

// TestDiagnosisCache_SetGet tests cache set and get operations
func TestDiagnosisCache_SetGet(t *testing.T) {
	cache := services.NewDiagnosisCache()

	cache.Set(1, "Test diagnosis content", "ready")

	diagnosis, status := cache.Get(1)

	if diagnosis != "Test diagnosis content" {
		t.Errorf("Expected 'Test diagnosis content', got '%s'", diagnosis)
	}
	if status != "ready" {
		t.Errorf("Expected status 'ready', got '%s'", status)
	}
}

// TestDiagnosisCache_GetNotFound tests getting non-existent entry
func TestDiagnosisCache_GetNotFound(t *testing.T) {
	cache := services.NewDiagnosisCache()

	diagnosis, status := cache.Get(9999)

	if diagnosis != "" {
		t.Errorf("Expected empty diagnosis, got '%s'", diagnosis)
	}
	if status != "" {
		t.Errorf("Expected empty status, got '%s'", status)
	}
}

// TestDiagnosisCache_Overwrite tests overwriting existing entry
func TestDiagnosisCache_Overwrite(t *testing.T) {
	cache := services.NewDiagnosisCache()

	cache.Set(1, "Initial", "pending")
	cache.Set(1, "Updated", "ready")

	diagnosis, status := cache.Get(1)

	if diagnosis != "Updated" {
		t.Errorf("Expected 'Updated', got '%s'", diagnosis)
	}
	if status != "ready" {
		t.Errorf("Expected 'ready', got '%s'", status)
	}
}

// TestCheckMedications_Risky tests detection of risky medications
func TestCheckMedications_Risky(t *testing.T) {
	service := &services.PredictionService{}

	result := service.CheckMedications("Metformin, Aspirin, NSAIDs")

	if len(result.Risky) != 2 {
		t.Errorf("Expected 2 risky medications, got %d", len(result.Risky))
	}

	riskyMap := make(map[string]bool)
	for _, m := range result.Risky {
		riskyMap[m] = true
	}

	if !riskyMap["Metformin"] {
		t.Error("Expected Metformin to be flagged as risky")
	}
	if !riskyMap["NSAIDs"] {
		t.Error("Expected NSAIDs to be flagged as risky")
	}
}

// TestCheckMedications_Safe tests safe medications
func TestCheckMedications_Safe(t *testing.T) {
	service := &services.PredictionService{}

	result := service.CheckMedications("Lisinopril, Atorvastatin")

	if len(result.Risky) != 0 {
		t.Errorf("Expected 0 risky medications, got %d", len(result.Risky))
	}
	if len(result.Safe) != 2 {
		t.Errorf("Expected 2 safe medications, got %d", len(result.Safe))
	}
}

// TestCheckMedications_Empty tests empty medication string
func TestCheckMedications_Empty(t *testing.T) {
	service := &services.PredictionService{}

	result := service.CheckMedications("")

	if len(result.Risky) != 0 {
		t.Errorf("Expected 0 risky medications, got %d", len(result.Risky))
	}
	if len(result.Safe) != 0 {
		t.Errorf("Expected 0 safe medications, got %d", len(result.Safe))
	}
}

// TestCheckMedications_MixedCase tests case-insensitive matching
func TestCheckMedications_MixedCase(t *testing.T) {
	service := &services.PredictionService{}

	result := service.CheckMedications("METFORMIN, nsaids")

	if len(result.Risky) != 2 {
		t.Errorf("Expected 2 risky medications (case-insensitive), got %d", len(result.Risky))
	}
}

// TestHashVitals tests vitals hashing for cache keys
func TestHashVitals(t *testing.T) {
	service := services.NewPredictionService("http://localhost:8000")

	patient1 := models.PatientData{
		Age:        45,
		SystolicBP: 120,
		Glucose:    100,
		BMI:        24.5,
		Cholesterol: 190,
		Smoking:    "No",
	}

	patient2 := models.PatientData{
		Age:        45,
		SystolicBP: 120,
		Glucose:    100,
		BMI:        24.5,
		Cholesterol: 190,
		Smoking:    "No",
	}

	patient3 := models.PatientData{
		Age:        50,
		SystolicBP: 120,
		Glucose:    100,
		BMI:        24.5,
		Cholesterol: 190,
		Smoking:    "No",
	}

	hash1 := service.HashVitals(patient1)
	hash2 := service.HashVitals(patient2)
	hash3 := service.HashVitals(patient3)

	if hash1 != hash2 {
		t.Error("Expected identical patients to have same hash")
	}
	if hash1 == hash3 {
		t.Error("Expected different patients to have different hash")
	}
}
