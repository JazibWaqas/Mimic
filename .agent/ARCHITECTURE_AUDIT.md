# MIMIC Project - Comprehensive Architecture Audit
**Date:** 2026-02-01  
**Auditor:** Claude (Sonnet 4.5)  
**Scope:** Full-stack review of ~20 files (Frontend + Backend)

---

## Executive Summary

### Overall Assessment: **7.5/10** (Production-Ready with Minor Fixes Needed)

**Strengths:**
- ✅ Clean separation of concerns (orchestrator → brain → editor → processors)
- ✅ Robust error handling in pipeline with graceful degradation
- ✅ Proper use of Pydantic models for type safety
- ✅ Smart caching strategies (thumbnails, standardized clips, AI analyses)
- ✅ Good state management in frontend with React hooks

**Critical Issues Found:** 2  
**Medium Issues Found:** 5  
**Minor Issues Found:** 8  

---

## 🔴 CRITICAL ISSUES (Must Fix)

### 1. **Missing `thumbnail_url` in Results API Response**
**File:** `backend/main.py` (Line 630-654)  
**Severity:** CRITICAL - Breaks Vault page thumbnails

**Problem:**
```python
# /api/results endpoint returns results WITHOUT thumbnail_url
results.append({
    "filename": result_path.name,
    "path": f"/api/files/results/{result_path.name}",
    # ❌ MISSING: "thumbnail_url": ...
    "size": result_path.stat().st_size,
    "created_at": result_path.stat().st_mtime
})
```

**Impact:** 
- Vault page tries to render `item.thumbnail_url` for results (line 268 in `vault/page.tsx`)
- Falls back to `<video>` tag, causing black frames and performance issues
- Inconsistent with `/api/clips` and `/api/references` which DO include thumbnails

**Fix Required:**
```python
# Add thumbnail generation for results
result_hash = get_file_hash(result_path)
thumb_name = f"thumb_result_{result_hash}.jpg"
thumb_path = THUMBNAILS_DIR / thumb_name

if not thumb_path.exists():
    generate_thumbnail(str(result_path), str(thumb_path))

results.append({
    "filename": result_path.name,
    "path": f"/api/files/results/{result_path.name}",
    "thumbnail_url": f"/api/files/thumbnails/{thumb_name}",  # ✅ ADD THIS
    "size": result_path.stat().st_size,
    "created_at": result_path.stat().st_mtime
})
```

---

### 2. **Race Condition in Session State Management**
**File:** `backend/main.py` (Line 188-195, 250-280)  
**Severity:** CRITICAL - Can cause data corruption

**Problem:**
- `active_sessions` is a global dict modified by multiple async endpoints
- No locking mechanism for concurrent access
- WebSocket and HTTP endpoints both modify session state

**Impact:**
- If user clicks "Generate" twice quickly, iteration counter can be wrong
- Progress updates can be lost or overwritten
- Session data can become inconsistent

**Fix Required:**
```python
import asyncio

# Add at top of file
session_locks = {}

@app.post("/api/generate/{session_id}")
async def generate_video(session_id: str, background_tasks: BackgroundTasks):
    # Acquire lock for this session
    if session_id not in session_locks:
        session_locks[session_id] = asyncio.Lock()
    
    async with session_locks[session_id]:
        # ... existing code ...
        session["status"] = "processing"
        # ... rest of logic ...
```

---

## 🟡 MEDIUM ISSUES (Should Fix)

### 3. **Inconsistent Error Handling in Frontend API Client**
**File:** `frontend/lib/api.ts`  
**Severity:** MEDIUM

**Problem:**
- All API methods throw generic `Error` objects
- No structured error types or status code handling
- Frontend can't distinguish between network errors, 404s, 500s, etc.

**Example:**
```typescript
fetchClips: async () => {
    const res = await fetch(`${API_BASE}/api/clips`);
    if (!res.ok) throw new Error("Failed to fetch clips"); // ❌ Too generic
    return res.json();
}
```

**Recommendation:**
```typescript
class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
    }
}

fetchClips: async () => {
    const res = await fetch(`${API_BASE}/api/clips`);
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new ApiError(res.status, error.detail || "Failed to fetch clips");
    }
    return res.json();
}
```

---

### 4. **Memory Leak in Intelligence Cache**
**File:** `frontend/lib/api.ts` (Line 10, 93-102)  
**Severity:** MEDIUM

**Problem:**
```typescript
const intelCache = new Map<string, any>(); // ❌ Never cleared
```

**Impact:**
- Cache grows indefinitely as user browses different videos
- In a long session, this could consume significant memory
- No TTL or size limit

**Fix:**
```typescript
// Add cache eviction
const MAX_CACHE_SIZE = 50;
const intelCache = new Map<string, any>();

fetchIntelligence: async (type: string, filename: string) => {
    const cacheKey = `${type}:${filename}`;
    if (intelCache.has(cacheKey)) return intelCache.get(cacheKey);

    const res = await fetch(`${API_BASE}/api/intelligence?type=${type}&filename=${encodeURIComponent(filename)}`);
    if (!res.ok) throw new Error("Intelligence data not found");
    const data = await res.json();
    
    // Evict oldest if cache is full
    if (intelCache.size >= MAX_CACHE_SIZE) {
        const firstKey = intelCache.keys().next().value;
        intelCache.delete(firstKey);
    }
    
    intelCache.set(cacheKey, data);
    return data;
}
```

---

### 5. **Unsafe Type Assertions in Vault Page**
**File:** `frontend/app/vault/page.tsx` (Multiple locations)  
**Severity:** MEDIUM

**Problem:**
```typescript
const path = "path" in item ? item.path : (item as any).url; // ❌ Unsafe cast
```

**Impact:**
- Runtime errors if data structure changes
- TypeScript can't catch bugs

**Fix:**
```typescript
// Define proper type guards
function hasPath(item: AssetItem): item is Result | Reference {
    return 'path' in item;
}

function hasUrl(item: AssetItem): item is Clip {
    return 'url' in item;
}

const getVideoUrl = (item: AssetItem) => {
    const path = hasPath(item) ? item.path : hasUrl(item) ? item.url : '';
    return `http://localhost:8000${path}`;
};
```

---

### 6. **No Validation of File Extensions**
**File:** `backend/main.py` (Upload endpoints)  
**Severity:** MEDIUM

**Problem:**
- Backend accepts any file type in upload
- Only checks `.mp4` extension when listing, not when saving
- Could save malicious files or corrupt data

**Fix:**
```python
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}

@app.post("/api/upload")
async def upload_files(reference: UploadFile = File(...), clips: List[UploadFile] = File(...)):
    # Validate reference
    ref_ext = Path(reference.filename).suffix.lower()
    if ref_ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, f"Invalid reference format: {ref_ext}")
    
    # Validate clips
    for clip in clips:
        clip_ext = Path(clip.filename).suffix.lower()
        if clip_ext not in ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(400, f"Invalid clip format: {clip_ext}")
    
    # ... rest of upload logic ...
```

---

### 7. **Hardcoded Localhost URLs**
**File:** `frontend/lib/api.ts`, `frontend/app/vault/page.tsx`  
**Severity:** MEDIUM

**Problem:**
```typescript
const API_BASE = "http://localhost:8000"; // ❌ Hardcoded
```

**Impact:**
- Can't deploy to production without code changes
- Can't use environment variables

**Fix:**
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
```

---

## 🟢 MINOR ISSUES (Nice to Fix)

### 8. **Inconsistent Naming Conventions**
- `active_sessions` (snake_case) vs `sessionId` (camelCase)
- `clip_paths` vs `clipPaths`
- Mix of Python and JavaScript conventions in same codebase

**Recommendation:** Stick to snake_case in Python, camelCase in TypeScript

---

### 9. **Missing Loading States**
**File:** `frontend/app/vault/page.tsx`

**Problem:**
- `intelLoading` state exists but isn't used in UI
- User doesn't know when intelligence is being fetched

**Fix:** Add loading spinner in Intelligence Panel

---

### 10. **No Request Timeout Configuration**
**File:** `frontend/lib/api.ts`

**Problem:**
- Fetch requests have no timeout
- Long-running requests can hang indefinitely

**Fix:**
```typescript
const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout = 30000) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
};
```

---

### 11. **Duplicate Hash Computation Logic**
**Files:** `backend/main.py` (multiple locations)

**Problem:**
- Hash computation logic duplicated in 3+ places
- Inconsistent chunk sizes (1MB vs 2MB thresholds)

**Fix:** Extract to utility function in `utils.py`

---

### 12. **No WebSocket Reconnection Logic**
**File:** `frontend/app/page.tsx` (Line 47)

**Problem:**
```typescript
const ws = api.connectProgress(sessionId); // ❌ No reconnect on disconnect
```

**Impact:** If connection drops, user loses progress updates

---

### 13. **Search Query Not Debounced**
**File:** `frontend/app/vault/page.tsx` (Line 120-124)

**Problem:**
- Filter runs on every keystroke
- Could be slow with large asset lists

**Fix:**
```typescript
const [debouncedQuery, setDebouncedQuery] = useState("");

useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(searchQuery), 300);
    return () => clearTimeout(timer);
}, [searchQuery]);

const currentAssets = useMemo(() => {
    const assets = viewMode === "results" ? results : viewMode === "references" ? references : clips;
    if (!debouncedQuery.trim()) return assets;
    return assets.filter(a => a.filename.toLowerCase().includes(debouncedQuery.toLowerCase()));
}, [viewMode, results, references, clips, debouncedQuery]);
```

---

### 14. **Missing CORS Preflight Cache**
**File:** `backend/main.py` (Line 52-58)

**Recommendation:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,  # ✅ Add preflight cache
)
```

---

### 15. **No Cleanup of Old Thumbnails**
**File:** `backend/main.py`

**Problem:**
- Thumbnails are generated but never deleted
- If user deletes a video, thumbnail remains

**Fix:** Add cleanup in delete endpoints

---

## ✅ ARCHITECTURAL STRENGTHS

### Well-Designed Patterns:

1. **Orchestrator Pattern** (`backend/engine/orchestrator.py`)
   - Single entry point for pipeline
   - Clean error boundaries
   - Proper logging and state management

2. **Pydantic Models** (`backend/models.py`)
   - Strong typing throughout backend
   - Validation at data boundaries
   - Good use of field validators

3. **Graceful Degradation**
   - Advisor can fail without breaking pipeline
   - Fallback blueprints when Gemini fails
   - Cache misses handled properly

4. **Smart Caching Strategy**
   - Content-based hashing for deduplication
   - Persistent cache for standardized clips
   - Thumbnail caching with smart sampling

5. **Separation of Concerns**
   - Brain (analysis) → Editor (matching) → Processors (rendering)
   - Each module has clear responsibility
   - Minimal coupling between modules

---

## 🎯 PRIORITY RECOMMENDATIONS

### Immediate (Before Demo):
1. ✅ Fix `thumbnail_url` in results API (CRITICAL #1)
2. ✅ Add session locking (CRITICAL #2)
3. Add file extension validation (MEDIUM #6)

### Short-term (This Week):
4. Improve error handling in API client (MEDIUM #3)
5. Add cache eviction (MEDIUM #4)
6. Fix hardcoded URLs (MEDIUM #7)

### Long-term (Next Sprint):
7. Implement proper type guards (MEDIUM #5)
8. Add WebSocket reconnection
9. Debounce search input
10. Add request timeouts

---

## 📊 CODE QUALITY METRICS

| Category | Score | Notes |
|----------|-------|-------|
| **Architecture** | 8/10 | Clean separation, good patterns |
| **Type Safety** | 7/10 | Pydantic strong, TS has `any` casts |
| **Error Handling** | 6/10 | Backend good, frontend needs work |
| **Performance** | 7/10 | Good caching, some memory leaks |
| **Security** | 6/10 | Missing input validation |
| **Maintainability** | 8/10 | Well-documented, clear structure |

**Overall:** 7.5/10 - Production-ready with minor fixes

---

## 🔍 TESTING RECOMMENDATIONS

### Unit Tests Needed:
- `get_file_hash()` utility function
- `compute_advisor_bonus()` scoring logic
- Type guards in frontend

### Integration Tests Needed:
- Full pipeline with mock Gemini responses
- WebSocket progress updates
- File upload deduplication

### E2E Tests Needed:
- Upload → Generate → View in Vault flow
- Search and filter functionality
- Refinement workflow

---

## 📝 DOCUMENTATION GAPS

1. No API documentation (consider OpenAPI/Swagger)
2. No deployment guide
3. No environment variable documentation
4. Missing inline comments in complex algorithms (editor.py)

---

## Final Verdict

The codebase is **well-architected and mostly production-ready**. The two critical issues (thumbnails and race conditions) are straightforward fixes. The medium issues are quality-of-life improvements that should be addressed before scaling.

**Recommendation:** Fix Critical #1 and #2, then ship. Address medium issues in next iteration.
