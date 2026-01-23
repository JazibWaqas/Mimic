"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import {
    Trash2,
    Search,
    Filter,
    X,
    Edit2,
    Check,
    Eye,
    Tag
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Clip, Reference, Result } from "@/lib/types";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ChevronDown } from "lucide-react";

const MOCK_TAGS = ["High Energy", "Aesthetic", "Nature", "Urban", "Cinematic", "Fast Pace", "Ambient"];

type AssetItem = Clip | Reference | Result;

export default function AssetsPage() {
    const router = useRouter();
    const [clips, setClips] = useState<Clip[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [results, setResults] = useState<Result[]>([]);
    const [recentItems, setRecentItems] = useState<AssetItem[]>([]);
    const [allItems, setAllItems] = useState<AssetItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [showFilters, setShowFilters] = useState(false);
    const [showTypeMenu, setShowTypeMenu] = useState(false);
    const [renamingId, setRenamingId] = useState<string | null>(null);
    const [newName, setNewName] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const typeMenuRef = useRef<HTMLDivElement>(null);

    const fetchAllAssets = async () => {
        try {
            const [clipsData, refsData, resultsData] = await Promise.all([
                api.fetchClips(),
                api.fetchReferences(),
                api.fetchResults()
            ]);
            
            const rawClips = clipsData.clips || [];
            const clipsWithTags = rawClips.map((c: Clip, i: number) => ({
                ...c,
                tags: [MOCK_TAGS[i % MOCK_TAGS.length]]
            }));
            
            setClips(clipsWithTags);
            setReferences(refsData.references || []);
            setResults(resultsData.results || []);
        } catch (err) {
            toast.error("Failed to load library");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAllAssets();
    }, []);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (typeMenuRef.current && !typeMenuRef.current.contains(event.target as Node)) {
                setShowTypeMenu(false);
            }
        };

        if (showTypeMenu) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [showTypeMenu]);

    useEffect(() => {
        let items: AssetItem[] = [];
        
        if (selectedCategory === null) {
            items = [...clips, ...references, ...results];
        } else if (selectedCategory === "clips") {
            items = [...clips];
        } else if (selectedCategory === "references") {
            items = [...references];
        } else if (selectedCategory === "results") {
            items = [...results];
        }
        
        if (searchQuery.trim()) {
            items = items.filter(item => 
                item.filename.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }
        
        if (selectedTags.length > 0) {
            items = items.filter(item => 
                "tags" in item && item.tags?.some(tag => selectedTags.includes(tag))
            );
        }
        
        const sorted = items.sort((a, b) => b.created_at - a.created_at);
        setRecentItems(sorted.slice(0, 4));
        setAllItems(sorted);
    }, [searchQuery, selectedTags, clips, references, results, selectedCategory]);

    const toggleTag = (tag: string) => {
        setSelectedTags(prev => 
            prev.includes(tag) 
                ? prev.filter(t => t !== tag)
                : [...prev, tag]
        );
    };

    const clearFilters = () => {
        setSelectedTags([]);
        setSearchQuery("");
    };

    const handleCategorySelect = (category: string | null) => {
        setSelectedCategory(category);
        setShowTypeMenu(false);
    };

    const getCategoryLabel = () => {
        if (selectedCategory === "clips") return "Source Clips";
        if (selectedCategory === "references") return "Reference Videos";
        if (selectedCategory === "results") return "Generated Videos";
        return "All Categories";
    };

    const deleteClip = async (sessionId: string, filename: string) => {
        if (!confirm("Delete this video?")) return;
        try {
            await api.deleteClip(sessionId, filename);
            fetchAllAssets();
            toast.success("Video deleted");
        } catch (err) {
            toast.error("Delete failed");
        }
    };

    const handleRename = async (item: AssetItem) => {
        if ("session_id" in item) {
            setClips(prev => prev.map(c => c.filename === item.filename && c.session_id === item.session_id ? { ...c, filename: newName } : c));
        }
        setRenamingId(null);
        toast.success("Metadata Updated");
    };

    const getItemPath = (item: AssetItem): string => {
        if ("path" in item) return item.path;
        if ("url" in item) return item.url;
        return "";
    };

    const getItemSessionId = (item: AssetItem): string => {
        if ("session_id" in item) return item.session_id;
        return "samples";
    };

    const getItemType = (item: AssetItem): "clips" | "references" | "results" => {
        if ("session_id" in item) return "clips";
        if ("url" in item) return "results";
        return "references";
    };

    const handleItemClick = (item: AssetItem) => {
        const type = getItemType(item);
        router.push(`/vault?filename=${encodeURIComponent(item.filename)}&type=${type}`);
    };

    const formatSize = (bytes: number) => (bytes / (1024 * 1024)).toFixed(1) + " MB";
    const formatDate = (timestamp: number) => new Date(timestamp * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' });

    const totalCount = clips.length + references.length + results.length;

    return (
        <div className="min-h-[calc(100vh-80px)] flex flex-col bg-black/20 mx-auto max-w-[1600px] border-x border-white/5 shadow-2xl">

            {/* Header */}
            <div className="shrink-0 p-8 border-b border-white/5 bg-black/40 backdrop-blur-xl">
                <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-8 mb-6">
                    <div className="space-y-1">
                        <h1 className="text-2xl font-black tracking-tighter uppercase shiny-text">Library</h1>
                        <p className="text-[9px] font-black uppercase tracking-[0.3em] text-slate-500">{totalCount} Videos Indexed</p>
                    </div>
                </div>

                {/* Search Bar with Filters and Type Buttons */}
                <div className="flex gap-4">
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
                    <div className="relative" ref={typeMenuRef}>
                        <button
                            onClick={() => setShowTypeMenu(!showTypeMenu)}
                            className={cn(
                                "h-12 px-6 bg-black/40 border border-white/5 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all flex items-center gap-2",
                                selectedCategory !== null
                                    ? "bg-indigo-500/10 border-indigo-500/40 text-white" 
                                    : "text-slate-500 hover:border-white/10"
                            )}
                        >
                            <span>Category</span>
                            <ChevronDown className={cn("h-4 w-4 transition-transform", showTypeMenu && "rotate-180")} />
                        </button>
                        {showTypeMenu && (
                            <div className="absolute right-0 top-full mt-2 w-48 bg-black/90 border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden">
                                <button
                                    onClick={() => handleCategorySelect(null)}
                                    className={cn(
                                        "w-full text-left px-4 py-3 text-[10px] font-bold uppercase tracking-widest transition-all",
                                        selectedCategory === null
                                            ? "bg-indigo-500/20 text-white"
                                            : "text-slate-400 hover:bg-white/5 hover:text-white"
                                    )}
                                >
                                    All Categories
                                </button>
                                <button
                                    onClick={() => handleCategorySelect("clips")}
                                    className={cn(
                                        "w-full text-left px-4 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-t border-white/5",
                                        selectedCategory === "clips"
                                            ? "bg-indigo-500/20 text-white"
                                            : "text-slate-400 hover:bg-white/5 hover:text-white"
                                    )}
                                >
                                    Source Clips
                                </button>
                                <button
                                    onClick={() => handleCategorySelect("references")}
                                    className={cn(
                                        "w-full text-left px-4 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-t border-white/5",
                                        selectedCategory === "references"
                                            ? "bg-indigo-500/20 text-white"
                                            : "text-slate-400 hover:bg-white/5 hover:text-white"
                                    )}
                                >
                                    Reference Videos
                                </button>
                                <button
                                    onClick={() => handleCategorySelect("results")}
                                    className={cn(
                                        "w-full text-left px-4 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-t border-white/5",
                                        selectedCategory === "results"
                                            ? "bg-indigo-500/20 text-white"
                                            : "text-slate-400 hover:bg-white/5 hover:text-white"
                                    )}
                                >
                                    Generated Videos
                                </button>
                            </div>
                        )}
                    </div>
                    <button
                        onClick={() => setShowFilters(true)}
                        className={cn(
                            "h-12 px-6 bg-black/40 border border-white/5 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all flex items-center gap-2",
                            selectedTags.length > 0 
                                ? "bg-indigo-500/10 border-indigo-500/40 text-white" 
                                : "text-slate-500 hover:border-white/10"
                        )}
                    >
                        <Filter className="h-4 w-4" />
                        Filters {selectedTags.length > 0 && `(${selectedTags.length})`}
                    </button>
                </div>
            </div>

            {/* Filters Dialog */}
            <Dialog open={showFilters} onOpenChange={setShowFilters}>
                <DialogContent className="bg-black/90 border-white/10 max-w-md">
                    <DialogHeader>
                        <DialogTitle className="text-white uppercase tracking-widest text-sm">Filters</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">Tags</h3>
                            <div className="grid grid-cols-2 gap-2">
                                {MOCK_TAGS.map(tag => (
                                    <label
                                        key={tag}
                                        className={cn(
                                            "flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all",
                                            selectedTags.includes(tag)
                                                ? "bg-indigo-500/10 border-indigo-500/40"
                                                : "bg-black/40 border-white/5 hover:border-white/10"
                                        )}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={selectedTags.includes(tag)}
                                            onChange={() => toggleTag(tag)}
                                            className="w-4 h-4 rounded border-white/20 bg-black/40 text-indigo-500 focus:ring-indigo-500"
                                        />
                                        <span className={cn(
                                            "text-[9px] font-black uppercase tracking-widest",
                                            selectedTags.includes(tag) ? "text-indigo-400" : "text-slate-400"
                                        )}>
                                            {tag}
                                        </span>
                                    </label>
                                ))}
                            </div>
                        </div>
                        {selectedTags.length > 0 && (
                            <button
                                onClick={clearFilters}
                                className="w-full px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-lg text-[9px] font-bold uppercase tracking-widest text-red-400 transition-all"
                            >
                                Clear All Filters
                            </button>
                        )}
                    </div>
                </DialogContent>
            </Dialog>

            {/* Content Area */}
            <div className="flex-1 min-h-0 overflow-y-auto p-8 custom-scrollbar">
                
                {/* Recently Uploaded Section */}
                <section className="mb-8">
                    <h2 className="text-xl font-bold text-white mb-4">Recently Uploaded</h2>
                    {loading ? (
                        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {[...Array(4)].map((_, i) => (
                                <div key={i} className="max-w-[260px] mx-auto w-full min-h-[160px] rounded-xl bg-white/[0.02] animate-pulse border border-white/5" />
                            ))}
                        </div>
                    ) : recentItems.length === 0 ? (
                        <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
                            No recent items
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {recentItems.map((item, idx) => {
                                const itemId = "session_id" in item ? `${item.session_id}-${item.filename}` : item.filename;
                                return (
                                    <Card key={`recent-${itemId}-${idx}`} onClick={() => handleItemClick(item)} className="group max-w-[260px] w-full mx-auto bg-black/40 border border-white/[0.03] rounded-xl overflow-hidden transition-all duration-300 hover:scale-[1.03] hover:border-indigo-500/30 hover:shadow-lg flex flex-col min-h-[160px] cursor-pointer">
                                        <div className="w-full h-32 bg-black relative group/video border-b border-white/[0.03] flex-shrink-0">
                                            <video
                                                src={`http://localhost:8000${getItemPath(item)}`}
                                                className="w-full h-full object-cover opacity-50 group-hover:opacity-90 transition-opacity"
                                                muted 
                                                onMouseOver={(e) => {
                                                    const video = e.currentTarget;
                                                    video.play().catch(() => {});
                                                }}
                                                onMouseOut={(e) => {
                                                    const video = e.currentTarget;
                                                    video.pause();
                                                    video.currentTime = 0;
                                                }}
                                            />
                                        </div>
                                        <div className="p-3 flex flex-col flex-1 gap-2">
                                            <div className="flex-1">
                                                {renamingId === itemId ? (
                                                    <div className="flex items-center gap-1 mb-1">
                                                        <input autoFocus value={newName} onChange={(e) => { e.stopPropagation(); setNewName(e.target.value); }} onClick={(e) => e.stopPropagation()} className="w-full bg-white/5 border border-indigo-500/30 rounded px-2 py-1 text-[9px] font-black text-white uppercase tracking-widest outline-none" />
                                                        <button onClick={(e) => { e.stopPropagation(); handleRename(item); }} className="text-green-500"><Check className="h-3 w-3" /></button>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center justify-between gap-2 group/name mb-1">
                                                        <h3 className="text-[10px] font-black uppercase tracking-widest text-white/70 truncate group-hover/name:text-indigo-400">{item.filename}</h3>
                                                        {"session_id" in item && (
                                                            <button onClick={(e) => { e.stopPropagation(); setRenamingId(itemId); setNewName(item.filename); }} className="opacity-0 group-hover/name:opacity-100"><Edit2 className="h-3 w-3 text-slate-600" /></button>
                                                        )}
                                                    </div>
                                                )}
                                                {"tags" in item && item.tags && (
                                                    <div className="flex flex-wrap gap-1 mb-2">
                                                        {item.tags.map(t => <span key={t} className="text-[7px] font-black uppercase text-cyan-500/60 flex items-center gap-1"><Tag className="h-2 w-2" />{t}</span>)}
                                                    </div>
                                                )}
                                            </div>
                                            <div className="flex items-center justify-between border-t border-white/5 pt-2 mt-auto">
                                                <span className="text-[8px] font-bold text-slate-700 uppercase">{formatSize(item.size)} // {formatDate(item.created_at)}</span>
                                                <div className="flex gap-2">
                                                    <button onClick={(e) => { e.stopPropagation(); window.open(`http://localhost:8000${getItemPath(item)}`, '_blank'); }} className="text-slate-500 hover:text-white transition-colors"><Eye className="h-3 w-3" /></button>
                                                    {"session_id" in item && (
                                                        <button onClick={(e) => { e.stopPropagation(); deleteClip(item.session_id, item.filename); }} className="text-slate-700 hover:text-red-500 transition-colors"><Trash2 className="h-3 w-3" /></button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </Card>
                                );
                            })}
                        </div>
                    )}
                </section>

                {/* All Files Section */}
                <section>
                    <h2 className="text-xl font-bold text-white mb-4">All Files</h2>
                    {loading ? (
                        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {[...Array(16)].map((_, i) => (
                                <div key={i} className="max-w-[260px] mx-auto w-full min-h-[160px] rounded-xl bg-white/[0.02] animate-pulse border border-white/5" />
                            ))}
                        </div>
                    ) : allItems.length === 0 ? (
                        <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
                            No items found matching your criteria
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {allItems.map((item, idx) => {
                                const itemId = "session_id" in item ? `${item.session_id}-${item.filename}` : item.filename;
                                return (
                                    <Card key={`all-${itemId}-${idx}`} onClick={() => handleItemClick(item)} className="group max-w-[260px] w-full mx-auto bg-black/40 border border-white/[0.03] rounded-xl overflow-hidden transition-all duration-300 hover:scale-[1.03] hover:border-indigo-500/30 hover:shadow-lg flex flex-col min-h-[160px] cursor-pointer">
                                        <div className="w-full h-32 bg-black relative group/video border-b border-white/[0.03] flex-shrink-0">
                                            <video
                                                src={`http://localhost:8000${getItemPath(item)}`}
                                                className="w-full h-full object-cover opacity-50 group-hover:opacity-90 transition-opacity"
                                                muted 
                                                onMouseOver={(e) => {
                                                    const video = e.currentTarget;
                                                    video.play().catch(() => {});
                                                }}
                                                onMouseOut={(e) => {
                                                    const video = e.currentTarget;
                                                    video.pause();
                                                    video.currentTime = 0;
                                                }}
                                            />
                                        </div>
                                        <div className="p-3 flex flex-col flex-1 gap-2">
                                            <div className="flex-1">
                                                {renamingId === itemId ? (
                                                    <div className="flex items-center gap-1 mb-1">
                                                        <input autoFocus value={newName} onChange={(e) => { e.stopPropagation(); setNewName(e.target.value); }} onClick={(e) => e.stopPropagation()} className="w-full bg-white/5 border border-indigo-500/30 rounded px-2 py-1 text-[9px] font-black text-white uppercase tracking-widest outline-none" />
                                                        <button onClick={(e) => { e.stopPropagation(); handleRename(item); }} className="text-green-500"><Check className="h-3 w-3" /></button>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center justify-between gap-2 group/name mb-1">
                                                        <h3 className="text-[10px] font-black uppercase tracking-widest text-white/70 truncate group-hover/name:text-indigo-400">{item.filename}</h3>
                                                        {"session_id" in item && (
                                                            <button onClick={(e) => { e.stopPropagation(); setRenamingId(itemId); setNewName(item.filename); }} className="opacity-0 group-hover/name:opacity-100"><Edit2 className="h-3 w-3 text-slate-600" /></button>
                                                        )}
                                                    </div>
                                                )}
                                                {"tags" in item && item.tags && (
                                                    <div className="flex flex-wrap gap-1 mb-2">
                                                        {item.tags.map(t => <span key={t} className="text-[7px] font-black uppercase text-cyan-500/60 flex items-center gap-1"><Tag className="h-2 w-2" />{t}</span>)}
                                                    </div>
                                                )}
                                            </div>
                                            <div className="flex items-center justify-between border-t border-white/5 pt-2 mt-auto">
                                                <span className="text-[8px] font-bold text-slate-700 uppercase">{formatSize(item.size)} // {formatDate(item.created_at)}</span>
                                                <div className="flex gap-2">
                                                    <button onClick={(e) => { e.stopPropagation(); window.open(`http://localhost:8000${getItemPath(item)}`, '_blank'); }} className="text-slate-500 hover:text-white transition-colors"><Eye className="h-3 w-3" /></button>
                                                    {"session_id" in item && (
                                                        <button onClick={(e) => { e.stopPropagation(); deleteClip(item.session_id, item.filename); }} className="text-slate-700 hover:text-red-500 transition-colors"><Trash2 className="h-3 w-3" /></button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </Card>
                                );
                            })}
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
}
