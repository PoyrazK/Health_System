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

export interface AssessmentResult {
    risk_scores: RiskScores;
    diagnosis: string;
    medication_analysis: MedicationAnalysis;
    model_precisions: ModelPrecision[];
    emergency: boolean;
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
}

/**
 * Default form values from /api/defaults
 */
export interface DefaultFormValues extends PatientFormData {
    history_heart_disease?: string;
    history_stroke?: string;
    history_diabetes?: string;
    history_high_chol?: string;
}

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
    diagnosis: string;
    diagnosis_status: 'pending' | 'ready' | 'error';
    emergency: boolean;
    patient: PatientFormData;
    medication_analysis: {
        risky: string[];
        safe: string[];
    };
    model_precisions: Array<{ model_name: string; confidence: number }>;
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
}
