import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, UserPlus, Dna } from 'lucide-react';

interface IntakeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: any) => void;
}

export const IntakeModal: React.FC<IntakeModalProps> = ({ isOpen, onClose, onSubmit }) => {
    const [form, setForm] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen && !form) {
            setLoading(true);
            // Simulate fetch or use real endpoint
            fetch("http://localhost:3000/api/defaults")
                .then(res => res.json())
                .then(data => {
                    setForm(data);
                    setLoading(false);
                })
                .catch(() => {
                    setForm({
                        age: 45, gender: 'Male', systolic_bp: 120, diastolic_bp: 80,
                        glucose: 100, bmi: 24.5, cholesterol: 190, heart_rate: 72, steps: 6000,
                        smoking: 'No', alcohol: 'No', medications: 'Lisinopril, Atorvastatin',
                        history_heart_disease: 'No', history_stroke: 'No',
                        history_diabetes: 'No', history_high_chol: 'No'
                    });
                    setLoading(false);
                });
        }
    }, [isOpen, form]);

    if (!isOpen) return null;

    if (loading || !form) return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/90 backdrop-blur-xl" />
            <div className="relative z-10 flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-sm font-bold text-blue-400 tracking-widest uppercase animate-pulse">Initializing Protocol...</p>
            </div>
        </div>
    );

    const inputClasses = "w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500/50 focus:bg-white/[0.05] transition-all font-medium placeholder:text-slate-700";
    const labelClasses = "text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1.5 block ml-1";

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 bg-black/80 backdrop-blur-md"
                onClick={onClose}
            />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="glass-card w-full max-w-2xl rounded-3xl p-8 relative z-10 border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Decorative background element */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/5 blur-[100px] rounded-full pointer-events-none" />

                <div className="flex justify-between items-center mb-8 relative">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-900/20">
                            <UserPlus className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-black text-white uppercase italic tracking-tighter">Clinical Intake Protocol</h2>
                            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">New Patient Entry</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/5 rounded-full transition-all text-slate-500 hover:text-white"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar pb-4 relative">
                    {Object.keys(form).map((key) => (
                        <div key={key} className={`space-y-1 ${key === 'medications' ? 'col-span-1 md:col-span-3' : ''}`}>
                            <label className={labelClasses}>{key.replace('_', ' ')}</label>

                            {key === 'gender' ? (
                                <div className="relative">
                                    <select
                                        className={`${inputClasses} appearance-none cursor-pointer`}
                                        value={form[key]}
                                        onChange={(e) => setForm({ ...form, gender: e.target.value })}
                                    >
                                        <option value="Male" className="bg-slate-900">Male</option>
                                        <option value="Female" className="bg-slate-900">Female</option>
                                    </select>
                                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
                                        <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </div>
                                </div>
                            ) : key === 'smoking' || key === 'alcohol' || key.startsWith('history_') ? (
                                <div className="relative">
                                    <select
                                        className={`${inputClasses} appearance-none cursor-pointer`}
                                        value={form[key]}
                                        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                                    >
                                        <option value="No" className="bg-slate-900">No</option>
                                        <option value="Yes" className="bg-slate-900">Yes</option>
                                    </select>
                                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
                                        <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </div>
                                </div>
                            ) : (
                                <input
                                    type={typeof form[key] === 'number' ? 'number' : 'text'}
                                    className={inputClasses}
                                    value={form[key]}
                                    onChange={(e) => setForm({ ...form, [key]: typeof form[key] === 'number' ? (e.target.value === '' ? 0 : Number(e.target.value)) : e.target.value })}
                                />
                            )}
                        </div>
                    ))}
                </div>

                <div className="mt-8 pt-6 border-t border-white/5 relative">
                    <button
                        onClick={() => onSubmit(form)}
                        className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-black tracking-[0.2em] rounded-2xl hover:from-blue-500 hover:to-indigo-500 transition-all uppercase shadow-xl shadow-blue-900/20 active:scale-[0.98] flex items-center justify-center gap-3"
                    >
                        <Dna className="w-5 h-5" /> Initialize AI Diagnostics
                    </button>
                </div>
            </motion.div>
        </div>
    );
};
