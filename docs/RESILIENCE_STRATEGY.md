# Resilience & Reliability Strategy

This document outlines the advanced resilience mechanisms implemented in the Healthcare Clinical Copilot backend to ensure high availability and graceful failure handling.

## 1. Circuit Breaker (State Machine)
We use the **Sony gobreaker** implementation to protect the backend from cascading failures when the Python ML Service is unavailable or slow.

- **Threshold**: trips if 60% of requests fail (minimum 5 requests).
- **Timeout**: stays in "Open" state for 30 seconds before transitioning to "Half-Open".
- **Benefit**: prevents the Go backend from hanging on socket timeouts and provides immediate feedback to the user.

## 2. Smart Fallback (Graceful Degradation)
When the ML Service is unresponsive (Circuit Breaker is OPEN or a direct error occurs), the system does **not** fail. Instead, it activates a **Rule-Based Fallback**.

### Heuristic Logic (Fallback):
- **Heart Risk**: Based on Blood Pressure (>160) and Cholesterol (>240).
- **Diabetes Risk**: Based on Glucose (>200) and BMI (>35).
- **Clinical Confidence**: Automatically set to `0.50` to signal to the doctor that these are heuristics, not AI model outputs.

## 3. Hybrid Caching
We use a two-tier caching strategy for predictions:
1. **L1: In-Memory (Go Maps)**: Instant access, survives Redis outages.
2. **L2: Redis (Global)**: Centralized cache, survives backend restarts and shares results across multiple backend instances.

## 4. Disaster Recovery (NATS Fallback)
If the NATS message queue is unavailable, the `PredictionService` automatically falls back to **Synchronous Direct Calls** in a separate goroutine to ensure the diagnosis process eventually completes.
