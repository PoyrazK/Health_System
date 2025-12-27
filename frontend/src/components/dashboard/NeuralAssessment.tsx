'use client';

import { useState, useEffect } from 'react';

interface NeuralAssessmentProps {
    diagnosis?: string;
    isCritical?: boolean;
}

export default function NeuralAssessment({ diagnosis, isCritical }: NeuralAssessmentProps) {
    const [displayText, setDisplayText] = useState('');

    useEffect(() => {
        if (!diagnosis) {
            setDisplayText('');
            return;
        }

        let i = 0;
        const interval = setInterval(() => {
            setDisplayText(diagnosis.substring(0, i));
            i += 5;
            if (i > diagnosis.length) clearInterval(interval);
        }, 10);

        return () => clearInterval(interval);
    }, [diagnosis]);

    return (
        <div className={`glass-card rounded-3xl p-0 overflow-hidden flex flex-col h-full border-2 transition-colors ${isCritical ? 'border-red-500/20' : 'border-blue-500/20'}`}>
            <div className={`p-5 flex items-center justify-between border-b border-white/5 ${isCritical ? 'bg-red-500/5' : 'bg-blue-500/5'}`}>
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${isCritical ? 'bg-red-500/10 text-red-400' : 'bg-blue-500/10 text-blue-400'}`}>
                        <span className="material-symbols-outlined">psychology</span>
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white leading-none">Neural Differential Assessment</h3>
                        <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-1">Model: Med-Gemini-V3-Pro</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <span className="px-2 py-1 rounded bg-white/5 border border-white/10 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Confidence: 99.8%</span>
                </div>
            </div>

            <div className="flex-1 p-6 overflow-y-auto font-sans text-sm leading-relaxed text-slate-300">
                {!diagnosis ? (
                    <div className="space-y-4">
                        <div className="h-4 bg-white/5 rounded-full animate-pulse w-3/4"></div>
                        <div className="h-4 bg-white/5 rounded-full animate-pulse w-full"></div>
                        <div className="h-4 bg-white/5 rounded-full animate-pulse w-5/6"></div>
                    </div>
                ) : (
                    <div className="whitespace-pre-wrap">
                        {displayText}
                        <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1 align-middle"></span>
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-white/5 bg-black/20 flex gap-3">
                <button className="flex-1 h-10 rounded-xl border border-white/10 text-xs font-bold hover:bg-white/5 transition-all">Review Source Data</button>
                <button className={`flex-1 h-10 rounded-xl text-xs font-bold transition-all shadow-lg ${isCritical ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'}`}>
                    Confirm Protocol
                </button>
            </div>
        </div>
    );
}
