import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils'; // We'll need to create a utils file for cn or just use template literals if clsx/tailwind-merge is not desired, but package.json has them.

interface MetricCardProps {
    label: string;
    value: string | number;
    unit: string;
    icon: LucideIcon;
    isCritical?: boolean;
    trend?: 'up' | 'down' | 'neutral';
    className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
    label,
    value,
    unit,
    icon: Icon,
    isCritical = false,
    className
}) => {
    return (
        <div
            className={`
        relative overflow-hidden rounded-2xl border p-4 transition-all duration-300
        ${isCritical
                    ? 'bg-red-500/10 border-red-500/30'
                    : 'bg-white/[0.03] border-white/5 hover:border-white/10 hover:bg-white/[0.05]'
                }
        ${className}
      `}
        >
            <div className="flex justify-between items-start mb-2">
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                    {label}
                </span>
                <Icon
                    className={`w-4 h-4 ${isCritical ? 'text-red-500 animate-pulse' : 'text-slate-600'}`}
                />
            </div>

            <div className="flex items-baseline gap-1.5">
                <span
                    className={`text-2xl font-black tracking-tight ${isCritical ? 'text-red-500' : 'text-white'
                        }`}
                >
                    {value}
                </span>
                <span className="text-[9px] font-bold text-slate-500 uppercase">
                    {unit}
                </span>
            </div>

            {/* Background decoration */}
            <div className="absolute -bottom-4 -right-4 w-12 h-12 rounded-full bg-gradient-to-br from-white/5 to-transparent blur-xl" />
        </div>
    );
};
