package services

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"healthcare-backend/pkg/blockchain"
	"healthcare-backend/pkg/models"

	"gorm.io/gorm"
)

type AuditService struct {
	DB       *gorm.DB
	mu       sync.Mutex
	lastHash string
}

func NewAuditService(db *gorm.DB) *AuditService {
	// Initialize the high-performance blockchain ledger
	if blockchain.GlobalChain == nil {
		blockchain.InitBlockchain()
	}

	// Auto-migrate the AuditLog table
	db.AutoMigrate(&models.AuditLog{})

	// Get the last hash from the chain (if any)
	var lastEntry models.AuditLog
	lastHash := "GENESIS" // Genesis block has no previous hash
	if err := db.Order("id DESC").First(&lastEntry).Error; err == nil {
		lastHash = lastEntry.CurrentHash
	}

	return &AuditService{
		DB:       db,
		lastHash: lastHash,
	}
}

// hashString creates a SHA-256 hash of the input string
func hashString(s string) string {
	h := sha256.Sum256([]byte(s))
	return hex.EncodeToString(h[:])
}

// LogEvent creates a new audit log entry chained to the previous one
func (a *AuditService) LogEvent(eventType string, patientID uint, payload interface{}, actorID string) error {
	a.mu.Lock()
	defer a.mu.Unlock()

	// Hash the patient ID for privacy
	patientIDHash := hashString(fmt.Sprintf("%d", patientID))

	// Hash the payload
	payloadBytes, _ := json.Marshal(payload)
	payloadHash := hashString(string(payloadBytes))

	// Create the entry
	entry := models.AuditLog{
		Timestamp:     time.Now().UTC(),
		EventType:     eventType,
		PatientIDHash: patientIDHash,
		PayloadHash:   payloadHash,
		PrevHash:      a.lastHash,
		ActorID:       actorID,
	}

	// Calculate the current hash (hash of entire entry except CurrentHash)
	entryData := fmt.Sprintf("%s|%s|%s|%s|%s|%s",
		entry.Timestamp.Format(time.RFC3339Nano),
		entry.EventType,
		entry.PatientIDHash,
		entry.PayloadHash,
		entry.PrevHash,
		entry.ActorID,
	)
	entry.CurrentHash = hashString(entryData)

	// Save to database
	if err := a.DB.Create(&entry).Error; err != nil {
		log.Printf("❌ Audit Log Error: %v", err)
		return err
	}

	// Update the chain
	a.lastHash = entry.CurrentHash

	// --- BLOCKCHAIN INTEGRATION ---
	// Also write to the in-memory high-performance ledger
	blockPayload := map[string]interface{}{
		"event_type": eventType,
		"entity_id":  patientID,
		"data_hash":  payloadHash,
		"timestamp":  entry.Timestamp,
		"actor":      actorID,
	}
	blockchain.GlobalChain.AddBlock(blockPayload)
	// -------------------------------

	log.Printf("📜 Audit Log: [%s] Patient %s | Hash: %s...%s",
		eventType,
		patientIDHash[:8],
		entry.CurrentHash[:8],
		entry.CurrentHash[len(entry.CurrentHash)-8:],
	)

	return nil
}

// VerifyChain checks if the entire audit chain is intact (no tampering)
func (a *AuditService) VerifyChain() (bool, int, error) {
	var entries []models.AuditLog
	if err := a.DB.Order("id ASC").Find(&entries).Error; err != nil {
		return false, 0, err
	}

	if len(entries) == 0 {
		return true, 0, nil
	}

	prevHash := "GENESIS"
	for i, entry := range entries {
		// Verify the previous hash matches
		if entry.PrevHash != prevHash {
			return false, i, fmt.Errorf("chain broken at entry %d: expected prev_hash %s, got %s", i, prevHash, entry.PrevHash)
		}

		// Recalculate the current hash to verify integrity
		entryData := fmt.Sprintf("%s|%s|%s|%s|%s|%s",
			entry.Timestamp.Format(time.RFC3339Nano),
			entry.EventType,
			entry.PatientIDHash,
			entry.PayloadHash,
			entry.PrevHash,
			entry.ActorID,
		)
		expectedHash := hashString(entryData)

		if entry.CurrentHash != expectedHash {
			return false, i, fmt.Errorf("hash mismatch at entry %d: expected %s, got %s", i, expectedHash, entry.CurrentHash)
		}

		prevHash = entry.CurrentHash
	}

	return true, len(entries), nil
}
