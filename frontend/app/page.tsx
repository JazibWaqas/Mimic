"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Upload, Video, ArrowRight, MonitorPlay, X, Plus, Sparkles, BrainCircuit, Terminal, Activity, CheckCircle2, ShieldCheck, Zap, Info, AlertTriangle, Layers, Target, Cpu, Wand2, Film } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
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
    <div className="min-h-[calc(100vh-80px)] flex flex-col mx-auto max-w-[1300px]">
      <div className="flex-1 flex flex-col px-6 md:px-12 pb-12 pt-4 space-y-10">

        {/* Hero Section - Reverted to Indigo Accent */}
        <div className="shrink-0 flex flex-col md:flex-row md:items-end justify-between gap-8 pb-10 border-b border-white/10">
          <div className="space-y-4 max-w-2xl">
            <div className="space-y-1">
              <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic leading-none">Studio</h1>
              <p className="text-[12px] font-black text-indigo-400 uppercase tracking-[0.4em]">Integrated Gemini 3 Engine</p>
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white/90 tracking-tight">Edit Videos by Reference Using Gemini 3</h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                Upload a reference video and your raw clips. This system analyzes the reference’s cut structure, pacing, energy, and rhythm, then automatically edits your footage to match the style using Gemini 3.
              </p>
            </div>
          </div>
          <button
            onClick={startMimic}
            disabled={isGenerating || !refFile || materialFiles.length === 0}
            className="h-16 px-12 rounded-2xl bg-indigo-600 text-white font-black text-[14px] uppercase tracking-[0.2em] shadow-[0_0_50px_rgba(79,70,229,0.4)] hover:shadow-[0_0_70px_rgba(79,70,229,0.6)] hover:scale-[1.05] active:scale-[0.95] transition-all disabled:opacity-20 flex items-center gap-4 border border-white/20"
          >
            <span className="drop-shadow-sm">Execute Synthesis</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>

        {/* Glass Content Interface */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-12">
          <div className="space-y-10">

            {/* Reference Module - Glass Slate */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-indigo-500 shadow-[0_0_12px_rgba(99,102,241,1)]" />
                <h3 className="text-[12px] font-black text-white uppercase tracking-[0.25em]">01. Style Binding</h3>
              </div>
              <div
                {...getRefProps()}
                className={`h-[280px] rounded-[2rem] border transition-all duration-300 flex flex-col items-center justify-center cursor-pointer relative group overflow-hidden ${isRefDragActive
                  ? 'border-indigo-400 bg-indigo-500/10'
                  : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.08] shadow-[0_20px_50px_rgba(0,0,0,0.5)]'
                  }`}
              >
                <input {...getRefInputProps()} />
                {refFile ? (
                  <>
                    <video src={URL.createObjectURL(refFile)} className="absolute inset-0 w-full h-full object-cover opacity-90" />
                    <button onClick={(e) => { e.stopPropagation(); setRefFile(null); }} className="absolute h-12 w-12 rounded-2xl bg-red-600 text-white border border-white/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-2xl"><X className="h-6 w-6" /></button>
                  </>
                ) : (
                  <div className="text-center space-y-6">
                    <div className="h-16 w-16 rounded-2xl bg-white/5 border border-white/10 text-indigo-400/50 flex items-center justify-center mx-auto group-hover:bg-indigo-500 group-hover:text-white transition-all shadow-xl">
                      <Plus className="h-8 w-8" />
                    </div>
                    <div>
                      <p className="text-[12px] font-black text-white uppercase tracking-widest mb-1">Bind Style Reference</p>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">MP4 / MOV / AVI</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Clips Module - Glass Slate */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-indigo-500 shadow-[0_0_12px_rgba(99,102,241,1)]" />
                <h3 className="text-[12px] font-black text-white uppercase tracking-[0.25em]">02. Source Injection</h3>
              </div>
              <div
                {...getMaterialProps()}
                className={`min-h-[280px] rounded-[2rem] border transition-all duration-300 flex flex-col items-center justify-center cursor-pointer relative group overflow-hidden ${isMaterialDragActive
                  ? 'border-indigo-400 bg-indigo-500/10'
                  : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.08] shadow-[0_20px_50px_rgba(0,0,0,0.5)]'
                  }`}
              >
                <input {...getMaterialInputProps()} />
                {materialFiles.length === 0 ? (
                  <div className="text-center space-y-6">
                    <div className="h-16 w-16 rounded-2xl bg-white/5 border border-white/10 text-indigo-400/50 flex items-center justify-center mx-auto group-hover:bg-indigo-500 group-hover:text-white transition-all shadow-xl">
                      <MonitorPlay className="h-8 w-8" />
                    </div>
                    <div>
                      <p className="text-[12px] font-black text-white uppercase tracking-widest mb-1">Inject Raw Samples</p>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Multiple video assets</p>
                    </div>
                  </div>
                ) : (
                  <div className="w-full p-8">
                    <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
                      {materialFiles.map((file, i) => (
                        <div key={i} className="aspect-square rounded-2xl bg-black border border-white/10 overflow-hidden relative group/item shadow-2xl">
                          <video src={URL.createObjectURL(file)} className="w-full h-full object-cover opacity-90" />
                          <button onClick={(e) => { e.stopPropagation(); setMaterialFiles(prev => prev.filter((_, idx) => idx !== i)); }} className="absolute inset-0 bg-red-600 text-white opacity-0 group-hover/item:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm shadow-xl"><X className="h-5 w-5" /></button>
                        </div>
                      ))}
                      <div className="aspect-square rounded-2xl border border-dashed border-white/10 flex items-center justify-center text-slate-700 hover:border-indigo-500/40 transition-all bg-white/[0.02]"><Plus className="h-5 w-5" /></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Logic Sidebar */}
          <div className="space-y-8">
            <div className="rounded-[2rem] bg-white/[0.03] border border-white/10 p-8 flex flex-col h-[440px] shadow-[0_30px_60px_rgba(0,0,0,0.8)]">
              <div className="flex items-center gap-3 mb-8 pb-4 border-b border-indigo-500/10 text-[12px] font-black text-white uppercase tracking-widest">
                <Terminal className="h-4 w-4 text-indigo-400" />
                <span>System Telemetry</span>
              </div>
              <div className="flex-1 overflow-y-auto custom-scrollbar pr-3 space-y-4 font-mono text-[11px]">
                {logMessages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center opacity-10">
                    <Activity className="h-10 w-10 mb-3 text-indigo-500" />
                    <p className="font-black uppercase tracking-[0.3em] italic">Awaiting Protocol</p>
                  </div>
                ) : (
                  logMessages.map((msg, i) => (
                    <div key={i} className="flex gap-4 text-slate-300">
                      <span className="text-indigo-500/30 shrink-0 select-none font-bold">{(i + 1).toString().padStart(2, '0')}</span>
                      <span className={msg.includes('ERROR') ? 'text-red-500' : ''}>{msg}</span>
                    </div>
                  ))
                )}
                <div ref={logEndRef} />
              </div>
            </div>

            <div className={`rounded-[2rem] p-8 transition-all duration-700 shadow-[0_30px_60px_rgba(0,0,0,0.6)] ${recommendations.length > 0 ? 'bg-indigo-600/10 border-indigo-500/20' : 'bg-white/[0.02] border-white/5 opacity-50'}`}>
              <div className="flex items-center gap-3 mb-6 text-[12px] font-black text-white uppercase tracking-widest">
                <Sparkles className="h-4 w-4 text-indigo-400" />
                <span>Agent Feedback</span>
              </div>
              <div className="space-y-4">
                {recommendations.length === 0 ? (
                  <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest italic leading-relaxed">System in idle state. Analysis requires source material injection.</p>
                ) : (
                  recommendations.map((rec, i) => (
                    <div key={i} className="flex gap-4 items-start">
                      <div className="h-1.5 w-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0 shadow-[0_0_8px_rgba(99,102,241,0.8)]" />
                      <p className="text-[11px] font-bold text-slate-300 leading-relaxed uppercase tracking-tight">{rec}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* System Protocol Description */}
        <div className="rounded-[2.5rem] bg-white/[0.02] border border-white/5 p-12 mt-12 space-y-8 shadow-inner">
          <h3 className="text-sm font-black text-indigo-400 uppercase tracking-[0.4em] mb-4">Operational Blueprint</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
            <div className="space-y-3">
              <h4 className="text-[12px] font-black text-white uppercase tracking-widest">Multi-Stage Orchestration</h4>
              <p className="text-[11px] text-slate-500 leading-relaxed font-medium">
                This is not a simple prompt. It is a complex system combining computer vision, audio beat analysis, and Gemini 3 multimodal reasoning to map temporal structures across footage.
              </p>
            </div>
            <div className="space-y-3">
              <h4 className="text-[12px] font-black text-white uppercase tracking-widest">Editing by Example</h4>
              <p className="text-[11px] text-slate-500 leading-relaxed font-medium">
                Our internal Editor engine makes deterministic decisions on clip selection, anti-repetition, and timeline continuity, turning creative intuition into an engineering protocol.
              </p>
            </div>
            <div className="space-y-3">
              <h4 className="text-[12px] font-black text-white uppercase tracking-widest">Temporal Intelligence</h4>
              <p className="text-[11px] text-slate-500 leading-relaxed font-medium">
                Gemini 3 allows us to reason over entire video sequences to understand energy shifts and motion patterns, enabling edits that feel humanly intuitive.
              </p>
            </div>
          </div>
        </div>

        {/* Main Loading UI */}
        {(isGenerating || progress > 0) && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[200] flex items-center justify-center p-6 animate-in fade-in duration-500">
            <div className="w-full max-w-[800px] rounded-[3rem] bg-[#020306] border border-indigo-500/30 p-12 shadow-[0_0_150px_rgba(99,102,241,0.15)] relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-indigo-500 to-transparent animate-pulse" />
              <div className="flex flex-col items-center text-center space-y-10">
                <div className="h-24 w-24 rounded-3xl bg-indigo-500 text-white flex items-center justify-center shadow-[0_0_50px_rgba(99,102,241,0.5)] animate-bounce-slow">
                  <Sparkles className="h-12 w-12" />
                </div>
                <div className="space-y-4">
                  <p className="text-[12px] font-black text-indigo-400 uppercase tracking-[0.5em]">Synthesis in Progress</p>
                  <h3 className="text-4xl font-black text-white uppercase italic tracking-tighter">{statusMsg || "Processing Logic..."}</h3>
                </div>

                <div className="w-full space-y-4">
                  <div className="flex justify-between items-end px-2">
                    <span className="text-[12px] font-black text-slate-500 uppercase tracking-widest">Protocol Completion</span>
                    <span className="text-5xl font-black text-white tabular-nums tracking-tighter">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-4 w-full bg-white/5 rounded-full overflow-hidden border border-white/5 p-1">
                    <div className="h-full bg-gradient-to-r from-indigo-600 to-blue-400 transition-all duration-1000 rounded-full shadow-[0_0_20px_rgba(99,102,241,0.8)]" style={{ width: `${progress}%` }} />
                  </div>
                </div>

                <p className="text-[10px] text-slate-500 max-w-md font-bold uppercase tracking-widest leading-relaxed">
                  Gemini 3 is currently analyzing temporal motion patterns and reconstructing the sequence timeline.
                </p>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
