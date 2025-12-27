package models

import (
	"time"

	"gorm.io/gorm"
)

// WiFiPoseEvent represents a WiFi-based pose detection event
type WiFiPoseEvent struct {
	gorm.Model
	PatientID  *uint   `json:"patient_id" gorm:"index"`
	RoomID     string  `json:"room_id" gorm:"index;size:50"`
	EventType  string  `json:"event_type" gorm:"size:50;index"` // pose, fall, activity
	PersonID   string  `json:"person_id" gorm:"size:50"`
	Activity   string  `json:"activity" gorm:"size:50"`
	Confidence float64 `json:"confidence"`
	Zone       string  `json:"zone" gorm:"size:50"`
	PoseData   string  `json:"pose_data" gorm:"type:text"` // JSON keypoints
	Timestamp  time.Time `json:"timestamp" gorm:"index"`
}

// FallAlert represents a fall detection alert
type FallAlert struct {
	gorm.Model
	EventID        uint       `json:"event_id" gorm:"index"`
	WiFiPoseEvent  *WiFiPoseEvent `json:"wifi_pose_event" gorm:"foreignKey:EventID"`
	Severity       string     `json:"severity" gorm:"size:20"` // critical, warning
	Confidence     float64    `json:"confidence"`
	PersonID       string     `json:"person_id" gorm:"size:50"`
	RoomID         string     `json:"room_id" gorm:"size:50"`
	Acknowledged   bool       `json:"acknowledged" gorm:"default:false"`
	AcknowledgedBy *uint      `json:"acknowledged_by"`
	AcknowledgedAt *time.Time `json:"acknowledged_at"`
}

// TableName for WiFiPoseEvent
func (WiFiPoseEvent) TableName() string {
	return "wifi_pose_events"
}

// TableName for FallAlert
func (FallAlert) TableName() string {
	return "fall_alerts"
}
