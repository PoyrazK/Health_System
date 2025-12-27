package blockchain

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"
)

type Block struct {
	Index        int64     `json:"index"`
	Timestamp    time.Time `json:"timestamp"`
	Data         interface{} `json:"data"` // Generic data (PredictRequest, Feedback, etc.)
	PreviousHash string    `json:"previous_hash"`
	Hash         string    `json:"hash"`
	Nonce        int       `json:"nonce"` // For basic proof of work (if needed) or simple sequencing
}

// CalculateHash creates a SHA-256 hash of the block content
func (b *Block) CalculateHash() string {
	dataBytes, _ := json.Marshal(b.Data)
	record := fmt.Sprintf("%d%s%s%s%d", b.Index, b.Timestamp.String(), string(dataBytes), b.PreviousHash, b.Nonce)
	
	h := sha256.New()
	h.Write([]byte(record))
	hashed := h.Sum(nil)
	
	return hex.EncodeToString(hashed)
}

// CreateBlock generates a new block
func CreateBlock(prevBlock Block, data interface{}) Block {
	newBlock := Block{
		Index:        prevBlock.Index + 1,
		Timestamp:    time.Now(),
		Data:         data,
		PreviousHash: prevBlock.Hash,
		Nonce:        0,
	}
	newBlock.Hash = newBlock.CalculateHash()
	return newBlock
}

// GenesisBlock creates the first block in the chain
func GenesisBlock() Block {
	b := Block{
		Index:        0,
		Timestamp:    time.Now(),
		Data:         "Genisis Block - Clinical Copilot High-Performance Ledger",
		PreviousHash: "0",
		Nonce:        0,
	}
	b.Hash = b.CalculateHash()
	return b
}
