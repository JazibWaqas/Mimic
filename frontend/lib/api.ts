// ============================================================================
// CENTRALIZED API CLIENT
// ============================================================================
// All backend communication goes through here
// Makes it easy to change endpoints, add error handling, etc.
// ============================================================================

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const intelCache = new Map<string, any>();

export const api = {
  // ... existing uploadFiles, identify, startGeneration, etc.
  identify: async (reference: File) => {
    const formData = new FormData();
    formData.append("reference", reference);
    const res = await fetch(`${API_BASE}/api/identify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Identity scan failed");
    return res.json();
  },
  uploadFiles: async (reference: File, clips: File[]) => {
    const formData = new FormData();
    formData.append("reference", reference);
    clips.forEach((clip) => formData.append("clips", clip));

    const res = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },

  startGeneration: async (sessionId: string) => {
    const res = await fetch(`${API_BASE}/api/generate/${sessionId}`, {
      method: "POST",
    });

    if (!res.ok) throw new Error("Generation failed");
    return res.json();
  },

  connectProgress: (sessionId: string) => {
    return new WebSocket(`ws://localhost:8000/ws/progress/${sessionId}`);
  },

  fetchClips: async () => {
    const res = await fetch(`${API_BASE}/api/clips`);
    if (!res.ok) throw new Error("Failed to fetch clips");
    return res.json();
  },

  deleteClip: async (sessionId: string, filename: string) => {
    const res = await fetch(`${API_BASE}/api/clips/${sessionId}/${filename}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete clip");
    return res.json();
  },

  fetchResults: async () => {
    const res = await fetch(`${API_BASE}/api/results`);
    if (!res.ok) throw new Error("Failed to fetch results");
    return res.json();
  },

  deleteResult: async (filename: string) => {
    const res = await fetch(`${API_BASE}/api/results/${filename}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete result");
    return res.json();
  },

  renameFile: async (type: string, oldFilename: string, newFilename: string) => {
    const res = await fetch(`${API_BASE}/api/rename?type=${type}&old_filename=${encodeURIComponent(oldFilename)}&new_filename=${encodeURIComponent(newFilename)}`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to rename file");
    return res.json();
  },

  fetchReferences: async () => {
    const res = await fetch(`${API_BASE}/api/references`);
    if (!res.ok) throw new Error("Failed to fetch references");
    return res.json();
  },

  fetchIntelligence: async (type: string, filename: string) => {
    const cacheKey = `${type}:${filename}`;
    if (intelCache.has(cacheKey)) return intelCache.get(cacheKey);

    const res = await fetch(`${API_BASE}/api/intelligence?type=${type}&filename=${encodeURIComponent(filename)}`);
    if (!res.ok) throw new Error("Intelligence data not found");
    const data = await res.json();
    intelCache.set(cacheKey, data);
    return data;
  },
};
