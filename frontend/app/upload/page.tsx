"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { uploadFiles } from "@/lib/api";
import { FileUpload } from "@/components/FileUpload";
import { toast } from "sonner";

export default function UploadPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"auto" | "manual">("auto");

  // Auto mode state
  const [referenceFiles, setReferenceFiles] = useState<File[]>([]);
  const [clipFiles, setClipFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // Manual mode state
  const [manualClips, setManualClips] = useState<File[]>([]);
  const [blueprintJSON, setBlueprintJSON] = useState("");
  const [clipAnalysisJSON, setClipAnalysisJSON] = useState("");

  const handleAutoMode = async () => {
    if (referenceFiles.length !== 1 || clipFiles.length < 2) return;

    setIsUploading(true);
    try {
      const result = await uploadFiles(referenceFiles[0], clipFiles);
      const sessionId = result.session_id as string;

      // Store reference for playback
      try {
        const refUrl = URL.createObjectURL(referenceFiles[0]);
        sessionStorage.setItem(`mimic_reference_url_${sessionId}`, refUrl);
      } catch { }

      router.push(`/generate/${sessionId}`);
    } catch (e: any) {
      toast.error(e?.message || "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const handleManualMode = async () => {
    if (manualClips.length < 2 || !blueprintJSON || !clipAnalysisJSON) {
      toast.error("Please provide clips and both JSON analyses");
      return;
    }

    // Validate JSON
    try {
      JSON.parse(blueprintJSON);
      JSON.parse(clipAnalysisJSON);
    } catch {
      toast.error("Invalid JSON format. Please check your input.");
      return;
    }

    setIsUploading(true);
    try {
      // Upload clips with manual analysis
      const formData = new FormData();
      formData.append("mode", "manual");
      formData.append("blueprint", blueprintJSON);
      formData.append("clip_analysis", clipAnalysisJSON);
      manualClips.forEach((clip) => formData.append("clips", clip));

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/upload-manual`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Manual upload failed");

      const result = await response.json();
      router.push(`/generate/${result.session_id}`);
    } catch (e: any) {
      toast.error(e?.message || "Manual mode failed");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-5xl px-6 py-12 space-y-8">
        <div className="space-y-2">
          <div className="text-sm text-muted-foreground">Step 1/3</div>
          <h1 className="text-3xl font-bold tracking-tight">Upload Your Videos</h1>
          <p className="text-muted-foreground">
            Choose Auto Mode (uses Gemini API) or Manual Mode (paste AI Studio analysis)
          </p>
        </div>

        <Tabs value={mode} onValueChange={(v) => setMode(v as "auto" | "manual")}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="auto">🤖 Auto Mode (API)</TabsTrigger>
            <TabsTrigger value="manual">✍️ Manual Mode (Paste JSON)</TabsTrigger>
          </TabsList>

          <TabsContent value="auto" className="space-y-4 mt-6">
            <Card className="bg-card border-border p-6 space-y-4">
              <div className="font-semibold">📹 Reference Video</div>
              <FileUpload type="reference" onFilesChange={setReferenceFiles} maxFiles={1} />
            </Card>

            <Card className="bg-card border-border p-6 space-y-4">
              <div className="font-semibold">🎥 Your Clips (2+ required)</div>
              <FileUpload type="clips" onFilesChange={setClipFiles} maxFiles={10} />
            </Card>

            <div className="flex justify-end">
              <Button
                disabled={referenceFiles.length !== 1 || clipFiles.length < 2 || isUploading}
                onClick={handleAutoMode}
              >
                {isUploading ? "Uploading..." : "Continue →"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="manual" className="space-y-4 mt-6">
            <Card className="bg-card border-border p-6 space-y-4">
              <div className="font-semibold">📋 Reference Blueprint JSON</div>
              <div className="text-sm text-muted-foreground mb-2">
                Paste the StyleBlueprint JSON from AI Studio analysis of your reference video
              </div>
              <textarea
                className="w-full h-40 p-3 bg-background border border-border rounded-lg font-mono text-sm"
                placeholder={`{\n  "total_duration": 12.5,\n  "segments": [\n    {\n      "id": 1,\n      "start": 0.0,\n      "end": 3.2,\n      "duration": 3.2,\n      "energy": "High",\n      "motion": "Dynamic"\n    }\n  ]\n}`}
                value={blueprintJSON}
                onChange={(e) => setBlueprintJSON(e.target.value)}
              />
            </Card>

            <Card className="bg-card border-border p-6 space-y-4">
              <div className="font-semibold">📊 Clip Analysis JSON</div>
              <div className="text-sm text-muted-foreground mb-2">
                Paste the ClipIndex JSON with energy/motion analysis for each clip
              </div>
              <textarea
                className="w-full h-40 p-3 bg-background border border-border rounded-lg font-mono text-sm"
                placeholder={`{\n  "clips": [\n    {\n      "filename": "clip1.mp4",\n      "energy": "High",\n      "motion": "Dynamic"\n    },\n    {\n      "filename": "clip2.mp4",\n      "energy": "Medium",\n      "motion": "Static"\n    }\n  ]\n}`}
                value={clipAnalysisJSON}
                onChange={(e) => setClipAnalysisJSON(e.target.value)}
              />
            </Card>

            <Card className="bg-card border-border p-6 space-y-4">
              <div className="font-semibold">🎥 Your Clips (2+ required)</div>
              <FileUpload type="clips" onFilesChange={setManualClips} maxFiles={10} />
            </Card>

            <div className="flex justify-end">
              <Button
                disabled={manualClips.length < 2 || !blueprintJSON || !clipAnalysisJSON || isUploading}
                onClick={handleManualMode}
              >
                {isUploading ? "Processing..." : "Render Video →"}
              </Button>
            </div>
          </TabsContent>
        </Tabs>

        <Card className="bg-blue-500/10 border-blue-500/20 p-4">
          <div className="text-sm space-y-2">
            <div className="font-semibold text-blue-400">💡 Manual Mode Tips:</div>
            <ul className="text-blue-300 space-y-1 ml-4 list-disc">
              <li>Use AI Studio to analyze your reference video once</li>
              <li>Copy the JSON output and paste it here</li>
              <li>Analyze each clip in AI Studio and compile the results</li>
              <li>This bypasses API quota limits - test unlimited times!</li>
            </ul>
          </div>
        </Card>
      </div>
    </main>
  );
}
