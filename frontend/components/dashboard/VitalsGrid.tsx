'use client';

// Flexible interface that works with both old and new Patient types
interface VitalsPatient {
    systolic_bp: number;
    diastolic_bp: number;
    heart_rate: number;
    glucose: number;
    bmi: number;
    steps: number;
}

interface VitalsGridProps {
    patient: VitalsPatient;
}

export default function VitalsGrid({ patient }: VitalsGridProps) {
    const vitals = [
        { label: 'BP Systolic', value: patient.systolic_bp, unit: 'mmHg', color: 'text-blue-400' },
        { label: 'BP Diastolic', value: patient.diastolic_bp, unit: 'mmHg', color: 'text-blue-400' },
        { label: 'Heart Rate', value: patient.heart_rate, unit: 'BPM', color: 'text-red-400' },
        { label: 'Glucose', value: patient.glucose, unit: 'mg/dL', color: 'text-yellow-400' },
        { label: 'BMI Index', value: patient.bmi, unit: 'kg/m²', color: 'text-emerald-400' },
        { label: 'Steps', value: patient.steps, unit: 'Daily', color: 'text-slate-400' },
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

