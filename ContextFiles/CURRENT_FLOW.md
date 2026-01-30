# 🌊 MIMIC - Agentic Development Flow (V7.1)

This document details the exact sequence of logic implemented in the MIMIC pipeline as of **January 30, 2026**.

---

## 🚀 The Agentic Flow (Plan -> Execute)

### 1. Pre-Analysis (The Brain)
- **Visual Scene Grounding:** FFmpeg identifies physical cuts to anchor the AI's temporal reasoning.
- **Rhythmic Extraction:** Librosa extracts the BPM and beat grid from the reference audio.
- **Gemini Analysis:** mapping the "Aesthetic Blueprint" (Energy, Motion, Vibes, Arc Stage).

### 2. Strategic Planning (The Advisor)
- **Library Audit:** The Advisor scans all clip analysis files to identify material coverage and gaps.
- **Narrative Strategy:** Injects weights into the matching engine to ensure a coherent story arc (e.g., "Intro" clips for start segments).

### 3. Selective Assembly (The Editor)
- **Weighted-Greedy Search:** Scores clips based on Discovery Bonus (+40), Vibe Match (+15), and Arc Consistency (+10).
- **Beat Snapping:** Mathematically aligns cut transitions to the nearest rhythmic anchor where possible.
- **Frame-Accurate Extractions:** FFmpeg surgical cuts with stream re-encoding for precision.

### 4. Output Generation (The Renderer)
- **Assembly:** Concatenates segments and merges original reference audio.
- **Validation:** Final duration check and integrity verification.

---

## 🏗️ Technical Integrity

- **Standardization Cache:** 100% persistent. Clips are standardized once and reused across sessions.
- **Timeline Continuity:** Zero-gap enforcement via mathematical start/end snapping.
- **Whitebox Reasoning:** Every single cut has a stored "Reasoning String" visible in logs and the Vault.

---

## 🏗️ Upcoming Stage

### Stage 6: Post-Render Reflection
- **Task:** Final judicial audit where Gemini "watches" the render.
- **Status:** Planned for V8.0.

---

**Last Updated:** January 31, 2026  
**Status:** 🟡 V7.1 Verified  
