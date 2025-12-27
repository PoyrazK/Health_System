"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Search, Activity, ChevronRight, Check, AlertCircle } from "lucide-react";

interface DiseasePrediction {
    disease: string;
    probability: number;
    confidence: string;
}

interface DiseaseCheckerModalProps {
    isOpen: boolean;
    onClose: () => void;
}

// Subset of common symptoms from the 318 features
const COMMON_SYMPTOMS = [
    "fever", "cough", "headache", "nausea", "vomiting", "fatigue",
    "dizziness", "shortness of breath", "chest pain", "sore throat",
    "diarrhea", "constipation", "muscle pain", "joint pain", "back pain",
    "skin rash", "itching of skin", "nasal congestion", "sneezing",
    "fainting", "seizures", "blurred vision", "ringing in ear",
    "weight loss", "weight gain", "loss of appetite"
].sort();

export default function DiseaseCheckerModal({ isOpen, onClose }: DiseaseCheckerModalProps) {
    const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
    const [search, setSearch] = useState("");
    const [predictions, setPredictions] = useState<DiseasePrediction[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const toggleSymptom = (symptom: string) => {
        setSelectedSymptoms(prev =>
            prev.includes(symptom)
                ? prev.filter(s => s !== symptom)
                : [...prev, symptom]
        );
    };

    const handlePredict = async () => {
        if (selectedSymptoms.length === 0) return;

        setLoading(true);
        setError(null);
        try {
            const response = await fetch("http://localhost:3000/api/disease/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symptoms: selectedSymptoms }),
            });

            if (!response.ok) throw new Error("Failed to get prediction");

            const data = await response.json();
            setPredictions(data.predictions || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    const filteredSymptoms = COMMON_SYMPTOMS.filter(s =>
        s.toLowerCase().includes(search.toLowerCase())
    );

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="w-full max-w-2xl bg-[#0a0a0f] border border-white/10 rounded-2xl overflow-hidden shadow-2xl"
            >
                {/* Header */}
                <div className="p-6 border-b border-white/10 flex items-center justify-between bg-gradient-to-r from-blue-500/10 to-purple-500/10">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500/20 rounded-lg">
                            <Activity className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold tracking-tight uppercase">AI Disease Classifier</h2>
                            <p className="text-xs text-white/40">Select symptoms for differential diagnosis</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                        <X className="w-5 h-5 text-white/40" />
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 h-[500px]">
                    {/* Left: Symptom Selector */}
                    <div className="p-6 border-r border-white/10 flex flex-col gap-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" />
                            <input
                                type="text"
                                placeholder="Search symptoms..."
                                className="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-blue-500/50"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                            />
                        </div>

                        <div className="flex-1 overflow-y-auto space-y-1 pr-2 custom-scrollbar">
                            {filteredSymptoms.map(symptom => (
                                <button
                                    key={symptom}
                                    onClick={() => toggleSymptom(symptom)}
                                    className={`w-full flex items-center justify-between p-3 rounded-lg text-sm transition-all ${selectedSymptoms.includes(symptom)
                                            ? "bg-blue-500/20 border-blue-500/30 text-blue-100"
                                            : "bg-white/5 border border-transparent text-white/60 hover:bg-white/10"
                                        }`}
                                >
                                    <span className="capitalize">{symptom}</span>
                                    {selectedSymptoms.includes(symptom) && <Check className="w-4 h-4" />}
                                </button>
                            ))}
                        </div>

                        <button
                            disabled={selectedSymptoms.length === 0 || loading}
                            onClick={handlePredict}
                            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>Run AI Analysis <ChevronRight className="w-4 h-4" /></>
                            )}
                        </button>
                    </div>

                    {/* Right: Results */}
                    <div className="p-6 bg-black/20 flex flex-col gap-6 overflow-y-auto custom-scrollbar">
                        <h3 className="text-xs font-black uppercase tracking-widest text-white/40">Analysis Results</h3>

                        <AnimatePresence mode="wait">
                            {predictions.length > 0 ? (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="space-y-4"
                                >
                                    {predictions.map((p, i) => (
                                        <motion.div
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: i * 0.1 }}
                                            key={p.disease}
                                            className="bg-white/5 border border-white/10 p-4 rounded-xl space-y-2 relative overflow-hidden"
                                        >
                                            <div className="flex justify-between items-start">
                                                <h4 className="font-bold text-white/90 leading-tight pr-8">{p.disease}</h4>
                                                <span className={`text-[10px] px-2 py-0.5 rounded-full border ${p.confidence === 'high' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
                                                        p.confidence === 'medium' ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' :
                                                            'bg-red-500/10 border-red-500/30 text-red-400'
                                                    }`}>
                                                    {p.confidence.toUpperCase()}
                                                </span>
                                            </div>
                                            <div className="space-y-1">
                                                <div className="flex justify-between text-[10px] text-white/40 uppercase tracking-tighter">
                                                    <span>Probability</span>
                                                    <span>{p.probability}%</span>
                                                </div>
                                                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                                    <motion.div
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${p.probability}%` }}
                                                        className={`h-full ${p.probability > 70 ? 'bg-red-500' :
                                                                p.probability > 30 ? 'bg-yellow-500' :
                                                                    'bg-blue-500'
                                                            }`}
                                                    />
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}

                                    <div className="p-3 bg-white/5 border border-white/10 rounded-lg flex gap-3 text-xs text-white/60">
                                        <AlertCircle className="w-4 h-4 flex-shrink-0 text-blue-400" />
                                        <p>These results are for clinical decision support only. Correlate with physical findings and history.</p>
                                    </div>
                                </motion.div>
                            ) : (
                                <div key="placeholder" className="h-full flex flex-col items-center justify-center text-center opacity-30 gap-4">
                                    <Activity className="w-12 h-12" />
                                    <p className="text-sm">Select symptoms and run<br />analysis to see results</p>
                                </div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
