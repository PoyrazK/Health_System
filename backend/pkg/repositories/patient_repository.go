package repositories

import (
	"healthcare-backend/pkg/models"

	"gorm.io/gorm"
)

// PatientRepository abstracts database operations for patients
type PatientRepository interface {
	Create(patient *models.PatientData) error
	GetByID(id uint) (*models.PatientData, error)
	GetAll() ([]models.PatientData, error)
}

type patientRepository struct {
	db *gorm.DB
}

// NewPatientRepository creates a new instance of PatientRepository
func NewPatientRepository(db *gorm.DB) PatientRepository {
	return &patientRepository{db: db}
}

func (r *patientRepository) Create(patient *models.PatientData) error {
	return r.db.Create(patient).Error
}

func (r *patientRepository) GetByID(id uint) (*models.PatientData, error) {
	var patient models.PatientData
	if err := r.db.First(&patient, id).Error; err != nil {
		return nil, err
	}
	return &patient, nil
}

func (r *patientRepository) GetAll() ([]models.PatientData, error) {
	var patients []models.PatientData
	if err := r.db.Order("created_at desc").Find(&patients).Error; err != nil {
		return nil, err
	}
	return patients, nil
}
