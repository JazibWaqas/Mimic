"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ProgressTracker } from "@/components/ProgressTracker";
import { Button } from "@/components/ui/button";
import { generateVideo, getStatus } from "@/lib/api";
import { toast } from "sonner";

export default function GeneratePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const sessionId = params.id;
  const [started, setStarted] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function start() {
      if (started) return;
      setStarted(true);
      try {
        await generateVideo(sessionId);
      } catch (e: any) {
        toast.error(e?.message || "Failed to start generation");
      }
    }

    start();

    const interval = setInterval(async () => {
      if (!sessionId || sessionId === "undefined") return;
      try {
        const status = await getStatus(sessionId);
        if (cancelled) return;

        if (status.status === "complete") {
          clearInterval(interval);
          router.push(`/result/${sessionId}`);
        }

        if (status.status === "error") {
          clearInterval(interval);
          toast.error(status.error || "Generation failed");
        }
      } catch {
        // ignore transient errors
      }
    }, 1000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [router, sessionId, started]);

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-3xl px-6 py-16 space-y-10">
        <div className="flex items-center justify-end">
          <Button variant="secondary" onClick={() => router.push("/upload")}>
            Cancel
          </Button>
        </div>
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">✨ Creating Your Video...</h1>
          <p className="text-muted-foreground">Powered by Gemini 3 Flash Preview</p>
        </div>
        <ProgressTracker sessionId={sessionId} />
      </div>
    </main>
  );
}


