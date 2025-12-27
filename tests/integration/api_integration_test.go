package integration

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"testing"
	"time"
)

const (
	BackendURL = "http://localhost:3000"
	MLServiceURL = "http://localhost:8000"
)

// isServiceRunning checks if a service is available
func isServiceRunning(url string) bool {
	client := &http.Client{Timeout: 2 * time.Second}
	resp, err := client.Get(url + "/health")
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	return resp.StatusCode == 200
}

// TestHealthEndpoint tests the backend health endpoint
func TestHealthEndpoint(t *testing.T) {
	if !isServiceRunning(BackendURL) {
		t.Skip("Backend not running, skipping integration test")
	}

	resp, err := http.Get(BackendURL + "/health")
	if err != nil {
		t.Fatalf("Health check failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	t.Logf("Health response: %s", string(body))
}

// TestMLServiceHealth tests the ML service health
func TestMLServiceHealth(t *testing.T) {
	if !isServiceRunning(MLServiceURL) {
		t.Skip("ML Service not running, skipping integration test")
	}

	resp, err := http.Get(MLServiceURL + "/health")
	if err != nil {
		t.Fatalf("ML health check failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}
}

// TestGetPatients_Integration tests fetching patients from running backend
func TestGetPatients_Integration(t *testing.T) {
	if !isServiceRunning(BackendURL) {
		t.Skip("Backend not running, skipping integration test")
	}

	resp, err := http.Get(BackendURL + "/api/patients")
	if err != nil {
		t.Fatalf("Get patients failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	t.Logf("Patients response: %s", string(body)[:min(len(body), 200)])
}

// TestFullAssessmentFlow tests complete patient assessment pipeline
func TestFullAssessmentFlow(t *testing.T) {
	if !isServiceRunning(BackendURL) || !isServiceRunning(MLServiceURL) {
		t.Skip("Services not running, skipping integration test")
	}

	// Create patient data
	patient := map[string]interface{}{
		"age":          45,
		"gender":       "Male",
		"systolic_bp":  130,
		"diastolic_bp": 85,
		"glucose":      110,
		"bmi":          26.5,
		"cholesterol":  210,
		"heart_rate":   75,
		"smoking":      "No",
		"alcohol":      "No",
		"medications":  "Lisinopril",
	}

	payloadBytes, _ := json.Marshal(patient)

	resp, err := http.Post(BackendURL+"/api/assess", "application/json", bytes.NewReader(payloadBytes))
	if err != nil {
		t.Fatalf("Assessment request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		t.Fatalf("Expected status 200, got %d: %s", resp.StatusCode, string(body))
	}

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	// Verify response structure
	if result["risks"] == nil {
		t.Error("Expected risks in response")
	}
	if result["patient"] == nil {
		t.Error("Expected patient in response")
	}
	if result["diagnosis_status"] != "pending" {
		t.Logf("Diagnosis status: %v", result["diagnosis_status"])
	}

	t.Logf("Assessment completed with patient ID: %v", result["id"])
}

// TestDiagnosisPoll tests polling for async diagnosis completion
func TestDiagnosisPoll(t *testing.T) {
	if !isServiceRunning(BackendURL) {
		t.Skip("Backend not running, skipping integration test")
	}

	// First create an assessment
	patient := map[string]interface{}{
		"age":          50,
		"gender":       "Female",
		"systolic_bp":  145,
		"diastolic_bp": 90,
		"glucose":      125,
		"bmi":          28.0,
	}

	payloadBytes, _ := json.Marshal(patient)
	assessResp, err := http.Post(BackendURL+"/api/assess", "application/json", bytes.NewReader(payloadBytes))
	if err != nil {
		t.Fatalf("Assessment failed: %v", err)
	}
	assessBody, _ := io.ReadAll(assessResp.Body)
	assessResp.Body.Close()

	var assessResult map[string]interface{}
	json.Unmarshal(assessBody, &assessResult)

	patientID := assessResult["id"]
	if patientID == nil {
		t.Fatal("No patient ID returned from assessment")
	}

	// Poll for diagnosis (up to 30 seconds)
	client := &http.Client{Timeout: 5 * time.Second}
	var finalStatus string

	for i := 0; i < 15; i++ {
		time.Sleep(2 * time.Second)

		diagResp, err := client.Get(BackendURL + "/api/diagnosis/" + fmt.Sprintf("%.0f", patientID.(float64)))
		if err != nil {
			continue
		}

		diagBody, _ := io.ReadAll(diagResp.Body)
		diagResp.Body.Close()

		var diagResult map[string]interface{}
		json.Unmarshal(diagBody, &diagResult)

		finalStatus = diagResult["status"].(string)
		if finalStatus == "ready" || finalStatus == "error" {
			t.Logf("Diagnosis completed with status: %s", finalStatus)
			break
		}
	}

	if finalStatus == "" {
		t.Log("Diagnosis polling timed out (expected in some environments)")
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
