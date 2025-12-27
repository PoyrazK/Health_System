'use client';

import { useState, useEffect, useRef } from 'react';

interface EKGReading {
    condition: string;
    probability: number;
    confidence: string;
}

interface EKGMonitorProps {
    patientId?: string;
}

const CONDITION_CONFIG: Record<string, { color: string; icon: string; label: string; severity: 'normal' | 'warning' | 'critical' }> = {
    'Normal': { color: 'text-emerald-400', icon: 'check_circle', label: 'Normal Sinüs Ritmi', severity: 'normal' },
    'SVEB': { color: 'text-amber-400', icon: 'warning', label: 'Supraventriküler Ektopi', severity: 'warning' },
    'VEB': { color: 'text-red-400', icon: 'emergency', label: 'Ventriküler Ektopi', severity: 'critical' },
};

export default function EKGMonitor({ patientId }: EKGMonitorProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [readings, setReadings] = useState<EKGReading[]>([
        { condition: 'Normal', probability: 0.92, confidence: 'High' }
    ]);
    const [heartRate, setHeartRate] = useState(72);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // Animated EKG waveform
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationId: number;
        let offset = 0;

        const drawEKG = () => {
            const width = canvas.width;
            const height = canvas.height;
            const midY = height / 2;

            // Clear canvas
            ctx.fillStyle = 'rgba(15, 17, 21, 0.15)';
            ctx.fillRect(0, 0, width, height);

            // Draw grid
            ctx.strokeStyle = 'rgba(59, 130, 246, 0.1)';
            ctx.lineWidth = 0.5;
            for (let x = 0; x < width; x += 20) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            }
            for (let y = 0; y < height; y += 20) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }

            // Draw EKG waveform
            ctx.strokeStyle = '#22c55e';
            ctx.lineWidth = 2;
            ctx.shadowColor = '#22c55e';
            ctx.shadowBlur = 8;
            ctx.beginPath();

            for (let x = 0; x < width; x++) {
                const t = (x + offset) * 0.03;
                const cycle = t % (Math.PI * 2);

                let y = midY;

                // P wave
                if (cycle > 0.5 && cycle < 1.2) {
                    y = midY - Math.sin((cycle - 0.5) * 4.5) * 8;
                }
                // QRS complex
                else if (cycle > 1.4 && cycle < 1.6) {
                    y = midY + 6; // Q
                }
                else if (cycle > 1.6 && cycle < 1.8) {
                    y = midY - 35; // R (tall spike)
                }
                else if (cycle > 1.8 && cycle < 2.0) {
                    y = midY + 12; // S
                }
                // T wave
                else if (cycle > 2.4 && cycle < 3.2) {
                    y = midY - Math.sin((cycle - 2.4) * 4) * 10;
                }

                if (x === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
            ctx.shadowBlur = 0;

            offset += 2;
            animationId = requestAnimationFrame(drawEKG);
        };

        drawEKG();

        return () => cancelAnimationFrame(animationId);
    }, []);

    // Simulate heart rate variation
    useEffect(() => {
        const interval = setInterval(() => {
            setHeartRate(prev => {
                const change = (Math.random() - 0.5) * 4;
                return Math.max(60, Math.min(100, prev + change));
            });
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const primaryReading = readings[0];
    const config = CONDITION_CONFIG[primaryReading?.condition] || CONDITION_CONFIG['Normal'];

    return (
        <div className="glass-card rounded-2xl p-5 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-emerald-400 text-[18px]">ecg</span>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">EKG Monitör</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span className="text-[10px] text-emerald-400 font-bold">CANLI</span>
                </div>
            </div>

            {/* EKG Waveform Canvas */}
            <div className="relative rounded-xl overflow-hidden bg-[#0a0f1c] border border-white/5">
                <canvas
                    ref={canvasRef}
                    width={400}
                    height={100}
                    className="w-full h-[100px]"
                />
                {/* Heart Rate Overlay */}
                <div className="absolute top-2 right-2 flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-lg">
                    <span className="material-symbols-outlined text-red-400 text-[16px] animate-pulse">favorite</span>
                    <span className="text-sm font-bold text-white">{Math.round(heartRate)}</span>
                    <span className="text-[10px] text-slate-400">BPM</span>
                </div>
            </div>

            {/* Analysis Results */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest">Analiz Sonucu</span>
                    {isAnalyzing && (
                        <span className="text-[10px] text-blue-400 animate-pulse">Analiz ediliyor...</span>
                    )}
                </div>

                <div className={`flex items-center gap-3 p-3 rounded-xl ${config.severity === 'critical' ? 'bg-red-500/10 border border-red-500/30' :
                        config.severity === 'warning' ? 'bg-amber-500/10 border border-amber-500/30' :
                            'bg-emerald-500/10 border border-emerald-500/30'
                    }`}>
                    <span className={`material-symbols-outlined ${config.color} text-[24px]`}>
                        {config.icon}
                    </span>
                    <div className="flex-1">
                        <p className={`text-sm font-bold ${config.color}`}>
                            {config.label}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                            <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${config.severity === 'critical' ? 'bg-red-500' :
                                            config.severity === 'warning' ? 'bg-amber-500' :
                                                'bg-emerald-500'
                                        } transition-all duration-500`}
                                    style={{ width: `${primaryReading.probability * 100}%` }}
                                />
                            </div>
                            <span className="text-xs text-slate-400">
                                {(primaryReading.probability * 100).toFixed(0)}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Confidence Footer */}
            <div className="flex items-center justify-between pt-2 border-t border-white/5">
                <span className="text-xs text-slate-500">Model Güveni</span>
                <span className={`text-xs font-bold ${config.color}`}>{primaryReading.confidence}</span>
            </div>
        </div>
    );
}
