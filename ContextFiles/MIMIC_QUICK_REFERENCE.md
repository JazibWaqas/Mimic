# 🧭 MIMIC - QUICK RECOVERY REFERENCE (V7.1)

**Use this when:** Code breaks, you're stuck, or need to understand the "why" behind a decision.

---

## 🎯 THE CORE IDEA (30 Seconds)

**What:** An AI agent that watches a viral video, extracts its editing structure (timing/pacing/energy), then applies that structure to user clips.

**The Loop:**
1. **Advisor (Plan):** Audits library and sets strategic weights.
2. **Editor (Execute):** Frame-perfect, beat-synced cuts matching the reference blueprint.
3. **Vault (Review):** Visualizing the AI reasoning behind every cut.

---

## 🏆 HACKATHON ALIGNMENT

### Category: 🎨 Creative Autopilot

**Why It Wins:**
- **Spatial-Temporal Reasoning:** Gemini doesn't just see objects; it understands the *timing* and *pacing* of a scene.
- **Precision Engineering:** Combined with FFmpeg for professional-grade results.
- **Explainable AI:** The Vault makes the "Black Box" of AI video editing transparent.

---

## 🔧 THE CRITICAL PATH

### 1. Gemini Analysis
**Must:** Return a valid `StyleBlueprint` with segments.
**Test:** `python test_ref.py` (Verify Stage 2 & 4).

### 2. FFmpeg Rendering
**Must:** Extract segments without drift.
**Fix:** Always re-encode (`-c:v libx264`).

---

## 🚨 COMMON FAILURES

### "API Key Exhausted"
**Fix:** The system uses a rotation carousel of 28 keys. If all fail, check your `.env` formatting.

### "Timeline Gaps"
**Fix:** The system enforces strict mathematical boundaries between segments in `editor.py`.

---

**Next Milestone:** Stage 6 Reflection (The AI Post-Audit).
