// ============================================================================
// TYPESCRIPT TYPES
// ============================================================================
// Shared types across the application
// ============================================================================

export interface Clip {
    session_id: string;
    filename: string;
    path: string;
    thumbnail_url?: string;
    size: number;
    created_at: number;
    tags?: string[];
}

export interface Result {
    filename: string;
    url: string;
    thumbnail_url?: string;
    size: number;
    created_at: number;
}

export interface Reference {
    filename: string;
    path: string;
    thumbnail_url?: string;
    size: number;
    created_at: number;
}

export interface ProgressData {
    status: "uploaded" | "processing" | "complete" | "error";
    progress: number;
    message: string;
}
