# Production Hardening - Fixes Applied
**Date:** 2026-02-01  
**Context:** Pre-demo polish based on GPT's pressure-tested audit

---

## ✅ **Fixes Applied (4 Changes)**

### 1. **File Extension Validation** ✅
**Files Modified:**
- `backend/main.py` (Lines 72-74, 96-104)

**What Changed:**
- Added `.mp4` validation to `/api/identify` endpoint
- Added `.mp4` validation to `/api/upload` endpoint for both reference and clips
- Returns HTTP 400 with clear error message for invalid file types

**Why:**
- Prevents confusion from uploading non-video files
- Improves error messages for users
- 2-line fix with high signal value

**Code:**
```python
# In /api/identify
if not reference.filename.lower().endswith('.mp4'):
    raise HTTPException(status_code=400, detail="Only .mp4 files are supported")

# In /api/upload
if not reference.filename.lower().endswith('.mp4'):
    raise HTTPException(status_code=400, detail="Reference must be .mp4 format")

for clip in clips:
    if not clip.filename.lower().endswith('.mp4'):
        raise HTTPException(status_code=400, detail=f"All clips must be .mp4 format (invalid: {clip.filename})")
```

---

### 2. **API Response Consistency** ✅
**Files Modified:**
- `backend/main.py` (Line 660)
- `frontend/lib/types.ts` (Line 19)

**What Changed:**
- Changed `/api/results` response from `"url"` to `"path"` 
- Updated TypeScript `Result` interface to match

**Why:**
- Results now use same field name as clips and references
- Frontend `getVideoUrl()` function works consistently across all asset types
- Eliminates need for `(item as any).url` fallback

**Before:**
```python
# Backend returned
{"url": "/api/files/results/video.mp4"}

# Frontend expected
interface Result { url: string; }
```

**After:**
```python
# Backend returns
{"path": "/api/files/results/video.mp4"}

# Frontend expects
interface Result { path: string; }
```

---

### 3. **Environment Variable Support** ✅
**Files Modified:**
- `frontend/lib/api.ts` (Line 8)
- `frontend/app/vault/page.tsx` (Lines 127, 247, 292)

**What Changed:**
- API base URL now reads from `NEXT_PUBLIC_API_URL` environment variable
- Falls back to `http://localhost:8000` for local development
- Applied to all URL construction points (API client, video URLs, thumbnail URLs)

**Why:**
- Enables deployment without code changes
- Follows Next.js best practices
- Maintains localhost default for development

**Code:**
```typescript
// In api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// In vault/page.tsx
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const path = "path" in item ? item.path : (item as any).url;
return `${API_BASE}${path}`;

// In thumbnail URLs
src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${item.thumbnail_url}`}
```

---

### 4. **Thumbnail Infrastructure** ✅
**Status:** Already Implemented (Verified)

**What Was Checked:**
- `/api/results` endpoint already generates thumbnails
- `/api/clips` endpoint already generates thumbnails  
- `/api/references` endpoint already generates thumbnails
- All use `generate_thumbnail()` with smart sampling to avoid black frames
- Frontend already prioritizes thumbnails over video elements

**Verification:**
```python
# In /api/results (lines 651-656)
res_hash = get_file_hash(result_path)
thumb_name = f"thumb_res_{res_hash}.jpg"
thumb_path = THUMBNAILS_DIR / thumb_name

if not thumb_path.exists():
    generate_thumbnail(str(result_path), str(thumb_path))
```

**No changes needed** - this was already correct.

---

## ❌ **Explicitly NOT Fixed (By Design)**

### 1. **Session Locking**
**Reason:** Already prevented by UI state management
- Button disabled during generation
- Status gate in `/api/generate`
- Returns `already_processing` if attempted
- Single-user demo context doesn't need asyncio locks

### 2. **Cache Eviction**
**Reason:** Not a demo blocker
- Single-session usage won't hit memory limits
- Would add complexity without benefit
- Deferred to production hardening phase

### 3. **WebSocket Reconnection**
**Reason:** Demo is synchronous
- User doesn't navigate away during generation
- Connection drops are edge cases
- Would add failure modes

### 4. **Type Assertions (`as any`)**
**Reason:** Controlled data context
- Data comes from known backend
- No user-supplied type data
- Refactoring now adds risk

### 5. **Search Debouncing**
**Reason:** Premature optimization
- <100 assets in demo
- Filter is instant
- No performance issue observed

---

## 📊 **Impact Assessment**

| Fix | Risk | Effort | Signal | Priority |
|-----|------|--------|--------|----------|
| File validation | Low | 5 min | High | ✅ Done |
| API consistency | Low | 2 min | Medium | ✅ Done |
| Environment vars | Low | 3 min | High | ✅ Done |
| Thumbnails | N/A | 0 min | High | ✅ Verified |

**Total Time:** ~10 minutes  
**Total Risk:** Minimal (no logic changes, only validation + config)

---

## 🎯 **Architectural Decisions Documented**

### Why No Locking?
> "MIMIC prioritizes deterministic artifact reconstruction over live session durability. For a single-user creative workflow, explicit locking adds complexity without improving editorial correctness."

### Why In-Memory Sessions?
> "Session state is ephemeral by design. All durable artifacts (videos, JSON reports, thumbnails) are persisted to disk with content-based hashing. Session recovery happens via filesystem scan, not memory."

### Why No Reconnection?
> "The generation workflow is synchronous and terminal-supervised. WebSocket is for progress visualization, not critical state management. Connection loss doesn't corrupt the render."

---

## ✅ **Verification Checklist**

- [x] File uploads reject non-.mp4 files
- [x] Results API returns `path` field (not `url`)
- [x] Frontend types match backend response
- [x] All URLs use environment variable
- [x] Thumbnails render for all asset types
- [x] No hardcoded `localhost:8000` in production code paths
- [x] Fallback to localhost still works for development

---

## 📝 **Deployment Notes**

To deploy to production, set environment variable:

```bash
# Frontend (.env.local or deployment config)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Backend (already configured)
FRONTEND_URL=https://yourdomain.com
```

No code changes required.

---

## 🔍 **What Was NOT Touched**

- Concurrency primitives
- Frontend error handling refactor
- Cache eviction logic
- Type guard implementations
- Debouncing
- Request timeouts
- CORS preflight cache
- Thumbnail cleanup on delete

**Reason:** These are production hardening tasks, not demo blockers. Implementing them now increases risk without improving the recorded demo experience.

---

## Final Status

**Demo-Ready:** ✅  
**Production-Ready:** 🟡 (with documented tradeoffs)  
**Risk Level:** Low (surgical fixes only)  
**Regression Risk:** Minimal (no logic changes)
