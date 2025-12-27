# ⚡ Scalability Architecture

Clinical Copilot v4.0 is designed for high availability and horizontal scaling. The backend has transitioned from a monolithic stateful service to a stateless, message-driven architecture.

---

## 🏗️ Architectural components

### 1. Stateless Go Backend
- **Horizontally Scalable:** Multiple pods can run behind a Load Balancer (Nginx/Traefik).
- **Stateless Session Management:** No patient data or diagnosis status is stored in memory. Everything is persisted in Redis or PostgreSQL.

### 2. High-Performance Caching (Redis)
- **ML Prediction Cache:** Repeat assessments for the same patient are served in <5ms from Redis.
- **Diagnosis State:** LLM diagnosis progress is tracked globally across pods.
- **Connection Pooling:** Controlled database connections (GORM) and Redis pooling prevent resource exhaustion.

### 3. Distributed Messaging (NATS)
- **Asynchronous LLM Processing:** Heavy LLM tasks are pushed to a NATS work queue.
- **Worker Pattern:** Dedicated workers (internal or separate services) consume tasks, preventing API timeouts and blocking.
- **Loose Coupling:** The backend doesn't wait for the ML service to finish; it just acknowledges the task.

### 4. Global WebSocket Broadcasting (Redis Pub/Sub)
- **Pod Inter-Communication:** When a background worker finishes, it publishes the result to Redis Pub/Sub.
- **Real-Time Delivery:** All backend pods listen to Redis and push the update to the specific clinician connected to *that* specific pod.

### 5. Resiliency (Circuit Breaker)
- **Graceful Degradation:** ML API failures are caught by the **Sony gobreaker**.
- **Self-Healing:** The system stops sending requests to a failing ML service, giving it time to recover while serving cached data.

---

## 📊 Performance Metrics

| Feature | Single Pod | Multi-Pod (Distributed) |
|---------|------------|-------------------------|
| Max Connections | ~1,000 | ~100,000+ |
| ML Latency | 200ms+ | 5ms (Cached) |
| LLM Handling | Blocking/Sync | Non-blocking/Async |
| Reliability | Single Point of Failure | High Availability |

---

## 🛠️ Infrastructure Ready
- **Docker Compose:** Fully containerized with health-dependent startup.
- **Kubernetes Ready:** Includes `/health/live` and `/health/ready` probes for automated healing and rolling updates.
- **Rate Limiting:** Built-in protection against DoS and resource abuse.
