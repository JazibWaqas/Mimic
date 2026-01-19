# 🌊 MIMIC - Current Development Flow

This document details the exact sequence of logic implemented in the MIMIC pipeline as of **January 19, 2026 - 21:55 PM**.

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
