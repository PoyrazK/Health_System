'use client';

import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';
import Link from 'next/link';

// Dynamically import GradientBlinds to avoid SSR issues
const GradientBlinds = dynamic(() => import('./GradientBlinds'), { ssr: false });
const MetallicText = dynamic(() => import('./MetallicText'), { ssr: false });

interface LandingPageProps {
    onLaunch: () => void;
}

export default function LandingPage({ onLaunch }: LandingPageProps) {
    return (
        <div className="relative w-full min-h-screen bg-[#0A0F1C]">
            {/* GradientBlinds Background */}
            <div className="fixed inset-0 z-0">
                <GradientBlinds
                    gradientColors={['#0A0F1C', '#1E3A8A', '#3B82F6', '#06B6D4', '#0A0F1C']}
                    angle={45}
                    noise={0.15}
                    blindCount={12}
                    blindMinWidth={80}
                    mouseDampening={0.2}
                    mirrorGradient={true}
                    spotlightRadius={0.6}
                    spotlightSoftness={1.5}
                    spotlightOpacity={0.8}
                    distortAmount={0.5}
                    shineDirection="right"
                    className="w-full h-full"
                />
            </div>

            {/* Main Content Container */}
            <div className="relative z-10">

                {/* Floating Apple-Style Navigation */}
                <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
                    <div
                        className="flex items-center gap-1 px-2 py-1.5 rounded-full"
                        style={{
                            background: 'linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%)',
                            backdropFilter: 'blur(20px)',
                            WebkitBackdropFilter: 'blur(20px)',
                            boxShadow: '0 4px 30px rgba(0,0,0,0.3), inset 0 1px 1px rgba(255,255,255,0.1)',
                            border: '1px solid rgba(255,255,255,0.1)'
                        }}
                    >
                        {/* Logo */}
                        <div className="flex items-center gap-2 px-3 py-1.5">
                            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                                <span className="material-symbols-outlined text-white text-[14px]">ecg_heart</span>
                            </div>
                            <span className="text-sm font-semibold text-white/90 hidden sm:block">RedFive</span>
                        </div>

                        {/* Divider */}
                        <div className="w-px h-5 bg-white/10 hidden md:block" />

                        {/* Nav Links */}
                        <div className="hidden md:flex items-center">
                            {[
                                { name: 'Çözümler', href: '/solutions' },
                                { name: 'İş Akışı', href: '/workflow' },
                                { name: 'Teknoloji', href: '/technology' },
                            ].map((item, i) => (
                                <Link
                                    key={i}
                                    href={item.href}
                                    prefetch={true}
                                    className="px-3 py-1.5 text-[13px] text-white/60 hover:text-white hover:bg-white/10 rounded-full transition-all"
                                >
                                    {item.name}
                                </Link>
                            ))}
                        </div>

                        {/* Divider */}
                        <div className="w-px h-5 bg-white/10" />

                        {/* CTA Button */}
                        <button
                            onClick={onLaunch}
                            className="px-4 py-1.5 text-[13px] font-medium text-[#0A0F1C] bg-white rounded-full hover:bg-white/90 transition-all shadow-lg"
                        >
                            Başla
                        </button>
                    </div>
                </nav>

                {/* Hero Section */}
                <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 px-6 z-10">

                    <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
                        <motion.div
                            initial={{ opacity: 0, x: -30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.8 }}
                            className="flex flex-col gap-8"
                        >
                            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-blue-400 backdrop-blur-sm w-fit">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-400"></span>
                                </span>
                                YZ Destekli Klinik Karar Desteği
                            </div>
                            <h1 className="font-quiet text-5xl lg:text-7xl font-bold tracking-tight text-white leading-[1.1]">
                                Klinik Kararların <br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#3B82F6] to-blue-300">Geleceği</span>
                            </h1>
                            <p className="text-lg text-slate-400 leading-relaxed max-w-xl">
                                Dağınık geçmişten klinik netleğe. Çoklu model sinir motorumuz, binlerce vital ve geçmiş veriyi analiz ederek hasta riskini gerçek zamanlı öngörür.
                            </p>
                            <div className="flex flex-wrap gap-4">
                                <button
                                    onClick={onLaunch}
                                    className="h-12 px-8 rounded-full bg-[#3B82F6] hover:bg-blue-600 text-white font-semibold transition-all shadow-[0_0_25px_rgba(59,130,246,0.3)] flex items-center gap-2 group"
                                >
                                    Demo Talep Et
                                    <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                                </button>
                                <button className="h-12 px-6 rounded-full bg-transparent border border-white/20 hover:border-white/40 text-white font-medium transition-all flex items-center gap-2">
                                    <span className="material-symbols-outlined text-[20px]">play_circle</span>
                                    Videoyu İzle
                                </button>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ duration: 1, delay: 0.2 }}
                            className="relative hidden lg:block"
                        >
                            {/* Liquid Glass Dashboard Preview */}
                            <div className="relative">
                                {/* Outer glow */}
                                <div className="absolute -inset-1 bg-gradient-to-br from-white/20 via-white/5 to-transparent rounded-[28px] blur-sm" />

                                {/* Main container with liquid glass effect */}
                                <div
                                    className="relative rounded-[24px] p-[1px] overflow-hidden"
                                    style={{
                                        background: 'linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.15) 100%)'
                                    }}
                                >
                                    {/* Inner frosted glass */}
                                    <div
                                        className="rounded-[23px] p-5 relative overflow-hidden"
                                        style={{
                                            background: 'linear-gradient(135deg, rgba(20,25,40,0.95) 0%, rgba(10,15,28,0.98) 100%)',
                                            boxShadow: 'inset 0 1px 1px rgba(255,255,255,0.1), 0 20px 50px -10px rgba(0,0,0,0.5)'
                                        }}
                                    >
                                        {/* Shine reflection */}
                                        <div
                                            className="absolute top-0 left-0 right-0 h-1/2 pointer-events-none"
                                            style={{
                                                background: 'linear-gradient(180deg, rgba(255,255,255,0.08) 0%, transparent 100%)'
                                            }}
                                        />

                                        <div className="relative space-y-4">
                                            {/* Window controls with subtle glow */}
                                            <div className="flex items-center justify-between pb-3 border-b border-white/5">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-3 h-3 rounded-full bg-[#FF5F57] shadow-[0_0_8px_rgba(255,95,87,0.5)]" />
                                                    <div className="w-3 h-3 rounded-full bg-[#FEBC2E] shadow-[0_0_8px_rgba(254,188,46,0.5)]" />
                                                    <div className="w-3 h-3 rounded-full bg-[#28C840] shadow-[0_0_8px_rgba(40,200,64,0.5)]" />
                                                </div>
                                                <span className="text-[10px] text-white/40 font-light tracking-wide">RedFive</span>
                                            </div>

                                            {/* Dashboard content */}
                                            <div className="grid grid-cols-3 gap-3">
                                                {/* Sidebar - Frosted pills */}
                                                <div className="space-y-2">
                                                    {['John Doe', 'Jane Miller', 'Elias T.'].map((name, i) => (
                                                        <div
                                                            key={i}
                                                            className={`p-2.5 rounded-xl transition-all ${i === 0
                                                                ? 'bg-white/10 ring-1 ring-white/20'
                                                                : 'bg-white/[0.03] hover:bg-white/[0.06]'
                                                                }`}
                                                        >
                                                            <div className="text-[11px] font-medium text-white/90">{name}</div>
                                                            <div className="text-[9px] text-white/30 mt-0.5 font-light">Hasta ID: {1000 + i * 111}</div>
                                                        </div>
                                                    ))}
                                                </div>

                                                {/* Main content */}
                                                <div className="col-span-2 space-y-3">
                                                    {/* Vitals - Frosted cards */}
                                                    <div className="grid grid-cols-2 gap-2">
                                                        {[
                                                            { label: 'Nabız', value: '82', unit: 'BPM', color: '#FF6B6B' },
                                                            { label: 'Tansiyon', value: '142/91', unit: 'mmHg', color: '#4DABF7' },
                                                            { label: 'Glikoz', value: '110', unit: 'mg/dL', color: '#FFD43B' },
                                                            { label: 'SpO2', value: '98', unit: '%', color: '#69DB7C' },
                                                        ].map((v, i) => (
                                                            <div
                                                                key={i}
                                                                className="bg-white/[0.04] rounded-xl p-2.5 border border-white/[0.05]"
                                                            >
                                                                <div className="text-[8px] text-white/40 uppercase tracking-wider font-light">{v.label}</div>
                                                                <div className="flex items-baseline gap-1 mt-1">
                                                                    <span className="text-base font-semibold" style={{ color: v.color }}>{v.value}</span>
                                                                    <span className="text-[8px] text-white/30">{v.unit}</span>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>

                                                    {/* Risk bars with liquid styling */}
                                                    <div className="bg-white/[0.03] rounded-xl p-3 border border-white/[0.05]">
                                                        <div className="text-[8px] text-white/40 uppercase tracking-wider mb-2 font-light">Risk Analizi</div>
                                                        <div className="space-y-2">
                                                            {[
                                                                { label: 'Kardiyak', pct: 65, color: 'from-red-500 to-orange-400' },
                                                                { label: 'Metabolik', pct: 42, color: 'from-blue-500 to-cyan-400' },
                                                                { label: 'Nöro', pct: 18, color: 'from-purple-500 to-pink-400' },
                                                            ].map((r, i) => (
                                                                <div key={i} className="flex items-center gap-2">
                                                                    <span className="text-[8px] text-white/40 w-12 font-light">{r.label}</span>
                                                                    <div className="flex-1 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                                                                        <div
                                                                            className={`h-full bg-gradient-to-r ${r.color} rounded-full`}
                                                                            style={{ width: `${r.pct}%` }}
                                                                        />
                                                                    </div>
                                                                    <span className="text-[9px] text-white/50 w-6 text-right font-medium">{r.pct}%</span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>

                                                    {/* AI Card - Premium frosted */}
                                                    <div
                                                        className="rounded-xl p-3 border border-white/[0.08]"
                                                        style={{
                                                            background: 'linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(139,92,246,0.05) 100%)'
                                                        }}
                                                    >
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                                                                <span className="material-symbols-outlined text-white text-[10px]">psychology</span>
                                                            </div>
                                                            <span className="text-[9px] font-medium text-white/70 tracking-wide">NÖRAL DEĞERLENDİRME</span>
                                                        </div>
                                                        <div className="text-[10px] text-white/60 font-light leading-relaxed">
                                                            Ön Tanı: <span className="text-white font-medium">Bakteriyel Pnömoni</span>
                                                            <span className="ml-2 text-emerald-400 font-medium">99.8%</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Bottom ambient glow */}
                                        <div className="absolute -bottom-16 -right-16 w-32 h-32 bg-blue-500/20 rounded-full blur-3xl" />
                                        <div className="absolute -bottom-16 -left-16 w-24 h-24 bg-purple-500/10 rounded-full blur-3xl" />
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </section>

                {/* Problem / Solution Section */}
                <section id="solutions" className="py-24 px-6 border-t border-white/5 bg-[#0f1118]/80 backdrop-blur-sm">
                    <div className="max-w-7xl mx-auto">
                        <div className="grid lg:grid-cols-2 gap-20 items-center">
                            <div className="space-y-6">
                                <h2 className="text-blue-500 font-bold tracking-widest uppercase text-xs">Sorun</h2>
                                <h3 className="text-3xl md:text-5xl font-bold text-white tracking-tight">Sağlık Verileri Bunaltıcı</h3>
                                <p className="text-slate-400 leading-relaxed text-lg">
                                    Bugün klinisyenler bilişsel bir darboğazla karşı karşıya. Parçalanmış geçmişler, binlerce gerçek zamanlı vital ve karmaşık ilaç etkileşimleri manuel analizi erken uyarıları kaçırmaya açık hale getiriyor.
                                </p>
                            </div>
                            <div className="space-y-6">
                                <h2 className="text-emerald-500 font-bold tracking-widest uppercase text-xs">Çözüm</h2>
                                <h3 className="text-3xl md:text-5xl font-bold text-white tracking-tight">YZ Destekli Netlik</h3>
                                <p className="text-slate-400 leading-relaxed text-lg">
                                    RedFive ham klinik verileri eyleme dönüştürülebilir zekaya sentezler. Klinisyenlerin yerine geçmiyoruz; onlara hiçbir detayı kaçırmayan 7/24 süper-işlemci sağlıyoruz.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Metrics Section */}
                <section className="py-24 px-6 bg-[#0A0F1C]/60">
                    <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
                        {[
                            { label: 'Eğitilmiş ML Modeli', value: '4' },
                            { label: 'Klinik Güven', value: '99.8%' },
                            { label: 'Uçtan Uca Gecikme', value: '<120ms' },
                            { label: 'Geçmiş Vaka', value: '1000+' },
                        ].map((m, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="text-center"
                            >
                                <div className="text-4xl md:text-6xl font-extrabold text-white mb-2">{m.value}</div>
                                <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">{m.label}</div>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* Metallic Logo Section */}
                <section className="py-16 px-6 flex justify-center items-center bg-gradient-to-b from-transparent to-[#0A0F1C]/50">
                    <div className="w-full max-w-3xl h-[300px]">
                        <MetallicText
                            text="REDFIVE"
                            fontSize={180}
                            className="w-full h-full"
                        />
                    </div>
                </section>

                {/* Footer */}
                <footer className="py-12 border-t border-white/5 bg-[#0A0F1C]/80 backdrop-blur-sm px-6">
                    <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 text-sm text-slate-500">
                        <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500 text-white">
                                <span className="material-symbols-outlined text-[20px]">medical_services</span>
                            </div>
                            <span className="text-lg font-bold text-white">RedFive</span>
                        </div>
                        <div>Sağlık için ❤️ ile yapıldı © 2024</div>
                    </div>
                </footer>
            </div >
        </div >
    );
}

