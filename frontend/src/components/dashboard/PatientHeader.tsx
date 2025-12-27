'use client';

import { Patient } from '@/lib/types';

interface PatientHeaderProps {
    patient: Patient;
    onExit: () => void;
}

export default function PatientHeader({ patient, onExit }: PatientHeaderProps) {
    return (
        <header className="h-16 border-b border-white/5 px-6 flex items-center justify-between bg-[#0f1115]/80 backdrop-blur sticky top-0 z-10">
            <div className="flex items-center gap-4">
                <button onClick={onExit} className="p-2 -ml-2 rounded-lg hover:bg-white/5 text-slate-400 transition-all">
                    <span className="material-symbols-outlined">arrow_back</span>
                </button>
                <div className="h-8 w-[1px] bg-white/10 mx-2"></div>
                <div className="flex flex-col">
                    <div className="flex items-center gap-3">
                        <h2 className="text-lg font-bold text-white leading-none">{patient.name}</h2>
                        <span className="text-xs text-slate-500 font-mono">ID: {patient.id}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] text-slate-400 uppercase tracking-widest">{patient.gender}, {patient.age}y</span>
                        <span className="text-slate-700">•</span>
                        <span className="text-[10px] text-slate-400 uppercase tracking-widest">Admitted: {new Date(patient.admitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-6">
                <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest leading-none">Status</span>
                    <span className={`text-sm font-bold ${patient.status === 'Critical' ? 'text-red-400' : 'text-green-400'} flex items-center gap-1.5`}>
                        <span className={`w-2 h-2 rounded-full ${patient.status === 'Critical' ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></span>
                        {patient.status}
                    </span>
                </div>
                <div className="h-8 w-[1px] bg-white/10"></div>
                <button className="h-10 px-4 bg-blue-500 hover:bg-blue-600 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2">
                    <span className="material-symbols-outlined text-[20px]">add_circle</span>
                    New Order
                </button>
            </div>
        </header>
    );
}
