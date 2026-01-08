"use client";

import { useEffect, useMemo, useState } from "react";
import { Progress } from "@/components/ui/progress";
import { Check, Loader2 } from "lucide-react";
import { getWebSocketUrl } from "@/lib/api";

interface ProgressStep {
  id: string;
  title: string;
  subtitle?: string;
  status: "pending" | "active" | "complete" | "error";
}

interface ProgressTrackerProps {
  sessionId: string;
}

export function ProgressTracker({ sessionId }: ProgressTrackerProps) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");

  const baseSteps = useMemo<ProgressStep[]>(
    () => [
      { id: "analyze_ref", title: "Analyzing reference", status: "pending" },
      { id: "analyze_clips", title: "Analyzing clips", status: "pending" },
      { id: "matching", title: "Creating sequence", status: "pending" },
      { id: "rendering", title: "Rendering video", status: "pending" },
      { id: "complete", title: "Finishing up", status: "pending" },
    ],
    []
  );

  const [steps, setSteps] = useState<ProgressStep[]>(baseSteps);

  useEffect(() => {
    setSteps(baseSteps);
  }, [baseSteps]);

  useEffect(() => {
    if (!sessionId || sessionId === "undefined") return;
    const ws = new WebSocket(getWebSocketUrl(sessionId));

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const p = Math.max(0, Math.min(1, Number(data.progress ?? 0)));
      setProgress(p * 100);
      setCurrentStep(String(data.message ?? ""));

      setSteps((prev) => {
        // Calculate which step index is currently active based on progress (0.0 to 1.0)
        // We have 5 steps, so each step is roughly 0.2 of the progress.
        const currentActiveIndex = Math.min(Math.floor(p * prev.length), prev.length - 1);

        return prev.map((step, index) => {
          if (index < currentActiveIndex) return { ...step, status: "complete" as const };
          if (index === currentActiveIndex) return { ...step, status: "active" as const };
          return { ...step, status: "pending" as const };
        });
      });
    };

    return () => ws.close();
  }, [sessionId]);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold">Creating Your Video...</h3>
          <span className="text-sm text-muted-foreground">{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className="h-2" />
        {currentStep && (
          <p className="mt-2 text-sm text-muted-foreground">{currentStep}</p>
        )}
      </div>

      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id} className="flex items-start gap-3">
            <div className="mt-0.5">
              {step.status === "complete" && (
                <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
                  <Check className="w-3 h-3 text-white" />
                </div>
              )}
              {step.status === "active" && (
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              )}
              {step.status === "pending" && (
                <div className="w-5 h-5 rounded-full border-2 border-border" />
              )}
            </div>
            <div>
              <p
                className={[
                  "font-medium",
                  step.status === "complete"
                    ? "text-emerald-500"
                    : step.status === "active"
                      ? "text-primary"
                      : "text-muted-foreground",
                ].join(" ")}
              >
                {step.title}
              </p>
              {step.subtitle && (
                <p className="text-sm text-muted-foreground">{step.subtitle}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


