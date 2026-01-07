"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { FileUpload } from "@/components/FileUpload";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { uploadFiles } from "@/lib/api";
import { toast } from "sonner";

export default function UploadPage() {
  const router = useRouter();

  const [referenceFiles, setReferenceFiles] = useState<File[]>([]);
  const [clipFiles, setClipFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const canContinue = useMemo(() => referenceFiles.length === 1 && clipFiles.length >= 2, [
    referenceFiles.length,
    clipFiles.length,
  ]);

  const onContinue = async () => {
    if (!canContinue) return;
    setIsUploading(true);
    try {
      const reference = referenceFiles[0];
      const result = await uploadFiles(reference, clipFiles);
      const sessionId = result.session_id as string;

      // Keep reference playable for side-by-side result page (same tab/session).
      try {
        const refUrl = URL.createObjectURL(reference);
        sessionStorage.setItem(`mimic_reference_url_${sessionId}`, refUrl);
      } catch {
        // ignore
      }

      router.push(`/generate/${sessionId}`);
    } catch (e: any) {
      toast.error(e?.message || "Upload failed");
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
            Upload a reference video (3–20s) and at least 2 clips.
          </p>
        </div>

        <Card className="bg-card border-border p-6 space-y-4">
          <div className="font-semibold">📹 Reference Video</div>
          <FileUpload type="reference" onFilesChange={setReferenceFiles} maxFiles={1} />
        </Card>

        <Card className="bg-card border-border p-6 space-y-4">
          <div className="font-semibold">🎥 Your Clips (2+ required)</div>
          <FileUpload type="clips" onFilesChange={setClipFiles} maxFiles={10} />
        </Card>

        <div className="flex justify-end">
          <Button disabled={!canContinue || isUploading} onClick={onContinue}>
            {isUploading ? "Uploading..." : "Continue →"}
          </Button>
        </div>
      </div>
    </main>
  );
}


