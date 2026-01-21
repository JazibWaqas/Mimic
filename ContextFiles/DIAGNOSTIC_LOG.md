# MIMIC Diagnostic Log - Bug Forensics

**Purpose:** Complete forensic record of all bugs discovered, root causes, and fixes applied.  
**Last Updated:** January 19, 2026, 23:32 PKT

---

## 🐛 Bug #1: BPM Drift (Hardcoded Tempo)

**Discovered:** January 15, 2026  
**Severity:** Medium  
**Status:** ✅ FIXED

### Symptoms:
- Cuts didn't align with audio beats
- Noticeable drift by end of video
- All videos assumed 120 BPM regardless of actual tempo

### Root Cause:
```python
# OLD CODE (editor.py)
BPM = 120.0  # Hardcoded!
beat_grid = generate_beat_grid(duration, BPM)
```

### Fix Applied:
1. Added `detect_bpm()` function using librosa
2. Extract audio in orchestrator Step 2
3. Pass detected BPM to editor
4. Generate beat grid with actual tempo

**Files Modified:**
- `backend/engine/processors.py` - Added `detect_bpm()` and `extract_audio()`
- `backend/engine/orchestrator.py` - Integrated BPM detection
- `backend/engine/editor.py` - Accept `bpm` parameter

**Verification:**
```python
# Test BPM detection
bpm = detect_bpm("ref4_audio.wav")
assert 125 < bpm < 135  # ref4 is ~129 BPM
```

---

## 🐛 Bug #2: Model Not Reinitializing After Key Rotation

**Discovered:** January 19, 2026, 22:50 PKT  
**Severity:** CRITICAL  
**Status:** ✅ FIXED

### Symptoms:
- API key rotation happened (logs showed rotation)
- But requests still used old key
- Got 429 errors even after rotation
- Only Key 1 was actually used

### Root Cause:
```python
# brain.py - Line 1017
if _handle_rate_limit_error(e, "comprehensive clip analysis"):
    # Key rotated, retry immediately
    continue  # ❌ Model object still uses old key!
```

The `model` object was created with the old key and never refreshed. After rotation, `genai.configure()` was called, but the existing `model` instance was still bound to the old key.

### Fix Applied:
```python
if _handle_rate_limit_error(e, "comprehensive clip analysis"):
    # Key rotated, REINITIALIZE MODEL
    model = initialize_gemini()  # ✅ Creates new model with new key
    continue
```

**Files Modified:**
- `backend/engine/brain.py` - Lines 1018, 1087 (two retry loops)

**Verification:**
- Logs now show successful requests after rotation
- Multiple keys used in sequence
- No repeated 429 errors on same operation

---

## 🐛 Bug #3: Upload/Analysis Key Mismatch (403 Errors)

**Discovered:** January 19, 2026, 23:05 PKT  
**Severity:** CRITICAL  
**Status:** ✅ FIXED

### Symptoms:
```
Uploading clip12.mp4... (attempt 1)
Upload complete: File ID xyz123
Requesting analysis (attempt 1)... 429 Rate Limit
[QUOTA] Rotated to new API key
Requesting analysis (attempt 2)... 403 Permission Denied
Error: You do not have permission to access File xyz123
```

### Root Cause:
**Gemini files are scoped to the API key that uploaded them.**

```python
# OLD FLOW (BROKEN):
video_file = _upload_video_with_retry(clip_path)  # Uploads with Key A
for attempt in range(3):
    # Attempt 1: Analyze with Key A → 429 error
    # Rotate to Key B
    # Attempt 2: Analyze File(uploaded_by=KeyA) with Key B → 403 error ❌
```

The upload happened ONCE before the retry loop. When we rotated keys mid-retry, the new key couldn't access the file uploaded by the old key.

### Fix Applied:
**Move upload INSIDE the retry loop:**

```python
# NEW FLOW (FIXED):
for attempt in range(3):
    video_file = _upload_video_with_retry(clip_path)  # ✅ Re-upload with current key
    response = model.generate_content([video_file, prompt])
    # If 429 → rotate → next iteration uploads with new key
```

**Files Modified:**
- `backend/engine/brain.py` - Lines 943, 1065 (moved upload into loop)

**Verification:**
- No more 403 errors after rotation
- Logs show re-upload after each rotation
- Different File IDs for each attempt

---

## 🐛 Bug #4: Upload Function Had Conflicting Rotation Logic

**Discovered:** January 19, 2026, 23:15 PKT  
**Severity:** HIGH  
**Status:** ✅ FIXED

### Symptoms:
- Upload function had its own retry loop
- Upload function also handled rate limits and rotated keys
- Created race condition with outer retry loop

### Root Cause:
```python
# OLD: _upload_video_with_retry() (BROKEN)
def _upload_video_with_retry(video_path):
    for attempt in range(3):
        try:
            video_file = genai.upload_file(path=video_path)
            return video_file
        except RateLimitError:
            rotate_api_key()  # ❌ Conflicts with outer loop's rotation!
            continue
```

**The problem:**
- Outer loop: Upload → Analyze → Rotate on error
- Inner loop: Upload → Rotate on error
- Both loops rotating = unpredictable key state

### Fix Applied:
**Remove retry/rotation from upload function:**

```python
# NEW: _upload_video_with_retry() (FIXED)
def _upload_video_with_retry(video_path):
    # Single upload attempt - caller handles retry
    video_file = genai.upload_file(path=video_path)
    # Wait for processing
    while video_file.state.name == "PROCESSING":
        time.sleep(10)
        video_file = genai.get_file(video_file.name)
    return video_file
```

Now the outer loop controls ALL retry logic and key rotation.

**Files Modified:**
- `backend/engine/brain.py` - Lines 406-434 (simplified upload function)

**Verification:**
- Only one rotation message per actual rotation
- Predictable key state
- Upload and analysis use same key

---

## 🐛 Bug #5: Rate Limiter Too Aggressive

**Discovered:** January 19, 2026, 23:00 PKT  
**Severity:** MEDIUM  
**Status:** ✅ FIXED

### Symptoms:
- Artificial delays even when quota available
- Limited to 14 requests/minute across ALL keys
- With 11 keys, should have 165 RPM capacity

### Root Cause:
```python
# brain.py
rate_limiter = RateLimiter(max_requests_per_minute=14)
# This throttled ALL requests, not per-key
```

**The problem:**
- Gemini enforces its own rate limits (15 RPM per key)
- Our rate limiter was redundant
- Worse, it throttled across all keys (should be per-key)
- Slowed down processing unnecessarily

### Fix Applied:
```python
# Disable rate limiter - let Gemini enforce its own limits
rate_limiter = RateLimiter()
rate_limiter.disable()  # ✅ No artificial throttling
```

**Rationale:**
- Gemini returns 429 errors when limits hit
- We have key rotation to handle 429s
- No need for pre-emptive throttling
- Faster processing

**Files Modified:**
- `backend/engine/brain.py` - Lines 296-298

**Verification:**
- No more "Waiting Xs to avoid quota" messages
- Requests go out immediately
- Faster overall processing

---

## 🐛 Bug #6: Defaults Poisoning Cache

**Discovered:** January 19, 2026, 23:08 PKT  
**Severity:** CRITICAL  
**Status:** ✅ FIXED

### Symptoms:
- Some clips showed "Using default: Medium/Dynamic"
- These defaults were being cached
- Once cached, clip was permanently "Medium/Dynamic" even if real analysis would differ

### Root Cause:
```python
# OLD CODE (brain.py - analyze_all_clips)
try:
    clip_metadata = _analyze_single_clip_comprehensive(model, clip_path, duration)
except Exception as e:
    print("Using default: Medium/Dynamic")
    clip_metadata = ClipMetadata(
        energy=EnergyLevel.MEDIUM,
        motion=MotionType.DYNAMIC
    )  # ❌ This gets added to the list and could be cached elsewhere!

clip_metadata_list.append(clip_metadata)  # Adds default to results
```

**The problem:**
- If analysis failed, we created a default ClipMetadata
- This default was returned to the orchestrator
- Orchestrator might cache it or use it in matching
- Future runs would use the bad data

### Fix Applied:
```python
# NEW CODE (FIXED)
try:
    clip_metadata = _analyze_single_clip_comprehensive(model, clip_path, duration)
except Exception as e:
    print(f"[ERROR] Analysis failed for {clip_path}: {e}")
    # DO NOT use defaults - this would poison the cache
    raise Exception(f"Failed to analyze {clip_path}: {e}")  # ✅ Fail hard
```

**Rationale:**
- Better to fail loudly than silently use bad data
- Orchestrator has its own fallback for total failure
- Individual clip failures should propagate up
- Never cache garbage data

**Files Modified:**
- `backend/engine/brain.py` - Lines 863-867

**Verification:**
- No more "Using default" messages in logs
- Failures propagate to orchestrator
- Cache only contains real analysis

---

## 🐛 Bug #7: Vibes Not Being Parsed or Saved

**Discovered:** January 19, 2026, 23:27 PKT  
**Severity:** CRITICAL  
**Status:** ✅ FIXED

### Symptoms:
- Prompt asked Gemini for vibes and content_description
- Gemini likely returned them
- But cache files had `vibes: null` and `content_description: null`
- Semantic matching couldn't work without vibes

### Root Cause:
```python
# OLD CODE (brain.py - _analyze_single_clip_comprehensive)
json_data = _parse_json_response(response.text)
energy = EnergyLevel(json_data["energy"])
motion = MotionType(json_data["motion"])
# ❌ Never extracted vibes or content_description!

cache_data = {
    "energy": energy.value,
    "motion": motion.value,
    # ❌ vibes and content_description not included!
}

return ClipMetadata(
    energy=energy,
    motion=motion,
    # ❌ vibes not passed to model!
)
```

**The problem:**
- We updated the prompt to request vibes
- We updated the data models to include vibes
- But we forgot to actually PARSE and SAVE the vibes from Gemini's response

### Fix Applied:
```python
# NEW CODE (FIXED)
json_data = _parse_json_response(response.text)
energy = EnergyLevel(json_data["energy"])
motion = MotionType(json_data["motion"])
vibes = json_data.get("vibes", [])  # ✅ Extract vibes
content_description = json_data.get("content_description", "")  # ✅ Extract content

cache_data = {
    "energy": energy.value,
    "motion": motion.value,
    "vibes": vibes,  # ✅ Save to cache
    "content_description": content_description,  # ✅ Save to cache
    ...
}

return ClipMetadata(
    energy=energy,
    motion=motion,
    vibes=vibes,  # ✅ Include in model
    ...
)
```

**Files Modified:**
- `backend/engine/brain.py` - Lines 939-942, 977-978, 995

**Verification:**
```powershell
# Check cache has vibes
Get-Content data/cache/clip_comprehensive_*.json | ConvertFrom-Json | Select vibes
# Should show: ["Urban", "Action", "Nightlife"]
```

---

## 📊 Bug Summary Statistics

| Bug | Severity | Discovery Date | Fix Date | Impact |
|-----|----------|----------------|----------|--------|
| #1 BPM Drift | Medium | Jan 15 | Jan 15 | Audio sync off |
| #2 Model Not Reinit | Critical | Jan 19 | Jan 19 | Keys not rotating |
| #3 Upload/Analysis Mismatch | Critical | Jan 19 | Jan 19 | 403 errors |
| #4 Upload Rotation Conflict | High | Jan 19 | Jan 19 | Unpredictable state |
| #5 Rate Limiter Aggressive | Medium | Jan 19 | Jan 19 | Slow processing |
| #6 Defaults Poisoning | Critical | Jan 19 | Jan 19 | Bad cache data |
| #7 Vibes Not Saved | Critical | Jan 19 | Jan 19 | Semantic matching broken |

**Total Bugs Fixed:** 7
**Critical Bugs:** 4
**All Fixes Verified:** ✅

---

## 🐛 Bug #8: Moment vs Segment Primitive Mismatch (ARCHITECTURAL)

**Discovered:** January 20, 2026, 10:00 AM
**Severity:** CRITICAL (Architecture Breaking)
**Status:** ❌ ACTIVE BLOCKER

### Symptoms:
- Timeline validation errors: "Value error, Timeline gap/overlap between decisions"
- FFmpeg concat failures with corrupt output
- Segments not filling completely, leaving gaps

### Root Cause:
**Fundamental primitive mismatch:**
- **Reference segments:** Fixed-duration holes (e.g., exactly 1.2s)
- **Clip moments:** Variable-duration pieces (e.g., 0.5s or 4.0s from Gemini)

The matching algorithm lets clip duration dictate segment length instead of forcing clips to fit reference segments.

### Impact:
- **Cannot render videos** - FFmpeg expects continuous timeline
- **Demo blocker** - No working output possible
- **Systemic issue** - Architecture assumes compatible primitives

### Required Fix:
**Change Gemini prompt:** Instead of "best moments that fit", ask for "start points", then code forces exact duration extraction.

---

## 🐛 Bug #9: Float Precision Timeline Gaps (MATHEMATICAL)

**Discovered:** January 20, 2026, 10:15 AM
**Severity:** CRITICAL (Accumulating Errors)
**Status:** ❌ ACTIVE BLOCKER

### Symptoms:
- Micro-gaps in timeline (0.000001s differences)
- FFmpeg strict validation catches tiny discontinuities
- Inconsistent render failures across runs

### Root Cause:
**Using Python floats for video timestamps:**
- `0.1 + 0.2 ≠ 0.3` in binary representation
- Over 20 segments/clips, errors accumulate
- No explicit boundary enforcement: `segment_N.end == segment_N+1.start`

### Impact:
- **Invisible but deadly** - Errors too small to see but break FFmpeg
- **Non-deterministic** - Same inputs produce different gaps
- **Hackathon killer** - Could fail live during demo

### Required Fix:
**Boundary enforcement:** Force `timeline_start` of decision N+1 = `timeline_end` of decision N, regardless of float precision.

---

## 🐛 Bug #10: Cache Poisoning with Defaults (DATA INTEGRITY)

**Discovered:** January 20, 2026, 10:30 AM
**Severity:** CRITICAL (Permanent Corruption)
**Status:** ❌ ACTIVE BLOCKER

### Symptoms:
- Clips showing "Medium/Dynamic" defaults in cache
- `vibes: null`, `content_description: null` in JSON files
- Matching uses garbage data permanently

### Root Cause:
**Caching partial failures as truth:**
- System caches ANY successful Gemini response, even with defaults
- Failed analyses insert fallback data that gets saved
- No "failed result" detection - defaults are treated as valid

### Impact:
- **Permanent poisoning** - Bad data survives cache clears
- **Hidden failures** - System appears to work but uses fake data
- **Development blocker** - Can't trust test results

### Required Fix:
**Sanitation policy:** Flag responses with defaults/nulls as "stale", never cache them. Fail loudly instead of silently defaulting.

---

**Updated Bug Summary Statistics**

| Bug | Severity | Discovery Date | Status | Impact |
|-----|----------|----------------|--------|--------|
| #1 BPM Drift | Medium | Jan 15 | ✅ FIXED | Audio sync off |
| #2 Model Not Reinit | Critical | Jan 19 | ✅ FIXED | Keys not rotating |
| #3 Upload/Analysis Mismatch | Critical | Jan 19 | ✅ FIXED | 403 errors |
| #4 Upload Rotation Conflict | High | Jan 19 | ✅ FIXED | Unpredictable state |
| #5 Rate Limiter Aggressive | Medium | Jan 19 | ✅ FIXED | Slow processing |
| #6 Defaults Poisoning | Critical | Jan 19 | ✅ FIXED | Bad cache data |
| #7 Vibes Not Saved | Critical | Jan 19 | ✅ FIXED | Semantic matching broken |
| #8 Moment vs Segment Mismatch | Critical | Jan 20 | ❌ DIAGNOSED | Timeline gaps |
| #9 Float Precision Gaps | Critical | Jan 20 | ❌ DIAGNOSED | Accumulating errors |
| #10 Cache Poisoning Defaults | Critical | Jan 20 | ❌ DIAGNOSED | Data corruption |

**Total Bugs Discovered:** 10
**Bugs Fixed:** 7 (original API bugs)
**Critical Architectural Issues:** 3 (DIAGNOSED, NOT FIXED)
**Active Blockers:** 3

---

## 🔍 Updated Debugging Methodology

### **New Lessons from Deep Architecture Analysis:**

1. **Primitives matter more than features** - Matching incompatible data types breaks everything
2. **Float math kills video editing** - Precision errors are invisible but fatal for timelines
3. **Cache integrity is existential** - Bad data permanence is worse than API failures
4. **Demo-safe means mathematically sound** - No amount of cheating fixes broken math
5. **Fail fast on contracts** - Don't let invalid data propagate through the pipeline

---

## 🚨 Current Known Issues (UPDATED)

### **CRITICAL ARCHITECTURAL BLOCKERS (3 Active - DIAGNOSED BUT NOT FIXED)**

#### **1. Timeline Primitive Mismatch**
**Status:** ❌ BLOCKING - Videos cannot render due to gaps
**Root:** Gemini moments ≠ Reference segments (incompatible durations)
**Impact:** FFmpeg concat fails on discontinuous timeline
**Fix Required:** Implement force-snap duration logic in editor.py

#### **2. Float Precision Accumulation**
**Status:** ❌ BLOCKING - Micro-gaps cause validation failures
**Root:** Python floats accumulate precision errors over 20+ operations
**Impact:** Invisible gaps that break strict FFmpeg requirements
**Fix Required:** Boundary enforcement in EditDecision creation

#### **3. Cache Default Poisoning**
**Status:** ❌ BLOCKING - Permanent bad data in cache
**Root:** System caches fallback defaults as truth
**Impact:** Matching uses fake "Medium/Dynamic" data forever
**Fix Required:** Sanitation policy - reject defaults, fail loudly

---

**Next Session Action:** Implement the 3 architectural fixes, then test integration.
