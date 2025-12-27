'use client';

import { useState } from 'react';

interface AuditBadgeProps {
    hash?: string;
}

export default function AuditBadge({ hash }: AuditBadgeProps) {
    const [copied, setCopied] = useState(false);

    if (!hash) {
        return null;
    }

    const truncatedHash = `${hash.slice(0, 8)}...${hash.slice(-6)}`;

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(hash);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    return (
        <div className="relative group">
            <button
                onClick={handleCopy}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20 transition-all"
            >
                <span className="material-symbols-outlined text-emerald-400 text-[14px]">verified</span>
                <code className="text-[11px] text-emerald-400 font-mono">{truncatedHash}</code>
                <span className="material-symbols-outlined text-slate-500 text-[14px] group-hover:text-emerald-400 transition-colors">
                    {copied ? 'check' : 'content_copy'}
                </span>
            </button>

            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-800 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                <p className="text-[10px] text-slate-400 mb-1">Audit Trail Hash</p>
                <code className="text-xs text-emerald-400 font-mono break-all block max-w-[300px]">{hash}</code>
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-slate-800" />
            </div>
        </div>
    );
}
