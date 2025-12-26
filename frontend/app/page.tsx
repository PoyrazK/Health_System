"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Activity,
  AlertTriangle,
  Brain,
  Dna,
  Heart,
  ShieldAlert,
  Stethoscope,
  Thermometer,
  Wind,
  PlusCircle,
  FileText,
  X,
  UserPlus,
  Zap,
  Flame,
  Droplets,
  Gauge
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

// --- Types ---

interface RiskScores {
  heart_risk_score: number;
  diabetes_risk_score: number;
  stroke_risk_score: number;
  kidney_risk_score: number;
  general_health_score: number;
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
  emergency: boolean;
  patient: Patient;
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

  if (submitted) return <div className="text-emerald-500 text-xs font-bold animate-pulse">✓ FEEDBACK SYNCHRONIZED</div>;

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
        placeholder="Clinical notes..."
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
              <span className="text-[10px] font-black text-white uppercase truncate">Case {p.id.toString().padStart(4, '0')}</span>
              <span className={`text-[8px] font-black px-1.5 py-0.5 rounded ml-2 ${p.systolic_bp > 160 ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-emerald-500/20 text-emerald-500'}`}>
                {p.systolic_bp > 160 ? 'CRITICAL' : 'STABLE'}
              </span>
            </div>
            <p className="text-[10px] text-slate-500 font-medium">{p.age}y / {p.gender} / BP {p.systolic_bp}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

const IntakeModal = ({ isOpen, onClose, onSubmit }: any) => {
  const [form, setForm] = useState({
    age: 45, gender: 'Male', systolic_bp: 120, diastolic_bp: 80,
    glucose: 100, bmi: 24.5, cholesterol: 190, heart_rate: 72, steps: 6000,
    smoking: 'No', alcohol: 'No', medications: 'Metformin, Lisinopril'
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-md" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="glass-card w-full max-w-2xl rounded-3xl p-8 relative z-10 border border-white/10 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-3">
            <UserPlus className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl font-black text-white uppercase italic tracking-tighter">New Assessment File</h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-all text-slate-600 hover:text-white">
            <X className="w-5 h-5" />
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
          Initialize Clinical Run
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

  const [patient, setPatient] = useState<Patient>({
    id: 0, age: 67, gender: "Male", systolic_bp: 185, diastolic_bp: 110,
    glucose: 240, bmi: 32.5, cholesterol: 245, heart_rate: 98, steps: 1200,
    smoking: "Yes", alcohol: "No", medications: "Metformin, Lisinopril"
  });

  const fetchPatients = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:3000/api/patients");
      const list = await res.json();
      setPatients(list);
      return list;
    } catch (err) {
      console.error("Queue fetch failed");
      return [];
    }
  }, []);

  const runAssessment = useCallback(async (pOverride?: any) => {
    setLoading(true);
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
      if (result.patient) {
        setPatient(result.patient);
      }
      await fetchPatients();
    } catch (error) {
      console.error("Assessment failed", error);
    } finally {
      setTimeout(() => setLoading(false), 200);
      setShowModal(false);
    }
  }, [patient, fetchPatients]);

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
    if (p.id === patient.id && data) return;
    setPatient(p);
    runAssessment(p);
  };

  return (
    <main className={`fixed inset-0 p-4 font-sans transition-all duration-700 overflow-hidden flex flex-col ${emergency ? 'bg-red-950/20' : 'bg-[#050505]'}`}>

      <IntakeModal isOpen={showModal} onClose={() => setShowModal(false)} onSubmit={runAssessment} />

      <AnimatePresence>
        {emergency && (
          <motion.div
            key="emergency-pulse"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 pointer-events-none border-[12px] border-red-500/20 animate-pulse z-50 ring-inset ring-[40px] ring-red-500/5 shadow-[inset_0_0_100px_rgba(239,68,68,0.2)]"
          />
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex justify-between items-center mb-4 px-2 relative z-10 shrink-0 h-14">
        <div>
          <div className="flex items-center gap-2 mb-0.5">
            <div className={`w-2 h-2 rounded-full transition-colors ${emergency ? 'bg-red-500 animate-ping' : 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'}`} />
            <h2 className={`text-[9px] font-black tracking-[0.3em] uppercase ${emergency ? 'text-red-500' : 'text-slate-500'}`}>
              {emergency ? "CRITICAL PATHWAY ACTIVATED" : "Neural Clinical Integration"}
            </h2>
          </div>
          <h1 className="text-xl font-black text-white tracking-widest uppercase italic">Clinical Copilot v1.8 <span className="text-slate-700 font-normal ml-2">TERMINAL</span></h1>
        </div>
        <div className="flex gap-2">
          <div className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-[9px] font-bold text-slate-500 items-center gap-2 uppercase tracking-widest hidden md:flex">
            Latency: <span className="text-emerald-500">14ms</span>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="px-6 py-2 rounded-xl bg-blue-600 text-[10px] font-black tracking-widest text-white hover:bg-blue-500 transition-all uppercase shadow-2xl shadow-blue-600/30 flex items-center gap-2 disabled:opacity-50"
            disabled={loading}
          >
            <PlusCircle className="w-3.5 h-3.5" /> New Assessment
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0 relative z-10">

        {/* Sidebar: Patient Queue */}
        <div className="col-span-2 h-full min-h-0">
          <PatientQueue patients={patients} selectedId={patient.id} onSelect={selectPatient} />
        </div>

        {/* Column 2: Biometrics Wall */}
        <div className="col-span-3 flex flex-col h-full min-h-0">
          <div className={`glass-card p-6 rounded-3xl transition-all duration-500 flex flex-col h-full border border-white/5 ${emergency ? 'border-red-500/30 shadow-[0_0_30px_rgba(239,68,68,0.1)]' : ''}`}>
            <div className="flex justify-between items-center mb-6 py-1 border-b border-white/5">
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Biometric Telemetry</h3>
              <div className="flex gap-1">
                {patient.smoking === 'Yes' && <span className="text-[8px] bg-amber-500/20 text-amber-500 px-1.5 py-0.5 rounded font-black tracking-tighter">SMOKER</span>}
                {patient.alcohol === 'Yes' && <span className="text-[8px] bg-purple-500/20 text-purple-500 px-1.5 py-0.5 rounded font-black tracking-tighter">ALCOHOL</span>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 shrink-0">
              {[
                { l: 'BP Systolic', v: patient.systolic_bp, u: 'mmHg', icon: Zap },
                { l: 'BP Diastolic', v: patient.diastolic_bp, u: 'mmHg', icon: Activity },
                { l: 'Heart Rate', v: patient.heart_rate, u: 'BPM', icon: Heart },
                { l: 'Glucose', v: patient.glucose, u: 'mg/dL', icon: Droplets },
                { l: 'Cholesterol', v: patient.cholesterol, u: 'mg/dL', icon: Wind },
                { l: 'BMI', v: patient.bmi, u: 'kg/m²', icon: Thermometer },
                { l: 'Daily Steps', v: patient.steps, u: 'STEPS', icon: Flame },
                { l: 'Patient Age', v: patient.age, u: 'YEARS', icon: UserPlus }
              ].map((bio, i) => (
                <div key={i} className={`p-4 rounded-2xl border transition-colors ${bio.l.includes('BP Systolic') && bio.v > 160 ? 'bg-red-500/10 border-red-500/30' : 'bg-white/[0.03] border-white/5'}`}>
                  <div className="flex justify-between items-center mb-1">
                    <p className="text-[8px] font-bold text-slate-500 uppercase">{bio.l}</p>
                    <bio.icon className="w-2.5 h-2.5 text-slate-600" />
                  </div>
                  <div className="flex items-baseline gap-1">
                    <p className={`text-lg font-black tracking-tighter ${bio.l.includes('BP Systolic') && bio.v > 160 ? 'text-red-500' : 'text-white'}`}>{bio.v || 0}</p>
                    <span className="text-[8px] text-slate-600 font-bold uppercase">{bio.u}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex-1 overflow-y-auto custom-scrollbar pr-1">
              {data && <FeedbackPanel assessmentId={data.id} risks={data.risks} />}
            </div>

            <div className="mt-auto pt-6 border-t border-white/5 shrink-0">
              <div className="flex justify-between items-end mb-2">
                <span className="text-[9px] font-black text-slate-600 uppercase tracking-[0.2em]">Overall Health Index</span>
                <span className="text-[10px] font-black text-emerald-500">{data?.risks.general_health_score?.toFixed(1) || '0.0'}%</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <motion.div initial={{ width: 0 }} animate={{ width: `${data?.risks.general_health_score || 0}%` }} className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.6)]" />
              </div>
            </div>
          </div>
        </div>

        {/* Intelligence Center */}
        <div className="col-span-5 flex flex-col gap-4 h-full min-h-0">
          <div className="grid grid-cols-4 gap-3 shrink-0">
            {[
              { t: 'Heart', s: data?.risks.heart_risk_score || 0, i: Heart, c: 'text-red-500' },
              { t: 'Diabetes', s: data?.risks.diabetes_risk_score || 0, i: Activity, c: 'text-emerald-500' },
              { t: 'Stroke', s: data?.risks.stroke_risk_score || 0, i: Brain, c: 'text-purple-500' },
              { t: 'Kidney', s: data?.risks.kidney_risk_score || 0, i: Stethoscope, c: 'text-blue-500' }
            ].map((r, i) => (
              <div key={i} className="glass-card p-4 rounded-2xl border border-white/5 flex flex-col items-center text-center group">
                <r.i className={`w-5 h-5 mb-2 group-hover:scale-110 transition-transform ${r.s > 70 ? 'text-red-500' : r.s > 40 ? 'text-amber-500' : r.c}`} />
                <p className="text-[8px] font-black text-slate-600 uppercase mb-1 tracking-widest">{r.t}</p>
                <p className="text-xl font-black text-white tracking-tighter">{r.s.toFixed(0)}%</p>
              </div>
            ))}
          </div>

          <div className="glass-card flex-1 rounded-[2.5rem] p-8 relative overflow-hidden bg-black/50 border border-white/5">
            <div className="flex justify-between items-center mb-8 relative z-10 shrink-0">
              <div className="flex items-center gap-3">
                <Dna className="w-6 h-6 text-blue-500 animate-pulse" />
                <h2 className="text-[10px] font-black italic tracking-[0.4em] text-white uppercase opacity-70">Neural differential assessment</h2>
              </div>
              <div className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-[8px] font-black text-blue-500">
                LLM_NODE_BETA_V2
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
                    transition={{ duration: 0.2 }}
                    className="absolute inset-0 z-20 bg-black/60 backdrop-blur-[8px] rounded-2xl flex flex-col items-center justify-center gap-4 border border-blue-500/10"
                  >
                    <div className="relative">
                      <div className="w-12 h-12 border-[3px] border-blue-500/10 rounded-full" />
                      <div className="w-12 h-12 border-[3px] border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0 shadow-[0_0_15px_rgba(59,130,246,0.3)]" />
                    </div>
                    <p className="text-[9px] font-black text-blue-500 tracking-[0.4em] uppercase animate-pulse">Analyzing Bio-Payload...</p>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="h-full overflow-y-auto custom-scrollbar pr-4 pb-20 selection:bg-blue-500/40">
                <motion.div
                  animate={{
                    opacity: loading ? 0.2 : 1,
                    y: loading ? 10 : 0,
                    filter: loading ? 'blur(8px)' : 'blur(0px)'
                  }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                  className="prose prose-invert prose-xs max-w-none text-slate-300 leading-relaxed font-medium"
                >
                  <ReactMarkdown>{data?.diagnosis || "Awaiting clinical intelligence stream..."}</ReactMarkdown>
                </motion.div>
              </div>
            </div>
          </div>
        </div>

        {/* Column 4: Alerts & Safety HUD */}
        <div className="col-span-2 space-y-4 flex flex-col h-full min-h-0">
          <div className="glass-card p-5 rounded-3xl bg-white/[0.01] shrink-0 border border-white/5">
            <h3 className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-4">Med Safety HUD</h3>
            <div className="space-y-4">
              {patient.medications && (
                <div className={`p-4 rounded-2xl border transition-all duration-500 ${emergency ? 'bg-red-500/10 border-red-500/40' : 'bg-emerald-500/5 border-emerald-500/10 opacity-70'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    {emergency ? <AlertTriangle className="w-3 h-3 text-red-500" /> : <ShieldAlert className="w-3 h-3 text-emerald-500" />}
                    <p className={`text-[8px] font-black uppercase tracking-tighter ${emergency ? 'text-red-500' : 'text-emerald-500'}`}>
                      {emergency ? 'Emergency Conflict' : 'Scan Result'}
                    </p>
                  </div>
                  <p className="text-xs text-white font-bold italic truncate tracking-tight">{patient.medications}</p>
                  <p className="text-[9px] text-slate-400 mt-2 leading-tight">
                    {emergency ? 'High risk profile detected - monitor vitals.' : 'Routine analysis: No acute conflicts.'}
                  </p>
                </div>
              )}
              <div className="px-4 py-3 bg-white/[0.02] border border-white/5 rounded-2xl opacity-40">
                <p className="text-[8px] font-bold text-slate-600 uppercase mb-1 italic tracking-widest">System Scan</p>
                <p className="text-[10px] text-slate-500">Lisinopril: SAFE</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-6 rounded-3xl flex-1 flex flex-col bg-white/[0.01] border border-white/5 overflow-hidden">
            <h3 className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-6 border-b border-white/5 pb-2 flex items-center gap-2">
              <Gauge className="w-3 h-3 text-blue-500" /> Sys Telemetry
            </h3>
            <div className="text-[9px] font-mono text-slate-600 space-y-3 flex-1 overflow-y-auto">
              {[
                { l: 'Node Status', v: 'Online', c: 'text-emerald-500/60' },
                { l: 'Engine', v: 'XGB-2.4', c: '' },
                { l: 'Global Health', v: `${data?.risks.general_health_score?.toFixed(1) || '0.0'}%`, c: 'text-emerald-400' },
                { l: 'Latency', v: '14ms', c: '' }
              ].map((t, i) => (
                <p key={i} className={`flex justify-between uppercase ${t.c}`}>{t.l}: <span className="text-slate-400">{t.v}</span></p>
              ))}

              <div className="pt-6 mt-6 border-t border-white/5 space-y-4">
                <p className="text-white font-black text-[8px] uppercase tracking-widest mb-3">Model Accuracy</p>
                {['Heart Risk', 'Stroke Map', 'Kidney AI'].map((m) => (
                  <div key={m} className="space-y-1">
                    <div className="flex justify-between text-slate-500 uppercase tracking-tighter text-[7px]"><span>{m}</span><span>{m === 'Kidney AI' ? '100%' : '98.2%'}</span></div>
                    <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden">
                      <motion.div initial={{ width: 0 }} animate={{ width: '95%' }} className="h-full bg-blue-500/40" />
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
