'use client';

import { RiskScores } from '@/lib/types';
import { roundPercent } from '@/lib/formatters';

interface RiskGaugesProps {
    scores?: RiskScores;
}

export default function RiskGauges({ scores }: RiskGaugesProps) {
    const risks = [
        {
            label: 'Kardiyak',
            value: roundPercent(scores?.heart ?? 0),
            icon: 'cardiology',
            gradient: 'from-red-500 to-orange-500',
            glow: 'shadow-red-500/50',
            bg: 'bg-red-500/10',
            border: 'border-red-500/30'
        },
        {
            label: 'Metabolik',
            value: roundPercent(scores?.diabetes ?? 0),
            icon: 'water_drop',
            gradient: 'from-blue-500 to-cyan-400',
            glow: 'shadow-blue-500/50',
            bg: 'bg-blue-500/10',
            border: 'border-blue-500/30'
        },
        {
            label: 'Nörolojik',
            value: roundPercent(scores?.stroke ?? 0),
            icon: 'psychology',
            gradient: 'from-purple-500 to-pink-500',
            glow: 'shadow-purple-500/50',
            bg: 'bg-purple-500/10',
            border: 'border-purple-500/30'
        },
        {
            label: 'Böbrek',
            value: roundPercent(scores?.kidney ?? 0),
            icon: 'nephrology',
            gradient: 'from-emerald-500 to-teal-400',
            glow: 'shadow-emerald-500/50',
            bg: 'bg-emerald-500/10',
            border: 'border-emerald-500/30'
        },
    ];

    const getRiskLevel = (value: number) => {
        if (value >= 70) return { text: 'KRİTİK', color: 'text-red-400' };
        if (value >= 50) return { text: 'YÜKSEK', color: 'text-orange-400' };
        if (value >= 30) return { text: 'ORTA', color: 'text-yellow-400' };
        return { text: 'DÜŞÜK', color: 'text-emerald-400' };
    };

    return (
        <div className="glass-card rounded-3xl p-6 space-y-5">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10">
                        <span className="material-symbols-outlined text-blue-400 text-[18px]">monitoring</span>
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white">Risk Analizi</h3>
                        <p className="text-[10px] text-slate-500 uppercase tracking-widest">Gerçek Zamanlı Değerlendirme</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span className="text-[10px] text-emerald-400 font-bold">CANLI</span>
                </div>
            </div>

            {/* Risk Cards */}
            <div className="space-y-3">
                {risks.map((risk, i) => {
                    const level = getRiskLevel(risk.value);
                    const isLoading = !scores;

                    return (
                        <div
                            key={i}
                            className={`group relative overflow-hidden rounded-2xl ${risk.bg} border ${risk.border} p-4 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg ${risk.glow}`}
                        >
                            {/* Animated Background Gradient */}
                            <div
                                className={`absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-500 bg-gradient-to-r ${risk.gradient}`}
                            />

                            <div className="relative flex items-center gap-4">
                                {/* Icon */}
                                <div className={`flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br ${risk.gradient} flex items-center justify-center shadow-lg ${risk.glow}`}>
                                    <span className="material-symbols-outlined text-white text-[20px]">{risk.icon}</span>
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs font-bold text-white">{risk.label}</span>
                                        <div className="flex items-center gap-2">
                                            {isLoading ? (
                                                <div className="h-4 w-12 bg-white/10 rounded animate-pulse" />
                                            ) : (
                                                <>
                                                    <span className={`text-[10px] font-bold ${level.color}`}>{level.text}</span>
                                                    <span className="text-lg font-black text-white">{risk.value}%</span>
                                                </>
                                            )}
                                        </div>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="h-2 bg-black/30 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full bg-gradient-to-r ${risk.gradient} rounded-full transition-all duration-1000 ease-out relative`}
                                            style={{ width: isLoading ? '0%' : `${risk.value}%` }}
                                        >
                                            {/* Shine Effect */}
                                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Threshold Markers */}
                            <div className="absolute bottom-1 right-4 flex gap-1">
                                {[30, 50, 70].map((threshold) => (
                                    <div
                                        key={threshold}
                                        className={`w-1 h-1 rounded-full ${risk.value >= threshold ? 'bg-white/50' : 'bg-white/10'}`}
                                    />
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Overall Summary */}
            <div className="pt-4 border-t border-white/10">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-slate-500 text-[16px]">avg_pace</span>
                        <span className="text-[10px] text-slate-500 uppercase tracking-widest">Toplam Skor</span>
                    </div>
                    {scores ? (
                        <div className="flex items-center gap-3">
                            <div className="flex gap-1">
                                {[1, 2, 3, 4, 5].map((bar) => (
                                    <div
                                        key={bar}
                                        className={`w-1.5 rounded-full transition-all duration-500 ${((scores.heart + scores.diabetes + scores.stroke + scores.kidney) / 4) >= bar * 20
                                            ? 'h-4 bg-gradient-to-t from-blue-500 to-purple-500'
                                            : 'h-2 bg-white/10'
                                            }`}
                                    />
                                ))}
                            </div>
                            <span className="text-sm font-black text-white">
                                {roundPercent((scores.heart + scores.diabetes + scores.stroke + scores.kidney) / 4)}%
                            </span>
                        </div>
                    ) : (
                        <div className="h-4 w-16 bg-white/10 rounded animate-pulse" />
                    )}
                </div>
            </div>
        </div>
    );
}
