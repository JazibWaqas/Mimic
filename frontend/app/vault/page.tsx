"use client";

import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import {
    Trash2,
    Download,
    Video,
    ChevronLeft,
    ChevronRight,
    HardDrive,
    Calendar,
    Columns2,
    X,
    ChevronDown
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Result, Reference, Clip } from "@/lib/types";

type ViewMode = "results" | "references" | "clips";

export default function ProjectsPage() {
    const searchParams = useSearchParams();
    const [results, setResults] = useState<Result[]>([]);
    const [references, setReferences] = useState<Reference[]>([]);
    const [clips, setClips] = useState<Clip[]>([]);
    const [selectedItem, setSelectedItem] = useState<Result | Reference | Clip | null>(null);
    const [selectedItem2, setSelectedItem2] = useState<Result | Reference | Clip | null>(null);
    const [sideBySideMode, setSideBySideMode] = useState(false);
    const [showLeftDropdown, setShowLeftDropdown] = useState(false);
    const [showRightDropdown, setShowRightDropdown] = useState(false);
    const [viewMode, setViewMode] = useState<ViewMode>("results");
    const [loading, setLoading] = useState(true);
    const scrollRef = useRef<HTMLDivElement>(null);
    const leftDropdownRef = useRef<HTMLDivElement>(null);
    const rightDropdownRef = useRef<HTMLDivElement>(null);

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
                    const item = dataProjects.results?.find(r => r.filename === filename);
                    if (item) {
                        setSelectedItem(item);
                        setViewMode("results");
                    }
                } else if (type === "references") {
                    const item = dataRefs.references?.find(r => r.filename === filename);
                    if (item) {
                        setSelectedItem(item);
                        setViewMode("references");
                    }
                } else if (type === "clips") {
                    const item = dataClips.clips?.find(c => c.filename === filename);
                    if (item) {
                        setSelectedItem(item);
                        setViewMode("clips");
                    }
                }
            } else {
                if (viewMode === "results" && dataProjects.results?.[0]) {
                    setSelectedItem(dataProjects.results[0]);
                } else if (viewMode === "references" && dataRefs.references?.[0]) {
                    setSelectedItem(dataRefs.references[0]);
                } else if (viewMode === "clips" && dataClips.clips?.[0]) {
                    setSelectedItem(dataClips.clips[0]);
                }
            }
        } catch (err) {
            toast.error("Failed to load videos");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchData(); }, [searchParams]);

    useEffect(() => {
        if (viewMode === "results" && results.length > 0 && !selectedItem) {
            setSelectedItem(results[0]);
        } else if (viewMode === "references" && references.length > 0 && !selectedItem) {
            setSelectedItem(references[0]);
        } else if (viewMode === "clips" && clips.length > 0 && !selectedItem) {
            setSelectedItem(clips[0]);
        }
    }, [viewMode, results, references, clips]);

    const deleteResult = async (filename: string) => {
        if (!confirm("Delete this video?")) return;
        try {
            await api.deleteResult(filename);
            toast.success("Video deleted");
            fetchData();
            if (selectedItem && 'url' in selectedItem && selectedItem.filename === filename) {
                setSelectedItem(null);
            }
        } catch (err) {
            toast.error("Delete failed");
        }
    };

    const formatSize = (bytes: number) => (bytes / (1024 * 1024)).toFixed(1) + " MB";
    const formatDate = (timestamp: number) => new Date(timestamp * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' });

    const getScrollBoxItems = () => {
        if (viewMode === "results") return results;
        if (viewMode === "references") return references;
        return clips;
    };

    const scrollBoxItems = getScrollBoxItems();

    const scrollByAmount = (amount: number) => {
        if (scrollRef.current) {
            scrollRef.current.scrollBy({ left: amount, behavior: 'smooth' });
        }
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (leftDropdownRef.current && !leftDropdownRef.current.contains(event.target as Node)) {
                setShowLeftDropdown(false);
            }
            if (rightDropdownRef.current && !rightDropdownRef.current.contains(event.target as Node)) {
                setShowRightDropdown(false);
            }
        };

        if (showLeftDropdown || showRightDropdown) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [showLeftDropdown, showRightDropdown]);

    const getItemUrl = (item: Result | Reference | Clip) => {
        if ('url' in item) return item.url;
        if ('path' in item) return item.path;
        return "";
    };

    const getItemType = (item: Result | Reference | Clip): "result" | "reference" | "clip" => {
        if ('url' in item) return "result";
        if ('session_id' in item) return "clip";
        return "reference";
    };

    return (
        <div className="min-h-screen flex flex-col bg-black/20">
            <div className="flex-1 flex flex-col max-w-[1700px] mx-auto w-full px-8 py-8">
                
                {/* Filter Tabs and Side-by-Side Toggle */}
                <div className="flex justify-center items-center mb-4 gap-4">
                    <button
                        onClick={() => {
                            setViewMode("results");
                            setSelectedItem(results[0] || null);
                        }}
                        className={cn(
                            "px-6 py-2 rounded-lg text-sm font-bold uppercase tracking-widest transition-all",
                            viewMode === "results" 
                                ? "bg-indigo-600 text-white" 
                                : "bg-black/40 text-slate-500 border border-white/5 hover:border-white/10"
                        )}
                    >
                        Generated Videos ({results.length})
                    </button>
                    <button
                        onClick={() => {
                            setViewMode("references");
                            setSelectedItem(references[0] || null);
                        }}
                        className={cn(
                            "px-6 py-2 rounded-lg text-sm font-bold uppercase tracking-widest transition-all",
                            viewMode === "references" 
                                ? "bg-indigo-600 text-white" 
                                : "bg-black/40 text-slate-500 border border-white/5 hover:border-white/10"
                        )}
                    >
                        Reference Videos ({references.length})
                    </button>
                    <button
                        onClick={() => {
                            setViewMode("clips");
                            setSelectedItem(clips[0] || null);
                        }}
                        className={cn(
                            "px-6 py-2 rounded-lg text-sm font-bold uppercase tracking-widest transition-all",
                            viewMode === "clips" 
                                ? "bg-indigo-600 text-white" 
                                : "bg-black/40 text-slate-500 border border-white/5 hover:border-white/10"
                        )}
                    >
                        Source Clips ({clips.length})
                    </button>
                    <button
                        onClick={() => {
                            setSideBySideMode(!sideBySideMode);
                            if (!sideBySideMode) {
                                if (selectedItem && getItemType(selectedItem) === "result") {
                                    const refs = references;
                                    if (refs.length > 0) {
                                        setSelectedItem2(refs[0]);
                                    }
                                } else if (selectedItem && getItemType(selectedItem) === "reference") {
                                    const res = results;
                                    if (res.length > 0) {
                                        setSelectedItem(res[0]);
                                        setSelectedItem2(selectedItem);
                                    }
                                } else if (results.length > 0 && references.length > 0) {
                                    setSelectedItem(results[0]);
                                    setSelectedItem2(references[0]);
                                }
                            } else {
                                setSelectedItem2(null);
                            }
                        }}
                        className={cn(
                            "px-6 py-2 rounded-lg text-sm font-bold uppercase tracking-widest transition-all flex items-center gap-2",
                            sideBySideMode
                                ? "bg-indigo-600 text-white"
                                : "bg-black/40 text-slate-500 border border-white/5 hover:border-white/10"
                        )}
                    >
                        <Columns2 className="h-4 w-4" />
                        Compare Mode
                    </button>
                </div>

                {/* Horizontal Scroll Box - Only show when not in side-by-side mode */}
                {!sideBySideMode && (
                <div className="relative flex items-center mb-8 min-h-[180px] px-4">
                    <div className="absolute -top-6 left-0 text-sm font-semibold text-white/70">
                        {viewMode === "results" ? "Generated Videos" : viewMode === "references" ? "Reference Videos" : "Source Clips"}
                    </div>
                    <button 
                        onClick={() => scrollByAmount(-260)}
                        className="shrink-0 text-2xl text-indigo-400 hover:text-indigo-300 transition-colors p-2"
                    >
                        <ChevronLeft className="h-6 w-6" />
                    </button>
                    <div 
                        ref={scrollRef}
                        className="flex-1 flex gap-4 overflow-x-auto overflow-y-hidden scroll-smooth no-scrollbar"
                    >
                        {scrollBoxItems.length > 0 ? (
                            scrollBoxItems.map((item) => {
                                const isSelected = selectedItem?.filename === item.filename;
                                const isSelected2 = selectedItem2?.filename === item.filename;
                                const itemUrl = getItemUrl(item);
                                return (
                                    <button
                                        key={item.filename}
                                        onClick={(e) => {
                                            if (sideBySideMode && e.shiftKey) {
                                                setSelectedItem2(item);
                                            } else {
                                                setSelectedItem(item);
                                            }
                                        }}
                                        className={cn(
                                            "shrink-0 w-[240px] h-[160px] rounded-xl border-2 transition-all duration-300 flex flex-col group overflow-hidden",
                                            isSelected 
                                                ? "border-indigo-500 shadow-lg shadow-indigo-500/20 bg-indigo-600/10" 
                                                : isSelected2
                                                ? "border-cyan-500 shadow-lg shadow-cyan-500/20 bg-cyan-600/10"
                                                : "border-white/10 bg-black/40 hover:border-white/20"
                                        )}
                                    >
                                        <div className="w-full flex-1 bg-black rounded-t-xl overflow-hidden relative">
                                            <video 
                                                src={`http://localhost:8000${itemUrl}`}
                                                className="w-full h-full object-cover opacity-50 group-hover:opacity-80 transition-opacity"
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
                                            {isSelected && <div className="absolute inset-0 bg-indigo-500/10" />}
                                            {isSelected2 && <div className="absolute inset-0 bg-cyan-500/10" />}
                                        </div>
                                        <div className="p-2 border-t border-white/5 bg-black/60">
                                            <p className={cn(
                                                "text-[10px] font-black uppercase tracking-widest truncate",
                                                isSelected ? "text-indigo-400" : "text-slate-400"
                                            )}>
                                                {item.filename}
                                            </p>
                                        </div>
                                    </button>
                                );
                            })
                        ) : (
                            <div className="flex items-center justify-center w-full h-[160px] text-slate-500 text-sm">
                                {viewMode === "results" ? "No generated videos available." : viewMode === "references" ? "No reference videos available." : "No source clips available."}
                            </div>
                        )}
                    </div>
                    <button 
                        onClick={() => scrollByAmount(260)}
                        className="shrink-0 text-2xl text-indigo-400 hover:text-indigo-300 transition-colors p-2"
                    >
                        <ChevronRight className="h-6 w-6" />
                    </button>
                </div>
                )}


                {/* Preview Box */}
                {sideBySideMode ? (
                    <div className="flex justify-center mb-8 w-full gap-4">
                        {/* Left Video */}
                        <div className="relative w-full max-w-[800px] min-h-[600px] max-h-[80vh] bg-gradient-to-br from-indigo-900/20 via-purple-900/20 to-black rounded-2xl overflow-hidden border border-indigo-500/30 shadow-2xl">
                            <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-r from-indigo-600/90 via-purple-600/90 to-black/90 backdrop-blur-sm flex items-center justify-between px-5 z-10">
                                <div className="relative" ref={leftDropdownRef}>
                                    <button
                                        onClick={() => setShowLeftDropdown(!showLeftDropdown)}
                                        className="flex items-center gap-2 px-3 py-1 bg-black/40 border border-white/10 rounded-lg text-[10px] font-bold uppercase tracking-widest text-white hover:bg-black/60 transition-all"
                                    >
                                        <span>Generated Videos</span>
                                        <ChevronDown className={cn("h-3 w-3 transition-transform", showLeftDropdown && "rotate-180")} />
                                    </button>
                                    {showLeftDropdown && (
                                        <div className="absolute top-full left-0 mt-2 w-96 max-w-[90vw] bg-black/90 border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden max-h-[400px] overflow-y-auto">
                                            {results.length > 0 ? (
                                                results.map((item) => (
                                                    <button
                                                        key={item.filename}
                                                        onClick={() => {
                                                            setSelectedItem(item);
                                                            setShowLeftDropdown(false);
                                                        }}
                                                        className={cn(
                                                            "w-full text-left px-4 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-b border-white/5 last:border-b-0 break-words",
                                                            selectedItem?.filename === item.filename
                                                                ? "bg-indigo-500/20 text-white"
                                                                : "text-slate-400 hover:bg-white/5 hover:text-white"
                                                        )}
                                                    >
                                                        {item.filename}
                                                    </button>
                                                ))
                                            ) : (
                                                <div className="px-4 py-3 text-[10px] text-slate-500">No generated videos available</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                                {selectedItem && (
                                    <>
                                        <h3 className="text-sm font-bold text-white truncate max-w-[40%]">
                                            {selectedItem.filename}
                                        </h3>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => {
                                                    const url = getItemUrl(selectedItem);
                                                    downloadFile(url, selectedItem.filename);
                                                }}
                                                className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                                                title="Download"
                                            >
                                                <Download className="h-4 w-4 text-white" />
                                            </button>
                                            {getItemType(selectedItem) === "result" && (
                                                <button
                                                    onClick={() => deleteResult(selectedItem.filename)}
                                                    className="p-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors"
                                                    title="Delete"
                                                >
                                                    <Trash2 className="h-4 w-4 text-red-400" />
                                                </button>
                                            )}
                                        </div>
                                    </>
                                )}
                            </div>
                            <div className="w-full h-full flex items-center justify-center pt-12">
                                {selectedItem ? (
                                    <video 
                                        key={getItemUrl(selectedItem)}
                                        src={`http://localhost:8000${getItemUrl(selectedItem)}`}
                                        className="w-full h-full object-contain"
                                        controls
                                    />
                                ) : (
                                    <div className="text-slate-600 text-lg font-semibold">
                                        Select a generated video
                                    </div>
                                )}
                            </div>
                        </div>
                        
                        {/* Right Video */}
                        <div className="relative w-full max-w-[800px] min-h-[600px] max-h-[80vh] bg-gradient-to-br from-cyan-900/20 via-blue-900/20 to-black rounded-2xl overflow-hidden border border-cyan-500/30 shadow-2xl">
                            <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-r from-cyan-600/90 via-blue-600/90 to-black/90 backdrop-blur-sm flex items-center justify-between px-5 z-10">
                                <div className="relative" ref={rightDropdownRef}>
                                    <button
                                        onClick={() => setShowRightDropdown(!showRightDropdown)}
                                        className="flex items-center gap-2 px-3 py-1 bg-black/40 border border-white/10 rounded-lg text-[10px] font-bold uppercase tracking-widest text-white hover:bg-black/60 transition-all"
                                    >
                                        <span>Reference Videos</span>
                                        <ChevronDown className={cn("h-3 w-3 transition-transform", showRightDropdown && "rotate-180")} />
                                    </button>
                                    {showRightDropdown && (
                                        <div className="absolute top-full left-0 mt-2 w-96 max-w-[90vw] bg-black/90 border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden max-h-[400px] overflow-y-auto">
                                            {references.length > 0 ? (
                                                references.map((item) => (
                                                    <button
                                                        key={item.filename}
                                                        onClick={() => {
                                                            setSelectedItem2(item);
                                                            setShowRightDropdown(false);
                                                        }}
                                                        className={cn(
                                                            "w-full text-left px-4 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-b border-white/5 last:border-b-0 break-words",
                                                            selectedItem2?.filename === item.filename
                                                                ? "bg-cyan-500/20 text-white"
                                                                : "text-slate-400 hover:bg-white/5 hover:text-white"
                                                        )}
                                                    >
                                                        {item.filename}
                                                    </button>
                                                ))
                                            ) : (
                                                <div className="px-4 py-3 text-[10px] text-slate-500">No reference videos available</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                                {selectedItem2 && (
                                    <>
                                        <h3 className="text-sm font-bold text-white truncate max-w-[40%]">
                                            {selectedItem2.filename}
                                        </h3>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => {
                                                    const url = getItemUrl(selectedItem2);
                                                    downloadFile(url, selectedItem2.filename);
                                                }}
                                                className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                                                title="Download"
                                            >
                                                <Download className="h-4 w-4 text-white" />
                                            </button>
                                            {getItemType(selectedItem2) === "result" && (
                                                <button
                                                    onClick={() => deleteResult(selectedItem2.filename)}
                                                    className="p-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors"
                                                    title="Delete"
                                                >
                                                    <Trash2 className="h-4 w-4 text-red-400" />
                                                </button>
                                            )}
                                            <button
                                                onClick={() => setSelectedItem2(null)}
                                                className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                                                title="Clear"
                                            >
                                                <X className="h-4 w-4 text-white" />
                                            </button>
                                        </div>
                                    </>
                                )}
                            </div>
                            <div className="w-full h-full flex items-center justify-center pt-12">
                                {selectedItem2 ? (
                                    <video 
                                        key={getItemUrl(selectedItem2)}
                                        src={`http://localhost:8000${getItemUrl(selectedItem2)}`}
                                        className="w-full h-full object-contain"
                                        controls
                                    />
                                ) : (
                                    <div className="text-slate-600 text-lg font-semibold">
                                        Select a reference video
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex justify-center mb-8 w-full">
                        <div className="relative w-full max-w-[800px] min-h-[600px] max-h-[80vh] bg-gradient-to-br from-indigo-900/20 via-purple-900/20 to-black rounded-2xl overflow-hidden border border-white/5 shadow-2xl">
                            {/* Overlay Title & Actions */}
                            {selectedItem && (
                                <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-r from-indigo-600/90 via-purple-600/90 to-black/90 backdrop-blur-sm flex items-center justify-between px-5 z-10">
                                    <h3 className="text-sm font-bold text-white truncate max-w-[60%]">
                                        {selectedItem.filename}
                                    </h3>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => {
                                                const url = getItemUrl(selectedItem);
                                                downloadFile(url, selectedItem.filename);
                                            }}
                                            className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                                            title="Download"
                                        >
                                            <Download className="h-4 w-4 text-white" />
                                        </button>
                                        {getItemType(selectedItem) === "result" && (
                                            <button
                                                onClick={() => deleteResult(selectedItem.filename)}
                                                className="p-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors"
                                                title="Delete"
                                            >
                                                <Trash2 className="h-4 w-4 text-red-400" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            )}
                            
                            {/* Video Preview */}
                            <div className="w-full h-full flex items-center justify-center pt-12">
                                {selectedItem ? (
                                    <video 
                                        key={getItemUrl(selectedItem)}
                                        src={`http://localhost:8000${getItemUrl(selectedItem)}`}
                                        className="w-full h-full object-contain"
                                        controls
                                    />
                                ) : (
                                    <div className="text-slate-600 text-lg font-semibold">
                                        Select a video to preview
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Metadata Card */}
                {selectedItem && (
                    <div className="max-w-[900px] mx-auto w-full mb-8">
                        <div className="bg-gradient-to-br from-slate-800/40 to-slate-900/40 border border-white/5 rounded-xl p-6 space-y-6">
                            <div>
                                <h3 className="text-lg font-bold text-white mb-4 pb-2 border-b border-white/10">File Information</h3>
                                <ul className="space-y-3">
                                    <li className="flex items-center gap-3 text-sm">
                                        <Video className="h-4 w-4 text-indigo-400" />
                                        <span className="text-slate-400 font-medium">Type:</span>
                                        <strong className="text-white ml-auto">
                                            {getItemType(selectedItem) === "result" ? "Generated Video" : getItemType(selectedItem) === "clip" ? "Source Clip" : "Reference Video"}
                                        </strong>
                                    </li>
                                    <li className="flex items-center gap-3 text-sm">
                                        <HardDrive className="h-4 w-4 text-indigo-400" />
                                        <span className="text-slate-400 font-medium">Size:</span>
                                        <strong className="text-white ml-auto">{formatSize(selectedItem.size)}</strong>
                                    </li>
                                    <li className="flex items-center gap-3 text-sm">
                                        <Calendar className="h-4 w-4 text-indigo-400" />
                                        <span className="text-slate-400 font-medium">Date:</span>
                                        <strong className="text-white ml-auto">{formatDate(selectedItem.created_at)}</strong>
                                    </li>
                                </ul>
                            </div>
                            <div className="pt-4 border-t border-white/10 flex gap-3">
                                <button
                                    onClick={() => {
                                        const url = getItemUrl(selectedItem);
                                        downloadFile(url, selectedItem.filename);
                                    }}
                                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-bold uppercase tracking-widest text-white transition-all"
                                >
                                    <Download className="h-4 w-4" />
                                    Download
                                </button>
                                {getItemType(selectedItem) === "result" && (
                                    <button
                                        onClick={() => deleteResult(selectedItem.filename)}
                                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 rounded-lg text-sm font-bold uppercase tracking-widest text-red-400 hover:text-white transition-all"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                        Delete
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                )}
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
