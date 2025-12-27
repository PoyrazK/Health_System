package adapters

import (
	"fmt"
	"strings"
	"time"

	"healthcare-backend/pkg/models"
)

// FHIRAdapter handles conversion between internal models and FHIR R4 resources
type FHIRAdapter struct{}

// NewFHIRAdapter creates a new instance
func NewFHIRAdapter() *FHIRAdapter {
	return &FHIRAdapter{}
}

// ToFHIRPatient converts our PatientData to a FHIR Patient resource (JSON map)
func (f *FHIRAdapter) ToFHIRPatient(p models.PatientData) map[string]interface{} {
	// Calculate approx birth year from age
	birthYear := time.Now().Year() - p.Age

	return map[string]interface{}{
		"resourceType": "Patient",
		"id":           fmt.Sprintf("pat-%d", p.ID),
		"active":       true,
		"identifier": []map[string]string{
			{
				"use":    "official",
				"system": "http://hospital.example.org/patients",
				"value":  fmt.Sprintf("%d", p.ID),
			},
		},
		"gender":    strings.ToLower(p.Gender),
		"birthDate": fmt.Sprintf("%d-01-01", birthYear),
		"extension": []map[string]interface{}{
			{
				"url":       "http://fhir.example.org/StructureDefinition/smoking-status",
				"valueCode": p.Smoking,
			},
		},
	}
}

// ToFHIRDiagnosticReport converts our AssessmentResponse to FHIR DiagnosticReport
// demonstrating interoperability for the hackathon
func (f *FHIRAdapter) ToFHIRDiagnosticReport(assessment models.FullAssessmentResponse) map[string]interface{} {
	return map[string]interface{}{
		"resourceType": "DiagnosticReport",
		"id":           fmt.Sprintf("rpt-%d", assessment.ID),
		"status":       "final",
		"code": map[string]interface{}{
			"coding": []map[string]string{
				{
					"system":  "http://loinc.org",
					"code":    "54531-9",
					"display": "Risk assessment",
				},
			},
		},
		"subject": map[string]string{
			"reference": fmt.Sprintf("Patient/pat-%d", assessment.Patient.ID),
		},
		"effectiveDateTime": time.Now().UTC().Format(time.RFC3339),
		"conclusion":        assessment.Diagnosis,
		"result": []map[string]interface{}{
			{
				"display": fmt.Sprintf("Heart Risk: %.1f%%", assessment.Risks.HeartRisk),
			},
			{
				"display": fmt.Sprintf("Urgency Level: %d", assessment.Urgency.UrgencyLevel),
			},
		},
	}
}
