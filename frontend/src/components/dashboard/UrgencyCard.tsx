'use client';

import { UrgencyInfo } from '@/lib/types';
import { roundPercent } from '@/lib/formatters';

interface UrgencyCardProps {
    urgency?: UrgencyInfo;
}

const URGENCY_CONFIG = {
    1: { name: 'Resüsitasyon', color: 'from-red-600 to-red-800', bgColor: 'bg-red-500/20', textColor: 'text-red-400', borderColor: 'border-red-500/50' },
    2: { name: 'Acil', color: 'from-orange-500 to-red-600', bgColor: 'bg-orange-500/20', textColor: 'text-orange-400', borderColor: 'border-orange-500/50' },
    3: { name: 'İvedili', color: 'from-amber-500 to-orange-500', bgColor: 'bg-amber-500/20', textColor: 'text-amber-400', borderColor: 'border-amber-500/50' },
    4: { name: 'Az Acil', color: 'from-emerald-500 to-teal-500', bgColor: 'bg-emerald-500/20', textColor: 'text-emerald-400', borderColor: 'border-emerald-500/50' },
    5: { name: 'Acil Değil', color: 'from-blue-500 to-cyan-500', bgColor: 'bg-blue-500/20', textColor: 'text-blue-400', borderColor: 'border-blue-500/50' },
};

export default function UrgencyCard({ urgency }: UrgencyCardProps) {
    if (!urgency) {
        return (
            <div className="glass-card rounded-2xl p-5 space-y-3">
                <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-slate-500 text-[18px]">priority_high</span>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Triaj Seviyesi</span>
                </div>
                <div className="flex items-center justify-center py-4">
                    <p className="text-sm text-slate-500">Değerlendirme bekleniyor...</p>
                </div>
            </div>
        );
    }

    const level = Math.min(Math.max(urgency.urgency_level, 1), 5) as keyof typeof URGENCY_CONFIG;
    const config = URGENCY_CONFIG[level];

    return (
        <div className={`glass-card rounded-2xl p-5 space-y-4 border ${config.borderColor}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-amber-400 text-[18px]">trending_down</span>
                    <div>
                        <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block">Kısa Vadeli Tahmin</span>
                        <span className="text-xs text-white font-semibold">Kötüleşme Riski (24s)</span>
                    </div>
                </div>
                <div className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${config.bgColor} ${config.textColor}`}>
                    ESI {level}
                </div>
            </div>

            {/* Urgency Level Display */}
            <div className="flex items-center gap-4">
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${config.color} flex items-center justify-center shadow-lg`}>
                    <span className="text-3xl font-black text-white">{level}</span>
                </div>
                <div className="flex-1">
                    <h3 className={`text-lg font-bold ${config.textColor}`}>
                        {urgency.urgency_name || config.name}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                        <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                            <div
                                className={`h-full bg-gradient-to-r ${config.color} transition-all duration-500`}
                                style={{ width: `${roundPercent(urgency.probability)}%` }}
                            />
                        </div>
                        <span className="text-xs text-slate-400">{roundPercent(urgency.probability)}%</span>
                    </div>
                </div>
            </div>

            {/* Golden Hour - Critical Intervention Time */}
            {urgency.golden_hour_minutes && urgency.golden_hour_minutes > 0 && (
                <div className={`flex items-center gap-3 p-3 rounded-xl ${config.bgColor} border ${config.borderColor}`}>
                    <div className="flex-shrink-0">
                        <span className="material-symbols-outlined text-amber-400 text-[24px] animate-pulse">timer</span>
                    </div>
                    <div className="flex-1">
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest">Kritik Müdahale Süresi</p>
                        <p className={`text-lg font-black ${config.textColor}`}>
                            {urgency.golden_hour_minutes < 60
                                ? `${urgency.golden_hour_minutes} dakika`
                                : `${Math.round(urgency.golden_hour_minutes / 60)} saat`}
                        </p>
                    </div>
                    {urgency.golden_hour_minutes <= 60 && (
                        <div className="flex-shrink-0">
                            <span className="material-symbols-outlined text-red-400 text-[20px] animate-bounce">warning</span>
                        </div>
                    )}
                </div>
            )}

            {/* Confidence */}
            <div className="flex items-center justify-between pt-2 border-t border-white/5">
                <span className="text-xs text-slate-500">Güven</span>
                <span className={`text-xs font-bold ${config.textColor}`}>{urgency.confidence}</span>
            </div>
        </div>
    );
}
