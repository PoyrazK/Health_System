'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchDefaults, submitAssessment, DEFAULT_FORM_VALUES } from '@/lib/api';
import type { PatientFormData, AssessmentAPIResponse } from '@/lib/types';

interface IntakeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmitSuccess?: (result: AssessmentAPIResponse) => void;
}

export default function IntakeModal({ isOpen, onClose, onSubmitSuccess }: IntakeModalProps) {
    const [form, setForm] = useState<PatientFormData | null>(null);
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch default values when modal opens
    useEffect(() => {
        if (isOpen && !form) {
            setLoading(true);
            setError(null);
            fetchDefaults()
                .then((data) => {
                    setForm({
                        age: data.age,
                        gender: data.gender,
                        systolic_bp: data.systolic_bp,
                        diastolic_bp: data.diastolic_bp,
                        glucose: data.glucose,
                        bmi: data.bmi,
                        cholesterol: data.cholesterol,
                        heart_rate: data.heart_rate,
                        steps: data.steps,
                        smoking: data.smoking,
                        alcohol: data.alcohol,
                        medications: data.medications,
                    });
                })
                .catch(() => {
                    // Fallback to default values if API fails
                    setForm(DEFAULT_FORM_VALUES);
                })
                .finally(() => setLoading(false));
        }
    }, [isOpen, form]);

    // Reset form when modal closes
    useEffect(() => {
        if (!isOpen) {
            setForm(null);
            setError(null);
        }
    }, [isOpen]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!form) return;

        setSubmitting(true);
        setError(null);

        try {
            const result = await submitAssessment(form);
            onSubmitSuccess?.(result);
            onClose();
        } catch (err) {
            setError('Failed to submit assessment. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const updateField = <K extends keyof PatientFormData>(key: K, value: PatientFormData[K]) => {
        if (form) {
            setForm({ ...form, [key]: value });
        }
    };

    const inputClasses = "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 focus:border-blue-500 outline-none text-white transition-all placeholder:text-slate-600";
    const labelClasses = "text-[10px] text-slate-500 uppercase font-bold tracking-widest";
    const selectClasses = "w-full bg-[#1a1c23] border border-white/10 rounded-xl px-4 py-2.5 focus:border-blue-500 outline-none text-white transition-all cursor-pointer";

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/80 backdrop-blur-md"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="glass-card w-full max-w-3xl rounded-3xl p-8 space-y-6 relative z-10 overflow-hidden max-h-[90vh] overflow-y-auto custom-scrollbar"
                    >
                        {/* Gradient accent */}
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-emerald-500" />

                        {/* Header */}
                        <div className="flex justify-between items-center">
                            <div>
                                <h2 className="text-2xl font-bold text-white">New Assessment Intake</h2>
                                <p className="text-sm text-slate-500">Submit patient vitals for real-time risk stratification</p>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 rounded-full hover:bg-white/5 text-slate-400 hover:text-white transition-all"
                                disabled={submitting}
                            >
                                <span className="material-symbols-outlined">close</span>
                            </button>
                        </div>

                        {/* Loading State */}
                        {loading && (
                            <div className="flex flex-col items-center justify-center py-12 gap-4">
                                <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                                <p className="text-sm text-slate-400">Loading form defaults...</p>
                            </div>
                        )}

                        {/* Error State */}
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3">
                                <span className="material-symbols-outlined text-red-400">error</span>
                                <p className="text-sm text-red-400">{error}</p>
                            </div>
                        )}

                        {/* Form */}
                        {!loading && form && (
                            <form onSubmit={handleSubmit} className="space-y-6">
                                {/* Demographics */}
                                <div className="space-y-4">
                                    <h3 className="text-xs text-slate-400 uppercase tracking-widest font-bold flex items-center gap-2">
                                        <span className="material-symbols-outlined text-[16px]">person</span>
                                        Demographics
                                    </h3>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Age (years)</label>
                                            <input
                                                type="number"
                                                value={form.age}
                                                onChange={(e) => updateField('age', parseInt(e.target.value) || 0)}
                                                className={inputClasses}
                                                min={0}
                                                max={120}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Gender</label>
                                            <select
                                                value={form.gender}
                                                onChange={(e) => updateField('gender', e.target.value as 'Male' | 'Female')}
                                                className={selectClasses}
                                            >
                                                <option value="Male">Male</option>
                                                <option value="Female">Female</option>
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className={labelClasses}>BMI</label>
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={form.bmi}
                                                onChange={(e) => updateField('bmi', parseFloat(e.target.value) || 0)}
                                                className={inputClasses}
                                                min={10}
                                                max={60}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Vitals */}
                                <div className="space-y-4">
                                    <h3 className="text-xs text-slate-400 uppercase tracking-widest font-bold flex items-center gap-2">
                                        <span className="material-symbols-outlined text-[16px]">monitoring</span>
                                        Vital Signs
                                    </h3>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Systolic BP (mmHg)</label>
                                            <input
                                                type="number"
                                                value={form.systolic_bp}
                                                onChange={(e) => updateField('systolic_bp', parseInt(e.target.value) || 0)}
                                                className={inputClasses}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Diastolic BP (mmHg)</label>
                                            <input
                                                type="number"
                                                value={form.diastolic_bp}
                                                onChange={(e) => updateField('diastolic_bp', parseInt(e.target.value) || 0)}
                                                className={inputClasses}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Heart Rate (BPM)</label>
                                            <input
                                                type="number"
                                                value={form.heart_rate}
                                                onChange={(e) => updateField('heart_rate', parseInt(e.target.value) || 0)}
                                                className={inputClasses}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Lab Values */}
                                <div className="space-y-4">
                                    <h3 className="text-xs text-slate-400 uppercase tracking-widest font-bold flex items-center gap-2">
                                        <span className="material-symbols-outlined text-[16px]">labs</span>
                                        Lab Values
                                    </h3>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Glucose (mg/dL)</label>
                                            <input
                                                type="number"
                                                value={form.glucose}
                                                onChange={(e) => updateField('glucose', parseInt(e.target.value) || 0)}
                                                className={inputClasses}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Cholesterol (mg/dL)</label>
                                            <input
                                                type="number"
                                                value={form.cholesterol}
                                                onChange={(e) => updateField('cholesterol', parseInt(e.target.value) || 0)}
                                                className={inputClasses}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Daily Steps</label>
                                            <input
                                                type="number"
                                                value={form.steps}
                                                onChange={(e) => updateField('steps', parseInt(e.target.value) || 0)}
                                                className={inputClasses}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Lifestyle */}
                                <div className="space-y-4">
                                    <h3 className="text-xs text-slate-400 uppercase tracking-widest font-bold flex items-center gap-2">
                                        <span className="material-symbols-outlined text-[16px]">self_improvement</span>
                                        Lifestyle
                                    </h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Smoking</label>
                                            <select
                                                value={form.smoking}
                                                onChange={(e) => updateField('smoking', e.target.value as 'Yes' | 'No' | 'Former')}
                                                className={selectClasses}
                                            >
                                                <option value="No">No</option>
                                                <option value="Yes">Yes</option>
                                                <option value="Former">Former</option>
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className={labelClasses}>Alcohol</label>
                                            <select
                                                value={form.alcohol}
                                                onChange={(e) => updateField('alcohol', e.target.value as 'Yes' | 'No')}
                                                className={selectClasses}
                                            >
                                                <option value="No">No</option>
                                                <option value="Yes">Yes</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                {/* Medications */}
                                <div className="space-y-4">
                                    <h3 className="text-xs text-slate-400 uppercase tracking-widest font-bold flex items-center gap-2">
                                        <span className="material-symbols-outlined text-[16px]">medication</span>
                                        Medications
                                    </h3>
                                    <div className="space-y-2">
                                        <label className={labelClasses}>Current Medications (comma-separated)</label>
                                        <input
                                            type="text"
                                            value={form.medications}
                                            onChange={(e) => updateField('medications', e.target.value)}
                                            placeholder="e.g., Lisinopril, Metformin, Atorvastatin"
                                            className={inputClasses}
                                        />
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex gap-4 pt-4 border-t border-white/5">
                                    <button
                                        type="button"
                                        onClick={onClose}
                                        disabled={submitting}
                                        className="flex-1 h-12 rounded-2xl border border-white/10 text-sm font-bold hover:bg-white/5 transition-all text-slate-300 disabled:opacity-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={submitting}
                                        className="flex-1 h-12 rounded-2xl bg-[#3B82F6] hover:bg-blue-600 text-white font-bold transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
                                    >
                                        {submitting ? (
                                            <>
                                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                                Analyzing...
                                            </>
                                        ) : (
                                            <>
                                                <span className="material-symbols-outlined text-[18px]">labs</span>
                                                Analyze Patient
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        )}
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
