"use client";

import { useState } from "react";
import { Upload, Video, ArrowRight, MonitorPlay, X, Plus, Sparkles, Download, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function StudioPage() {
  const router = useRouter();
  const [refFile, setRefFile] = useState<File | null>(null);
  const [materialFiles, setMaterialFiles] = useState<File[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState("");
  const [resultVideoUrl, setResultVideoUrl] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [resultFilename, setResultFilename] = useState<string | null>(null);
  const [logMessages, setLogMessages] = useState<string[]>([]);

  const handleRefUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setRefFile(e.target.files[0]);
      toast.success("Reference Acquired");
    }
  };

  const handleMaterialUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setMaterialFiles(prev => [...prev, ...newFiles]);
      toast.success(`${newFiles.length} Source Clip${newFiles.length !== 1 ? 's' : ''} Added`);
      // Reset input so same files can be selected again if needed
      e.target.value = '';
    }
  };

  const checkStatus = async (sessionId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/status/${sessionId}`);
      if (!res.ok) return;
      const status = await res.json();
      
      setProgress(status.progress * 100);
      const currentStep = status.current_step || status.message || "";
      if (currentStep && currentStep !== statusMsg) {
        setStatusMsg(currentStep);
      }
      
      // Update logs from orchestrator output
      if (status.logs && Array.isArray(status.logs)) {
        setLogMessages(status.logs);
      }
      
      if (status.status === "complete") {
        setIsGenerating(false);
        setProgress(100);
        setStatusMsg("Complete!");
        toast.success("Synthesis Complete!");
        // Auto-redirect to Projects page with the result selected
        if (status.output_path) {
          const filename = status.output_path.split('/').pop() || status.output_path.split('\\').pop();
          router.push(`/vault?filename=${filename}&type=results`);
        } else {
          const filename = `mimic_output_${sessionId}.mp4`;
          router.push(`/vault?filename=${filename}&type=results`);
        }
      } else if (status.status === "error") {
        setIsGenerating(false);
        toast.error(`Error: ${status.error || status.message}`);
      }
    } catch (err) {
      // Silently fail - WebSocket will handle updates
    }
  };

  const startMimic = async () => {
    if (!refFile || materialFiles.length === 0) {
      toast.error("Reference Video & Source Clips Required");
      return;
    }

    setIsGenerating(true);
    setStatusMsg("Initializing...");
    setProgress(10);
    setResultVideoUrl(null);
    setLogMessages(["Starting generation..."]);

    try {
      const { session_id } = await api.uploadFiles(refFile, materialFiles);
      setCurrentSessionId(session_id);
      await api.startGeneration(session_id);

      const ws = api.connectProgress(session_id);
      ws.onopen = () => {
        // Check status immediately when WebSocket opens
        checkStatus(session_id);
      };
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setProgress(data.progress * 100);
        const message = data.message || "";
        setStatusMsg(message);
        
        // Update logs from orchestrator output
        if (data.logs && Array.isArray(data.logs)) {
          setLogMessages(data.logs);
        } else if (message && message !== statusMsg) {
          addLogMessage(message);
        }

        if (data.status === "complete") {
          setIsGenerating(false);
          setProgress(100);
          checkStatus(session_id);
        } else if (data.status === "error") {
          setIsGenerating(false);
          toast.error(`Error: ${data.message}`);
        }
      };
      ws.onerror = () => {
        // If WebSocket fails, try polling status
        checkStatus(session_id);
        const interval = setInterval(() => {
          checkStatus(session_id).then(() => {
            if (!isGenerating) {
              clearInterval(interval);
            }
          });
        }, 2000);
      };
    } catch (err) {
      toast.error("System Error");
      setIsGenerating(false);
    }
  };

  const addLogMessage = (message: string) => {
    setLogMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  return (
    <div className="min-h-[calc(100vh-80px)] flex flex-col bg-black/20 mx-auto max-w-[1600px] border-x border-white/5 shadow-2xl">
      <div className="flex-1 flex flex-col p-8 space-y-6">

        {/* Header */}
        <div className="shrink-0 pb-6 border-b border-white/5 bg-black/40 backdrop-blur-xl -mx-8 px-8 pt-8">
          <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6">
            <div className="space-y-1">
              <h1 className="text-3xl font-black tracking-tighter uppercase shiny-text">Studio</h1>
              <p className="text-[9px] font-black uppercase tracking-[0.3em] text-slate-500">Create & Generate Videos</p>
            </div>
            <button
              onClick={startMimic}
              disabled={isGenerating || !refFile || materialFiles.length === 0}
              className="btn-premium flex items-center gap-3 disabled:opacity-20 shrink-0"
            >
              <span>Generate</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Upload Modules & Logs */}
        <div className="flex-1 min-h-0 flex gap-6">
          <div className="flex-1 min-h-0 space-y-6">

            {/* Reference */}
            <div className={`module ${refFile ? 'module-active-indigo' : ''}`}>
              <div className="flex flex-col md:flex-row gap-6">
                <div className="md:w-56 space-y-3">
                  <div className="h-10 w-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                    <Video className="h-4 w-4 text-indigo-400" />
                  </div>
                  <div>
                    <h3 className="text-xs font-black uppercase text-white">01. Reference Video</h3>
                    <p className="text-[9px] text-slate-500 uppercase tracking-wider mt-1.5">
                      Blueprint for synthesis
                    </p>
                  </div>
                </div>

              <div className="flex-1 min-w-0">
                <div className="h-[240px] rounded-2xl border-2 border-dashed border-white/10 bg-white/[0.02] hover:bg-indigo-500/[0.03] hover:border-indigo-500/20 transition-all flex flex-col items-center justify-center cursor-pointer relative group overflow-hidden">
                  <input type="file" onChange={handleRefUpload} accept="video/*" className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                  {refFile ? (
                    <>
                      <div className="absolute inset-0 rounded-2xl bg-black border border-indigo-500/20 overflow-hidden">
                        <video src={URL.createObjectURL(refFile)} className="w-full h-full object-cover opacity-50" />
                        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button onClick={(e) => { e.stopPropagation(); setRefFile(null); }} className="h-10 w-10 rounded-xl bg-red-500/20 border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition-all flex items-center justify-center">
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <div className="relative z-10 text-[10px] font-black uppercase tracking-widest text-indigo-400 bg-black/60 px-3 py-1 rounded">
                        Reference Acquired
                      </div>
                    </>
                  ) : (
                    <>
                      <Plus className="h-7 w-7 text-indigo-500/20 mb-3 group-hover:scale-110 transition-transform" />
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-700 group-hover:text-indigo-400">Drop Reference Video</span>
                    </>
                  )}
                </div>
              </div>
              </div>
            </div>

            {/* Source Clips */}
            <div className={`module ${materialFiles.length > 0 ? 'module-active-cyan' : ''}`}>
              <div className="flex flex-col md:flex-row gap-6">
                <div className="md:w-56 space-y-3">
                  <div className="h-10 w-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                    <MonitorPlay className="h-4 w-4 text-cyan-400" />
                  </div>
                  <div>
                    <h3 className="text-xs font-black uppercase text-white">02. Source Clips</h3>
                    <p className="text-[9px] text-slate-500 uppercase tracking-wider mt-1.5">
                      Raw material for synthesis
                    </p>
                    {materialFiles.length > 0 && (
                      <span className="inline-block mt-2 text-[9px] font-black text-white/40 bg-white/5 px-3 py-1 rounded-full">
                        {materialFiles.length} Staged
                      </span>
                    )}
                  </div>
                </div>

              <div className="flex-1 min-w-0">
                <div className="h-[240px] rounded-2xl border-2 border-dashed border-white/10 bg-white/[0.02] hover:bg-cyan-500/[0.03] hover:border-cyan-500/20 transition-all flex flex-col items-center justify-center cursor-pointer relative group overflow-hidden">
                  <input type="file" onChange={handleMaterialUpload} multiple accept="video/*" className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                  {materialFiles.length === 0 ? (
                    <>
                      <Upload className="h-7 w-7 text-cyan-500/20 mb-3 group-hover:scale-110 transition-transform" />
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-700 group-hover:text-cyan-400">Stage Source Clips</span>
                    </>
                  ) : (
                    <div className="w-full h-full p-4 flex flex-col items-center justify-center gap-2 shrink-0">
                      <div className="text-[10px] font-black uppercase tracking-widest text-cyan-400 shrink-0">
                        {materialFiles.length} File{materialFiles.length !== 1 ? 's' : ''} Uploaded
                      </div>
                      <div className="w-full flex-1 min-h-0 grid grid-cols-4 gap-2 overflow-y-auto pr-1 custom-scrollbar">
                        {materialFiles.map((file, i) => (
                          <div key={i} className="h-16 rounded-lg bg-black border border-white/5 overflow-hidden relative group/item shrink-0">
                            <video src={URL.createObjectURL(file)} className="w-full h-full object-cover opacity-40 group-hover/item:opacity-70 transition-opacity" />
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                setMaterialFiles(prev => prev.filter((_, idx) => idx !== i));
                              }} 
                              className="absolute top-0.5 right-0.5 h-4 w-4 rounded bg-red-500/80 text-white opacity-0 group-hover/item:opacity-100 transition-all flex items-center justify-center"
                            >
                              <X className="h-2.5 w-2.5" />
                            </button>
                          </div>
                        ))}
                      </div>
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider shrink-0">Click to add more</span>
                    </div>
                  )}
                </div>
              </div>
              </div>
            </div>
          </div>

          {/* Logs Box */}
          <div className="w-80 shrink-0">
            <div className="module h-full flex flex-col">
              <div className="flex items-center gap-2 mb-4">
                <div className="h-2 w-2 rounded-full bg-cyan-500 animate-pulse" />
                <h3 className="text-xs font-black uppercase text-white">Show Thinking</h3>
              </div>
              <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar pr-2">
                <div className="space-y-2">
                  {logMessages.length === 0 ? (
                    <div className="text-[9px] text-slate-500 uppercase tracking-wider">
                      Waiting for activity...
                    </div>
                  ) : (
                    logMessages.map((msg, i) => (
                      <div key={i} className="text-[9px] text-slate-400 font-mono leading-relaxed">
                        {msg}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress */}
        {(isGenerating || resultVideoUrl) && (
          <div className="module-progress">
            <div className="flex justify-between items-end mb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">{statusMsg || (resultVideoUrl ? "Complete!" : "Processing...")}</span>
                </div>
              </div>
              <div className="text-3xl font-black text-white">{Math.round(progress)}%</div>
            </div>
            <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-indigo-600 via-cyan-400 to-indigo-600 transition-all duration-1000" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}


      </div>
    </div>
  );
}
