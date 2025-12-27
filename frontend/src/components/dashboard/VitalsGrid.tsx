'use client';

import { Patient } from '@/lib/types';

interface VitalsGridProps {
    patient: Patient;
}

export default function VitalsGrid({ patient }: VitalsGridProps) {
    const vitals = [
        { label: 'Sistolik Tansiyon', value: patient.systolic_bp, unit: 'mmHg', color: 'text-blue-400' },
        { label: 'Diastolik Tansiyon', value: patient.diastolic_bp, unit: 'mmHg', color: 'text-blue-400' },
        { label: 'Nabız', value: patient.heart_rate, unit: 'BPM', color: 'text-red-400' },
        { label: 'Glikoz', value: patient.glucose, unit: 'mg/dL', color: 'text-yellow-400' },
        { label: 'VKİ', value: patient.bmi, unit: 'kg/m²', color: 'text-emerald-400' },
        { label: 'Adım', value: patient.steps, unit: 'Günlük', color: 'text-slate-400' },
    ];

    return (
        <div className="grid grid-cols-2 gap-3">
            {vitals.map((v, i) => (
                <div key={i} className="glass-card rounded-2xl p-4 flex flex-col justify-between hover:bg-white/5 transition-colors group">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{v.label}</span>
                    <div className="flex items-baseline gap-1 mt-2">
                        <span className={`text-xl font-bold ${v.color}`}>{v.value}</span>
                        <span className="text-[10px] text-slate-600 font-bold">{v.unit}</span>
                    </div>
                </div>
            ))}
        </div>
    );
}
