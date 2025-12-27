package handlers

import (
	"healthcare-backend/pkg/services"
	"time"

	"github.com/gofiber/fiber/v2"
)

type BlockchainHandler struct {
	Audit *services.AuditService
	IPFS  *services.IPFSService
}

func NewBlockchainHandler(audit *services.AuditService, ipfs *services.IPFSService) *BlockchainHandler {
	return &BlockchainHandler{Audit: audit, IPFS: ipfs}
}

// VerifyChain checks the cryptographic integrity of the entire audit log
// GET /api/blockchain/verify
func (h *BlockchainHandler) VerifyChain(c *fiber.Ctx) error {
	isValid, blockCount, err := h.Audit.VerifyChain()
	
	status := "secure"
	if !isValid {
		status = "compromised"
	}

	response := fiber.Map{
		"valid":         isValid,
		"block_count":   blockCount,
		"status":        status,
		"last_verified": time.Now().UTC(),
		"node_id":       "NODE_GEMINI_01", // Mock node ID
		"algorithm":     "SHA-256 + Ed25519",
	}

	if err != nil {
		response["error"] = err.Error()
		return c.Status(500).JSON(response)
	}

	return c.JSON(response)
}

// BackupChain exports the current chain and uploads it to IPFS (Simulated)
// POST /api/blockchain/backup
func (h *BlockchainHandler) BackupChain(c *fiber.Ctx) error {
	// 1. Export Chain Data
	chainData, err := h.Audit.ExportChain()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Failed to export chain"})
	}

	// 2. Backup to IPFS
	cid, err := h.IPFS.BackupChain(chainData)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "IPFS upload failed"})
	}

	return c.JSON(fiber.Map{
		"status":      "backed_up",
		"ipfs_cid":    cid,
		"timestamp":   time.Now().UTC(),
		"block_count": len(chainData) / 200, // Rough estimate or pass real count
		"provider":    "IPFS (Decentralized)",
	})
}
