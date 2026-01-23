"use client";

import { useEffect, useState } from "react";
import {
    Trash2,
    Play,
    Calendar,
    HardDrive,
    MonitorPlay,
    Video,
    Download,
    ChevronRight
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference } from "@/lib/types";

export default function ProjectsPage() {
    const [results, setResults] = useState<Result[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [selectedResult, setSelectedResult] = useState<Result | null>(null);
    const [selectedRef, setSelectedRef] = useState<Reference | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const [dataProjects, dataRefs] = await Promise.all([
                api.fetchResults(),
                api.fetchReferences()
            ]);
            setResults(dataProjects.results || []);
            setReferences(dataRefs.references || []);
            if (!selectedResult) setSelectedResult(dataProjects.results?.[0] || null);
            if (!selectedRef) setSelectedRef(dataRefs.references?.[0] || null);
        } catch (err) {
            toast.error("Failed to load projects");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchData(); }, []);

    const deleteResult = async (filename: string) => {
        if (!confirm("Delete this project?")) return;
        try {
            await api.deleteResult(filename);
            toast.success("Project deleted");
            fetchData();
        } catch (err) {
            toast.error("Delete failed");
        }
    };

    const formatSize = (bytes: number) => (bytes / (1024 * 1024)).toFixed(1) + " MB";
    const formatDate = (timestamp: number) => new Date(timestamp * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' });

    return (
        <div className="h-[calc(100vh-80px)] overflow-hidden flex flex-col bg-black/20 mx-auto max-w-[1700px] border-x border-white/5 shadow-2xl">

            {/* 1. COMPACT REFERENCE CONTEXT (TOP) */}
            <section className="shrink-0 h-[220px] bg-black/40 border-b border-white/5 flex flex-col">
                <div className="px-8 py-3 flex items-center justify-between bg-black/40">
                    <div className="flex items-center gap-3">
                        <Video className="h-3 w-3 text-indigo-400" />
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/60">Reference Context</h3>
                    </div>
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">{references.length} Blueprints Active</span>
                </div>
                <div className="flex-1 overflow-x-auto p-6 flex gap-4 custom-scrollbar bg-black/20">
                    {references.map((ref) => {
                        const isSelected = selectedRef?.filename === ref.filename;
                        return (
                            <button
                                key={ref.filename}
                                onClick={() => setSelectedRef(ref)}
                                className={cn(
                                    "min-w-[140px] h-full rounded-xl border transition-all duration-300 flex flex-col group",
                                    isSelected ? "bg-indigo-600/10 border-indigo-500/40 ring-1 ring-indigo-500/20" : "bg-black/40 border-white/[0.03] hover:border-white/10"
                                )}
                            >
                                <div className="flex-1 bg-black rounded-t-xl overflow-hidden relative">
                                    <video src={`http://localhost:8000${ref.path}`} className="w-full h-full object-cover opacity-30 group-hover:opacity-60" />
                                    {isSelected && <div className="absolute inset-0 bg-indigo-500/10" />}
                                </div>
                                <div className="p-2 border-t border-white/5">
                                    <p className={cn("text-[7px] font-black uppercase tracking-widest truncate", isSelected ? "text-indigo-400" : "text-slate-600")}>{ref.filename}</p>
                                </div>
                            </button>
                        )
                    })}
                </div>
            </section>

            {/* 2. MAIN HUB (VIEWER + INDEX) */}
            <div className="flex-1 flex overflow-hidden">

                {/* Diagnostic Terminal (Center) */}
                <section className="flex-1 flex flex-col bg-gradient-to-b from-transparent to-black/40 border-r border-white/5 overflow-hidden">
                    <div className="flex-1 flex flex-col justify-center px-10 py-8 relative">
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-[40%] bg-indigo-500/5 blur-[120px] -z-10" />

                        <div className="w-full h-full max-h-[800px] flex flex-col">
                            <div className="flex items-center justify-between mb-3 bg-black/60 border border-white/5 p-3 rounded-2xl backdrop-blur-xl shrink-0">
                                <div className="flex items-center gap-4">
                                    <div className="h-8 w-8 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                                        <MonitorPlay className="h-4 w-4 text-cyan-400" />
                                    </div>
                                    <div className="space-y-0.5">
                                        <h2 className="text-[11px] font-black text-white uppercase tracking-[0.2em]">{selectedResult?.filename || "Archive Null"}</h2>
                                        <p className="text-[7px] font-black text-slate-500 uppercase tracking-widest">Master Sequence // {selectedResult ? formatDate(selectedResult.created_at) : "-"}</p>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button onClick={() => selectedResult && downloadFile(selectedResult.url, selectedResult.filename)} className="h-8 px-4 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-[8px] font-black uppercase tracking-widest text-white transition-all">Download</button>
                                    <button onClick={() => selectedResult && deleteResult(selectedResult.filename)} className="h-8 w-8 bg-red-500/10 hover:bg-red-500 border border-red-500/20 rounded-lg flex items-center justify-center text-red-500 hover:text-white transition-all"><Trash2 className="h-3.5 w-3.5" /></button>
                                </div>
                            </div>

                            <div className="flex-1 bg-black rounded-[2rem] overflow-hidden border border-white/5 shadow-3xl flex items-center justify-center">
                                {selectedResult ? (
                                    <video key={selectedResult?.url} src={`http://localhost:8000${selectedResult?.url}`} className="w-full h-full object-contain" controls />
                                ) : (
                                    <span className="text-[10px] font-black text-slate-800 tracking-[1em]">NO_SELECTION</span>
                                )}
                            </div>
                        </div>
                    </div>
                </section>

                {/* Master Index (Right) */}
                <section className="w-[320px] flex flex-col bg-black/20">
                    <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-black/40">
                        <div className="flex items-center gap-2">
                            <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/70">Project Index</h3>
                        </div>
                        <span className="text-[8px] font-black text-cyan-500 shadow-[0_0_10px_rgba(34,211,238,0.2)] bg-cyan-500/5 px-2 py-1 rounded border border-cyan-500/10">{results.length}</span>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                        {results.map((project) => {
                            const isSelected = selectedResult?.filename === project.filename;
                            return (
                                <button
                                    key={project.filename}
                                    onClick={() => setSelectedResult(project)}
                                    className={cn(
                                        "w-full rounded-xl p-3 text-left transition-all duration-300 border group",
                                        isSelected ? "bg-cyan-600/10 border-cyan-500/40" : "bg-black/30 border-white/[0.03] hover:border-white/10"
                                    )}
                                >
                                    <div className="aspect-video rounded-lg bg-black overflow-hidden border border-white/5 relative mb-2">
                                        <video src={`http://localhost:8000${project.url}`} className="w-full h-full object-cover opacity-30" />
                                    </div>
                                    <h4 className={cn("text-[8px] font-black uppercase tracking-widest truncate", isSelected ? "text-cyan-400" : "text-slate-500 group-hover:text-white transition-colors")}>{project.filename}</h4>
                                    <p className="text-[6px] font-bold text-slate-700 uppercase mt-1">{formatSize(project.size)} // {formatDate(project.created_at)}</p>
                                </button>
                            );
                        })}
                    </div>
                </section>
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
