# MIMIC Architecture Documentation

**Version:** V7.0  
**Last Updated:** January 23, 2026

This document provides a complete technical overview of the MIMIC system architecture, algorithms, and design decisions.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Algorithms](#core-algorithms)
3. [Caching Strategy](#caching-strategy)
4. [Data Flow](#data-flow)
5. [Key Design Decisions](#key-design-decisions)
6. [Performance Optimizations](#performance-optimizations)

---

## System Overview

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                   UI Components + State                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────┴──────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                     main.py (API Layer)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   Orchestrator (Pipeline)                    │
│              orchestrator.py (State Machine)                 │
└─────┬──────────┬──────────┬──────────┬──────────────────────┘
      │          │          │          │
┌─────┴────┐ ┌──┴────┐ ┌───┴────┐ ┌──┴─────┐
│  Brain   │ │Editor │ │Process │ │ Utils  │
│ (Gemini) │ │(Match)│ │(FFmpeg)│ │(Cache) │
└──────────┘ └───────┘ └────────┘ └────────┘
```

### Module Responsibilities

**orchestrator.py** - Pipeline Controller
- Manages 5-stage pipeline execution
- Handles session state and directories
- Coordinates all modules
- Implements persistent caching

**brain.py** - AI Analysis
- Gemini API integration
- Reference video analysis
- Clip analysis (comprehensive mode)
- Cache management (analysis results)

**editor.py** - Matching Algorithm
- Tiered energy eligibility
- Scoring system (discovery, vibe, arc, usage)
- Best moment selection
- Diversity optimization
- Compromise tracking
- Smart recommendations

**processors.py** - Video Processing
- FFmpeg wrappers
- Scene detection
- BPM detection (librosa)
- Video standardization
- Segment extraction
- Concatenation

**utils/api_key_manager.py** - Quota Management
- Multi-key loading (28 keys)
- Automatic rotation on quota limits
- Per-operation tracking

---

## Core Algorithms

### 1. Tiered Energy Matching

**Problem:** Using a Low-energy clip for a High-energy segment creates jarring transitions.

**Solution:** Tiered eligibility system

```python
def get_eligible_clips(segment_energy, all_clips):
    """
    High segment → High + Medium clips (never Low)
    Low segment → Low + Medium clips (never High)
    Medium → Any clips
    """
    if segment_energy == HIGH:
        return [c for c in all_clips if c.energy in [HIGH, MEDIUM]]
    elif segment_energy == LOW:
        return [c for c in all_clips if c.energy in [LOW, MEDIUM]]
    else:  # MEDIUM
        return all_clips
```

**Benefits:**
- Prevents Low→High jumps
- Allows graceful degradation (Medium as fallback)
- Tracks compromises for user feedback

### 2. Clip Scoring System

**Multi-factor scoring** to select the best clip for each segment:

```python
def score_clip(clip, segment, usage_count, last_used_at):
    score = 0
    
    # 1. Discovery Bonus (prioritize unused clips)
    if usage_count[clip] == 0:
        score += 40
    
    # 2. Energy Match
    if clip.energy == segment.energy:
        score += 20  # Exact match
    else:
        score += 5   # Adjacent (allowed by tier)
    
    # 3. Vibe Match (semantic alignment)
    if segment.vibe in clip.vibes:
        score += 15
    
    # 4. Arc Stage Alignment
    if is_arc_relevant(clip, segment.arc_stage):
        score += 10
    
    # 5. Usage Penalty (discourage repetition)
    score -= usage_count[clip] * 25
    
    # 6. Cooldown (prevent visual monotony)
    time_since_use = current_time - last_used_at[clip]
    if time_since_use < 5.0:  # 5 second cooldown
        score -= 40
    
    return score
```

**Score Ranges:**
- **75+**: Perfect match (new clip, exact energy, vibe match)
- **60-74**: Good match (new clip, adjacent energy or no vibe)
- **45-59**: Acceptable (new clip, compromise)
- **<45**: Used clip or cooldown violation

### 3. Best Moment Selection

Each clip is pre-analyzed to identify optimal segments for each energy level:

```python
# During clip analysis (brain.py)
best_moments = {
    "High": {
        "start": 8.2,
        "end": 10.5,
        "reason": "Peak action - skateboard trick"
    },
    "Medium": {
        "start": 4.0,
        "end": 6.2,
        "reason": "Cruising - steady movement"
    },
    "Low": {
        "start": 0.0,
        "end": 2.0,
        "reason": "Setup - minimal movement"
    }
}
```

**During matching:**
```python
# Extract the pre-computed best moment
moment = clip.best_moments[segment.energy]
extract_segment(clip.path, moment.start, moment.end)
```

**Benefits:**
- Gemini pre-identifies optimal moments
- No runtime analysis needed
- Consistent quality

### 4. Beat Synchronization

**BPM Detection:**
```python
import librosa

def detect_bpm(audio_path):
    y, sr = librosa.load(audio_path)
    tempo = librosa.beat.beat_track(y=y, sr=sr)[0]
    return float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
```

**Beat Grid Generation:**
```python
def get_beat_grid(duration, bpm):
    beat_interval = 60.0 / bpm  # seconds per beat
    beats = []
    t = 0.0
    while t <= duration:
        beats.append(t)
        t += beat_interval
    return beats
```

**Cut Snapping:**
```python
def snap_to_beat(time, beat_grid, tolerance=0.1):
    nearest_beat = min(beat_grid, key=lambda b: abs(b - time))
    if abs(nearest_beat - time) <= tolerance:
        return nearest_beat
    return time  # Don't snap if too far
```

---

## Caching Strategy

### Three-Tier Cache System

#### 1. **Gemini Analysis Cache** (Permanent)

**Location:** `data/cache/`

**Clip Analysis:**
```
clip_comprehensive_{hash}.json
```
- Hash: MD5 of (filepath + filesize + mtime)
- Never expires (clips don't change)
- Contains: energy, motion, vibes, best_moments, content_description

**Reference Analysis:**
```
ref_{video_hash}_h{hints_hash}.json
```
- video_hash: MD5 of (filepath + filesize + mtime)
- hints_hash: MD5 of scene timestamps
- Expires if scene detection changes
- Contains: segments with energy, motion, vibe, arc_stage, reasoning

#### 2. **Standardization Cache** (Persistent)

**Location:** `data/cache/standardized/`

**Naming:**
```
std_{hash}.mp4
```
- Hash: MD5 of (filepath + filesize + mtime + standardization_params)
- Reused across all sessions
- Auto-detects file changes

**Process:**
```python
def standardize_clip(input_path, output_path):
    # Generate cache key
    stat = Path(input_path).stat()
    cache_key = f"{input_path}_{stat.st_size}_{stat.st_mtime}"
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
    cached_path = f"data/cache/standardized/std_{cache_hash}.mp4"
    
    # Check cache
    if cached_path.exists():
        shutil.copy2(cached_path, output_path)
        return
    
    # Standardize (1080x1920, 30fps, h264, AAC)
    ffmpeg_standardize(input_path, output_path)
    
    # Save to cache
    shutil.copy2(output_path, cached_path)
```

**Performance:**
- **Cache Hit:** <1 second (file copy)
- **Cache Miss:** 5-10 seconds (FFmpeg encoding)

#### 3. **Session Cache** (Temporary)

**Location:** `temp/{session_id}/`

**Contents:**
- `standardized/` - Session-specific standardized clips (copied from persistent cache)
- `segments/` - Extracted segments for concatenation
- `ref_analysis_audio.wav` - Extracted audio for BPM detection

**Lifecycle:** Deleted after session completes (optional cleanup)

---

## Data Flow

### Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: VALIDATION                                          │
│ - Check reference exists                                     │
│ - Check clips directory                                      │
│ - Validate API key                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│ STAGE 2: REFERENCE ANALYSIS                                  │
│ 1. Scene Detection (FFmpeg)                                  │
│    └─> timestamps = [0.5, 1.2, 2.3, ...]                    │
│ 2. BPM Detection (librosa)                                   │
│    └─> bpm = 129.2                                           │
│ 3. Gemini Analysis (with scene hints)                        │
│    └─> segments = [{energy, vibe, arc_stage, ...}, ...]     │
│ 4. Cache Result                                              │
│    └─> ref_{hash}_h{hints_hash}.json                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│ STAGE 3: CLIP ANALYSIS + STANDARDIZATION                     │
│ For each clip:                                               │
│ 1. Check Analysis Cache                                      │
│    └─> clip_comprehensive_{hash}.json                        │
│ 2. If miss: Gemini Analysis                                  │
│    └─> {energy, vibes, best_moments, ...}                    │
│ 3. Check Standardization Cache                               │
│    └─> data/cache/standardized/std_{hash}.mp4               │
│ 4. If miss: FFmpeg Standardization                           │
│    └─> 1080x1920, 30fps, h264, AAC                          │
│ 5. Copy to session directory                                 │
│    └─> temp/{session}/standardized/clip_001.mp4             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│ STAGE 4: INTELLIGENT MATCHING                                │
│ 1. Pre-Edit Demand Analysis                                  │
│    └─> Count High/Medium/Low needed vs available            │
│ 2. For each segment:                                         │
│    a. Filter by tiered eligibility                           │
│    b. Score each eligible clip                               │
│    c. Select highest score                                   │
│    d. Extract best moment                                    │
│    e. Record reasoning                                       │
│ 3. Post-Edit Summary                                         │
│    └─> Diversity, compromises, recommendations              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│ STAGE 5: RENDERING                                           │
│ 1. Generate beat grid from BPM                               │
│ 2. For each decision:                                        │
│    a. Snap cut points to beats                               │
│    b. Extract segment (FFmpeg)                               │
│    └─> temp/{session}/segments/segment_001.mp4              │
│ 3. Concatenate all segments                                  │
│ 4. Extract reference audio                                   │
│ 5. Merge audio + video                                       │
│ 6. Output final video                                        │
│    └─> data/results/mimic_output_{session}.mp4              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Why Tiered Energy Matching?

**Problem:** Early versions used strict energy matching (High→High only). This caused:
- Frequent clip repetition
- "All keys exhausted" errors (re-analyzing same clips)
- Poor diversity

**Solution:** Tiered system allows graceful degradation:
- High can use Medium (acceptable energy drop)
- Low can use Medium (acceptable energy increase)
- Never Low→High or High→Low (jarring)

**Result:** 90%+ unique clip usage, zero repetition in most edits

### 2. Why Discovery Bonus (+40 points)?

**Problem:** Without discovery bonus, the system would:
- Reuse "perfect match" clips repeatedly
- Ignore 80% of the library
- Create visually monotonous edits

**Solution:** Massive bonus for unused clips ensures:
- Every clip gets a chance
- Variety is prioritized over perfect matches
- Only repeats when absolutely necessary

**Trade-off:** Occasionally uses "good" clip over "perfect" clip for variety

### 3. Why Persistent Standardization Cache?

**Problem:** Standardizing 36 clips took 5-10 minutes every run

**Solution:** Hash-based persistent cache:
- Standardize once, reuse forever
- Automatic invalidation on file changes
- Shared across all sessions

**Result:** 15-20s total pipeline time (down from 600s+)

### 4. Why Pre-Compute Best Moments?

**Problem:** Runtime analysis of "best moment" for each segment would require:
- 30+ Gemini calls per edit
- 5-10 minutes of analysis
- Quota exhaustion

**Solution:** Pre-compute during clip analysis:
- One-time cost per clip
- Cached forever
- Instant lookup during matching

**Result:** Zero runtime AI calls for moment selection

### 5. Why Scene Hint Fingerprinting?

**Problem:** Reference cache was invalidating unnecessarily

**Solution:** Include scene timestamps in cache key:
- Same video + same scene detection = cache hit
- Different scene detection = cache miss (correct)

**Result:** Stable caching, no false hits

---

## Performance Optimizations

### Optimization Timeline

**V1.0 (Initial):** 600+ seconds
- No caching
- Re-analyzed everything
- Stream copy (inaccurate cuts)

**V6.0 (Semantic):** 120-180 seconds
- Gemini analysis cache
- Still re-standardizing clips
- Frame-accurate cuts

**V7.0 (Production):** 15-20 seconds
- Persistent standardization cache
- Optimized API key rotation
- Parallel cache checks

### Bottleneck Analysis

**Current Breakdown (30-segment edit):**
```
Scene Detection:     2-3s
BPM Detection:       1-2s
Reference Analysis:  0s (cached)
Clip Analysis:       0s (cached)
Standardization:     1s (cached, 36 copies)
Matching:            <1s
Segment Extraction:  8-10s (30 FFmpeg calls)
Concatenation:       2-3s
Audio Merge:         1s
─────────────────────────
Total:              15-20s
```

**Remaining Bottleneck:** Segment extraction (FFmpeg)
- 30 separate FFmpeg processes
- Frame-accurate re-encoding required
- Potential optimization: Batch processing or segment cache

### Memory Usage

**Peak Memory:** ~500MB
- Gemini API responses: ~50MB
- FFmpeg processes: ~200MB per process
- Python runtime: ~100MB
- Cache metadata: ~10MB

**Disk Usage:**
- Standardized cache: ~300MB (36 clips)
- Analysis cache: ~2MB (JSON files)
- Session temp: ~500MB (deleted after)

---

## Error Handling

### API Key Rotation

```python
class APIKeyManager:
    def rotate_key(self, reason):
        self.exhausted_keys.add(self.current_key)
        self.current_index = (self.current_index + 1) % len(self.keys)
        
        if len(self.exhausted_keys) == len(self.keys):
            raise Exception("All API keys exhausted")
        
        # Re-initialize genai with new key
        genai.configure(api_key=self.current_key)
```

**Triggers:**
- 429 Rate Limit
- 403 Permission Denied (file upload issues)
- Quota exceeded errors

### Timeline Integrity

**Enforcement:**
```python
def validate_edl(edl, blueprint):
    # Check continuity
    for i in range(1, len(edl.decisions)):
        gap = edl.decisions[i].timeline_start - edl.decisions[i-1].timeline_end
        if abs(gap) > 0.001:
            raise ValueError(f"Timeline gap detected: {gap}s")
    
    # Check total duration
    total = edl.decisions[-1].timeline_end
    if abs(total - blueprint.total_duration) > 0.1:
        raise ValueError(f"Duration mismatch: {total} vs {blueprint.total_duration}")
```

### Fallback Strategies

**Reference Analysis Failure:**
```python
# Fallback to linear 2-second segments
blueprint = create_fallback_blueprint(duration)
```

**Clip Analysis Failure:**
```python
# Fallback to Medium/Dynamic for all clips
clip_meta = ClipMetadata(
    energy=EnergyLevel.MEDIUM,
    motion=MotionType.DYNAMIC,
    vibes=["General"]
)
```

**BPM Detection Failure:**
```python
# Fallback to 120 BPM
bpm = 120.0
```

---

## Future Optimizations

### Potential Improvements

1. **Segment Extraction Cache**
   - Cache extracted segments by (clip_path + start + duration)
   - Reuse across edits with same clips
   - Trade-off: Disk space vs speed

2. **Parallel FFmpeg Processing**
   - Extract segments in parallel (4-8 threads)
   - Potential 4x speedup
   - Trade-off: CPU usage

3. **GPU Acceleration**
   - Use NVENC for encoding
   - Potential 10x speedup
   - Trade-off: Requires NVIDIA GPU

4. **Incremental Matching**
   - Cache matching decisions
   - Only re-match changed segments
   - Trade-off: Complexity

5. **Streaming Concatenation**
   - Concatenate while extracting
   - Reduce total time
   - Trade-off: Error handling complexity

---

**Last Updated:** January 23, 2026  
**Version:** V7.0  
**Author:** MIMIC Development Team
