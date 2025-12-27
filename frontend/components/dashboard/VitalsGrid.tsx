import React from 'react';
import {
    Activity,
    Heart,
    Wind,
    Thermometer,
    Droplets,
    Zap
} from 'lucide-react';
import { MetricCard } from '@/components/ui/MetricCard';
import { Patient } from "../../types";

interface VitalsGridProps {
    patient: Patient | null;
}

export const VitalsGrid: React.FC<VitalsGridProps> = ({ patient }) => {
    if (!patient) return null;

    const metrics = [
        {
            label: 'Systolic BP',
            value: patient.systolic_bp,
            unit: 'mmHg',
            icon: Zap,
            isCritical: patient.systolic_bp > 160
        },
        {
            label: 'Diastolic BP',
            value: patient.diastolic_bp,
            unit: 'mmHg',
            icon: Activity,
            isCritical: false
        },
        {
            label: 'Heart Rate',
            value: patient.heart_rate,
            unit: 'BPM',
            icon: Heart,
            isCritical: patient.heart_rate > 100
        },
        {
            label: 'Glucose',
            value: patient.glucose,
            unit: 'mg/dL',
            icon: Droplets,
            isCritical: patient.glucose > 180
        },
        {
            label: 'Cholesterol',
            value: patient.cholesterol,
            unit: 'mg/dL',
            icon: Wind,
            isCritical: patient.cholesterol > 240
        },
        {
            label: 'BMI Index',
            value: patient.bmi,
            unit: 'kg/m²',
            icon: Thermometer,
            isCritical: false
        }
    ];

    return (
        <div className="grid grid-cols-2 gap-3">
            {metrics.map((m, idx) => (
                <MetricCard
                    key={idx}
                    label={m.label}
                    value={m.value}
                    unit={m.unit}
                    icon={m.icon}
                    isCritical={m.isCritical}
                />
            ))}
        </div>
    );
};
