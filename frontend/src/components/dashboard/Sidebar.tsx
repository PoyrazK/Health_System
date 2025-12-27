'use client';

import { Patient } from '@/lib/types';

interface SidebarProps {
    patients: Patient[];
    selectedId: string;
    onSelect: (p: Patient) => void;
    onNew: () => void;
}

export default function Sidebar({ patients, selectedId, onSelect, onNew }: SidebarProps) {
    return (
        <aside className="w-64 border-r border-white/5 flex flex-col bg-[#080a0f]">
            {/* Logo */}
            <div className="h-14 px-4 flex items-center justify-between border-b border-white/5">
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-lg bg-blue-500 flex items-center justify-center">
                        <span className="text-[10px] font-black text-white">R5</span>
                    </div>
                    <span className="text-sm font-semibold text-white">RedFive</span>
                </div>
                <button
                    onClick={onNew}
                    className="w-7 h-7 rounded-lg hover:bg-white/5 flex items-center justify-center text-slate-500 hover:text-white transition-colors"
                >
                    <span className="material-symbols-outlined text-[18px]">add</span>
                </button>
            </div>

            {/* Patient List */}
            <div className="flex-1 overflow-y-auto py-3 px-2">
                <div className="text-[9px] font-bold text-slate-600 uppercase tracking-widest px-2 mb-2">HASTA SIRASI</div>
                <div className="space-y-0.5">
                    {patients.map(patient => (
                        <button
                            key={patient.id}
                            onClick={() => onSelect(patient)}
                            className={`w-full text-left px-3 py-2.5 rounded-xl transition-all flex items-center gap-3 group ${selectedId === patient.id
                                ? 'bg-blue-500/10 border border-blue-500/20'
                                : 'hover:bg-white/5 border border-transparent'
                                }`}
                        >
                            {/* Status Indicator */}
                            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${patient.status === 'Critical'
                                ? 'bg-red-500 animate-pulse'
                                : patient.status === 'Observing'
                                    ? 'bg-yellow-500'
                                    : 'bg-emerald-500'
                                }`} />

                            {/* Patient Info */}
                            <div className="flex-1 min-w-0">
                                <div className={`text-sm font-medium truncate ${selectedId === patient.id ? 'text-white' : 'text-slate-300'
                                    }`}>
                                    {patient.name}
                                </div>
                                <div className="text-[10px] text-slate-500 flex items-center gap-1">
                                    <span>#{patient.id}</span>
                                    <span>•</span>
                                    <span>{patient.age} yaş</span>
                                </div>
                            </div>

                            {/* Arrow */}
                            <span className={`material-symbols-outlined text-[14px] transition-transform ${selectedId === patient.id
                                ? 'text-blue-400'
                                : 'text-slate-700 group-hover:text-slate-500 group-hover:translate-x-0.5'
                                }`}>
                                chevron_right
                            </span>
                        </button>
                    ))}
                </div>
            </div>

            {/* User Profile */}
            <div className="p-3 border-t border-white/5">
                <div className="flex items-center gap-2.5 px-2 py-2 rounded-xl hover:bg-white/5 transition-colors cursor-pointer">
                    <div
                        className="w-8 h-8 rounded-full bg-cover bg-center ring-2 ring-white/10"
                        style={{ backgroundImage: "url('https://picsum.photos/seed/doc/100/100')" }}
                    />
                    <div className="flex-1 min-w-0">
                        <div className="text-xs font-medium text-white truncate">Dr. Sara Yılmaz</div>
                        <div className="text-[9px] text-slate-500 uppercase tracking-wider">Uzman</div>
                    </div>
                    <span className="material-symbols-outlined text-slate-600 text-[16px]">expand_more</span>
                </div>
            </div>
        </aside>
    );
}
