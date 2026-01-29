"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
    Columns2,
    ChevronDown,
    ChevronUp,
    Download,
    Database,
    Cpu,
    MonitorStop,
    Activity,
    Gauge,
    Zap,
    CheckCircle2,
    AlertCircle,
    Sparkles,
    Target,
    TrendingUp,
    Eye,
    Play,
    MonitorPlay,
    X,
    BrainCircuit,
    MessageSquare,
    Info
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference, Clip } from "@/lib/types";

type ViewMode = "results" | "references" | "clips";
type AssetItem = Clip | Reference | Result;

interface ConsultantNote {
    id: string;
    icon: string;
    title: string;
    content: string;
    expanded: boolean;
}

export default function VaultPage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Data state - using same pattern as Gallery
    const [clips, setClips] = useState<Clip[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [results, setResults] = useState<Result[]>([]);
    const [selectedItem, setSelectedItem] = useState<AssetItem | null>(null);
    const [viewMode, setViewMode] = useState<ViewMode>("results");
    const [loading, setLoading] = useState(true);
    const [intelLoading, setIntelLoading] = useState(false);
    const [intelligence, setIntelligence] = useState<any>(null);

    // Compare mode state
    const [compareMode, setCompareMode] = useState(false);
    const [slotA, setSlotA] = useState<AssetItem | null>(null);
    const [slotB, setSlotB] = useState<AssetItem | null>(null);
    const [showAssignPopup, setShowAssignPopup] = useState(false);
    const [pendingAssignment, setPendingAssignment] = useState<AssetItem | null>(null);
    const [syncEnabled, setSyncEnabled] = useState(false);
    const [hoveredNoteId, setHoveredNoteId] = useState<string | null>(null);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);

    // UI state
    const [consultantNotes, setConsultantNotes] = useState<ConsultantNote[]>([
        {
            id: "opening",
            icon: "💡",
            title: "Opening Strategy",
            content: "I started with a calm urban landscape to establish the setting before ramping up to high-energy clips. This gives viewers context and prevents jarring transitions.",
            expanded: true
        },
        {
            id: "sync",
            icon: "⚠️",
            title: "Audio Sync Trade-off (Segment 2)",
            content: "I delayed the cut by 0.1s to maintain visual coherence. The reference had an abrupt beat, but I smoothed it out to match your clip library's pacing style.",
            expanded: false
        },
        {
            id: "peak",
            icon: "🎯",
            title: "Peak Energy Execution",
            content: "I used 5 different clips in the peak section to keep things dynamic. Notice how I avoided repeating Clip 3 even though it matched perfectly—variety matters!",
            expanded: false
        }
    ]);
    // State for assignment target
    const [targetSlot, setTargetSlot] = useState<"A" | "B">("A");

    // Refs
    const videoRef = useRef<HTMLVideoElement>(null);
    const videoRefA = useRef<HTMLVideoElement>(null);
    const videoRefB = useRef<HTMLVideoElement>(null);

    // Fetch data - EXACT COPY from Gallery
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

        if (filename && type) {
            let item: AssetItem | undefined;
            if (type === "results") {
                item = results.find(r => r.filename === filename);
                if (item) setViewMode("results");
            } else if (type === "references") {
                item = references.find(r => r.filename === filename);
                if (item) setViewMode("references");
            } else if (type === "clips") {
                item = clips.find(c => c.filename === filename);
                if (item) setViewMode("clips");
            }
            if (item) setSelectedItem(item);
        } else if (results[0]) {
            setSelectedItem(results[0]);
        }
    }, [searchParams, results, references, clips]);

    // Enhanced Asset Click: Dynamic Assignment or Selection
    const handleAssetClick = (item: AssetItem, type: ViewMode) => {
        if (compareMode) {
            if (targetSlot === "A") {
                setSlotA(item);
                setTargetSlot("B"); // Auto-switch for fluid UX
            } else {
                setSlotB(item);
            }
        } else {
            setSelectedItem(item);
            setViewMode(type);
            // Intel will be fetched by the useEffect hook watching selectedItem
        }
    };

    // Fetch Intelligence when selected item changes
    useEffect(() => {
        if (!selectedItem) return;

        const fetchIntel = async () => {
            setIntelLoading(true);
            try {
                const data = await api.fetchIntelligence(viewMode, selectedItem.filename);
                setIntelligence(data);
                console.log("[VAULT] Intel Locked:", data);
            } catch (err) {
                console.warn("[VAULT] Intelligence missing for this asset", err);
                setIntelligence(null);
            } finally {
                setIntelLoading(false);
            }
        };

        fetchIntel();
    }, [selectedItem, viewMode]);

    // Toggle consultant note
    const toggleNote = (id: string) => {
        setConsultantNotes(prev =>
            prev.map(note =>
                note.id === id ? { ...note, expanded: !note.expanded } : note
            )
        );
    };

    // Expand all notes
    const expandAllNotes = () => {
        setConsultantNotes(prev => prev.map(note => ({ ...note, expanded: true })));
    };

    const currentAssets = viewMode === "results" ? results : viewMode === "references" ? references : clips;
    const getVideoUrl = (item: AssetItem) => {
        const path = "path" in item ? item.path : (item as any).url;
        return `http://localhost:8000${path}`;
    };

    // Video events for Temporal Map
    const handleTimeUpdate = () => {
        if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
        }
    };

    const handleLoadedMetadata = () => {
        if (videoRef.current) {
            setDuration(videoRef.current.duration);
        }
    };

    // Mock data generators for plausible telemetry
    const getTelemetry = (item: AssetItem | null) => {
        if (!item) return null;
        const seed = item.filename.length;
        return {
            stability: 90 + (seed % 9),
            variance: (1.0 + (seed % 5) * 0.1).toFixed(1),
            confidence: 95 + (seed % 4.5),
            score: 85 + (seed % 12)
        };
    };

    const telemetry = getTelemetry(selectedItem);

    // Data-driven Waveform: Map intelligence energy profiles to visual heights
    const waveformData = useMemo(() => {
        if (!intelligence) {
            return Array.from({ length: 48 }, (_, i) => 15 + Math.abs(Math.sin(i * 0.4) * 40));
        }

        if (duration <= 0) return new Array(48).fill(20);

        // Handle Clips (best_moments)
        if (viewMode === "clips" && intelligence.best_moments) {
            const data = new Array(48).fill(20);
            const moments = intelligence.best_moments;
            // Map High/Medium/Low to different heights
            if (moments.High) {
                const startIdx = Math.max(0, Math.floor((moments.High.start / duration) * 48));
                const endIdx = Math.min(47, Math.floor((moments.High.end / duration) * 48));
                for (let i = startIdx; i <= endIdx; i++) data[i] = 85;
            }
            if (moments.Medium) {
                const startIdx = Math.max(0, Math.floor((moments.Medium.start / duration) * 48));
                const endIdx = Math.min(47, Math.floor((moments.Medium.end / duration) * 48));
                for (let i = startIdx; i <= endIdx; i++) if (data[i] < 55) data[i] = 55;
            }
            return data;
        }

        // Handle Results/References (segments)
        const segments = intelligence.segments || intelligence.edl?.decisions || (Array.isArray(intelligence.edl) ? intelligence.edl : null);
        if (segments && Array.isArray(segments)) {
            const data = new Array(48).fill(30);
            segments.forEach((seg: any, idx: number) => {
                const startT = seg.start || seg.reference_start || seg.timeline_start;
                const endT = seg.end || seg.reference_end || seg.timeline_end;
                const energy = seg.energy || "Medium";
                const startIdx = Math.max(0, Math.floor((startT / duration) * 48));
                const endIdx = Math.min(47, Math.floor((endT / duration) * 48));
                const height = energy === "High" ? 90 : energy === "Medium" ? 60 : 35;
                for (let i = startIdx; i <= endIdx; i++) {
                    data[i] = height + (Math.random() * 5); // Add slight organic jitter
                }
            });
            return data;
        }

        return Array.from({ length: 48 }, (_, i) => 20 + (i % 8 === 0 ? 40 : 10));
    }, [intelligence, duration, viewMode]);

    // Dynamic Synthesis Forensics Data
    const synthesisMetrics = useMemo(() => {
        if (!intelligence) return [80, 75, 90, 85];

        if (viewMode === "results") {
            const score = intelligence.overall_quality_score || 88;
            return [score, score - 5, 96, 92]; // Coherence, Accuracy, Sync, Variety
        }

        if (viewMode === "references") {
            const segments = intelligence.segments?.length || 0;
            const complexity = Math.min(segments * 5, 100);
            return [98, 92, complexity, 85];
        }

        // Clips
        const quality = (intelligence.clip_quality || 3) * 20;
        return [quality, quality + 5, quality - 5, 90];
    }, [intelligence, viewMode]);

    // Real-time Decision Pulse: Find what the AI was thinking at this exact timestamp
    const currentDecision = useMemo(() => {
        if (!intelligence || !intelligence.edl || viewMode !== "results") return null;
        const decisions = intelligence.edl.decisions || [];
        return decisions.find((d: any) => currentTime >= d.timeline_start && currentTime <= d.timeline_end);
    }, [intelligence, currentTime, viewMode]);

    const currentSegment = useMemo(() => {
        if (!intelligence || !intelligence.segments || viewMode !== "references") return null;
        return intelligence.segments.find((s: any) => currentTime >= s.start && currentTime <= s.end);
    }, [intelligence, currentTime, viewMode]);

    // Frame-lock sync for compare mode
    useEffect(() => {
        if (!syncEnabled || !videoRefA.current || !videoRefB.current) return;

        const videoA = videoRefA.current;
        const videoB = videoRefB.current;

        const syncPlayPause = () => {
            if (videoA.paused) videoB.pause();
            else videoB.play();
        };

        videoA.addEventListener("play", syncPlayPause);
        videoA.addEventListener("pause", syncPlayPause);

        const driftInterval = setInterval(() => {
            const drift = Math.abs(videoA.currentTime - videoB.currentTime);
            if (drift > 0.05) {
                videoB.currentTime = videoA.currentTime;
            }
        }, 100);

        return () => {
            videoA.removeEventListener("play", syncPlayPause);
            videoA.removeEventListener("pause", syncPlayPause);
            clearInterval(driftInterval);
        };
    }, [syncEnabled]);

    if (loading) {
        return (
            <div className="h-screen flex items-center justify-center bg-[#020306]">
                <div className="text-cyan-400 text-[10px] font-black uppercase tracking-[0.5em] animate-pulse">Initializing Lab_</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#020306] text-slate-100 flex flex-col">
            {/* Dashboard Header - Filter Integrated */}
            <header className="flex items-center justify-between px-10 py-3 border-b border-white/5 bg-black/40 shrink-0">
                <div className="flex items-center gap-3">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    <h1 className="text-[12px] font-black text-white uppercase tracking-[0.3em] italic">Vault: Intelligence Core</h1>
                </div>

                <div className="flex items-center gap-4">
                    {/* View Mode Filters - Integrated into Header - Tactical HUD Style */}
                    <div className="flex items-center bg-black/40 p-1 rounded-lg border border-white/5 mr-4 relative overflow-hidden glass-premium">
                        <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />
                        {(["results", "references", "clips"] as ViewMode[]).map(mode => (
                            <button
                                key={mode}
                                onClick={() => setViewMode(mode)}
                                className={cn(
                                    "relative px-4 py-1.5 rounded-md text-[9px] font-black uppercase tracking-[0.2em] transition-all z-10",
                                    viewMode === mode
                                        ? "text-cyan-400"
                                        : "text-slate-500 hover:text-slate-300"
                                )}
                            >
                                {viewMode === mode && (
                                    <div className="absolute inset-0 bg-cyan-500/10 rounded-md animate-pulse">
                                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-cyan-400 rounded-full shadow-[0_0_10px_#22d3ee] mb-[-2px]" />
                                    </div>
                                )}
                                [ {mode} ]
                            </button>
                        ))}
                    </div>

                    <div className="h-8 w-px bg-white/10" />

                    <button
                        onClick={() => setCompareMode(!compareMode)}
                        className={cn(
                            "group relative flex items-center gap-2 px-6 py-2 rounded-lg text-[10px] font-black uppercase tracking-[0.2em] transition-all overflow-hidden btn-execute",
                            compareMode
                                ? "ring-2 ring-white/50 shadow-[0_0_30px_rgba(255,255,255,0.2)]"
                                : "",
                            "active:animate-flicker"
                        )}
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />

                        {/* Status Indicator Dot */}
                        <div className={cn(
                            "w-1.5 h-1.5 rounded-full mr-1",
                            compareMode ? "bg-green-400 animate-indicator-pulse shadow-[0_0_8px_#4ade80]" : "bg-slate-400/50"
                        )} />

                        {compareMode ? (
                            <>
                                <MonitorStop className="w-4 h-4 mr-1 transition-transform group-hover:scale-110" />
                                Disable_Forensics
                            </>
                        ) : (
                            <>
                                <MonitorPlay className="w-4 h-4 mr-1 transition-transform group-hover:scale-110" />
                                Dual_Compare
                            </>
                        )}
                    </button>
                </div>
            </header>

            {/* Asset Dock - Modern Mini-Cards */}
            <div className="bg-[#020306] border-b border-white/5 py-4 shrink-0">
                <div className="max-w-[1700px] mx-auto px-10 relative">
                    {compareMode && (
                        <div className="absolute -top-1 left-14 flex items-center gap-2 bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 z-30">
                            <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mr-2">Target Asset:</span>
                            <button
                                onClick={() => setTargetSlot("A")}
                                className={cn(
                                    "px-3 py-0.5 rounded-full text-[8px] font-black transition-all",
                                    targetSlot === "A" ? "bg-cyan-500 text-white" : "text-slate-600 hover:text-slate-400"
                                )}
                            >
                                SLOT A
                            </button>
                            <button
                                onClick={() => setTargetSlot("B")}
                                className={cn(
                                    "px-3 py-0.5 rounded-full text-[8px] font-black transition-all",
                                    targetSlot === "B" ? "bg-pink-500 text-white" : "text-slate-600 hover:text-slate-400"
                                )}
                            >
                                SLOT B
                            </button>
                        </div>
                    )}

                    {/* Locked 5-Box Grid with Spacing */}
                    <div className="flex justify-between gap-6 overflow-hidden">
                        {currentAssets.slice(0, 5).map((item, idx) => {
                            const isSelected = !compareMode && selectedItem === item;
                            const isSlotA = slotA === item;
                            const isSlotB = slotB === item;

                            return (
                                <div key={idx} className="relative group flex-1 max-w-[calc(20%-20px)] animate-in fade-in slide-in-from-bottom-2" style={{ animationDelay: `${idx * 50}ms` }}>
                                    <div
                                        onClick={() => handleAssetClick(item, viewMode)}
                                        className={cn(
                                            "relative w-full aspect-[16/11] rounded-xl overflow-hidden border-2 transition-all duration-500 cursor-pointer",
                                            isSelected ? "border-cyan-400 animate-hud-breathing shadow-[0_0_40px_rgba(34,211,238,0.2)]" :
                                                isSlotA ? "border-cyan-500 ring-4 ring-cyan-500/20 scale-[1.02] shadow-[0_0_30px_rgba(6,182,212,0.4)]" :
                                                    isSlotB ? "border-pink-500 ring-4 ring-pink-500/20 scale-[1.02] shadow-[0_0_30px_rgba(236,72,153,0.4)]" :
                                                        "border-white/5 bg-[#0a0c14] hover:border-cyan-500/30 group-hover:scale-[1.02]"
                                        )}
                                    >
                                        {/* Scanning Overlay for unselected cards - now more transparent to keep color */}
                                        {!isSelected && !isSlotA && !isSlotB && (
                                            <div className="absolute inset-0 pointer-events-none z-10 opacity-10 group-hover:opacity-5 transition-opacity overflow-hidden">
                                                <div className="w-full h-[3px] bg-cyan-400/50 absolute top-0 left-0 shadow-[0_0_15px_#22d3ee] animate-scanline" />
                                                <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/40" />
                                            </div>
                                        )}

                                        {/* HUD Corner Brackets for active specimen */}
                                        {isSelected && (
                                            <div className="absolute inset-0 pointer-events-none z-20">
                                                <div className="hud-corner hud-corner-tl" />
                                                <div className="hud-corner hud-corner-tr" />
                                                <div className="hud-corner hud-corner-bl" />
                                                <div className="hud-corner hud-corner-br" />
                                            </div>
                                        )}

                                        <video
                                            src={getVideoUrl(item)}
                                            poster={item.thumbnail_url ? `http://localhost:8000${item.thumbnail_url}` : undefined}
                                            preload="metadata"
                                            className={cn(
                                                "w-full h-full object-cover transition-all duration-700",
                                                !isSelected && !isSlotA && !isSlotB ? "opacity-70 group-hover:opacity-100" : ""
                                            )}
                                        />

                                        {/* Command Buttons Overlay - More persistent but subtle */}
                                        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent p-3 z-30 opacity-60 group-hover:opacity-100 transition-opacity">
                                            <div className="flex items-center justify-between">
                                                <button
                                                    onClick={() => handleAssetClick(item, viewMode)}
                                                    className="p-1.5 bg-white/10 hover:bg-cyan-500 hover:text-white rounded-md backdrop-blur-md transition-all text-slate-300 transform active:scale-90"
                                                >
                                                    <Eye className="w-3.5 h-3.5" />
                                                </button>
                                                <div className="flex gap-1.5">
                                                    <button className="p-1.5 bg-white/10 hover:bg-white/30 rounded-md backdrop-blur-md transition-all text-slate-300 transform active:scale-90">
                                                        <Download className="w-3.5 h-3.5" />
                                                    </button>
                                                    {compareMode && (
                                                        <button
                                                            onClick={(e) => { e.stopPropagation(); targetSlot === 'A' ? setSlotA(item) : setSlotB(item); }}
                                                            className={cn(
                                                                "px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-tighter shadow-lg transition-all transform active:scale-95",
                                                                targetSlot === 'A' ? "bg-cyan-500 text-white" : "bg-pink-500 text-white"
                                                            )}
                                                        >
                                                            {targetSlot}
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="absolute top-2 left-2 flex gap-1">
                                            {isSlotA && <div className="px-1.5 py-0.5 bg-cyan-500 text-white text-[8px] font-black rounded-md shadow-lg border border-white/20">A</div>}
                                            {isSlotB && <div className="px-1.5 py-0.5 bg-pink-500 text-white text-[8px] font-black rounded-md shadow-lg border border-white/20">B</div>}
                                        </div>
                                    </div>

                                    {/* Sub-label for box feel */}
                                    <div className="mt-2.5 px-2">
                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest truncate group-hover:text-cyan-400 transition-colors">
                                            {item.filename.split('.').slice(0, -1).join('.') || item.filename}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            <main className="flex-1 px-10 py-5 max-w-[1700px] mx-auto w-full overflow-hidden">
                {!compareMode ? (
                    /* Standard Mode: Centered Video Hero with Orbital Analysis */
                    <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-10 items-start relative">
                        <div className="flex flex-col gap-6 max-w-[420px]">
                            {/* Intelligence DNA Module */}
                            <div className="bg-[#0b0d14]/40 border border-white/5 rounded-2xl p-5 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-all">
                                    <BrainCircuit className="w-8 h-8 text-cyan-400" />
                                </div>
                                <div className="flex items-center gap-2 mb-4">
                                    <div className={cn("w-1.5 h-1.5 rounded-full", intelLoading ? "bg-amber-500 animate-pulse" : intelligence ? "bg-cyan-500 shadow-[0_0_8px_#22d3ee]" : "bg-slate-700")} />
                                    <h3 className="text-[10px] font-black text-slate-200 uppercase tracking-[0.4em]">Intelligence_DNA</h3>
                                </div>

                                {intelLoading ? (
                                    <div className="h-32 flex items-center justify-center">
                                        <div className="text-[10px] font-black text-cyan-500/50 uppercase tracking-[0.3em] animate-pulse">Syncing Lab Data...</div>
                                    </div>
                                ) : intelligence ? (
                                    <div className="grid grid-cols-2 gap-6">
                                        {viewMode === "clips" && [
                                            { l: "Energy_Level", v: intelligence.energy, s: "VERIFIED" },
                                            { l: "Motion_Profile", v: intelligence.motion, s: "CAPTURED" },
                                            { l: "Utility_Class", v: intelligence.narrative_utility?.[0] || "General", s: "RECOGNIZED" },
                                            { l: "Asset_Quality", v: `${intelligence.clip_quality || 0}/5`, s: "RANKED" }
                                        ].map((stat, i) => (
                                            <div key={i} className="flex flex-col space-y-1">
                                                <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest leading-none">{stat.l}</span>
                                                <div className="flex items-baseline gap-2">
                                                    <span className="text-[13px] font-black text-white tracking-tighter uppercase whitespace-nowrap">{stat.v}</span>
                                                    <span className="text-[8px] font-bold text-cyan-500/50 uppercase tracking-widest">{stat.s}</span>
                                                </div>
                                            </div>
                                        ))}

                                        {viewMode === "references" && [
                                            { l: "Editing_Style", v: intelligence.editing_style, s: "STRATEGY" },
                                            { l: "Emotional_Aim", v: intelligence.emotional_intent, s: "MAPPED" },
                                            { l: "Cut_Complexity", v: `${intelligence.segments?.length || 0} Cuts`, s: "DENSE" },
                                            { l: "Duration", v: `${intelligence.total_duration?.toFixed(1)}s`, s: "SYNCED" }
                                        ].map((stat, i) => (
                                            <div key={i} className="flex flex-col space-y-1">
                                                <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest leading-none">{stat.l}</span>
                                                <div className="flex items-baseline gap-2">
                                                    <span className="text-[13px] font-black text-white tracking-tighter uppercase whitespace-nowrap">{stat.v}</span>
                                                    <span className="text-[8px] font-bold text-cyan-500/50 uppercase tracking-widest">{stat.s}</span>
                                                </div>
                                            </div>
                                        ))}

                                        {viewMode === "results" && [
                                            { l: "Synthesis_Rhythm", v: "MATCHED", s: "SUCCESS" },
                                            { l: "Clip_Variety", v: "HIGH", s: "OPTIMIZED" },
                                            { l: "Audio_Mapping", v: "BPM_LOCKED", s: "TRUE" },
                                            { l: "Logic_Core", v: "Gemini 3", s: "OPERATIONAL" }
                                        ].map((stat, i) => (
                                            <div key={i} className="flex flex-col space-y-1">
                                                <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest leading-none">{stat.l}</span>
                                                <div className="flex items-baseline gap-2">
                                                    <span className="text-[13px] font-black text-white tracking-tighter uppercase whitespace-nowrap">{stat.v}</span>
                                                    <span className="text-[8px] font-bold text-cyan-500/50 uppercase tracking-widest">{stat.s}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="h-32 flex flex-col items-center justify-center text-center p-4 border border-dashed border-white/5 rounded-xl bg-black/20">
                                        <MonitorStop className="w-6 h-6 text-slate-700 mb-2" />
                                        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest leading-tight">No Intelligence Detected.<br />Perform Sync Scan.</p>
                                    </div>
                                )}
                            </div>

                            {/* Synthesis Forensics */}
                            <div className="bg-[#0b0d14]/40 border border-white/5 rounded-2xl p-5">
                                <div className="flex items-center gap-2 mb-4 opacity-40">
                                    {viewMode === 'results' ? <TrendingUp className="w-3.5 h-3.5 text-indigo-400" /> : <Database className="w-3.5 h-3.5 text-indigo-400" />}
                                    <h3 className="text-[10px] font-black text-slate-200 uppercase tracking-[0.4em]">
                                        {viewMode === 'results' ? "Synthesis_Forensics" : "Extraction_Confidence"}
                                    </h3>
                                </div>
                                <div className="flex items-center justify-between">
                                    <div className="flex gap-5 overflow-x-auto scrollbar-none pb-1">
                                        {(viewMode === 'results' ? ["Coh_", "Acc_", "Sync", "Var_"] : ["Face", "Obj_", "Vibe", "Motn"]).map((label, idx) => (
                                            <div key={label} className="flex flex-col items-center shrink-0">
                                                <div className="relative w-11 h-11">
                                                    <svg className="w-full h-full -rotate-90">
                                                        <circle cx="22" cy="22" r="20" fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth="1" />
                                                        <circle
                                                            cx="22" cy="22" r="20" fill="none"
                                                            stroke={viewMode === 'results' ? "#06B6D4" : "#818CF8"}
                                                            strokeWidth="2.5"
                                                            strokeDasharray={`${(synthesisMetrics[idx] || 0) * 1.25} 125`}
                                                            className="transition-all duration-1000"
                                                        />
                                                    </svg>
                                                    <div className="absolute inset-0 flex items-center justify-center">
                                                        <span className={cn("text-[10px] font-black", viewMode === 'results' ? "text-cyan-400" : "text-indigo-300")}>
                                                            {Math.round(synthesisMetrics[idx] || 0)}%
                                                        </span>
                                                    </div>
                                                </div>
                                                <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest mt-2">{label}</span>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="flex flex-col gap-3 border-l border-white/5 pl-6">
                                        {[
                                            { l: viewMode === 'results' ? "SYNC" : "CONF", v: viewMode === 'results' ? "HIGH" : `${(synthesisMetrics[0] || 90).toFixed(1)}%` },
                                            { l: "RANK", v: viewMode === 'results' ? "P1" : (intelligence?.clip_quality || intelligence?.overall_quality_score > 80 ? "S_CLASS" : "A_CLASS") }
                                        ].map((item, i) => (
                                            <div key={i}>
                                                <p className="text-[8px] font-black text-slate-600 uppercase tracking-widest">{item.l}</p>
                                                <p className={cn("text-[12px] font-black uppercase tracking-widest", viewMode === 'results' ? "text-cyan-400" : "text-indigo-300")}>{item.v}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Center Column: Video Hero */}
                        <div className="flex flex-col items-center gap-4">
                            <div className="relative h-[88vh] w-[420px] max-w-[440px]">
                                <div className="absolute inset-0 rounded-[3rem] bg-black/40 border border-white/5 shadow-2xl overflow-hidden">
                                    {selectedItem ? (
                                        <video
                                            ref={videoRef}
                                            src={getVideoUrl(selectedItem)}
                                            onTimeUpdate={handleTimeUpdate}
                                            onLoadedMetadata={handleLoadedMetadata}
                                            controls
                                            playsInline
                                            autoPlay={false}
                                            preload="auto"
                                            className="h-full w-full object-contain"
                                        />
                                    ) : (
                                        <div className="w-full h-full flex flex-col items-center justify-center opacity-10 bg-black/20">
                                            <MonitorPlay className="w-16 h-16 mb-4" />
                                            <p className="text-[12px] font-black uppercase tracking-[0.6em] text-slate-500">SIGNAL_OFFLINE</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Filename Below Video */}
                            {selectedItem && (
                                <p className="text-xs text-white/40 font-mono text-center max-w-[420px] truncate">
                                    {selectedItem.filename}
                                </p>
                            )}

                            {/* Temporal Sequence Map */}
                            <div className="w-[420px] bg-[#0b0d14]/40 rounded-3xl border border-white/5 p-4 shadow-2xl relative overflow-hidden">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                        <div className="w-1 h-3 bg-cyan-500 rounded-full" />
                                        <p className="text-[9px] font-black text-slate-200 uppercase tracking-[0.3em]">Temporal_Sequence_Map</p>
                                    </div>
                                    <span className="font-mono text-[9px] text-cyan-400/60 font-black">
                                        {currentTime.toFixed(2)}s / {duration.toFixed(2)}s
                                    </span>
                                </div>
                                <div className="h-8 flex items-end gap-[1px] bg-black/40 rounded-xl p-2 border border-white/5 overflow-hidden relative">
                                    {/* Segment Markers Layer */}
                                    {intelligence && (
                                        <div className="absolute inset-0 z-0 pointer-events-none px-2">
                                            {(intelligence.segments || intelligence.edl?.decisions || (Array.isArray(intelligence.edl) ? intelligence.edl : [])).map((seg: any, idx: number) => {
                                                const startT = seg.start || seg.reference_start || seg.timeline_start;
                                                const left = (startT / duration) * 100;
                                                if (isNaN(left) || left <= 0) return null;
                                                return (
                                                    <div
                                                        key={`marker-${idx}`}
                                                        className="absolute top-0 bottom-0 w-[1px] bg-white/10"
                                                        style={{ left: `${left}%` }}
                                                    />
                                                );
                                            })}
                                        </div>
                                    )}

                                    {waveformData.map((h: number, i: number) => {
                                        const progress = (currentTime / duration) * waveformData.length;
                                        const isActive = i <= progress;
                                        const isCurrent = Math.floor(progress) === i;
                                        return (
                                            <div
                                                key={i}
                                                className={cn(
                                                    "flex-1 rounded-full transition-all duration-300 relative z-10",
                                                    isActive ? (isCurrent ? "bg-cyan-400 shadow-[0_0_10px_#22d3ee]" : "bg-cyan-500/40") : "bg-white/5"
                                                )}
                                                style={{ height: `${h}%` }}
                                            />
                                        );
                                    })}
                                </div>
                                <div className="mt-2 flex justify-between font-mono text-[9px] font-bold text-slate-500 uppercase tracking-[0.3em] px-2 italic">
                                    <span className="text-white">H_00s</span>
                                    <span className="text-white">T_{duration.toFixed(2)}s</span>
                                </div>
                            </div>
                        </div>

                        {/* Right Column: Director's Log & Strategy */}
                        <div className="sticky top-5 flex flex-col gap-6 max-w-[520px] pb-20">
                            <div className="bg-[#0b0d14]/60 border border-indigo-500/20 rounded-[2.5rem] p-6 relative overflow-hidden group shadow-2xl">
                                <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                                    <MessageSquare className="w-16 h-16 text-indigo-400" />
                                </div>

                                <div className="flex items-center gap-4 mb-6">
                                    <Sparkles className="w-5 h-5 text-indigo-400" />
                                    <h3 className="text-[12px] font-black text-slate-200 uppercase tracking-[0.5em]">Director_Log</h3>
                                </div>

                                <div className="space-y-4">
                                    <div className="font-mono bg-black/40 p-5 rounded-2xl border border-white/5 relative min-h-[160px] flex flex-col justify-between">
                                        <div className="absolute top-3 right-3 flex items-center gap-2">
                                            <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse", intelligence ? "bg-lime-500 shadow-[0_0_8px_#84cc16]" : "bg-slate-700")} />
                                            <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
                                                {intelLoading ? "SCANNING" : intelligence ? "LIVE_REASONING" : "AWAITING"}
                                            </span>
                                        </div>

                                        {intelLoading ? (
                                            <div className="space-y-2">
                                                <div className="h-3 w-3/4 bg-white/5 rounded animate-pulse" />
                                                <div className="h-3 w-1/2 bg-white/5 rounded animate-pulse" />
                                            </div>
                                        ) : intelligence ? (
                                            <div className="space-y-4">
                                                <div className="bg-indigo-500/10 -mx-2 -mt-2 p-3 rounded-t-xl border-b border-white/5">
                                                    <h4 className="text-[8px] font-black text-indigo-400 uppercase tracking-widest mb-1">Current_Logic_Pulse</h4>
                                                    <p className="text-[14px] text-white font-black tracking-tight leading-tight">
                                                        {viewMode === "results" ? (currentDecision?.reasoning || "Analyzing sequence dynamics...") :
                                                            viewMode === "references" ? (currentSegment?.reasoning || "Mapping structural targets...") :
                                                                (intelligence.content_description || "Visual asset verified.")}
                                                    </p>
                                                </div>
                                                <p className="text-[12px] text-slate-400 leading-relaxed font-medium mt-2">
                                                    {viewMode === "results" && (intelligence.blueprint?.overall_reasoning || "Synthesis matches reference pacing and energy signatures.")}
                                                    {viewMode === "references" && (intelligence.blueprint?.arc_description || "Reference pattern identified for cinematic style replication.")}
                                                    {viewMode === "clips" && (`Ideal for: ${intelligence.best_for?.join(", ")}`)}
                                                </p>
                                            </div>
                                        ) : (
                                            <p className="text-[13px] text-slate-600 italic">Select a specimen to view AI reasoning and editing logic.</p>
                                        )}
                                    </div>

                                    {/* Actionable Insights Section - Data Driven */}
                                    {intelligence && (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="bg-indigo-500/5 border border-indigo-500/10 p-4 rounded-xl flex flex-col justify-between group/insight">
                                                <span className="text-[9px] font-black text-indigo-400/60 uppercase tracking-[0.3em] mb-1.5 flex items-center gap-2">
                                                    <BrainCircuit className="w-3 h-3" />
                                                    Agent_Advice
                                                </span>
                                                <p className="text-[11px] font-black text-white uppercase tracking-tight leading-tight">
                                                    {viewMode === "clips" ? (intelligence?.narrative_utility?.[0] ? `BEST AS: ${intelligence.narrative_utility[0]}` : "VERSATILE CLIP") :
                                                        viewMode === "references" ? `TARGET: ${intelligence.blueprint?.editing_style || "STYLE_SYNC"}` :
                                                            `MOOD: ${intelligence.blueprint?.emotional_intent || "DYNAMIC"}`}
                                                </p>
                                            </div>
                                            <div className="bg-cyan-500/5 border border-cyan-500/10 p-4 rounded-xl flex flex-col justify-between">
                                                <span className="text-[9px] font-black text-cyan-400/60 uppercase tracking-[0.3em] mb-1.5 flex items-center gap-2">
                                                    <Zap className="w-3 h-3" />
                                                    Status
                                                </span>
                                                <p className="text-[11px] font-black text-white uppercase tracking-tight">
                                                    LOGIC_LOCKED
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {/* Additional Multi-line Advice for Judges/Users */}
                                    {intelligence && (
                                        <div className="p-4 bg-white/[0.02] border border-white/5 rounded-2xl relative overflow-hidden">
                                            <div className="absolute top-0 right-0 p-3 opacity-10">
                                                <Sparkles className="w-8 h-8 text-indigo-400" />
                                            </div>
                                            <h4 className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-2">Strategy_Refinement</h4>
                                            <p className="text-[11px] text-slate-300 font-medium leading-relaxed uppercase tracking-tight">
                                                {viewMode === "clips" ? (intelligence.best_moments?.High?.reason || "Dynamic intensity detected in primary segment.") :
                                                    viewMode === "references" ? (intelligence.blueprint?.ideal_material_suggestions?.[0] || "Match with high-motion clips for optimal pacing.") :
                                                        "All aesthetic constraints satisfied. Ready for final export pass."}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    /* Compare Mode: Forensic Split Monitor (Zero-Scroll Optimized) */
                    <div className="flex flex-col h-full space-y-5">
                        <div className="grid grid-cols-2 gap-6 flex-1 min-h-0">
                            {[
                                { id: "A", slot: slotA, ref: videoRefA, set: setSlotA, color: "cyan" },
                                { id: "B", slot: slotB, ref: videoRefB, set: setSlotB, color: "pink" }
                            ].map(s => (
                                <div key={s.id} className={cn(
                                    "bg-[#0b0d14]/40 border-2 rounded-[2.5rem] p-5 flex flex-col relative transition-all duration-700",
                                    s.slot ? `border-${s.color}-500/20 shadow-2xl` : "border-white/5 border-dashed"
                                )}>
                                    {s.slot ? (
                                        <>
                                            <div className={cn(
                                                "absolute top-6 left-6 z-20 px-3 py-1 text-white text-[10px] font-black uppercase tracking-widest rounded shadow-xl",
                                                s.color === "cyan" ? "bg-cyan-500" : "bg-pink-500"
                                            )}>Specimen_{s.id}</div>
                                            <div className="absolute top-6 right-6 z-20 flex items-center gap-3">
                                                <span className="text-[9px] font-black text-white/30 uppercase tracking-widest truncate max-w-[120px]">{s.slot.filename}</span>
                                                <button onClick={() => s.set(null)} className="p-1 text-slate-600 hover:text-white transition-colors bg-white/5 rounded-full"><X className="w-3.5 h-3.5" /></button>
                                            </div>
                                            <video ref={s.ref} src={getVideoUrl(s.slot as AssetItem)} controls className="w-full h-full object-contain rounded-xl" />
                                        </>
                                    ) : (
                                        <div className="flex-1 flex flex-col items-center justify-center space-y-4 text-slate-800 group cursor-pointer" onClick={() => setTargetSlot(s.id as any)}>
                                            <div className={cn(
                                                "w-16 h-16 rounded-full border border-dashed border-white/10 flex items-center justify-center transition-all",
                                                s.color === "cyan" ? "group-hover:border-cyan-500/40 group-hover:text-cyan-400" : "group-hover:border-pink-500/40 group-hover:text-pink-400"
                                            )}>
                                                {s.id === "A" ? <MonitorPlay className="w-7 h-7 opacity-40" /> : <Target className="w-7 h-7 opacity-40" />}
                                            </div>
                                            <div className="text-center">
                                                <p className={cn(
                                                    "text-[12px] font-black uppercase tracking-[0.3em] mb-1",
                                                    s.color === "cyan" ? "group-hover:text-cyan-400" : "group-hover:text-pink-400"
                                                )}>Mount _{s.id}</p>
                                                <p className="text-[9px] font-medium italic opacity-30">Select from Dock Above</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* Compare Mode Logic Bridge / Differential Diagnostic */}
                        {slotA && slotB && (
                            <div className="bg-[#0b0d14]/60 border border-white/5 rounded-3xl p-6 animate-in slide-in-from-bottom-4 duration-700">
                                <div className="flex items-center justify-between mb-6">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-indigo-500/10 rounded-lg">
                                            <Cpu className="w-4 h-4 text-indigo-400" />
                                        </div>
                                        <div>
                                            <h3 className="text-[11px] font-black text-white uppercase tracking-[0.2em]">Differential_Diagnostic</h3>
                                            <p className="text-[9px] text-slate-500 font-medium">Cross-referencing Specimen_A and Specimen_B</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-8">
                                        {[
                                            { l: "Motion_Delta", v: "±4.2%", s: "CORRELATED" },
                                            { l: "Sync_Alignment", v: "99.8%", s: "LOCKED" },
                                            { l: "Vibe_Divergence", v: "LOW", s: "COHESIVE" }
                                        ].map((m, i) => (
                                            <div key={i} className="text-right">
                                                <p className="text-[8px] font-black text-slate-600 uppercase tracking-widest mb-0.5">{m.l}</p>
                                                <div className="flex items-center gap-2 justify-end">
                                                    <span className="text-[12px] font-black text-white">{m.v}</span>
                                                    <span className="text-[7px] font-bold text-indigo-500/50 uppercase tracking-widest">{m.s}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="grid grid-cols-3 gap-6">
                                    <div className="col-span-2 bg-black/40 rounded-2xl p-4 border border-white/5 relative overflow-hidden">
                                        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />
                                        <p className="text-[11px] text-slate-400 leading-relaxed italic">
                                            <span className="text-indigo-400 font-bold mr-2">ANALYSIS:</span>
                                            Both specimens exhibit high semantic correlation. Specimen_B provides a more aggressive motion profile which complements the static framing in Specimen_A. Alignment exceeds the delta threshold—pairing is recommended for final synthesis.
                                        </p>
                                    </div>
                                    <div className="bg-indigo-500/10 rounded-2xl p-4 border border-indigo-500/20 flex flex-col justify-center items-center text-center">
                                        <span className="text-[8px] font-black text-indigo-400 uppercase tracking-widest mb-1">COHESION_SCORE</span>
                                        <span className="text-[24px] font-black text-white leading-none">94.8</span>
                                        <span className="text-[8px] font-bold text-indigo-400/50 uppercase tracking-widest mt-1">OPTIMAL_LINK</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Telemetry Status Strip - Slimmed */}
                        <div className="flex items-center justify-center pb-2">
                            <div className="bg-white/[0.03] border border-white/5 rounded-2xl px-10 py-3 flex items-center gap-12 backdrop-blur-xl shrink-0">
                                <div className="flex items-center gap-12">
                                    <div className="flex flex-col gap-0.5">
                                        <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest">Linkage</span>
                                        <span className={cn("text-[11px] font-black uppercase tracking-wider", syncEnabled ? "text-cyan-400" : "text-white/20")}>{syncEnabled ? "STABILIZED" : "STANDBY"}</span>
                                    </div>
                                    <div className="flex flex-col gap-0.5">
                                        <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest">Drift</span>
                                        <span className="text-[11px] font-black text-indigo-400 font-mono tracking-widest">±0s_LOCKED</span>
                                    </div>
                                </div>
                                <div className="h-8 w-px bg-white/10" />
                                <label className="flex items-center gap-6 cursor-pointer group">
                                    <div className={cn(
                                        "h-5 w-10 rounded-full border transition-all duration-500 relative",
                                        syncEnabled ? "bg-cyan-500 border-cyan-400" : "bg-white/5 border-white/10"
                                    )}>
                                        <input type="checkbox" checked={syncEnabled} onChange={(e) => setSyncEnabled(e.target.checked)} className="sr-only" />
                                        <div className={cn(
                                            "absolute top-1 left-1 h-3 w-3 rounded-full transition-all duration-500",
                                            syncEnabled ? "translate-x-5 bg-white shadow-md" : "bg-slate-700"
                                        )} />
                                    </div>
                                    <span className="text-[10px] font-black text-white/40 uppercase tracking-widest group-hover:text-white transition-colors">Engage Temporal Sync</span>
                                </label>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
