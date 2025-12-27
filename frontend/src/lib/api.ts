/**
 * API Client for RedFive Backend
 * 
 * Go Backend runs on port 3000
 * ML API runs on port 8000 (called by backend, not directly)
 */

import type {
    PatientFormData,
    DefaultFormValues,
    AssessmentAPIResponse,
    DiagnosisResponse,
    PatientRecord,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

/**
 * Fetch default form values for new patient intake
 */
export async function fetchDefaults(): Promise<DefaultFormValues> {
    const response = await fetch(`${API_BASE_URL}/api/defaults`);
    if (!response.ok) {
        throw new Error('Failed to fetch default values');
    }
    return response.json();
}

/**
 * Submit patient data for full assessment
 */
export async function submitAssessment(data: PatientFormData): Promise<AssessmentAPIResponse> {
    const response = await fetch(`${API_BASE_URL}/api/assess`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error('Failed to submit assessment');
    }
    return response.json();
}

/**
 * Poll diagnosis status for a patient
 */
export async function pollDiagnosis(patientId: number): Promise<DiagnosisResponse> {
    const response = await fetch(`${API_BASE_URL}/api/diagnosis/${patientId}`);
    if (!response.ok) {
        throw new Error('Failed to fetch diagnosis');
    }
    return response.json();
}

/**
 * Fetch all patients
 */
export async function fetchPatients(): Promise<PatientRecord[]> {
    const response = await fetch(`${API_BASE_URL}/api/patients`);
    if (!response.ok) {
        throw new Error('Failed to fetch patients');
    }
    return response.json();
}

/**
 * Submit doctor feedback for RAG-Lite learning
 */
export async function submitFeedback(data: {
    assessment_id: string;
    doctor_approved: boolean;
    doctor_notes: string;
    risk_profile: string;
}): Promise<{ status: string; id: number }> {
    const response = await fetch(`${API_BASE_URL}/api/feedback`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error('Failed to submit feedback');
    }
    return response.json();
}

/**
 * Fetch dashboard summary statistics
 */
export async function fetchDashboardSummary(): Promise<DashboardSummary> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/summary`);
    if (!response.ok) {
        throw new Error('Failed to fetch dashboard summary');
    }
    return response.json();
}

/**
 * Analyze EKG signal
 */
export async function analyzeEKG(signal: number[], samplingRate: number = 360): Promise<EKGAnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/ekg/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signal, sampling_rate: samplingRate }),
    });
    if (!response.ok) {
        throw new Error('Failed to analyze EKG');
    }
    return response.json();
}

/**
 * Predict disease from symptoms
 */
export async function predictDisease(symptoms: string[], patientId?: string): Promise<DiseasePrediction> {
    const response = await fetch(`${API_BASE_URL}/disease/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms, patient_id: patientId }),
    });
    if (!response.ok) {
        throw new Error('Failed to predict disease');
    }
    return response.json();
}

/**
 * Predict urgency/triage level
 */
export async function predictUrgency(
    symptoms: string[],
    patientData: PatientFormData
): Promise<UrgencyPrediction> {
    const response = await fetch(`${API_BASE_URL}/urgency/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms, patient_data: patientData }),
    });
    if (!response.ok) {
        throw new Error('Failed to predict urgency');
    }
    return response.json();
}

/**
 * Get golden hour information for a disease
 */
export async function getGoldenHour(disease: string): Promise<GoldenHour> {
    const response = await fetch(`${API_BASE_URL}/urgency/golden-hour/${encodeURIComponent(disease)}`);
    if (!response.ok) {
        throw new Error('Failed to get golden hour info');
    }
    return response.json();
}

// Type definitions for new endpoints
export interface DashboardSummary {
    TotalPatients: number;
    HighRiskPatients: number;
    RecentAssessments: number;
    SystemHealth: string;
    MLServicePulse: string;
    AuditChainValid: boolean;
    RiskDistribution: Record<string, number>;
    Performance: {
        AvgMLInferenceTimeMs: number;
        UptimeSeconds: number;
        RequestCount: number;
        ErrorRate: number;
    };
}

export interface EKGAnalysisResponse {
    status: string;
    predictions: Array<{
        condition: string;
        probability: number;
        confidence: string;
    }>;
    features: {
        heart_rate: number;
        rr_mean: number;
        rr_std: number;
    };
}

export interface DiseasePrediction {
    predictions: Array<{
        disease: string;
        probability: number;
        confidence: string;
    }>;
}

export interface UrgencyPrediction {
    urgency_level: number;
    urgency_name: string;
    probability: number;
    confidence: string;
}

export interface GoldenHour {
    urgency: number;
    golden_hour: number;
    description: string;
}

/**
 * Default form values (fallback when API is unavailable)
 */
export const DEFAULT_FORM_VALUES: DefaultFormValues = {
    age: 45,
    gender: 'Male',
    systolic_bp: 120,
    diastolic_bp: 80,
    glucose: 100,
    bmi: 24.5,
    cholesterol: 190,
    heart_rate: 72,
    steps: 6000,
    smoking: 'No',
    alcohol: 'No',
    medications: 'Lisinopril, Atorvastatin',
};

