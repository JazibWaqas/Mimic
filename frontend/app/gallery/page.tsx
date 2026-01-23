"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import {
    Trash2,
    Search,
    Filter,
    Calendar,
    HardDrive,
    Edit2,
    Check,
    X,
    Eye,
    Tag,
    MonitorPlay,
    FileVideo
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface Clip {
    session_id: string;
    filename: string;
    path: string;
    size: number;
    created_at: number;
    tags?: string[];
}

const MOCK_TAGS = ["High Energy", "Aesthetic", "Nature", "Urban", "Cinematic", "Fast Pace", "Ambient"];

export default function AssetsPage() {
    const [clips, setClips] = useState<Clip[]>([]);
    const [filteredClips, setFilteredClips] = useState<Clip[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedTag, setSelectedTag] = useState<string | null>(null);
    const [renamingId, setRenamingId] = useState<string | null>(null);
    const [newName, setNewName] = useState("");

    const fetchClips = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/clips");
            const data = await res.json();
            const rawClips = data.clips || [];
            const clipsWithTags = rawClips.map((c: Clip, i: number) => ({
                ...c,
                tags: [MOCK_TAGS[i % MOCK_TAGS.length]]
            }));
            setClips(clipsWithTags);
            setFilteredClips(clipsWithTags);
        } catch (err) {
            toast.error("Telemetry Error: Failed to acquire assets");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClips();
    }, []);

    useEffect(() => {
        let result = clips;
        if (searchQuery) result = result.filter(c => c.filename.toLowerCase().includes(searchQuery.toLowerCase()));
        if (selectedTag) result = result.filter(c => c.tags?.includes(selectedTag));
        setFilteredClips(result);
    }, [searchQuery, selectedTag, clips]);

    const deleteClip = async (sessionId: string, filename: string) => {
        if (!confirm("Confirm Asset Deletion?")) return;
        try {
            const res = await fetch(`http://localhost:8000/api/clips/${sessionId}/${filename}`, { method: "DELETE" });
            if (res.ok) { fetchClips(); toast.success("Asset Purged"); }
        } catch (err) { toast.error("Purge Failed"); }
    };

    const handleRename = async (clip: Clip) => {
        setClips(prev => prev.map(c => c.filename === clip.filename && c.session_id === clip.session_id ? { ...c, filename: newName } : c));
        setRenamingId(null);
        toast.success("Metadata Updated");
    };

    const formatSize = (bytes: number) => (bytes / (1024 * 1024)).toFixed(1) + " MB";
    const formatDate = (timestamp: number) => new Date(timestamp * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' });

    return (
        <div className="h-[calc(100vh-100px)] flex flex-col bg-black/20 overflow-hidden mx-auto max-w-[1600px] border-x border-white/5 shadow-2xl">

            {/* Search & Filter Header */}
            <div className="shrink-0 p-8 border-b border-white/5 bg-black/40 backdrop-blur-xl">
                <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-8">
                    <div className="space-y-1">
                        <h1 className="text-2xl font-black tracking-tighter uppercase shiny-text">Assets</h1>
                        <p className="text-[9px] font-black uppercase tracking-[0.3em] text-slate-500">{clips.length} Neural Seeds Indexed</p>
                    </div>

                    <div className="flex flex-col md:flex-row gap-4 flex-1 max-w-[900px]">
                        <div className="relative flex-1 group">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 group-hover:text-indigo-400 transition-colors" />
                            <input
                                type="text"
                                placeholder="Search index..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full h-12 bg-black/40 border border-white/5 rounded-xl pl-12 pr-4 text-[10px] font-bold uppercase tracking-widest text-white placeholder:text-slate-700 outline-none focus:border-indigo-500/30 transition-all"
                            />
                        </div>
                        <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar md:w-[400px]">
                            <button onClick={() => setSelectedTag(null)} className={cn("px-4 py-2 h-10 rounded-lg border text-[8px] font-black uppercase tracking-widest shrink-0 transition-all", !selectedTag ? "bg-indigo-500/10 border-indigo-500/40 text-white" : "border-white/5 text-slate-500")}>All</button>
                            {MOCK_TAGS.map(t => (
                                <button key={t} onClick={() => setSelectedTag(t)} className={cn("px-4 py-2 h-10 rounded-lg border text-[8px] font-black uppercase tracking-widest shrink-0 transition-all", selectedTag === t ? "bg-cyan-500/10 border-cyan-500/40 text-white" : "border-white/5 text-slate-500")}>{t}</button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Internal Scroll Grid */}
            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                {loading ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
                        {[...Array(16)].map((_, i) => <div key={i} className="aspect-[4/5] rounded-2xl bg-white/[0.02] animate-pulse border border-white/5" />)}
                    </div>
                ) : filteredClips.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center opacity-20"><p className="text-[10px] font-black uppercase tracking-widest">Index Null</p></div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-6">
                        {filteredClips.map((clip, idx) => (
                            <Card key={`${clip.session_id}-${idx}`} className="group p-0 bg-black/40 border border-white/[0.03] rounded-2xl overflow-hidden transition-all duration-500 hover:scale-[1.05] hover:border-indigo-500/30">
                                <div className="aspect-video bg-black relative group/video border-b border-white/[0.03]">
                                    <video
                                        src={`http://localhost:8000${clip.path}`}
                                        className="w-full h-full object-cover opacity-50 group-hover:opacity-90 transition-all"
                                        muted onMouseOver={(e) => e.currentTarget.play()} onMouseOut={(e) => { e.currentTarget.pause(); e.currentTarget.currentTime = 0; }}
                                    />
                                </div>
                                <div className="p-4 space-y-4">
                                    <div className="space-y-1.5 min-h-[40px]">
                                        {renamingId === clip.session_id + clip.filename ? (
                                            <div className="flex items-center gap-1">
                                                <input autoFocus value={newName} onChange={(e) => setNewName(e.target.value)} className="w-full bg-white/5 border border-indigo-500/30 rounded px-2 py-1 text-[8px] font-black text-white uppercase tracking-widest outline-none" />
                                                <button onClick={() => handleRename(clip)} className="text-green-500"><Check className="h-3 w-3" /></button>
                                            </div>
                                        ) : (
                                            <div className="flex items-center justify-between gap-2 group/name">
                                                <h3 className="text-[9px] font-black uppercase tracking-widest text-white/70 truncate group-hover/name:text-indigo-400">{clip.filename}</h3>
                                                <button onClick={() => { setRenamingId(clip.session_id + clip.filename); setNewName(clip.filename); }} className="opacity-0 group-hover/name:opacity-100"><Edit2 className="h-2.5 w-2.5 text-slate-600" /></button>
                                            </div>
                                        )}
                                        <div className="flex gap-2">
                                            {clip.tags?.map(t => <span key={t} className="text-[7px] font-black uppercase text-cyan-500/60 flex items-center gap-1"><Tag className="h-2 w-2" />{t}</span>)}
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between border-t border-white/5 pt-3">
                                        <span className="text-[7px] font-bold text-slate-700 uppercase">{formatSize(clip.size)} // {formatDate(clip.created_at)}</span>
                                        <div className="flex gap-2">
                                            <button onClick={() => window.open(`http://localhost:8000${clip.path}`, '_blank')} className="text-slate-500 hover:text-white"><Eye className="h-3 w-3" /></button>
                                            <button onClick={() => deleteClip(clip.session_id, clip.filename)} className="text-slate-700 hover:text-red-500"><Trash2 className="h-3 w-3" /></button>
                                        </div>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </div>

        </div>
    );
}
