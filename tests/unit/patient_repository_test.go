package unit

import (
	"healthcare-backend/pkg/models"
	"healthcare-backend/pkg/repositories"
	"testing"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// setupTestDB creates an in-memory SQLite database for testing
func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		t.Fatalf("Failed to connect to test database: %v", err)
	}

	err = db.AutoMigrate(&models.PatientData{})
	if err != nil {
		t.Fatalf("Failed to migrate test database: %v", err)
	}

	return db
}

// TestPatientRepo_Create tests patient creation
func TestPatientRepo_Create(t *testing.T) {
	db := setupTestDB(t)
	repo := repositories.NewPatientRepository(db)

	patient := &models.PatientData{
		Age:        45,
		Gender:     "Male",
		SystolicBP: 120,
		DiastolicBP: 80,
		Glucose:    100,
		BMI:        24.5,
	}

	err := repo.Create(patient)
	if err != nil {
		t.Fatalf("Failed to create patient: %v", err)
	}

	if patient.ID == 0 {
		t.Error("Expected patient ID to be set after creation")
	}
}

// TestPatientRepo_GetByID tests retrieval by ID
func TestPatientRepo_GetByID(t *testing.T) {
	db := setupTestDB(t)
	repo := repositories.NewPatientRepository(db)

	patient := &models.PatientData{
		Age:    30,
		Gender: "Female",
	}
	repo.Create(patient)

	retrieved, err := repo.GetByID(patient.ID)
	if err != nil {
		t.Fatalf("Failed to get patient by ID: %v", err)
	}

	if retrieved.Age != 30 {
		t.Errorf("Expected age 30, got %d", retrieved.Age)
	}
	if retrieved.Gender != "Female" {
		t.Errorf("Expected gender 'Female', got '%s'", retrieved.Gender)
	}
}

// TestPatientRepo_GetByID_NotFound tests retrieval of non-existent patient
func TestPatientRepo_GetByID_NotFound(t *testing.T) {
	db := setupTestDB(t)
	repo := repositories.NewPatientRepository(db)

	_, err := repo.GetByID(9999)
	if err == nil {
		t.Error("Expected error when getting non-existent patient, got nil")
	}
}

// TestPatientRepo_GetAll tests listing all patients
func TestPatientRepo_GetAll(t *testing.T) {
	db := setupTestDB(t)
	repo := repositories.NewPatientRepository(db)

	patients := []models.PatientData{
		{Age: 25, Gender: "Male"},
		{Age: 35, Gender: "Female"},
		{Age: 45, Gender: "Male"},
	}

	for i := range patients {
		repo.Create(&patients[i])
	}

	all, err := repo.GetAll()
	if err != nil {
		t.Fatalf("Failed to get all patients: %v", err)
	}

	if len(all) != 3 {
		t.Errorf("Expected 3 patients, got %d", len(all))
	}
}

// TestPatientRepo_GetAll_Empty tests listing when no patients exist
func TestPatientRepo_GetAll_Empty(t *testing.T) {
	db := setupTestDB(t)
	repo := repositories.NewPatientRepository(db)

	all, err := repo.GetAll()
	if err != nil {
		t.Fatalf("Failed to get all patients: %v", err)
	}

	if len(all) != 0 {
		t.Errorf("Expected 0 patients, got %d", len(all))
	}
}
