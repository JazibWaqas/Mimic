"use client";

import { useRef } from "react";
import {
    Play,
    MessageSquare,
    ChevronDown
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { AssetItem } from "./page";

interface VaultBProps {
    slotA: AssetItem | null;
    slotB: AssetItem | null;
    videoRefA: React.RefObject<HTMLVideoElement | null>;
    videoRefB: React.RefObject<HTMLVideoElement | null>;
    getVideoUrl: (item: AssetItem) => string;
    syncEnabled: boolean;
    setSyncEnabled: (val: boolean) => void;
    setIsCabinetOpen: (val: boolean) => void;
    results: AssetItem[];
    references: AssetItem[];
    setSlotA: (item: AssetItem | null) => void;
    setSlotB: (item: AssetItem | null) => void;
}

export default function VaultB({
    slotA,
    slotB,
    videoRefA,
    videoRefB,
    getVideoUrl,
    syncEnabled,
    setSyncEnabled,
    setIsCabinetOpen,
    results,
    references,
    setSlotA,
    setSlotB
}: VaultBProps) {
    return (
        <div className="flex flex-col h-full">
            {/* Vertical Side-by-Side */}
            <div className="flex-1 grid grid-cols-2 gap-8 items-start justify-center max-w-[900px] mx-auto w-full pt-4">
                {/* Left: Output Selector + Video */}
                <div className="flex flex-col gap-3">
                    <div className="relative">
                        <select
                            value={slotA?.filename || ""}
                            onChange={(e) => {
                                const selected = results.find(r => r.filename === e.target.value);
                                setSlotA(selected || null);
                            }}
                            className="w-full bg-black/40 border border-cyan-500/30 rounded-xl px-4 py-2 text-[10px] font-black text-white uppercase tracking-widest appearance-none cursor-pointer hover:bg-black/60 transition-all"
                        >
                            <option value="">Select Output</option>
                            {results.map(res => (
                                <option key={res.filename} value={res.filename}>
                                    {res.filename}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyan-400 pointer-events-none" />
                    </div>

                    <div className="relative h-[90vh] w-[420px] max-w-[440px] mx-auto">
                        <div className={cn(
                            "absolute inset-0 rounded-[3rem] bg-black/40 border-2 shadow-2xl overflow-hidden transition-all duration-700",
                            slotA ? "border-cyan-500/40" : "border-white/5 border-dashed"
                        )}>
                            {slotA ? (
                                <>
                                    <div className="absolute top-6 left-6 z-20 flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full animate-pulse bg-cyan-400" />
                                        <span className="text-[9px] font-black text-white/50 uppercase tracking-[0.2em]">Output</span>
                                    </div>
                                    <video
                                        ref={videoRefA}
                                        src={getVideoUrl(slotA)}
                                        controls
                                        className="h-full w-full object-cover"
                                    />
                                </>
                            ) : (
                                <div className="w-full h-full flex flex-col items-center justify-center gap-2">
                                    <Play className="w-8 h-8 opacity-10" />
                                    <p className="text-[9px] font-black uppercase text-slate-700 tracking-widest">Select Output</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right: Reference Selector + Video */}
                <div className="flex flex-col gap-3">
                    <div className="relative">
                        <select
                            value={slotB?.filename || ""}
                            onChange={(e) => {
                                const selected = references.find(r => r.filename === e.target.value);
                                setSlotB(selected || null);
                            }}
                            className="w-full bg-black/40 border border-pink-500/30 rounded-xl px-4 py-2 text-[10px] font-black text-white uppercase tracking-widest appearance-none cursor-pointer hover:bg-black/60 transition-all"
                        >
                            <option value="">Select Reference</option>
                            {references.map(ref => (
                                <option key={ref.filename} value={ref.filename}>
                                    {ref.filename}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-pink-400 pointer-events-none" />
                    </div>

                    <div className="relative h-[90vh] w-[420px] max-w-[440px] mx-auto">
                        <div className={cn(
                            "absolute inset-0 rounded-[3rem] bg-black/40 border-2 shadow-2xl overflow-hidden transition-all duration-700",
                            slotB ? "border-pink-500/40" : "border-white/5 border-dashed"
                        )}>
                            {slotB ? (
                                <>
                                    <div className="absolute top-6 left-6 z-20 flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full animate-pulse bg-pink-400" />
                                        <span className="text-[9px] font-black text-white/50 uppercase tracking-[0.2em]">Reference</span>
                                    </div>
                                    <video
                                        ref={videoRefB}
                                        src={getVideoUrl(slotB)}
                                        muted
                                        controls
                                        className="h-full w-full object-cover"
                                    />
                                </>
                            ) : (
                                <div className="w-full h-full flex flex-col items-center justify-center gap-2">
                                    <Play className="w-8 h-8 opacity-10" />
                                    <p className="text-[9px] font-black uppercase text-slate-700 tracking-widest">Select Reference</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* AI Analysis Footer */}
            {slotA && slotB && (
                <div className="mt-6 px-10 pb-8 animate-in slide-in-from-bottom-4 duration-700">
                    <div className="bg-[#0b0d14]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl flex flex-col md:flex-row gap-8 items-center relative overflow-hidden">
                        {/* Grade Score */}
                        <div className="shrink-0 flex flex-col items-center justify-center p-5 bg-cyan-500/10 border border-cyan-500/20 rounded-2xl w-32">
                            <span className="text-[9px] font-black text-cyan-400/60 uppercase tracking-widest mb-1">Match Score</span>
                            <span className="text-3xl font-black text-white">94%</span>
                            <span className="text-[8px] font-bold text-cyan-400/40 uppercase tracking-widest mt-1 text-center">Quality</span>
                        </div>

                        {/* Reasoning Memo */}
                        <div className="flex-1 space-y-3">
                            <div className="flex items-center gap-2 text-cyan-400">
                                <MessageSquare className="w-3.5 h-3.5" />
                                <h3 className="text-[10px] font-black uppercase tracking-[0.3em]">AI Analysis</h3>
                            </div>
                            <p className="text-[11px] text-slate-300 font-medium leading-relaxed uppercase tracking-tight">
                                <span className="text-cyan-400 font-black mr-2">[Summary]</span>
                                Strong match overall. The AI correctly identified high-motion segments in the reference and paired them with your best clips.
                                <span className="text-cyan-400/60 font-black mx-2 ml-4">[What Worked]</span>
                                Beat timing is frame-perfect at 0:08.
                                <span className="text-pink-400/60 font-black mx-2 ml-4">[Trade-offs]</span>
                                Used landscape clips to maintain visual flow, even though the target is vertical.
                            </p>
                        </div>

                        {/* Controls Column */}
                        <div className="shrink-0 border-l border-white/5 pl-8 flex flex-col gap-4">
                            <label className="flex items-center gap-4 cursor-pointer group">
                                <div className={cn(
                                    "h-5 w-10 rounded-full border transition-all relative",
                                    syncEnabled ? "bg-cyan-500 border-cyan-400 shadow-[0_0_15px_#22d3ee]" : "bg-white/5 border-white/10"
                                )}>
                                    <input type="checkbox" checked={syncEnabled} onChange={(e) => setSyncEnabled(e.target.checked)} className="sr-only" />
                                    <div className={cn("absolute top-1 left-1 h-3 w-3 rounded-full transition-all", syncEnabled ? "translate-x-5 bg-white" : "bg-slate-700")} />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[9px] font-black text-white uppercase tracking-widest">Frame Sync</span>
                                    <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest">{syncEnabled ? 'ENGAGED' : 'STANDBY'}</span>
                                </div>
                            </label>

                            <button
                                onClick={() => {
                                    if (videoRefA.current && videoRefB.current) {
                                        videoRefA.current.currentTime = 0;
                                        videoRefB.current.currentTime = 0;
                                        videoRefA.current.play();
                                        videoRefB.current.play();
                                    }
                                }}
                                className="flex items-center justify-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all group active:scale-95"
                            >
                                <Play className="w-3 h-3 text-cyan-400" />
                                <span className="text-[9px] font-black text-white uppercase tracking-widest">Play Both</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
