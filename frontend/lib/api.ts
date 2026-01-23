// ============================================================================
// CENTRALIZED API CLIENT
// ============================================================================
// All backend communication goes through here
// Makes it easy to change endpoints, add error handling, etc.
// ============================================================================

const API_BASE = "http://localhost:8000";

export const api = {
  // ==================== UPLOAD ====================
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

  // ==================== GENERATION ====================
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

  // ==================== CLIPS (Assets Page) ====================
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

  // ==================== RESULTS (Projects Page) ====================
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

  // ==================== REFERENCES (Projects Page) ====================
  fetchReferences: async () => {
    const res = await fetch(`${API_BASE}/api/references`);
    if (!res.ok) throw new Error("Failed to fetch references");
    return res.json();
  },
};
