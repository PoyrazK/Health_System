'use client';

interface TelemetryGraphProps {
    isCritical?: boolean;
}

export default function TelemetryGraph({ isCritical }: TelemetryGraphProps) {
    return (
        <div className={`glass-card rounded-3xl p-0 h-[180px] relative overflow-hidden flex flex-col transition-colors ${isCritical ? 'bg-red-500/5' : ''}`}>
            <div className="px-5 py-3 border-b border-white/5 flex items-center justify-between bg-black/20">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <span className={`material-symbols-outlined text-[18px] ${isCritical ? 'text-red-400' : 'text-blue-400'} animate-pulse`}>ecg_heart</span>
                        <span className="text-xs font-bold text-slate-300 uppercase tracking-widest">Live Telemetry</span>
                    </div>
                    <div className="flex gap-4">
                        <div className="flex items-baseline gap-1">
                            <span className="text-[10px] text-slate-500 font-mono">HR</span>
                            <span className={`text-sm font-bold font-mono ${isCritical ? 'text-red-400' : 'text-white'}`}>86</span>
                        </div>
                        <div className="flex items-baseline gap-1">
                            <span className="text-[10px] text-slate-500 font-mono">O2</span>
                            <span className="text-sm font-bold font-mono text-blue-400">98%</span>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-600 font-mono">SPS: 240</span>
                    <button className="text-slate-500 hover:text-white"><span className="material-symbols-outlined text-[18px]">fullscreen</span></button>
                </div>
            </div>

            <div className="relative flex-1 bg-black/40 overflow-hidden">
                {/* Grid lines */}
                <div className="absolute inset-0 z-0 opacity-10" style={{
                    backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)',
                    backgroundSize: '40px 40px'
                }}></div>

                {/* ECG Line Simulation */}
                <svg className="absolute inset-0 w-full h-full z-10" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="ecgGradient" x1="0%" x2="100%" y1="0%" y2="0%">
                            <stop offset="0%" stopColor={isCritical ? "#EF4444" : "#3B82F6"} stopOpacity="0" />
                            <stop offset="20%" stopColor={isCritical ? "#EF4444" : "#3B82F6"} stopOpacity="1" />
                            <stop offset="80%" stopColor={isCritical ? "#EF4444" : "#3B82F6"} stopOpacity="1" />
                            <stop offset="100%" stopColor={isCritical ? "#EF4444" : "#3B82F6"} stopOpacity="0" />
                        </linearGradient>
                        <filter id="ecgGlow">
                            <feGaussianBlur stdDeviation="2" result="blur" />
                            <feMerge>
                                <feMergeNode in="blur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>
                    <path
                        className="animate-pulse"
                        d="M0,80 L50,80 L60,40 L70,120 L80,20 L90,140 L100,80 L150,80 L160,40 L170,120 L180,20 L190,140 L200,80 L250,80 L260,40 L270,120 L280,20 L290,140 L300,80 L350,80 L360,40 L370,120 L380,20 L390,140 L400,80 L450,80 L460,40 L470,120 L480,20 L490,140 L500,80 L550,80 L560,40 L570,120 L580,20 L590,140 L600,80 L650,80 L660,40 L670,120 L680,20 L690,140 L700,80 L750,80 L760,40 L770,120 L780,20 L790,140 L800,80 L850,80 L860,40 L870,120 L880,20 L890,140 L900,80 L950,80 L960,40 L970,120 L980,20 L990,140 L1000,80"
                        fill="none"
                        stroke="url(#ecgGradient)"
                        strokeWidth="2.5"
                        filter="url(#ecgGlow)"
                        style={{
                            strokeDasharray: '1000',
                            strokeDashoffset: '0',
                            animation: 'telemetryMove 10s linear infinite'
                        }}
                    />
                </svg>

                {/* Scan line */}
                <div className="absolute top-0 bottom-0 w-[2px] bg-white/30 z-20 shadow-[0_0_10px_white]" style={{ left: '50%', animation: 'telemetryScan 4s linear infinite' }}></div>
            </div>
        </div>
    );
}
