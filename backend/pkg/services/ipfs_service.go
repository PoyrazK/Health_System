package services

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"io"
	"log"
	"time"
)

// IPFSService handles decentralized storage backups
type IPFSService struct {
	// In a real app, we would hold the IPFS shell client here
	// shell *shell.Shell
	EncryptionKey []byte
}

func NewIPFSService() *IPFSService {
	// Generate a random encryption key for this session
	key := make([]byte, 32)
	if _, err := io.ReadFull(rand.Reader, key); err != nil {
		log.Printf("⚠️ Failed to generate IPFS encryption key: %v", err)
	}
	return &IPFSService{EncryptionKey: key}
}

// BackupChain encrypts the audit chain and uploads it to IPFS (Simulated)
// Returns the CID (Content Identifier)
func (s *IPFSService) BackupChain(chainData []byte) (string, error) {
	// 1. Encrypt Data (AES-GCM)
	encrypted, err := s.encrypt(chainData)
	if err != nil {
		return "", err
	}

	// 2. Upload to IPFS (Simulated)
	// In a real app: cid, err := s.shell.Add(bytes.NewReader(encrypted))
	
	// Simulate network latency
	time.Sleep(100 * time.Millisecond)

	// Generate a deterministic fake CID based on content hash
	// Real IPFS CIDs look like "QmX..."
	hash := sha256.Sum256(encrypted)
	cid := fmt.Sprintf("Qm%s", base64.RawURLEncoding.EncodeToString(hash[:]))[:46] // Truncate to typical CID length

	log.Printf("☁️ IPFS Backup: Uploaded %d bytes (encrypted) -> CID: %s", len(encrypted), cid)
	
	return cid, nil
}

func (s *IPFSService) encrypt(data []byte) ([]byte, error) {
	block, err := aes.NewCipher(s.EncryptionKey)
	if err != nil {
		return nil, err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, err
	}

	return gcm.Seal(nonce, nonce, data, nil), nil
}
