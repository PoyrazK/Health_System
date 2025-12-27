"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";

interface DashboardSummary {
    total_patients: number;
    high_risk_patients: number;
    recent_assessments: number;
    system_health: "Healthy" | "Warning" | "Critical";
    ml_service_pulse: "Online" | "Offline";
    audit_chain_valid: boolean;
    risk_distribution: Record<string, number>;
    performance: {
        avg_ml_inference_time_ms: number;
        uptime_seconds: number;
        request_count: number;
        error_rate: number;
    };
}

export default function AdminDashboard() {
    const [data, setData] = useState<DashboardSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    const fetchDashboard = useCallback(async () => {
        try {
            const res = await fetch("http://localhost:3000/api/dashboard/summary");
            if (!res.ok) throw new Error("Failed to fetch");
            const json = await res.json();
            setData(json);
            setLastUpdate(new Date());
        } catch (err) {
            console.error("Dashboard fetch error:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDashboard();
        const interval = setInterval(fetchDashboard, 1000); // Poll every 1s for real-time
        return () => clearInterval(interval);
    }, [fetchDashboard]);

    const formatUptime = (seconds: number) => {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        return `${hrs}h ${mins}m ${secs}s`;
    };

    const getHealthColor = (health: string) => {
        switch (health) {
            case "Healthy": return "text-emerald-400";
            case "Warning": return "text-amber-400";
            case "Critical": return "text-red-400";
            default: return "text-gray-400";
        }
    };

    const getHealthBg = (health: string) => {
        switch (health) {
            case "Healthy": return "bg-emerald-500/20 border-emerald-500/30";
            case "Warning": return "bg-amber-500/20 border-amber-500/30";
            case "Critical": return "bg-red-500/20 border-red-500/30";
            default: return "bg-gray-500/20 border-gray-500/30";
        }
    };

    if (loading) {
        return (
            <main className="min-h-screen bg-[#050505] flex items-center justify-center">
                <div className="text-center">
                    <div className="relative mb-4">
                        <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full mx-auto" />
                        <div className="absolute inset-0 w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto" />
                    </div>
                    <p className="text-[10px] font-black text-cyan-500 tracking-[0.5em] uppercase animate-pulse">
                        Loading Dashboard...
                    </p>
                </div>
            </main>
        );
    }

    if (!data) {
        return (
            <main className="min-h-screen bg-[#050505] flex items-center justify-center">
                <div className="text-center text-red-400">
                    <p className="text-lg">Failed to load dashboard data</p>
                    <button
                        onClick={fetchDashboard}
                        className="mt-4 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-500 transition"
                    >
                        Retry
                    </button>
                </div>
            </main>
        );
    }

    const totalRisk = Object.values(data.risk_distribution).reduce((a, b) => a + b, 0);

    return (
        <main className="min-h-screen bg-[#050505] p-6">
            {/* Header */}
            <header className="mb-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-white">
                            Admin Dashboard
                            <span className="ml-3 text-sm font-normal text-cyan-400">Healthcare System</span>
                        </h1>
                        <p className="text-gray-500 text-sm mt-1">
                            Real-time system monitoring and analytics
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className={`px-4 py-2 rounded-full border ${getHealthBg(data.system_health)}`}>
                            <span className={`text-sm font-semibold ${getHealthColor(data.system_health)}`}>
                                ● {data.system_health}
                            </span>
                        </div>
                        {lastUpdate && (
                            <span className="text-xs text-gray-500">
                                Updated: {lastUpdate.toLocaleTimeString()}
                            </span>
                        )}
                    </div>
                </div>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-blue-900/40 to-blue-950/40 border border-blue-500/20 rounded-2xl p-6"
                >
                    <p className="text-blue-400 text-xs uppercase tracking-wider mb-2">Total Patients</p>
                    <p className="text-4xl font-bold text-white">{data.total_patients.toLocaleString()}</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-gradient-to-br from-red-900/40 to-red-950/40 border border-red-500/20 rounded-2xl p-6"
                >
                    <p className="text-red-400 text-xs uppercase tracking-wider mb-2">High Risk Patients</p>
                    <p className="text-4xl font-bold text-white">{data.high_risk_patients}</p>
                    <p className="text-xs text-red-300/60 mt-1">SystolicBP &gt; 160</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-gradient-to-br from-purple-900/40 to-purple-950/40 border border-purple-500/20 rounded-2xl p-6"
                >
                    <p className="text-purple-400 text-xs uppercase tracking-wider mb-2">Recent Assessments</p>
                    <p className="text-4xl font-bold text-white">{data.recent_assessments}</p>
                    <p className="text-xs text-purple-300/60 mt-1">Last 24 hours</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-gradient-to-br from-cyan-900/40 to-cyan-950/40 border border-cyan-500/20 rounded-2xl p-6"
                >
                    <p className="text-cyan-400 text-xs uppercase tracking-wider mb-2">Request Count</p>
                    <p className="text-4xl font-bold text-white">{data.performance.request_count.toLocaleString()}</p>
                    <p className="text-xs text-cyan-300/60 mt-1">Since startup</p>
                </motion.div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Risk Distribution */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 }}
                    className="lg:col-span-2 bg-[#0a0a0a] border border-gray-800 rounded-2xl p-6"
                >
                    <h2 className="text-lg font-semibold text-white mb-4">Risk Distribution</h2>
                    <div className="space-y-4">
                        {Object.entries(data.risk_distribution).map(([level, count]) => {
                            const percentage = totalRisk > 0 ? (count / totalRisk) * 100 : 0;
                            const colors: Record<string, string> = {
                                Low: "bg-emerald-500",
                                Medium: "bg-amber-500",
                                High: "bg-red-500",
                            };
                            return (
                                <div key={level}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400">{level}</span>
                                        <span className="text-white font-medium">{count} ({percentage.toFixed(1)}%)</span>
                                    </div>
                                    <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${percentage}%` }}
                                            transition={{ duration: 1, ease: "easeOut" }}
                                            className={`h-full ${colors[level] || "bg-gray-500"} rounded-full`}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </motion.div>

                {/* System Status */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 }}
                    className="bg-[#0a0a0a] border border-gray-800 rounded-2xl p-6"
                >
                    <h2 className="text-lg font-semibold text-white mb-4">System Status</h2>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                            <span className="text-gray-400">ML Service</span>
                            <span className={`font-semibold ${data.ml_service_pulse === "Online" ? "text-emerald-400" : "text-red-400"}`}>
                                ● {data.ml_service_pulse}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                            <span className="text-gray-400">Audit Chain</span>
                            <span className={`font-semibold ${data.audit_chain_valid ? "text-emerald-400" : "text-red-400"}`}>
                                {data.audit_chain_valid ? "✓ Valid" : "✗ Invalid"}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                            <span className="text-gray-400">Uptime</span>
                            <span className="text-white font-mono text-sm">{formatUptime(data.performance.uptime_seconds)}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                            <span className="text-gray-400">Error Rate</span>
                            <span className={`font-semibold ${data.performance.error_rate < 1 ? "text-emerald-400" : data.performance.error_rate < 5 ? "text-amber-400" : "text-red-400"}`}>
                                {data.performance.error_rate.toFixed(2)}%
                            </span>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Performance Metrics */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="mt-6 bg-[#0a0a0a] border border-gray-800 rounded-2xl p-6"
            >
                <h2 className="text-lg font-semibold text-white mb-4">Performance Metrics</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-gray-900/30 rounded-xl">
                        <p className="text-3xl font-bold text-cyan-400">{data.performance.avg_ml_inference_time_ms}ms</p>
                        <p className="text-xs text-gray-500 mt-1">Avg ML Latency</p>
                    </div>
                    <div className="text-center p-4 bg-gray-900/30 rounded-xl">
                        <p className="text-3xl font-bold text-blue-400">{formatUptime(data.performance.uptime_seconds)}</p>
                        <p className="text-xs text-gray-500 mt-1">Uptime</p>
                    </div>
                    <div className="text-center p-4 bg-gray-900/30 rounded-xl">
                        <p className="text-3xl font-bold text-purple-400">{data.performance.request_count}</p>
                        <p className="text-xs text-gray-500 mt-1">Total Requests</p>
                    </div>
                    <div className="text-center p-4 bg-gray-900/30 rounded-xl">
                        <p className="text-3xl font-bold text-emerald-400">{(100 - data.performance.error_rate).toFixed(1)}%</p>
                        <p className="text-xs text-gray-500 mt-1">Success Rate</p>
                    </div>
                </div>
            </motion.div>

            {/* Footer */}
            <footer className="mt-8 text-center text-gray-600 text-xs">
                <p>Healthcare Clinical Copilot | Admin Dashboard | Live Updates: 1s</p>
            </footer>
        </main>
    );
}
