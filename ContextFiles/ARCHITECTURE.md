# MIMIC Architecture Documentation

**Version:** V14.1 - Advisor-Driven Contextual Selection  
**Last Updated:** February 5, 2026

This document provides a complete technical overview of the MIMIC system architecture, governed by the [Identity Contract](#ii-the-identity-contract-v121), the [Pacing Authority Model](#iii-pacing-authority-model-v121), the [Semantic Intelligence System](#iv-semantic-intelligence-v132), and the [Contextual Moment Selection System](#v-contextual-moment-selection-v140).

---

## 🏗️ System Overview

### The Collaborative Director Stack

MIMIC is built on a 7-stage multimodal pipeline designed to transform raw footage into premium social content with editorial intelligence.

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Next.js 14)                      │
│         Vault Dashboard | Real-time Intelligence             │
│         Studio | Gallery | History | Compare                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────┴──────────────────────────────────┐
│                    Backend (FastAPI)                         │
│           Orchestrator Pipeline (7 Stages)                   │
└─────┬──────────┬──────────┬──────────┬──────────┬───────────┘
      │          │          │          │          │
┌─────┴────┐ ┌──┴────┐ ┌───┴────┐ ┌──┴─────┐ ┌──┴──────┐
│  Brain   │ │Advisor│ │ Editor │ │Stylist │ │Reflector│
│ (Gemini) │ │(Plan) │ │(Match) │ │(Aesth) │ │(Critique)│
└──────────┘ └───────┘ └────────┘ └────────┘ └─────────┘
```

### Module Responsibilities

- **`orchestrator.py`**: The central state machine. Manages the 7-stage pipeline with adaptive rhythm and narrative intelligence.
- **`brain.py`**: Multimodal reasoning engine. Uses Gemini for semantic analysis and "Creative DNA" extraction.
- **`gemini_advisor.py`**: Strategic planning layer. Generates editorial guidance, assesses library gaps, and provides remake strategies.
- **`gemini_moment_prompt.py`**: Contextual moment selection prompt with Three Hard Rules (v14.1).
- **`moment_selector.py`**: Contextual moment selection engine - builds candidates, scores them, calls Advisor.
- **`editor.py`**: The "Grammar" engine. Implements tiered energy matching, narrative budgeting, subject locking, **CDE-aware subdivision (v13.3)**, **semantic intelligence scoring (v13.2)**, and **Advisor-driven moment selection (v14.0)**.
- **`stylist.py`**: Aesthetic post-processing. Maps reference font styles to high-end typography and applies cinematic color grading.
- **`reflector.py`**: The "Director's Voice." Performs post-render AI reflection to judge narrative cohesion and generate a Director's Monologue.
- **`processors.py`**: FFmpeg / Librosa operations for surgical cuts, beat detection, and thumbnail generation.
- **`main.py`**: FastAPI server with file management, session tracking, and intelligence serving.

---

## IV. Semantic Intelligence (V13.2)

### The Problem: Limited Reel-Type Vocabulary
Prior versions had limited semantic understanding for specific reel types like nostalgia, childhood, and celebration content.

### The Solution: Expanded Semantic Bridges

#### 1. SEMANTIC_MAP Categories
The editor now recognizes 12 vibe categories:

| Category | Keywords | Reel Types |
|----------|----------|------------|
| `nature` | outdoors, scenic, landscape, forest, beach, sunset | Travel, Scenic |
| `urban` | city, street, architecture, lights, downtown | Urban, Lifestyle |
| `travel` | adventure, road, explore, journey, destination | Travel, Trip |
| `friends` | social, laughing, group, candid, bonding | Friends, Social |
| `action` | fast, sport, intense, adrenaline, power | Sports, Action |
| `calm` | peaceful, sunset, aesthetic, serene, gentle | Peaceful, Reflection |
| `nostalgia` | memories, childhood, family, vintage, throwback | My Year, Throwback |
| `celebration` | party, dance, cheers, birthday, wedding | Birthday, Wedding |
| `intimate` | close, embrace, love, tender, romantic | Couple, Personal |
| `childhood` | playing, laughter, discovery, wonder, innocence | Pure Nostalgia |
| `cinematic` | epic, dramatic, hero, iconic, majestic | Professional |
| `transition` | walking, driving, flying, moving, flowing | B-roll, Transitions |

#### 2. Emotional Tone → Vibe Bridge
Clip emotional tones (from Brain analysis) are mapped to segment vibes:

```python
EMOTIONAL_TONE_BRIDGE = {
    "nostalgic": ["memories", "throwback", "warmth", "childhood", "home"],
    "joyful": ["friends", "celebration", "fun", "happy", "party"],
    "energetic": ["action", "party", "dance", "adrenaline", "power"],
    "peaceful": ["calm", "nature", "sunset", "escape", "serene"],
    "adventurous": ["travel", "explore", "journey", "destination"],
    "intimate": ["close", "love", "personal", "romantic"],
    "dramatic": ["cinematic", "epic", "hero", "iconic", "majestic"]
}
```

**Example:** A clip tagged `"emotional_tone": ["Nostalgic"]` will score +12 points when matching a segment with `vibe: "memories"`.

#### 3. Arc-Stage Tone Affinity
Certain tones naturally fit certain arc stages:

| Arc Stage | Preferred Tones | Points |
|-----------|-----------------|--------|
| Intro | peaceful, nostalgic, adventurous | +8 |
| Build-up | energetic, adventurous, dramatic | +8 |
| Peak | joyful, energetic, dramatic | +8 |
| Outro | nostalgic, peaceful, intimate | +8 |

#### 4. Complete Scoring Breakdown

| Factor | Points | Condition |
|--------|--------|----------|
| Advisor Primary Carrier | +60 | Clip in `exemplar_clips` |
| Vibe Direct Match | +40 | Exact vibe match |
| Vibe Semantic Bridge | +30 | Vehicle→Speed mapping |
| Narrative Anchor | +25 | Matches primary subject |
| Shot Function Match | +25 | Establish→Establishing |
| Subject Consistency | +20 | Friends→People-Group |
| Scale Continuity | +15 | Wide→Establishing |
| Tone→Vibe Bridge | +12 | Nostalgic→memories |
| Scale Variety | +10 | Alternating scales |
| Arc-Stage Tone | +8 | Outro+nostalgic |
| Intent Dilution | -50 | Wrong subject for stage |
| Repeat Penalty | -20 | Recently used clip |

### Reel-Type Coverage Status

| Reel Type | Coverage | Key Features |
|-----------|----------|-------------|
| Cinematic | ✅ Excellent | cinematic bridge, scale continuity |
| Friends/Celebration | ✅ Excellent | celebration + joyful tones |
| Travel/Trip | ✅ Excellent | adventurous + travel vocabulary |
| Nostalgia/Childhood | ✅ Excellent | nostalgia + childhood semantics |
| My Year | ✅ Good | nostalgia + transition support |

---

## 🌊 Core Stages (The 7-Stage Pipeline)

### Stage 1: Pre-Analysis (Processors)
- **Scene Detection:** FFmpeg identifies every visual cut in the reference.
- **BPM Detection:** librosa extracts music tempo for beat-perfect cuts.
- **Standardization:** Clips normalized to consistent format with hash-based caching.

### Stage 2: Reference Analysis (Brain)
- **Multimodal Understanding:** Gemini analyzes energy, motion, vibes, and narrative arc.
- **Segment Breakdown:** Each cut classified with energy level, arc stage, shot function.
- **Text Overlay Extraction:** On-screen text captured for narrative intent interpretation.

### Stage 3: Clip Analysis (Brain)
- **Comprehensive Metadata:** Energy, motion, primary subject, narrative utility, emotional tone.
- **Best Moments:** Pre-computed optimal segments for each energy level.
- **Quality Scoring:** 1-5 scale for visual appeal and usefulness.

### Stage 4: Strategic Planning (Advisor)
- **Text Overlay Intent:** Highest authority signal for narrative direction.
- **Arc Stage Guidance:** Editorial intent reasoning for each story stage.
- **Library Assessment:** Strengths, editorial tradeoffs, constraint gaps.
- **Narrative Subject Locking:** Primary subject enforcement (e.g., "People-Group" for friend videos).

### Stage 5: Semantic Editing (Editor)
- **Stateful Continuity-Aware Scoring:** Balances energy fidelity, vibe alignment, and novelty with rolling context.
- **Narrative Budgeting:** Tracks "Emotional Capital" to prevent clip fatigue.
- **Pacing Authority (V12.1):** Implements "Director over Metronome" logic.
    - **Sacred Cuts:** Prevents subdivision of segments derived from real reference camera cuts.
    - **Inferred Sync:** Automatically relaxes beat-snapping if audio was muted during reference analysis (`audio_confidence == "Inferred"`).
    - **Narrative Jitter:** Uses logic-driven durations with human-like variation (±10%) instead of rigid beat math.
- **Subject Lock Enforcement:** Applies strong narrative bonus (~+50), balanced against reuse bonuses.

### Stage 6: Aesthetic Styling (Stylist)
- **Typography Mapping:** Reference text style → High-end fonts (Georgia, Futura, etc.).
- **Color Grading:** Applies safe, demo-grade color transforms aligned to reference tone.
- **Text Rendering:** Demo-safe filtergraph construction with punctuation reconciliation.

### Stage 7: Post-Render Reflection (Reflector)
- **Director's Monologue:** A 3-4 sentence AI reflection on the edit's "soul" and story transfer.
- **Hierarchy of Judgment:** Prioritizes Narrative Adherence > Semantic Flow > Rhythmic Precision.
- **Remake Checklist:** Concrete, filmable shot suggestions to reach a 10/10 score.
- **Critique Caching:** Hash-based caching for instant Director notes in the Vault.

---

## 🆔 II. The Identity Contract (V12.1)

> **All processing decisions must be keyed exclusively on the 32-character MD5 content hash.**
> **No other signal (mtime, path, filename, thumbnail existence) may trigger work.**

### 1. Identity Definition
**Authority:** The **32-character MD5 Content Hash** is the sole source of truth.
- **Logic:** `md5(full file content)` → 32-character hex digest. Fingerprint shortcuts (mtime + size) are used only to skip re-hashing, never as identity.
- **Benefit:** Renames, moves, and duplicate files are instantly resolved to the same Identity.
- **Implementation:** Global `get_file_hash()` utility in `utils.py`.
- **Registry:** `hash_registry.json` is a *read-optimization* only. It does not define identity.

### 2. The Artifact Contracts

#### A. Identity Thumbnails (Content-First)
- **Naming:** `thumb_{hash}.jpg` (Strict 32-char)
- **Role:** Visual cache for the *file itself*.
- **Invariant:** One per unique content hash. Multiple files, paths, or roles referencing the same content share a single thumbnail.

#### B. UX Clip Thumbnails (Derived)
- **Naming:** `clip_thumb_{hash}_{start}_{end}.jpg` (Optional)
- **Role:** Visual cache for a *segment of time*.
- **Invariant:** These are purely UX artifacts for the Vault/Timeline. They must **never** occupy the `thumb_{hash}.jpg` namespace and are generated lazily.

#### C. Standardized Clips
- **Naming:** `data/cache/standardized/std_{hash}.mp4`
- **Role:** Persistent render cache.
- **Invariant:** Orchestrator must always check this global path before running FFmpeg.

---

## ⚡ Performance & Caching

MIMIC uses tiered hash-based caching for instant (~1s) re-runs:

### 1. Standardization Cache
- **Location:** `data/cache/standardized/`
- **Naming:** `std_{hash}.mp4` (32-char MD5)
- **Benefit:** Clips encoded once, reused forever. Orchestrator checks here *before* FFmpeg.

### 2. Analysis Cache
- **Location:** `data/cache/`
- **Files:** `ref_{hash}.json`, `clip_comprehensive_{hash}.json`
- **Benefit:** Gemini analysis cached per file content.

### 3. critique Cache
- **Location:** `data/cache/`
- **Files:** `critique_{edl_hash}.json`
- **Benefit:** Director notes appear instantly in the Vault for known edits.

### 4. Clip Thumbnails (UX Cache)
- **Location:** `data/cache/clip_thumbnails/`
- **Naming:** `clip_thumb_{hash}_{start}_{end}.jpg`
- **Benefit:** Lazily generated visuals for specific time segments in the Vault/Timeline.

---

## 🎯 Key Algorithms

### Narrative Subject Locking (V11.0)
When text overlay demands specific content (e.g., "friends" → People-Group):
```python
if primary_narrative_subject == NarrativeSubject.PEOPLE_GROUP:
    if clip.primary_subject contains "People-Group":
        bonus += 50  # Strong anchor
    elif clip.primary_subject contains "People-Solo":
        bonus += 25  # Acceptable substitute
    else:
        bonus -= 50  # Narrative dilution
```

### Emotional Capital Management
Tracks clip usage to prevent "star" clip fatigue:
```python
if clip_usage_count[clip] == 0:
    bonus += 40  # Discovery bonus
elif clip_usage_count[clip] >= 3:
    bonus -= 30  # Overuse penalty
```

---

## 📊 Project Status & Health (V12.1)

**Status:** 💎 **PRODUCTION READY / DEMO GRADE**

| Module | Status | Confidence |
| :--- | :--- | :--- |
| **Stage 1: Pre-Analysis** | ✅ COMPLETE | 100% |
| **Stage 2: Multimodal Brain** | ✅ COMPLETE | 98% |
| **Stage 3: Strategic Advisor** | ✅ COMPLETE | 98% |
| **Stage 4: Semantic Editor** | ✅ COMPLETE | 100% |
| **Stage 5: Aesthetic Stylist** | ✅ COMPLETE | 98% |
| **Stage 6: Director Reflector** | ✅ COMPLETE | 95% |
| **The Vault (Unified UI)** | ✅ COMPLETE | 98% |

### Recent Achievements
- ✅ **High Diversity Bias** - Aggressive freshness and cooldown logic minimizes repetition, allowing zero-repeat edits when library capacity permits.
- ✅ **Narrative Subject Locking** - Primary subject enforcement (~+50 bonus)
- ✅ **Director's Critique** - Automated 1-10 scoring and "Missing Ingredients" checklist
- ✅ **Idempotent Indexing** - Zero re-processing of known assets with strict MD5 contract

---

## 🎵 IV. Cut Density Expectation (V13.3)

### The Problem: Mechanical Subdivision
Prior versions could over-cut or under-cut segments because they lacked awareness of the reference video's musical cadence. The system needed to match not just *what* content was in each segment, but *how rhythmically dense* the cuts should feel.

### The Solution: CDE
**Cut Density Expectation (CDE)** is a derived signal per reference segment that influences subdivision decisions based on musical context.

**CDE Categories:**
| CDE | Trigger Conditions | Editor Bias |
|-----|-------------------|-------------|
| **Sparse** | `expected_hold == Long` OR beat_density < 0.08/s | Strongly prefer single usable window, resist subdivision |
| **Moderate** | Normal hold + moderate beats OR cut_origin == visual | Allow 1-2 cuts if needed |
| **Dense** | `expected_hold == Short` OR beat_density > 0.20/s OR peak_density context | Encourage subdivision even if visuals could hold |

**Derivation (No New AI Calls):**
- `segment.duration` - Base timing
- `cut_origin` - Visual cuts are sacred, beat cuts more flexible
- `expected_hold` - Long = sparse, Short = dense
- `beat_confidence` - Only trust beats if "Observed"
- Local beat density from reference audio

**Implementation:**
```python
def calculate_cde(segment, beat_grid, blueprint, mode):
    beats_in_segment = [b for b in beat_grid if segment.start <= b < segment.end]
    beat_density = len(beats_in_segment) / segment.duration
    
    if expected_hold == "Long":
        return "Sparse"
    elif expected_hold == "Short":
        return "Dense"
    elif beat_density > 0.20:
        return "Dense"
    elif beat_density < 0.08:
        return "Sparse"
    else:
        return "Moderate"
```

**Hard Rules:**
1. CDE is **advisory only** - never overrides segment boundaries
2. Beats remain **snap points**, never authorities
3. No looping, no stretching, no content generation
4. Only affects `max_cuts_per_segment` ceiling

---

## 🧠 V. Contextual Moment Selection (V14.0 - V14.1)

### The Problem: Clip-Centric Best Moments
The original best-moment logic assumed each clip has **one canonical moment per energy level**. This was limiting because:
- A 60s clip with 10 valid micro-moments was treated as having one "best" moment
- That moment was reused even when a *different part of the same clip* would fit the current reference segment better
- Selection was not conditioned on music cadence, narrative flow, or arc stage intent

### The Solution: Reference-Conditioned Moment Selection
**Best moments are now candidates, not absolute truth.** The Advisor selects which moment fits a specific reference segment based on:
- Reference segment identity (vibe, energy, arc stage)
- Music cadence and phrase boundaries
- Narrative flow from previous decisions
- Cut density expectation (CDE)

### The Architectural Shift

**Before (Clip-Centric):**
```
Clip A → "Best High Moment" (0:15-0:20)
Clip B → "Best High Moment" (0:05-0:12)
Editor picks between clips, not moments within clips
```

**After (Reference-Centric):**
```
Segment 1 (Peak, Dense CDE) → Advisor picks moment 0:15-0:18 from Clip A
Segment 2 (Build-up, Sparse CDE) → Advisor picks moment 0:40-0:52 from Clip A (same clip!)
Segment 3 (Intro, Long hold) → Advisor picks moment 0:02-0:08 from Clip B
```

The Advisor now compares **multiple moments within the same clip** and reasons about which fits the specific reference segment.

### New Data Structures

#### `MomentCandidate`
```python
class MomentCandidate(BaseModel):
    clip_filename: str
    moment_energy_level: str  # "High", "Medium", "Low"
    start: float
    end: float
    duration: float
    moment_role: str
    stable_moment: bool
    reason: str
    # Contextual scoring (filled by editor, used by Advisor)
    semantic_score: float  # How well content matches segment vibe
    musical_alignment: float  # Alignment with beat/phrase (0-1)
    narrative_continuity: float  # Flow from previous decisions (0-1)
```

#### `ContextualMomentSelection`
```python
class ContextualMomentSelection(BaseModel):
    segment_id: int
    selection: MomentCandidate
    reasoning: str  # Why this moment for THIS segment
    confidence: str  # High, Medium, or Low
    alternatives_considered: List[Dict[str, Any]]
    continuity_notes: str  # How this flows from previous cuts
```

#### `SegmentMomentPlan`
```python
class SegmentMomentPlan(BaseModel):
    segment_id: int
    moments: List[MomentCandidate]  # Ordered sequence to fill segment duration
    total_duration: float
    is_single_moment: bool  # True if one moment fills the segment
    chaining_reason: str | None  # Why multiple moments were needed
```

### New Components

**`moment_selector.py`** - The Contextual Moment Selection Engine
- `build_moment_candidates()` - Exposes ALL moments (High/Medium/Low) from ALL clips
- `select_moment_with_advisor()` - Calls Gemini with contextual prompt
- `plan_segment_moments()` - Chains moments to fill segment duration completely
- Pre-calculates semantic, musical, and continuity scores for each candidate

**`gemini_moment_prompt.py`** - The Advisor Prompt (v14.1 Production-Safe)
Contains the "Three Hard Rules" to prevent over-editing:

### The Three Hard Rules (v14.1)

**Rule 1: Restraint Rule**
> Prefer the fewest moments necessary to satisfy the segment. Multiple moments are a last resort, not a default. Only chain moments if no single stable moment can cover the duration, OR musical cadence (CDE = Dense) explicitly demands rhythmic contrast.

**Rule 2: Hold Authority Rule**
> For visual-origin segments with "Long" expected holds, stability outweighs semantic richness. A single stable moment with acceptable (not perfect) semantic alignment is preferred over multiple "perfect" micro-moments.

**Rule 3: Music Precedence Rule**
> Musical phrasing dominates beat accents. Respect phrase boundaries before micro-rhythmic cuts unless CDE = Dense AND cut_origin = beat.

### Integration in Editor

The editor now checks for Advisor moment plans before falling back to CDE-based matching:

```python
# v14.0: ADVISOR-DRIVEN CONTEXTUAL MOMENT SELECTION
if advisor_hints and hasattr(advisor_hints, 'segment_moment_plans'):
    plan_key = str(segment.id)
    if plan_key in advisor_hints.segment_moment_plans:
        advisor_moment_plan = advisor_hints.segment_moment_plans[plan_key]
        
        # Execute Advisor's moments directly
        for moment in advisor_moment_plan.moments:
            decision = EditDecision(...)
            decisions.append(decision)
            
        continue  # Skip legacy matching for this segment

# Fallback: v13.3 CDE-based matching
```

### Role Separation

**Advisor = Editor (Makes contextual decisions):**
- Compares multiple moments within the same clip
- Reasons about which moment fits the current reference segment
- Considers music cadence, narrative flow, arc stage intent
- Suggests, never controls timing directly

**Matcher = Executor (Enforces contracts deterministically):**
- Applies Advisor's moment selections
- Enforces segment timing contracts (immutable boundaries)
- Handles moment chaining if duration requires it
- Updates clip usage tracking and continuity state

### Key Design Decisions

**Why Reference-Centric Over Clip-Centric?**
- **Problem:** Clip-centric logic treats best moments as absolute truth
- **Solution:** Reference-centric logic treats best moments as candidates
- **Benefit:** Same clip can contribute different moments to different segments based on context
- **Trade-off:** More complex, requires Advisor reasoning per segment

**Why Three Hard Rules?**
- **Problem:** Advisor could over-edit by chaining "perfect" micro-moments
- **Solution:** Explicit constraints that prioritize restraint
- **Benefit:** Prevents 70% of over-editing failure modes
- **Implementation:** Hard-coded in prompt, not post-hoc filtering

**Why Qualitative Scoring (Strong/Acceptable/Poor)?**
- **Problem:** 0-10 numerical scoring encourages pseudo-precision
- **Solution:** Ordered preference reasoning (Strong/Acceptable/Poor)
- **Benefit:** Reduces hallucinated precision, clearer decision boundaries
- **Implementation:** Prompt instructs qualitative assessment, not numeric

---

## 🕒 VI. Pacing Authority Model (V12.1)

MIMIC V12.1 solves the "Mechanical Metronome" problem by inverting the authority of the music grid.

### 1. The Conflict: Director vs. Metronome
- **Old Way:** Beats dictated duration. Result: Machine-gun pacing and emotional exhaustion.
- **New Way (V12.1):** Narrative intent dictates duration; Beats provide snapping.

### 2. Implementation Rules
1. **Sacred Cuts:** If a segment start-time originates from a visual cut (`cut_origin == "visual"`), subdivision is FORBIDDEN.
2. **Emotional Registration:** Minimum holds are strictly enforced (1.2s for Peak, 2.5s for Normal).
3. **Audio Confidence:** If audio is muted during analysis, the system marks rhythm as `Inferred` and disables strict beat-snapping to prevent rhythmic "guessing" errors.
4. **Contextual Scaling:** AI analysis requests "Best Moments" relative to energy:
   - Low: 3-6s
   - High: 1.2-3s

---

**Last Updated:** February 5, 2026
**Version:** V14.1
