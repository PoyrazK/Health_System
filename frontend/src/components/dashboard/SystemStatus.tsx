'use client';

import { ModelPrecision } from '@/lib/types';
import { roundPercent } from '@/lib/formatters';

interface SystemStatusProps {
    models?: ModelPrecision[];
}

export default function SystemStatus({ models }: SystemStatusProps) {
    const isLoading = !models;

    return (
        <div className="glass-card rounded-2xl p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <div className="w-2 h-2 rounded-full bg-emerald-500" />
                        <div className="absolute inset-0 w-2 h-2 rounded-full bg-emerald-500 animate-ping opacity-75" />
                    </div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">YZ Hattı</span>
                </div>
                <span className="text-[9px] text-emerald-400 font-mono">SAĞLIKLI</span>
            </div>

            {/* Model Cards */}
            <div className="space-y-2">
                {isLoading ? (
                    Array.from({ length: 3 }).map((_, i) => (
                        <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse" />
                    ))
                ) : (
                    models.map((model, i) => {
                        const pct = roundPercent(model.confidence * 100);
                        const isHigh = pct >= 95;

                        return (
                            <div
                                key={i}
                                className="group relative overflow-hidden rounded-lg bg-white/[0.02] hover:bg-white/5 transition-colors p-3"
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <span className="material-symbols-outlined text-[14px] text-slate-600">
                                            {model.name.includes('XGBoost') ? 'favorite' :
                                                model.name.includes('LSTM') ? 'water_drop' : 'image'}
                                        </span>
                                        <span className="text-xs text-slate-400">{model.name}</span>
                                    </div>
                                    <span className={`text-xs font-bold tabular-nums ${isHigh ? 'text-emerald-400' : 'text-blue-400'}`}>
                                        {pct}%
                                    </span>
                                </div>

                                {/* Progress */}
                                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-700 ${isHigh ? 'bg-emerald-500' : 'bg-blue-500'
                                            }`}
                                        style={{ width: `${pct}%` }}
                                    />
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Footer */}
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
                <span className="text-[9px] text-slate-600">Gecikme</span>
                <span className="text-[10px] text-slate-400 font-mono">~118ms</span>
            </div>
        </div>
    );
}
