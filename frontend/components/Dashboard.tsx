'use client';

import { useState, useEffect, useCallback } from 'react';
import { Patient, AssessmentResult, AssessmentAPIResponse, PatientRecord } from '@/lib/types';
import { pollDiagnosis, fetchPatients, submitAssessment } from '@/lib/api';
import Sidebar from './dashboard/Sidebar';
import PatientHeader from './dashboard/PatientHeader';
import VitalsGrid from './dashboard/VitalsGrid';
import RiskGauges from './dashboard/RiskGauges';
import NeuralAssessment from './dashboard/NeuralAssessment';
import MedicationSafety from './dashboard/MedicationSafety';
import TelemetryGraph from './dashboard/TelemetryGraph';
import VitalsChart from './dashboard/VitalsChart';
import IntakeModal from './dashboard/IntakeModal';
import SystemStatus from './dashboard/SystemStatus';

// Convert PatientRecord from API to Patient for UI
function recordToPatient(record: PatientRecord, index: number): Patient {
    return {
        id: String(record.id),
        name: `Patient #${record.id}`,
        age: record.age,
        gender: record.gender,
        systolic_bp: record.systolic_bp,
        diastolic_bp: record.diastolic_bp,
        glucose: record.glucose,
        bmi: record.bmi,
        cholesterol: record.cholesterol,
        heart_rate: record.heart_rate,
        steps: record.steps,
        smoking: record.smoking === 'Yes',
        alcohol: record.alcohol === 'Yes',
        medications: record.medications ? record.medications.split(',').map(m => m.trim()) : [],
        history_heart_disease: false,
        history_stroke: false,
        history_diabetes: false,
        history_high_chol: false,
        admitted_at: record.created_at,
        attending: 'Dr. AI Copilot',
        status: record.systolic_bp > 160 ? 'Critical' : record.systolic_bp > 140 ? 'Observing' : 'Stable',
    };
}

interface DashboardProps {
    onExit: () => void;
}

export default function Dashboard({ onExit }: DashboardProps) {
    const [patients, setPatients] = useState<Patient[]>([]);
    const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
    const [assessment, setAssessment] = useState<AssessmentResult | null>(null);
    const [isNewPatientModalOpen, setIsNewPatientModalOpen] = useState(false);
    const [lastAPIResult, setLastAPIResult] = useState<AssessmentAPIResponse | null>(null);
    const [diagnosisPolling, setDiagnosisPolling] = useState(false);
    const [loading, setLoading] = useState(true);

    // Fetch patients from backend
    useEffect(() => {
        async function loadPatients() {
            try {
                const records = await fetchPatients();
                const patientList = records.map(recordToPatient);
                setPatients(patientList);
                if (patientList.length > 0) {
                    setSelectedPatient(patientList[0]);
                }
            } catch (error) {
                console.error('Failed to load patients:', error);
            } finally {
                setLoading(false);
            }
        }
        loadPatients();
    }, []);

    // Mock historical data for charts (based on selected patient)
    const historyData = selectedPatient ? [
        { time: '08:00', value: selectedPatient.heart_rate - 10 },
        { time: '10:00', value: selectedPatient.heart_rate + 5 },
        { time: '12:00', value: selectedPatient.heart_rate - 2 },
        { time: '14:00', value: selectedPatient.heart_rate + 8 },
        { time: '16:00', value: selectedPatient.heart_rate },
    ] : [];

    // Fetch real assessment when patient changes
    useEffect(() => {
        if (!selectedPatient) return;

        const patient = selectedPatient; // Capture for TypeScript narrowing
        setAssessment(null);

        // Trigger real ML assessment via backend
        async function fetchAssessment() {
            try {
                const result = await submitAssessment({
                    age: patient.age,
                    gender: patient.gender as 'Male' | 'Female',
                    systolic_bp: patient.systolic_bp,
                    diastolic_bp: patient.diastolic_bp,
                    glucose: patient.glucose,
                    bmi: patient.bmi,
                    cholesterol: patient.cholesterol,
                    heart_rate: patient.heart_rate,
                    steps: patient.steps,
                    smoking: patient.smoking ? 'Yes' : 'No',
                    alcohol: patient.alcohol ? 'Yes' : 'No',
                    medications: patient.medications.join(', '),
                });

                // Map API response to AssessmentResult
                setAssessment({
                    risk_scores: {
                        heart: result.risks.heart_risk_score,
                        diabetes: result.risks.diabetes_risk_score,
                        stroke: result.risks.stroke_risk_score,
                        kidney: result.risks.kidney_risk_score,
                        general_health: result.risks.general_health_score,
                        clinical_confidence: result.risks.clinical_confidence,
                    },
                    diagnosis: result.diagnosis || 'Analysis pending...',
                    medication_analysis: result.medication_analysis,
                    model_precisions: result.model_precisions.map(m => ({
                        name: m.model_name,
                        confidence: m.confidence / 100,
                    })),
                    emergency: result.emergency,
                });

                // Poll for diagnosis if pending
                if (result.diagnosis_status === 'pending') {
                    setDiagnosisPolling(true);
                    const pollInterval = setInterval(async () => {
                        try {
                            const diagResult = await pollDiagnosis(result.id);
                            if (diagResult.status === 'ready') {
                                setAssessment(prev => prev ? { ...prev, diagnosis: diagResult.diagnosis } : null);
                                clearInterval(pollInterval);
                                setDiagnosisPolling(false);
                            } else if (diagResult.status === 'error') {
                                clearInterval(pollInterval);
                                setDiagnosisPolling(false);
                            }
                        } catch {
                            clearInterval(pollInterval);
                            setDiagnosisPolling(false);
                        }
                    }, 2000);

                    setTimeout(() => {
                        clearInterval(pollInterval);
                        setDiagnosisPolling(false);
                    }, 30000);
                }
            } catch (error) {
                console.error('Failed to fetch assessment:', error);
                // Fallback to mock data if API fails
                setAssessment({
                    risk_scores: {
                        heart: 35,
                        diabetes: 25,
                        stroke: 15,
                        kidney: 20,
                        general_health: 82,
                        clinical_confidence: 94.5
                    },
                    diagnosis: '⚠️ **ML Service Unavailable** - Using fallback assessment',
                    medication_analysis: { risky: [], safe: [] },
                    model_precisions: [],
                    emergency: patient.status === 'Critical'
                });
            }
        }

        fetchAssessment();
    }, [selectedPatient]);

    // Handle IntakeModal submission result
    const handleAssessmentResult = useCallback(async (result: AssessmentAPIResponse) => {
        setLastAPIResult(result);

        // Map API response to local AssessmentResult format
        const mappedResult: AssessmentResult = {
            risk_scores: {
                heart: result.risks.heart_risk_score,
                diabetes: result.risks.diabetes_risk_score,
                stroke: result.risks.stroke_risk_score,
                kidney: result.risks.kidney_risk_score,
                general_health: result.risks.general_health_score,
                clinical_confidence: result.risks.clinical_confidence,
            },
            diagnosis: result.diagnosis || 'Analysis pending...',
            medication_analysis: result.medication_analysis,
            model_precisions: result.model_precisions.map(m => ({
                name: m.model_name,
                confidence: m.confidence / 100,
            })),
            emergency: result.emergency,
        };

        setAssessment(mappedResult);

        // Poll for diagnosis if pending
        if (result.diagnosis_status === 'pending') {
            setDiagnosisPolling(true);
            const pollInterval = setInterval(async () => {
                try {
                    const diagResult = await pollDiagnosis(result.id);
                    if (diagResult.status === 'ready') {
                        setAssessment(prev => prev ? {
                            ...prev,
                            diagnosis: diagResult.diagnosis
                        } : null);
                        clearInterval(pollInterval);
                        setDiagnosisPolling(false);
                    } else if (diagResult.status === 'error') {
                        clearInterval(pollInterval);
                        setDiagnosisPolling(false);
                    }
                } catch {
                    clearInterval(pollInterval);
                    setDiagnosisPolling(false);
                }
            }, 2000);

            // Stop polling after 30 seconds
            setTimeout(() => {
                clearInterval(pollInterval);
                setDiagnosisPolling(false);
            }, 30000);
        }
    }, []);

    // Show loading state
    if (loading) {
        return (
            <div className="flex h-screen bg-[#0A0F1C] text-white items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-slate-400">Loading patients...</p>
                </div>
            </div>
        );
    }

    // Handle no patients case
    if (!selectedPatient) {
        return (
            <div className="flex h-screen bg-[#0A0F1C] text-white items-center justify-center">
                <div className="text-center">
                    <p className="text-xl text-slate-300 mb-4">No patients found</p>
                    <button
                        onClick={() => setIsNewPatientModalOpen(true)}
                        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors"
                    >
                        Add New Patient
                    </button>
                    <IntakeModal
                        isOpen={isNewPatientModalOpen}
                        onClose={() => setIsNewPatientModalOpen(false)}
                        onSubmitSuccess={handleAssessmentResult}
                    />
                </div>
            </div>
        );
    }

    return (
        <div className={`flex h-screen bg-[#0A0F1C] text-white overflow-hidden transition-all duration-700 ${assessment?.emergency ? 'ring-[4px] ring-red-500/50 ring-inset' : ''}`}>
            <Sidebar
                patients={patients}
                selectedId={selectedPatient.id}
                onSelect={setSelectedPatient}
                onNew={() => setIsNewPatientModalOpen(true)}
            />

            <main className="flex-1 flex flex-col min-w-0 bg-[#0f1115]">
                <PatientHeader
                    patient={selectedPatient}
                    onExit={onExit}
                />

                <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 custom-scrollbar">
                    <div className="grid grid-cols-12 gap-6">
                        {/* Left: Vitals & History Charts */}
                        <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
                            <VitalsGrid patient={selectedPatient} />
                            <div className="glass-card rounded-3xl p-6 space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest leading-none">Vitals History</span>
                                    <span className="text-[10px] text-blue-400 font-bold">24H</span>
                                </div>
                                <div className="space-y-6">
                                    <div>
                                        <div className="flex justify-between items-baseline mb-2">
                                            <span className="text-xs text-slate-400">Heart Rate</span>
                                            <span className="text-sm font-bold text-red-400">{selectedPatient.heart_rate} BPM</span>
                                        </div>
                                        <VitalsChart label="HR" data={historyData} color="#EF4444" />
                                    </div>
                                    <div>
                                        <div className="flex justify-between items-baseline mb-2">
                                            <span className="text-xs text-slate-400">BP Systolic</span>
                                            <span className="text-sm font-bold text-blue-400">{selectedPatient.systolic_bp} mmHg</span>
                                        </div>
                                        <VitalsChart label="BP" data={historyData.map(d => ({ ...d, value: d.value + 40 }))} color="#3B82F6" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Middle: Assessment Result + 3D HUD */}
                        <div className="col-span-12 lg:col-span-6 flex flex-col gap-6">
                            <div className="space-y-6">
                                <RiskGauges scores={assessment?.risk_scores} />
                                <div className="glass-card rounded-3xl p-5 space-y-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="material-symbols-outlined text-slate-500 text-[18px]">history</span>
                                            <span className="text-xs text-slate-500 font-bold uppercase tracking-widest">Patient History</span>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                                            <span className="text-xs text-slate-400">Heart Disease</span>
                                            <span className={`text-xs font-bold ${selectedPatient.history_heart_disease ? 'text-red-400' : 'text-emerald-400'}`}>
                                                {selectedPatient.history_heart_disease ? 'Yes' : 'No'}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                                            <span className="text-xs text-slate-400">Diabetes</span>
                                            <span className={`text-xs font-bold ${selectedPatient.history_diabetes ? 'text-red-400' : 'text-emerald-400'}`}>
                                                {selectedPatient.history_diabetes ? 'Yes' : 'No'}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                                            <span className="text-xs text-slate-400">Stroke</span>
                                            <span className={`text-xs font-bold ${selectedPatient.history_stroke ? 'text-red-400' : 'text-emerald-400'}`}>
                                                {selectedPatient.history_stroke ? 'Yes' : 'No'}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                                            <span className="text-xs text-slate-400">High Cholesterol</span>
                                            <span className={`text-xs font-bold ${selectedPatient.history_high_chol ? 'text-red-400' : 'text-emerald-400'}`}>
                                                {selectedPatient.history_high_chol ? 'Yes' : 'No'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <NeuralAssessment
                                diagnosis={assessment?.diagnosis}
                                isCritical={assessment?.emergency}
                            />
                        </div>

                        {/* Right: Medication & System telemetry */}
                        <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
                            <MedicationSafety analysis={assessment?.medication_analysis} />
                            <SystemStatus models={assessment?.model_precisions} />
                        </div>
                    </div>

                    <div className="mt-auto">
                        <TelemetryGraph isCritical={assessment?.emergency} />
                    </div>
                </div>
            </main>

            <IntakeModal
                isOpen={isNewPatientModalOpen}
                onClose={() => setIsNewPatientModalOpen(false)}
                onSubmitSuccess={handleAssessmentResult}
            />
        </div>
    );
}

