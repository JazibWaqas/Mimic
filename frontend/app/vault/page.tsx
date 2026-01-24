"use client";

import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import {
    Trash2,
    Download,
    Columns2,
    X,
    ChevronDown,
    Activity,
    History,
    Sparkles,
    Target,
    Zap,
    Cpu,
    Shield,
    Terminal,
    Layers
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference, Clip } from "@/lib/types";

type ViewMode = "results" | "references" | "clips";

export default function VaultPage() {
    const searchParams = useSearchParams();
    const [results, setResults] = useState<Result[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [clips, setClips] = useState<Clip[]>([]);
    const [selectedItem, setSelectedItem] = useState<Result | Reference | Clip | null>(null);
    const [selectedItem2, setSelectedItem2] = useState<Result | Reference | Clip | null>(null);
    const [sideBySideMode, setSideBySideMode] = useState(false);
    const [viewMode, setViewMode] = useState<ViewMode>("results");
    const [loading, setLoading] = useState(true);
    const scrollRef = useRef<HTMLDivElement>(null);

    const fetchData = async () => {
        try {
            const [dataProjects, dataRefs, dataClips] = await Promise.all([
                api.fetchResults(),
                api.fetchReferences(),
                api.fetchClips()
            ]);
            setResults(dataProjects.results || []);
            setReferences(dataRefs.references || []);
            setClips(dataClips.clips || []);

            const filename = searchParams.get("filename");
            const type = searchParams.get("type") as ViewMode | null;

            if (filename && type) {
                if (type === "results") {
                    const item = dataProjects.results?.find((r: Result) => r.filename === filename);
                    if (item) { setSelectedItem(item); setViewMode("results"); }
                } else if (type === "references") {
                    const item = dataRefs.references?.find((r: Reference) => r.filename === filename);
                    if (item) { setSelectedItem(item); setViewMode("references"); }
                } else if (type === "clips") {
                    const item = dataClips.clips?.find((c: Clip) => c.filename === filename);
                    if (item) { setSelectedItem(item); setViewMode("clips"); }
                }
            } else if (dataProjects.results?.[0]) {
                setSelectedItem(dataProjects.results[0]);
            }
        } catch (err) {
            toast.error("Telemetry failed");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchData(); }, [searchParams]);

    const deleteResult = async (filename: string) => {
        if (!confirm("Confirm data erasure?")) return;
        try {
            await api.deleteResult(filename);
            toast.success("Data erased");
            fetchData();
            if (selectedItem?.filename === filename) setSelectedItem(null);
        } catch (err) {
            toast.error("Erasure failed");
        }
    };

    const formatSize = (bytes: number) => (bytes / (1024 * 1024)).toFixed(1) + " MB";
    const formatDate = (timestamp: number) => new Date(timestamp * 1000).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });

    const scrollBoxItems = viewMode === "results" ? results : viewMode === "references" ? references : clips;

    const getItemUrl = (item: Result | Reference | Clip) => {
        if ('url' in item) return item.url;
        if ('path' in item) return item.path;
        return "";
    };

    const getItemType = (item: Result | Reference | Clip): string => {
        if ('url' in item) return "Synthesis";
        if ('path' in item && !('session_id' in item)) return "Reference";
        return "Raw Clip";
    };

    const downloadFile = (url: string, filename: string) => {
        const link = document.createElement("a");
        link.href = `http://localhost:8000${url}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="min-h-screen bg-[#020306] flex flex-col pt-12 pb-32 overflow-x-hidden">
            <div className="max-w-[1700px] w-full mx-auto px-6 md:px-12 flex flex-col gap-10">
                {/* Header Section */}
                <div className="flex items-end justify-between border-b border-white/10 pb-8">
                    <div className="space-y-3">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                                <Shield className="h-6 w-6" />
                            </div>
                            <h1 className="text-4xl font-black text-white uppercase tracking-tighter italic">The Vault</h1>
                        </div>
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] ml-16">Temporal Synthesis Archive / Level 7 Clearance</p>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => {
                                setSideBySideMode(!sideBySideMode);
                                if (!sideBySideMode) {
                                    if (!selectedItem2 && results.length > 1) setSelectedItem2(results[1]);
                                    else if (!selectedItem2 && results.length > 0 && references.length > 0) setSelectedItem2(references[0]);
                                }
                            }}
                            className={cn(
                                "h-12 px-10 rounded-xl font-black text-[11px] uppercase tracking-[0.2em] transition-all border flex items-center gap-4 group",
                                sideBySideMode
                                    ? "bg-cyan-500 border-cyan-400 text-white shadow-[0_0_40px_rgba(6,182,212,0.4)]"
                                    : "bg-white/5 border-white/10 text-slate-400 hover:text-white hover:border-indigo-500/50"
                            )}
                        >
                            <Columns2 className={cn("h-5 w-5 transition-transform", sideBySideMode && "rotate-90")} />
                            {sideBySideMode ? "Exit Core Comparison" : "Dual Stream Compare"}
                        </button>
                    </div>
                </div>

                {!sideBySideMode ? (
                    /* Standard View - Rebalanced Grid */
                    <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-12 items-start">
                        {/* Center: Main Player Area */}
                        <div className="space-y-10">
                            <div className="aspect-video w-full rounded-[2.5rem] bg-[#0b0d14] border border-white/5 overflow-hidden shadow-[0_60px_100px_rgba(0,0,0,0.9)] relative group border-indigo-500/10 hover:border-indigo-500/30 transition-all duration-700">
                                {selectedItem ? (
                                    <video
                                        key={getItemUrl(selectedItem)}
                                        src={`http://localhost:8000${getItemUrl(selectedItem)}`}
                                        className="w-full h-full object-contain"
                                        controls
                                        autoPlay
                                    />
                                ) : (
                                    <div className="w-full h-full flex flex-col items-center justify-center text-slate-700">
                                        <Layers className="h-16 w-16 opacity-10 mb-6 animate-pulse" />
                                        <p className="text-xs font-black uppercase tracking-[0.3em]">Initialize Source Selection</p>
                                    </div>
                                )}

                                {selectedItem && (
                                    <div className="absolute top-8 left-8 z-10 animate-in fade-in slide-in-from-left-4 duration-700">
                                        <div className="px-5 py-2 rounded-full bg-black/60 backdrop-blur-xl border border-indigo-500/30 text-[10px] font-black text-white uppercase tracking-[0.25em] flex items-center gap-3">
                                            <div className="h-2 w-2 rounded-full bg-indigo-400 glow-indigo pulse-glow" />
                                            Active Stream: {selectedItem.filename}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Integrated Telemetry Quick Actions */}
                            <div className="grid grid-cols-1 md:grid-cols-[1fr_300px] gap-6">
                                <div className="p-8 rounded-[2rem] bg-white/[0.02] border border-white/5 flex items-center justify-between">
                                    <div className="space-y-1.5">
                                        <div className="flex items-center gap-2">
                                            <div className="h-1.5 w-1.5 rounded-full bg-lime-400 glow-lime" />
                                            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Metadata Integrity Verified</p>
                                        </div>
                                        <p className="text-lg font-black text-white uppercase tracking-tight truncate max-w-[300px]">{selectedItem?.filename || "No Data"}</p>
                                    </div>
                                    <div className="flex gap-4">
                                        <button
                                            disabled={!selectedItem}
                                            onClick={() => selectedItem && downloadFile(getItemUrl(selectedItem), selectedItem.filename)}
                                            className="h-12 px-8 rounded-xl bg-white text-black font-black text-[10px] uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all shadow-2xl disabled:opacity-20"
                                        >
                                            Export
                                        </button>
                                        <button
                                            disabled={!selectedItem}
                                            onClick={() => selectedItem && deleteResult(selectedItem.filename)}
                                            className="h-12 w-12 rounded-xl bg-red-600/10 text-red-500 border border-red-500/20 flex items-center justify-center hover:bg-red-500 hover:text-white transition-all disabled:opacity-20"
                                        >
                                            <Trash2 className="h-5 w-5" />
                                        </button>
                                    </div>
                                </div>

                                <div className="p-8 rounded-[2rem] bg-indigo-600/5 border border-indigo-500/10 flex flex-col justify-center">
                                    <p className="text-[9px] font-black text-indigo-400/60 uppercase tracking-widest mb-1">Session Data</p>
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs font-black text-white uppercase">{selectedItem ? formatSize(selectedItem.size) : "0 MB"}</span>
                                        <div className="h-1 w-12 bg-white/10 rounded-full overflow-hidden">
                                            <div className="h-full bg-indigo-500 w-2/3" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Sidebar: Optimized Telemetry Panels */}
                        <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-1000">
                            <div className="p-8 rounded-[2.5rem] bg-[#0b0d14]/40 border border-white/5 space-y-8 shadow-2xl relative overflow-hidden">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-[60px] -mr-16 -mt-16" />
                                <div className="flex items-center gap-4 pb-6 border-b border-white/5">
                                    <Activity className="h-5 w-5 text-cyan-400" />
                                    <h3 className="text-[12px] font-black text-white uppercase tracking-[0.2em]">X-Ray Metrics</h3>
                                </div>
                                <div className="space-y-8">
                                    {[
                                        { label: 'Clip Diversity', val: 94, icon: <Layers className="h-4 w-4" />, color: 'bg-indigo-500' },
                                        { label: 'Rhythmic Sync', val: 88, icon: <Zap className="h-4 w-4" />, color: 'bg-purple-500' },
                                        { label: 'Vector Pacing', val: 91, icon: <Target className="h-4 w-4" />, color: 'bg-cyan-500' }
                                    ].map(m => (
                                        <div key={m.label} className="space-y-3">
                                            <div className="flex items-center justify-between text-[11px] font-black uppercase tracking-tighter">
                                                <span className="text-slate-500 flex items-center gap-3">{m.icon} {m.label}</span>
                                                <span className="text-white">{m.val}%</span>
                                            </div>
                                            <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden p-0.5 border border-white/5">
                                                <div className={cn("h-full rounded-full transition-all duration-[2000ms]", m.color)} style={{ width: `${m.val}%` }} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="p-8 rounded-[2.5rem] bg-[#0b0d14]/40 border border-white/5 space-y-6 shadow-2xl">
                                <div className="flex items-center gap-4 pb-4 border-b border-white/5">
                                    <Terminal className="h-5 w-5 text-purple-400" />
                                    <h3 className="text-[12px] font-black text-white uppercase tracking-[0.2em]">Logic Protocol</h3>
                                </div>
                                <div className="h-[240px] overflow-y-auto font-mono text-[10px] text-slate-500 space-y-3 custom-scrollbar pr-3 leading-relaxed">
                                    <p className="text-cyan-400/80 font-bold">&gt; [CORE] Parsing multimodal streams...</p>
                                    <p className="border-l border-white/10 pl-3">&gt; [LOG] Temporal motion vectors mapped to energy stages.</p>
                                    <p className="border-l border-white/10 pl-3">&gt; [LOG] Audio transients sync'd at 128 BPM.</p>
                                    <p className="border-l border-white/10 pl-3">&gt; [LOG] Recyclic frame filtering applied.</p>
                                    <p className="text-purple-400 font-bold">&gt; [AGI] Strategy: High-Impact Pacing.</p>
                                    <p className="text-lime-400/80 font-bold">&gt; [DONE] Output locked and verified.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    /* Compare Mode - Balanced Overhaul */
                    <div className="grid grid-cols-2 gap-12 items-start animate-in zoom-in-[0.98] duration-700">
                        {[
                            { item: selectedItem, setter: setSelectedItem, label: "Stream A / Primary" },
                            { item: selectedItem2, setter: setSelectedItem2, label: "Stream B / Analytics" }
                        ].map((stream, idx) => (
                            <div key={idx} className="space-y-8 group/stream">
                                {/* Selector above player - Centered UI */}
                                <div className="flex flex-col gap-4">
                                    <div className="flex items-center gap-3">
                                        <div className={cn("h-2 w-2 rounded-full animation-pulse", idx === 0 ? "bg-indigo-500 glow-indigo" : "bg-cyan-500 glow-cyan")} />
                                        <p className="text-[11px] font-black text-white uppercase tracking-[0.3em]">{stream.label}</p>
                                    </div>
                                    <div className="relative">
                                        <select
                                            className="w-full bg-[#0b0d14] border border-white/10 rounded-2xl h-14 px-6 text-[11px] font-black text-indigo-400 outline-none focus:border-indigo-500 transition-all uppercase tracking-[0.2em] appearance-none"
                                            value={stream.item?.filename || ""}
                                            onChange={(e) => {
                                                const all = [...results, ...references, ...clips];
                                                const found = all.find(i => i.filename === e.target.value);
                                                if (found) stream.setter(found);
                                            }}
                                        >
                                            <option value="" className="bg-[#0b0d14]">Select Core Asset...</option>
                                            <optgroup label="Synthesis Results" className="bg-[#0b0d14] text-white">
                                                {results.map(r => <option key={r.filename} value={r.filename}>{r.filename}</option>)}
                                            </optgroup>
                                            <optgroup label="References" className="bg-[#0b0d14] text-white">
                                                {references.map(r => <option key={r.filename} value={r.filename}>{r.filename}</option>)}
                                            </optgroup>
                                            <optgroup label="Raw Samples" className="bg-[#0b0d14] text-white">
                                                {clips.map(r => <option key={r.filename} value={r.filename}>{r.filename}</option>)}
                                            </optgroup>
                                        </select>
                                        <ChevronDown className="absolute right-6 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-600 pointer-events-none" />
                                    </div>
                                </div>

                                <div className="aspect-video w-full rounded-[2.5rem] bg-black border border-white/10 overflow-hidden shadow-[0_40px_80px_rgba(0,0,0,0.8)] relative group/vid hover:border-white/20 transition-all duration-500">
                                    {stream.item ? (
                                        <video
                                            key={getItemUrl(stream.item)}
                                            src={`http://localhost:8000${getItemUrl(stream.item)}`}
                                            className="w-full h-full object-contain"
                                            controls
                                            autoPlay
                                        />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-slate-800 space-y-4">
                                            <Cpu className="h-10 w-10 opacity-10" />
                                            <p className="text-[10px] font-black uppercase tracking-[0.3em]">Stream Offline</p>
                                        </div>
                                    )}
                                </div>

                                {stream.item && (
                                    <div className="p-6 rounded-[2rem] bg-white/[0.02] border border-white/5 flex items-center justify-between">
                                        <div className="min-w-0 pr-6">
                                            <p className="text-xs font-black text-white truncate uppercase tracking-tight">{stream.item.filename}</p>
                                            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">{(stream.item.size / (1024 * 1024)).toFixed(1)} MB • {formatDate(stream.item.created_at)}</p>
                                        </div>
                                        <button
                                            onClick={() => downloadFile(getItemUrl(stream.item!), stream.item!.filename)}
                                            className="h-10 w-10 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center hover:bg-indigo-500 hover:text-white transition-all shadow-lg"
                                        >
                                            <Download className="h-4 w-4" />
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Bottom Asset Tray - Integrated Global Selector */}
                <div className="space-y-8 mt-12 pb-24">
                    <div className="flex items-center justify-between border-t border-white/10 pt-12">
                        <div className="flex gap-10">
                            {[
                                { id: 'results', label: 'Synthesis' },
                                { id: 'references', label: 'References' },
                                { id: 'clips', label: 'Source Clips' }
                            ].map(tab => (
                                <button
                                    key={tab.id}
                                    onClick={() => setViewMode(tab.id as ViewMode)}
                                    className={cn(
                                        "text-[11px] font-black uppercase tracking-[0.3em] transition-all relative pb-4 group",
                                        viewMode === tab.id ? "text-white" : "text-slate-500 hover:text-white"
                                    )}
                                >
                                    {tab.label}
                                    <div className={cn(
                                        "absolute bottom-0 left-0 h-1 bg-indigo-500 transition-all duration-500",
                                        viewMode === tab.id ? "w-full opacity-100 glow-indigo" : "w-0 opacity-0 group-hover:w-full group-hover:opacity-40"
                                    )} />
                                </button>
                            ))}
                        </div>
                        <div className="text-[10px] font-black text-slate-600 uppercase tracking-widest">
                            Total Index: {scrollBoxItems.length} Blocks
                        </div>
                    </div>

                    <div className="flex gap-6 overflow-x-auto pb-10 -mx-4 px-4 custom-scrollbar-horizontal snap-x scroll-smooth" ref={scrollRef}>
                        {scrollBoxItems.map((item, idx) => (
                            <button
                                key={item.filename}
                                onClick={() => setSelectedItem(item)}
                                className={cn(
                                    "shrink-0 w-[280px] rounded-[2rem] border transition-all p-3 bg-[#0b0d14]/60 snap-start flex flex-col group/card",
                                    selectedItem?.filename === item.filename
                                        ? "border-indigo-500 shadow-[0_20px_50px_rgba(0,0,0,0.5)] bg-indigo-500/5 scale-[1.02]"
                                        : "border-white/5 hover:border-indigo-500/30 hover:bg-white/[0.02]"
                                )}
                            >
                                <div className="aspect-video rounded-[1.5rem] overflow-hidden bg-black mb-4 relative">
                                    <video src={`http://localhost:8000${getItemUrl(item)}`} className="w-full h-full object-cover opacity-60 group-hover/card:opacity-100 transition-opacity" muted />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover/card:opacity-100 transition-opacity" />
                                </div>
                                <div className="px-2 pb-1 flex justify-between items-start">
                                    <div className="min-w-0 pr-4 text-left">
                                        <p className="text-[10px] font-black text-white truncate uppercase tracking-tight leading-tight">{item.filename}</p>
                                        <p className="text-[8px] font-bold text-slate-600 uppercase tracking-widest mt-1">{formatDate(item.created_at)}</p>
                                    </div>
                                    <p className="text-[9px] font-black text-indigo-400 shrink-0">{formatSize(item.size)}</p>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
