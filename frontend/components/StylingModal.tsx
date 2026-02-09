"use client";

import { X, Check, Type } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface StylingModalProps {
    isOpen: boolean;
    onClose: () => void;
    onApply: (payload: { caption: string; position: 'top' | 'center' | 'bottom' }) => void;
    initialCaption?: string;
    initialPosition?: 'top' | 'center' | 'bottom';
}
const POSITIONS = ['top', 'center', 'bottom'] as const;

export default function StylingModal({ isOpen, onClose, onApply, initialCaption, initialPosition }: StylingModalProps) {
    const [caption, setCaption] = useState("");
    const [position, setPosition] = useState<(typeof POSITIONS)[number]>("center");

    useEffect(() => {
        if (!isOpen) return;
        if (typeof initialCaption === "string") setCaption(initialCaption);
        if (initialPosition) setPosition(initialPosition);
    }, [isOpen, initialCaption, initialPosition]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-6 sm:p-12">
            <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />

            <div className="relative w-full max-w-2xl bg-[#0d1017] border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="p-8 border-b border-white/5 flex items-center justify-between bg-black/20">
                    <div className="flex items-center gap-4">
                        <div className="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
                            <Type className="h-5 w-5" />
                        </div>
                        <div>
                            <h2 className="text-sm font-black text-white uppercase tracking-[0.3em]">Apply Visual Style</h2>
                            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-0.5">Post-Production Effects</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="h-10 w-10 rounded-xl hover:bg-white/5 flex items-center justify-center text-slate-500 transition-colors">
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
                    <section className="space-y-4">
                        <div className="flex items-center gap-3">
                            <Type className="h-4 w-4 text-indigo-500" />
                            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Text Overlay</h3>
                        </div>
                        <div className="space-y-2">
                            <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Caption</p>
                            <div className="flex gap-2">
                                <input
                                    value={caption}
                                    onChange={(e) => setCaption(e.target.value)}
                                    placeholder='Type overlay text (e.g. "Oh, to be this young again.")'
                                    className="flex-1 h-12 px-4 rounded-xl bg-white/[0.02] border border-white/5 text-[11px] text-slate-200 placeholder:text-slate-600 outline-none focus:border-indigo-500/30 focus:bg-white/[0.04] transition-all"
                                />
                                <button
                                    onClick={() => setCaption("")}
                                    className="h-12 px-4 rounded-xl bg-white/5 border border-white/10 text-[9px] font-black text-slate-400 uppercase tracking-widest hover:bg-white/10 transition-all"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Placement</p>
                            <div className="flex gap-2">
                                {POSITIONS.map(p => (
                                    <button
                                        key={p}
                                        onClick={() => setPosition(p)}
                                        className={cn(
                                            "flex-1 py-2 rounded-lg border text-[9px] font-black uppercase tracking-widest transition-all",
                                            position === p
                                                ? "bg-indigo-600/10 border-indigo-500/30 text-white"
                                                : "bg-white/[0.02] border-white/5 text-slate-500 hover:bg-white/[0.04]"
                                        )}
                                    >
                                        {p}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </section>
                </div>

                {/* Footer */}
                <div className="p-8 border-t border-white/5 bg-black/20 flex gap-4">
                    <button
                        onClick={onClose}
                        className="flex-1 h-14 rounded-2xl bg-white/5 border border-white/10 text-[10px] font-black text-slate-400 uppercase tracking-widest hover:bg-white/10 transition-all"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={() => {
                            setCaption("");
                            setPosition("center");
                        }}
                        className="flex-1 h-14 rounded-2xl bg-white/5 border border-white/10 text-[10px] font-black text-slate-400 uppercase tracking-widest hover:bg-white/10 transition-all"
                    >
                        Reset
                    </button>
                    <button
                        onClick={() => onApply({ caption, position })}
                        className="flex-[1.5] h-14 rounded-2xl bg-indigo-600 text-[10px] font-black text-white uppercase tracking-widest hover:bg-indigo-500 transition-all shadow-xl shadow-indigo-600/20"
                    >
                        Update Visual Path
                    </button>
                </div>
            </div>
        </div>
    );
}
