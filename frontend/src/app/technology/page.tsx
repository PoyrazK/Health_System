'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import dynamic from 'next/dynamic';

const GradientBlinds = dynamic(() => import('@/components/GradientBlinds'), { ssr: false });

export default function TechnologyPage() {
    const techStack = [
        { name: 'XGBoost', desc: 'Kardiyak Risk Tahmini', color: 'from-red-500 to-orange-500' },
        { name: 'LSTM', desc: 'Zaman Serisi Analizi', color: 'from-blue-500 to-cyan-500' },
        { name: 'CNN', desc: 'Tıbbi Görüntüleme', color: 'from-purple-500 to-pink-500' },
        { name: 'GPT-4', desc: 'Klinik Akıl Yürütme', color: 'from-emerald-500 to-teal-500' }
    ];

    const features = [
        {
            title: 'Çoklu Model Mimarisi',
            desc: 'Her biri belirli klinik alanlar için optimize edilmiş, paralel çalışan dört özelleşmiş sinir ağı.',
            icon: 'hub'
        },
        {
            title: 'Gerçek Zamanlı Çıkarım',
            desc: 'Optimize edilmiş çıkarım hatları ile veri girişinden klinik önerilere 120ms altı gecikme.',
            icon: 'speed'
        },
        {
            title: 'HIPAA Uyumlu',
            desc: 'Sağlık düzenlemelerini karşılayan uçtan uca şifreleme, denetim günlüğü ve rol tabanlı erişim kontrolü.',
            icon: 'security'
        },
        {
            title: 'Sürekli Öğrenme',
            desc: 'Modeller, hasta gizliliğini koruyarak anonimleştirilmiş geri bildirimle zamanla gelişir.',
            icon: 'model_training'
        }
    ];

    return (
        <div className="relative min-h-screen bg-[#0A0F1C] text-white">
            {/* Background */}
            <div className="fixed inset-0 z-0 opacity-50">
                <GradientBlinds
                    gradientColors={['#0A0F1C', '#581C87', '#7C3AED', '#0A0F1C']}
                    angle={60}
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
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 mb-6">
                                <span className="material-symbols-outlined text-purple-400">memory</span>
                                <span className="text-sm text-purple-300">Kaputun Altında</span>
                            </div>
                            <h1 className="text-5xl md:text-7xl font-bold mb-6">
                                Üzerine İnşa Edildi<br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                                    Son Teknoloji YZ.
                                </span>
                            </h1>
                            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                                Titiz doğrulama ile binlerce klinik vakada eğitilmiş
                                sofistike bir makine öğrenmesi modelleri topluluğu.
                            </p>
                        </motion.div>
                    </div>
                </section>

                {/* Tech Stack Grid */}
                <section className="py-16 px-6">
                    <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
                        {techStack.map((tech, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, scale: 0.9 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="text-center p-6 rounded-2xl bg-white/[0.03] border border-white/10"
                            >
                                <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${tech.color} flex items-center justify-center shadow-lg`}>
                                    <span className="text-white text-xl font-bold">{tech.name.slice(0, 2)}</span>
                                </div>
                                <h3 className="text-lg font-bold text-white mb-1">{tech.name}</h3>
                                <p className="text-xs text-slate-500">{tech.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* Features */}
                <section className="py-16 px-6">
                    <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-6">
                        {features.map((feature, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="flex gap-4 p-6 rounded-2xl bg-white/[0.02] border border-white/5"
                            >
                                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center flex-shrink-0">
                                    <span className="material-symbols-outlined text-purple-400">{feature.icon}</span>
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white mb-1">{feature.title}</h3>
                                    <p className="text-sm text-slate-400">{feature.desc}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* Architecture Diagram Placeholder */}
                <section className="py-16 px-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="rounded-3xl bg-gradient-to-br from-white/[0.05] to-white/[0.02] border border-white/10 p-8">
                            <h2 className="text-2xl font-bold text-white mb-6 text-center">Sistem Mimarisi</h2>
                            <div className="flex flex-wrap justify-center items-center gap-4">
                                {['Hasta Verisi', 'API Ağ Geçidi', 'ML Topluluğu', 'Risk Motoru', 'Klinik Çıktı'].map((node, i) => (
                                    <div key={i} className="flex items-center gap-3">
                                        <div className="px-4 py-2 rounded-xl bg-white/10 text-sm text-white font-medium">
                                            {node}
                                        </div>
                                        {i < 4 && <span className="material-symbols-outlined text-slate-600">arrow_forward</span>}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* CTA */}
                <section className="py-20 px-6 text-center">
                    <Link
                        href="/#dashboard"
                        className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-[#0A0F1C] font-semibold hover:bg-slate-100 transition-colors"
                    >
                        <span>Çalışırken Gör</span>
                        <span className="material-symbols-outlined">arrow_forward</span>
                    </Link>
                </section>
            </div>
        </div>
    );
}
