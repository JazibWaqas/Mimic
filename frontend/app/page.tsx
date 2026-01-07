import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="mimic-fade-in space-y-6">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold tracking-wide text-muted-foreground">
              MIMIC
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <Link href="/history" className="hover:text-foreground transition-colors">
                History
              </Link>
            </div>
          </div>

          <div className="mimic-slide-up space-y-5">
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">
              Steal the Structure
              <br />
              of Any Viral Video
            </h1>
            <p className="max-w-2xl text-lg text-muted-foreground">
              Upload a reference → add your clips → get a perfectly timed video in ~60 seconds.
              Powered by Gemini 3.
            </p>
            <div className="flex items-center gap-4">
              <Button asChild className="mimic-pulse-glow">
                <Link href="/upload">Get Started →</Link>
              </Button>
              <Button asChild variant="secondary">
                <Link href="/upload">Upload Videos</Link>
              </Button>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2 pt-10">
            <Card className="bg-card border-border p-6">
              <div className="text-sm font-semibold text-muted-foreground mb-3">Before</div>
              <div className="h-48 rounded-lg bg-secondary border border-border flex items-center justify-center text-muted-foreground">
                Random clips
              </div>
            </Card>
            <Card className="bg-card border-border p-6">
              <div className="text-sm font-semibold text-muted-foreground mb-3">After</div>
              <div className="h-48 rounded-lg bg-secondary border border-border flex items-center justify-center text-muted-foreground">
                Perfectly synced cuts
              </div>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}
