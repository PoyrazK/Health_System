'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import dynamic from 'next/dynamic';

const GradientBlinds = dynamic(() => import('@/components/GradientBlinds'), { ssr: false });

export default function SolutionsPage() {
    const solutions = [
        {
            icon: 'ecg_heart',
            title: 'Cardiac Risk Assessment',
            desc: 'XGBoost-powered prediction model analyzing 47+ biomarkers to forecast cardiovascular events with 94% accuracy.',
            features: ['Real-time ECG analysis', 'Arrhythmia detection', 'Heart failure risk scoring']
        },
        {
            icon: 'glucose',
            title: 'Glycemic Trend Analysis',
            desc: 'LSTM neural networks tracking glucose patterns to predict hypoglycemic and hyperglycemic events up to 4 hours ahead.',
            features: ['Continuous monitoring', 'Trend prediction', 'Medication timing optimization']
        },
        {
            icon: 'radiology',
            title: 'Medical Imaging AI',
            desc: 'CNN-based analysis of X-rays, CT scans, and MRIs to detect anomalies and assist in differential diagnosis.',
            features: ['Pneumonia detection', 'Tumor identification', 'Fracture analysis']
        },
        {
            icon: 'psychology',
            title: 'Clinical Reasoning Engine',
            desc: 'GPT-4 powered differential diagnosis with evidence-based recommendations tailored to patient context.',
            features: ['Multi-condition reasoning', 'Drug interaction checks', 'Treatment protocols']
        }
    ];

    return (
        <div className="relative min-h-screen bg-[#0A0F1C] text-white">
            {/* Background */}
            <div className="fixed inset-0 z-0 opacity-50">
                <GradientBlinds
                    gradientColors={['#0A0F1C', '#1E3A8A', '#3B82F6', '#0A0F1C']}
                    angle={45}
                    noise={0.1}
                    blindCount={8}
                    className="w-full h-full"
                />
            </div>

            <div className="relative z-10">
                {/* Navigation */}
                <nav className="fixed top-6 left-6 z-50">
                    <Link
                        href="/"
                        className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md hover:bg-white/20 transition-colors"
                    >
                        <span className="material-symbols-outlined text-[18px]">arrow_back</span>
                        <span className="text-sm font-medium">Back</span>
                    </Link>
                </nav>

                {/* Hero */}
                <section className="pt-32 pb-20 px-6">
                    <div className="max-w-5xl mx-auto text-center">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
                                <span className="material-symbols-outlined text-blue-400">biotech</span>
                                <span className="text-sm text-blue-300">AI-Powered Solutions</span>
                            </div>
                            <h1 className="text-5xl md:text-7xl font-bold mb-6">
                                Four Neural Engines.<br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                                    One Unified Platform.
                                </span>
                            </h1>
                            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                                Harness the power of specialized AI models working in harmony to deliver
                                comprehensive clinical decision support.
                            </p>
                        </motion.div>
                    </div>
                </section>

                {/* Solutions Grid */}
                <section className="py-20 px-6">
                    <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8">
                        {solutions.map((solution, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="group relative p-8 rounded-3xl bg-white/[0.03] border border-white/10 hover:border-blue-500/30 transition-all"
                            >
                                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-6 shadow-lg shadow-blue-500/20">
                                    <span className="material-symbols-outlined text-white text-[28px]">{solution.icon}</span>
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-3">{solution.title}</h3>
                                <p className="text-slate-400 mb-6 leading-relaxed">{solution.desc}</p>
                                <ul className="space-y-2">
                                    {solution.features.map((feature, j) => (
                                        <li key={j} className="flex items-center gap-2 text-sm text-slate-500">
                                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* CTA */}
                <section className="py-20 px-6 text-center">
                    <Link
                        href="/#dashboard"
                        className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-[#0A0F1C] font-semibold hover:bg-slate-100 transition-colors"
                    >
                        <span>Experience the Dashboard</span>
                        <span className="material-symbols-outlined">arrow_forward</span>
                    </Link>
                </section>
            </div>
        </div>
    );
}
