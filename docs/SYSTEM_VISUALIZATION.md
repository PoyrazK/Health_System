# 🔍 System Architecture Visualization

This document visualizes the **Clinical Copilot v3.1** technical architecture, illustrating how the Next.js Frontend, Go Backend, Python ML Engine, and Compliance Services interact.

---

## 1. System Landscape (High-Level)

The high-level view of how Clinical Copilot integrates with the healthcare ecosystem.

```mermaid
C4Context
    title System Context Diagram - Clinical Copilot v3.1

    Person(doctor, "Clinician", "Doctor or Medical Professional using the system")
    
    System_Boundary(clinical_copilot, "Clinical Copilot System") {
        System(webapp, "High-Performance Dashboard", "Next.js UI for patient assessment and risk visualization")
        System(backend, "Core Orchestrator", "Go/Fiber Backend managing logic, state, and security")
        System(ai_core, "AI Intelligence Layer", "Python/FastAPI handling ML models and LLM reasoning")
    }

    System_Ext(gemini, "Google Gemini API", "LLM for Clinical Reasoning & Chat")
    System_Ext(fhir_sys, "Hospital EHR (Simulated)", "External Electronic Health Records via FHIR R4")
    System_Ext(ipfs, "IPFS Network", "Decentralized Disaster Recovery Storage")

    Rel(doctor, webapp, "Views Insights & Inputs Vitals", "HTTPS/WebSocket")
    Rel(webapp, backend, "API Calls", "JSON/REST")
    Rel(backend, ai_core, "Predict & Diagnose", "HTTP/RPC")
    
    Rel(ai_core, gemini, "Generates Analysis", "HTTPS")
    Rel(backend, fhir_sys, "Syncs Patient Data", "FHIR/JSON")
    Rel(backend, ipfs, "Backs up Audit Logs", "Encrypted Blob")
    
    UpdateRelStyle(doctor, webapp, $textColor="blue", $lineColor="blue")
    UpdateRelStyle(backend, ai_core, $textColor="red", $lineColor="red")
```

---

## 2. Container Architecture (Detailed Tech Stack)

A deep dive into the deployed containers, protocols, and data stores.

```mermaid
C4Container
    title Container Diagram - Microservices & Data

    Container(frontend, "Frontend App", "Next.js, Tailwind, Framer Motion", "Real-time Clinical Dashboard")
    
    Container_Boundary(backend_scope, "Backend Services") {
        Container(go_api, "API Gateway & Logic", "Go, Fiber v2", "Orchestrates reqs, auth, and business logic")
        Container(audit_svc, "Audit & Compliance", "Go, Ed25519", "Signs and chains critical events")
        Container(websocket, "Real-Time Hub", "Go, WS", "Pushes alerts and diagnosis to UI")
    }

    Container_Boundary(ml_scope, "AI & ML Services") {
        Container(ml_api, "ML API", "Python, FastAPI", "Serves XGBoost/RF models & SHAP values")
        Container(llm_worker, "LLM Worker", "Python, Async", "Interacts with Gemini for reasoning")
    }

    ContainerDb(postgres, "Primary DB", "PostgreSQL", "Patient Data, Feedbacks, Users")
    ContainerDb(redis, "Cache & PubSub", "Redis", "Session, Diagnosis Cache, WS Channels")
    ContainerDb(nats, "Message Queue", "NATS", "Async Tasks, Decoupling Services")
    
    Rel(frontend, go_api, "REST API", "HTTPS/JSON")
    Rel(frontend, websocket, "Live Updates", "WSS")
    
    Rel(go_api, postgres, "Reads/Writes", "TCP/5432")
    Rel(go_api, redis, "Caches State", "TCP/6379")
    Rel(go_api, nats, "Publishes Jobs", "TCP/4222")
    
    Rel(nats, llm_worker, "Consumes Jobs", "JetStream")
    Rel(llm_worker, redis, "Writes Result", "TCP/6379")
    
    Rel(go_api, ml_api, "Sync Prediction", "HTTP/JSON")
    
    Rel(audit_svc, postgres, "Stores Hash Chain", "SQL")
```

---

## 3. Critical Process Flows

### A. The "Zero-Block" Diagnosis Pipeline

How the system delivers instant risk scores while processing complex reasoning in the background.

```mermaid
sequenceDiagram
    autonumber
    participant D as Doctor (UI)
    participant B as Go Backend
    participant ML as ML Service (Py)
    participant Q as NATS Queue
    participant W as LLM Worker
    participant R as Redis
    
    note over D, B: Step 1: Instant Triage
    D->>B: POST /assess (Patient Data)
    B->>ML: Predict Risks (XGBoost)
    ML-->>B: Risks + SHAP Values (50ms)
    B-->>D: Return Risk JSON (Immediate)
    
    note over B, W: Step 2: Async Reasoning
    B->>Q: Publish "assess.requested"
    Q->>W: Consume Event
    W->>W: Fetch RAG Context
    W->>W: Call Gemini 1.5 Flash
    W->>R: Store Diagnosis in Cache
    R-->>D: WebSocket Push "Diagnosis Ready"
```

### B. EU AI Act - Audit & Integrity Flow

How we ensure non-repudiation and tamper-proof logging.

```mermaid
flowchart LR
    subgraph "Action Origin"
        A[Doctor Decision] -->|Approve/Reject| B(Backend Handler)
    end
    
    subgraph "Cryptographic Layer"
        B --> C{Sign Event}
        C -->|Ed25519 Key| D[Generate Signature]
    end
    
    subgraph "Audit Chain"
        D --> E[Fetch Previous Hash]
        E --> F[Create New Block]
        F -->|SHA-256| G[Next Hash]
        G --> H[(PostgreSQL Audit Table)]
    end
    
    subgraph "Disaster Recovery"
        H -.->|Batch Backup| I[AES-256 Encryption]
        I -.-> J((IPFS Network))
    end
    
    style C fill:#f9f,stroke:#333
    style J fill:#bbf,stroke:#333
```

---

## 4. Network & Security Topology

Physical deployment view (Docker Compose / Cloud).

```mermaid
graph TB
    subgraph "Public Internet"
        Client[Client Browser]
    end
    
    subgraph "Private Network (Docker Bridge)"
        RP[Reverse Proxy / LB]
        
        subgraph "App Layer"
            UI[Next.js Container :3001]
            API[Go Backend :3000]
        end
        
        subgraph "Intelligence Layer"
            ML[ML API :8000]
        end
        
        subgraph "Persistence Layer"
            DB[(PostgreSQL :5432)]
            Cache[(Redis :6379)]
        end
    end
    
    Client -->|HTTPS/443| RP
    RP -->|HTTP| UI
    RP -->|HTTP| API
    
    API --> DB
    API --> Cache
    API --> ML
    UI -.-> API
```
