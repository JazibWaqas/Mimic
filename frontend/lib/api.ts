const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadFiles(reference: File, clips: File[]) {
  const formData = new FormData();
  formData.append("reference", reference);
  clips.forEach((clip) => formData.append("clips", clip));

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) throw new Error("Upload failed");
  return response.json();
}

export async function generateVideo(sessionId: string) {
  const response = await fetch(`${API_BASE}/api/generate/${sessionId}`, {
    method: "POST",
  });

  if (!response.ok) throw new Error("Generation failed");
  return response.json();
}

export async function getStatus(sessionId: string) {
  const response = await fetch(`${API_BASE}/api/status/${sessionId}`);
  if (!response.ok) throw new Error("Status check failed");
  return response.json();
}

export async function getHistory() {
  const response = await fetch(`${API_BASE}/api/history`);
  if (!response.ok) throw new Error("History fetch failed");
  return response.json();
}

export function getDownloadUrl(sessionId: string) {
  // Add timestamp to prevent browser caching
  const timestamp = Date.now();
  return `${API_BASE}/api/download/${sessionId}?t=${timestamp}`;
}

export function getWebSocketUrl(sessionId: string) {
  const base = new URL(API_BASE);
  base.protocol = base.protocol === "https:" ? "wss:" : "ws:";
  base.pathname = `/ws/progress/${sessionId}`;
  base.search = "";
  return base.toString();
}


