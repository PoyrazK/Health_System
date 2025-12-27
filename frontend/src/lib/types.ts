export interface Patient {
    id: string;
    name: string;
    age: number;
    gender: string;
    systolic_bp: number;
    diastolic_bp: number;
    glucose: number;
    bmi: number;
    cholesterol: number;
    heart_rate: number;
    steps: number;
    smoking: boolean;
    alcohol: boolean;
    medications: string[];
    history_heart_disease: boolean;
    history_stroke: boolean;
    history_diabetes: boolean;
    history_high_chol: boolean;
    admitted_at: string;
    attending: string;
    status: 'Critical' | 'Stable' | 'Observing';
}

export interface RiskScores {
    heart: number;
    diabetes: number;
    stroke: number;
    kidney: number;
    general_health: number;
    clinical_confidence: number;
}

export interface MedicationAnalysis {
    risky: string[];
    safe: string[];
}

export interface ModelPrecision {
    name: string;
    confidence: number;
}

export interface UrgencyInfo {
    urgency_level: number;
    urgency_name: string;
    probability: number;
    confidence: string;
    golden_hour_minutes?: number;
}

export interface AssessmentResult {
    id?: number;
    risk_scores: RiskScores;
    diagnosis: string;
    medication_analysis: MedicationAnalysis;
    model_precisions: ModelPrecision[];
    emergency: boolean;
    urgency?: UrgencyInfo;
    audit_hash?: string;
}

// ==========================================
// Backend API Compatible Types
// ==========================================

/**
 * Form data structure for new patient intake.
 * Matches the Go backend `/api/assess` endpoint requirements.
 */
export interface PatientFormData {
    age: number;
    gender: 'Male' | 'Female';
    systolic_bp: number;
    diastolic_bp: number;
    glucose: number;
    bmi: number;
    cholesterol: number;
    heart_rate: number;
    steps: number;
    smoking: 'Yes' | 'No' | 'Former';
    alcohol: 'Yes' | 'No';
    medications: string; // Comma-separated list
    history_heart_disease: 'Yes' | 'No';
    history_stroke: 'Yes' | 'No';
    history_diabetes: 'Yes' | 'No';
    history_high_chol: 'Yes' | 'No';
    symptoms: string; // Comma-separated list
}

/**
 * Default form values from /api/defaults
 * This type extends PatientFormData to ensure full compatibility
 */
export type DefaultFormValues = PatientFormData;

/**
 * Response from /api/assess endpoint
 */
export interface AssessmentAPIResponse {
    id: number;
    risks: {
        heart_risk_score: number;
        diabetes_risk_score: number;
        stroke_risk_score: number;
        kidney_risk_score: number;
        general_health_score: number;
        clinical_confidence: number;
        model_precisions: Record<string, number>;
    };
    urgency: {
        urgency_level: number;
        urgency_name: string;
        probability: number;
        confidence: string;
        golden_hour_minutes?: number;
    };
    diagnosis: string;
    diagnosis_status: 'pending' | 'ready' | 'error';
    emergency: boolean;
    patient: PatientFormData;
    medication_analysis: {
        risky: string[];
        safe: string[];
    };
    model_precisions: Array<{ model_name: string; confidence: number }>;
    audit_hash: string;
}

/**
 * Response from /api/diagnosis/:id
 */
export interface DiagnosisResponse {
    id: number;
    diagnosis: string;
    status: 'pending' | 'ready' | 'error';
}

/**
 * Patient record from /api/patients
 */
export interface PatientRecord {
    id: number;
    created_at: string;
    age: number;
    gender: string;
    systolic_bp: number;
    diastolic_bp: number;
    glucose: number;
    bmi: number;
    cholesterol: number;
    heart_rate: number;
    steps: number;
    smoking: string;
    alcohol: string;
    medications: string;
    history_heart_disease: string;
    history_stroke: string;
    history_diabetes: string;
    history_high_chol: string;
    symptoms: string;
}
