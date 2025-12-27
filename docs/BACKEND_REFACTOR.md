# Backend Architecture Refactoring (Phase 7-8)

This document details the architectural improvements made to the Go backend to address technical debt, improve testability, and ensure regulatory compliance.

## 1. Modular Configuration
**Path**: `internal/config/config.go`
- **Why**: Hardcoded values (ports, DB paths) prevented easy environment switching.
- **Solution**: A centralized `Config` struct that loads from `.env` files using `godotenv`.
- **Key Fields**:
  - `ENABLE_AUDIT_LOG`: Feature flag for blockchain logging.
  - `ML_SERVICE_URL`: Dynamic URL for the Python ML API.

## 2. Repository Pattern
**Path**: `internal/repositories/`
- **Why**: `RAGService` and Handlers were tightly coupled to GORM/SQLite, making them impossible to unit test without a real DB.
- **Solution**: Abstracted data access behind interfaces:
  - `PatientRepository`
  - `FeedbackRepository`
- **Benefit**: We can now inject mock repositories into services for testing (see `internal/services/rag_service_test.go`).

## 3. Cryptographic Audit Trail (SaMD Compliance)
**Path**: `internal/services/audit_service.go`
- **Why**: FDA/MDR regulations require proof that AI decisions haven't been tampered with.
- **Solution**: A SHA-256 hash-chain (blockchain-lite) stored locally.
- **Mechanism**:
  - Each log entry contains `PrevHash`.
  - `CurrentHash = SHA256(Timestamp + EventType + Payload + PrevHash)`
  - If a row is deleted or modified, the entire subsequent chain becomes invalid.

## 4. Middleware & Safety
- **Validation**: `internal/middleware/validator.go` using `go-playground/validator` ensuring clinical values (e.g., BP > 50) are respected.
- **Error Handling**: Global middleware catches panics and returns standard JSON errors.
- **Graceful Shutdown**: The server waits for active requests to finish before killing the process on SIGTERM.
