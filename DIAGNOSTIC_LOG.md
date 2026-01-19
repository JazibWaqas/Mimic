# 🔍 MIMIC - FORENSIC DIAGNOSTIC LOG

This document contains the raw forensic evidence and systematic diagnostic results gathered during Phase 1 of the "Precision Overhaul" (January 19, 2026). Use this to justify architectural pivots.

---

## 🔬 SYSTEMATIC DIAGNOSIS: PHASE 1 (Scientific Audit)

### 1. The Raw Data Evidence (JSON Cache Audit)
**Finding:** Inspected `ref_ee04c14e021e.json`. The segments returned by Gemini were mathematically "too perfect," indicating the AI was guessing rather than observing.
- Segment 2: 1.1s - 2.1s (Duration: 1.0s)
- Segment 3: 2.1s - 3.1s (Duration: 1.0s)
- Segment 4: 3.1s - 4.1s (Duration: 1.0s)
- **Proof:** Without "Scene Anchors" (visual hints), Gemini defaults to 1-second placeholders. It isn't actually finding the cuts.

### 2. The Prompt Audit (Why Gemini was "Lazy")
**File:** `brain.py:REFERENCE_ANALYSIS_PROMPT`
- **The Flaw:** We were asking for segments without providing the list of detected visual scene changes.
- **The Result:** We were forcing Gemini to do "Hard Scene Detection" (multimodal vision task) rather than "Creative Classification" (reasoning task).
- **Pivot:** Gemini is a genius at classification but mediocre at millisecond-precise cut detection. FFmpeg must handle the cuts; Gemini must handle the "vibe."

### 3. The Audio Sync Proof (The BPM Drift)
**Forensic Tool:** `librosa` v0.11.0
- **Reference Video (ref4.mp4):** Analyzed via `librosa.beat.beat_track`.
- **Resulting Data:** **129.20 BPM**.
- **The Glitch:** Our `editor.py` was hardcoded to `120.00 BPM`. 
- **The Impact:** A beat at 129.2 BPM happens every **0.46s**. Snapping to our 0.5s grid causes a cumulative drift of **0.6 seconds** by the end of a 14-second video. This makes the edit feel "laggy" to the human eye/ear.

### 4. The Scene Detection Proof (Timing Discrepancy)
**Forensic Tool:** FFmpeg `showinfo` filter.
- **Reference (ref4.mp4):** Real visual cuts at `4.9s`, `5.4s`, `5.7s`, `6.1s` (Erratic, rapid rhythm).
- **MIMIC Output (result4.mp4):** Cuts at `4.1s`, `4.8s`, `6.3s`.
- **Match Rate:** **0%**. 
- **Conclusion:** We were making a different video, not a "mimicked" one. We must anchor AI to these exact timestamps.

### 5. The Matching Trace (The "Lottery" Proof)
**Tool:** `trace_matching.py`
- **Finding:** Every clip was selected based purely on `lowest usage count`.
- **Missing:** Content/Semantic check. The AI didn't care if the segment needed "Action" or "Nature." It just picked the next available clip.

### 6. The FFmpeg Execution Audit (Keyframe Snapping)
**File:** `processors.py:extract_segment`
- **Issue:** Using `-c copy` for segment extraction.
- **The Physics:** Copy codec only cuts on Keyframes (GOP boundaries). If a beat happens at `3.5s` but the keyframe is at `3.1s` or `4.0s`, the cut drifts.
- **The Fix:** Must re-encode segments during extraction (`-c:v libx264`) to ensure frame-accuracy.

---

## 🛠️ THE EXPERT ACTION PLAN (Status: In Progress)

| Fix | Status | Note |
| :--- | :--- | :--- |
| **Scene Anchor Fix** | ✅ DONE | Passed visual cuts to Gemini as `scene_timestamps`. |
| **Clamping Fix** | ✅ DONE | Clamped cuts to ≥ 0.1s to prevent 0-duration Pydantic errors. |
| **Precision Rendering** | ✅ DONE | Switched to re-encoding for all extract/concat operations. |
| **Dynamic BPM Fix** | ⏳ NEXT | Replace hardcoded 120 BPM with `librosa` or Gemini estimate. |
| **Semantic Matching** | ⏳ NEXT | Map "Vibe" labels (Nature, Action) between segments and clips. |

---

## 📁 Diagnostic Evidence Files (Now Cleared for Performance)
- `temp/ref4_audio.wav` (Used for BPM detection)
- `temp/ref4_scenes.txt` (Used for visual cut audit)
- `temp/diagnose_audio.py` (The forensic script)
- `temp/trace_matching.py` (The rotation logic auditor)
- `ref_ee04c14e021e.json` (The "Lazy Gemini" proof)
