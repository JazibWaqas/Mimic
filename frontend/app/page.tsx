"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Upload, Video, ArrowRight, MonitorPlay, X, Plus, Sparkles, BrainCircuit, Terminal, Activity, CheckCircle2, ShieldCheck, Zap, Info, AlertTriangle, Layers, Target, Cpu, Wand2, Film } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { useDropzone } from "react-dropzone";

export default function StudioPage() {
  const router = useRouter();
  const [refFile, setRefFile] = useState<File | null>(null);
  const [materialFiles, setMaterialFiles] = useState<File[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState("");
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [logMessages, setLogMessages] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logMessages]);

  const onDropRef = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles?.[0]) {
      setRefFile(acceptedFiles[0]);
      toast.success("Reference Locked");
    }
  }, []);

  const onDropMaterial = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles?.length > 0) {
      setMaterialFiles(prev => [...prev, ...acceptedFiles]);
      toast.success(`${acceptedFiles.length} Clips Added`);
    }
  }, []);

  const { getRootProps: getRefProps, getInputProps: getRefInputProps, isDragActive: isRefDragActive } = useDropzone({
    onDrop: onDropRef, accept: { 'video/*': [] }, multiple: false
  });

  const { getRootProps: getMaterialProps, getInputProps: getMaterialInputProps, isDragActive: isMaterialDragActive } = useDropzone({
    onDrop: onDropMaterial, accept: { 'video/*': [] }, multiple: true
  });

  const checkStatus = async (sessionId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/status/${sessionId}`);
      if (!res.ok) return;
      const status = await res.json();
      setProgress(status.progress * 100);
      if (status.current_step && status.current_step !== statusMsg) setStatusMsg(status.current_step);
      if (status.logs) setLogMessages(status.logs);
      if (status.blueprint?.recommendations) setRecommendations(status.blueprint.recommendations);
      if (status.status === "complete") {
        setIsGenerating(false); setProgress(100);
        const filename = status.output_path?.split(/[\\/]/).pop() || `mimic_output_${sessionId}.mp4`;
        router.push(`/vault?filename=${filename}&type=results`);
      } else if (status.status === "error") {
        setIsGenerating(false); toast.error(status.error || "Generation Error");
      }
    } catch (err) { }
  };

  const startMimic = async () => {
    if (!refFile || materialFiles.length === 0) return toast.error("Provide all assets.");
    setIsGenerating(true); setStatusMsg("Initializing..."); setProgress(5);
    try {
      const { session_id } = await api.uploadFiles(refFile, materialFiles);
      setCurrentSessionId(session_id); await api.startGeneration(session_id);
      const ws = api.connectProgress(session_id);
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        setProgress(data.progress * 100); setStatusMsg(data.message || "");
        if (data.logs) setLogMessages(data.logs);
        if (data.status === "complete") { setIsGenerating(false); checkStatus(session_id); }
      };
      ws.onerror = () => checkStatus(session_id);
    } catch (err) { setIsGenerating(false); toast.error("Process failed."); }
  };

  return (
    <div className="min-h-screen bg-[#020306] overflow-x-hidden pt-4 pb-24">
      <div className="max-w-[1700px] mx-auto px-6 md:px-12 relative transition-all duration-700">

        {/* Hero Section - Professional Scale (Reduced 20%) */}
        <div className="shrink-0 flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-white/10">
          <div className="space-y-2 max-w-2xl">
            <div className="space-y-0.5 group">
              <div className="flex items-center gap-3">
                <div className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                  <Wand2 className="h-4 w-4" />
                </div>
                <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">Studio</h1>
              </div>
              <p className="text-[9px] font-black text-indigo-400 uppercase tracking-[0.3em] ml-10">Integrated Gemini 3 Engine</p>
            </div>
            <div className="space-y-1.5 ml-10 border-l-2 border-white/5 pl-6 py-1">
              <h2 className="text-lg font-bold text-white/90">Edit Videos by Reference Using Gemini 3</h2>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                Upload a reference video and your raw clips. This system analyzes the reference's cut structure, pacing, energy, and rhythm, then automatically edits your footage to match the style using Gemini 3.
              </p>
            </div>
          </div>
          <div className="hidden md:flex flex-col items-end gap-2 pr-2 group/logic">
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Logic Core:</span>
              <span className={cn(
                "text-[9px] font-black uppercase tracking-widest transition-all duration-500",
                refFile && materialFiles.length > 0 ? "text-[#ff007f] shadow-[0_0_10px_#ff007f]" : "text-cyan-500 animate-pulse"
              )}>
                {refFile && materialFiles.length > 0 ? "System Ready" : "Syncing"}
              </span>
            </div>
            <div className="h-1.5 w-40 bg-white/5 rounded-full overflow-hidden border border-white/5 relative">
              <div
                className="h-full transition-all duration-1000 ease-out relative z-10"
                style={{
                  width: refFile && materialFiles.length > 0 ? '100%' : refFile || materialFiles.length > 0 ? '50%' : '10%',
                  background: `linear-gradient(to right, #bf00ff, #00d4ff)`
                }}
              />
              {refFile && materialFiles.length > 0 && (
                <div className="absolute inset-0 bg-[#ff007f]/20 animate-pulse z-20" />
              )}
            </div>
          </div>
        </div>

        {/* Glass Content Interface - Added significant margin top */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-12 mt-12">
          <div className="space-y-12">

            {/* Reference Module - Glass Slate */}
            <div className="space-y-5">
              <div className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 rounded-full bg-indigo-500 shadow-[0_0_12px_rgba(99,102,241,1)]" />
                <h3 className="text-[11px] font-black text-white uppercase tracking-[0.3em]">01. Style Binding</h3>
              </div>
              <div
                {...getRefProps()}
                className={cn(
                  "h-[200px] rounded-xl border transition-all duration-700 flex flex-col items-center justify-center cursor-pointer relative group overflow-hidden",
                  isRefDragActive ? "border-cyan-400 bg-cyan-500/10 glow-cyan" :
                    refFile ? "border-cyan-500/40 bg-white/[0.05] shadow-[0_0_20px_rgba(0,212,255,0.15)]" :
                      "border-white/10 bg-white/[0.03] hover:bg-white/[0.08] hover:border-cyan-500/30"
                )}
              >
                <input {...getRefInputProps()} />
                {refFile ? (
                  <>
                    <video src={URL.createObjectURL(refFile)} className="absolute inset-0 w-full h-full object-cover opacity-90" />
                    <button onClick={(e) => { e.stopPropagation(); setRefFile(null); }} className="absolute h-10 w-10 rounded-xl bg-red-600/20 backdrop-blur-md text-white border border-red-500/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:bg-red-600 shadow-2xl z-20"><X className="h-5 w-5" /></button>
                    <div className="absolute top-4 right-4 z-10">
                      <div className="px-2 py-0.5 rounded bg-cyan-500 text-[8px] font-black text-white uppercase tracking-widest glow-cyan">Target Locked</div>
                    </div>
                  </>
                ) : (
                  <div className="text-center space-y-4">
                    <div className="h-12 w-12 rounded-xl bg-white/5 border border-white/10 text-indigo-400/50 flex items-center justify-center mx-auto group-hover:bg-cyan-500 group-hover:text-white group-hover:border-cyan-400 transition-all">
                      <Plus className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-[10px] font-black text-white uppercase tracking-widest mb-1 group-hover:text-cyan-400 transition-colors">Bind Style Reference</p>
                      <p className="text-[8px] font-bold text-slate-600 uppercase tracking-widest">MP4 / MOV / AVI</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Clips Module - Glass Slate */}
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 rounded-full bg-indigo-500 shadow-[0_0_12px_rgba(99,102,241,1)]" />
                <h3 className="text-[11px] font-black text-white uppercase tracking-[0.3em]">02. Source Injection</h3>
              </div>
              <div
                {...getMaterialProps()}
                className={cn(
                  "min-h-[200px] rounded-xl border transition-all duration-700 flex flex-col items-center justify-center cursor-pointer relative group overflow-hidden",
                  isMaterialDragActive ? "border-cyan-400 bg-cyan-500/10 glow-cyan" :
                    materialFiles.length > 0 ? "border-cyan-500/40 bg-white/[0.05] shadow-[0_0_20px_rgba(0,212,255,0.15)]" :
                      "border-white/10 bg-white/[0.03] hover:bg-white/[0.08] hover:border-cyan-500/30"
                )}
              >
                <input {...getMaterialInputProps()} />
                {materialFiles.length === 0 ? (
                  <div className="text-center space-y-4">
                    <div className="h-12 w-12 rounded-xl bg-white/5 border border-white/10 text-indigo-400/50 flex items-center justify-center mx-auto group-hover:bg-cyan-500 group-hover:text-white group-hover:border-cyan-400 transition-all">
                      <MonitorPlay className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-[10px] font-black text-white uppercase tracking-widest mb-1 group-hover:text-cyan-400 transition-colors">Inject Raw Samples</p>
                      <p className="text-[8px] font-bold text-slate-600 uppercase tracking-widest">Multiple video assets</p>
                    </div>
                  </div>
                ) : (
                  <div className="w-full p-6">
                    <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
                      {materialFiles.map((file, i) => (
                        <div key={i} className="aspect-square rounded-xl bg-black border border-white/10 overflow-hidden relative group/item shadow-2xl">
                          <video src={URL.createObjectURL(file)} className="w-full h-full object-cover opacity-90" />
                          <button onClick={(e) => { e.stopPropagation(); setMaterialFiles(prev => prev.filter((_, idx) => idx !== i)); }} className="absolute inset-0 bg-red-600 text-white opacity-0 group-hover/item:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm shadow-xl"><X className="h-4 w-4" /></button>
                        </div>
                      ))}
                      <div className="aspect-square rounded-xl border border-dashed border-white/10 flex items-center justify-center text-slate-700 hover:border-indigo-500/40 transition-all bg-white/[0.02] active:scale-95"><Plus className="h-4 w-4" /></div>
                    </div>
                    <div className="mt-4 flex items-center gap-2">
                      <div className="px-2 py-0.5 rounded bg-indigo-500/20 text-[8px] font-black text-indigo-400 uppercase border border-indigo-500/20">{materialFiles.length} Streams Injected</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Logic Sidebar - Command Center Layout */}
          <div className="space-y-6">
            <div className="glass-premium rounded-xl flex flex-col h-[520px] shadow-2xl border border-white/5 relative overflow-hidden group/telemetry">
              {/* Background Glow */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-[60px] -mr-16 -mt-16 group-hover/telemetry:bg-cyan-500/20 transition-all duration-1000" />

              <div className="px-5 py-4 border-b border-indigo-500/10 flex items-center justify-between relative z-10">
                <div className="flex items-center gap-3 text-[10px] font-black text-white uppercase tracking-[0.2em]">
                  <Terminal className="h-3.5 w-3.5 text-cyan-400" />
                  <span>System Telemetry</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="h-1.5 w-1.5 rounded-full bg-cyan-400 glow-cyan animate-pulse" />
                  <span className="text-[8px] font-black text-cyan-400/60 uppercase tracking-widest">Syncing</span>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto custom-scrollbar px-5 py-6 space-y-3 font-mono text-[14px] relative z-10 leading-relaxed bg-black/20">
                {logMessages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center opacity-20">
                    <Activity className="h-8 w-8 mb-4 text-indigo-400 animate-pulse" />
                    <p className="font-black uppercase tracking-[0.4em] italic text-[10px]">Awaiting Protocol</p>
                  </div>
                ) : (
                  logMessages.map((msg, i) => (
                    <div key={i} className="flex gap-4 text-slate-400 hover:text-white transition-colors animate-in fade-in slide-in-from-left-2 duration-300">
                      <span className="text-indigo-500/40 shrink-0 select-none font-bold text-[10px] mt-1">{(i + 1).toString().padStart(2, '0')}</span>
                      <span className={cn("inline-block", msg.includes('ERROR') ? 'text-red-500' : msg.includes('GEMINI') ? 'text-cyan-400 font-bold' : '')}>{msg}</span>
                    </div>
                  ))
                )}
                <div ref={logEndRef} />
              </div>

              {/* TACTICAL EXECUTE BUTTON - Permanent Adrenaline State */}
              <div className="p-5 bg-white/[0.02] border-t border-white/5 relative z-10">
                <button
                  onClick={startMimic}
                  disabled={isGenerating || !refFile || materialFiles.length === 0}
                  className={cn(
                    "w-full h-14 rounded-xl font-black text-[11px] uppercase tracking-[0.25em] transition-all duration-700 flex flex-col items-center justify-center relative overflow-hidden group/execute border",
                    isGenerating
                      ? "bg-gradient-to-r from-[#ff007f] to-[#bf00ff] border-[#ff007f]/40 text-white animate-pulse"
                      : !refFile || materialFiles.length === 0
                        ? "bg-gradient-to-br from-indigo-500/10 to-cyan-500/10 border-cyan-500/20 text-slate-400 shadow-[0_0_20px_rgba(0,212,255,0.1)] hover:border-cyan-500/40"
                        : "bg-gradient-to-r from-[#00d4ff] via-[#4f46e5] to-[#bf00ff] bg-[length:200%_auto] border-white/30 text-white shadow-[0_0_30px_rgba(0,212,255,0.4)] hover:shadow-[0_0_60px_rgba(0,212,255,0.7)] hover:bg-right hover:scale-[1.02] active:scale-[0.98] animate-pulse-slow"
                  )}
                >
                  {/* Hover Label Layer */}
                  <div className="absolute inset-0 flex items-center justify-center transition-all duration-500 group-hover/execute:-translate-y-full">
                    <div className="flex items-center gap-3">
                      <Sparkles className={cn(
                        "h-4 w-4",
                        isGenerating ? "text-white animate-spin-slow" :
                          refFile && materialFiles.length > 0 ? "text-white animate-spin-slow" : "text-cyan-400"
                      )} />
                      <span>{isGenerating ? "Synthesizing..." : "Execute Synthesis"}</span>
                    </div>
                  </div>

                  <div className="absolute inset-0 flex flex-col items-center justify-center translate-y-full transition-all duration-500 group-hover/execute:translate-y-0 bg-white/10 backdrop-blur-sm">
                    <span className="text-white">Initialize Gemini 3</span>
                    <span className="text-[8px] opacity-70 tracking-[0.4em] mt-1">Engine Port: 8000 // Primed</span>
                  </div>

                  {/* Charged Visual Effect */}
                  {refFile && materialFiles.length > 0 && !isGenerating && (
                    <div className="absolute inset-0 pointer-events-none">
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
                    </div>
                  )}
                </button>
              </div>
            </div>

            <div className={cn(
              "glass-premium rounded-xl px-5 py-6 transition-all duration-1000 border relative overflow-hidden",
              recommendations.length > 0 ? "border-indigo-500/40 bg-indigo-500/[0.03] shadow-[0_0_30px_rgba(99,102,241,0.1)]" : "border-white/5 opacity-60"
            )}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.2em]">
                  <Sparkles className={cn("h-3.5 w-3.5", recommendations.length > 0 ? "text-[#ccff00]" : "text-pink-400")} />
                  <span className={cn(recommendations.length > 0 ? "text-[#ccff00]" : "text-white")}>Agent Feedback</span>
                </div>
                {recommendations.length > 0 && (
                  <div className="px-2 py-0.5 rounded bg-[#ccff00]/10 border border-[#ccff00]/20 text-[8px] font-black text-[#ccff00] uppercase animate-pulse">New Intel</div>
                )}
              </div>
              <div className="space-y-4">
                {recommendations.length === 0 ? (
                  <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest italic leading-relaxed border-l border-white/10 pl-4 py-1">System in idle state. Analysis requires source material injection.</p>
                ) : (
                  recommendations.map((rec, i) => (
                    <div key={i} className="flex gap-4 items-start group/rec p-2 rounded-lg hover:bg-white/[0.02] border-l-2 border-[#ff007f] shadow-[inset_4px_0_10px_-4px_rgba(255,0,127,0.2)] transition-all">
                      <div className="h-1.5 w-1.5 rounded-full bg-[#ff007f] mt-1.5 shrink-0 shadow-[0_0_8px_rgba(255,0,127,0.8)] group-hover/rec:scale-125 transition-transform" />
                      <p className="text-[11px] font-bold text-slate-300 leading-relaxed uppercase tracking-tight group-hover/rec:text-white transition-colors">{rec}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* System Protocol Description & Pipeline Preview */}
        <div className="rounded-[2.5rem] bg-white/[0.02] border border-white/5 p-10 mt-12 space-y-12 shadow-inner group/blueprint relative overflow-hidden">
          <div className="absolute top-0 left-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-[120px] -ml-32 -mt-32" />

          <div className="space-y-8 relative z-10">
            <div className="flex items-center justify-between">
              <h3 className="text-[11px] font-black text-indigo-400 uppercase tracking-[0.5em]">Operational Blueprint</h3>
              <div className="flex gap-2">
                <div className="h-1 w-6 bg-indigo-500/20 rounded-full" />
                <div className="h-1 w-1 bg-indigo-500/40 rounded-full" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
              <div className="space-y-3 group/bp card-glint p-4 -m-4 hover:border-cyan-500/30 transition-all duration-500">
                <h4 className="text-[11px] font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <div className="h-4 w-4 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover/bp:bg-cyan-500 group-hover/bp:text-white transition-all duration-500 shadow-[0_0_10px_rgba(34,211,238,0.2)] group-hover/bp:shadow-[0_0_20px_rgba(34,211,238,0.4)]"><Layers className="h-2.5 w-2.5" /></div>
                  Multi-Stage Orchestration
                </h4>
                <p className="text-[11px] text-slate-500 leading-relaxed font-bold uppercase tracking-tight group-hover/bp:text-slate-400 transition-colors">
                  Combining computer vision, audio beat analysis, and Gemini 3 multimodal reasoning to map temporal structures across footage.
                </p>
              </div>
              <div className="space-y-3 group/bp card-glint p-4 -m-4 hover:border-purple-500/30 transition-all duration-500">
                <h4 className="text-[11px] font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <div className="h-4 w-4 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover/bp:bg-purple-500 group-hover/bp:text-white transition-all duration-500 shadow-[0_0_10px_rgba(191,0,255,0.2)] group-hover/bp:shadow-[0_0_20px_rgba(191,0,255,0.4)]"><Zap className="h-2.5 w-2.5" /></div>
                  Editing by Example
                </h4>
                <p className="text-[11px] text-slate-500 leading-relaxed font-bold uppercase tracking-tight group-hover/bp:text-slate-400 transition-colors">
                  Deterministic decisions on clip selection, anti-repetition, and timeline continuity, turning creative intuition into an engineering protocol.
                </p>
              </div>
              <div className="space-y-3 group/bp card-glint p-4 -m-4 hover:border-lime-500/30 transition-all duration-500">
                <h4 className="text-[11px] font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <div className="h-4 w-4 rounded-lg bg-lime-500/10 border border-lime-500/20 flex items-center justify-center text-lime-400 group-hover/bp:bg-lime-500 group-hover/bp:text-white transition-all duration-500 shadow-[0_0_10px_rgba(204,255,0,0.2)] group-hover/bp:shadow-[0_0_20px_rgba(204,255,0,0.4)]"><BrainCircuit className="h-2.5 w-2.5" /></div>
                  Temporal Intelligence
                </h4>
                <p className="text-[11px] text-slate-500 leading-relaxed font-bold uppercase tracking-tight group-hover/bp:text-slate-400 transition-colors">
                  Using Gemini 3 to reason over entire video sequences to understand energy shifts and motion patterns for humanly intuitive edits.
                </p>
              </div>
            </div>
          </div>

          {/* Pipeline Preview - Conditional Visibility (Active Processing Only) */}
          {isGenerating && (
            <div className="pt-8 border-t border-white/5 space-y-6 relative z-10 animate-in fade-in slide-in-from-bottom-2 duration-1000">
              <div className="flex items-center gap-3">
                <Activity className="h-3.5 w-3.5 text-cyan-400" />
                <p className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Signal Pipeline Architecture</p>
              </div>
              <div className="flex items-center gap-2">
                {[
                  { label: 'Ingestion', color: 'bg-indigo-500', active: true },
                  { label: 'Temporal Map', color: 'bg-cyan-500', active: !!refFile },
                  { label: 'Beat Alignment', color: 'bg-purple-500', active: false },
                  { label: 'Logic Reasoning', color: 'bg-[#bf00ff]', active: false, cached: true },
                  { label: 'Final Output', color: 'bg-lime-500', active: false }
                ].map((step, i) => (
                  <div key={i} className="flex-1 flex items-center gap-2">
                    <div className={cn(
                      "flex-1 h-1.5 rounded-full transition-all duration-1000 relative overflow-hidden",
                      step.active ? step.color : "bg-white/5"
                    )}>
                      {step.active && <div className="absolute inset-0 bg-white/40 animate-shimmer" />}
                    </div>
                    {i < 4 && <div className="h-1 w-1 rounded-full bg-white/10" />}
                    <div className="hidden lg:block">
                      <p className={cn(
                        "text-[8px] font-black uppercase tracking-widest transition-colors",
                        step.active ? "text-white" : "text-slate-700"
                      )}>
                        {step.label}
                        {step.cached && <span className="ml-2 text-indigo-400">[CACHED]</span>}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Tier 1 Feature: Pipeline Visualization Modal */}
        {isGenerating && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-xl z-[200] flex items-center justify-center p-6 animate-in fade-in zoom-in duration-500">
            <div className="w-full max-w-[700px] glass-premium rounded-2xl p-10 border border-white/5 shadow-[0_0_100px_rgba(0,212,255,0.1)] relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent pulse-cyan" />

              <div className="flex flex-col space-y-8">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 glow-cyan">
                      <Cpu className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white tracking-tight uppercase">System Pipeline Sync</h3>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Protocol v7.0.4-SYNTH | PID: {currentSessionId?.slice(0, 8)}</p>
                    </div>
                  </div>
                  <div className="px-3 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-[9px] font-black text-indigo-400 uppercase tracking-[0.2em]">
                    Gemini Orchestration
                  </div>
                </div>

                {/* Pipeline Stages */}
                <div className="space-y-2">
                  <div className="flex items-center gap-4 p-3 rounded-lg bg-white/[0.03] border border-white/5 group transition-all">
                    <div className="h-2 w-2 rounded-full bg-lime-400 glow-lime" />
                    <span className="flex-1 text-xs font-bold text-white uppercase tracking-wider">Asset Validation</span>
                    <span className="text-[10px] font-mono text-slate-500">0.4s</span>
                  </div>

                  <div className={cn(
                    "flex items-center gap-4 p-3 rounded-lg border transition-all",
                    progress > 10 ? "bg-white/[0.03] border-white/5" : "bg-cyan-500/5 border-cyan-500/20 glow-cyan animate-pulse"
                  )}>
                    <div className={cn("h-2 w-2 rounded-full", progress > 20 ? "bg-lime-400 glow-lime" : "bg-cyan-400 glow-cyan animate-pulse")} />
                    <span className="flex-1 text-xs font-bold text-white uppercase tracking-wider">Multimodal Analysis</span>
                    <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-[8px] font-black text-cyan-400 uppercase">Gemini</span>
                  </div>

                  <div className={cn(
                    "flex items-center gap-4 p-3 rounded-lg border transition-all",
                    progress > 40 ? "bg-white/[0.03] border-white/5" : progress > 20 ? "bg-purple-500/5 border-purple-500/20 animate-pulse" : "opacity-30 border-white/5"
                  )}>
                    <div className={cn("h-2 w-2 rounded-full", progress > 50 ? "bg-lime-400 glow-lime" : progress > 20 ? "bg-purple-400 glow-purple animate-pulse" : "bg-slate-700")} />
                    <span className="flex-1 text-xs font-bold text-white uppercase tracking-wider">Temporal Synthesis</span>
                    <span className="text-[10px] font-mono text-slate-500">CORE-EDITOR</span>
                  </div>

                  <div className={cn(
                    "flex items-center gap-4 p-3 rounded-lg border transition-all",
                    progress > 70 ? "bg-white/[0.03] border-white/5" : progress > 50 ? "bg-pink-500/5 border-pink-500/20 animate-pulse" : "opacity-30 border-white/5"
                  )}>
                    <div className={cn("h-2 w-2 rounded-full", progress > 80 ? "bg-lime-400 glow-lime" : progress > 50 ? "bg-pink-400 glow-pink animate-pulse" : "bg-slate-700")} />
                    <span className="flex-1 text-xs font-bold text-white uppercase tracking-wider">Editing Grammar Reasoning</span>
                    <span className="text-[10px] font-mono text-slate-500">GEMINI-3</span>
                  </div>

                  <div className={cn(
                    "flex items-center gap-4 p-3 rounded-lg border transition-all",
                    progress > 95 ? "bg-white/[0.03] border-white/5" : progress > 80 ? "bg-white/5 border-white/10 animate-pulse" : "opacity-30 border-white/5"
                  )}>
                    <div className={cn("h-2 w-2 rounded-full", progress > 98 ? "bg-lime-400 glow-lime" : "bg-slate-700")} />
                    <span className="flex-1 text-xs font-bold text-white uppercase tracking-wider">Sequence Locking</span>
                    <span className="text-[10px] font-mono text-slate-500">FINALIZING</span>
                  </div>
                </div>

                {/* Main Progress Tracker */}
                <div className="space-y-3 pt-4">
                  <div className="flex justify-between items-end">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Global Protocol Sync</span>
                    <span className="text-4xl font-black text-white font-mono">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden p-[1px] border border-white/5">
                    <div className="h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 transition-all duration-1000 rounded-full glow-cyan" style={{ width: `${progress}%` }} />
                  </div>
                </div>

                <div className="flex items-center justify-between gap-4 pt-4 border-t border-white/5 italic">
                  <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Autonomous system coordination in progress...</p>
                  <p className="text-[9px] font-bold text-cyan-400 uppercase tracking-widest leading-relaxed">{statusMsg}</p>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
