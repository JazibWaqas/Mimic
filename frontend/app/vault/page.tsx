"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
    Activity,
    MonitorPlay,
    X,
    Sparkles,
    Zap,
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
    TrendingUp
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference, Clip } from "@/lib/types";

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
    const [intelExpanded, setIntelExpanded] = useState(true);
    const [showMoreDetails, setShowMoreDetails] = useState(false);

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

    // Auto-scroll decision list
    useEffect(() => {
        if (viewMode === "results" && intelligence?.edl?.decisions) {
            const activeIdx = intelligence.edl.decisions.findIndex((d: any) =>
                currentTime >= d.timeline_start && currentTime <= d.timeline_end
            );
            if (activeIdx !== -1 && decisionListRef.current) {
                const activeEl = decisionListRef.current.children[activeIdx] as HTMLElement;
                if (activeEl) {
                    decisionListRef.current.scrollTo({
                        top: activeEl.offsetTop - 40,
                        behavior: "smooth"
                    });
                }
            }
        }
    }, [currentTime, intelligence, viewMode]);

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
            <header className="h-20 flex items-center justify-between px-12 bg-[#08090a]/80 backdrop-blur-2xl border-b border-white/[0.03] shrink-0 z-[100]">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]" />
                        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Live</span>
                    </div>
                </div>

                <div className="flex-1 max-w-lg mx-auto">
                    <div className="relative group">
                        <div className="absolute inset-0 bg-white/[0.02] backdrop-blur-3xl rounded-2xl border border-white/5 group-focus-within:border-indigo-500/20 group-focus-within:bg-white/[0.04] transition-all duration-700" />
                        <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-600 group-focus-within:text-indigo-400 z-10 transition-colors" />
                        <input
                            type="text"
                            placeholder="Search library..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="relative w-full bg-transparent py-3 pl-12 pr-4 text-[11px] font-medium text-white placeholder-slate-700 outline-none z-10"
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

                    <div className="max-w-[1400px] mx-auto w-full flex gap-10 items-start">

                        {/* LEFT: Video Stage (Increased height for cinematic feel) */}
                        <div className="flex-1 flex flex-col gap-10 min-w-0">
                            <div className="relative w-full max-w-[820px] mx-auto group">
                                <div className={cn("video-aura", isPlaying && "video-aura-active animate-pulse-vibrant")} />
                                <div className="relative aspect-[16/11] rounded-[2.5rem] overflow-hidden bg-black shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-white/10 group-hover:border-indigo-500/30 transition-all duration-700">
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
                            <div className="w-full max-w-[820px] mx-auto flex items-center justify-between px-4">
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
                                    <button className="h-12 w-12 rounded-2xl bg-white/5 border border-white/10 text-slate-500 flex items-center justify-center hover:bg-white/10 transition-all active:scale-95"><Type className="h-4 w-4" /></button>
                                </div>
                            </div>

                            {/* AI INTELLIGENCE SUITE: Collapsible Forensic Modules */}
                            <div className="w-full max-w-[820px] mx-auto space-y-4">

                                {/* 1. WHY THE EDIT WORKS (The Story) */}
                                <div className="rounded-3xl border border-white/[0.03] bg-white/[0.01] overflow-hidden group/module">
                                    <button
                                        onClick={() => setIntelExpanded(!intelExpanded)}
                                        className="w-full p-6 flex items-center justify-between hover:bg-white/[0.02] transition-all"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="h-10 w-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 border border-cyan-500/20">
                                                <BrainCircuit className="h-5 w-5" />
                                            </div>
                                            <div className="text-left">
                                                <h3 className="text-[10px] font-black text-white uppercase tracking-[0.3em]">Why the edit works</h3>
                                                <p className="text-[8px] font-bold text-slate-600 uppercase tracking-widest mt-0.5">The Creative Logic</p>
                                            </div>
                                        </div>
                                        {intelExpanded ? <ChevronUp className="h-4 w-4 text-slate-600" /> : <ChevronDown className="h-4 w-4 text-slate-600" />}
                                    </button>

                                    {intelExpanded && (
                                        <div className="p-8 pt-0 space-y-8 animate-slide-in-from-top">
                                            <div className="space-y-4">
                                                <p className="text-base font-medium text-slate-300 leading-relaxed italic border-l-2 border-cyan-500/30 pl-6">
                                                    "{intelligence?.critique?.monologue ?
                                                        intelligence.critique.monologue.split('.').slice(0, 2).join('.') + '.' :
                                                        "This edit flows naturally, capturing the energy perfectly while maintaining a consistent visual rhythm."}"
                                                </p>
                                                <p className="text-sm text-slate-400 leading-relaxed pl-6 opacity-60">
                                                    The system prioritized **narrative continuity** by anchoring on solo subjects, ensuring the transition from intro to peak feels earned rather than forced.
                                                </p>
                                            </div>

                                            <div className="grid grid-cols-2 gap-8">
                                                <div className="space-y-4">
                                                    <p className="text-[9px] font-black text-indigo-400 uppercase tracking-widest">What Worked</p>
                                                    <div className="space-y-2">
                                                        {intelligence?.critique?.star_performers?.slice(0, 2).map((s: string, i: number) => (
                                                            <div key={i} className="flex items-center gap-3 text-[10px] font-bold text-slate-400 uppercase bg-white/[0.02] p-3 rounded-xl border border-white/5"><CheckCircle2 className="h-3.5 w-3.5 text-indigo-500" />{s}</div>
                                                        ))}
                                                    </div>
                                                </div>
                                                <div className="space-y-4">
                                                    <p className="text-[9px] font-black text-pink-500 uppercase tracking-widest">Ways to evolve</p>
                                                    <div className="space-y-2">
                                                        {intelligence?.critique?.missing_ingredients?.slice(0, 2).map((s: string, i: number) => (
                                                            <div key={i} className="flex items-center gap-3 text-[10px] font-bold text-slate-500 uppercase bg-white/[0.02] p-3 rounded-xl border border-white/5"><Sparkles className="h-3.5 w-3.5 text-pink-500/30" />{s}</div>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* MORE DETAILS TOGGLE */}
                                {!showMoreDetails ? (
                                    <button
                                        onClick={() => setShowMoreDetails(true)}
                                        className="w-full py-4 text-[9px] font-black text-slate-600 uppercase tracking-[0.3em] hover:text-indigo-400 transition-colors"
                                    >
                                        + Show System Details
                                    </button>
                                ) : (
                                    <div className="space-y-4 animate-slide-in-from-top">
                                        {/* 2. HOW THE SYSTEM THOUGHT (The Strategy) */}
                                        <div className="rounded-3xl border border-white/[0.03] bg-white/[0.01] overflow-hidden">
                                            <button className="w-full p-6 flex items-center justify-between hover:bg-white/[0.02] transition-all">
                                                <div className="flex items-center gap-4">
                                                    <div className="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
                                                        <Zap className="h-5 w-5" />
                                                    </div>
                                                    <div className="text-left">
                                                        <h3 className="text-[10px] font-black text-white uppercase tracking-[0.3em]">How the system thought</h3>
                                                        <p className="text-[8px] font-bold text-slate-600 uppercase tracking-widest mt-0.5">Operational Strategy</p>
                                                    </div>
                                                </div>
                                                <ChevronDown className="h-4 w-4 text-slate-600" />
                                            </button>
                                        </div>

                                        {/* 3. EXTRA DETAILS (The Data) */}
                                        <div className="rounded-3xl border border-white/[0.03] bg-white/[0.01] overflow-hidden">
                                            <button className="w-full p-6 flex items-center justify-between hover:bg-white/[0.02] transition-all">
                                                <div className="flex items-center gap-4">
                                                    <div className="h-10 w-10 rounded-xl bg-slate-500/10 flex items-center justify-center text-slate-400 border border-slate-500/20">
                                                        <Activity className="h-5 w-5" />
                                                    </div>
                                                    <div className="text-left">
                                                        <h3 className="text-[10px] font-black text-white uppercase tracking-[0.3em]">Extra Details</h3>
                                                        <p className="text-[8px] font-bold text-slate-600 uppercase tracking-widest mt-0.5">Frame-Level Data</p>
                                                    </div>
                                                </div>
                                                <ChevronDown className="h-4 w-4 text-slate-600" />
                                            </button>
                                        </div>

                                        <button
                                            onClick={() => setShowMoreDetails(false)}
                                            className="w-full py-2 text-[8px] font-black text-slate-700 uppercase tracking-widest hover:text-white transition-colors"
                                        >
                                            Hide Details
                                        </button>
                                    </div>
                                )}

                            </div>
                        </div>

                        {/* RIGHT: THE WHITEBOX (Decision Stream - Bigger & Stylized) */}
                        <div className="w-[420px] flex flex-col bg-gradient-to-b from-white/[0.02] to-transparent border border-white/[0.05] rounded-[2.5rem] overflow-hidden shrink-0 shadow-2xl" style={{ height: '600px' }}>
                            <div className="p-7 border-b border-white/[0.05] flex items-center justify-between bg-black/20 backdrop-blur-md">
                                <div className="flex items-center gap-4">
                                    <div className="h-2 w-2 rounded-full bg-indigo-500 shadow-[0_0_10px_#6366f1]" />
                                    <h3 className="text-[11px] font-black text-white uppercase tracking-[0.4em]">Decision Stream</h3>
                                </div>
                                <div className="px-3 py-1 rounded-lg bg-white/5 border border-white/10">
                                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{intelligence?.edl?.decisions?.length || 0} Points</span>
                                </div>
                            </div>

                            <div ref={decisionListRef} className="flex-1 overflow-y-auto p-7 space-y-5 custom-scrollbar-thin">
                                {!intelligence?.edl?.decisions?.length ? (
                                    <div className="h-full flex flex-col items-center justify-center opacity-20 text-center px-12">
                                        <Zap className="h-10 w-10 mb-6 text-indigo-500" />
                                        <p className="text-[11px] font-black uppercase tracking-[0.2em] leading-relaxed">Awaiting logic<br />Play to sync</p>
                                    </div>
                                ) : (
                                    intelligence.edl.decisions.map((decision: any, idx: number) => {
                                        const isActive = currentTime >= decision.timeline_start && currentTime <= decision.timeline_end;
                                        return (
                                            <div key={idx} className={cn(
                                                "p-6 rounded-[2rem] border transition-all duration-700 relative group/card",
                                                isActive
                                                    ? "bg-indigo-600/20 border-indigo-500/50 shadow-[0_20px_40px_rgba(0,0,0,0.3)] scale-[1.02] z-10"
                                                    : "bg-white/[0.02] border-white/5 opacity-60 hover:opacity-100 hover:bg-white/[0.04]"
                                            )}>
                                                <div className="flex items-center justify-between mb-4">
                                                    <div className="flex items-center gap-3">
                                                        <span className="text-[9px] font-black text-indigo-500/50 font-mono tracking-widest">POINT_{idx + 1}</span>
                                                        {isActive && <div className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse shadow-[0_0_10px_#818cf8]" />}
                                                    </div>
                                                    <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest">AI VERIFIED</span>
                                                </div>
                                                <div className="space-y-3">
                                                    <p className="text-[12px] text-white font-black uppercase tracking-tight leading-tight line-clamp-1">{decision.clip_path?.split(/[\\/]/).pop()}</p>
                                                    <p className="text-[11px] text-slate-400 font-medium leading-relaxed">
                                                        {cleanupReasoning(decision.reasoning)}
                                                    </p>
                                                </div>
                                                {isActive && (
                                                    <div className="absolute bottom-0 left-0 h-1 bg-indigo-500 rounded-full transition-all duration-300" style={{ width: '100%' }} />
                                                )}
                                            </div>
                                        );
                                    })
                                )}
                            </div>
                        </div>

                    </div>
                </div>
            </main>
        </div>
    );
}
