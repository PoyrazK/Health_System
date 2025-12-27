'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import dynamic from 'next/dynamic';

const GradientBlinds = dynamic(() => import('@/components/GradientBlinds'), { ssr: false });

export default function SolutionsPage() {
    const solutions = [
        {
            icon: 'ecg_heart',
            title: 'Kardiyak Risk Değerlendirmesi',
            desc: 'Kardiyovasküler olayları %94 doğrulukla tahmin etmek için 47+ biyobelirteci analiz eden XGBoost destekli öngörü modeli.',
            features: ['Gerçek zamanlı EKG analizi', 'Aritmi tespiti', 'Kalp yetmezliği risk puanlaması']
        },
        {
            icon: 'glucose',
            title: 'Glisemik Trend Analizi',
            desc: '4 saate kadar öncesinden hipoglisemik ve hiperglisemik olayları öngörmek için glikoz paternlerini takip eden LSTM sinir ağları.',
            features: ['Sürekli izleme', 'Trend tahmini', 'İlaç zamanlama optimizasyonu']
        },
        {
            icon: 'radiology',
            title: 'Tıbbi Görüntüleme YZ',
            desc: 'Anomalileri tespit etmek ve ayırıcı tanıya yardımcı olmak için X-ray, BT taramaları ve MR\'ların CNN tabanlı analizi.',
            features: ['Pnömoni tespiti', 'Tümör tanımlama', 'Kırık analizi']
        },
        {
            icon: 'psychology',
            title: 'Klinik Akıl Yürütme Motoru',
            desc: 'Hasta bağlamına göre uyarlanmış kanıta dayalı önerilerle GPT-4 destekli ayırıcı tanı.',
            features: ['Çoklu durum akıl yürütme', 'İlaç etkileşim kontrolleri', 'Tedavi protokolleri']
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
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
                                <span className="material-symbols-outlined text-blue-400">biotech</span>
                                <span className="text-sm text-blue-300">YZ Destekli Çözümler</span>
                            </div>
                            <h1 className="text-5xl md:text-7xl font-bold mb-6">
                                Dört Sinir Motoru.<br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                                    Tek Birleşik Platform.
                                </span>
                            </h1>
                            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                                Kapsamlı klinik karar desteği sunmak için uyum içinde çalışan
                                özelleşmiş YZ modellerinin gücünden yararlanın.
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
                        <span>Dashboard'u Deneyimle</span>
                        <span className="material-symbols-outlined">arrow_forward</span>
                    </Link>
                </section>
            </div>
        </div>
    );
}
