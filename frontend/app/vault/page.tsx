"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
    Activity,
    MonitorPlay,
    X,
    Sparkles,
    Zap,
    Palette,
    BrainCircuit,
    ChevronDown,
    ChevronUp,
    Video,
    Search,
    Type,
    Share2,
    Play,
    Info,
    History,
    MoreHorizontal,
    Download,
    Settings,
    Heart,
    Plus,
    Film,
    Layers,
    Eye,
    CheckCircle2,
    Clock,
    Music,
    TrendingUp,
    Check,
    Wand2
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference, Clip, StyleConfig } from "@/lib/types";
import StylingModal from "@/components/StylingModal";

export type ViewMode = "results" | "references" | "clips";
export type AssetItem = Clip | Reference | Result;

export default function VaultPage() {
    const searchParams = useSearchParams();
    const router = useRouter();

    // Data state
    const [clips, setClips] = useState<Clip[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [results, setResults] = useState<Result[]>([]);
    const [selectedItem, setSelectedItem] = useState<AssetItem | null>(null);
    const [viewMode, setViewMode] = useState<ViewMode>("results");
    const [loading, setLoading] = useState(true);
    const [intelligence, setIntelligence] = useState<any>(null);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [searchQuery, setSearchQuery] = useState("");
    const [isPlaying, setIsPlaying] = useState(false);

    // Module expansion states
    const [intelExpanded, setIntelExpanded] = useState(true);

    const [showAllDecisions, setShowAllDecisions] = useState(false);
    const [isStylingOpen, setIsStylingOpen] = useState(false);
    const [isStylingLoading, setIsStylingLoading] = useState(false);

    const videoRef = useRef<HTMLVideoElement>(null);
    const decisionListRef = useRef<HTMLDivElement>(null);

    // Fetch data
    useEffect(() => {
        const fetchAllAssets = async () => {
            try {
                const [clipsData, refsData, resultsData] = await Promise.all([
                    api.fetchClips(),
                    api.fetchReferences(),
                    api.fetchResults()
                ]);
                setClips(clipsData.clips || []);
                setReferences(refsData.references || []);
                setResults(resultsData.results || []);
            } catch (err) {
                toast.error("Failed to load assets");
            } finally {
                setLoading(false);
            }
        };
        fetchAllAssets();
    }, []);

    // Selection logic
    useEffect(() => {
        const filename = searchParams.get("filename");
        const type = searchParams.get("type") as ViewMode | null;

        if (filename && type && (references.length > 0 || results.length > 0 || clips.length > 0)) {
            let item: AssetItem | undefined;
            if (type === "results") item = results.find(r => r.filename === filename);
            else if (type === "references") item = references.find(r => r.filename === filename);
            else if (type === "clips") item = clips.find(c => c.filename === filename);

            if (item) {
                setSelectedItem(item);
                setViewMode(type);
            }
        } else if (results.length > 0 && !selectedItem) {
            setSelectedItem(results[0]);
        }
    }, [searchParams, results, references, clips, selectedItem]);

    // Intelligence Fetch
    useEffect(() => {
        if (!selectedItem) return;
        const fetchIntel = async () => {
            try {
                const key = viewMode === "clips" ? (selectedItem as Clip).clip_hash || selectedItem.filename : selectedItem.filename;
                const data = await api.fetchIntelligence(viewMode, key);
                setIntelligence(data);
            } catch (err) {
                setIntelligence(null);
            }
        };
        fetchIntel();
    }, [selectedItem, viewMode]);

    // Filter key decisions based on intelligence criteria
    const keyDecisions = useMemo(() => {
        if (!intelligence?.vault_report?.decision_stream) return [];
        
        return intelligence.vault_report.decision_stream.filter((decision: any) => {
            // Key decision criteria:
            // 1. Has counterfactual (what_if)
            // 2. Decision indicates constraint/compromise
            // 3. Structural importance
            const hasCounterfactual = decision.what_if && 
                !decision.what_if.toLowerCase().includes('no stronger alternative') && 
                !decision.what_if.toLowerCase().includes('no viable upgrade');
            
            const isCompromise = decision.decision.toLowerCase().includes('necessity') ||
                decision.decision.toLowerCase().includes('forced') ||
                decision.decision.toLowerCase().includes('compromise') ||
                decision.decision.toLowerCase().includes('structural');
            
            return hasCounterfactual || isCompromise;
        });
    }, [intelligence?.vault_report?.decision_stream]);

    const displayDecisions = showAllDecisions ? 
        (intelligence?.edl?.decisions || []) : 
        (intelligence?.vault_report?.decision_stream || []);
    const edlTimingMap = useMemo(() => {
        const map = new Map<number, { start: number; end: number }>();

        intelligence?.edl?.decisions?.forEach((d: any) => {
            map.set(d.segment_id, {
                start: d.timeline_start,
                end: d.timeline_end
            });
        });

        return map;
    }, [intelligence?.edl?.decisions]);

    // Auto-scroll decision list - REMOVED for better UX
    // useEffect(() => {
    //     if (viewMode === "results" && intelligence?.vault_report?.decision_stream) {
    //         const activeIdx = intelligence.vault_report.decision_stream.findIndex((decision: any) => {
    //             const timing = edlTimingMap.get(decision.segment_id);
    //             return timing && currentTime >= timing.start && currentTime <= timing.end;
    //         });
    //         if (activeIdx !== -1 && decisionListRef.current) {
    //             const activeEl = decisionListRef.current.children[activeIdx] as HTMLElement;
    //             if (activeEl) {
    //                 activeEl.scrollIntoView({
    //                     behavior: "smooth",
    //                     block: "center"
    //                 });
    //             }
    //         }
    //     }
    // }, [currentTime, intelligence, viewMode, edlTimingMap]);

    const videoUrl = useMemo(() => {
        if (!selectedItem) return "";
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        let path = (selectedItem as any).path || (selectedItem as any).filepath || (selectedItem as any).url || "";
        if (path && !path.startsWith("/")) path = "/" + path;
        return `${API_BASE}${path}?v=${Date.now()}`;
    }, [selectedItem]);

    const currentModeAssets = useMemo(() => {
        const assets = viewMode === "results" ? results : viewMode === "references" ? references : clips;
        if (!searchQuery.trim()) return assets;
        return assets.filter(a => a.filename.toLowerCase().includes(searchQuery.toLowerCase()));
    }, [viewMode, results, references, clips, searchQuery]);

    const cleanupReasoning = (text: string) => {
        if (!text) return "Optimized for visual flow.";
        return text
            .replace(/SERVING AS A STRATEGIC/g, 'Chosen as a')
            .replace(/SATISFIES THE NARRATIVE'S/g, 'Matches the')
            .replace(/HIGH-ENERGY DEMAND/g, 'energy')
            .replace(/PRIMARY EMOTIONAL CARRIER/g, 'main vibe')
            .toLowerCase();
    };

    if (loading) return (
        <div className="h-screen flex items-center justify-center bg-[#020306]">
            <div className="text-indigo-500 text-[10px] font-black uppercase tracking-[0.5em] animate-pulse">Syncing_Vault</div>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#08090a] text-slate-100 flex flex-col overflow-hidden">

            {/* STAGE HEADER: Netflix-Deep Glass */}
            <header className="h-14 flex items-center justify-between px-12 bg-[#08090a]/80 backdrop-blur-2xl border-b border-white/[0.03] shrink-0 z-[100]">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]" />
                        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Live</span>
                    </div>
                </div>

                <div className="flex-1 max-w-lg mx-auto">
                    <div className="relative group">
                        <div className="absolute inset-0 bg-white/[0.03] backdrop-blur-3xl rounded-3xl border border-white/5 group-focus-within:border-indigo-500/20 group-focus-within:bg-white/[0.05] transition-all duration-700" />
                        <input
                            type="text"
                            placeholder="Search library..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="relative w-full bg-transparent py-2 pl-4 pr-4 text-[11px] font-normal text-white placeholder-slate-600 outline-none z-10"
                        />
                    </div>
                </div>

                <nav className="flex items-center bg-white/5 p-1 rounded-xl border border-white/10 shrink-0">
                    {(["results", "references", "clips"] as ViewMode[]).map(mode => (
                        <button
                            key={mode}
                            onClick={() => setViewMode(mode)}
                            className={cn(
                                "px-5 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all",
                                viewMode === mode ? "text-white bg-indigo-600 shadow-lg shadow-indigo-600/20" : "text-slate-500 hover:text-slate-300"
                            )}
                        >
                            {mode}
                        </button>
                    ))}
                </nav>
            </header>

            {/* ASSET STRIP: Netflix-Style Content Cards */}
            <div className="h-48 border-b border-white/[0.03] bg-black/10 shrink-0 overflow-hidden relative">
                <div className="flex gap-6 overflow-x-auto p-6 custom-scrollbar-horizontal no-scrollbar h-full items-center px-12">
                    {currentModeAssets.map((item, idx) => {
                        const isSelected = selectedItem?.filename === item.filename;
                        return (
                            <div
                                key={idx}
                                onClick={() => setSelectedItem(item)}
                                className="shrink-0 w-64 group/item cursor-pointer"
                            >
                                <div
                                    className={cn(
                                        "relative w-full aspect-video rounded-xl overflow-hidden border transition-all duration-500 bg-[#0f1115] shadow-2xl",
                                        isSelected
                                            ? "border-indigo-500 ring-2 ring-indigo-500/40 scale-[1.05] z-10"
                                            : "border-white/5 opacity-90 hover:opacity-100 hover:scale-[1.02] hover:border-white/20"
                                    )}
                                >
                                    {item.thumbnail_url ? (
                                        <img
                                            src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${item.thumbnail_url}`}
                                            alt={item.filename}
                                            className="w-full h-full object-cover"
                                        />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-indigo-500/5">
                                            <Film className="h-6 w-6 text-indigo-500/20" />
                                        </div>
                                    )}

                                    {/* Netflix-style Card Footer */}
                                    <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/90 to-transparent flex flex-col justify-end p-3 transform translate-y-2 group-hover/item:translate-y-0 transition-transform">
                                        <div className="flex items-center justify-between">
                                            <p className="text-[9px] font-black text-white uppercase tracking-wider truncate">{item.filename}</p>
                                            <div className="flex items-center gap-1.5">
                                                <div className="h-5 w-5 rounded bg-white/10 backdrop-blur-md flex items-center justify-center">
                                                    <Play className="h-2.5 w-2.5 text-white fill-white" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {isSelected && (
                                        <div className="absolute top-3 right-3 px-2 py-0.5 rounded bg-indigo-600 text-[7px] font-black uppercase tracking-tighter shadow-lg">Viewing</div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* WORKBENCH: Dense Two-Column Stage */}
            <main className="flex-1 flex overflow-hidden">
                <div className="flex-1 flex flex-col overflow-y-auto custom-scrollbar p-12">

                    <div className="max-w-[1500px] mx-auto w-full flex gap-10 items-start">

                        {/* LEFT: Video Stage (Increased height for cinematic feel) */}
                        <div className="flex-1 flex flex-col gap-6 min-w-0 -mt-4">
                            <div className="relative w-full max-w-[850px] mx-auto group">
                                <div className={cn("video-aura", isPlaying && "video-aura-active animate-pulse-vibrant")} />
                                <div className="relative aspect-[14/12] rounded-[2.5rem] overflow-hidden bg-black shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-white/10 group-hover:border-indigo-500/30 transition-all duration-700">
                                    {selectedItem ? (
                                        <video
                                            ref={videoRef}
                                            src={videoUrl}
                                            onTimeUpdate={() => setCurrentTime(videoRef.current?.currentTime || 0)}
                                            onLoadedMetadata={() => setDuration(videoRef.current?.duration || 0)}
                                            onPlay={() => setIsPlaying(true)}
                                            onPause={() => setIsPlaying(false)}
                                            className="w-full h-full object-cover"
                                            controls
                                        />
                                    ) : (
                                        <div className="w-full h-full flex flex-col items-center justify-center opacity-20">
                                            <Play className="h-12 w-12 mb-4" />
                                            <p className="text-[10px] font-black uppercase tracking-widest">Select specimen</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Info & Secondary Controls */}
                            <div className="w-full max-w-[850px] mx-auto flex items-center justify-between px-4">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-4">
                                        <span className="text-2xl font-black text-white uppercase tracking-tighter italic drop-shadow-sm">{selectedItem?.filename.split('_')[0] || "UNTITLED"}</span>
                                        <div className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20">
                                            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Edit Feel: 9.2</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-5 opacity-50">
                                        <div className="flex items-center gap-2"><Clock className="h-3.5 w-3.5" /><span className="text-[10px] font-bold uppercase tracking-wider">{duration.toFixed(1)}s</span></div>
                                        <div className="flex items-center gap-2"><Music className="h-3.5 w-3.5" /><span className="text-[10px] font-bold uppercase tracking-wider">{intelligence?.bpm || 128} BPM</span></div>
                                    </div>
                                </div>
                                <div className="flex gap-3">
                                    <button className="h-12 px-7 rounded-2xl bg-white text-black font-black text-[10px] uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all shadow-xl active:scale-95">Remix Vibe</button>
                                    <button className="h-12 w-12 rounded-2xl bg-white/5 border border-white/10 text-white flex items-center justify-center hover:bg-white/10 transition-all active:scale-95"><Share2 className="h-5 w-5" /></button>
                                    <button
                                        onClick={() => setIsStylingOpen(true)}
                                        disabled={viewMode !== "results"}
                                        className={cn(
                                            "h-12 w-12 rounded-2xl bg-white/5 border border-white/10 text-slate-500 flex items-center justify-center hover:bg-white/10 transition-all active:scale-95",
                                            viewMode !== "results" && "opacity-20 cursor-not-allowed"
                                        )}
                                    >
                                        <Palette className="h-4 w-4" />
                                    </button>
                                </div>
                            </div>

                            {/* AI INTELLIGENCE SUITE */}
                            <div className="w-full max-w-[850px] mx-auto space-y-4">

                                {/* MODULE 1: NARRATIVE (Full Width) */}
                                <div className="rounded-3xl border border-white/[0.03] bg-white/[0.01] overflow-hidden group/module">
                                    <button
                                        onClick={() => setIntelExpanded(!intelExpanded)}
                                        className="w-full p-6 flex items-center justify-between hover:bg-white/[0.02] transition-all"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.1)]">
                                                <BrainCircuit className="h-5 w-5" />
                                            </div>
                                            <div className="text-left">
                                                <h3 className="text-[11px] font-black text-white uppercase tracking-[0.3em]">Creative Logic</h3>
                                                <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest mt-0.5">Narrative Intent</p>
                                            </div>
                                        </div>
                                        {intelExpanded ? <ChevronUp className="h-4 w-4 text-slate-600" /> : <ChevronDown className="h-4 w-4 text-slate-600" />}
                                    </button>

                                    {intelExpanded && (
                                        <div className="p-8 pt-0 animate-slide-in-from-top">
                                            <p className="text-base font-medium text-slate-300 leading-relaxed italic border-l-2 border-indigo-500/30 pl-6 mb-2">
                                                "{intelligence?.critique?.monologue || "Analyzing narrative flow..."}"
                                            </p>
                                        </div>
                                    )}
                                </div>

                                {/* MODULE 2: DIRECTOR'S NOTES (Full Width) */}
                                <div className="rounded-3xl border border-pink-500/10 bg-pink-500/[0.01] overflow-hidden relative min-h-[220px]">
                                    <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                                        <Sparkles className="h-24 w-24 text-pink-500" />
                                    </div>
                                    <div className="p-6">
                                        <div className="flex items-center gap-3 mb-6 relative z-10">
                                            <div className="h-8 w-8 rounded-lg bg-pink-500/10 flex items-center justify-center text-pink-400 border border-pink-500/20">
                                                <Palette className="h-4 w-4" />
                                            </div>
                                            <div>
                                                <h3 className="text-[10px] font-black text-pink-100 uppercase tracking-[0.2em]">Director's Notes</h3>
                                                <p className="text-[8px] font-bold text-pink-500/60 uppercase tracking-widest mt-0.5">Recommended Actions</p>
                                            </div>
                                        </div>

                                        <div className="space-y-3 relative z-10">
                                            {intelligence?.critique?.remake_actions?.length > 0 ? (
                                                intelligence.critique.remake_actions.map((action: any, i: number) => (
                                                    <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-black/20 border border-pink-500/10 hover:border-pink-500/30 transition-colors group">
                                                        <div className="mt-0.5 h-1.5 w-1.5 rounded-full bg-pink-500 shadow-[0_0_5px_#ec4899]" />
                                                        <div className="flex-1">
                                                            <div className="flex justify-between items-center mb-1">
                                                                <span className="text-[9px] font-black text-pink-400 uppercase tracking-wider">{action.type.replace('_', ' ')}</span>
                                                                <button className="opacity-0 group-hover:opacity-100 text-[8px] px-2 py-0.5 rounded bg-pink-500 text-white font-bold uppercase transition-opacity">Apply</button>
                                                            </div>
                                                            <p className="text-[10px] text-slate-300 leading-snug">{action.suggestion}</p>
                                                        </div>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="flex items-center gap-3 opacity-40 p-2">
                                                    <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                                                    <span className="text-[10px] font-bold uppercase tracking-widest">No Critical Actions Needed</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* RIGHT COLUMN: DECISION STREAM + TELEMETRY */}
                        <div className="w-[420px] flex flex-col gap-6 shrink-0">

                            {/* DECISION STREAM: THE WHITEBOX */}
                            <div className="flex flex-col bg-gradient-to-b from-white/[0.02] to-transparent border border-white/[0.05] rounded-[2.5rem] overflow-hidden shadow-2xl" style={{ height: '520px' }}>
                                <div className="p-7 border-b border-white/[0.05] flex items-center justify-between bg-black/20 backdrop-blur-md">
                                    <div className="flex items-center gap-4">
                                        <div className="h-2 w-2 rounded-full bg-indigo-500 shadow-[0_0_10px_#6366f1]" />
                                        <h3 className="text-[11px] font-black text-white uppercase tracking-[0.4em]">Decision Stream</h3>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className="px-3 py-1 rounded-lg bg-white/5 border border-white/10">
                                            <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
                                                {showAllDecisions ? "All" : "Key"} {displayDecisions.length} / {intelligence?.edl?.decisions?.length || 0}
                                            </span>
                                        </div>
                                        <button
                                            onClick={() => setShowAllDecisions(!showAllDecisions)}
                                            className={cn(
                                                "px-2 py-1 rounded-md transition-colors",
                                                showAllDecisions 
                                                    ? "bg-white/10 border-white/20 hover:bg-white/15"
                                                    : "bg-indigo-500/15 border-indigo-500/30 hover:bg-indigo-500/25"
                                            )}
                                        >
                                            <span className={cn(
                                                "text-[7px] font-black uppercase tracking-widest",
                                                showAllDecisions ? "text-slate-400" : "text-indigo-400"
                                            )}>
                                                {showAllDecisions ? "All" : "Key"}
                                            </span>
                                        </button>
                                    </div>
                                </div>

                                <div ref={decisionListRef} className="flex-1 overflow-y-auto p-7 space-y-4 custom-scrollbar-thin">
                                    {!displayDecisions.length ? (
                                        <div className="h-full flex flex-col items-center justify-center opacity-20 text-center px-12">
                                            <Zap className="h-10 w-10 mb-6 text-indigo-500" />
                                            <p className="text-[11px] font-black uppercase tracking-[0.2em] leading-relaxed">Awaiting logic<br />Play to sync</p>
                                        </div>
                                    ) : (
                                        <>
                                            {/* Show filtered decisions with proper hierarchy */}
                                            {displayDecisions.map((decision: any, idx: number) => {
                                                const timing = edlTimingMap.get(decision.segment_id);
                                                const isActive = timing && currentTime >= timing.start && currentTime <= timing.end;
                                                const isKeyDecision = !showAllDecisions; // Vault decisions are key decisions, EDL are all decisions
                                                
                                                return (
                                                    <div 
                                                        key={idx} 
                                                        onClick={() => {
                                                            if (timing && videoRef.current) {
                                                                videoRef.current.currentTime = timing.start;
                                                            }
                                                        }}
                                                        className={cn(
                                                            "transition-all duration-300 relative group/card cursor-pointer",
                                                            isKeyDecision ? (
                                                                "p-6 rounded-[1.25rem] bg-gradient-to-b from-white/[0.04] to-white/[0.015] border-[rgba(130,140,255,0.15] shadow-[0_0_40px_rgba(120,130,255,0.08)] border-l-2 border-[rgba(59,130,246,0.6)]"
                                                            ) : (
                                                                "p-4 rounded-[1rem] bg-gradient-to-b from-white/[0.02] to-white/[0.01] border-white/[0.1] shadow-[0_0_20px_rgba(120,130,255,0.04)]"
                                                            ),
                                                            isActive
                                                                ? "scale-[1.05] z-20 border-2 border-indigo-400 shadow-[0_0_100px_rgba(99,102,241,0.4)] bg-gradient-to-b from-indigo-500/10 to-indigo-500/5 animate-pulse"
                                                                : isKeyDecision
                                                                    ? "opacity-90 hover:opacity-100 hover:translateY-[-2px] hover:shadow-[0_0_60px_rgba(120,130,255,0.15)]"
                                                                    : "opacity-60 hover:opacity-80 hover:translateY-[-1px]"
                                                        )}
                                                    >
                                                        <div className="flex items-center justify-between mb-3">
                                                            <div className="flex items-center gap-3">
                                                                <span className={cn(
                                                                    "font-mono tracking-[0.12em]",
                                                                    isKeyDecision ? "text-[#8B90FF]" : "text-slate-400"
                                                                )}>
                                                                    SEGMENT {String(decision.segment_id).padStart(2, '0')}
                                                                </span>
                                                                {isActive && (
                                                                    <div className={cn(
                                                                        "h-1.5 w-1.5 rounded-full animate-pulse",
                                                                        isKeyDecision ? "bg-indigo-400 shadow-[0_0_10px_#818cf8]" : "bg-gray-400"
                                                                    )} />
                                                                )}
                                                            </div>
                                                            <div className="flex items-center gap-2">
                                                                {timing && (
                                                                    <span className="text-[10px] font-mono text-[rgba(180,190,255,0.7)]">
                                                                        {timing.start.toFixed(1)}s – {timing.end.toFixed(1)}s
                                                                    </span>
                                                                )}
                                                                {isKeyDecision && (
                                                                    <span className="px-2 py-0.5 rounded bg-indigo-500/20 border border-indigo-500/30">
                                                                        <span className="text-[6px] font-black text-indigo-300 uppercase tracking-widest">KEY DECISION</span>
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                        
                                                        <div className="space-y-3">
                                                            {/* Vault decisions have full intelligence structure */}
                                                            {isKeyDecision && (
                                                                <>
                                                                    {/* Intent Line (largest) */}
                                                                    <div className="mb-2">
                                                                        <p className="text-[15px] font-medium text-white leading-[1.35]">
                                                                            <span className="text-[#9AA0FF] font-normal">I wanted </span>
                                                                            {decision.what_i_tried}
                                                                        </p>
                                                                    </div>
                                                                    
                                                                    {/* Decision Label + Explanation */}
                                                                    <div className="space-y-1">
                                                                        <p className="text-[10px] font-black text-[#6F74FF] uppercase tracking-[0.14em]">DECISION</p>
                                                                        <p className="text-[13px] text-[#D6D8FF] leading-relaxed">{decision.decision}</p>
                                                                    </div>
                                                                    
                                                                    {/* Counterfactual (if exists) */}
                                                                    {decision.what_if && 
                                                                        !decision.what_if.toLowerCase().includes('no stronger alternative') && 
                                                                        !decision.what_if.toLowerCase().includes('no viable upgrade') && (
                                                                        <div className="flex items-start gap-2">
                                                                            <span className="text-[rgba(180,190,255,0.55)] text-sm">→</span>
                                                                            <p className="text-[12px] text-[rgba(180,190,255,0.55)] italic leading-relaxed flex-1">
                                                                                {decision.what_if}
                                                                            </p>
                                                                        </div>
                                                                    )}
                                                                </>
                                                            )}
                                                            
                                                            {/* EDL decisions have basic structure */}
                                                            {!isKeyDecision && (
                                                                <div className="space-y-2">
                                                                    <p className="text-[11px] text-slate-300 leading-relaxed">
                                                                        {decision.clip_path?.split(/[\\/]/).pop()}
                                                                    </p>
                                                                    <p className="text-[10px] text-slate-500 leading-relaxed">
                                                                        {cleanupReasoning(decision.reasoning)}
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                        
                                                        {isActive && (
                                                            <div className="absolute bottom-0 left-0 h-1 bg-indigo-500 rounded-full transition-all duration-300" style={{ width: '100%' }} />
                                                        )}
                                                    </div>
                                                );
                                            })}
                                            
                                            {/* Show all EDL decisions when toggle is on */}
                                            {showAllDecisions && intelligence?.edl?.decisions?.map((edlDecision: any, idx: number) => {
                                                const timing = { start: edlDecision.timeline_start, end: edlDecision.timeline_end };
                                                const isActive = currentTime >= timing.start && currentTime <= timing.end;
                                                const vaultDecision = intelligence?.vault_report?.decision_stream?.find((v: any) => v.segment_id === edlDecision.segment_id);
                                                
                                                return (
                                                    <div key={`all-${idx}`} className={cn(
                                                        "p-4 rounded-[1rem] border transition-all duration-300 relative group/card",
                                                        "bg-gradient-to-b from-white/[0.02] to-white/[0.01] border-white/[0.1]",
                                                        "shadow-[0_0_20px_rgba(120,130,255,0.04)]",
                                                        isActive
                                                            ? "scale-[1.02] z-10 border-indigo-400/50 shadow-[0_0_40px_rgba(99,102,241,0.2)]"
                                                            : "opacity-50 hover:opacity-70"
                                                    )}>
                                                        <div className="flex items-center justify-between mb-2">
                                                            <div className="flex items-center gap-3">
                                                                <span className="text-[10px] font-mono text-slate-400 tracking-widest">SEGMENT {String(edlDecision.segment_id).padStart(2, '0')}</span>
                                                                {isActive && <div className="h-1 w-1 rounded-full bg-indigo-400 animate-pulse" />}
                                                            </div>
                                                            <span className="text-[9px] text-[rgba(180,190,255,0.5)] font-mono">
                                                                {timing.start.toFixed(1)}s - {timing.end.toFixed(1)}s
                                                            </span>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <p className="text-[11px] text-slate-300 leading-relaxed">
                                                                {edlDecision.clip_path?.split(/[\\/]/).pop()}
                                                            </p>
                                                            <p className="text-[10px] text-slate-500 leading-relaxed">
                                                                {cleanupReasoning(edlDecision.reasoning)}
                                                            </p>
                                                        </div>
                                                        {isActive && (
                                                            <div className="absolute bottom-0 left-0 h-0.5 bg-indigo-400 rounded-full transition-all duration-300" style={{ width: '100%' }} />
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* RIGHT: SYSTEM TELEMETRY (Relocated) */}
                            <div className="rounded-3xl border border-blue-500/10 bg-blue-500/[0.01] overflow-hidden relative shadow-xl">
                                <div className="p-6">
                                    <div className="flex items-center gap-3 mb-6 relative z-10">
                                        <div className="h-8 w-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20">
                                            <Activity className="h-4 w-4" />
                                        </div>
                                        <div>
                                            <h3 className="text-[10px] font-black text-blue-100 uppercase tracking-[0.2em]">Telemetry</h3>
                                            <p className="text-[8px] font-bold text-blue-500/60 uppercase tracking-widest mt-0.5">System Status</p>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 relative z-10 mb-4">
                                        <div className="p-3 rounded-xl bg-blue-500/[0.03] border border-blue-500/10 hover:border-blue-500/30 transition-colors">
                                            <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Sync Engine</p>
                                            <div className="flex items-center justify-between">
                                                <span className="text-[10px] font-bold text-slate-300">{intelligence?.bpm ? `${intelligence.bpm} BPM` : "Adaptive"}</span>
                                                <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_5px_#10b981] animate-pulse" />
                                            </div>
                                        </div>
                                        <div className="p-3 rounded-xl bg-blue-500/[0.03] border border-blue-500/10 hover:border-blue-500/30 transition-colors">
                                            <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Confidence</p>
                                            <div className="mt-1 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                                                <div className="h-full bg-blue-500 w-[92%]" />
                                            </div>
                                        </div>
                                    </div>

                                    <div className="relative z-10">
                                        <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-2">Star Performers</p>
                                        <div className="space-y-2">
                                            {intelligence?.critique?.star_performers?.slice(0, 3).map((s: string, i: number) => (
                                                <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-emerald-500/[0.03] border border-emerald-500/10 hover:bg-emerald-500/[0.06] transition-colors group">
                                                    <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                                                    <span className="text-[9px] font-bold text-slate-300 truncate w-full group-hover:text-emerald-400 transition-colors">{s}</span>
                                                </div>
                                            ))}
                                            {(!intelligence?.critique?.star_performers?.length) && <div className="text-[9px] opacity-40 uppercase pl-1">None detected</div>}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </main>

            <StylingModal
                isOpen={isStylingOpen}
                onClose={() => setIsStylingOpen(false)}
                initialConfig={intelligence?.style_config}
                onApply={async (config) => {
                    if (!selectedItem) return;
                    setIsStylingLoading(true);
                    const toastId = toast.loading("Applying styling...");
                    try {
                        await api.applyStyle(selectedItem.filename, config);

                        // Force refresh intelligence to get new config
                        const key = viewMode === "clips" ? (selectedItem as Clip).clip_hash || selectedItem.filename : selectedItem.filename;
                        const data = await api.fetchIntelligence(viewMode, key);
                        setIntelligence(data);

                        toast.success("Aesthetic Path Updated", { id: toastId });
                        setIsStylingOpen(false);

                        // Refresh video to show changes
                        if (videoRef.current) {
                            const currentPos = videoRef.current.currentTime;
                            videoRef.current.src = `${videoUrl}&t=${Date.now()}`;
                            videoRef.current.currentTime = currentPos;
                            videoRef.current.play();
                        }
                    } catch (err) {
                        toast.error("Styling failed", { id: toastId });
                    } finally {
                        setIsStylingLoading(false);
                    }
                }}
            />
        </div>
    );
}
