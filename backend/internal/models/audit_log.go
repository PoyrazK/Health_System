package models

import "time"

// AuditLog represents a single entry in the cryptographic audit chain.
// Each entry contains the hash of the previous entry, making any tampering detectable.
type AuditLog struct {
	ID            uint      `gorm:"primaryKey" json:"id"`
	Timestamp     time.Time `json:"timestamp"`
	EventType     string    `json:"event_type"`     // AI_PREDICTION, DOCTOR_FEEDBACK, PATIENT_CREATED, etc.
	PatientIDHash string    `json:"patient_id_hash"` // SHA-256 hash of patient ID for privacy
	PayloadHash   string    `json:"payload_hash"`    // SHA-256 hash of the full event payload
	PrevHash      string    `json:"prev_hash"`       // Hash of the previous audit entry (chain link)
	CurrentHash   string    `json:"current_hash"`    // Hash of this entire entry
	ActorID       string    `json:"actor_id"`        // Who triggered this event (e.g., "system", "doctor_123")
}
