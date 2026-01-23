"use client";

import { useState } from "react";
import { Upload, Video, ArrowRight, MonitorPlay, X, Plus, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function StudioPage() {
  const [refFile, setRefFile] = useState<File | null>(null);
  const [materialFiles, setMaterialFiles] = useState<File[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState("");

  const handleRefUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setRefFile(e.target.files[0]);
      toast.success("Reference Acquired");
    }
  };

  const handleMaterialUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setMaterialFiles(Array.from(e.target.files));
      toast.success(`${e.target.files.length} Assets Staged`);
    }
  };

  const startMimic = async () => {
    if (!refFile || materialFiles.length === 0) {
      toast.error("Reference & Material Required");
      return;
    }

    setIsGenerating(true);
    setStatusMsg("Initializing...");
    setProgress(10);

    try {
      const { session_id } = await api.uploadFiles(refFile, materialFiles);
      await api.startGeneration(session_id);

      const ws = api.connectProgress(session_id);
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setProgress(data.progress * 100);
        setStatusMsg(data.message);

        if (data.status === "complete") {
          toast.success("Synthesis Complete!");
          setIsGenerating(false);
          setProgress(0);
        } else if (data.status === "error") {
          toast.error(`Error: ${data.message}`);
          setIsGenerating(false);
        }
      };
    } catch (err) {
      toast.error("System Error");
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen p-8 pb-40">
      <div className="max-w-6xl mx-auto space-y-12">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 rounded-full border border-indigo-500/20">
              <Sparkles className="h-3 w-3 text-indigo-400" />
              <span className="text-[9px] font-black uppercase tracking-wider text-indigo-400">Studio</span>
            </div>
            <h1 className="text-5xl font-black tracking-tight uppercase">
              <span className="shiny-text">Create.</span> <span className="text-white/20">Mimic.</span>
            </h1>
            <p className="text-xs text-slate-500 uppercase tracking-widest">
              Neural video synthesis engine
            </p>
          </div>

          <button
            onClick={startMimic}
            disabled={isGenerating || !refFile || materialFiles.length === 0}
            className="btn-premium flex items-center gap-3 disabled:opacity-20"
          >
            <span>Initialize</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>

        {/* Upload Modules */}
        <div className="space-y-8">

          {/* Reference */}
          <div className={`module ${refFile ? 'module-active-indigo' : ''}`}>
            <div className="flex flex-col md:flex-row gap-8">
              <div className="md:w-64 space-y-4">
                <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                  <Video className="h-5 w-5 text-indigo-400" />
                </div>
                <div>
                  <h3 className="text-sm font-black uppercase text-white">01. Reference</h3>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mt-2">
                    Blueprint for synthesis
                  </p>
                </div>
              </div>

              <div className="flex-1 min-h-[300px]">
                {refFile ? (
                  <div className="h-full rounded-3xl bg-black border border-indigo-500/20 overflow-hidden relative group">
                    <video src={URL.createObjectURL(refFile)} className="w-full h-full object-cover opacity-50" />
                    <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => setRefFile(null)} className="h-12 w-12 rounded-xl bg-red-500/20 border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition-all flex items-center justify-center">
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="h-full rounded-3xl border-2 border-dashed border-white/10 bg-white/[0.02] hover:bg-indigo-500/[0.03] hover:border-indigo-500/20 transition-all flex flex-col items-center justify-center cursor-pointer relative group">
                    <input type="file" onChange={handleRefUpload} accept="video/*" className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                    <Plus className="h-8 w-8 text-indigo-500/20 mb-4 group-hover:scale-110 transition-transform" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-700 group-hover:text-indigo-400">Drop Reference</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Materials */}
          <div className={`module ${materialFiles.length > 0 ? 'module-active-cyan' : ''}`}>
            <div className="flex flex-col md:flex-row gap-8">
              <div className="md:w-64 space-y-4">
                <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                  <MonitorPlay className="h-5 w-5 text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-sm font-black uppercase text-white">02. Source Assets</h3>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mt-2">
                    Raw material for synthesis
                  </p>
                  {materialFiles.length > 0 && (
                    <span className="inline-block mt-3 text-[9px] font-black text-white/40 bg-white/5 px-3 py-1 rounded-full">
                      {materialFiles.length} Staged
                    </span>
                  )}
                </div>
              </div>

              <div className="flex-1 min-h-[300px]">
                {materialFiles.length > 0 ? (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                    {materialFiles.map((file, i) => (
                      <div key={i} className="aspect-video rounded-xl bg-black border border-white/5 overflow-hidden relative group">
                        <video src={URL.createObjectURL(file)} className="w-full h-full object-cover opacity-30 group-hover:opacity-60 transition-opacity" />
                        <button onClick={() => setMaterialFiles(prev => prev.filter((_, idx) => idx !== i))} className="absolute top-2 right-2 h-6 w-6 rounded-lg bg-red-500/20 text-red-500 opacity-0 group-hover:opacity-100 transition-all border border-red-500/20 flex items-center justify-center">
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                    <div className="aspect-video rounded-xl border-2 border-dashed border-white/5 flex items-center justify-center relative hover:bg-cyan-500/[0.03] hover:border-cyan-500/20 transition-all cursor-pointer group">
                      <input type="file" onChange={handleMaterialUpload} multiple accept="video/*" className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                      <Plus className="h-6 w-6 text-slate-700 group-hover:text-cyan-400 transition-colors" />
                    </div>
                  </div>
                ) : (
                  <div className="h-full rounded-3xl border-2 border-dashed border-white/10 bg-white/[0.02] hover:bg-cyan-500/[0.03] hover:border-cyan-500/20 transition-all flex flex-col items-center justify-center cursor-pointer relative group">
                    <input type="file" onChange={handleMaterialUpload} multiple accept="video/*" className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                    <Upload className="h-8 w-8 text-cyan-500/20 mb-4 group-hover:scale-110 transition-transform" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-700 group-hover:text-cyan-400">Stage Source Clips</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Progress */}
        {isGenerating && (
          <div className="module-progress">
            <div className="flex justify-between items-end mb-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">{statusMsg}</span>
                </div>
              </div>
              <div className="text-4xl font-black text-white">{Math.round(progress)}%</div>
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
