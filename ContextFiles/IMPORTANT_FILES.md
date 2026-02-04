# 🗺️ MIMIC - Important Files & Linkages

This document identifies the critical files in the MIMIC project and how they connect to form the complete pipeline.

---

## 🏗️ Technical Architecture Map (Updated February 5, 2026)

### 1. The Core Engine (Backend Logic)
These files reside in `backend/engine/` and form the heart of the system.

| File | Responsibility | Connected To |
|------|--------------|--------------|
| `orchestrator.py` | **The Controller.** Orchestrates the 7-stage pipeline. Merges physical cuts with beat grids and assigns `cut_origin`. | Calls `brain.py`, `editor.py`, `processors.py`. |
| `brain.py` | **The AI.** Handles Gemini 3 API calls. Extracts "Editorial DNA" and "Contextual Best Moments." | Called by `orchestrator.py`. Uses `models.py`. |
| `editor.py` | **The Matcher.** implements **Director-First Pacing**. Uses narrative intent to lead and beats to snap. | Called by `orchestrator.py`. Uses `models.py`. |
| `processors.py` | **The Hand.** FFmpeg wrappers for standardized encoding, scene detection, and surgical cutting. | Called by `orchestrator.py`. |
| `reflector.py` | **The Critic.** Performs post-render AI reflection to judge story transfer. | Final stage of pipeline. |

---

## 🔄 The Flow (V12.1 Authority Model)

1.  **Reference Analysis:** `orchestrator.py` detects physical cuts and marks them as **"Sacred."**
2.  **Instruction extraction:** `brain.py` defines the energy and arc stages.
3.  **Clip Strategy:** `brain.py` finds best moments matching the energy-specific hold times (1.2s-6s).
4.  **Pacing Decision:** `editor.py` calculates a narrative duration first. If a cut is "Sacred", it **refuses** to subdivide it.
5.  **Rhythmic Snapping:** If audio is present, the narrative durations snap to the nearest beat.
6.  **Rendering:** FFmpeg executes the decisions.
7.  **Reflection:** Gemini watches the final MP4 and provides a Director's Monologue.

---

## ✅ The V12.1 Ground Truth
- **Editorial Intent > Beat Grid:** The most important rule in the codebase.
- **Sacred Cuts:** Real camera changes from the reference are never artificiality chopped.
- **Registration over Speed:** Ensuring the human eye has time (~1.2s) to register a shot.
