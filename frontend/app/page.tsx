"use client";

import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Stethoscope,
  Wifi,
  PlusCircle,
  ShieldAlert,
  AlertTriangle,
  Gauge
} from "lucide-react";

// Components
import { PatientSidebar } from "@/components/dashboard/PatientSidebar";
import { VitalsGrid } from "@/components/dashboard/VitalsGrid";
import { RiskAnalysis } from "@/components/dashboard/RiskAnalysis";
import { DiagnosisPanel } from "@/components/dashboard/DiagnosisPanel";
import { FeedbackPanel } from "@/components/dashboard/FeedbackPanel";
import { IntakeModal } from "@/components/modals/IntakeModal";
import DiseaseCheckerModal from "@/components/modals/DiseaseCheckerModal";
import EKGPanel from "@/components/dashboard/EKGPanel";
import { Activity } from "lucide-react";
import { useTelemetry } from "@/hooks/useTelemetry";
// Shared interfaces imported from types.ts
import { Patient, AssessmentResponse, ModelPrecision } from '../types';

// Redundant local interfaces removed in favor of types.ts

interface DashboardState {
  loading: boolean;
  data: AssessmentResponse | null;
  patients: Patient[];
  patient: Patient | null;
  latency: number;
}

export default function ClinicalCockpit() {
  const telemetry = useTelemetry(10000);
  const [state, setState] = useState<DashboardState>({
    loading: true,
    data: null,
    patients: [],
    patient: null,
    latency: 0
  });
  const [showModal, setShowModal] = useState(false);
  const [showDiseaseModal, setShowDiseaseModal] = useState(false);

  const mountedRef = useRef(true);
  const loadingRef = useRef(false);

  // Unified updater to batch changes
  const updateState = useCallback((updates: Partial<DashboardState>) => {
    if (mountedRef.current) {
      setState(prev => ({ ...prev, ...updates }));
    }
  }, []);

  // Fetch patients list
  const fetchPatients = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:3000/api/patients");
      if (!mountedRef.current) return [];
      const list = await res.json();
      updateState({ patients: list });
      return list;
    } catch (err) {
      console.error("Failed to fetch patients", err);
      return [];
    }
  }, [updateState]);

  // Poll for diagnosis updates
  const pollDiagnosis = useCallback(async (patientId: number) => {
    for (let i = 0; i < 30; i++) {
      if (!mountedRef.current) return;
      await new Promise(r => setTimeout(r, 1000));

      try {
        const res = await fetch(`http://localhost:3000/api/diagnosis/${patientId}`);
        const result = await res.json();

        if (result.status === "ready" || result.status === "error") {
          if (mountedRef.current) {
            setState(prev => {
              if (prev.data?.patient?.id === patientId) {
                return {
                  ...prev,
                  data: { ...prev.data, diagnosis: result.diagnosis, diagnosis_status: result.status }
                };
              }
              return prev;
            });
          }
          return;
        }
      } catch { /* continue polling */ }
    }
  }, []);

  const { loading, data, patients, patient, latency } = state;
  const emergency = data?.emergency || false;

  // Use refs for stable values in callbacks
  const patientRef = useRef(patient);
  useEffect(() => { patientRef.current = patient; }, [patient]);

  // Run assessment (Stable Function)
  const runAssessment = useCallback(async (targetPatient?: Patient) => {
    if (loadingRef.current) return;
    loadingRef.current = true;

    const currentPatient = patientRef.current;
    const isNewPatient = targetPatient && currentPatient?.id !== targetPatient.id;
    updateState({ loading: isNewPatient });

    const start = performance.now();
    let target = targetPatient || currentPatient;

    // If no patient override and current patient is null, use defaults
    if (!target) {
      // Fetch defaults as fallback
      try {
        const defRes = await fetch("http://localhost:3000/api/defaults");
        target = await defRes.json();
      } catch {
        const initialPatient: Patient = {
          id: 0,
          age: 65,
          gender: "Male",
          systolic_bp: 145,
          diastolic_bp: 90,
          glucose: 110,
          bmi: 27.5,
          cholesterol: 190,
          heart_rate: 72,
          steps: 4500,
          smoking: "No",
          alcohol: "No",
          medications: "Lisinopril",
          history_heart_disease: "No",
          history_stroke: "No",
          history_diabetes: "No",
          history_high_chol: "No",
          created_at: new Date().toISOString()
        };
        target = initialPatient;
      }
    }

    try {
      const res = await fetch("http://localhost:3000/api/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(target),
      });

      if (!mountedRef.current) return;

      const result = await res.json();
      const end = performance.now();

      updateState({
        data: result,
        latency: Math.round(end - start),
        patient: result.patient || currentPatient,
        loading: false
      });

      if (result.patient && result.diagnosis_status === "pending") {
        pollDiagnosis(result.patient.id);
      }

      fetchPatients();
    } catch (error) {
      console.error("Assessment failed", error);
      updateState({ loading: false });
    } finally {
      if (mountedRef.current) {
        setShowModal(false);
      }
      loadingRef.current = false;
    }
  }, [updateState, pollDiagnosis, fetchPatients]); // Stabilized: no patient dependency

  // Initial load
  useEffect(() => {
    mountedRef.current = true;

    const init = async () => {
      const list = await fetchPatients();
      if (!mountedRef.current) return;

      if (list && list.length > 0) {
        runAssessment(list[0]);
      } else {
        updateState({ loading: false });
      }
    };

    init();
    return () => { mountedRef.current = false; };
  }, [fetchPatients, runAssessment]);

  // Select patient handler
  const selectPatient = useCallback((p: Patient) => {
    if (patientRef.current?.id === p.id) return;
    runAssessment(p);
  }, [runAssessment]); // Stabilized

  const medInfo = useMemo(() => {
    if (data?.medication_analysis) {
      return data.medication_analysis;
    }
    return { risky: [], safe: [] };
  }, [data]);

  // Loading Screen
  if (loading && !patient) {
    return (
      <main className="fixed inset-0 bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="relative mb-4">
            <div className="w-16 h-16 border-4 border-blue-500/20 rounded-full mx-auto" />
            <div className="absolute inset-0 w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
          </div>
          <p className="text-[10px] font-black text-blue-500 tracking-[0.5em] uppercase animate-pulse">
            Loading System Core...
          </p>
        </div>
      </main>
    );
  }

  // Final fallback
  if (!patient) return null;

  return (
    <main
      className={`
        fixed inset-0 p-4 font-sans transition-colors duration-1000 overflow-hidden flex flex-col 
        ${emergency ? 'bg-red-950/20' : 'bg-[#050505]'}
      `}
    >
      <IntakeModal isOpen={showModal} onClose={() => setShowModal(false)} onSubmit={runAssessment} />

      <AnimatePresence>
        {emergency && (
          <motion.div
            key="emergency-pulse"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 pointer-events-none border-[8px] border-red-500/20 animate-pulse z-50 shadow-[inset_0_0_100px_rgba(239,68,68,0.2)]"
          />
        )}
      </AnimatePresence>

      {/* Header HUD */}
      <div className="flex justify-between items-center mb-6 px-2 relative z-10 shrink-0 h-14">
        <div className="flex items-center gap-6">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Stethoscope className={`w-5 h-5 text-white ${emergency ? 'animate-pulse' : ''}`} />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className={`relative flex h-2 w-2`}>
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${emergency ? 'bg-red-500' : 'bg-emerald-500'}`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${emergency ? 'bg-red-500' : 'bg-emerald-500'}`}></span>
              </span>
              <h2 className={`text-[9px] font-black tracking-[0.4em] uppercase ${emergency ? 'text-red-500' : 'text-slate-500'}`}>
                {emergency ? "CRITICAL ASSESSMENT OVERRIDE" : "NEURAL CLINICAL INTEGRATION"}
              </h2>
            </div>
            <h1 className="text-xl font-black text-white tracking-widest uppercase italic leading-none">
              Clinical Copilot <span className="text-blue-500">v2.0</span>
            </h1>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="px-5 py-2.5 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center gap-3 backdrop-blur-md">
            <Wifi className={`w-4 h-4 ${latency < 100 ? 'text-emerald-500' : 'text-amber-500'}`} />
            <div className="text-left">
              <p className="text-[7px] font-bold text-slate-500 uppercase tracking-widest">Latency</p>
              <p className="text-[10px] font-black text-white">{latency}ms</p>
            </div>
          </div>
          <button
            onClick={() => setShowDiseaseModal(true)}
            className="px-6 py-2 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 text-[11px] font-black tracking-[0.2em] text-white hover:opacity-90 transition-all uppercase shadow-lg shadow-purple-600/20 flex items-center gap-2"
          >
            <Activity className="w-4 h-4" /> AI Disease Check
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="px-6 py-2 rounded-2xl bg-blue-600 text-[11px] font-black tracking-[0.2em] text-white hover:bg-blue-500 transition-all uppercase shadow-lg shadow-blue-600/20 flex items-center gap-2 disabled:opacity-50"
            disabled={loading}
          >
            <PlusCircle className="w-4 h-4" /> New Assessment
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-5 min-h-0 relative z-10">

        {/* COL 1: Patient Queue */}
        <div className="col-span-2 h-full min-h-0">
          <PatientSidebar patients={patients} selectedId={patient?.id} onSelect={selectPatient} />
        </div>

        {/* COL 2: Biometrics & Feedback */}
        <div className="col-span-3 flex flex-col h-full min-h-0">
          <div className={`
            glass-card p-6 rounded-[2rem] transition-all duration-700 flex flex-col h-full border border-white/5 bg-gradient-to-b from-white/[0.02] to-transparent
            ${emergency ? 'border-red-500/40 shadow-[0_0_30px_rgba(239,68,68,0.1)]' : ''}
          `}>
            <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/5">
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                <Gauge className="w-3 h-3" /> Telemetry Stream
              </h3>
              <div className="flex gap-1.5">
                {patient?.smoking === 'Yes' && (
                  <span className="text-[8px] bg-amber-500/10 text-amber-500 px-2.5 py-1 rounded-md font-black tracking-wider border border-amber-500/10">SMOKER</span>
                )}
                {patient?.alcohol === 'Yes' && (
                  <span className="text-[8px] bg-purple-500/10 text-purple-500 px-2.5 py-1 rounded-md font-black tracking-wider border border-purple-500/10">ALCOHOL</span>
                )}
              </div>
            </div>

            <div className="shrink-0">
              <VitalsGrid patient={patient} />
            </div>

            <div className="mt-4 flex-1 overflow-y-auto custom-scrollbar pr-1 -mr-1 space-y-4">
              <EKGPanel />
              {data && <FeedbackPanel assessmentId={data.id} risks={data.risks} />}
            </div>

            <div className="mt-auto pt-4 border-t border-white/5 shrink-0">
              <div className="flex justify-between items-end mb-2">
                <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">AI Confidence</span>
                <span className={`text-[10px] font-black ${data?.risks.clinical_confidence && data.risks.clinical_confidence > 90 ? 'text-emerald-500' : 'text-amber-500'}`}>
                  {data?.risks.clinical_confidence || '0.0'}%
                </span>
              </div>
              <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${data?.risks.clinical_confidence || 0}%` }}
                  className={`h-full shadow-[0_0_10px_currentColor] ${data?.risks.clinical_confidence && data.risks.clinical_confidence > 90 ? 'bg-emerald-500 text-emerald-500' : 'bg-blue-500 text-blue-500'}`}
                />
              </div>
            </div>
          </div>
        </div>

        {/* COL 3: Intelligence Core */}
        <div className="col-span-5 flex flex-col gap-5 h-full min-h-0">
          <div className="shrink-0">
            <RiskAnalysis risks={data?.risks} explanations={data?.risks.explanations} />
          </div>

          <DiagnosisPanel
            diagnosis={data?.diagnosis || ""}
            status={data?.diagnosis_status || "pending"}
            loading={loading}
            urgency={data?.urgency}
            auditHash={data?.audit_hash}
          />
        </div>

        {/* COL 4: Safety & Analytics */}
        <div className="col-span-2 space-y-5 flex flex-col h-full min-h-0">

          {/* Medication Safety */}
          <div className="glass-card p-6 rounded-[2rem] bg-white/[0.01] shrink-0 border border-white/5 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-red-500/5 blur-3xl rounded-full pointer-events-none" />
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-5 pb-2 border-b border-white/5 flex items-center gap-2 relative z-10">
              <ShieldAlert className="w-3 h-3" /> Medication Security
            </h3>

            <div className="space-y-3 relative z-10">
              {medInfo.risky.map((m: string, i: number) => (
                <div key={i} className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 group hover:bg-red-500/15 transition-colors">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-3 h-3 text-red-500 animate-pulse" />
                    <p className="text-[8px] font-black uppercase text-red-500 tracking-wider">Detection</p>
                  </div>
                  <p className="text-[10px] text-white font-bold italic tracking-tight">{m}</p>
                  <p className="text-[8px] text-red-400/60 mt-1 font-semibold">Interaction Warning</p>
                </div>
              ))}

              {medInfo.safe.slice(0, 3).map((m: string, i: number) => (
                <div key={i} className="px-3 py-2.5 bg-white/[0.02] border border-white/5 rounded-xl flex items-center justify-between group hover:bg-white/[0.05] transition-colors">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/40 group-hover:bg-emerald-500 transition-colors shadow"></div>
                    <p className="text-[9px] text-slate-400 font-bold group-hover:text-slate-200 uppercase truncate max-w-[100px]">{m}</p>
                  </div>
                  <span className="text-[7px] font-black text-emerald-500/40 tracking-wider">SAFE</span>
                </div>
              ))}

              {patient?.medications === "" && (
                <div className="text-center py-6">
                  <p className="text-[9px] text-slate-600 italic uppercase font-bold tracking-widest">No medications listed</p>
                </div>
              )}
            </div>
          </div>

          {/* Node Telemetry */}
          <div className="glass-card p-6 rounded-[2rem] flex-1 flex flex-col bg-white/[0.01] border border-white/5 overflow-hidden">
            <h3 className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-6 border-b border-white/5 pb-3 flex items-center gap-2">
              <Gauge className="w-3.5 h-3.5 text-blue-500" /> Node Telemetry
            </h3>

            <div className="text-[9px] font-mono text-slate-500 space-y-3 flex-1">
              {[
                { l: 'Node Status', v: telemetry.status === 'ready' ? 'ONLINE' : 'DEGRADED', c: telemetry.status === 'ready' ? 'text-emerald-500' : 'text-amber-500' },
                { l: 'DB Link', v: telemetry.dependencies.db.toUpperCase(), c: telemetry.dependencies.db === 'healthy' ? 'text-emerald-500' : 'text-red-500' },
                { l: 'Redis/Cache', v: telemetry.dependencies.redis.toUpperCase(), c: telemetry.dependencies.redis === 'healthy' ? 'text-emerald-500' : 'text-red-500' },
                { l: 'NATS/Queue', v: telemetry.dependencies.nats.toUpperCase(), c: telemetry.dependencies.nats === 'healthy' ? 'text-emerald-500' : 'text-red-500' },
                { l: 'Latency', v: `${telemetry.latency}ms`, c: 'text-amber-500' }
              ].map((t, idx) => (
                <div key={idx} className="flex justify-between uppercase p-2 rounded-lg hover:bg-white/[0.02] transition-colors">
                  <span className="font-bold tracking-tighter opacity-70">{t.l}</span>
                  <span className={`font-black ${t.c}`}>{t.v}</span>
                </div>
              ))}

              <div className="pt-6 mt-6 border-t border-white/5 space-y-4">
                <p className="text-white font-black text-[9px] uppercase tracking-[0.3em] mb-2 opacity-50">Model Weights</p>
                {(data?.model_precisions || []).map((m: ModelPrecision) => (
                  <div key={m.model_name} className="space-y-1">
                    <div className="flex justify-between text-slate-500 uppercase tracking-tighter text-[7.5px] font-black">
                      <span>{m.model_name}</span>
                      <span className="text-blue-500">{m.confidence.toFixed(1)}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${m.confidence}%` }}
                        className="h-full bg-gradient-to-r from-blue-600 to-blue-400"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

      </div>
      <DiseaseCheckerModal isOpen={showDiseaseModal} onClose={() => setShowDiseaseModal(false)} />
    </main>
  );
}
