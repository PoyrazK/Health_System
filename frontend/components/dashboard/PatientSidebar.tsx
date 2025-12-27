import React from 'react';
import { Patient } from "../../types";

interface PatientSidebarProps {
    patients: Patient[];
    selectedId: number | undefined;
    onSelect: (patient: Patient) => void;
}

export const PatientSidebar: React.FC<PatientSidebarProps> = ({
    patients,
    selectedId,
    onSelect
}) => {
    return (
        <div className="glass-card h-full rounded-2xl overflow-hidden flex flex-col border border-white/5 bg-white/[0.02]">
            <div className="p-5 border-b border-white/5 shrink-0 bg-white/[0.02]">
                <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-1">
                    Live Queue
                </h3>
                <p className="text-[10px] text-slate-400 italic">
                    Clinical Node Active
                </p>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {patients.map((p) => {
                    const isSelected = selectedId === p.id;
                    const isCritical = p.systolic_bp > 160;

                    return (
                        <button
                            key={p.id}
                            onClick={() => onSelect(p)}
                            className={`
                w-full p-4 border-b border-white/5 text-left transition-all duration-200
                hover:bg-white/5
                ${isSelected
                                    ? 'bg-blue-600/10 border-l-4 border-l-blue-500 pl-[12px]'
                                    : 'border-l-4 border-l-transparent pl-4'
                                }
              `}
                        >
                            <div className="flex justify-between items-start mb-1 overflow-hidden">
                                <span className={`text-[10px] font-black uppercase tracking-tighter truncate ${isSelected ? 'text-white' : 'text-slate-400'}`}>
                                    Case {p.id.toString().padStart(4, '0')}
                                </span>

                                <span className={`text-[8px] font-black px-1.5 py-0.5 rounded ml-2 uppercase tracking-tight
                  ${isCritical
                                        ? 'bg-red-500/20 text-red-500 animate-pulse'
                                        : 'bg-emerald-500/20 text-emerald-500'
                                    }
                `}>
                                    {isCritical ? 'CRITICAL' : 'STABLE'}
                                </span>
                            </div>

                            <div className="flex items-center gap-2 text-[9px] text-slate-500 font-medium">
                                <span>{p.age}y</span>
                                <span className="w-0.5 h-0.5 bg-slate-700 rounded-full" />
                                <span>{p.gender}</span>
                                <span className="w-0.5 h-0.5 bg-slate-700 rounded-full" />
                                <span className={p.systolic_bp > 140 ? 'text-amber-500' : ''}>BP {p.systolic_bp}</span>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};
