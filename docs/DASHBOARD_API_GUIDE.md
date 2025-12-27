# Dashboard API Integration Guide

This document provides technical details for integrating the Dashboard summary endpoint into the React/Next.js frontend.

## Endpoint Overview
- **URL**: `/api/dashboard/summary`
- **Method**: `GET`
- **Auth**: None (current development phase)
- **Rate Limit**: Categorized under Global Rate Limits (100 req/min).

## Response Schema (JSON)

```json
{
  "total_patients": 150,
  "high_risk_patients": 12,
  "recent_assessments": 5,
  "system_health": "Healthy",
  "ml_service_pulse": "Online",
  "audit_chain_valid": true,
  "risk_distribution": {
    "Low": 90,
    "Medium": 48,
    "High": 12
  },
  "performance": {
    "avg_ml_inference_time_ms": 245,
    "uptime_seconds": 3600.5,
    "request_count": 1250,
    "error_rate": 0.05
  }
}
```

### Field Definitions:
...
- `performance` (object): Real-time API telemetry.
  - `avg_ml_inference_time_ms` (int64): The latency of the last successful ML prediction.
  - `uptime_seconds` (float): Duration the backend has been running.
  - `request_count` (int64): Total requests handled since start.
  - `error_rate` (float): Percentage of failed requests.
- `total_patients` (int64): Total number of unique patient records in the PostgreSQL DB.
- `high_risk_patients` (int64): Count of patients with a Systolic BP > 160 (current dashboard heuristic).
- `recent_assessments` (int64): New patient assessments logged in the last 24 hours.
- `system_health` (string): Overall status based on service connectivity (`Healthy`, `Warning`, `Critical`).
- `ml_service_pulse` (string): Status of the Python ML Microservice via Circuit Breaker state (`Online` / `Offline`).
- `audit_chain_valid` (bool): Real-time integrity check of the cryptographic audit trail.
- `risk_distribution` (map): Breakdown of patient population by risk severity levels.

## Frontend Usage Example (TypeScript)

```typescript
interface DashboardSummary {
  total_patients: number;
  high_risk_patients: number;
  recent_assessments: number;
  system_health: 'Healthy' | 'Warning' | 'Critical';
  ml_service_pulse: 'Online' | 'Offline';
  audit_chain_valid: boolean;
  risk_distribution: Record<string, number>;
}

async function fetchDashboardStats(): Promise<DashboardSummary> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/summary`);
  if (!response.ok) throw new Error('Dashboard stats unavailable');
  return response.json();
}
```

## Best Practices
1. **Polling**: For a live administrative view, poll this endpoint every 60 seconds.
2. **Global State**: Store the `system_health` and `ml_service_pulse` in a global context (e.g., Zustand or Redux) to show a system-status banner across all pages.
3. **Visuals**: Use the `risk_distribution` data for a Pie Chart or Bar Chart using libraries like `recharts` or `tremor`.
