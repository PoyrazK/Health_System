'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import dynamic from 'next/dynamic';

const GradientBlinds = dynamic(() => import('@/components/GradientBlinds'), { ssr: false });

export default function WorkflowPage() {
    const steps = [
        {
            step: '01',
            title: 'Patient Intake',
            desc: 'Capture comprehensive patient data including vitals, symptoms, medical history, and current medications through an intuitive interface.',
            icon: 'assignment_ind',
            detail: 'Smart forms adapt based on chief complaint, pulling relevant history automatically.'
        },
        {
            step: '02',
            title: 'Neural Processing',
            desc: 'Four specialized AI models simultaneously analyze the patient data—cardiac, metabolic, imaging, and clinical reasoning engines.',
            icon: 'hub',
            detail: 'Parallel processing delivers results in under 120ms with 99.8% confidence.'
        },
        {
            step: '03',
            title: 'Risk Stratification',
            desc: 'Real-time risk scores generated for cardiovascular events, diabetic complications, stroke probability, and more.',
            icon: 'speed',
            detail: 'Dynamic gauges update as new data enters the system.'
        },
        {
            step: '04',
            title: 'Clinical Recommendations',
            desc: 'AI-generated differential diagnosis with evidence-based treatment protocols, drug interaction alerts, and follow-up scheduling.',
            icon: 'clinical_notes',
            detail: 'All recommendations cite medical literature and institutional guidelines.'
        },
        {
            step: '05',
            title: 'Physician Review',
            desc: 'Human-in-the-loop validation ensures AI suggestions are reviewed and approved by the attending physician.',
            icon: 'verified_user',
            detail: 'One-click approval or modification of AI recommendations.'
        }
    ];

    return (
        <div className="relative min-h-screen bg-[#0A0F1C] text-white">
            {/* Background */}
            <div className="fixed inset-0 z-0 opacity-50">
                <GradientBlinds
                    gradientColors={['#0A0F1C', '#1E3A8A', '#3B82F6', '#0A0F1C']}
                    angle={-45}
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
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
                                <span className="material-symbols-outlined text-emerald-400">account_tree</span>
                                <span className="text-sm text-emerald-300">Clinical Workflow</span>
                            </div>
                            <h1 className="text-5xl md:text-7xl font-bold mb-6">
                                From Intake to<br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                                    Actionable Insights.
                                </span>
                            </h1>
                            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                                A streamlined five-step process that transforms patient data into
                                clinical intelligence in under 2 minutes.
                            </p>
                        </motion.div>
                    </div>
                </section>

                {/* Steps Timeline */}
                <section className="py-20 px-6">
                    <div className="max-w-4xl mx-auto">
                        {steps.map((step, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="relative flex gap-8 mb-12 last:mb-0"
                            >
                                {/* Timeline line */}
                                {i < steps.length - 1 && (
                                    <div className="absolute left-[27px] top-16 w-0.5 h-full bg-gradient-to-b from-blue-500/50 to-transparent" />
                                )}

                                {/* Step number */}
                                <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-xl font-bold shadow-lg shadow-blue-500/20">
                                    {step.step}
                                </div>

                                {/* Content */}
                                <div className="flex-1 pb-8">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="material-symbols-outlined text-blue-400">{step.icon}</span>
                                        <h3 className="text-2xl font-bold text-white">{step.title}</h3>
                                    </div>
                                    <p className="text-slate-400 mb-3">{step.desc}</p>
                                    <p className="text-sm text-slate-500 italic">{step.detail}</p>
                                </div>
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
                        <span>Try the Workflow</span>
                        <span className="material-symbols-outlined">arrow_forward</span>
                    </Link>
                </section>
            </div>
        </div>
    );
}
