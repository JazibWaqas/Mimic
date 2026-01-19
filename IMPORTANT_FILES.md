# 🗺️ MIMIC - Important Files & Linkages

This document identifies the critical files in the MIMIC project and how they connect to form the complete pipeline.

---

## 🏗️ Technical Architecture Map (Updated Jan 19, 2026 - 22:10 PM)

### 1. The Core Engine (Backend Logic)
These files reside in `backend/engine/` and form the heart of the system.

| File | Responsibility | Connected To |
|------|--------------|--------------|
| `orchestrator.py` | **The Brain.** Orchestrates the entire pipeline. Now includes **Scene Detection** as a pre-analysis step. | Calls `brain.py`, `editor.py`, `processors.py`. |
| `brain.py` | **AI Integration.** Handles Gemini 3 API calls with **Compact Hint Encoding** (`HD, MS` codes). | Called by `orchestrator.py`. Uses `models.py`. |
| `editor.py` | **Matching Algorithm.** Match clips to segments. Now respects **Visual Scene Anchors**. | Called by `orchestrator.py`. Uses `models.py`. |
| `processors.py` | **Video Execution.** FFmpeg wrappers. Includes **Scene Detection** (`detect_scene_changes`). | Called by `orchestrator.py`. |

### 2. The API Layer (Backend Entry)
| File | Responsibility | Connected To |
|------|--------------|--------------|
| `main.py` | **FastAPI Server.** Defines REST endpoints and WebSockets for progress tracking. | Calls `orchestrator.py`. Communicates with Frontend. |
| `models.py` | **Data Structures.** Pydantic models that ensure data consistency across the backend. | Used by almost every backend file. |
| `utils.py` | **Utility functions.** File management, directory creation, and session cleanup. | Used across the backend. |

### 3. The Frontend (Next.js)
| File | Responsibility | Connected To |
|------|--------------|--------------|
| `app/page.tsx` | Landing Page. | Links to `/upload`. |
| `app/upload/page.tsx` | File upload interface (Auto/Manual modes). | Calls `lib/api.ts`. |
| `app/generate/[id]/page.tsx` | Progress tracking page. | Connects to WebSocket in `main.py`. |
| `app/result/[id]/page.tsx` | Results gallery & side-by-side comparison. | Fetches results from `main.py`. |
| `lib/api.ts` | API Client. | Acts as the bridge between Frontend and Backend REST API. |

---

## 🔄 The Flow (How it's linked)

1.  **Frontend (`upload/page.tsx`)** sends files to **Backend (`main.py` -> `/api/upload`)**.
2.  **Backend** creates a `session_id` and saves files to `data/uploads/{session_id}/`.
3.  **Frontend** redirects to `/generate/{session_id}` and triggers **Backend (`/api/generate`)**.
4.  **Backend (`main.py`)** starts a background task calling **`orchestrator.py:run_mimic_pipeline`**.
5.  **`orchestrator.py`** then:
    - Calls **`processors.py`** to detect physical scene cuts in the reference first.
    - Calls **`brain.py`** to analyze the reference using those cuts as **anchors**.
    - Calls **`brain.py`** to analyze clips comprehensively (one call per clip).
    - Calls **`editor.py`** to create an EDL aligned to the **scene-anchored segments**.
    - Calls **`processors.py`** to render the final video using FFmpeg.
6.  **Backend (`main.py`)** sends updates via **WebSocket** to **Frontend (`ProgressTracker.tsx`)**.
7.  **Frontend** displays the final video from `data/results/`.

---

## ✅ What is Correct?
- **`editor.py`** is the LATEST matching engine. It implements the high-energy rapid cuts that make the edits feel professional.
- **`brain.py`** uses Gemini 3 comprehensively. One API call per clip extracts everything needed.
- **`models.py`** is the single source of truth for data structures.

## ⚠️ What was Incorrect?
- `editor_fixed.py` was a redundant older version (now removed).
- Documentation (Master Build Plan) was outdated relative to recent "Rapid Cuts" improvements.
