package blockchain

import (
	"log"
	"sync"
)

type Blockchain struct {
	Chain []Block
	mu    sync.RWMutex
}

var GlobalChain *Blockchain

// InitBlockchain initializes the singleton chain
func InitBlockchain() {
	GlobalChain = &Blockchain{
		Chain: []Block{GenesisBlock()},
	}
	log.Println("🔗 Blockchain Initialized: Genesis Block created.")
}

// AddBlock adds a new block to the chain securely
func (bc *Blockchain) AddBlock(data interface{}) Block {
	bc.mu.Lock()
	defer bc.mu.Unlock()

	prevBlock := bc.Chain[len(bc.Chain)-1]
	newBlock := CreateBlock(prevBlock, data)
	
	// In a real PoW, we'd mine here. For low-latency clinical use, we accept immediately
	// but we could enforce basic difficulty if required.
	
	bc.Chain = append(bc.Chain, newBlock)
	return newBlock
}

// IsChainValid verifies the integrity of the ledger
func (bc *Blockchain) IsChainValid() bool {
	bc.mu.RLock()
	defer bc.mu.RUnlock()

	for i := 1; i < len(bc.Chain); i++ {
		currentBlock := bc.Chain[i]
		prevBlock := bc.Chain[i-1]

		// 1. Verify data integrity (Hash match)
		if currentBlock.Hash != currentBlock.CalculateHash() {
			return false
		}

		// 2. Verify chain continuity (PreviousHash match)
		if currentBlock.PreviousHash != prevBlock.Hash {
			return false
		}
	}
	return true
}

// GetChain returns a copy of the chain (thread-safe)
func (bc *Blockchain) GetChain() []Block {
	bc.mu.RLock()
	defer bc.mu.RUnlock()
	
	// Return copy to prevent external mutation
	copied := make([]Block, len(bc.Chain))
	copy(copied, bc.Chain)
	return copied
}
