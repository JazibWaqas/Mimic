# 🌊 MIMIC - Current Development Flow

This document details the exact sequence of logic implemented in the MIMIC pipeline as of **January 21, 2026 - 02:08 AM PKT**.

---

## 🚀 The Pipeline (Step-by-Step)

### 1. Pre-Analysis & Caching (V6.0 Deep Semantic Analysis)

**Reference Video Analysis:**
- **Mute and Analyze:** FFmpeg creates a muted copy to bypass copyright blocks
- **Visual Scene Detection:** FFmpeg detects physical cuts in the reference video
- **Gemini V6.0 Analysis:** Analyzes muted video and extracts:
  - **Overall:** editing_style, emotional_intent, arc_description
  - **Per Segment:** energy, motion, vibe, arc_stage (Intro/Build-up/Peak/Outro), reasoning
- **Result:** Cached in `data/cache/ref_{hash}_hints0.json` (V6.0 format)
- **Muted Copy:** Cached in `data/cache/muted_{hash}.mp4`

**User Clips Analysis:**
- **Gemini V6.0 Comprehensive Analysis:** Every clip analyzed once, extracting:
  - Overall Energy/Motion
  - **Vibes:** Aesthetic/content tags (e.g., "Urban", "Nature", "Action")
  - **Content Description:** Detailed semantic description (e.g., "Person surfing at sunset")
  - **Three Best Moments:** Low/Medium/High energy windows with timestamps and reasoning
- **Result:** Cached in `data/cache/clip_comprehensive_{hash}.json` (V6.0 format)

### 2. Intelligent Matching (Editing Grammar System)

The `editor.py:match_clips_to_blueprint` function uses **Multi-Dimensional Scoring:**

**For Each Segment:**
1. **Clip Scoring (5 Factors):**
   - **Arc Stage Relevance (20 pts):** Matches intro/peak/outro keywords in content_description
   - **Vibe Matching (12 pts):** Semantic tag alignment
   - **Visual Cooldown (-50 pts):** Heavy penalty if clip used within 5 seconds
   - **Transition Smoothness (8 pts):** Rewards motion continuity from previous clip
   - **Usage Penalty (3 pts/use):** Encourages variety

2. **Adaptive Pacing:**
   - **Intro:** 2.0-3.5s cuts (slower, establishing)
   - **Build-up:** 0.5-1.2s cuts (accelerating)
   - **Peak:** 0.15-0.45s cuts (rapid fire)
   - **Outro:** Longer, breathing cuts

3. **Beat Alignment:**
   - BPM detected from reference audio (librosa)
   - Cuts snapped to nearest beat (±0.15s tolerance)

4. **Best Moment Selection:**
   - Uses pre-computed best moments for matched energy level
   - Tracks position within moment windows
   - Falls back to sequential if window exhausted

**Result:** Edit Decision List (EDL) with frame-perfect instructions and AI reasoning

### 3. Rendering (Frame-Perfect)

**Standardization:**
- All clips converted to consistent format (1080x1920, 30fps)
- Prevents FFmpeg failures during concatenation

**Precision Cuts:**
- FFmpeg uses `-ss` (start) and `-t` (duration) on re-encoded streams
- Ensures cuts are exactly where specified (no keyframe snapping)

**Timeline Validation:**
- Boundary enforcement: `decision_N.start = decision_N-1.end`
- Float snapping in segment subdivision
- Pydantic validation ensures no gaps/overlaps

**Audio Preservation:**
- Original reference audio extracted and merged with final edit
- Ensures rhythm matches music/sound perfectly

---

## 🧠 Editing Grammar Intelligence

### **Visual Memory:**
- Tracks when each clip was last used on timeline
- Prevents visual monotony with 5-second cooldown
- Heavy scoring penalty for recent reuse

### **Transition Awareness:**
- Remembers last clip's motion type
- Scores clips higher if motion continues smoothly
- Prevents jarring Dynamic → Static → Dynamic jumps

### **Semantic Understanding:**
- Matches clips based on content, not just energy
- Understands narrative arc progression
- Adapts pacing to story stage

### **Variety Enforcement:**
- Tracks usage count per clip
- Prevents any single clip from dominating
- Ensures fair distribution across material

---

## 🛠️ Developer Commands & Testing

### Running the End-to-End Test
Use `test_real_pipeline.py` to verify the backend without frontend interaction:
```bash
python test_real_pipeline.py
```
This script:
1. Picks a reference from `data/samples/reference/`
2. Picks clips from `data/samples/clips/`
3. Runs full V6.0 analysis + Editing Grammar
4. Reports on duration accuracy, clip usage, semantic matches

### Analyzing All References
Pre-analyze all reference videos with V6.0:
```bash
python analyze_references.py
```
Creates muted copies and extracts deep semantic metadata.

### Populating Clip Cache
Pre-analyze all clips with V6.0:
```bash
python populate_cache.py
```
Extracts vibes, content descriptions, and best moments.

### Checking API Key Status
```bash
python test_api_keys.py
```
Shows which of the 28 API keys are fresh vs exhausted.

---

## 📁 Directory Roles

- `data/uploads/`: Original files. NEVER modified.
- `data/cache/`: AI Analysis results (V6.0 format). Safe to delete (triggers re-analysis).
  - `ref_*.json`: Reference video analysis
  - `muted_*.mp4`: Muted reference copies for analysis
  - `clip_comprehensive_*.json`: Clip analysis
- `data/results/`: Final videos. Source for frontend "Download" button.
- `temp/`: Scratch space. Cleared after successful runs.

---

## 🎯 Key Concepts

### **V6.0 Deep Semantic Analysis**
The system doesn't just see "High Energy" - it understands:
- **Why** the edit is High Energy (e.g., "Peak action moment")
- **What** is happening (e.g., "Person jumping off cliff")
- **Where** it fits in the story (e.g., "Peak of the arc")

### **Editing Grammar**
The editor doesn't just match patterns - it thinks:
- "This clip was just used 3 seconds ago - too soon"
- "Last clip was Dynamic, this one is too - smooth flow"
- "This is an Intro segment, need an establishing shot"
- "This clip has been used 5 times already - find variety"

### **Mute and Analyze**
Copyright music doesn't block analysis because:
- Visual analysis happens on muted copy
- Original audio preserved for BPM detection
- Final render uses original soundtrack

---

**Last Updated:** January 22, 2026, 11:30 PM PKT
**Cache Versions:** Reference v6.1, Clips v6.1
**Status:** Production-ready, full pipeline validated with 3 reference videos


---

## 🚀 The Pipeline (Step-by-Step)

### 1. Pre-Analysis & Caching
- **Visual Scene Detection:** FFmpeg detects physical cuts in the reference video first. These timestamps are used as "ground truth" for the AI.
- **Reference Video:** Gemini 3 analyzes the reference using scene timestamps as anchors. It returns a compact string of codes (`HD, MS, LS`). Reconstructs segments by splitting the video at exactly those detected scene points. Result is cached in `ref_{hash}_hints{N}.json`.
- **User Clips:** Every clip is analyzed *once* comprehensively. Gemini extracts:
  - Overall Energy/Motion.
  - Three "Best Moments" (Low, Medium, High energy windows).
  - This is cached in `data/cache/clip_comprehensive_{hash}.json`.

### 2. Matching Algorithm (The "Rapid Cuts" Logic)
The `editor.py:match_clips_to_blueprint` function now works as follows:
- **Rhythmic Anchors:** Reference segments are treated as anchors.
- **Rapid Cuts:** For EACH segment, the editor doesn't just pick one clip. It creates **multiple cuts** (0.2s - 1.5s) to match the pacing.
- **Variety:** It avoids using the same clip twice in a row and rotates through the least-used clips.
- **Best Moments:** For every cut, it pulls from the pre-analyzed "Best Moment" window for that energy level.

### 3. Rendering (Frame-Perfect)
- **Standardization:** All clips are converted to a consistent format (1080x1920, 30fps) to prevent FFmpeg failures during concatenation.
- **Precision Cuts:** FFmpeg uses `-ss` (start) and `-t` (duration) on re-encoded streams. This ensures the cut is *exactly* where Gemini suggested, avoiding keyframe "snapping" issues.
- **Audio Preservation:** The original audio from the reference video is extracted and merged with the final edit, ensuring the rhythm matches the music/sound perfectly.

---

## 🛠️ Developer Commands & Testing

### Running the End-to-End Test
Use `test_real_pipeline.py` to verify the backend without a frontend interaction.
```bash
python test_real_pipeline.py
```
This script:
1. Picks a reference from `data/samples/reference/`.
2. Picks clips from `data/samples/clips/`.
3. Runs the full pipeline.
4. Reports on duration accuracy and clip usage.

### Mocking the Brain (API Key Saver)
If you want to test FFmpeg/Rendering without burning Gemini quota:
1. Open `backend/engine/brain.py`.
2. You can enable mock mode manually or by calling `set_mock_mode(True)` in your script.
3. This will generate synthetic analysis data instantly.

---

## 📁 Directory Roles
- `data/uploads/`: Original files. NEVER modified.
- `data/cache/`: AI Analysis results. SAFE to delete (will trigger re-analysis).
- `data/results/`: Final videos. The source for the frontend "Download" button.
- `temp/`: Scratch space. Cleared after successful runs (usually).
