"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getHistory } from "@/lib/api";

export default function HistoryPage() {
  const [projects, setProjects] = useState<any[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const data = await getHistory();
      if (!cancelled) setProjects(data.projects || []);
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-6xl px-6 py-12 space-y-8">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">History</h1>
            <p className="text-muted-foreground">Your past projects (in-memory)</p>
          </div>
          <Button asChild>
            <Link href="/upload">New Project</Link>
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {projects.map((p) => (
            <Card key={p.session_id} className="bg-card border-border p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="font-semibold truncate">{p.reference_filename}</div>
                <Badge variant="secondary">{p.status}</Badge>
              </div>
              <div className="text-sm text-muted-foreground">
                {p.clip_count} clips
              </div>
              <Button asChild variant="secondary" className="w-full">
                <Link href={`/result/${p.session_id}`}>View</Link>
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}


