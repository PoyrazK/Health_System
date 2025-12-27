import React from 'react';
import {
    Heart,
    Activity,
    Brain,
    Stethoscope
} from 'lucide-react';

interface RiskAnalysisProps {
    risks: {
        heart_risk_score: number;
        diabetes_risk_score: number;
        stroke_risk_score: number;
        kidney_risk_score: number;
    } | undefined;
    explanations?: Record<string, Record<string, number>>;
}

export const RiskAnalysis: React.FC<RiskAnalysisProps> = ({ risks, explanations }) => {
    const riskItems = [
        {
            id: 'heart',
            label: 'Heart',
            score: risks?.heart_risk_score || 0,
            icon: Heart,
            colorClass: 'text-red-500',
            bgClass: 'bg-red-500/5 group-hover:bg-red-500/10'
        },
        {
            id: 'diabetes',
            label: 'Diabetes',
            score: risks?.diabetes_risk_score || 0,
            icon: Activity,
            colorClass: 'text-emerald-500',
            bgClass: 'bg-emerald-500/5 group-hover:bg-emerald-500/10'
        },
        {
            id: 'stroke',
            label: 'Stroke',
            score: risks?.stroke_risk_score || 0,
            icon: Brain,
            colorClass: 'text-purple-500',
            bgClass: 'bg-purple-500/5 group-hover:bg-purple-500/10'
        },
        {
            id: 'kidney',
            label: 'Kidney',
            score: risks?.kidney_risk_score || 0,
            icon: Stethoscope,
            colorClass: 'text-blue-500',
            bgClass: 'bg-blue-500/5 group-hover:bg-blue-500/10'
        }
    ];

    return (
        <div className="grid grid-cols-4 gap-4">
            {riskItems.map((item, idx) => {
                const factors = explanations?.[item.id] || {};
                const topFactors = Object.entries(factors)
                    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
                    .slice(0, 3);

                return (
                    <div
                        key={idx}
                        className={`
            glass-card p-5 rounded-3xl border border-white/5 flex flex-col items-center text-center 
            group transition-all duration-500 hover:border-white/20 hover:-translate-y-1 overflow-hidden
            ${item.bgClass}
          `}
                    >
                        <div className="relative mb-3">
                            <div className={`absolute inset-0 blur-lg opacity-40 ${item.colorClass} bg-current`} />
                            <item.icon
                                className={`w-6 h-6 z-10 relative transition-transform duration-300 group-hover:scale-110
                    ${item.score > 70 ? 'text-red-500 animate-pulse' : item.score > 40 ? 'text-amber-500' : item.colorClass}
                  `}
                            />
                        </div>

                        <p className="text-[9px] font-black text-slate-500 uppercase mb-1 tracking-widest">
                            {item.label}
                        </p>

                        <div className="relative mb-3">
                            <span className="text-2xl font-black text-white tracking-tighter">
                                {item.score.toFixed(0)}
                            </span>
                            <span className="text-[10px] font-bold text-slate-500 align-top ml-0.5">%</span>
                        </div>

                        {/* SHAP Explanations */}
                        <div className="w-full space-y-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <div className="h-px bg-white/5 w-full mb-2" />
                            {topFactors.map(([name, value]) => (
                                <div key={name} className="flex flex-col gap-0.5">
                                    <div className="flex justify-between text-[7px] font-black uppercase tracking-tighter">
                                        <span className="text-slate-500">{name.replace('_', ' ')}</span>
                                        <span className={value > 0 ? 'text-red-400' : 'text-emerald-400'}>
                                            {value > 0 ? '+' : ''}{value.toFixed(1)}
                                        </span>
                                    </div>
                                    <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full ${value > 0 ? 'bg-red-500/40' : 'bg-emerald-500/40'}`}
                                            style={{ width: `${Math.min(Math.abs(value) * 2, 100)}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                            {topFactors.length === 0 && (
                                <p className="text-[7px] text-slate-600 italic">No attribution data</p>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
