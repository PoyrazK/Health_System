'use client';

import { MedicationAnalysis } from '@/lib/types';

interface MedicationSafetyProps {
    analysis?: MedicationAnalysis;
}

export default function MedicationSafety({ analysis }: MedicationSafetyProps) {
    const allMeds = analysis ? [...analysis.safe.map(m => ({ name: m, safe: true })), ...analysis.risky.map(m => ({ name: m, safe: false }))] : [];
    const isLoading = !analysis;

    return (
        <div className="glass-card rounded-2xl p-5">
            {/* Minimal Header */}
            <div className="flex items-center gap-2 mb-4">
                <div className="w-1 h-4 rounded-full bg-gradient-to-b from-emerald-500 to-red-500" />
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">İlaçlar</span>
                <div className="flex-1" />
                <span className="text-[10px] text-slate-600 font-mono">
                    {analysis ? `${allMeds.length} aktif` : '...'}
                </span>
            </div>

            {/* Medication List */}
            <div className="space-y-1.5">
                {isLoading ? (
                    Array.from({ length: 3 }).map((_, i) => (
                        <div key={i} className="h-8 bg-white/5 rounded-lg animate-pulse" />
                    ))
                ) : (
                    allMeds.map((med, i) => (
                        <div
                            key={i}
                            className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${med.safe
                                ? 'hover:bg-emerald-500/5'
                                : 'bg-red-500/5 hover:bg-red-500/10'
                                }`}
                        >
                            {/* Status Dot */}
                            <div className={`w-1.5 h-1.5 rounded-full ${med.safe ? 'bg-emerald-500' : 'bg-red-500 animate-pulse'}`} />

                            {/* Med Name */}
                            <span className="flex-1 text-sm text-white">{med.name}</span>

                            {/* Status Badge */}
                            {!med.safe && (
                                <span className="text-[9px] font-bold text-red-400 uppercase tracking-wider">
                                    Risk
                                </span>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* Footer Summary */}
            {analysis && analysis.risky.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/5 flex items-center gap-2">
                    <span className="material-symbols-outlined text-red-400 text-[14px]">info</span>
                    <span className="text-[10px] text-slate-500">
                        {analysis.risky.length} etkileşim tespit edildi
                    </span>
                </div>
            )}
        </div>
    );
}
