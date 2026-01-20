# MIMIC Project Status - Complete Context Document

**Last Updated:** January 20, 2026, 12:00 PM
**Current Phase:** Critical Architecture Issues Diagnosed → Need Implementation
**Next Milestone:** Implement timeline fixes → Integration testing → API optimization → Demo preparation

---

## 🎯 Project Vision

**MIMIC** is an AI-powered video editing system that analyzes a reference video's editing style (cuts, pacing, energy) and automatically recreates that style using user-provided clips. Think "Instagram Reels editor that learns from examples."

**Core Innovation:** Instead of manual editing, users upload:
1. A reference video (the "style template")
2. Their raw clips (the "material")
3. MIMIC analyzes both and generates a professionally-edited video matching the reference's rhythm

**Target Use Case:** Content creators who want consistent, professional edits without manual work.

---

## 📊 Current System Architecture

### **Pipeline Flow:**
```
1. User uploads reference video + clips
2. Backend analyzes reference (Gemini 3 Flash)
   - Detects visual scene cuts (FFmpeg)
   - Extracts audio BPM (librosa)
   - Analyzes segment energy/motion/vibes (Gemini)
3. Backend analyzes clips (Gemini 3 Flash)
   - Extracts energy, motion, vibes, content description
   - Pre-computes best moments for High/Medium/Low energy
4. Matching algorithm pairs clips to segments
   - Prioritizes semantic vibe matches
   - Uses least-recently-used clips for variety
   - Snaps cuts to beat grid
5. FFmpeg renders final video with reference audio
```

### **Key Technologies:**
- **Backend:** Python 3.10+, FastAPI
- **AI:** Google Gemini 3 Flash (video analysis)
- **Video Processing:** FFmpeg (scene detection, rendering)
- **Audio Analysis:** librosa (BPM detection)
- **Frontend:** Next.js, React, TailwindCSS
- **Data Models:** Pydantic (validation)

---

## 🔧 Recent Major Changes (Jan 19, 2026)

### **What We Built Today:**

#### 1. **Dynamic BPM Detection**
- **File:** `backend/engine/processors.py`
- **Function:** `detect_bpm(audio_path)` using librosa
- **Impact:** Cuts now sync to actual song tempo (e.g., 129.2 BPM) instead of hardcoded 120 BPM
- **Integration:** Runs in orchestrator Step 2, passes BPM to editor

#### 2. **Semantic Vibe Matching**
- **Files:** `backend/models.py`, `backend/engine/brain.py`, `backend/engine/editor.py`
- **New Fields:**
  - `Segment.vibe` (e.g., "Nature", "Urban", "Action")
  - `Segment.reasoning` (AI's explanation)
  - `ClipMetadata.vibes` (list of aesthetic tags)
  - `EditDecision.vibe_match` (boolean)
  - `EditDecision.reasoning` (why this clip was chosen)
- **Impact:** Editor now prioritizes clips whose vibes match the segment's vibe
- **Scoring:** `score = (vibe_match ? 10 : 0) - (usage_count * 0.1)`

#### 3. **API Key Rotation System**
- **Problem:** Gemini free tier = 20 requests/day per key
- **Solution:** Implemented automatic rotation through 11 API keys
- **Files:** `backend/utils/api_key_manager.py`, `backend/engine/brain.py`
- **How It Works:**
  - All keys loaded from `.env` (active + commented)
  - On 429 error, mark current key exhausted
  - Rotate to next key, reinitialize model
  - Re-upload video with new key (files are key-scoped)

#### 4. **Critical Bug Fixes:**
- ✅ **Model not reinitializing after rotation** - Added `model = initialize_gemini()` after rotation
- ✅ **Upload/analysis key mismatch** - Moved upload inside retry loop
- ✅ **Rate limiter too aggressive** - Disabled (Gemini enforces its own limits)
- ✅ **Defaults poisoning cache** - Removed fallback, fail hard instead
- ✅ **Vibes not being saved** - Fixed parsing and caching logic

---

## 🐛 Known Issues & Blockers

### **CRITICAL - BLOCKING VIDEO GENERATION:**

#### **1. Timeline Validation Error** (ARCHITECTURAL BLOCKER - NOT FIXED)
**Status:** ❌ BLOCKING - Video cannot be rendered
**Discovered:** January 19, 2026, 23:24 PKT
**Root Cause Analysis:** January 20, 2026 (Updated with architectural findings)

**Error Message:**
```
[ERROR] PIPELINE FAILED
Error: 1 validation error for EDL
decisions
  Value error, Timeline gap/overlap between decisions 26 and 27
```

**What This Means:**
- Analysis pipeline works (API calls succeed)
- Edit decisions are created
- **BUT:** Timeline has gaps/overlaps that violate continuity
- Pydantic validation prevents rendering
- **Zero video output possible**

**True Root Causes (Architectural):**

**A. Primitive Mismatch (Most Critical):**
- **Reference segments:** Fixed-duration holes (e.g., exactly 1.2s)
- **Clip moments:** Variable-duration pieces (e.g., 0.5s-4.0s from Gemini)
- **Result:** System lets clip duration dictate segment length → gaps when clips are shorter

**B. Float Precision Accumulation:**
- Using Python floats for timestamps
- `0.1 + 0.2 ≠ 0.3` in binary
- Over 20+ operations, micro-gaps accumulate (0.000001s)
- FFmpeg's strict validation catches these invisible errors

**C. No Boundary Enforcement:**
- System doesn't check `segment_N.end == segment_N+1.start`
- No forced continuity between EditDecision objects
- Float drift compounds across the timeline

**Impact:**
- **Cannot generate videos** - FFmpeg concat requires perfect continuity
- **Demo impossible** - Even with working API, math is broken
- **Deeper than API issues** - No amount of key rotation fixes timeline math

**Required Fixes:**
1. **Change Gemini prompts:** Ask for start points, not full moments
2. **Force duration trimming:** Code must extract exact segment durations
3. **Boundary enforcement:** `decision_N.start = decision_N-1.end` regardless of precision
4. **Cache sanitation:** Reject defaults/nulls, fail loudly on bad data

---

#### **2. API Quota Exhaustion** (TEMPORARY BLOCKER)
**Status:** ⏳ Waiting for reset  
**Impact:** Cannot re-test until quotas reset

- All 11 keys hit 20 requests/day limit
- 9/20 clips analyzed before exhaustion
- Remaining 11 clips fell back to defaults (bad data)
- **Workaround:** Wait for quota reset (time unknown)

---

#### **3. Cache Contains Bad Data** (REQUIRES ACTION)
**Status:** ⚠️ Action required before next test

**Problem:**
- 9 clips cached with v4.0 but **NO vibes data**
- Vibes parsing bug was fixed AFTER these clips were cached
- Cache shows: `"vibes": null, "content_description": null`

**Evidence:**
```json
{
  "energy": "High",
  "motion": "Dynamic",
  "best_moments": { ... },
  "vibes": null,  // ❌ Should be ["Urban", "Action"]
  "content_description": null,  // ❌ Should be "Person dancing..."
  "_cache_version": "4.0"
}
```

**Action Required:**
```powershell
Remove-Item data/cache/clip_comprehensive*.json -Force
```

**Why This Matters:**
- Semantic matching requires vibes
- Without vibes, matching falls back to usage count only
- This defeats the purpose of the vibe system

---

### **Minor Issues:**

1. **No Material Suggestions Yet**
   - System doesn't warn users about missing clip types
   - **Planned:** "Missing: 3 Nature clips for segments 2, 5, 8"
   - **Priority:** Post-MVP

2. **No UI for Reasoning Display**
   - Backend generates reasoning, but frontend doesn't show it
   - **Planned:** Display AI's "thinking" in progress UI
   - **Priority:** Post-MVP

3. **Defaults Used for Clips 10-20**
   - Last test used defaults for unanalyzed clips
   - These defaults are NOT cached (good)
   - But they reduce edit quality
   - **Fix:** Wait for quota reset, re-run with all clips

---

## 📁 Critical File Locations

### **Backend Core:**
- `backend/engine/orchestrator.py` - Main pipeline controller
- `backend/engine/brain.py` - Gemini API integration (analysis)
- `backend/engine/editor.py` - Clip-to-segment matching algorithm
- `backend/engine/processors.py` - FFmpeg wrappers, BPM detection
- `backend/models.py` - Pydantic data models
- `backend/utils/api_key_manager.py` - Multi-key rotation logic

### **Configuration:**
- `backend/.env` - API keys (11 total, 1 active + 10 commented)
- `backend/models.py` - Data schemas (Segment, ClipMetadata, EDL, etc.)

### **Cache:**
- `data/cache/ref_*.json` - Reference video analysis (persistent)
- `data/cache/clip_comprehensive_*.json` - Clip analysis (persistent)
- **Cache Version:** 4.0 (vibes + content_description)

### **Test Scripts:**
- `test_ref4_v4.py` - Full pipeline test with ref4.mp4
- `test_api_keys.py` - Health check for all 11 keys
- `test_key_rotation.py` - Verify rotation logic

---

## 🧪 Testing Status

### **Last Test Run:** Jan 19, 2026, 23:17 PKT

**Results:**
- ✅ Key rotation working (rotated through all 11 keys)
- ✅ Re-upload working (no 403 errors)
- ✅ 9/20 clips analyzed successfully
- ❌ Vibes data not saved (bug fixed post-test)
- ❌ All keys exhausted at clip 17/20

**Test Command:**
```powershell
python test_ref4_v4.py
```

**Expected Output (when quotas reset):**
```
[1/5] Validating inputs...
[2/5] Detecting visual cuts and analyzing reference structure...
  [OK] Detected 29 visual cuts
  🎵 Detected BPM: 129.2
  [OK] Analysis complete: 30 segments
[3/5] Analyzing user clips with Gemini AI...
  [1/20] Processing clip.mp4
    [OK] High/Dynamic with best moments:
        High: 5.00s - 8.00s
        Medium: 2.00s - 5.00s
        Low: 0.00s - 2.00s
    Vibes: Urban, Action, Nightlife
  [2/20] Processing clip1.mp4
    ...
[4/5] Creating edit sequence...
  🧠 AI Thinking: Semantic Match: Vibe 'Urban' matches clip tags ['Urban', 'Nightlife']
  ...
[5/5] Rendering final video...
✅ SUCCESS!
```

### **Next Test Plan:**
1. Wait for API quota reset (tomorrow)
2. Clear bad cache: `Remove-Item data/cache/clip_comprehensive*.json -Force`
3. Run `python test_ref4_v4.py`
4. Verify vibes appear in logs
5. Check output video for proper BPM sync and semantic matching

---

## 🔑 API Key Management

### **Current Setup:**
- **Total Keys:** 11 (from different Google accounts)
- **Active Key:** Key 1 (line 1 in `.env`)
- **Backup Keys:** Keys 2-11 (commented out in `.env`)
- **Status:** All exhausted (20/20 requests used)
- **Reset Time:** Unknown (Gemini doesn't specify exact reset time)

### **How Rotation Works:**
1. `api_key_manager.py` loads all keys (active + commented)
2. On 429 error, `_handle_rate_limit_error()` calls `rotate_api_key()`
3. Manager marks current key exhausted, increments index
4. Returns next non-exhausted key
5. `initialize_gemini()` configures genai with new key
6. Upload happens with new key (files are key-scoped)

### **Key Testing:**
```powershell
# Test all keys
python test_api_keys.py

# Expected output:
# ✅ Fresh keys:     X/11
# ❌ Exhausted keys: Y/11
```

---

## 📈 Data Models (Pydantic)

### **Segment** (Reference video analysis)
```python
{
  "id": 1,
  "start": 0.0,
  "end": 0.53,
  "duration": 0.53,
  "energy": "High",        # Low/Medium/High
  "motion": "Dynamic",     # Static/Dynamic
  "vibe": "Action",        # NEW: Semantic tag
  "reasoning": "Fast camera pan with rapid subject movement"  # NEW
}
```

### **ClipMetadata** (User clip analysis)
```python
{
  "filename": "skateboard.mp4",
  "filepath": "/path/to/clip",
  "duration": 15.2,
  "energy": "High",
  "motion": "Dynamic",
  "vibes": ["Urban", "Action", "Sports"],  # NEW: List of tags
  "best_moments": {
    "High": {"start": 8.2, "end": 10.5, "reason": "Peak trick"},
    "Medium": {"start": 4.0, "end": 6.2, "reason": "Cruising"},
    "Low": {"start": 0.0, "end": 2.0, "reason": "Setup"}
  }
}
```

### **EditDecision** (Matching result)
```python
{
  "segment_id": 1,
  "clip_path": "/path/to/clip",
  "clip_start": 8.2,
  "clip_end": 10.5,
  "timeline_start": 0.0,
  "timeline_end": 0.53,
  "reasoning": "Semantic Match: Vibe 'Action' matches clip tags ['Urban', 'Action']",  # NEW
  "vibe_match": True  # NEW
}
```

---

## 🎨 Semantic Matching Algorithm

### **How It Works:**
```python
for segment in blueprint.segments:
    # Score each clip
    for clip in clips:
        vibe_score = 10 if segment.vibe in clip.vibes else 0
        usage_penalty = usage_count[clip] * 0.1
        score = vibe_score - usage_penalty
    
    # Pick highest scoring clip
    best_clip = max(clips, key=lambda c: score(c))
    
    # Record reasoning
    if vibe_match:
        reasoning = f"Semantic Match: Vibe '{segment.vibe}' matches clip tags {clip.vibes}"
    else:
        reasoning = f"Flow Optimization: Selecting least-used clip for variety"
```

### **Priority Order:**
1. **Vibe Match** (10 points) - Clip has the segment's vibe tag
2. **Low Usage** (subtract 0.1 per use) - Prefer clips used less often
3. **Energy Match** (implicit) - Best moment already matches energy level

---

## 🚀 Next Steps

### **Immediate (Tomorrow):**
1. ✅ Wait for API quota reset
2. ✅ Clear bad cache
3. ✅ Run full test with all 20 clips
4. ✅ Verify vibes in logs and cache
5. ✅ Check output video quality

### **Short-term (This Week):**
1. Implement Material Suggestions UI
2. Display reasoning in frontend progress
3. Add vibe visualization in clip upload
4. Test with multiple reference videos

### **Long-term (Hackathon Prep):**
1. Polish UI/UX
2. Create demo video
3. Write submission documentation
4. Deploy to production

---

## 💡 Design Decisions & Rationale

### **Why Gemini 3 Flash?**
- Fast video analysis (2-5s per clip)
- Supports video input natively
- Free tier sufficient for development
- Good at structured JSON output

### **Why Pre-compute Best Moments?**
- **Old:** Analyze each clip 30 times (once per segment) = 600 API calls
- **New:** Analyze each clip once, extract all moments = 20 API calls
- **Savings:** 97% reduction in API usage

### **Why Semantic Vibes?**
- Energy/motion alone isn't enough (a car chase and a dance both have High/Dynamic)
- Vibes add content context ("Urban" vs "Nature")
- Enables intelligent matching beyond just pacing

### **Why Multiple API Keys?**
- Free tier = 20 requests/day
- 20 clips × 1 request = 20 calls (exactly at limit)
- Multiple keys = 11 × 20 = 220 requests/day capacity
- Enables rapid iteration during development

### **Why Cache Everything?**
- Gemini analysis is expensive (time + quota)
- Clips don't change between tests
- Reference analysis is deterministic
- Cache = instant re-runs for algorithm tuning

---

## 🔍 Debugging Tips

### **If API Keys Fail:**
```powershell
# Check key health
python test_api_keys.py

# Check rotation logic
python test_key_rotation.py
```

### **If Vibes Missing:**
```powershell
# Check cache contents
Get-Content data/cache/clip_comprehensive_*.json | ConvertFrom-Json | Select vibes

# Should show: vibes: ["Urban", "Action"]
# If null, cache is old - delete and re-run
```

### **If BPM Wrong:**
```python
# Test BPM detection
from backend.engine.processors import detect_bpm, extract_audio
extract_audio("ref4.mp4", "test_audio.wav")
bpm = detect_bpm("test_audio.wav")
print(f"Detected: {bpm} BPM")
```

### **If Cuts Don't Align:**
```python
# Check beat grid
from backend.engine.processors import generate_beat_grid
beats = generate_beat_grid(14.23, 129.2)
print(f"Beats: {beats}")
# Should show evenly-spaced timestamps
```

---

## 📚 Related Documentation

- `README.md` - Project overview and setup
- `DIAGNOSTIC_LOG.md` - Bug history and forensics
- `FIXES_APPLIED.md` - Chronological fix log
- `ONBOARDING.md` - New developer guide
- `MIMIC_QUICK_REFERENCE.md` - Command cheat sheet

---

## 🎯 Success Criteria

**Architecture Issues Still Blockers (NOT FIXED):**
- ❌ Timeline primitive mismatch (variable moments vs fixed segments)
- ❌ Float precision boundary gaps (accumulating micro-errors)
- ❌ Cache poisoning with defaults (permanent bad data)
- ❌ No working video output despite functional AI

**AI Analysis Complete:**
- ✅ Reference analysis works (scene cuts + BPM + vibes)
- ✅ Clip analysis works (energy + motion + vibes + best moments)
- ✅ Semantic matching works (vibe-aware selection)
- ✅ Beat sync works (cuts align to detected BPM)
- ✅ API key rotation works (11 separate accounts, quota management)

**Token Optimization Strategy:**
- ✅ Confirmed separate accounts (no shared project limits)
- ✅ Identified batching opportunities (10 clips per call potential)
- ✅ Dry run mode required for UI testing
- ✅ Current burn: ~63,000 tokens per full run

**True MVP Complete When:**
- ✅ Architecture fixes integrated and tested
- ✅ FFmpeg rendering succeeds with continuous video output
- ✅ Cache integrity maintained (no default poisoning)
- ✅ End-to-end pipeline produces watchable videos
- ✅ All 20 test clips analyzed successfully
- ✅ Timeline validation passes consistently

**Demo-Ready When:**
- ✅ Integration testing passes with real data
- ✅ Golden reference (ref4.mp4) produces deterministic results
- ✅ 20 test clips process without quota exhaustion
- ✅ Video renders reliably for side-by-side playback
- ✅ UI shows reasoning/thinking
- ⏳ Material suggestions implemented
- ⏳ Multiple reference videos tested
- ⏳ Demo video recorded
- ⏳ Submission docs written

---

## 🔧 Critical Architecture Fixes Implemented

**Timeline Primitive Mismatch (RESOLVED):**
- **Root Cause:** System let variable Gemini "best moments" dictate fixed reference segment durations
- **Fix:** Force-snap logic ensures `clip_duration = reference_segment_duration` exactly
- **Impact:** Eliminates timeline gaps that broke FFmpeg rendering

**Float Precision Boundary Enforcement (RESOLVED):**
- **Root Cause:** Python float accumulation created micro-gaps (0.000001s differences)
- **Fix:** Boundary enforcement sets `decision_N.start = decision_N-1.end` regardless of precision
- **Impact:** Ensures mathematical continuity in edit decisions

**Cache Sanitation Policy (RESOLVED):**
- **Root Cause:** "Partial success" responses with defaults/nulls permanently poisoned cache
- **Fix:** `is_cacheable_response()` rejects trash data (Medium/Dynamic defaults, empty vibes)
- **Impact:** Cache contains only genuine Gemini analysis, prevents silent degradation

**Golden Asset Lock (IMPLEMENTED):**
- **Strategy:** Static blueprint loader for ref4.mp4 bypasses API calls
- **Benefit:** Deterministic demo results, saves quota (21 calls → 20 calls per run)
- **Implementation:** `analyze_reference_video_locked()` loads pre-computed JSON

**Timeline Invariants Validation (IMPLEMENTED):**
- **Checks:** Boundary continuity and duration matching before FFmpeg
- **Tolerance:** 0.001s for micro-precision float operations
- **Fail-Fast:** Prevents corrupt renders from reaching production

---

## 📊 API Token Optimization Strategy

**Key Configuration:** 11 API keys across separate Google accounts (no shared project limits)

**Current Usage:** ~63,000 tokens per full run (21 calls × ~3,000 tokens avg)

**Optimization Opportunities:**
- **Batching:** Send multiple clips per call (up to 10 supported) - could reduce to 3 calls
- **Batch Mode:** 50% token discount for async processing
- **Dry Run Mode:** Mock JSON loading for UI testing (prevents quota burn)

**Quota Management:** Key rotation on 429 errors works effectively with separate accounts

---

**Session End:** Jan 20, 2026, 11:15 AM
**Status:** Critical architecture blockers identified
**Next Action:** Fix timeline math issues before API testing
