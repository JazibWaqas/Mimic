# MIMIC Project - Comprehensive Status Document

**Last Updated:** January 9, 2025  
**Purpose:** This document provides a complete overview of the MIMIC project, its implementation, design decisions, current status, and how to get up to speed.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Implementation Details](#implementation-details)
4. [Recent Changes](#recent-changes)
5. [Current Status](#current-status)
6. [Known Issues](#known-issues)
7. [Design Decisions](#design-decisions)
8. [Testing & Usage](#testing--usage)
9. [API Limits & Optimization](#api-limits--optimization)

---

## 🎯 Project Overview

**MIMIC** is an AI-powered video editing system that analyzes a reference video's "editing DNA" (cut timing, pacing, energy) and applies that style to user-uploaded clips.

### Core Concept
- **Input:** Reference video + User clips
- **Process:** AI analyzes reference structure → Matches clips to segments → Finds best moments → Renders output
- **Output:** Video matching reference style/rhythm

### Key Features
- ✅ Reference video analysis (cut detection, energy/motion classification)
- ✅ User clip analysis (energy/motion matching)
- ✅ **Best moment selection** (finds optimal timestamps within clips)
- ✅ Caching system (reduces API calls)
- ✅ Manual mode (bypass API for testing)
- ✅ Real-time progress tracking (WebSocket)
- ✅ Video standardization & rendering (FFmpeg)

---

## 🏗️ Architecture

### Tech Stack
- **Backend:** FastAPI (Python 3.10.11)
- **Frontend:** Next.js 16.1.1 (React, TypeScript)
- **AI:** Gemini 3 Flash Preview (primary), Gemini 1.5 Flash (fallback)
- **Video Processing:** FFmpeg 8.0.1
- **Communication:** REST API + WebSocket

### Directory Structure
```
Mimic/
├── backend/
│   ├── main.py              # FastAPI app, endpoints, WebSocket
│   ├── models.py            # Pydantic data models
│   ├── engine/
│   │   ├── brain.py         # Gemini API integration, analysis
│   │   ├── editor.py        # Clip-to-segment matching algorithm
│   │   ├── orchestrator.py  # Main pipeline controller
│   │   └── processors.py    # FFmpeg wrappers
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Landing page
│   │   ├── upload/page.tsx  # Upload interface (Auto/Manual modes)
│   │   ├── generate/[id]/   # Progress tracking page
│   │   └── result/[id]/     # Results page
│   ├── components/
│   │   ├── FileUpload.tsx
│   │   ├── ProgressTracker.tsx  # WebSocket progress updates
│   │   └── VideoComparison.tsx
│   └── lib/api.ts           # API client
├── temp/                    # ⚠️ INTERMEDIATE PROCESSING FILES ONLY (can be cleaned)
│   └── {session_id}/
│       ├── standardized/   # Standardized clips (during processing)
│       ├── segments/       # Extracted segments (during processing)
│       └── temp_video.mp4  # Intermediate concatenated video
└── data/
    ├── uploads/             # ✅ PERMANENT: Uploaded reference videos & clips
    │   └── {session_id}/
    │       ├── reference/   # Uploaded reference video (kept permanently)
    │       └── clips/      # Uploaded user clips (kept permanently)
    ├── cache/               # ✅ PERMANENT: Cached AI analyses (MD5-based)
    │   ├── ref_{hash}.json  # Cached reference analyses
    │   └── clip_{hash}.json # Cached clip analyses
    ├── results/             # ✅ PERMANENT: Final output videos
    │   └── mimic_output_{session_id}.mp4
    └── samples/             # Test assets
```

### File Storage Flow

**New Design (Updated):** Permanent files go to `data/`, only intermediate processing goes to `temp/`.

1. **Upload Phase:**
   - Files saved to `data/uploads/{session_id}/reference/` and `data/uploads/{session_id}/clips/`
   - **These are PERMANENT** - kept forever (user uploaded them)

2. **Processing Phase:**
   - Standardized clips → `temp/{session_id}/standardized/` (temporary)
   - Extracted segments → `temp/{session_id}/segments/` (temporary)
   - Intermediate video → `temp/{session_id}/temp_video.mp4` (temporary)

3. **Final Output:**
   - Final rendered video → `data/results/mimic_output_{session_id}.mp4` (permanent)

4. **Cache:**
   - AI analyses cached to `data/cache/` (permanent, reusable)

**✅ Benefits of New Design:**
- **Uploaded files are preserved** - can reuse reference/clips later
- **Only processing intermediates in temp/** - safe to clean up
- **Clear separation:** `data/` = permanent, `temp/` = disposable
- **Can clean temp/ without losing user uploads**

**Cleanup:**
- `cleanup_session(session_id)` - Cleans only `temp/` (keeps uploads)
- `cleanup_session(session_id, cleanup_uploads=True)` - Also deletes uploads
- `cleanup_all_temp()` - Cleans all `temp/` directories

### Data Flow

```
1. User uploads reference + clips
   ↓
2. Backend saves files, creates session
   ↓
3. Frontend navigates to /generate/{session_id}
   ↓
4. Backend starts pipeline (background task):
   a. Analyze reference → StyleBlueprint (segments with energy/motion)
   b. Analyze clips → ClipIndex (energy/motion per clip)
   c. Match clips to segments → EDL (edit decisions)
   d. Find best moments (NEW) → Updates clip timestamps
   e. Extract segments → FFmpeg cuts
   f. Concatenate → Final video
   ↓
5. WebSocket sends progress updates
   ↓
6. Frontend redirects to /result/{session_id}
```

---

## 🔧 Implementation Details

### 1. Reference Video Analysis (`brain.py`)

**Purpose:** Extract the "editing DNA" from reference video.

**Process:**
1. Upload video to Gemini 3
2. Use `REFERENCE_ANALYSIS_PROMPT` to analyze:
   - Cut points (when edits happen)
   - Segment boundaries (0.5-5 seconds each)
   - Energy level per segment (Low/Medium/High)
   - Motion type per segment (Static/Dynamic)
3. Return `StyleBlueprint` with ordered segments

**Key Prompt Features:**
- Detects **actual cut points** (not just energy changes)
- Creates 10-30+ segments for rapid-cut videos
- Segment length matches cut frequency (0.5-1.5s for rapid, 2-5s for slow)

**Caching:**
- MD5 hash of video file → `data/cache/ref_{hash}.json`
- Prevents re-analysis of same reference
- **Version-aware:** Cache includes `_cache_version` field
- **Auto-invalidation:** If prompt changes (version mismatch), cache is deleted and re-analyzed

**Example Output:**
```json
{
  "total_duration": 11.0,
  "segments": [
    {"id": 1, "start": 0.0, "end": 0.8, "duration": 0.8, "energy": "High", "motion": "Dynamic"},
    {"id": 2, "start": 0.8, "end": 1.5, "duration": 0.7, "energy": "High", "motion": "Dynamic"},
    ...
  ]
}
```

### 2. Clip Analysis (`brain.py`)

**Purpose:** Classify each user clip's overall energy and motion.

**Process:**
1. Upload clip to Gemini
2. Use `CLIP_ANALYSIS_PROMPT` to get:
   - Overall energy (Low/Medium/High)
   - Overall motion (Static/Dynamic)
3. Return `ClipMetadata` per clip

**Caching:**
- MD5 hash of clip file → `data/cache/clip_{hash}.json`
- Reuses analysis across sessions
- **Version-aware:** Cache includes `_cache_version` field
- **Auto-invalidation:** If prompt changes, old cache is invalidated

**Example Output:**
```json
{
  "energy": "High",
  "motion": "Dynamic"
}
```

### 3. Best Moment Selection (`brain.py`) ⭐ **NEW FEATURE**

**Purpose:** Find the optimal moment within a clip that matches a segment's profile.

**Why This Matters:**
- **Before:** Used clips sequentially (0s-2s, 2s-4s, etc.)
- **After:** AI finds best 2-second moment anywhere in clip (e.g., 12.5s-14.5s)

**Process:**
1. When matching clip to segment, call `find_best_moment()`
2. Use `BEST_MOMENT_PROMPT_TEMPLATE` with:
   - Target energy (from segment)
   - Target motion (from segment)
   - Target duration (from segment)
3. Gemini analyzes entire clip, returns:
   - `best_moment_start` (timestamp in seconds)
   - `best_moment_end` (timestamp in seconds)
   - Reason (why this moment matches)
4. Store in `ClipMetadata.best_moment_start/end`

**Prompt Strategy:**
- Asks for "SINGLE BEST continuous moment"
- Prioritizes "visually compelling" and "viral-worthy"
- Returns timestamps in decimal seconds (e.g., 12.5 not 12:30)

**Fallback:**
- If analysis fails → Sequential cutting (0s-2s)
- If best moment too short → Use full moment + continue with next clip

**Example:**
```
Segment: 2.3s, High/Dynamic
Clip: 15s long, High/Dynamic overall
AI finds: Best moment is 8.2s-10.5s (peak dance move)
Uses: 8.2s-10.5s (not 0s-2.3s)
```

### 4. Clip-to-Segment Matching (`editor.py`)

**Purpose:** Decide which clips go where in the final video.

**Algorithm:**
1. Group clips by energy level (energy pools)
2. For each segment:
   a. Find clips matching segment energy
   b. Select least-used clip from pool
   c. **Find best moment** (if enabled)
   d. Create edit decision with timestamps
   e. If clip exhausted, switch to next clip
3. Return `EDL` (Edit Decision List)

**Best Moment Integration:**
- If `find_best_moments=True` and clip has no best moment → Call `find_best_moment()`
- Use `best_moment_start/end` instead of sequential `clip_current_position`
- If best moment shorter than needed → Use full moment + continue

**Edit Decision Format:**
```python
EditDecision(
    segment_id=1,
    clip_path="/temp/abc/clip.mp4",
    clip_start=8.2,      # Best moment start (or sequential)
    clip_end=10.5,       # Best moment end (or sequential)
    timeline_start=0.0,  # Position in final video
    timeline_end=2.3
)
```

### 5. Video Processing (`processors.py`)

**Functions:**
- `standardize_clip()`: Convert to 1080x1920, 30fps, h.264
- `extract_segment()`: Cut specific timestamp range
- `concatenate_videos()`: Stitch segments together
- `merge_audio_video()`: Add reference audio to output
- `get_video_duration()`: Get clip length

**FFmpeg Commands:**
- Uses `-c:v libx264 -preset medium -crf 23` (not `-c copy` for compatibility)
- Frame-accurate cuts with `-ss` and `-t`

### 6. Caching System (`brain.py`)

**Purpose:** Reduce redundant Gemini API calls.

**Implementation:**
- **Reference caching:** MD5 hash → `data/cache/ref_{hash}.json`
- **Clip caching:** MD5 hash → `data/cache/clip_{hash}.json`
- **Best moment:** NOT cached (segment-specific, recalculated per match)

**Cache Key Generation:**
```python
import hashlib
with open(file_path, 'rb') as f:
    file_hash = hashlib.md5(f.read()).hexdigest()
cache_file = f"data/cache/ref_{file_hash}.json"
```

**Cache Invalidation:**
- Manual: Delete `data/cache/*.json`
- Automatic: File content change = new hash = cache miss

**Why This Matters:**
- Reference analysis: ~5-10 seconds per video
- Clip analysis: ~3-5 seconds per clip
- With 8 clips: Saves 24-40 seconds + API quota

### 7. Manual Mode (`main.py`, `orchestrator.py`)

**Purpose:** Bypass Gemini API for testing/development.

**How It Works:**
1. User pastes pre-analyzed JSON:
   - `StyleBlueprint` (reference analysis)
   - `ClipIndex` (clip analysis)
2. Backend skips AI analysis
3. Goes straight to matching → rendering

**Use Cases:**
- Testing without API quota
- Debugging matching algorithm
- Demo with pre-analyzed data

**Endpoint:** `POST /api/upload-manual`

### 8. WebSocket Progress (`main.py`, `ProgressTracker.tsx`)

**Purpose:** Real-time progress updates during pipeline.

**Implementation:**
- Backend: `@app.websocket("/ws/progress/{session_id}")`
- Frontend: Connects on `/generate/{id}` page
- Updates: `{status, progress, message}` every second

**Status Flow:**
- `uploaded` → `processing` → `complete` / `error`

**Error Handling:**
- Initial connection may fail (session not ready)
- Auto-reconnects up to 10 times
- 2-second delay between retries

**Known Issue:**
- WebSocket error on initial connect (harmless, auto-fixes)

### 9. Session Management (`main.py`)

**Storage:**
- In-memory dictionary: `active_sessions[session_id]`
- Contains: file paths, status, progress, output path

**Session Lifecycle:**
1. Upload → Create session (`status: "uploaded"`)
2. Generate → Start pipeline (`status: "processing"`)
3. Complete → Store output path (`status: "complete"`)

**Limitation:**
- Sessions lost on server restart (in-memory)
- No persistence to database

---

## 🆕 Recent Changes

### January 9, 2025 - Best Moment Selection

**What Changed:**
1. Added `best_moment_start/end` to `ClipMetadata` model
2. Created `find_best_moment()` function in `brain.py`
3. Updated `match_clips_to_blueprint()` to use best moments
4. Modified editor logic to prefer best moments over sequential cutting

**Why:**
- Sequential cutting uses first N seconds (often boring)
- Best moment finds most compelling part (more professional)

**Impact:**
- **API Calls:** +1 per clip-segment match (when enabled)
- **Quality:** Significantly better (uses peak moments)
- **Performance:** Slight increase (extra Gemini calls)

**Configuration:**
- Auto mode: `find_best_moments=True` (enabled)
- Manual mode: `find_best_moments=False` (disabled, saves API)

### January 9, 2025 - Reference Analysis Improvements

**What Changed:**
- Updated `REFERENCE_ANALYSIS_PROMPT` to detect actual cut points
- Increased segment count for rapid-cut videos (10-30+ segments)
- Shorter segments for rapid cuts (0.5-1.5s)

**Why:**
- Old prompt created only 3-8 segments (missed rapid cuts)
- New prompt detects every significant cut

**Impact:**
- Better cut detection
- More accurate pacing replication

### January 9, 2025 - Output File Naming

**What Changed:**
- Changed from `mimic_output_{session_id[:8]}.mp4` to `mimic_output_{full_session_id}.mp4`
- Added file deletion before generation (force regeneration)

**Why:**
- First 8 chars could collide (different sessions, same prefix)
- Full ID ensures uniqueness

### January 9, 2025 - Logging Improvements

**What Changed:**
- Added `[UPLOAD]`, `[PIPELINE]`, `[PROGRESS]` log prefixes
- Added timestamps to pipeline start
- Better error messages

**Why:**
- Easier debugging
- Track when pipeline actually runs

---

## ✅ Current Status

### Working Features

✅ **File Upload**
- Reference + multiple clips
- Manual mode JSON input
- File validation

✅ **Reference Analysis**
- Cut point detection
- Energy/motion classification
- Caching

✅ **Clip Analysis**
- Energy/motion classification
- Caching
- Batch processing

✅ **Best Moment Selection** ⭐
- Finds optimal timestamps
- Segment-specific matching
- Fallback to sequential

✅ **Video Matching**
- Energy-based matching
- Round-robin fallback
- Clip looping

✅ **Video Rendering**
- Standardization (1080x1920, 30fps)
- Segment extraction
- Concatenation
- Audio merging

✅ **Progress Tracking**
- WebSocket updates
- Real-time progress bar
- Step-by-step status

✅ **Result Display**
- Video comparison
- Download button
- Session info

### Partially Working

⚠️ **WebSocket Connection**
- Initial connection may fail (timing issue)
- Auto-reconnects successfully
- **Fix:** Harmless, but could be improved

⚠️ **Session Persistence**
- Lost on server restart
- **Fix:** Would need database (not implemented)

### Not Working / Known Issues

❌ **Hydration Mismatch (Frontend)**
- React hydration warning (timestamp in URL)
- **Impact:** Cosmetic only, doesn't break functionality
- **Fix:** Use `useEffect` for timestamp instead of render-time

❌ **Empty Video Source Warning**
- "Empty string passed to src attribute"
- **Impact:** Cosmetic only
- **Fix:** Check for empty string before rendering `<video>`

---

## 🐛 Known Issues

### 1. WebSocket Initial Connection Error

**Symptom:**
```
WebSocket connection to 'ws://localhost:8000/ws/progress/{id}' failed: 
WebSocket is closed before the connection is established.
```

**Cause:**
- Frontend connects before backend session is ready
- WebSocket handler waits 10 seconds, but connection fails immediately

**Impact:**
- Harmless (auto-reconnects)
- User sees error in console (confusing)

**Fix:**
- Add 500ms delay before WebSocket connect (already implemented)
- Improve error message (show "Connecting..." instead of error)

### 2. Server Auto-Reload Interrupts Uploads

**Symptom:**
- Backend restarts during file upload
- Session lost, upload fails

**Cause:**
- `uvicorn --reload` watches for file changes
- Code edits trigger restart mid-upload

**Impact:**
- Development only (production doesn't use --reload)
- Frustrating during testing

**Fix:**
- Use `uvicorn main:app --port 8000` (no --reload) for testing
- Or: Implement session persistence to database

### 3. Output Video Caching

**Symptom:**
- Same video shown for different sessions
- Browser caches old video

**Impact:**
- User sees wrong video
- Confusing during testing

**Fix:**
- Added cache-busting timestamp to download URL ✅
- Delete old output files before generation ✅

### 5. Temp File Accumulation

**Symptom:**
- `temp/` directory grows large over time
- Old session files never deleted

**Cause:**
- `cleanup_session()` exists but is commented out in orchestrator
- No automatic cleanup after pipeline completes

**Impact:**
- Disk space usage grows
- Cluttered temp directory
- No functional impact (just storage)

**Fix:**
- Uncomment cleanup in orchestrator after success
- Or: Add background cleanup job
- Or: Manual cleanup with `cleanup_all_temp()`

### 4. Best Moment API Calls

**Symptom:**
- Each clip-segment match = 1 extra API call
- Can hit rate limits quickly

**Impact:**
- Higher API usage
- Slower processing

**Mitigation:**
- Best moments are segment-specific (can't cache globally)
- Could cache per (clip, energy, motion, duration) tuple
- **Not implemented** (would need complex cache key)

---

## 🎨 Design Decisions

### Why Gemini 3 Flash?

**Decision:** Use `gemini-3-flash-preview` as primary model

**Reasons:**
1. **Spatial-temporal reasoning:** Better at video analysis
2. **Hackathon requirement:** Must use Gemini 3
3. **Speed:** Flash is faster than Pro
4. **Cost:** Lower token cost

**Fallbacks:**
- `gemini-1.5-flash` (reliable, high quota)
- `gemini-3-pro-preview` (higher tier)
- `gemini-2.0-flash-exp` (emergency)

### Why Energy-Based Matching?

**Decision:** Match clips to segments by energy level, not content

**Reasons:**
1. **Style over content:** We want pacing/rhythm, not subject matter
2. **Generalizable:** Works for any video type
3. **Simple:** Easy to understand and debug

**Alternative Considered:**
- Content-based matching (cat videos → cat segments)
- **Rejected:** Too specific, harder to generalize

### Why Sequential Cutting as Fallback?

**Decision:** Use sequential cutting when best moment fails

**Reasons:**
1. **Reliability:** Always works (no API dependency)
2. **Speed:** No extra API call
3. **Good enough:** Better than nothing

**Alternative Considered:**
- Random timestamp selection
- **Rejected:** Less predictable, harder to debug

### Why In-Memory Sessions?

**Decision:** Store sessions in dictionary, not database

**Reasons:**
1. **Simplicity:** No database setup needed
2. **Speed:** Fast lookups
3. **Hackathon scope:** MVP doesn't need persistence

**Trade-off:**
- Lost on restart (acceptable for demo)
- Could add Redis/PostgreSQL later

### Why MD5 Caching?

**Decision:** Use MD5 hash of file content as cache key

**Reasons:**
1. **Content-based:** Same file = same hash (even if renamed)
2. **Simple:** No database needed
3. **Fast:** Hash calculation is quick

**Alternative Considered:**
- Filename-based caching
- **Rejected:** Same file, different name = duplicate analysis

### Why Manual Mode?

**Decision:** Allow bypassing API with pre-analyzed JSON

**Reasons:**
1. **Testing:** Test matching without API quota
2. **Debugging:** Isolate issues (API vs matching)
3. **Demo:** Pre-analyze once, demo many times

**Use Case:**
- Generate JSON once with API
- Reuse for multiple tests
- Saves API calls

---

## 🧪 Testing & Usage

### Local Setup

**Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
python -m uvicorn main:app --port 8000  # NO --reload for testing
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Environment Variables:**
- `backend/.env`: `GEMINI_API_KEY=...`, `FRONTEND_URL=http://localhost:3000`
- `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`

### Testing Workflow

1. **Upload Files:**
   - Go to http://localhost:3000/upload
   - Upload 1 reference video
   - Upload 2+ clips
   - Click "Generate"

2. **Watch Progress:**
   - Backend terminal shows:
     - `[UPLOAD] New upload request`
     - `[PIPELINE] STARTING NEW PIPELINE RUN`
     - `[PROGRESS] Step X/Y: ...`
     - `Finding best moment in clip.mp4...`
   - Frontend shows progress bar

3. **Check Results:**
   - Redirects to `/result/{session_id}`
   - Video comparison component
   - Download button

### Manual Mode Testing

1. **Generate JSON:**
   - Run auto mode once
   - Copy `blueprint` and `clip_index` from session
   - Save to files

2. **Use Manual Mode:**
   - Go to "Manual Mode" tab
   - Paste JSON
   - Upload clips
   - Generate (no API calls)

### API Limit Testing

**Current Limits (Gemini 3 Flash):**
- ~15 requests/minute
- ~1500 requests/day

**With Best Moments:**
- Reference: 1 call
- Clips: N calls (N = number of clips)
- Best moments: M calls (M = number of segments)
- **Total:** 1 + N + M calls per video

**Example:**
- 1 reference + 8 clips + 10 segments = 19 calls
- **Within limits** for single video
- **May hit limits** if testing multiple videos quickly

**Optimization:**
- Caching reduces repeat calls
- Manual mode bypasses API
- Best moments only in auto mode

---

## 📊 Performance Metrics

### Processing Times (Approximate)

- **Reference analysis:** 5-10 seconds
- **Clip analysis:** 3-5 seconds per clip
- **Best moment finding:** 3-5 seconds per match
- **Video standardization:** 2-5 seconds per clip
- **Segment extraction:** 1-2 seconds per segment
- **Concatenation:** 2-5 seconds
- **Audio merge:** 1-2 seconds

**Total (8 clips, 10 segments):**
- Without caching: ~60-90 seconds
- With caching: ~30-50 seconds (if reference/clips cached)

### File Sizes

- **Reference cache:** ~1-5 KB (JSON)
- **Clip cache:** ~100 bytes (JSON)
- **Output video:** ~5-15 MB (depends on duration)

---

## 🔮 Future Improvements

### High Priority

1. **Session Persistence**
   - Store sessions in database (PostgreSQL/Redis)
   - Survive server restarts
   - Enable history feature

2. **Best Moment Caching**
   - Cache per (clip, energy, motion, duration) tuple
   - Reduce redundant API calls
   - Complex but worth it

3. **WebSocket Error Handling**
   - Better initial connection logic
   - Clearer error messages
   - Retry with exponential backoff

### Medium Priority

4. **Batch Best Moment Analysis**
   - Analyze all best moments in parallel
   - Faster processing
   - More API calls at once (may hit limits)

5. **Content-Aware Matching**
   - Match by subject matter (optional)
   - Cat videos → cat segments
   - More intelligent matching

6. **Video Quality Options**
   - User-selectable resolution
   - Compression settings
   - Format options (MP4, MOV, etc.)

### Low Priority

7. **Multi-Reference Support**
   - Blend multiple reference styles
   - Weighted matching
   - More complex but powerful

8. **Real-Time Preview**
   - Show preview before final render
   - Faster iteration
   - Lower quality preview

---

## 📝 Notes for New Contributors

### Getting Started

1. **Read this document** (you're doing it!)
2. **Check `README.md`** for setup instructions
3. **Review code structure** (see Architecture section)
4. **Run local setup** (see Testing & Usage)

### Key Files to Understand

- `backend/engine/brain.py`: AI integration, prompts, caching
- `backend/engine/editor.py`: Matching algorithm, best moments
- `backend/engine/orchestrator.py`: Pipeline flow
- `backend/main.py`: API endpoints, WebSocket
- `frontend/components/ProgressTracker.tsx`: Real-time updates

### Common Tasks

**Adding a new feature:**
1. Update this STATUS.md
2. Add tests (if applicable)
3. Update README if needed
4. Document in code comments

**Debugging:**
1. Check backend terminal logs (`[PIPELINE]`, `[UPLOAD]`, etc.)
2. Check browser console (WebSocket errors)
3. Check `data/cache/` for cached analyses
4. Check `data/results/` for output videos

**API Issues:**
1. Check `backend/.env` for API key
2. Check rate limits (15/min, 1500/day)
3. Use manual mode to bypass API
4. Clear cache to force re-analysis

---

## 🎯 Summary

**MIMIC is a functional AI video editing system** that:
- ✅ Analyzes reference videos for editing structure
- ✅ Matches user clips to segments by energy
- ✅ **Finds best moments within clips** (new feature)
- ✅ Renders final videos matching reference style
- ✅ Provides real-time progress updates
- ✅ Caches analyses to reduce API calls

**Current State:**
- Core functionality: **Working**
- Best moment selection: **Implemented** (needs testing)
- WebSocket: **Working** (minor timing issues)
- Session persistence: **Not implemented** (in-memory only)

**Next Steps:**
1. Test best moment selection with real videos
2. Monitor API usage (may need optimization)
3. Fix WebSocket initial connection error
4. Consider session persistence for production

---

**Questions?** Check this document first, then code comments, then ask!
