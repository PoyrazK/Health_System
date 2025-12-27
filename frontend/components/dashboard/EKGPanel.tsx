"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Activity, Upload, AlertCircle, RefreshCcw, Loader2 } from "lucide-react";

interface EKGPrediction {
    condition: string;
    probability: number;
    confidence: string;
}

interface EKGFeatures {
    heart_rate: number;
    rr_mean: number;
    rr_std: number;
    [key: string]: number;
}

export default function EKGPanel() {
    const [loading, setLoading] = useState(false);
    const [signal, setSignal] = useState<number[]>([]);
    const [results, setResults] = useState<{
        predictions: EKGPrediction[];
        features: EKGFeatures;
    } | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Generate demo signal on mount
    useEffect(() => {
        generateDemoSignal();
    }, []);

    const generateDemoSignal = () => {
        setLoading(true);
        // Simulate API call to fetch demo signal or generate client-side
        const demo: number[] = [];
        const points = 200;
        for (let i = 0; i < points; i++) {
            // Simple cardiac cycle simulation
            const x = i % 50;
            let y = 0;
            if (x < 5) y = 0.2 * Math.sin((x / 5) * Math.PI); // P wave
            else if (x >= 10 && x < 12) y = 2.0; // R peak
            else if (x >= 12 && x < 15) y = -0.5; // S wave
            else if (x >= 25 && x < 35) y = 0.4 * Math.sin(((x - 25) / 10) * Math.PI); // T wave

            y += (Math.random() - 0.5) * 0.1; // Noise
            demo.push(y);
        }
        setSignal(demo);
        setLoading(false);
    };

    const analyzeSignal = async () => {
        if (signal.length === 0) return;
        setLoading(true);
        setError(null);
        try {
            const response = await fetch("http://localhost:3000/api/ekg/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ signal, sampling_rate: 360 })
            });
            if (!response.ok) throw new Error("Analysis failed");
            const data = await response.json();
            setResults(data);
        } catch (err) {
            setError("AI Service Offline");
        } finally {
            setLoading(false);
        }
    };

    // SVG Waveform generator
    const renderWaveform = () => {
        if (signal.length === 0) return null;
        const width = 800;
        const height = 100;
        const step = width / (signal.length - 1);

        // Scale y to fit height
        const max = Math.max(...signal);
        const min = Math.min(...signal);
        const range = max - min || 1;
        const scale = (val: number) => height - ((val - min) / range) * height;

        const points = signal.map((y, i) => `${i * step},${scale(y)}`).join(" ");

        return (
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
                <defs>
                    <linearGradient id="wave-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
                        <stop offset="50%" stopColor="#3b82f6" stopOpacity="1" />
                        <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                    </linearGradient>
                </defs>
                <path
                    d={`M ${points}`}
                    fill="none"
                    stroke="url(#wave-gradient)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />
            </svg>
        );
    };

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-6 relative overflow-hidden group">
            {/* Background Grid */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
                style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />

            <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/20 rounded-lg">
                        <Activity className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                        <h3 className="text-sm font-black uppercase tracking-widest text-white/90">ECG Telemetry</h3>
                        <p className="text-[10px] text-white/40 uppercase tracking-tighter">Real-time signal analysis</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button onClick={generateDemoSignal} className="p-2 hover:bg-white/5 rounded-lg text-white/40 transition-colors">
                        <RefreshCcw className="w-4 h-4" />
                    </button>
                    <button className="p-2 hover:bg-white/5 rounded-lg text-white/40">
                        <Upload className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Waveform Window */}
            <div className="h-24 bg-black/40 border border-white/5 rounded-xl p-4 relative overflow-hidden">
                {loading ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                    </div>
                ) : renderWaveform()}

                {/* Heart Rate Indicator */}
                {results && (
                    <div className="absolute top-4 right-4 text-right">
                        <div className="text-2xl font-black text-blue-400 leading-none">
                            {results.features.heart_rate.toFixed(0)}
                            <span className="text-[10px] ml-1 text-white/40 font-normal uppercase">BPM</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Analysis Section */}
            <div className="space-y-4">
                {!results ? (
                    <button
                        onClick={analyzeSignal}
                        disabled={loading}
                        className="w-full py-3 bg-white/5 border border-white/10 rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-white/10 transition-all flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Initiate AI Analysis"}
                    </button>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-3">
                            <p className="text-[10px] font-black uppercase text-white/30 tracking-widest">Top Findings</p>
                            {results.predictions.map((p, i) => (
                                <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded-lg border border-white/10">
                                    <span className="text-xs font-bold text-white/80">{p.condition}</span>
                                    <span className="text-[10px] font-mono text-blue-400">{(p.probability * 100).toFixed(0)}%</span>
                                </div>
                            ))}
                        </div>
                        <div className="space-y-3">
                            <p className="text-[10px] font-black uppercase text-white/30 tracking-widest">Clinical Parameters</p>
                            <div className="grid grid-cols-2 gap-2">
                                <div className="bg-white/5 p-2 rounded-lg border border-white/10">
                                    <p className="text-[8px] text-white/40 uppercase">R-R Mean</p>
                                    <p className="text-xs font-mono">{results.features.rr_mean.toFixed(1)}ms</p>
                                </div>
                                <div className="bg-white/5 p-2 rounded-lg border border-white/10">
                                    <p className="text-[8px] text-white/40 uppercase">R-R Var</p>
                                    <p className="text-xs font-mono">{results.features.rr_std.toFixed(1)}ms</p>
                                </div>
                            </div>
                            {results.predictions[0]?.condition !== "Normal Sinus Rhythm" && (
                                <div className="flex items-center gap-2 p-2 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500">
                                    <AlertCircle className="w-3 h-3" />
                                    <span className="text-[10px] uppercase font-black">Anomaly Detected</span>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {error && (
                    <div className="text-center p-2 bg-red-500/10 rounded text-[10px] text-red-400 uppercase font-black tracking-widest border border-red-500/20">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
}
