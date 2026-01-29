"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
    Database,
    Activity,
    MonitorPlay,
    X,
    Eye,
    Download
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference, Clip } from "@/lib/types";

// Import our split Vault views
import VaultA from "./VaultA";
import VaultB from "./VaultB";

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

    // Compare mode state
    const [compareMode, setCompareMode] = useState(false);
    const [slotA, setSlotA] = useState<AssetItem | null>(null);
    const [slotB, setSlotB] = useState<AssetItem | null>(null);
    const [syncEnabled, setSyncEnabled] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isCabinetOpen, setIsCabinetOpen] = useState(false);
    const [targetSlot, setTargetSlot] = useState<"A" | "B">("A");

    // Refs
    const videoRef = useRef<HTMLVideoElement>(null);
    const videoRefA = useRef<HTMLVideoElement>(null);
    const videoRefB = useRef<HTMLVideoElement>(null);

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

        if (filename && type && references.length > 0) {
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

    // Enhanced Asset Click: Dynamic Assignment or Selection
    const handleAssetClick = (item: AssetItem, type: ViewMode) => {
        if (compareMode) {
            // In compare mode, if selecting from library (results), auto-load the reference
            if (type === "results") {
                // Set the output in Slot A
                setSlotA(item);

                // Auto-find and load the matching reference in Slot B
                const refPrefix = item.filename.split('_')[0];
                const matchingRef = references.find(r => r.filename.startsWith(refPrefix));
                if (matchingRef) {
                    setSlotB(matchingRef);
                }

                setIsCabinetOpen(false);
            } else {
                // Manual slot selection for references/clips
                if (targetSlot === "A") {
                    setSlotA(item);
                    setTargetSlot("B");
                } else {
                    setSlotB(item);
                }
            }
        } else {
            setSelectedItem(item);
            setViewMode(type);
        }
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

    // Waveform & Metrics Logic (Calculated here and passed down)
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

    const synthesisMetrics = useMemo(() => {
        if (!intelligence) return [80, 75, 90, 85];
        if (viewMode === "results") return [intelligence.overall_quality_score || 88, 83, 96, 92];
        const quality = (intelligence.clip_quality || 3) * 20;
        return [quality, quality + 5, 85, 90];
    }, [intelligence, viewMode]);

    const currentDecision = useMemo(() => {
        if (!intelligence || !intelligence.edl || viewMode !== "results") return null;
        const decisions = intelligence.edl.decisions || [];
        return decisions.find((d: any) => currentTime >= d.timeline_start && currentTime <= d.timeline_end);
    }, [intelligence, currentTime, viewMode]);

    const currentSegment = useMemo(() => {
        if (!intelligence || !intelligence.segments || viewMode !== "references") return null;
        return intelligence.segments.find((s: any) => currentTime >= s.start && currentTime <= s.end);
    }, [intelligence, currentTime, viewMode]);

    // Sync Logic
    useEffect(() => {
        if (!syncEnabled || !videoRefA.current || !videoRefB.current) return;
        const videoA = videoRefA.current;
        const videoB = videoRefB.current;
        const syncPlayPause = () => { if (videoA.paused) videoB.pause(); else videoB.play(); };
        const handleSyncSeek = () => { videoB.currentTime = videoA.currentTime; };
        videoA.addEventListener("play", syncPlayPause);
        videoA.addEventListener("pause", syncPlayPause);
        videoA.addEventListener("seeking", handleSyncSeek);
        const driftInterval = setInterval(() => {
            if (Math.abs(videoA.currentTime - videoB.currentTime) > 0.05) videoB.currentTime = videoA.currentTime;
        }, 100);
        return () => {
            videoA.removeEventListener("play", syncPlayPause);
            videoA.removeEventListener("pause", syncPlayPause);
            videoA.removeEventListener("seeking", handleSyncSeek);
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
        <div className="min-h-screen bg-[#020306] text-slate-100 flex flex-col overflow-hidden">
            {/* Shared Header */}
            <header className="flex items-center justify-between px-10 py-3 border-b border-white/5 bg-black/40 shrink-0 z-[110]">
                <div className="flex items-center gap-3">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    <h1 className="text-[12px] font-black text-white uppercase tracking-[0.3em] italic">Vault: Intelligence Core</h1>
                </div>

                <div className="flex items-center gap-4">
                    <div className="text-right mr-6">
                        <p className="text-[10px] font-black text-white/40 uppercase tracking-[0.3em]">
                            {compareMode ? "Compare Mode" : "Intelligence Core"}
                        </p>
                        <p className="text-[8px] font-bold text-cyan-400 uppercase tracking-widest leading-none mt-1">
                            {compareMode ? "Side-by-Side Review" : "Analysis & Insights"}
                        </p>
                    </div>

                    {!compareMode && (
                        <div className="flex items-center bg-black/40 p-1 rounded-lg border border-white/5 mr-4">
                            {(["results", "references", "clips"] as ViewMode[]).map(mode => (
                                <button
                                    key={mode}
                                    onClick={() => setViewMode(mode)}
                                    className={cn(
                                        "relative px-4 py-1.5 rounded-md text-[9px] font-black uppercase tracking-[0.2em] transition-all z-10",
                                        viewMode === mode ? "text-cyan-400" : "text-slate-500 hover:text-slate-300"
                                    )}
                                >
                                    {viewMode === mode && <div className="absolute inset-0 bg-cyan-500/10 rounded-md" />}
                                    {mode}
                                </button>
                            ))}
                        </div>
                    )}

                    <button
                        onClick={() => setCompareMode(!compareMode)}
                        className={cn(
                            "group relative flex items-center gap-2 px-6 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all",
                            compareMode ? "ring-2 ring-white/50 bg-white/10" : "bg-black/40 border border-white/10"
                        )}
                    >
                        <div className={cn("w-1.5 h-1.5 rounded-full mr-1", compareMode ? "bg-green-400 shadow-[0_0_8px_#4ade80]" : "bg-slate-400/50")} />
                        {compareMode ? "Exit Compare" : "Compare Mode"}
                    </button>
                </div>
            </header>

            {/* Specimen Cabinet */}
            <div className={cn(
                "fixed inset-y-0 left-0 w-80 bg-[#05060a]/95 backdrop-blur-2xl border-r border-white/10 z-[150] transform transition-transform duration-500 flex flex-col shadow-2xl",
                isCabinetOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-cyan-400">
                        <Database className="w-4 h-4" />
                        <h2 className="text-[11px] font-black uppercase tracking-[0.3em]">Library</h2>
                    </div>
                    <button onClick={() => setIsCabinetOpen(false)} className="p-1 hover:bg-white/10 rounded-full transition-all">
                        <X className="w-4 h-4 text-slate-400" />
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    <p className="text-[8px] font-black text-slate-600 uppercase tracking-widest px-2">Your Results</p>
                    {results.map((res) => (
                        <div
                            key={res.filename}
                            onClick={() => handleAssetClick(res, "results")}
                            className={cn(
                                "p-3 rounded-xl border transition-all cursor-pointer group/item",
                                (selectedItem?.filename === res.filename || slotA?.filename === res.filename) ? "bg-cyan-500/10 border-cyan-500/30" : "bg-white/5 border-white/5 hover:border-white/20"
                            )}
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-16 h-10 rounded-md bg-black relative overflow-hidden shrink-0 border border-white/10">
                                    <video src={getVideoUrl(res)} className="w-full h-full object-cover opacity-60" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-[10px] font-black text-white uppercase truncate">{res.filename}</p>
                                    <p className="text-[8px] font-medium text-slate-500 uppercase tracking-widest">ID: {res.filename.split('_').pop()?.split('.')[0]}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {isCabinetOpen && <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[140]" onClick={() => setIsCabinetOpen(false)} />}

            {/* Asset Dock (Mini-Cards) - ONLY IN VAULT A */}
            {!compareMode && (
                <div className="bg-[#020306] border-b border-white/5 py-4 shrink-0">
                    <div className="max-w-[1700px] mx-auto px-10 flex justify-between gap-6">
                        {currentAssets.slice(0, 5).map((item, idx) => (
                            <div key={idx} className="relative flex-1 max-w-[calc(20%-20px)] group">
                                <div
                                    onClick={() => handleAssetClick(item, viewMode)}
                                    className={cn(
                                        "relative w-full aspect-[16/11] rounded-xl overflow-hidden border-2 transition-all duration-500 cursor-pointer",
                                        selectedItem === item ? "border-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.2)]" : "border-white/5 bg-[#0a0c14] hover:border-cyan-500/30"
                                    )}
                                >
                                    <video src={getVideoUrl(item)} className="w-full h-full object-cover opacity-70 group-hover:opacity-100" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <main className="flex-1 px-10 py-5 max-w-[1700px] mx-auto w-full overflow-hidden flex flex-col relative">
                {!compareMode ? (
                    <VaultA
                        selectedItem={selectedItem}
                        viewMode={viewMode}
                        intelLoading={intelLoading}
                        intelligence={intelligence}
                        currentTime={currentTime}
                        duration={duration}
                        handleTimeUpdate={handleTimeUpdate}
                        handleLoadedMetadata={handleLoadedMetadata}
                        videoRef={videoRef}
                        getVideoUrl={getVideoUrl}
                        waveformData={waveformData}
                        synthesisMetrics={synthesisMetrics}
                        currentDecision={currentDecision}
                        currentSegment={currentSegment}
                    />
                ) : (
                    <VaultB
                        slotA={slotA}
                        slotB={slotB}
                        videoRefA={videoRefA}
                        videoRefB={videoRefB}
                        getVideoUrl={getVideoUrl}
                        syncEnabled={syncEnabled}
                        setSyncEnabled={setSyncEnabled}
                        setIsCabinetOpen={setIsCabinetOpen}
                        results={results}
                        references={references}
                        setSlotA={setSlotA}
                        setSlotB={setSlotB}
                    />
                )}
            </main>
        </div>
    );
}
