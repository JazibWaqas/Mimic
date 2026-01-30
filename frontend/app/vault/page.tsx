"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
    Database,
    Activity,
    MonitorPlay,
    X,
    Sparkles,
    Zap,
    BrainCircuit,
    MonitorStop,
    TrendingUp,
    MessageSquare,
    ChevronDown,
    Plus
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference, Clip } from "@/lib/types";

export type ViewMode = "results" | "references" | "clips";
export type AssetItem = Clip | Reference | Result;

export default function VaultPage() {
    const searchParams = useSearchParams();

    // Data state
    const [clips, setClips] = useState<Clip[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [results, setResults] = useState<Result[]>([]);
    const [selectedItem, setSelectedItem] = useState<AssetItem | null>(null);
    const [viewMode, setViewMode] = useState<ViewMode>("results");
    const [loading, setLoading] = useState(true);
    const [intelLoading, setIntelLoading] = useState(false);
    const [intelligence, setIntelligence] = useState<any>(null);

    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isCabinetOpen, setIsCabinetOpen] = useState(false);

    // Refs
    const videoRef = useRef<HTMLVideoElement>(null);

    // Fetch data
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

    useEffect(() => {
        fetchAllAssets();
    }, []);

    // Auto-select from URL params
    useEffect(() => {
        const filename = searchParams.get("filename");
        const type = searchParams.get("type") as ViewMode | null;

        if (filename && type && (references.length > 0 || results.length > 0)) {
            let item: AssetItem | undefined;
            if (type === "results") {
                item = results.find(r => r.filename === filename);
            } else if (type === "references") {
                item = references.find(r => r.filename === filename);
            } else if (type === "clips") {
                item = clips.find(c => c.filename === filename);
            }
            if (item) {
                setSelectedItem(item);
                setViewMode(type);
            }
        } else if (results.length > 0 && !selectedItem) {
            setSelectedItem(results[0]);
        }
    }, [searchParams, results, references, clips, selectedItem]);

    const handleAssetClick = (item: AssetItem, type: ViewMode) => {
        setSelectedItem(item);
        setViewMode(type);
        setIsCabinetOpen(false);
    };

    // Fetch Intelligence
    useEffect(() => {
        if (!selectedItem) return;

        const fetchIntel = async () => {
            setIntelLoading(true);
            try {
                const data = await api.fetchIntelligence(viewMode, selectedItem.filename);
                setIntelligence(data);
            } catch (err) {
                setIntelligence(null);
            } finally {
                setIntelLoading(false);
            }
        };

        fetchIntel();
    }, [selectedItem, viewMode]);

    const currentAssets = viewMode === "results" ? results : viewMode === "references" ? references : clips;

    const getVideoUrl = (item: AssetItem) => {
        const path = "path" in item ? item.path : (item as any).url;
        return `http://localhost:8000${path}`;
    };

    // Video events
    const handleTimeUpdate = () => {
        if (videoRef.current) setCurrentTime(videoRef.current.currentTime);
    };

    const handleLoadedMetadata = () => {
        if (videoRef.current) setDuration(videoRef.current.duration);
    };

    // Waveform & Metrics Logic
    const waveformData = useMemo(() => {
        if (!intelligence || duration <= 0) return Array.from({ length: 48 }, (_, i) => 15 + Math.abs(Math.sin(i * 0.4) * 40));
        const segments = intelligence.segments || intelligence.edl?.decisions || (Array.isArray(intelligence.edl) ? intelligence.edl : []);
        if (Array.isArray(segments) && segments.length > 0) {
            const data = new Array(48).fill(30);
            segments.forEach((seg: any) => {
                const startT = seg.start || seg.reference_start || seg.timeline_start;
                const endT = seg.end || seg.reference_end || seg.timeline_end;
                const energy = seg.energy || "Medium";
                const startIdx = Math.max(0, Math.floor((startT / duration) * 48));
                const endIdx = Math.min(47, Math.floor((endT / duration) * 48));
                const height = energy === "High" ? 90 : energy === "Medium" ? 60 : 35;
                for (let i = startIdx; i <= endIdx; i++) data[i] = height + (Math.random() * 5);
            });
            return data;
        }
        return Array.from({ length: 48 }, (_, i) => 20 + (i % 8 === 0 ? 40 : 10));
    }, [intelligence, duration]);

    const currentDecision = useMemo(() => {
        if (!intelligence || !intelligence.edl || viewMode !== "results") return null;
        const decisions = intelligence.edl.decisions || [];
        return decisions.find((d: any) => currentTime >= d.timeline_start && currentTime <= d.timeline_end);
    }, [intelligence, currentTime, viewMode]);

    const currentSegment = useMemo(() => {
        if (!intelligence || !intelligence.segments || viewMode !== "references") return null;
        return intelligence.segments.find((s: any) => currentTime >= s.start && currentTime <= s.end);
    }, [intelligence, currentTime, viewMode]);

    if (loading) {
        return (
            <div className="h-screen flex items-center justify-center bg-[#020306]">
                <div className="text-cyan-400 text-[10px] font-black uppercase tracking-[0.5em] animate-pulse">Initializing Lab_</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#020306] text-slate-100 flex flex-col overflow-hidden">
            {/* Compact Header */}
            <header className="h-14 flex items-center justify-between px-10 bg-black/60 backdrop-blur-xl border-b border-white/5 shrink-0 z-[100]">
                <div className="flex items-center gap-3">
                    <div className="h-6 w-6 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                        <Activity className="h-3.5 w-3.5 text-indigo-400" />
                    </div>
                    <h1 className="text-[11px] font-black text-white uppercase tracking-[0.3em]">Vault // Edit Review</h1>
                </div>

                <div className="flex items-center bg-black/40 p-1 rounded-lg border border-white/5">
                    {(["results", "references", "clips"] as ViewMode[]).map(mode => (
                        <button
                            key={mode}
                            onClick={() => setViewMode(mode)}
                            className={cn(
                                "relative px-4 py-1.5 rounded-md text-[9px] font-black uppercase tracking-[0.2em] transition-all duration-300",
                                viewMode === mode ? "text-cyan-400 bg-cyan-500/10" : "text-slate-500 hover:text-slate-300"
                            )}
                        >
                            {mode}
                        </button>
                    ))}
                </div>
            </header>

            {/* Specimen Cabinet (Library Drawer) */}
            <div className={cn(
                "fixed inset-y-0 left-0 w-80 bg-[#05060a]/95 backdrop-blur-2xl border-r border-white/10 z-[150] transform transition-transform duration-500 flex flex-col shadow-2xl",
                isCabinetOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-cyan-400">
                        <Database className="w-4 h-4" />
                        <h2 className="text-sm font-black uppercase tracking-[0.3em]">Library</h2>
                    </div>
                    <button onClick={() => setIsCabinetOpen(false)} className="p-1 hover:bg-white/10 rounded-full transition-all">
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest px-2">{viewMode} Available</p>
                    {currentAssets.map((res) => (
                        <div
                            key={res.filename}
                            onClick={() => handleAssetClick(res, viewMode)}
                            className={cn(
                                "p-3 rounded-xl border transition-all cursor-pointer group/item",
                                selectedItem?.filename === res.filename ? "bg-cyan-500/10 border-cyan-500/30" : "bg-white/5 border-white/5 hover:border-white/20"
                            )}
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-20 h-12 rounded-lg bg-black relative overflow-hidden shrink-0 border border-white/10">
                                    <video src={getVideoUrl(res)} className="w-full h-full object-cover opacity-60" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-xs font-black text-white uppercase truncate">{res.filename}</p>
                                    <p className="text-[9px] font-medium text-slate-500 uppercase tracking-widest">ID: {res.filename.split('_').pop()?.split('.')[0]}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {isCabinetOpen && <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[140]" onClick={() => setIsCabinetOpen(false)} />}

            {/* Compact Asset Strip */}
            <div className="bg-[#020306] border-b border-white/5 py-4 shrink-0 overflow-hidden">
                <div className="max-w-[1400px] mx-auto px-10">

                    <div className="flex gap-4 overflow-x-auto pb-2 custom-scrollbar">
                        {currentAssets.slice(0, 8).map((item, idx) => {
                            const isSelected = selectedItem?.filename === item.filename;
                            const isReference = viewMode === "references" || (viewMode === "results" && idx === 0);

                            return (
                                <div
                                    key={idx}
                                    onClick={() => handleAssetClick(item, viewMode)}
                                    className="shrink-0 w-44 group cursor-pointer"
                                >
                                    <div
                                        className={cn(
                                            "relative w-full aspect-[16/11] rounded-lg overflow-hidden border transition-all duration-500",
                                            isSelected
                                                ? "border-cyan-400 bg-[#0a0c10]"
                                                : "border-white/10 bg-[#0a0c14] opacity-60 hover:opacity-80"
                                        )}
                                    >
                                        <video src={getVideoUrl(item)} className="w-full h-full object-cover" />
                                        <div className={cn(
                                            "absolute bottom-1 right-1 px-1 py-0.5 rounded text-[7px] font-black uppercase",
                                            isSelected ? "bg-cyan-500 text-white" : "bg-black/60 text-white"
                                        )}>
                                            {item.filename}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            <main className="max-w-[1400px] mx-auto px-10 py-8 grid grid-cols-[300px_1fr_400px] gap-10 flex-1 overflow-hidden">
                {/* LEFT: Edit Structure */}
                <aside className="space-y-6">
                    <div className="glass-premium rounded-2xl p-6 border-l-2 border-l-indigo-500/30 relative overflow-hidden group">
                        <div className="flex items-center gap-2 mb-5">
                            <TrendingUp className="w-4 h-4 text-indigo-400" />
                            <h3 className="text-xs font-black text-slate-300 uppercase tracking-[0.4em]">Edit Structure</h3>
                        </div>
                        <div className="space-y-5 relative z-10">
                            <div className="flex flex-col gap-2 border-b border-white/5 pb-3">
                                <span className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Temporal & Rhythmic Analysis</span>
                                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tight leading-relaxed">
                                    Detected increasing emotional intensity toward peak window (8.2s–12.5s)
                                </p>
                            </div>
                            <div className="flex justify-between items-end border-b border-white/5 pb-3">
                                <span className="text-xs font-black text-slate-500 uppercase tracking-widest">Beat Bias</span>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-lg font-black text-cyan-400">{intelligence?.bpm || 128}</span>
                                    <span className="text-[10px] text-cyan-900 font-black uppercase">BPM</span>
                                </div>
                            </div>

                            <div className="mt-6">
                                <div className="h-16 flex items-center gap-1.5 opacity-80">
                                    {[30, 45, 80, 100, 70, 90, 50, 40].map((h, i) => (
                                        <div
                                            key={i}
                                            className={cn(
                                                "flex-1 rounded-sm border transition-all duration-700",
                                                i === 3 ? "bg-cyan-500 border-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.5)]" : "bg-indigo-500/20 border-indigo-500/10"
                                            )}
                                            style={{ height: `${h}%` }}
                                        />
                                    ))}
                                </div>
                                <div className="mt-3 text-[9px] text-center font-black text-slate-600 uppercase tracking-widest">Structural Intensity Map</div>
                            </div>
                        </div>
                    </div>

                    {/* RECOMMENDED ACTIONS */}
                    <div className="bg-[#0a0c14]/60 border border-white/5 rounded-2xl p-5 backdrop-blur-sm">
                        <div className="flex items-center gap-3 mb-4">
                            <Sparkles className="w-4 h-4 text-indigo-400" />
                            <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em]">Recommended Action</h3>
                        </div>
                        <p className="text-[10px] font-bold text-slate-300 uppercase tracking-tight leading-relaxed mb-5 border-l-2 border-indigo-500/30 pl-4">
                            Add 2–3 clips with fast camera motion to reinforce emotional climax.
                        </p>
                        <button
                            onClick={() => toast.success("Re-generating video with editorial insights...")}
                            className="w-full h-14 rounded-xl bg-indigo-600 text-white font-black text-[11px] uppercase tracking-[0.3em] shadow-[0_20px_40px_rgba(79,102,241,0.3)] hover:scale-[1.02] transition-all relative group overflow-hidden border border-indigo-500/40"
                        >
                            <span className="relative z-10">Remake Video</span>
                            <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        </button>
                        <p className="text-[9px] text-center text-slate-600 uppercase tracking-widest mt-3 font-black">Applies editorial insights automatically</p>
                    </div>
                </aside>

                {/* CENTER: Video Hero */}
                <section className="flex flex-col items-center gap-6">
                    <div className="w-[400px] flex items-center justify-between px-1">
                        <div className="px-4 py-1.5 bg-black/40 border border-white/10 rounded-full">
                            <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.4em]">
                                {viewMode === "results" ? "Final Output (Locked)" : "Reference Specimen"}
                            </span>
                        </div>
                        <button className="flex items-center gap-3 px-5 py-2 rounded-full bg-indigo-500/15 border border-indigo-500/40 hover:bg-indigo-500/25 transition-all group shadow-[0_0_15px_rgba(79,102,241,0.2)]">
                            <div className="h-2 w-2 rounded-full bg-indigo-400 group-hover:bg-cyan-400 transition-colors"></div>
                            <span className="text-[10px] font-black text-indigo-200 uppercase tracking-[0.2em] leading-none">Add Styling</span>
                        </button>
                    </div>

                    <div className="w-[400px] h-[710px] rounded-2xl overflow-hidden border border-white/10 bg-black shadow-2xl relative group ring-1 ring-white/5 hover:ring-indigo-500/30 transition-all duration-700">
                        {selectedItem ? (
                            <video
                                ref={videoRef}
                                src={getVideoUrl(selectedItem)}
                                onTimeUpdate={handleTimeUpdate}
                                onLoadedMetadata={handleLoadedMetadata}
                                controls
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center bg-black/20">
                                <MonitorPlay className="w-16 h-16 mb-4 opacity-10" />
                                <p className="text-sm font-black uppercase tracking-[0.6em] text-slate-500">No Selection</p>
                            </div>
                        )}



                    </div>

                    {/* Mini Timeline Control */}
                    <div className="glass-premium w-[400px] rounded-2xl p-4 border-white/10 bg-black/40 shadow-xl">
                        <div className="flex items-center justify-between mb-3 px-1">
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none">Rhythmic Consistency</span>
                            <span className="text-[10px] font-black text-cyan-400 uppercase tracking-widest leading-none">Sync: Frame-Locked</span>
                        </div>
                        <div className="h-12 flex items-end gap-[2.5px] relative pt-2">
                            {waveformData.map((h, i) => {
                                const isPeak = h > 85;
                                return (
                                    <div
                                        key={i}
                                        className={cn(
                                            "flex-1 transition-all duration-300 rounded-sm cursor-pointer",
                                            duration > 0 && i <= (currentTime / duration) * 48
                                                ? (isPeak ? "bg-[#ff007f] shadow-[0_0_15px_#ff007f]" : "bg-[#00d4ff] shadow-[0_0_10px_#00d4ff]")
                                                : "bg-white/5 hover:bg-white/10"
                                        )}
                                        style={{ height: `${h}%` }}
                                    />
                                );
                            })}
                        </div>
                        <div className="text-[9px] text-center text-slate-600 uppercase tracking-[0.4em] mt-4 font-black">
                            Scrub to analyze temporal deltas
                        </div>
                    </div>
                </section>

                {/* RIGHT: Telemetry-Inspired Intelligence Panel */}
                <aside className="space-y-4 pr-2">
                    {/* EDITORIAL DECISIONS - Top Priority */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 px-2">
                            <div className="h-1 w-8 bg-gradient-to-r from-cyan-500 to-transparent rounded-full" />
                            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em]">Editorial Decisions</h3>
                        </div>

                        {/* SEG_15: Peak Moment */}
                        <div className={cn(
                            "bg-[#0a0c14]/60 border rounded-2xl p-5 transition-all duration-700 backdrop-blur-sm",
                            (currentTime >= 8.2 && currentTime <= 12.5) || viewMode !== "results"
                                ? "border-[#ff007f]/40 shadow-[0_0_30px_rgba(255,0,127,0.15)] scale-[1.01]"
                                : "border-white/5 opacity-50"
                        )}>
                            <div className="flex items-center justify-between mb-5">
                                <div className="flex items-center gap-3">
                                    <div className={cn("h-2 w-2 rounded-full bg-[#ff007f] shadow-[0_0_10px_#ff007f]", currentTime >= 8.2 && currentTime <= 12.5 && "animate-pulse")} />
                                    <span className="text-[10px] font-black text-[#ff007f] uppercase tracking-[0.25em]">SEG_15: Peak Moment</span>
                                </div>
                                <span className="text-[9px] font-black text-white bg-[#ff007f]/20 px-3 py-1 rounded-full border border-[#ff007f]/30 uppercase tracking-wider">Critical</span>
                            </div>
                            <div className="flex gap-5">
                                <div className="w-24 h-24 rounded-xl bg-black border border-[#ff007f]/30 overflow-hidden shrink-0 shadow-inner">
                                    <video src={selectedItem ? getVideoUrl(selectedItem) : ""} className="w-full h-full object-cover" />
                                </div>
                                <div className="min-w-0 flex-1 flex flex-col justify-center">
                                    <p className="text-[11px] font-black text-white uppercase tracking-tight truncate mb-3">
                                        {selectedItem?.filename}
                                    </p>
                                    <p className="text-[10px] text-slate-300 font-bold uppercase leading-tight mb-1">Matches reference intensity</p>
                                    <p className="text-[9px] text-slate-500 uppercase leading-snug font-medium">Best available peak candidate</p>
                                </div>
                            </div>
                        </div>

                        {/* SEG_14: System Build */}
                        <div className={cn(
                            "bg-[#0a0c14]/40 border rounded-xl p-5 transition-all duration-700",
                            currentTime >= 4 && currentTime < 8.2
                                ? "border-indigo-500/40 shadow-[0_0_20px_rgba(79,102,241,0.1)] opacity-100"
                                : "border-white/5 opacity-40"
                        )}>
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">SEG_14: System Build</span>
                                <span className="text-[9px] font-black text-indigo-400 uppercase tracking-wider">Strong Match</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <TrendingUp className="h-4 w-4 text-emerald-500" />
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Supports emotional build</span>
                            </div>
                        </div>
                    </div>

                    {/* AI INSIGHT - Compact Summary */}
                    <div className="bg-[#0a0c14]/60 border border-white/5 rounded-2xl p-5 backdrop-blur-sm">
                        <div className="flex items-center gap-3 mb-4">
                            <BrainCircuit className="w-4 h-4 text-cyan-400" />
                            <h3 className="text-[10px] font-black text-cyan-400 uppercase tracking-[0.3em]">AI Insight</h3>
                        </div>
                        <div className="space-y-4">
                            <div className="border-l-2 border-cyan-500/30 pl-4">
                                <p className="text-[10px] font-bold text-slate-300 uppercase tracking-tight leading-relaxed">
                                    Edit maintained rhythmic consistency but lacked high-energy clips during peak window (8.2s–12.5s).
                                </p>
                            </div>
                            <div className="border-l-2 border-[#ff007f]/30 pl-4">
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight leading-relaxed">
                                    Clip library skewed toward calm shots, limiting peak amplification.
                                </p>
                            </div>
                        </div>
                    </div>




                </aside>
            </main>
        </div>
    );
}
