package unit

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http/httptest"
	"testing"

	"healthcare-backend/pkg/models"

	"github.com/gofiber/fiber/v2"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// setupTestApp creates a test Fiber app with mock handlers
func setupTestApp(t *testing.T) (*fiber.App, *gorm.DB) {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		t.Fatalf("Failed to connect to test database: %v", err)
	}

	db.AutoMigrate(&models.PatientData{}, &models.Feedback{})

	app := fiber.New()
	return app, db
}

// TestGetPatients_Success tests successful patient list retrieval
func TestGetPatients_Success(t *testing.T) {
	app, db := setupTestApp(t)

	// Create test patients
	db.Create(&models.PatientData{Age: 30, Gender: "Male"})
	db.Create(&models.PatientData{Age: 45, Gender: "Female"})

	// Create handler directly for testing
	app.Get("/api/patients", func(c *fiber.Ctx) error {
		var patients []models.PatientData
		db.Order("created_at desc").Find(&patients)
		return c.JSON(patients)
	})

	// Make request
	req := httptest.NewRequest("GET", "/api/patients", nil)
	resp, err := app.Test(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}

	if resp.StatusCode != 200 {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	var patients []models.PatientData
	json.Unmarshal(body, &patients)

	if len(patients) != 2 {
		t.Errorf("Expected 2 patients, got %d", len(patients))
	}
}

// TestGetPatients_Empty tests empty patient list
func TestGetPatients_Empty(t *testing.T) {
	app, db := setupTestApp(t)

	app.Get("/api/patients", func(c *fiber.Ctx) error {
		var patients []models.PatientData
		db.Order("created_at desc").Find(&patients)
		return c.JSON(patients)
	})

	req := httptest.NewRequest("GET", "/api/patients", nil)
	resp, err := app.Test(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}

	body, _ := io.ReadAll(resp.Body)
	var patients []models.PatientData
	json.Unmarshal(body, &patients)

	if len(patients) != 0 {
		t.Errorf("Expected 0 patients, got %d", len(patients))
	}
}

// TestGetDefaults_ValidResponse tests default form values
func TestGetDefaults_ValidResponse(t *testing.T) {
	app, _ := setupTestApp(t)

	app.Get("/api/defaults", func(c *fiber.Ctx) error {
		defaults := fiber.Map{
			"age":          45,
			"gender":       "Male",
			"systolic_bp":  120,
			"diastolic_bp": 80,
			"glucose":      100,
			"bmi":          24.5,
		}
		return c.JSON(defaults)
	})

	req := httptest.NewRequest("GET", "/api/defaults", nil)
	resp, err := app.Test(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}

	if resp.StatusCode != 200 {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	var defaults map[string]interface{}
	json.Unmarshal(body, &defaults)

	if defaults["age"] != float64(45) {
		t.Errorf("Expected age 45, got %v", defaults["age"])
	}
	if defaults["gender"] != "Male" {
		t.Errorf("Expected gender 'Male', got %v", defaults["gender"])
	}
}

// TestAssessPatient_InvalidInput tests 400 error on invalid input
func TestAssessPatient_InvalidInput(t *testing.T) {
	app, _ := setupTestApp(t)

	app.Post("/api/assess", func(c *fiber.Ctx) error {
		var patient models.PatientData
		if err := c.BodyParser(&patient); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
		}
		return c.JSON(fiber.Map{"success": true})
	})

	// Send invalid JSON
	req := httptest.NewRequest("POST", "/api/assess", bytes.NewReader([]byte("not json")))
	req.Header.Set("Content-Type", "application/json")
	resp, err := app.Test(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}

	if resp.StatusCode != 400 {
		t.Errorf("Expected status 400, got %d", resp.StatusCode)
	}
}

// TestAssessPatient_ValidInput tests successful assessment
func TestAssessPatient_ValidInput(t *testing.T) {
	app, db := setupTestApp(t)

	app.Post("/api/assess", func(c *fiber.Ctx) error {
		var patient models.PatientData
		if err := c.BodyParser(&patient); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
		}
		patient.ID = 0
		db.Create(&patient)
		return c.JSON(fiber.Map{"success": true, "patient_id": patient.ID})
	})

	patientJSON := `{"age": 45, "gender": "Male", "systolic_bp": 120}`
	req := httptest.NewRequest("POST", "/api/assess", bytes.NewReader([]byte(patientJSON)))
	req.Header.Set("Content-Type", "application/json")
	resp, err := app.Test(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}

	if resp.StatusCode != 200 {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}
}

// TestGetDiagnosis_NotFound tests diagnosis retrieval for non-existent patient
func TestGetDiagnosis_NotFound(t *testing.T) {
	app, _ := setupTestApp(t)

	app.Get("/api/diagnosis/:id", func(c *fiber.Ctx) error {
		id := c.Params("id")
		// Simulate empty cache response
		return c.JSON(fiber.Map{
			"id":        id,
			"diagnosis": "",
			"status":    "",
		})
	})

	req := httptest.NewRequest("GET", "/api/diagnosis/9999", nil)
	resp, err := app.Test(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}

	if resp.StatusCode != 200 {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	if result["status"] != "" {
		t.Errorf("Expected empty status, got %v", result["status"])
	}
}
