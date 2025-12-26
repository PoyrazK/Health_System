# 📡 Real-Time Infrastructure: WebSockets & Async Delivery

Clinical Copilot v3.0 introduces a persistent real-time communication layer between the frontend and backend, enabling instantaneous updates for heavy computational tasks like LLM synthesis.

---

## 🏗️ WebSocket Integration

The system now utilizes **Go Fiber's WebSocket Middleware** to maintain long-lived connections. This eliminates the need for aggressive polling and reduces server load.

### Subscription Pattern
1. **Initial Request**: The clinician triggers an assessment via `POST /api/assess`.
2. **WS Handshake**: The frontend establishes a WebSocket connection and sends a `subscribe` payload for the specific `patient_id`.
3. **Async Processing**: The Go backend fires off the ML and LLM tasks in background goroutines.
4. **Instant Broadcast**: As soon as the LLM (GPT-4o/Gemini) returns a result, the `WebSocketHandler` broadcasts the `diagnosis_update` directly to the subscribed client.

---

## 🔄 Zero-Latency Feedback Loop

| Mechanism | Frequency | Data Type |
|-----------|-----------|-----------|
| **REST (POST)** | On Demand | Patient Intake / Biometrics |
| **WebSocket** | Persistent | Diagnosis Progress, Results, Alerts |
| **Telemetry** | 1 Hz | Network Latency, Service Health |

---

## 🛠️ Implementation Details

### Backend Handler (`backend/internal/handlers/ws_handler.go`)
- **Connection Registry**: Managed via a thread-safe `sync.RWMutex` map.
- **Patient ID Grouping**: Clients are grouped by the patient record they are currently viewing, ensuring "targeted" broadcasts rather than global noise.
- **Auto-Cleanup**: Connections are automatically removed from the registry on disconnect to prevent memory leaks.

### Benefits for Clinicians
- **Instant Result Delivery**: The "Neural synthesis in progress" spinner disappears the exact millisecond the diagnosis is ready.
- **Collaborative Potential**: Multiple clinicians viewing the same patient will receive updates simultaneously.

---
*Powered by Fiber v2 & sync.RWMutex synchronization.*
