export interface Patient {
    id: number;
    created_at: string;
    age: number;
    gender: 'Male' | 'Female' | 'Other';
    systolic_bp: number;
    diastolic_bp: number;
    glucose: number;
    bmi: number;
    cholesterol: number;
    heart_rate: number;
    steps: number;
    smoking: 'Yes' | 'No' | 'Former';
    alcohol: 'Yes' | 'No';
    medications: string;
    history_heart_disease: 'Yes' | 'No';
    history_stroke: 'Yes' | 'No';
    history_diabetes: 'Yes' | 'No';
    history_high_chol: 'Yes' | 'No';
    symptoms?: string;
}

export interface RiskScores {
    heart_risk_score: number;
    diabetes_risk_score: number;
    stroke_risk_score: number;
    kidney_risk_score: number;
    general_health_score: number;
    clinical_confidence: number;
    model_precisions: Record<string, number>;
    explanations: Record<string, Record<string, number>>;
}

export interface Urgency {
    urgency_level: number;
    urgency_name: string;
    probability: number;
    confidence: 'high' | 'medium' | 'low';
    golden_hour_minutes?: number | null;
}

export interface ModelPrecision {
    model_name: string;
    confidence: number;
}

export interface AssessmentResponse {
    id: number;
    risks: RiskScores;
    urgency: Urgency;
    diagnosis: string;
    diagnosis_status: 'pending' | 'ready' | 'error';
    emergency: boolean;
    patient: Patient;
    medication_analysis: {
        risky: string[];
        safe: string[];
    };
    model_precisions: ModelPrecision[];
    audit_hash?: string;
}
