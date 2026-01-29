"use client";

import { useRef } from "react";
import {
    BrainCircuit,
    MonitorStop,
    TrendingUp,
    Database,
    MonitorPlay,
    MessageSquare,
    Sparkles,
    Zap
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { AssetItem } from "./page";

interface VaultAProps {
    selectedItem: AssetItem | null;
    viewMode: "results" | "references" | "clips";
    intelLoading: boolean;
    intelligence: any;
    currentTime: number;
    duration: number;
    handleTimeUpdate: () => void;
    handleLoadedMetadata: () => void;
    videoRef: React.RefObject<HTMLVideoElement | null>;
    getVideoUrl: (item: AssetItem) => string;
    waveformData: number[];
    synthesisMetrics: number[];
    currentDecision: any;
    currentSegment: any;
}

export default function VaultA({
    selectedItem,
    viewMode,
    intelLoading,
    intelligence,
    currentTime,
    duration,
    handleTimeUpdate,
    handleLoadedMetadata,
    videoRef,
    getVideoUrl,
    waveformData,
    synthesisMetrics,
    currentDecision,
    currentSegment
}: VaultAProps) {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-10 items-start relative flex-1">
            {/* Left: Intelligence DNA */}
            <div className="flex flex-col gap-6 max-w-[420px]">
                <div className="bg-[#0b0d14]/40 border border-white/5 rounded-2xl p-5 relative overflow-hidden group">
                    <div className="flex items-center gap-2 mb-4">
                        <div className={cn("w-1.5 h-1.5 rounded-full", intelligence ? "bg-cyan-500" : "bg-slate-700")} />
                        <h3 className="text-[10px] font-black text-slate-200 uppercase tracking-[0.4em]">Intelligence_DNA</h3>
                    </div>
                    {intelligence ? (
                        <div className="grid grid-cols-2 gap-6">
                            {[
                                { l: "Motion", v: intelligence.motion || "MED", s: "CAPTURED" },
                                { l: "Energy", v: intelligence.energy || "8.5", s: "VERIFIED" },
                                { l: "Style", v: intelligence.editing_style || "REEL", s: "STRATEGY" },
                                { l: "Cuts", v: `${intelligence.segments?.length || 0}`, s: "MAPPED" }
                            ].map((stat, i) => (
                                <div key={i} className="flex flex-col">
                                    <span className="text-[8px] font-black text-slate-600 uppercase mb-1">{stat.l}</span>
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-[13px] font-black text-white">{stat.v}</span>
                                        <span className="text-[8px] font-bold text-cyan-500/50">{stat.s}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="h-24 flex items-center justify-center border border-dashed border-white/5 rounded-xl text-[9px] text-slate-600 uppercase font-black">Scanning Asset...</div>
                    )}
                </div>

                <div className="bg-[#0b0d14]/40 border border-white/5 rounded-2xl p-5">
                    <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-[0.4em] mb-4">Aesthetic_Extraction</h3>
                    <div className="flex gap-4">
                        {synthesisMetrics.map((m, i) => (
                            <div key={i} className="flex-1 flex flex-col items-center">
                                <div className="w-10 h-10 rounded-full border border-white/5 flex items-center justify-center text-[10px] font-black text-indigo-400">{m}%</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Center: Video Hero */}
            <div className="flex flex-col items-center gap-4">
                <div className="relative h-[97vh] w-[420px] max-w-[440px]">
                    <div className="absolute inset-0 rounded-[3rem] bg-black/40 border border-white/5 shadow-2xl overflow-hidden">
                        {selectedItem ? (
                            <video
                                ref={videoRef}
                                src={getVideoUrl(selectedItem)}
                                onTimeUpdate={handleTimeUpdate}
                                onLoadedMetadata={handleLoadedMetadata}
                                controls
                                className="h-full w-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center opacity-10 bg-black/20">
                                <MonitorPlay className="w-16 h-16 mb-4" />
                                <p className="text-[12px] font-black uppercase tracking-[0.6em] text-slate-500">No Video Selected</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="w-[420px] bg-[#0b0d14]/40 rounded-3xl border border-white/5 p-4">
                    <div className="h-6 flex items-end gap-[1px]">
                        {waveformData.map((h, i) => (
                            <div
                                key={i}
                                className={cn(
                                    "flex-1 transition-all duration-300",
                                    duration > 0 && i <= (currentTime / duration) * 48 ? "bg-cyan-400" : "bg-white/5"
                                )}
                                style={{ height: `${h}%` }}
                            />
                        ))}
                    </div>
                </div>
            </div>

            {/* Right: Director's Log */}
            <div className="flex flex-col gap-6 max-w-[420px]">
                <div className="bg-[#0b0d14]/60 border border-indigo-500/20 rounded-3xl p-6 shadow-xl">
                    <div className="flex items-center gap-2 mb-4 text-indigo-400">
                        <Sparkles className="w-4 h-4" />
                        <h3 className="text-[11px] font-black uppercase tracking-[0.3em]">Director_Log</h3>
                    </div>
                    <div className="bg-black/40 p-4 rounded-xl border border-white/5 font-mono text-[11px] text-slate-300 leading-relaxed min-h-[120px]">
                        {intelLoading ? (
                            <p className="animate-pulse">Accessing consciousness stream...</p>
                        ) : intelligence ? (
                            <p>{viewMode === "results" ? currentDecision?.reasoning || intelligence.blueprint?.overall_reasoning : (currentSegment?.reasoning || intelligence.content_description || "Analysis stream active. Identifying structural targets and motion deltas.")}</p>
                        ) : (
                            <p className="text-slate-600 italic">Select a specimen to view AI reasoning.</p>
                        )}
                    </div>
                </div>

                {intelligence && (
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-indigo-500/5 border border-indigo-500/10 p-4 rounded-xl">
                            <span className="text-[8px] font-black text-indigo-400/60 uppercase block mb-1">Agent_Advice</span>
                            <p className="text-[10px] font-black text-white uppercase truncate">
                                {viewMode === "clips" ? "IDEAL FOR PEAK" : "SYNC STABILIZED"}
                            </p>
                        </div>
                        <div className="bg-cyan-500/5 border border-cyan-500/10 p-4 rounded-xl">
                            <span className="text-[8px] font-black text-cyan-400/60 uppercase block mb-1">Status</span>
                            <p className="text-[10px] font-black text-white uppercase">LOGIC_LOCKED</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
