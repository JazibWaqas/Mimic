"use client";

import { X, Check, Palette, Type, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import type { StyleConfig } from "@/lib/types";

interface StylingModalProps {
    isOpen: boolean;
    onClose: () => void;
    onApply: (payload: { config: StyleConfig; caption: string }) => void;
    initialConfig?: StyleConfig;
    initialCaption?: string;
}

const COLOR_PRESETS = [
    { id: 'neutral', name: 'Neutral', bg: 'bg-slate-500' },
    { id: 'warm', name: 'Golden Hour', bg: 'bg-orange-500' },
    { id: 'cool', name: 'Cyber Blue', bg: 'bg-cyan-500' },
    { id: 'high_contrast', name: 'Noir/Bold', bg: 'bg-indigo-600' },
    { id: 'vintage', name: 'Retro Film', bg: 'bg-amber-700' },
] as const;

const FONTS = ['Inter', 'Outfit', 'serif', 'sans-serif', 'mono'];
const POSITIONS = ['top', 'center', 'bottom'] as const;

export default function StylingModal({ isOpen, onClose, onApply, initialConfig, initialCaption }: StylingModalProps) {
    const [config, setConfig] = useState<StyleConfig>(initialConfig || {
        text: { font: 'Inter', weight: 600, color: '#FFFFFF', shadow: true, position: 'bottom', animation: 'fade' },
        color: { preset: 'neutral' },
        texture: { grain: false }
    });

    const [caption, setCaption] = useState("");

    useEffect(() => {
        if (!isOpen) return;
        if (initialConfig) setConfig(initialConfig);
        if (typeof initialCaption === "string") setCaption(initialCaption);
    }, [isOpen, initialConfig, initialCaption]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-6 sm:p-12">
            <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />

            <div className="relative w-full max-w-2xl bg-[#0d1017] border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="p-8 border-b border-white/5 flex items-center justify-between bg-black/20">
                    <div className="flex items-center gap-4">
                        <div className="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
                            <Palette className="h-5 w-5" />
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
                    {/* 0. Text Overlay */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-3">
                            <Type className="h-4 w-4 text-indigo-500" />
                            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Text Overlay</h3>
                        </div>
                        <div className="space-y-2">
                            <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Caption</p>
                            <input
                                value={caption}
                                onChange={(e) => setCaption(e.target.value)}
                                placeholder='Type overlay text (e.g. "Oh, to be this young again.")'
                                className="w-full h-12 px-4 rounded-xl bg-white/[0.02] border border-white/5 text-[11px] text-slate-200 placeholder:text-slate-600 outline-none focus:border-indigo-500/30 focus:bg-white/[0.04] transition-all"
                            />
                        </div>
                    </section>

                    {/* 1. Color Treatment */}
                    <section className="space-y-6">
                        <div className="flex items-center gap-3">
                            <Sparkles className="h-4 w-4 text-indigo-500" />
                            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Color Treatment</h3>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                            {COLOR_PRESETS.map((p) => (
                                <button
                                    key={p.id}
                                    onClick={() => setConfig(prev => ({ ...prev, color: { preset: p.id } }))}
                                    className={cn(
                                        "flex flex-col items-center gap-3 p-4 rounded-2xl border transition-all group",
                                        config.color.preset === p.id
                                            ? "bg-indigo-600/10 border-indigo-500/50 shadow-lg shadow-indigo-500/10"
                                            : "bg-white/[0.02] border-white/5 hover:border-white/10"
                                    )}
                                >
                                    <div className={cn("h-10 w-10 rounded-full shadow-inner", p.bg)} />
                                    <span className={cn(
                                        "text-[9px] font-black uppercase tracking-tighter truncate w-full text-center",
                                        config.color.preset === p.id ? "text-indigo-400" : "text-slate-500"
                                    )}>{p.name}</span>
                                    {config.color.preset === p.id && <Check className="h-3 w-3 text-indigo-500" />}
                                </button>
                            ))}
                        </div>
                    </section>

                    {/* 2. Typography */}
                    <section className="space-y-6">
                        <div className="flex items-center gap-3">
                            <Type className="h-4 w-4 text-indigo-500" />
                            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Typography</h3>
                        </div>

                        <div className="grid grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Font Family</p>
                                <div className="space-y-2">
                                    {FONTS.map(f => (
                                        <button
                                            key={f}
                                            onClick={() => setConfig(prev => ({ ...prev, text: { ...prev.text, font: f } }))}
                                            className={cn(
                                                "w-full text-left px-4 py-3 rounded-xl border text-[11px] font-medium transition-all",
                                                config.text.font === f
                                                    ? "bg-indigo-600/10 border-indigo-500/30 text-white"
                                                    : "bg-white/[0.02] border-white/5 text-slate-500 hover:bg-white/[0.04]"
                                            )}
                                            style={{ fontFamily: f }}
                                        >
                                            {f}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div className="space-y-4">
                                    <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Placement</p>
                                    <div className="flex gap-2">
                                        {POSITIONS.map(p => (
                                            <button
                                                key={p}
                                                onClick={() => setConfig(prev => ({ ...prev, text: { ...prev.text, position: p } }))}
                                                className={cn(
                                                    "flex-1 py-2 rounded-lg border text-[9px] font-black uppercase tracking-widest transition-all",
                                                    config.text.position === p
                                                        ? "bg-indigo-600/10 border-indigo-500/30 text-white"
                                                        : "bg-white/[0.02] border-white/5 text-slate-500 hover:bg-white/[0.04]"
                                                )}
                                            >
                                                {p}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Effects</p>
                                    <div className="flex flex-col gap-2">
                                        <button
                                            onClick={() => setConfig(prev => ({ ...prev, text: { ...prev.text, shadow: !prev.text.shadow } }))}
                                            className={cn(
                                                "px-4 py-3 rounded-xl border text-[10px] font-black uppercase tracking-widest flex items-center justify-between transition-all",
                                                config.text.shadow ? "bg-indigo-600/10 border-indigo-500/30 text-white" : "bg-white/[0.02] border-white/5 text-slate-600"
                                            )}
                                        >
                                            Drop Shadow
                                            {config.text.shadow && <Check className="h-3 w-3" />}
                                        </button>
                                        <button
                                            onClick={() => setConfig(prev => ({ ...prev, texture: { grain: !prev.texture.grain } }))}
                                            className={cn(
                                                "px-4 py-3 rounded-xl border text-[10px] font-black uppercase tracking-widest flex items-center justify-between transition-all",
                                                config.texture.grain ? "bg-indigo-600/10 border-indigo-500/30 text-white" : "bg-white/[0.02] border-white/5 text-slate-600"
                                            )}
                                        >
                                            Film Grain
                                            {config.texture.grain && <Check className="h-3 w-3" />}
                                        </button>
                                    </div>
                                </div>
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
                        onClick={() => onApply({ config, caption })}
                        className="flex-[1.5] h-14 rounded-2xl bg-indigo-600 text-[10px] font-black text-white uppercase tracking-widest hover:bg-indigo-500 transition-all shadow-xl shadow-indigo-600/20"
                    >
                        Update Visual Path
                    </button>
                </div>
            </div>
        </div>
    );
}
