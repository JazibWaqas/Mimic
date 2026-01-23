"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import {
    Trash2,
    Search,
    ChevronDown,
    Plus,
    Activity,
    Database,
    Zap,
    Target,
    Layers,
    Info,
    History
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Clip, Reference, Result } from "@/lib/types";

type AssetItem = Clip | Reference | Result;

export default function LibraryPage() {
    const router = useRouter();
    const [clips, setClips] = useState<Clip[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [results, setResults] = useState<Result[]>([]);
    const [allItems, setAllItems] = useState<AssetItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [showTypeMenu, setShowTypeMenu] = useState(false);
    const typeMenuRef = useRef<HTMLDivElement>(null);

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
            toast.error("Telemetry Sync Failed");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchAllAssets(); }, []);

    useEffect(() => {
        let items: AssetItem[] = [];
        if (selectedCategory === null) items = [...clips, ...references, ...results];
        else if (selectedCategory === "raw_samples") items = [...clips];
        else if (selectedCategory === "references") items = [...references];
        else if (selectedCategory === "synthesis_output") items = [...results];

        if (searchQuery.trim()) {
            items = items.filter(item => item.filename.toLowerCase().includes(searchQuery.toLowerCase()));
        }

        const sorted = items.sort((a, b) => (b.created_at || 0) - (a.created_at || 0));
        setAllItems(sorted);
    }, [searchQuery, clips, references, results, selectedCategory]);

    const deleteItem = async (sessionId: string, filename: string) => {
        if (!confirm("Execute asset termination?")) return;
        try {
            await api.deleteClip(sessionId, filename);
            fetchAllAssets();
            toast.success("Asset terminated");
        } catch (err) {
            toast.error("Termination failed");
        }
    };

    const getItemType = (item: AssetItem): "Raw Sample" | "Reference" | "Synthesis Output" => {
        if ("session_id" in item) return "Raw Sample";
        if ("url" in item) return "Synthesis Output";
        return "Reference";
    };

    const handleItemClick = (item: AssetItem) => {
        const type = getItemType(item) === 'Raw Sample' ? 'clips' : getItemType(item) === 'Synthesis Output' ? 'results' : 'references';
        router.push(`/vault?filename=${encodeURIComponent(item.filename)}&type=${type}`);
    };

    const renderCard = (item: AssetItem, idx: number) => {
        const itemId = "session_id" in item ? `${item.session_id}-${item.filename}` : item.filename;
        const type = getItemType(item);
        const path = "path" in item ? item.path : (item as any).url;

        return (
            <Card key={`${itemId}-${idx}`} onClick={() => handleItemClick(item)} className="group bg-[#15192d] border border-white/5 rounded-2xl overflow-hidden transition-all duration-300 hover:border-indigo-500/40 hover:shadow-[0_0_30px_rgba(99,102,241,0.1)] flex flex-col cursor-pointer relative">
                <div className="w-full aspect-[16/10] bg-black relative group/video border-b border-white/5 overflow-hidden">
                    <video
                        src={`http://localhost:8000${path}`}
                        className="w-full h-full object-cover opacity-60 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700"
                        muted
                        onMouseOver={(e) => e.currentTarget.play().catch(() => { })}
                        onMouseOut={(e) => { e.currentTarget.pause(); e.currentTarget.currentTime = 0; }}
                    />
                    <div className="absolute top-2 left-2">
                        <div className={cn(
                            "px-2 py-1 rounded-lg text-[8px] font-black uppercase tracking-widest backdrop-blur-md border border-white/10 shadow-xl",
                            type === 'Raw Sample' ? 'text-cyan-400 bg-cyan-500/20' :
                                type === 'Reference' ? 'text-indigo-400 bg-indigo-500/20' :
                                    'text-purple-400 bg-purple-500/20'
                        )}>
                            {type}
                        </div>
                    </div>
                </div>

                <div className="p-4 space-y-3">
                    <div className="flex items-center justify-between gap-2">
                        <h3 className="text-[10px] font-black text-white/90 truncate tracking-tighter uppercase">{item.filename}</h3>
                        <div className="flex opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onClick={(e) => { e.stopPropagation(); deleteItem((item as any).session_id || 'samples', item.filename); }} className="p-1.5 rounded-lg text-slate-700 hover:text-red-500 transition-all"><Trash2 className="h-3 w-3" /></button>
                        </div>
                    </div>
                    <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest text-slate-600">
                        <span>{(item.size / (1024 * 1024)).toFixed(1)} MB</span>
                        <span className="opacity-20">|</span>
                        <span>{new Date(item.created_at * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                    </div>
                </div>
            </Card>
        );
    };

    return (
        <div className="min-h-[calc(100vh-80px)] flex flex-col mx-auto max-w-[1500px] border-x border-white/5 px-8 pt-8 bg-black/20">
            {/* Header */}
            <div className="flex flex-col gap-8 mb-10">
                <div className="flex items-center justify-between border-b border-white/5 pb-8">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-[0_0_20px_rgba(79,70,229,0.5)] border border-white/10">
                                <Database className="h-5 w-5 text-white" />
                            </div>
                            <h1 className="text-2xl font-black tracking-tighter text-white uppercase italic">Library</h1>
                        </div>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.4em] max-w-xl leading-relaxed">Compressed Asset Index. Real-time access to the neural agent's synchronized data points.</p>
                    </div>

                    <div className="flex gap-4">
                        <div className="px-6 py-3 rounded-2xl bg-[#15192d] border border-indigo-500/20 flex items-center gap-4 shadow-xl">
                            <div className="text-right">
                                <p className="text-[8px] font-black text-slate-500 uppercase">Total Samples</p>
                                <p className="text-sm font-black text-white">{allItems.length}</p>
                            </div>
                            <Activity className="h-5 w-5 text-indigo-400" />
                        </div>
                    </div>
                </div>

                <div className="flex gap-4 items-center">
                    <div className="relative flex-1">
                        <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-600" />
                        <input
                            type="text"
                            placeholder="QUERY INDEX SYSTEM..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full h-12 bg-[#15192d] border border-white/10 rounded-2xl pl-14 pr-6 text-[11px] font-black text-white placeholder:text-slate-700 outline-none focus:border-indigo-500/40 transition-all uppercase tracking-widest"
                        />
                    </div>

                    <div className="relative">
                        <button
                            onClick={() => setShowTypeMenu(!showTypeMenu)}
                            className="h-12 px-8 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] hover:scale-105 transition-all flex items-center gap-4 border border-white/10 shadow-[0_0_30px_rgba(79,70,229,0.3)]"
                        >
                            <span>{selectedCategory ? selectedCategory.replace('_', ' ') : 'ALL DATA'}</span>
                            <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", showTypeMenu && "rotate-180")} />
                        </button>
                        {showTypeMenu && (
                            <div className="absolute right-0 top-[calc(100%+12px)] w-64 bg-[#15192d] border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden p-2">
                                {[
                                    { id: 'All', label: 'All Sources' },
                                    { id: 'raw_samples', label: 'Raw Samples' },
                                    { id: 'references', label: 'References' },
                                    { id: 'synthesis_output', label: 'Synthesis Output' }
                                ].map((cat) => (
                                    <button
                                        key={cat.id}
                                        onClick={() => { setSelectedCategory(cat.id === 'All' ? null : cat.id); setShowTypeMenu(false); }}
                                        className="w-full text-left px-5 py-3 text-[10px] font-black uppercase tracking-widest text-slate-500 hover:bg-indigo-600 hover:text-white rounded-xl transition-all"
                                    >
                                        {cat.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Grid */}
            <div className="flex-1 pb-16">
                {allItems.length === 0 ? (
                    <div className="h-64 flex flex-col items-center justify-center border border-dashed border-white/5 rounded-[3rem] text-slate-800 text-[10px] font-black uppercase tracking-[0.5em]">System Archive Empty</div>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5">
                        {allItems.map((item, idx) => renderCard(item, idx))}
                    </div>
                )}
            </div>
        </div>
    );
}
