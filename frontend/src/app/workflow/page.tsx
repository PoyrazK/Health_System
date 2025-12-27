'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import dynamic from 'next/dynamic';

const GradientBlinds = dynamic(() => import('@/components/GradientBlinds'), { ssr: false });

export default function WorkflowPage() {
    const steps = [
        {
            step: '01',
            title: 'Hasta Kabul',
            desc: 'Sezgisel bir arayüz aracılığıyla vital bulgular, semptomlar, tıbbi geçmiş ve mevcut ilaçlar dahil kapsamlı hasta verilerini yakalayın.',
            icon: 'assignment_ind',
            detail: 'Akıllı formlar ana şikayete göre uyarlanır ve ilgili geçmişi otomatik olarak çeker.'
        },
        {
            step: '02',
            title: 'Nöral İşleme',
            desc: 'Dört özelleşmiş YZ modeli hasta verilerini eş zamanlı analiz eder—kardiyak, metabolik, görüntüleme ve klinik akıl yürütme motorları.',
            icon: 'hub',
            detail: 'Paralel işleme %99.8 güvenle 120ms altında sonuç verir.'
        },
        {
            step: '03',
            title: 'Risk Katmanlandırma',
            desc: 'Kardiyovasküler olaylar, diyabetik komplikasyonlar, inme olasılığı ve daha fazlası için gerçek zamanlı risk skorları üretilir.',
            icon: 'speed',
            detail: 'Dinamik göstergeler sisteme yeni veri girdikçe güncellenir.'
        },
        {
            step: '04',
            title: 'Klinik Öneriler',
            desc: 'Kanıta dayalı tedavi protokolleri, ilaç etkileşim uyarıları ve takip planlaması ile YZ tarafından oluşturulan ayırıcı tanı.',
            icon: 'clinical_notes',
            detail: 'Tüm öneriler tıbbi literatürü ve kurumsal kılavuzları referans gösterir.'
        },
        {
            step: '05',
            title: 'Hekim İncelemesi',
            desc: 'İnsan-döngüde doğrulama, YZ önerilerinin sorumlu hekim tarafından incelenip onaylanmasını sağlar.',
            icon: 'verified_user',
            detail: 'YZ önerilerinin tek tıkla onayı veya düzenlenmesi.'
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
                        <span className="text-sm font-medium">Geri</span>
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
                                <span className="text-sm text-emerald-300">Klinik İş Akışı</span>
                            </div>
                            <h1 className="text-5xl md:text-7xl font-bold mb-6">
                                Kabulden<br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                                    Eyleme Dönük İçgörülere.
                                </span>
                            </h1>
                            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                                Hasta verilerini 2 dakikadan kısa sürede klinik zekaya
                                dönüştüren beş adımlı akıcı bir süreç.
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
                        <span>İş Akışını Dene</span>
                        <span className="material-symbols-outlined">arrow_forward</span>
                    </Link>
                </section>
            </div>
        </div>
    );
}
