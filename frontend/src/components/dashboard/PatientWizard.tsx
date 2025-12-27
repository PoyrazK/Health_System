'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchDefaults, submitAssessment, DEFAULT_FORM_VALUES } from '@/lib/api';
import type { PatientFormData, AssessmentAPIResponse } from '@/lib/types';

interface PatientWizardProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmitSuccess?: (result: AssessmentAPIResponse) => void;
}

const STEPS = [
    { id: 1, title: 'Demografik', icon: 'person', description: 'Temel hasta bilgileri' },
    { id: 2, title: 'Vital Bulgular', icon: 'monitoring', description: 'Tansiyon & nabız' },
    { id: 3, title: 'Laboratuvar', icon: 'labs', description: 'Kan testleri & aktivite' },
    { id: 4, title: 'Tıbbi Geçmiş', icon: 'history', description: 'Geçmiş durumlar' },
    { id: 5, title: 'Yaşam Tarzı', icon: 'self_improvement', description: 'Alışkanlıklar & ilaçlar' },
];

export default function PatientWizard({ isOpen, onClose, onSubmitSuccess }: PatientWizardProps) {
    const [currentStep, setCurrentStep] = useState(1);
    const [form, setForm] = useState<PatientFormData | null>(null);
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [direction, setDirection] = useState(0);

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
                        history_heart_disease: (data.history_heart_disease as 'Yes' | 'No') || 'No',
                        history_stroke: (data.history_stroke as 'Yes' | 'No') || 'No',
                        history_diabetes: (data.history_diabetes as 'Yes' | 'No') || 'No',
                        history_high_chol: (data.history_high_chol as 'Yes' | 'No') || 'No',
                        symptoms: data.symptoms || '',
                    });
                })
                .catch(() => {
                    setForm({
                        ...DEFAULT_FORM_VALUES,
                        history_heart_disease: 'No',
                        history_stroke: 'No',
                        history_diabetes: 'No',
                        history_high_chol: 'No',
                        symptoms: '',
                    });
                })
                .finally(() => setLoading(false));
        }
    }, [isOpen, form]);

    // Reset form when modal closes
    useEffect(() => {
        if (!isOpen) {
            setForm(null);
            setError(null);
            setCurrentStep(1);
        }
    }, [isOpen]);

    const handleSubmit = async () => {
        if (!form) return;

        setSubmitting(true);
        setError(null);

        try {
            const result = await submitAssessment(form);
            onSubmitSuccess?.(result);
            onClose();
        } catch {
            setError('Değerlendirme gönderilemedi. Lütfen tekrar deneyin.');
        } finally {
            setSubmitting(false);
        }
    };

    const nextStep = () => {
        if (currentStep < STEPS.length) {
            setDirection(1);
            setCurrentStep(currentStep + 1);
        }
    };

    const prevStep = () => {
        if (currentStep > 1) {
            setDirection(-1);
            setCurrentStep(currentStep - 1);
        }
    };

    const goToStep = (step: number) => {
        setDirection(step > currentStep ? 1 : -1);
        setCurrentStep(step);
    };

    const updateField = <K extends keyof PatientFormData>(key: K, value: PatientFormData[K]) => {
        if (form) {
            setForm({ ...form, [key]: value });
        }
    };

    const inputClasses = "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-blue-500 outline-none text-white transition-all placeholder:text-slate-600 text-lg";
    const selectClasses = "w-full bg-[#1a1c23] border border-white/10 rounded-xl px-4 py-3 focus:border-blue-500 outline-none text-white transition-all cursor-pointer text-lg";
    const labelClasses = "text-xs text-slate-400 uppercase font-bold tracking-widest mb-2 block";

    const slideVariants = {
        enter: (direction: number) => ({
            x: direction > 0 ? 300 : -300,
            opacity: 0,
        }),
        center: {
            x: 0,
            opacity: 1,
        },
        exit: (direction: number) => ({
            x: direction < 0 ? 300 : -300,
            opacity: 0,
        }),
    };

    const renderStepContent = () => {
        if (!form) return null;

        switch (currentStep) {
            case 1:
                return (
                    <div className="space-y-4">
                        <div className="text-center mb-4">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mx-auto mb-3">
                                <span className="material-symbols-outlined text-white text-3xl">person</span>
                            </div>
                            <h3 className="text-lg font-bold text-white">Hasta Demografisi</h3>
                            <p className="text-xs text-slate-400 mt-1">Temel hasta bilgilerini girin</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="col-span-2 sm:col-span-1">
                                <label className={labelClasses}>Yaş</label>
                                <input
                                    type="number"
                                    value={form.age}
                                    onChange={(e) => updateField('age', parseInt(e.target.value) || 0)}
                                    className={inputClasses}
                                    min={0}
                                    max={120}
                                />
                            </div>
                            <div className="col-span-2 sm:col-span-1">
                                <label className={labelClasses}>Cinsiyet</label>
                                <select
                                    value={form.gender}
                                    onChange={(e) => updateField('gender', e.target.value as 'Male' | 'Female')}
                                    className={selectClasses}
                                >
                                    <option value="Male">Erkek</option>
                                    <option value="Female">Kadın</option>
                                </select>
                            </div>
                            <div className="col-span-2">
                                <label className={labelClasses}>VKİ (Vücut Kitle İndeksi)</label>
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
                );

            case 2:
                return (
                    <div className="space-y-4">
                        <div className="text-center mb-4">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center mx-auto mb-3">
                                <span className="material-symbols-outlined text-white text-3xl">monitoring</span>
                            </div>
                            <h3 className="text-lg font-bold text-white">Vital Bulgular</h3>
                            <p className="text-xs text-slate-400 mt-1">Tansiyon ve nabız değerleri</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelClasses}>Sistolik KB (mmHg)</label>
                                <input
                                    type="number"
                                    value={form.systolic_bp}
                                    onChange={(e) => updateField('systolic_bp', parseInt(e.target.value) || 0)}
                                    className={inputClasses}
                                />
                            </div>
                            <div>
                                <label className={labelClasses}>Diastolik KB (mmHg)</label>
                                <input
                                    type="number"
                                    value={form.diastolic_bp}
                                    onChange={(e) => updateField('diastolic_bp', parseInt(e.target.value) || 0)}
                                    className={inputClasses}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className={labelClasses}>Nabız (BPM)</label>
                                <input
                                    type="number"
                                    value={form.heart_rate}
                                    onChange={(e) => updateField('heart_rate', parseInt(e.target.value) || 0)}
                                    className={inputClasses}
                                />
                            </div>
                        </div>
                    </div>
                );

            case 3:
                return (
                    <div className="space-y-4">
                        <div className="text-center mb-4">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center mx-auto mb-3">
                                <span className="material-symbols-outlined text-white text-3xl">labs</span>
                            </div>
                            <h3 className="text-lg font-bold text-white">Laboratuvar Değerleri</h3>
                            <p className="text-xs text-slate-400 mt-1">Kan testleri ve aktivite seviyesi</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelClasses}>Glikoz (mg/dL)</label>
                                <input
                                    type="number"
                                    value={form.glucose}
                                    onChange={(e) => updateField('glucose', parseInt(e.target.value) || 0)}
                                    className={inputClasses}
                                />
                            </div>
                            <div>
                                <label className={labelClasses}>Kolesterol (mg/dL)</label>
                                <input
                                    type="number"
                                    value={form.cholesterol}
                                    onChange={(e) => updateField('cholesterol', parseInt(e.target.value) || 0)}
                                    className={inputClasses}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className={labelClasses}>Günlük Adım</label>
                                <input
                                    type="number"
                                    value={form.steps}
                                    onChange={(e) => updateField('steps', parseInt(e.target.value) || 0)}
                                    className={inputClasses}
                                />
                            </div>
                        </div>
                    </div>
                );

            case 4:
                return (
                    <div className="space-y-4">
                        <div className="text-center mb-4">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center mx-auto mb-3">
                                <span className="material-symbols-outlined text-white text-3xl">history</span>
                            </div>
                            <h3 className="text-lg font-bold text-white">Tıbbi Geçmiş</h3>
                            <p className="text-xs text-slate-400 mt-1">Geçmiş hastalıklar ve teşhisler</p>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            {[
                                { key: 'history_heart_disease' as const, label: 'Kalp Hastalığı', icon: 'cardiology' },
                                { key: 'history_diabetes' as const, label: 'Diyabet', icon: 'water_drop' },
                                { key: 'history_stroke' as const, label: 'İnme', icon: 'neurology' },
                                { key: 'history_high_chol' as const, label: 'Yüksek Kolesterol', icon: 'science' },
                            ].map((item) => (
                                <button
                                    key={item.key}
                                    type="button"
                                    onClick={() => updateField(item.key, form[item.key] === 'Yes' ? 'No' : 'Yes')}
                                    className={`p-3 rounded-xl border-2 transition-all flex flex-col items-center gap-1 ${form[item.key] === 'Yes'
                                        ? 'border-red-500 bg-red-500/20 text-red-400'
                                        : 'border-white/10 bg-white/5 text-slate-400 hover:border-white/20'
                                        }`}
                                >
                                    <span className="material-symbols-outlined text-xl">{item.icon}</span>
                                    <span className="text-xs font-medium">{item.label}</span>
                                    <span className={`text-[10px] ${form[item.key] === 'Yes' ? 'text-red-400' : 'text-slate-500'}`}>
                                        {form[item.key] === 'Yes' ? 'Evet' : 'Hayır'}
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>
                );

            case 5:
                return (
                    <div className="space-y-4">
                        <div className="text-center mb-4">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mx-auto mb-3">
                                <span className="material-symbols-outlined text-white text-3xl">self_improvement</span>
                            </div>
                            <h3 className="text-lg font-bold text-white">Yaşam Tarzı & İlaçlar</h3>
                            <p className="text-xs text-slate-400 mt-1">Alışkanlıklar ve mevcut tedaviler</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelClasses}>Sigara</label>
                                <select
                                    value={form.smoking}
                                    onChange={(e) => updateField('smoking', e.target.value as 'Yes' | 'No' | 'Former')}
                                    className={selectClasses}
                                >
                                    <option value="No">Hayır</option>
                                    <option value="Yes">Evet</option>
                                    <option value="Former">Bırakmış</option>
                                </select>
                            </div>
                            <div>
                                <label className={labelClasses}>Alkol</label>
                                <select
                                    value={form.alcohol}
                                    onChange={(e) => updateField('alcohol', e.target.value as 'Yes' | 'No')}
                                    className={selectClasses}
                                >
                                    <option value="No">Hayır</option>
                                    <option value="Yes">Evet</option>
                                </select>
                            </div>
                            <div className="col-span-2">
                                <label className={labelClasses}>Mevcut İlaçlar</label>
                                <input
                                    type="text"
                                    value={form.medications}
                                    onChange={(e) => updateField('medications', e.target.value)}
                                    placeholder="ör: Lisinopril, Metformin, Atorvastatin"
                                    className={inputClasses}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className={labelClasses}>Semptomlar (virgülle ayırın)</label>
                                <textarea
                                    value={form.symptoms}
                                    onChange={(e) => updateField('symptoms', e.target.value)}
                                    placeholder="ör: göğüs ağrısı, nefes darlığı, yorgunluk"
                                    className={`${inputClasses} resize-none h-20`}
                                />
                            </div>
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
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
                        className="glass-card w-full max-w-xl rounded-3xl relative z-10 overflow-hidden max-h-[90vh] flex flex-col"
                    >
                        {/* Gradient accent */}
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-500" />

                        {/* Header */}
                        <div className="flex justify-between items-center p-4 border-b border-white/5 flex-shrink-0">
                            <div>
                                <h2 className="text-lg font-bold text-white">Yeni Hasta Kaydı</h2>
                                <p className="text-xs text-slate-500">Adım {currentStep} / {STEPS.length}</p>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 rounded-full hover:bg-white/5 text-slate-400 hover:text-white transition-all"
                                disabled={submitting}
                            >
                                <span className="material-symbols-outlined">close</span>
                            </button>
                        </div>

                        {/* Step Indicators */}
                        <div className="flex items-center justify-between px-4 py-3 bg-white/[0.02] flex-shrink-0">
                            {STEPS.map((step, index) => (
                                <button
                                    key={step.id}
                                    onClick={() => goToStep(step.id)}
                                    className="flex flex-col items-center gap-1 group"
                                >
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all ${currentStep === step.id
                                        ? 'bg-blue-500 text-white'
                                        : currentStep > step.id
                                            ? 'bg-emerald-500/20 text-emerald-400'
                                            : 'bg-white/5 text-slate-500 group-hover:bg-white/10'
                                        }`}>
                                        {currentStep > step.id ? (
                                            <span className="material-symbols-outlined text-sm">check</span>
                                        ) : (
                                            <span className="material-symbols-outlined text-sm">{step.icon}</span>
                                        )}
                                    </div>
                                    <span className={`text-[9px] font-medium hidden sm:block ${currentStep === step.id ? 'text-blue-400' : 'text-slate-500'
                                        }`}>
                                        {step.title}
                                    </span>
                                    {index < STEPS.length - 1 && (
                                        <div className={`absolute w-[calc(100%/5-2rem)] h-0.5 left-[calc(${index}*20%+10%+1.25rem)] top-[calc(1rem+5px)] ${currentStep > step.id ? 'bg-emerald-500/50' : 'bg-white/10'
                                            }`} />
                                    )}
                                </button>
                            ))}
                        </div>

                        {/* Progress Bar */}
                        <div className="h-0.5 bg-white/5 flex-shrink-0">
                            <motion.div
                                className="h-full bg-gradient-to-r from-blue-500 to-emerald-500"
                                initial={{ width: 0 }}
                                animate={{ width: `${(currentStep / STEPS.length) * 100}%` }}
                                transition={{ duration: 0.3 }}
                            />
                        </div>

                        {/* Content */}
                        <div className="p-4 overflow-y-auto flex-1 min-h-0">
                            {loading ? (
                                <div className="flex flex-col items-center justify-center h-[250px] gap-4">
                                    <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                                    <p className="text-sm text-slate-400">Form yükleniyor...</p>
                                </div>
                            ) : error ? (
                                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3 mb-4">
                                    <span className="material-symbols-outlined text-red-400">error</span>
                                    <p className="text-sm text-red-400">{error}</p>
                                </div>
                            ) : (
                                <AnimatePresence mode="wait" custom={direction}>
                                    <motion.div
                                        key={currentStep}
                                        custom={direction}
                                        variants={slideVariants}
                                        initial="enter"
                                        animate="center"
                                        exit="exit"
                                        transition={{ duration: 0.3, ease: 'easeInOut' }}
                                    >
                                        {renderStepContent()}
                                    </motion.div>
                                </AnimatePresence>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="flex gap-3 p-4 border-t border-white/5 flex-shrink-0">
                            <button
                                type="button"
                                onClick={currentStep === 1 ? onClose : prevStep}
                                disabled={submitting}
                                className="flex-1 h-10 rounded-xl border border-white/10 text-sm font-bold hover:bg-white/5 transition-all text-slate-300 disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {currentStep === 1 ? (
                                    'İptal'
                                ) : (
                                    <>
                                        <span className="material-symbols-outlined text-base">arrow_back</span>
                                        Geri
                                    </>
                                )}
                            </button>
                            <button
                                type="button"
                                onClick={currentStep === STEPS.length ? handleSubmit : nextStep}
                                disabled={submitting || loading}
                                className="flex-1 h-10 rounded-xl bg-gradient-to-r from-blue-500 to-emerald-500 text-white font-bold transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 flex items-center justify-center gap-2 hover:shadow-xl hover:shadow-blue-500/30"
                            >
                                {submitting ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                        Analiz Ediliyor...
                                    </>
                                ) : currentStep === STEPS.length ? (
                                    <>
                                        <span className="material-symbols-outlined text-base">labs</span>
                                        Hastayı Analiz Et
                                    </>
                                ) : (
                                    <>
                                        İleri
                                        <span className="material-symbols-outlined text-base">arrow_forward</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
