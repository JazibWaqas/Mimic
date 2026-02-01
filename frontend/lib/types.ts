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
    path: string;
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

export interface DirectorCritique {
    overall_score: number;
    monologue: string;
    star_performers: string[];
    dead_weight: string[];
    missing_ingredients: string[];
    technical_fidelity: string;
}
