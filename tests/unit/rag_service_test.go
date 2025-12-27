package unit

import (
	"healthcare-backend/pkg/models"
	"healthcare-backend/pkg/services"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// -- Mocks --

type MockPatientRepo struct {
	mock.Mock
}

func (m *MockPatientRepo) Create(p *models.PatientData) error {
	args := m.Called(p)
	return args.Error(0)
}

func (m *MockPatientRepo) GetByID(id uint) (*models.PatientData, error) {
	args := m.Called(id)
	if p, ok := args.Get(0).(*models.PatientData); ok {
		return p, args.Error(1)
	}
	return nil, args.Error(1)
}

func (m *MockPatientRepo) GetAll() ([]models.PatientData, error) {
	args := m.Called()
	return args.Get(0).([]models.PatientData), args.Error(1)
}

type MockFeedbackRepo struct {
	mock.Mock
}

func (m *MockFeedbackRepo) Create(f *models.Feedback) error {
	args := m.Called(f)
	return args.Error(0)
}

func (m *MockFeedbackRepo) GetApproved() ([]models.Feedback, error) {
	args := m.Called()
	return args.Get(0).([]models.Feedback), args.Error(1)
}

// -- Tests --

func TestFindSimilarCases(t *testing.T) {
	// Setup Mocks
	mockP := new(MockPatientRepo)
	mockF := new(MockFeedbackRepo)
	rag := services.NewRAGService(mockP, mockF)

	// Mock Data
	currentPatient := models.PatientData{
		Age: 45, SystolicBP: 120, Glucose: 100, BMI: 25,
	}

	histPatient := models.PatientData{
		ID: 1, Age: 46, SystolicBP: 122, Glucose: 105, BMI: 25.5,
	}

	feedbacks := []models.Feedback{
		{PatientID: 1, DoctorApproved: true, DoctorNotes: "Patient responded well to ACE inhibitors."},
	}

	// Expectations
	mockF.On("GetApproved").Return(feedbacks, nil)
	mockP.On("GetByID", uint(1)).Return(&histPatient, nil)

	// Execute
	result := rag.FindSimilarCases(currentPatient)

	// Assertions
	assert.Contains(t, result, "PAST SIMILAR CLINICAL CASES")
	assert.Contains(t, result, "responded well to ACE inhibitors")
	assert.Contains(t, result, "Dist:") // Should have distance score
	
	mockF.AssertExpectations(t)
	mockP.AssertExpectations(t)
}

func TestFindSimilarCases_NoFeedbacks(t *testing.T) {
	mockP := new(MockPatientRepo)
	mockF := new(MockFeedbackRepo)
	rag := services.NewRAGService(mockP, mockF)

	mockF.On("GetApproved").Return([]models.Feedback{}, nil)

	result := rag.FindSimilarCases(models.PatientData{})

	assert.Contains(t, result, "None available")
}
