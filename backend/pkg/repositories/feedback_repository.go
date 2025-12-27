package repositories

import (
	"healthcare-backend/pkg/models"

	"gorm.io/gorm"
)

// FeedbackRepository abstracts database operations for feedback
type FeedbackRepository interface {
	Create(feedback *models.Feedback) error
	GetApproved() ([]models.Feedback, error)
}

type feedbackRepository struct {
	db *gorm.DB
}

// NewFeedbackRepository creates a new instance of FeedbackRepository
func NewFeedbackRepository(db *gorm.DB) FeedbackRepository {
	return &feedbackRepository{db: db}
}

func (r *feedbackRepository) Create(feedback *models.Feedback) error {
	return r.db.Create(feedback).Error
}

func (r *feedbackRepository) GetApproved() ([]models.Feedback, error) {
	var feedbacks []models.Feedback
	err := r.db.Where("doctor_approved = ?", true).Find(&feedbacks).Error
	return feedbacks, err
}
