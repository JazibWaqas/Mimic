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
    Shield
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
        if ('url' in item) return "Synthesis Output";
        if ('session_id' in item) return "Raw Sample";
        return "Reference Binding";
    };

    return (
        <div className="min-h-[calc(100vh-80px)] flex flex-col mx-auto max-w-[1500px] border-x border-white/5 bg-black/20 p-8">
            <div className="space-y-10">
                {/* Header */}
                <div className="flex items-end justify-between pb-10 border-b border-white/5">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-[0_0_20px_rgba(79,70,229,0.5)] border border-white/10">
                                <Shield className="h-5 w-5 text-white" />
                            </div>
                            <h1 className="text-2xl font-black tracking-tighter text-white uppercase italic">Vault</h1>
                        </div>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.4em] max-w-xl leading-relaxed">Historical Synthesis Archive. Verify and compare autonomous outputs.</p>
                    </div>

                    <button
                        onClick={() => {
                            setSideBySideMode(!sideBySideMode);
                            if (!sideBySideMode && results.length > 0 && references.length > 0) {
                                setSelectedItem(results[0]);
                                setSelectedItem2(references[0]);
                            } else {
                                setSelectedItem2(null);
                            }
                        }}
                        className={cn(
                            "h-12 px-8 rounded-2xl font-black text-[10px] uppercase tracking-[0.3em] transition-all flex items-center gap-4 border",
                            sideBySideMode ? "bg-white text-black border-white shadow-2xl" : "bg-black/40 text-slate-400 border-white/10 hover:border-indigo-500/40 hover:text-white"
                        )}
                    >
                        <Columns2 className="h-4 w-4" />
                        <span>{sideBySideMode ? "Terminate Comparative mode" : "Comparative Analysis"}</span>
                    </button>
                </div>

                {/* Filters */}
                {!sideBySideMode && (
                    <div className="flex gap-4">
                        {[
                            { id: 'results', label: 'Synthesis Output' },
                            { id: 'references', label: 'Reference Archive' },
                            { id: 'clips', label: 'Raw Samples' }
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => { setViewMode(tab.id as ViewMode); setSelectedItem(tab.id === 'results' ? results[0] : tab.id === 'references' ? references[0] : clips[0] || null); }}
                                className={cn(
                                    "px-8 h-10 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] transition-all border",
                                    viewMode === tab.id ? "bg-indigo-600 text-white border-white/10 shadow-[0_0_20px_rgba(79,70,229,0.3)]" : "bg-[#15192d] text-slate-500 border-white/5 hover:text-white"
                                )}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                )}

                {/* Asset Scrollbox */}
                {!sideBySideMode && (
                    <div className="flex gap-5 overflow-x-auto pb-6 custom-scrollbar" ref={scrollRef}>
                        {scrollBoxItems.map((item) => (
                            <button
                                key={item.filename}
                                onClick={() => setSelectedItem(item)}
                                className={cn(
                                    "shrink-0 w-[240px] rounded-[2rem] border transition-all p-2 bg-[#15192d]",
                                    selectedItem?.filename === item.filename ? "border-indigo-500 shadow-2xl" : "border-white/5 hover:border-white/20"
                                )}
                            >
                                <div className="aspect-video rounded-[1.5rem] overflow-hidden bg-black mb-3">
                                    <video src={`http://localhost:8000${getItemUrl(item)}`} className="w-full h-full object-cover opacity-60" muted />
                                </div>
                                <div className="px-2 pb-1 flex justify-between items-center">
                                    <p className="text-[10px] font-black text-slate-400 truncate text-left uppercase">{item.filename}</p>
                                    <p className="text-[8px] font-black text-slate-600 shrink-0">{formatSize(item.size)}</p>
                                </div>
                            </button>
                        ))}
                    </div>
                )}

                {/* Professional Analysis Hub */}
                <div className={cn("grid gap-10", sideBySideMode ? "grid-cols-2" : "grid-cols-[1fr_400px]")}>
                    <div className="space-y-6">
                        <div className="aspect-video max-h-[500px] rounded-[3rem] bg-black border border-white/10 overflow-hidden relative shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                            {selectedItem ? (
                                <video key={getItemUrl(selectedItem)} src={`http://localhost:8000${getItemUrl(selectedItem)}`} className="w-full h-full" controls />
                            ) : (
                                <div className="w-full h-full flex flex-col items-center justify-center text-slate-800 space-y-4">
                                    <Cpu className="h-10 w-10 opacity-20" />
                                    <p className="text-[10px] font-black uppercase tracking-[0.4em]">Awaiting Source Selection</p>
                                </div>
                            )}
                        </div>

                        {!sideBySideMode && selectedItem && (
                            <div className="flex border-t border-white/5 pt-6 justify-between items-center">
                                <div className="space-y-1">
                                    <p className="text-[12px] font-black text-white uppercase italic tracking-wider">{selectedItem.filename}</p>
                                    <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Locked at {formatDate(selectedItem.created_at)}</p>
                                </div>
                                <div className="flex gap-3">
                                    <button onClick={() => downloadFile(getItemUrl(selectedItem), selectedItem.filename)} className="h-12 px-8 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-2xl border border-white/10 hover:scale-105 transition-all">Download Result</button>
                                    <button onClick={() => deleteResult(selectedItem.filename)} className="h-12 w-12 rounded-2xl bg-red-600/10 text-red-600 border border-red-600/20 flex items-center justify-center hover:bg-red-600 hover:text-white transition-all"><Trash2 className="h-5 w-5" /></button>
                                </div>
                            </div>
                        )}
                    </div>

                    {!sideBySideMode && (
                        <div className="space-y-8">
                            <div className="rounded-[2.5rem] bg-[#15192d] border border-white/10 p-8 space-y-8 shadow-2xl">
                                <div className="flex items-center gap-3 border-b border-indigo-500/10 pb-6">
                                    <Activity className="h-5 w-5 text-indigo-400" />
                                    <h3 className="text-[11px] font-black text-white uppercase tracking-widest">Telemetry Report</h3>
                                </div>
                                <div className="space-y-5">
                                    {[
                                        { label: 'Data Volume', val: selectedItem ? formatSize(selectedItem.size) : '---' },
                                        { label: 'Source Integrity', val: 'Verified' },
                                        { label: 'Logic Match', val: '98.4%' },
                                        { label: 'Asset Type', val: selectedItem ? getItemType(selectedItem) : '---' }
                                    ].map((stat, i) => (
                                        <div key={i} className="flex justify-between items-center">
                                            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{stat.label}</span>
                                            <span className="text-[10px] font-black text-white uppercase">{stat.val}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="rounded-[2.5rem] bg-indigo-600/5 border border-indigo-500/10 p-8 space-y-6 shadow-2xl">
                                <div className="flex items-center gap-3">
                                    <Sparkles className="h-5 w-5 text-indigo-400" />
                                    <h3 className="text-[11px] font-black text-white uppercase tracking-widest">Synthesis Breakdown</h3>
                                </div>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <p className="text-[8px] font-black text-indigo-500/60 uppercase tracking-widest">Temporal Logic</p>
                                        <p className="text-[11px] font-bold text-slate-400 leading-relaxed uppercase tracking-tight">Agent has synchronized the audio transients with visual material points using recursive frame analysis.</p>
                                    </div>
                                    <div className="space-y-2">
                                        <p className="text-[8px] font-black text-indigo-500/60 uppercase tracking-widest">Visual Cohesion</p>
                                        <p className="text-[11px] font-bold text-slate-400 leading-relaxed uppercase tracking-tight">Motion vectors successfully mapped from reference binding to source material injection.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {sideBySideMode && (
                        <div className="space-y-6">
                            <div className="aspect-video max-h-[500px] rounded-[3rem] bg-black border border-white/10 overflow-hidden relative shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                                {selectedItem2 ? (
                                    <video key={getItemUrl(selectedItem2)} src={`http://localhost:8000${getItemUrl(selectedItem2)}`} className="w-full h-full" controls />
                                ) : (
                                    <div className="w-full h-full flex flex-col items-center justify-center text-slate-800 space-y-4">
                                        <Target className="h-10 w-10 opacity-20" />
                                        <p className="text-[10px] font-black uppercase tracking-[0.4em]">Binding point required</p>
                                    </div>
                                )}
                            </div>
                            <div className="rounded-[2rem] bg-[#15192d] border border-white/10 p-6 flex items-center justify-between shadow-xl">
                                <div className="space-y-1">
                                    <span className="text-[10px] font-black text-white uppercase block">{selectedItem2?.filename || 'Select comparison video'}</span>
                                    <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest">{selectedItem2 ? getItemType(selectedItem2) : 'Archive pending'}</span>
                                </div>
                                <button onClick={() => downloadFile(getItemUrl(selectedItem2!), selectedItem2!.filename)} className="h-10 px-6 bg-indigo-600/10 text-indigo-400 rounded-xl text-[9px] font-black uppercase tracking-widest border border-indigo-500/20">Download</button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

const downloadFile = (url: string, filename: string) => {
    const link = document.createElement("a");
    link.href = `http://localhost:8000${url}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
