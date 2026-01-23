# MIMIC UI Enhancement - Implementation Plan

## Data Discovery Summary

### ✅ Backend Data Available

**From `/api/status/{session_id}`:**
```json
{
  "status": "uploaded" | "processing" | "complete" | "error",
  "progress": 0.0-1.0,
  "current_step": "Analyzing reference...",
  "logs": ["...", "..."],
  "output_path": "data/results/mimic_output_xxx.mp4",
  "blueprint": {
    "total_duration": 15.2,
    "segments": [...],
    "editing_style": "Montage",
    "emotional_intent": "Energetic",
    "arc_description": "...",
    "overall_reasoning": "...",
    "ideal_material_suggestions": ["..."]
  },
  "clip_index": {
    "clips": [...]
  },
  "error": "..." (if error)
}
```

**Blueprint Structure:**
- `total_duration`: Total video length
- `segments`: Array of segments with energy, vibe, arc_stage, reasoning
- `editing_style`: e.g., "Cinematic", "Vlog", "Montage"
- `emotional_intent`: e.g., "Energetic", "Peaceful"
- `ideal_material_suggestions`: Recommendations for user

**Segment Structure:**
```json
{
  "id": 1,
  "start": 0.0,
  "end": 2.3,
  "duration": 2.3,
  "energy": "High" | "Medium" | "Low",
  "motion": "Static" | "Dynamic",
  "vibe": "Action",
  "reasoning": "...",
  "arc_stage": "Intro" | "Build-up" | "Peak" | "Outro"
}
```

**Clip Metadata:**
```json
{
  "filename": "clip.mp4",
  "filepath": "...",
  "duration": 15.2,
  "energy": "High",
  "motion": "Dynamic",
  "vibes": ["Urban", "Action"],
  "content_description": "...",
  "best_moments": {
    "High": {"start": 8.2, "end": 10.5, "reason": "..."},
    "Medium": {"start": 4.0, "end": 6.2, "reason": "..."},
    "Low": {"start": 0.0, "end": 2.0, "reason": "..."}
  }
}
```

### ✅ WebSocket Progress Updates

**Real-time updates via `/ws/progress/{session_id}`:**
```json
{
  "status": "processing",
  "progress": 0.65,
  "message": "Matching clips...",
  "logs": ["...", "..."]
}
```

### ❌ Missing Data (Need to Calculate)

- **Stage Timing**: Not explicitly tracked, but can infer from logs
- **EDL Decisions**: Available in `PipelineResult` but not exposed in `/api/status`
- **Metrics**: Need to calculate from blueprint/clip_index
  - Clip Diversity = unique clips used / total segments
  - Vibe Match = segments with matching vibes / total segments
  - Energy Coherence = segments with exact energy match / total

---

## Implementation Strategy

### Phase 1: Foundation (15 min) ✅
**Status:** Ready to implement
**Dependencies:** None

**Tasks:**
1. Update `globals.css` with new color palette
2. Add typography utilities
3. Create base component files

**Data Required:** None (pure styling)

---

### Phase 2: Studio Page (35 min) ⚠️
**Status:** Partially ready
**Dependencies:** Need to add `/api/cache-stats` endpoint OR calculate from existing data

#### 2.1 System Status Bar
**Data Available:**
- ✅ System status (from active sessions)
- ❌ Cache hit rate (need to calculate or add endpoint)
- ❌ Clips analyzed count (need to query cache directory)
- ✅ Gemini status (can show "Active" when processing)

**Recommendation:** Use placeholder values initially, add `/api/cache-stats` endpoint later

#### 2.2 Gemini Intelligence Panel
**Data Available:**
- ✅ Can show static description of Gemini capabilities
- ✅ Can show `ideal_material_suggestions` from blueprint (after analysis)
- ✅ Can show cache status from session

**Implementation:** Static content + dynamic recommendations when available

#### 2.3 Enhanced Processing Modal
**Data Available:**
- ✅ Progress (0.0-1.0)
- ✅ Current step message
- ✅ Logs array
- ❌ Stage timing (not explicitly tracked)

**Recommendation:** 
- Use `current_step` to infer which stage is active
- Parse logs to extract stage completion messages
- Show live logs in reasoning panel

---

### Phase 3: Vault Page (20 min) ✅
**Status:** Fully ready
**Dependencies:** Need to fetch session data for displayed result

#### 3.1 X-Ray Metrics
**Data Available:**
- ✅ Blueprint with segments
- ✅ Clip index with metadata
- ✅ Can calculate all metrics:
  - Clip Diversity: Count unique clip paths in decisions
  - Vibe Match: Count segments where vibe matches
  - Energy Coherence: Count segments where energy matches
  - Timeline Precision: Always <0.001s (enforced by validation)

**Implementation:** Calculate metrics from blueprint + clip_index

#### 3.2 EDL Visualization
**Data Available:**
- ❌ EDL not currently exposed in `/api/status`
- ✅ Blueprint segments available
- ✅ Clip index available

**Recommendation:** 
- **Option A:** Add `edl` to session data in `main.py` (5 min backend change)
- **Option B:** Show blueprint segments instead (still valuable)

**I recommend Option A** - it's a simple addition to line 324 in `main.py`:
```python
active_sessions[session_id]["edl"] = result.edl.model_dump() if result.edl else None
```

---

### Phase 4: Library Page (10 min) ✅
**Status:** Fully ready
**Dependencies:** None

**Data Available:**
- ✅ Clip list from `/api/clips`
- ❌ AI analysis metadata not included in clip list
- ✅ Can add cache check to see if clip is analyzed

**Recommendation:** Add `analyzed` and `cached` flags to `/api/clips` response

---

## Recommended Implementation Order

### Session 1: Foundation + Backend Prep (20 min)
1. **Update `globals.css`** (5 min)
2. **Add EDL to session data** (5 min backend)
   ```python
   # In main.py line 324
   active_sessions[session_id]["edl"] = result.edl.model_dump() if result.edl else None
   ```
3. **Add cache stats endpoint** (10 min backend)
   ```python
   @app.get("/api/cache-stats")
   async def get_cache_stats():
       clip_count = len(list(CACHE_DIR.glob("clip_comprehensive_*.json")))
       ref_count = len(list(CACHE_DIR.glob("ref_*.json")))
       return {
           "clips_analyzed": clip_count,
           "references_cached": ref_count,
           "cache_hit_rate": 1.0  # Calculate if needed
       }
   ```

### Session 2: Studio Page (35 min)
1. **Create SystemStatusBar component** (10 min)
2. **Redesign Gemini Intelligence Panel** (15 min)
3. **Enhance Processing Modal** (10 min)

### Session 3: Vault Page (20 min)
1. **Add X-Ray Metrics calculation** (10 min)
2. **Add EDL Visualization** (10 min)

### Session 4: Library + Polish (15 min)
1. **Add AI badges to Library** (5 min)
2. **Update Header** (5 min)
3. **Final testing** (5 min)

---

## Backend Changes Required

### Required (for full functionality):
1. **Add EDL to session data** (main.py:324)
   ```python
   active_sessions[session_id]["edl"] = result.edl.model_dump() if result.edl else None
   ```

### Optional (nice to have):
1. **Add `/api/cache-stats` endpoint**
2. **Add analysis metadata to `/api/clips` response**

---

## Data Wiring Plan

### Studio Page
```tsx
// System Status Bar
const [cacheStats, setCacheStats] = useState({ clips_analyzed: 0 });
useEffect(() => {
  fetch('/api/cache-stats').then(r => r.json()).then(setCacheStats);
}, []);

// Gemini Panel - shows recommendations after synthesis
const recommendations = sessionData?.blueprint?.ideal_material_suggestions || [];
```

### Vault Page
```tsx
// Fetch session data for selected result
const [sessionData, setSessionData] = useState(null);
useEffect(() => {
  if (selectedResult) {
    // Extract session_id from filename or store it
    fetch(`/api/status/${session_id}`).then(r => r.json()).then(setSessionData);
  }
}, [selectedResult]);

// Calculate metrics
const metrics = useMemo(() => {
  if (!sessionData?.blueprint || !sessionData?.edl) return null;
  
  const uniqueClips = new Set(sessionData.edl.decisions.map(d => d.clip_path)).size;
  const totalSegments = sessionData.blueprint.segments.length;
  
  return {
    clipDiversity: (uniqueClips / totalSegments * 100).toFixed(0),
    vibeMatch: calculateVibeMatch(sessionData),
    energyCoherence: calculateEnergyCoherence(sessionData),
    timelinePrecision: "<0.001s"
  };
}, [sessionData]);
```

---

## Next Steps

**Ready to proceed with:**
1. ✅ Phase 1 (Foundation) - No blockers
2. ⚠️ Phase 2 (Studio) - Can use placeholders, add backend later
3. ✅ Phase 3 (Vault) - Need EDL in session data (5 min backend change)
4. ✅ Phase 4 (Library) - No blockers

**Recommendation:** Start with Phase 1 immediately, then add EDL to backend while building Studio components.
