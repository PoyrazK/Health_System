# EU AI Act Compliance & Technical Implementation

## 🛡️ Overview
This document details the technical architecture implemented to ensure the Healthcare Clinical Copilot complies with the **EU AI Act**, specifically targeting "High-Risk AI Systems" in healthcare (Annex III). The system moves beyond simple prediction to become a **transparent, auditable, and resilient** platform.

---

## 🏗️ Compliance Architecture

### 1. Cryptographic Trust (Article 15 - Accuracy, Robustness and Cybersecurity)
We implemented a tamper-proof audit trail where every critical system event is cryptographically signed and chained.

*   **Technology:** SHA-256 Hashing + Ed25519 Digital Signatures.
*   **Implementation:** `AuditService` (Backend).
*   **Mechanism:**
    1.  **Chaining:** Each log entry contains the SHA-256 hash of the previous entry (`PrevHash`), forming an immutable chain similar to a blockchain.
    2.  **Non-Repudiation:** Every critical action (Doctor Approval, AI Prediction) is signed with an Ed25519 private key.
    3.  **Verification:** The `ActorSignature` and `ActorPublicKey` are stored with the log, allowing any auditor to verify the authenticity of the action.

> **API Endpoint:** `GET /api/blockchain/verify` checks the integrity of the entire chain in O(n) time.

### 2. Transparency & Explainability (Article 13)
The system is designed to be interpretable and transparent for users (doctors). It avoids the "Black Box" problem.

*   **Feature:** **Model Identity Card**.
*   **Implementation:** Frontend (`DiagnosisPanel.tsx`).
*   **Details Displayed:**
    *   **Architecture:** Explicit transparency about the models used (Gemini 1.5 + XGBoost).
    *   **Training Data:** Information about the dataset (e.g., Synthetic Records).
    *   **Known Limitations:** Explicit warnings about biases (e.g., "Lower confidence for pediatric patients"), fulfilling the legal requirement to inform users of the system's capabilities and limits.

### 3. Human Oversight (Article 14)
The system is a "Human-in-the-Loop" design. The AI never takes autonomous final actions; it acts as a Clinical Decision Support System (CDSS).

*   **Feature:** **Override Logging**.
*   **Implementation:** `FeedbackHandler` (Backend).
*   **Workflow:**
    *   If a doctor rejects an AI diagnosis (`Approved: false`), the system explicitly logs this as a `HUMAN_OVERRIDE` event.
    *   The reason for the override (e.g., "Clinical Intuition") is captured.
    *   This creates a specific audit trail for human interventions, critical for post-market monitoring.

---

## 🌐 Interoperability & Resilience (Phase 2 & 3 Features)

To demonstrate a production-ready vision, we implemented advanced integration and disaster recovery protocols.

### 4. FHIR R4 Interoperability
The system is not an isolated silo. It speaks the global language of healthcare data.

*   **Standard:** HL7 FHIR Release 4.
*   **Implementation:** `FHIRAdapter` (Backend).
*   **Capability:**
    *   Converts internal `PatientData` -> FHIR `Patient` resource.
    *   Converts AI `AssessmentResponse` -> FHIR `DiagnosticReport` resource (with LOINC coding).
    *   This allows instant integration with Epic, Cerner, or national health systems.

### 5. Decentralized Disaster Recovery
To protect audit logs against catastrophic server failures or data corruption.

*   **Technology:** IPFS (InterPlanetary File System).
*   **Implementation:** `IPFSService` (Backend).
*   **Workflow:**
    1.  The audit chain is serialized and encrypted (AES-256).
    2.  The encrypted blob is uploaded to IPFS (Simulated/Mocked for Hackathon).
    3.  A **Content Identifier (CID)** is returned and stored.
    4.  This CID ensures that the audit history can be recovered from the decentralized network even if the central server is destroyed.

---

## 📊 Technical Stack Summary

| Feature | Tech Stack | AI Act Article |
| :--- | :--- | :--- |
| **Audit Log** | Go, SHA-256, SQLite | Art. 15 (Cybersecurity) |
| **Signatures** | Ed25519 (Crypto Library) | Art. 15 (Cybersecurity) |
| **Model Card** | React, Framer Motion | Art. 13 (Transparency) |
| **Oversight** | Custom Go Structs | Art. 14 (Human Oversight) |
| **Interoperability** | FHIR R4 (JSON) | N/A (Industry Standard) |
| **Backup** | IPFS (Simulated), AES-256 | Art. 15 (Resilience) |

---

## 🚀 How to Demo

1.  **Verify Trust:** Click the "Blockchain Verified" badge on the dashboard to see signature details.
2.  **Verify Model:** Click the "Model Card" button to see transparency info.
3.  **Trigger Override:** Reject a diagnosis and check backend logs for `HUMAN_OVERRIDE`.
4.  **Check Integrity:** Call `/api/blockchain/verify` to see the chain status.
