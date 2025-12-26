import React from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { Dna, Activity } from 'lucide-react';

interface DiagnosisPanelProps {
    diagnosis: string;
    status: string; // "pending", "ready", "error"
    loading: boolean;
}

export const DiagnosisPanel: React.FC<DiagnosisPanelProps> = ({ diagnosis, status, loading }) => {
    return (
        <div className="glass-card flex-1 rounded-[3rem] p-8 md:p-10 relative overflow-hidden bg-gradient-to-br from-black to-blue-950/20 border border-white/5 shadow-inner flex flex-col min-h-[400px]">
            {/* Header */}
            <div className="flex justify-between items-center mb-8 relative z-10 shrink-0">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center ring-1 ring-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
                        <Dna className="w-5 h-5 text-blue-500 animate-[pulse_3s_infinite]" />
                    </div>
                    <div>
                        <h2 className="text-[11px] font-black tracking-[0.3em] text-white uppercase italic">
                            Neural Differential Assessment
                        </h2>
                        <div className="flex items-center gap-2 mt-0.5">
                            <Activity className="w-3 h-3 text-slate-500" />
                            <p className="text-[8px] text-slate-500 font-bold uppercase tracking-widest">
                                Gemini 1.5 Flash Engine Active
                            </p>
                        </div>

                    </div>
                </div>

                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/5 border border-emerald-500/10">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span className="text-[9px] font-black text-emerald-500/90 tracking-widest uppercase">
                        System_Live
                    </span>
                </div>
            </div>

            {/* Content Area */}
            <div className="relative flex-1 min-h-0">
                <AnimatePresence>
                    {loading && (
                        <motion.div
                            key="loader-overlay"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="absolute inset-0 z-20 bg-black/60 backdrop-blur-sm rounded-2xl flex flex-col items-center justify-center gap-6 border border-white/5"
                        >
                            <div className="relative">
                                <div className="w-16 h-16 border-[4px] border-blue-500/10 rounded-full" />
                                <div className="w-16 h-16 border-[4px] border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0 shadow-[0_0_30px_rgba(59,130,246,0.4)]" />
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] font-black text-blue-500 tracking-[0.5em] uppercase animate-pulse">
                                    Analyzing Case Architecture...
                                </p>
                                <div className="flex items-center justify-center gap-1 mt-2">
                                    <span className="w-1 h-1 bg-slate-600 rounded-full animate-bounce delay-75" />
                                    <span className="w-1 h-1 bg-slate-600 rounded-full animate-bounce delay-150" />
                                    <span className="w-1 h-1 bg-slate-600 rounded-full animate-bounce delay-300" />
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="h-full overflow-y-auto custom-scrollbar pr-4 pb-12 selection:bg-blue-600/50">
                    <motion.div
                        animate={{
                            opacity: loading ? 0.3 : 1,
                            filter: loading ? 'blur(4px)' : 'blur(0px)',
                            scale: loading ? 0.98 : 1
                        }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                        className="prose prose-invert prose-sm max-w-none text-slate-300 leading-loose"
                    >
                        {status === "pending" ? (
                            <div className="flex flex-col items-center justify-center h-48 gap-4 opacity-50">
                                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                                <span className="text-[10px] font-bold uppercase tracking-widest text-blue-400 animate-pulse">
                                    Neural synthesis in progress...
                                </span>
                            </div>
                        ) : (
                            <ReactMarkdown
                                components={{
                                    h1: ({ node, ...props }) => <h1 className="text-xl font-black text-white uppercase tracking-wider mb-4 border-b border-white/10 pb-2" {...props} />,
                                    h2: ({ node, ...props }) => <h2 className="text-lg font-bold text-blue-400 mt-6 mb-3" {...props} />,
                                    h3: ({ node, ...props }) => <h3 className="text-base font-semibold text-emerald-400 mt-4 mb-2" {...props} />,
                                    strong: ({ node, ...props }) => <strong className="text-white font-bold" {...props} />,
                                    ul: ({ node, ...props }) => <ul className="list-disc pl-4 space-y-2 marker:text-blue-500/50" {...props} />,
                                    li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                                    blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-blue-500/30 pl-4 py-1 italic text-slate-400 bg-blue-900/10 rounded-r-lg my-4" {...props} />,
                                }}
                            >
                                {diagnosis || "Wait for analysis..."}
                            </ReactMarkdown>
                        )}
                    </motion.div>
                </div>
            </div>
        </div>
    );
};
