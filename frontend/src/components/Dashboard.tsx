'use client';

import { useState, useEffect, useCallback } from 'react';
import { MOCK_PATIENTS } from '@/lib/constants';
import { Patient, AssessmentResult, AssessmentAPIResponse } from '@/lib/types';
import { pollDiagnosis } from '@/lib/api';
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


interface DashboardProps {
    onExit: () => void;
}

export default function Dashboard({ onExit }: DashboardProps) {
    const [selectedPatient, setSelectedPatient] = useState<Patient>(MOCK_PATIENTS[0]);
    const [assessment, setAssessment] = useState<AssessmentResult | null>(null);
    const [isNewPatientModalOpen, setIsNewPatientModalOpen] = useState(false);
    const [lastAPIResult, setLastAPIResult] = useState<AssessmentAPIResponse | null>(null);
    const [diagnosisPolling, setDiagnosisPolling] = useState(false);

    // Mock historical data for charts
    const historyData = [
        { time: '08:00', value: selectedPatient.heart_rate - 10 },
        { time: '10:00', value: selectedPatient.heart_rate + 5 },
        { time: '12:00', value: selectedPatient.heart_rate - 2 },
        { time: '14:00', value: selectedPatient.heart_rate + 8 },
        { time: '16:00', value: selectedPatient.heart_rate },
    ];

    useEffect(() => {
        setAssessment(null);
        const timer = setTimeout(() => {
            setAssessment({
                risk_scores: {
                    heart: Math.floor(Math.random() * 60) + 10,
                    diabetes: Math.floor(Math.random() * 50) + 20,
                    stroke: Math.floor(Math.random() * 30) + 5,
                    kidney: Math.floor(Math.random() * 40) + 10,
                    general_health: 82,
                    clinical_confidence: 99.8
                },
                diagnosis: `### Clinical Impression for ${selectedPatient.name}\n\nBased on the analysis of **vitals** and **EHR history**, the neural engine indicates a probable diagnosis of **Bacterial Pneumonia**.\n\n- **Consolidation**: Indicated in lower right lobe\n- **Biomarkers**: Elevated WBC counts (${selectedPatient.systolic_bp > 150 ? 'Severe' : 'Moderate'})\n- **Oxygen Saturation**: Stable but trending down.\n\n#### Recommendations\n1. Initiate broad-spectrum antibiotics (Vancomycin/Piperacillin).\n2. Schedule repeat CXR in 12 hours.\n3. Monitor renal clearance given age and baseline GFR.`,
                medication_analysis: {
                    risky: ['Warfarin'],
                    safe: ['Vancomycin', 'Piperacillin', 'Insulin']
                },
                model_precisions: [
                    { name: 'XGBoost Cardio', confidence: 0.99 },
                    { name: 'LSTM Glycemic', confidence: 0.98 },
                    { name: 'CNN Imaging', confidence: 0.95 }
                ],
                emergency: selectedPatient.status === 'Critical'
            });
        }, 1500);
        return () => clearTimeout(timer);
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

    return (
        <div className={`flex h-screen bg-[#0A0F1C] text-white overflow-hidden transition-all duration-700 ${assessment?.emergency ? 'ring-[4px] ring-red-500/50 ring-inset' : ''}`}>
            <Sidebar
                patients={MOCK_PATIENTS}
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
