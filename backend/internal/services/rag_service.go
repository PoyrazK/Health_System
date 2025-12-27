package services

import (
	"fmt"
	"math"
	"sort"
	"healthcare-backend/internal/models"
	"healthcare-backend/internal/repositories"
)

type RAGService struct {
	PatientRepo  repositories.PatientRepository
	FeedbackRepo repositories.FeedbackRepository
}

func NewRAGService(patientRepo repositories.PatientRepository, feedbackRepo repositories.FeedbackRepository) *RAGService {
	return &RAGService{
		PatientRepo:  patientRepo,
		FeedbackRepo: feedbackRepo,
	}
}

type ScoredFeedback struct {
	Feedback models.Feedback
	Score    float64 // Lower is better (distance)
}

func (s *RAGService) FindSimilarCases(patient models.PatientData) string {
	approvedFeedbacks, err := s.FeedbackRepo.GetApproved()
	if err != nil {
		return "Error fetching past cases."
	}

	var scored []ScoredFeedback

	for _, f := range approvedFeedbacks {
		// Fetch associated patient data
		histP, err := s.PatientRepo.GetByID(f.PatientID)
		if err == nil {
			// Calculate Normalized Euclidean Distance
			// Features: Age (0-100), SystolicBP (90-200), Glucose (70-300), BMI (15-50)
			
			dAge := float64(patient.Age - histP.Age) / 80.0
			dBP := float64(patient.SystolicBP - histP.SystolicBP) / 100.0
			dGluc := float64(patient.Glucose - histP.Glucose) / 200.0
			dBMI := (patient.BMI - histP.BMI) / 35.0
			
			dist := math.Sqrt(dAge*dAge + dBP*dBP + dGluc*dGluc + dBMI*dBMI)
			scored = append(scored, ScoredFeedback{Feedback: f, Score: dist})
		}
	}
	
	// Sort by nearest neighbors (lowest distance)
	sort.Slice(scored, func(i, j int) bool {
		return scored[i].Score < scored[j].Score
	})
	
	// Take top 3 relevant cases
	contextStr := "PAST SIMILAR CLINICAL CASES (RAG):\n"
	if len(scored) == 0 {
		contextStr += "None available.\n"
	}
	
	for i := 0; i < len(scored) && i < 3; i++ {
		f := scored[i].Feedback
		contextStr += fmt.Sprintf("- Similar Case (Dist: %.2f): %s\n", scored[i].Score, f.DoctorNotes)
	}
	
	return contextStr
}
