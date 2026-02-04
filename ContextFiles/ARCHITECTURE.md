# MIMIC Architecture Documentation

**Version:** V13.2 - Semantic Intelligence  
**Last Updated:** February 5, 2026

This document provides a complete technical overview of the MIMIC system architecture, governed by the [Identity Contract](#ii-the-identity-contract-v121), the [Pacing Authority Model](#iii-pacing-authority-model-v121), and the [Semantic Intelligence System](#iv-semantic-intelligence-v132).

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
- **`editor.py`**: The "Grammar" engine. Implements tiered energy matching, narrative budgeting, subject locking, and **semantic intelligence scoring (v13.2)**.
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

## 🕒 III. Pacing Authority Model (V12.1)

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
**Version:** V13.2
