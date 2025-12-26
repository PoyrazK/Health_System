"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import * as Lucide from "lucide-react";
const {
  Activity: ActivityIco,
  AlertTriangle: AlertIco,
  Brain: BrainIco,
  Dna: DnaIco,
  Heart: HeartIco,
  ShieldAlert: ShieldIco,
  Stethoscope: StethIco,
  Thermometer: ThermoIco,
  Wind: WindIco,
  PlusCircle: PlusIco,
  X: XIco,
  UserPlus: UserPlusIco,
  Zap: ZapIco,
  Flame: FlameIco,
  Droplets: DropIco,
  Gauge: GaugeIco,
  Wifi: WifiIco,
  ChevronRight
} = Lucide;

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

// --- Components ---

const FeedbackPanel = ({ assessmentId, risks }: any) => {
  const [approved, setApproved] = useState<boolean | null>(null);
  const [notes, setNotes] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const submitFeedback = async () => {
    try {
      await fetch("http://localhost:3000/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          assessment_id: String(assessmentId),
          doctor_approved: approved,
          doctor_notes: notes,
          risk_profile: JSON.stringify(risks)
        }),
      });
      setSubmitted(true);
    } catch (e) { }
  };

  if (submitted) return <div className="text-emerald-500 text-[10px] font-black animate-pulse py-4 tracking-widest border-t border-white/5">✓ CLINICAL MEMORY SYNCHRONIZED</div>;

  return (
    <div className="mt-6 pt-6 border-t border-white/5">
      <h4 className="text-[10px] font-bold text-slate-500 uppercase mb-3 tracking-widest">Validation Terminal</h4>
      <div className="flex gap-2 mb-4">
        <button
          onClick={(e) => { e.stopPropagation(); setApproved(true); }}
          className={`flex-1 py-2 text-[10px] font-bold rounded-lg border transition-all ${approved === true ? 'bg-emerald-500/20 border-emerald-500 text-emerald-500' : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'}`}
        >
          APPROVE
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); setApproved(false); }}
          className={`flex-1 py-2 text-[10px] font-bold rounded-lg border transition-all ${approved === false ? 'bg-red-500/20 border-red-500 text-red-500' : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'}`}
        >
          CORRECT
        </button>
      </div>
      <textarea
        placeholder="Clinical observations..."
        className="w-full bg-black/40 border border-white/5 rounded-xl p-3 text-[10px] text-slate-300 focus:outline-none focus:border-blue-500/50 h-16 resize-none"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        onClick={(e) => e.stopPropagation()}
      />
      <button
        onClick={(e) => { e.stopPropagation(); submitFeedback(); }}
        className="w-full mt-3 py-2 bg-blue-600 text-[10px] font-bold rounded-lg hover:bg-blue-500 transition-all uppercase tracking-widest text-white disabled:opacity-50"
        disabled={approved === null}
      >
        Commit to Memory
      </button>
    </div>
  );
};

const PatientQueue = ({ patients, selectedId, onSelect }: any) => {
  return (
    <div className="glass-card h-full rounded-2xl overflow-hidden flex flex-col border border-white/5">
      <div className="p-6 border-b border-white/5 bg-white/[0.02] shrink-0">
        <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-1">Live Queue</h3>
        <p className="text-[10px] text-slate-400 italic">Clinical Node Active</p>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {patients.map((p: any) => (
          <button
            key={p.id}
            onClick={() => onSelect(p)}
            className={`w-full p-4 border-b border-white/5 text-left transition-all hover:bg-white/5 ${selectedId === p.id ? 'bg-blue-600/10 border-l-4 border-l-blue-500' : ''}`}
          >
            <div className="flex justify-between items-start mb-1 text-nowrap overflow-hidden">
              <span className="text-[10px] font-black text-white uppercase truncate tracking-tighter">Case {p.id.toString().padStart(4, '0')}</span>
              <span className={`text-[8px] font-black px-1.5 py-0.5 rounded ml-2 ${p.systolic_bp > 160 ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-emerald-500/20 text-emerald-500'}`}>
                {p.systolic_bp > 160 ? 'CRITICAL' : 'STABLE'}
              </span>
            </div>
            <p className="text-[9px] text-slate-500 font-medium">{p.age}y / {p.gender} / BP {p.systolic_bp}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

const IntakeModal = ({ isOpen, onClose, onSubmit }: any) => {
  const [form, setForm] = useState<any>(null);
  const [loadingDefaults, setLoadingDefaults] = useState(false);

  useEffect(() => {
    if (isOpen && !form) {
      setLoadingDefaults(true);
      fetch("http://localhost:3000/api/defaults")
        .then(res => res.json())
        .then(data => {
          setForm(data);
          setLoadingDefaults(false);
        })
        .catch(() => {
          // Fallback if backend is not available
          setForm({
            age: 45, gender: 'Male', systolic_bp: 120, diastolic_bp: 80,
            glucose: 100, bmi: 24.5, cholesterol: 190, heart_rate: 72, steps: 6000,
            smoking: 'No', alcohol: 'No', medications: 'Lisinopril, Atorvastatin'
          });
          setLoadingDefaults(false);
        });
    }
  }, [isOpen, form]);

  if (!isOpen) return null;
  if (loadingDefaults || !form) return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/90 backdrop-blur-md" />
      <div className="text-white text-sm">Loading form defaults...</div>
    </div>
  );

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/90 backdrop-blur-md" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="glass-card w-full max-w-2xl rounded-3xl p-8 relative z-10 border border-white/10 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-3">
            <UserPlusIco className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl font-black text-white uppercase italic tracking-tighter">Clinical Intake Protocol</h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-all text-slate-600 hover:text-white">
            <XIco className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar pb-4">
          {Object.keys(form).map((key) => (
            <div key={key} className={`space-y-1.5 ${key === 'medications' ? 'col-span-3' : ''}`}>
              <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{key.replace('_', ' ')}</label>
              {key === 'gender' ? (
                <select
                  className="w-full bg-white/5 border border-white/5 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/50 appearance-none"
                  value={(form as any)[key]}
                  onChange={(e) => setForm({ ...form, gender: e.target.value })}
                >
                  <option value="Male" className="bg-slate-900">Male</option>
                  <option value="Female" className="bg-slate-900">Female</option>
                </select>
              ) : key === 'smoking' || key === 'alcohol' ? (
                <select
                  className="w-full bg-white/5 border border-white/5 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/50 appearance-none"
                  value={(form as any)[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                >
                  <option value="No" className="bg-slate-900">No</option>
                  <option value="Yes" className="bg-slate-900">Yes</option>
                </select>
              ) : (
                <input
                  type={typeof (form as any)[key] === 'number' ? 'number' : 'text'}
                  className="w-full bg-white/5 border border-white/5 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/50 transition-all font-medium"
                  value={(form as any)[key]}
                  onChange={(e) => setForm({ ...form, [key]: typeof (form as any)[key] === 'number' ? (e.target.value === '' ? 0 : Number(e.target.value)) : e.target.value })}
                />
              )}
            </div>
          ))}
        </div>

        <button
          onClick={() => onSubmit(form)}
          className="w-full mt-6 py-4 bg-blue-600 text-white font-black tracking-[0.2em] rounded-2xl hover:bg-blue-500 transition-all uppercase shadow-2xl shadow-blue-600/30"
        >
          Initialize AI Diagnostics
        </button>
      </motion.div>
    </div>
  );
};

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

  // Poll for async diagnosis result
  const pollForDiagnosis = useCallback(async (patientId: number) => {
    const maxAttempts = 30; // Max 30 seconds
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
          // Still pending, poll again in 1 second
          setTimeout(poll, 1000);
        }
      } catch {
        // Retry on error
        setTimeout(poll, 1000);
      }
    };

    // Start polling after 500ms
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

  // Medication Safety Parser - Connected to Backend
  const medInfo = useMemo(() => {
    if (data?.medication_analysis) {
      return data.medication_analysis;
    }
    return { risky: [], safe: [] };
  }, [data]);

  // Show loading state if patient data hasn't loaded yet
  if (!patient) {
    return (
      <main className="fixed inset-0 bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[10px] font-black text-blue-500 tracking-[0.5em] uppercase animate-pulse">Loading Patient Data...</p>
        </div>
      </main>
    );
  }

  return (
    <main className={`fixed inset-0 p-4 font-sans transition-all duration-1000 overflow-hidden flex flex-col ${emergency ? 'bg-red-950/30' : 'bg-[#050505]'}`}>

      <IntakeModal isOpen={showModal} onClose={() => setShowModal(false)} onSubmit={runAssessment} />

      <AnimatePresence>
        {emergency && (
          <motion.div
            key="emergency-pulse"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 pointer-events-none border-[12px] border-red-500/20 animate-pulse z-50 ring-inset ring-[60px] ring-red-500/5 shadow-[inset_0_0_150px_rgba(239,68,68,0.3)]"
          />
        )}
      </AnimatePresence>

      {/* Header HUD */}
      <div className="flex justify-between items-center mb-4 px-2 relative z-10 shrink-0 h-14">
        <div className="flex items-center gap-6">
          <div className="h-10 w-10 rounded-full border border-white/10 flex items-center justify-center bg-white/5">
            <StethIco className={`w-5 h-5 ${emergency ? 'text-red-500 animate-pulse' : 'text-blue-500'}`} />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <div className={`w-1.5 h-1.5 rounded-full transition-colors ${emergency ? 'bg-red-500 animate-ping' : 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'}`} />
              <h2 className={`text-[9px] font-black tracking-[0.4em] uppercase ${emergency ? 'text-red-500' : 'text-slate-500'}`}>
                {emergency ? "CRITICAL ASSESSMENT OVERRIDE" : "NEURAL CLINICAL INTEGRATION"}
              </h2>
            </div>
            <h1 className="text-xl font-black text-white tracking-widest uppercase italic leading-none">Clinical Copilot v1.9</h1>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="px-4 py-2 rounded-2xl bg-white/5 border border-white/5 flex items-center gap-3">
            <WifiIco className={`w-3.5 h-3.5 ${latency < 100 ? 'text-emerald-500' : 'text-amber-500'}`} />
            <div className="text-left">
              <p className="text-[7px] font-bold text-slate-500 uppercase tracking-widest">Network Latency</p>
              <p className="text-[10px] font-black text-white">{latency}ms</p>
            </div>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="px-8 py-2 rounded-2xl bg-blue-600 text-[11px] font-black tracking-[0.2em] text-white hover:bg-blue-500 transition-all uppercase shadow-2xl shadow-blue-600/30 flex items-center gap-2 disabled:opacity-50"
            disabled={loading}
          >
            <PlusIco className="w-4 h-4" /> New Assessment
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-5 min-h-0 relative z-10">

        {/* Patient Queue */}
        <div className="col-span-2 h-full min-h-0">
          <PatientQueue patients={patients} selectedId={patient.id} onSelect={selectPatient} />
        </div>

        {/* Biometrics */}
        <div className="col-span-3 flex flex-col h-full min-h-0">
          <div className={`glass-card p-6 rounded-[2rem] transition-all duration-700 flex flex-col h-full border border-white/5 bg-gradient-to-b from-white/[0.03] to-transparent ${emergency ? 'border-red-500/40 shadow-[0_0_40px_rgba(239,68,68,0.15)]' : ''}`}>
            <div className="flex justify-between items-center mb-8 pb-4 border-b border-white/5">
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Telemetry Stream</h3>
              <div className="flex gap-1.5">
                {patient.smoking === 'Yes' && <span className="text-[8px] bg-amber-500/20 text-amber-500 px-2 py-0.5 rounded-full font-black tracking-tighter border border-amber-500/20">SMOKER</span>}
                {patient.alcohol === 'Yes' && <span className="text-[8px] bg-purple-500/20 text-purple-500 px-2 py-0.5 rounded-full font-black tracking-tighter border border-purple-500/20">ALCOHOL</span>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 shrink-0">
              {[
                { l: 'Systolic BP', v: patient.systolic_bp, u: 'mmHg', i: ZapIco, c: patient.systolic_bp > 160 },
                { l: 'Diastolic BP', v: patient.diastolic_bp, u: 'mmHg', i: ActivityIco, c: false },
                { l: 'Heart Rate', v: patient.heart_rate, u: 'BPM', i: HeartIco, c: patient.heart_rate > 100 },
                { l: 'Glucose', v: patient.glucose, u: 'mg/dL', i: DropIco, c: patient.glucose > 180 },
                { l: 'Cholesterol', v: patient.cholesterol, u: 'mg/dL', i: WindIco, c: patient.cholesterol > 240 },
                { l: 'BMI Index', v: patient.bmi, u: 'kg/m²', i: ThermoIco, c: false }
              ].map((bio, idx) => (
                <div key={idx} className={`p-4 rounded-2xl border transition-all duration-500 ${bio.c ? 'bg-red-500/10 border-red-500/30 ring-1 ring-red-500/20' : 'bg-white/[0.02] border-white/5 hover:border-white/10'}`}>
                  <div className="flex justify-between items-center mb-1.5">
                    <p className="text-[8px] font-black text-slate-500 uppercase tracking-tighter">{bio.l}</p>
                    <bio.i className={`w-3 h-3 ${bio.c ? 'text-red-500' : 'text-slate-600'}`} />
                  </div>
                  <div className="flex items-baseline gap-1">
                    <p className={`text-xl font-black tracking-tighter ${bio.c ? 'text-red-500' : 'text-white'}`}>{bio.v || 0}</p>
                    <span className="text-[8px] text-slate-600 font-bold uppercase">{bio.u}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex-1 overflow-y-auto custom-scrollbar pr-1 -mr-1">
              {data && <FeedbackPanel assessmentId={data.id} risks={data.risks} />}
            </div>

            <div className="mt-auto pt-6 border-t border-white/5 shrink-0">
              <div className="flex justify-between items-end mb-2.5">
                <div className="flex gap-2 items-center">
                  <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Confidence Index</span>
                  <span className={`text-[10px] font-black ${data?.risks.clinical_confidence && data.risks.clinical_confidence > 90 ? 'text-emerald-500' : 'text-amber-500'}`}>
                    {data?.risks.clinical_confidence || '0.0'}%
                  </span>
                </div>
                <span className="text-[8px] font-bold text-slate-600 uppercase italic">Neural Verified</span>
              </div>
              <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${data?.risks.clinical_confidence || 0}%` }}
                  className={`h-full shadow-[0_0_15px_rgba(59,130,246,0.3)] ${data?.risks.clinical_confidence && data.risks.clinical_confidence > 90 ? 'bg-emerald-500' : 'bg-blue-500'}`}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Intelligence Core */}
        <div className="col-span-5 flex flex-col gap-5 h-full min-h-0">
          <div className="grid grid-cols-4 gap-4 shrink-0">
            {[
              { t: 'Heart', s: data?.risks.heart_risk_score || 0, i: HeartIco, c: 'text-red-500', bg: 'bg-red-500/5' },
              { t: 'Diabetes', s: data?.risks.diabetes_risk_score || 0, i: ActivityIco, c: 'text-emerald-500', bg: 'bg-emerald-500/5' },
              { t: 'Stroke', s: data?.risks.stroke_risk_score || 0, i: BrainIco, c: 'text-purple-500', bg: 'bg-purple-500/5' },
              { t: 'Kidney', s: data?.risks.kidney_risk_score || 0, i: StethIco, c: 'text-blue-500', bg: 'bg-blue-500/5' }
            ].map((r, i) => (
              <div key={i} className={`glass-card p-5 rounded-3xl border border-white/5 flex flex-col items-center text-center group transition-all duration-500 hover:border-white/20 ${r.bg}`}>
                <r.i className={`w-6 h-6 mb-3 group-hover:scale-110 transition-transform ${r.s > 70 ? 'text-red-500' : r.s > 40 ? 'text-amber-500' : r.c}`} />
                <p className="text-[9px] font-black text-slate-600 uppercase mb-1 tracking-widest">{r.t}</p>
                <p className="text-2xl font-black text-white tracking-tighter">{r.s.toFixed(0)}%</p>
              </div>
            ))}
          </div>

          <div className="glass-card flex-1 rounded-[3rem] p-10 relative overflow-hidden bg-gradient-to-br from-black to-blue-950/20 border border-white/5 shadow-inner">
            <div className="flex justify-between items-center mb-10 relative z-10 shrink-0">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center ring-1 ring-blue-500/20">
                  <DnaIco className="w-5 h-5 text-blue-500 animate-pulse" />
                </div>
                <div>
                  <h2 className="text-[11px] font-black tracking-[0.3em] text-white uppercase italic">Neural Differential assessment</h2>
                  <p className="text-[8px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Gemini 1.5 Flash Engine Active</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span className="text-[10px] font-black text-emerald-500/80 tracking-widest">SYSTEM_LIVE</span>
              </div>
            </div>

            <div className="relative h-full">
              <AnimatePresence>
                {loading && (
                  <motion.div
                    key="loader-overlay"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="absolute inset-0 z-20 bg-black/70 backdrop-blur-xl rounded-2xl flex flex-col items-center justify-center gap-6 border border-blue-500/10"
                  >
                    <div className="relative">
                      <div className="w-16 h-16 border-[4px] border-blue-500/10 rounded-full" />
                      <div className="w-16 h-16 border-[4px] border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0 shadow-[0_0_20px_rgba(59,130,246,0.5)]" />
                    </div>
                    <div className="text-center">
                      <p className="text-[10px] font-black text-blue-500 tracking-[0.5em] uppercase animate-pulse">Analyzing Case Architecture...</p>
                      <p className="text-[8px] text-slate-600 mt-2 font-bold italic">Synthesizing Clinical Intelligence</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="h-full overflow-y-auto custom-scrollbar pr-6 pb-24 selection:bg-blue-600/50">
                <motion.div
                  animate={{
                    opacity: loading ? 0.2 : 1,
                    y: loading ? 20 : 0,
                    filter: loading ? 'blur(10px)' : 'blur(0px)'
                  }}
                  transition={{ duration: 0.6, ease: "easeOut" }}
                  className="prose prose-invert prose-xs max-w-none text-slate-300 leading-relaxed font-medium"
                >
                  {data?.diagnosis_status === "pending" ? (
                    <div className="flex items-center gap-3">
                      <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                      <span className="text-blue-400 animate-pulse">Neural synthesis in progress...</span>
                    </div>
                  ) : (
                    <ReactMarkdown>{data?.diagnosis || "Awaiting clinical intelligence handshaking..."}</ReactMarkdown>
                  )}
                </motion.div>
              </div>
            </div>
          </div>
        </div>

        {/* Safety & Analytics */}
        <div className="col-span-2 space-y-5 flex flex-col h-full min-h-0">
          {/* Med Safety Section */}
          <div className="glass-card p-6 rounded-[2rem] bg-white/[0.01] shrink-0 border border-white/5">
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-5 pb-2 border-b border-white/5 flex items-center gap-2">
              <ShieldIco className="w-3 h-3" /> Medication Security
            </h3>
            <div className="space-y-3">
              {medInfo.risky.map((m, i) => (
                <div key={i} className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertIco className="w-3 h-3 text-red-500" />
                    <p className="text-[8px] font-black uppercase text-red-500">Caution Required</p>
                  </div>
                  <p className="text-[11px] text-white font-black italic tracking-tight">{m}</p>
                  <p className="text-[8px] text-red-400/60 mt-1.5 font-bold">Possible conflict detected.</p>
                </div>
              ))}

              {medInfo.safe.slice(0, 2).map((m, i) => (
                <div key={i} className="px-4 py-3 bg-white/[0.01] border border-white/5 rounded-2xl flex items-center justify-between group">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/40 group-hover:bg-emerald-500 transition-colors"></div>
                    <p className="text-[10px] text-slate-400 font-bold group-hover:text-slate-200 transition-colors uppercase">{m}</p>
                  </div>
                  <span className="text-[8px] font-black text-emerald-500/40">SAFE</span>
                </div>
              ))}

              {patient.medications === "" && (
                <p className="text-[9px] text-slate-600 italic text-center py-4 uppercase font-bold tracking-widest">No medications listed</p>
              )}
            </div>
          </div>

          {/* Telemetry Section */}
          <div className="glass-card p-7 rounded-[2rem] flex-1 flex flex-col bg-white/[0.01] border border-white/5 overflow-hidden">
            <h3 className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-8 border-b border-white/5 pb-3 flex items-center gap-2">
              <GaugeIco className="w-3.5 h-3.5 text-blue-500" /> Node Telemetry
            </h3>

            <div className="text-[9px] font-mono text-slate-600 space-y-4 flex-1">
              {[
                { l: 'Node Status', v: 'ONLINE', c: 'text-emerald-500' },
                { l: 'Health Score', v: `${data?.risks.general_health_score?.toFixed(1) || '0.0'}%`, c: 'text-blue-400' },
                { l: 'Precision', v: `${data?.risks.clinical_confidence || '0.0'}%`, c: '' },
                { l: 'Latency', v: `${latency}ms`, c: '' }
              ].map((t, idx) => (
                <div key={idx} className="flex justify-between uppercase">
                  <span className="font-bold tracking-tighter opacity-60">{t.l}</span>
                  <span className={`font-black ${t.c || 'text-slate-300'}`}>{t.v}</span>
                </div>
              ))}

              <div className="pt-8 mt-8 border-t border-white/5 space-y-5">
                <p className="text-white font-black text-[9px] uppercase tracking-[0.3em] mb-4">Precision Mapping</p>
                {(data?.model_precisions || []).map((m: any) => {
                  return (
                    <div key={m.model_name} className="space-y-1.5">
                      <div className="flex justify-between text-slate-500 uppercase tracking-tighter text-[7.5px] font-black">
                        <span>{m.model_name}</span>
                        <span className="text-blue-500/80">{m.confidence.toFixed(1)}%</span>
                      </div>
                      <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${m.confidence}%` }}
                          className="h-full bg-blue-500/30"
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

      </div>
    </main>
  );
}
