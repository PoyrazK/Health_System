import React, { useState } from 'react';
import { Check, X, Send } from 'lucide-react';

interface FeedbackPanelProps {
    assessmentId: number;
    risks: any;
}

export const FeedbackPanel: React.FC<FeedbackPanelProps> = ({ assessmentId, risks }) => {
    const [approved, setApproved] = useState<boolean | null>(null);
    const [notes, setNotes] = useState("");
    const [submitted, setSubmitted] = useState(false);

    const submitFeedback = async () => {
        try {
            await fetch("http://localhost:3000/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    assessment_id: assessmentId,
                    approved: approved,
                    notes: notes,
                    risks: risks
                }),
            });
            setSubmitted(true);
        } catch (e) {
            console.error("Feedback submission failed", e);
        }
    };

    if (submitted) return (
        <div className="mt-6 py-4 flex flex-col items-center justify-center border-t border-white/5 animate-pulse">
            <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center mb-2">
                <Check className="w-4 h-4 text-emerald-500" />
            </div>
            <span className="text-emerald-500 text-[10px] font-black tracking-[0.2em] uppercase">
                Memory Synchronized
            </span>
        </div>
    );

    return (
        <div className="mt-6 pt-6 border-t border-white/5">
            <h4 className="text-[10px] font-bold text-slate-500 uppercase mb-4 tracking-widest flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-slate-600 rounded-full" /> Validation Terminal
            </h4>

            <div className="flex gap-3 mb-4">
                <button
                    onClick={(e) => { e.stopPropagation(); setApproved(true); }}
                    className={`flex-1 py-3 px-4 text-[10px] font-black uppercase tracking-wider rounded-xl border transition-all duration-300 flex items-center justify-center gap-2
            ${approved === true
                            ? 'bg-emerald-500/20 border-emerald-500 text-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                            : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10 hover:text-white'
                        }`}
                >
                    <Check className="w-3 h-3" /> Approve
                </button>
                <button
                    onClick={(e) => { e.stopPropagation(); setApproved(false); }}
                    className={`flex-1 py-3 px-4 text-[10px] font-black uppercase tracking-wider rounded-xl border transition-all duration-300 flex items-center justify-center gap-2
            ${approved === false
                            ? 'bg-red-500/20 border-red-500 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.2)]'
                            : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10 hover:text-white'
                        }`}
                >
                    <X className="w-3 h-3" /> Correct
                </button>
            </div>

            <textarea
                placeholder="Enter clinical observations or correction details..."
                className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-4 text-[11px] text-slate-300 focus:outline-none focus:border-blue-500/50 focus:bg-white/[0.05] h-20 resize-none transition-all placeholder:text-slate-600"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                onClick={(e) => e.stopPropagation()}
            />

            <button
                onClick={(e) => { e.stopPropagation(); submitFeedback(); }}
                className="w-full mt-4 py-3 bg-blue-600 text-white text-[10px] font-black rounded-xl hover:bg-blue-500 transition-all uppercase tracking-[0.2em] shadow-lg shadow-blue-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                disabled={approved === null}
            >
                <Send className="w-3 h-3" /> Commit to Memory
            </button>
        </div>
    );
};
