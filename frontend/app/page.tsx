"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
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

// --- Types ---
interface RiskScores {
  heart_risk_score: number;
  diabetes_risk_score: number;
  stroke_risk_score: number;
  kidney_risk_score: number;
  general_health_score: number;
  clinical_confidence: number;
}

interface Patient {
  id: number;
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
}

interface AssessmentResponse {
  id: number;
  risks: RiskScores;
  diagnosis: string;
  diagnosis_status: string; // "pending", "ready", "error"
  emergency: boolean;
  patient: Patient;
  medication_analysis: { risky: string[]; safe: string[] };
  model_precisions: { model_name: string; confidence: number }[];
}

export default function ClinicalCockpit() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<AssessmentResponse | null>(null);
  const [emergency, setEmergency] = useState(false);
  const [patients, setPatients] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [latency, setLatency] = useState(0);

  const [patient, setPatient] = useState<Patient | null>(null);

  const fetchPatients = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:3000/api/patients");
      const list = await res.json();
      setPatients(list);
      return list;
    } catch (err) {
      console.error("Failed to fetch patients", err);
      return [];
    }
  }, []);

  const runAssessment = useCallback(async (pOverride?: any) => {
    setLoading(true);
    const start = performance.now();
    const target = pOverride || patient;
    try {
      const res = await fetch("http://localhost:3000/api/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(target),
      });
      const result = await res.json();
      setData(result);
      setEmergency(result.emergency);
      if (result.patient) setPatient(result.patient);
      await fetchPatients();

      const end = performance.now();
      setLatency(Math.round(end - start));

      // Start polling for diagnosis if status is pending
      if (result.diagnosis_status === "pending" && result.patient?.id) {
        pollForDiagnosis(result.patient.id);
      }
    } catch (error) {
      console.error("Assessment failed", error);
    } finally {
      setTimeout(() => setLoading(false), 200);
      setShowModal(false);
    }
  }, [patient, fetchPatients]);

  const pollForDiagnosis = useCallback(async (patientId: number) => {
    const maxAttempts = 30;
    let attempts = 0;

    const poll = async () => {
      if (attempts >= maxAttempts) return;
      attempts++;

      try {
        const res = await fetch(`http://localhost:3000/api/diagnosis/${patientId}`);
        const result = await res.json();

        if (result.status === "ready" || result.status === "error") {
          setData(prev => prev ? { ...prev, diagnosis: result.diagnosis, diagnosis_status: result.status } : prev);
        } else {
          setTimeout(poll, 1000);
        }
      } catch {
        setTimeout(poll, 1000);
      }
    };

    setTimeout(poll, 500);
  }, []);

  useEffect(() => {
    let active = true;
    const init = async () => {
      setLoading(true);
      const list = await fetchPatients();
      if (!active) return;
      if (list && list.length > 0) {
        setPatient(list[0]);
        await runAssessment(list[0]);
      } else {
        await runAssessment();
      }
    };
    init();
    return () => { active = false; };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const selectPatient = (p: any) => {
    if (patient && p.id === patient.id && data) return;
    setPatient(p);
    runAssessment(p);
  };

  const medInfo = useMemo(() => {
    if (data?.medication_analysis) {
      return data.medication_analysis;
    }
    return { risky: [], safe: [] };
  }, [data]);

  // Loading Screen
  if (!patient) {
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
          <PatientSidebar patients={patients} selectedId={patient.id} onSelect={selectPatient} />
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
                {patient.smoking === 'Yes' && (
                  <span className="text-[8px] bg-amber-500/10 text-amber-500 px-2.5 py-1 rounded-md font-black tracking-wider border border-amber-500/10">SMOKER</span>
                )}
                {patient.alcohol === 'Yes' && (
                  <span className="text-[8px] bg-purple-500/10 text-purple-500 px-2.5 py-1 rounded-md font-black tracking-wider border border-purple-500/10">ALCOHOL</span>
                )}
              </div>
            </div>

            <div className="shrink-0">
              <VitalsGrid patient={patient} />
            </div>

            <div className="mt-4 flex-1 overflow-y-auto custom-scrollbar pr-1 -mr-1">
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
            <RiskAnalysis risks={data?.risks} />
          </div>

          <DiagnosisPanel
            diagnosis={data?.diagnosis || ""}
            status={data?.diagnosis_status || "pending"}
            loading={loading}
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
              {medInfo.risky.map((m, i) => (
                <div key={i} className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 group hover:bg-red-500/15 transition-colors">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-3 h-3 text-red-500 animate-pulse" />
                    <p className="text-[8px] font-black uppercase text-red-500 tracking-wider">Detection</p>
                  </div>
                  <p className="text-[10px] text-white font-bold italic tracking-tight">{m}</p>
                  <p className="text-[8px] text-red-400/60 mt-1 font-semibold">Interaction Warning</p>
                </div>
              ))}

              {medInfo.safe.slice(0, 3).map((m, i) => (
                <div key={i} className="px-3 py-2.5 bg-white/[0.02] border border-white/5 rounded-xl flex items-center justify-between group hover:bg-white/[0.05] transition-colors">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/40 group-hover:bg-emerald-500 transition-colors shadow"></div>
                    <p className="text-[9px] text-slate-400 font-bold group-hover:text-slate-200 uppercase truncate max-w-[100px]">{m}</p>
                  </div>
                  <span className="text-[7px] font-black text-emerald-500/40 tracking-wider">SAFE</span>
                </div>
              ))}

              {patient.medications === "" && (
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
                { l: 'Node Status', v: 'ONLINE', c: 'text-emerald-500' },
                { l: 'Health Score', v: `${data?.risks.general_health_score?.toFixed(1) || '0.0'}%`, c: 'text-blue-400' },
                { l: 'Precision', v: `${data?.risks.clinical_confidence || '0.0'}%`, c: 'text-slate-200' },
                { l: 'Latency', v: `${latency}ms`, c: 'text-amber-500' }
              ].map((t, idx) => (
                <div key={idx} className="flex justify-between uppercase p-2 rounded-lg hover:bg-white/[0.02] transition-colors">
                  <span className="font-bold tracking-tighter opacity-70">{t.l}</span>
                  <span className={`font-black ${t.c}`}>{t.v}</span>
                </div>
              ))}

              <div className="pt-6 mt-6 border-t border-white/5 space-y-4">
                <p className="text-white font-black text-[9px] uppercase tracking-[0.3em] mb-2 opacity-50">Model Weights</p>
                {(data?.model_precisions || []).map((m: any) => (
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
    </main>
  );
}
