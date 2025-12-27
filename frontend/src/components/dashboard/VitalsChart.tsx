'use client';

import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';

interface VitalsChartProps {
    label: string;
    data: { time: string; value: number }[];
    color: string;
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ value: number; payload: { time: string } }> }) {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#0f1115] border border-white/10 p-2 rounded-lg shadow-xl">
                <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">{payload[0].payload.time}</p>
                <p className="text-sm font-bold text-white">{payload[0].value}</p>
            </div>
        );
    }
    return null;
}

export default function VitalsChart({ label, data, color }: VitalsChartProps) {
    return (
        <div className="h-[100px] w-full">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id={`gradient-${label}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
                    <XAxis hide dataKey="time" />
                    <YAxis hide domain={['dataMin - 5', 'dataMax + 5']} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        strokeWidth={2}
                        fillOpacity={1}
                        fill={`url(#gradient-${label})`}
                        animationDuration={1500}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
