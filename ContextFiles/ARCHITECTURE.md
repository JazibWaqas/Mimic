# MIMIC Architecture Documentation

**Version:** V11.0 - The Collaborative Director  
**Last Updated:** February 1, 2026

This document provides a complete technical overview of the MIMIC system architecture, detailing the full "Plan → Execute → Style → Reflect" loop with narrative intelligence.

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
- **`editor.py`**: The "Grammar" engine. Implements tiered energy matching, narrative budgeting, and subject locking.
- **`stylist.py`**: 
    - **Responsibility:** Aesthetic Post-Processing
    - **Logic:** Maps reference font styles to high-end typography and applies cinematic color grading
    - **Hardening:** Demo-safe punctuation handling, shell-safe rendering
- **`processors.py`**: FFmpeg / Librosa operations for surgical cuts, beat detection, and thumbnail generation.
- **`main.py`**: FastAPI server with file management, session tracking, and intelligence serving.

---

## 🌊 Core Stages (The 7-Stage Pipeline)

### Stage 1: Pre-Analysis (Processors)
- **Scene Detection:** FFmpeg identifies every visual cut in the reference
- **BPM Detection:** librosa extracts music tempo for beat-perfect cuts
- **Standardization:** Clips normalized to consistent format with hash-based caching

### Stage 2: Reference Analysis (Brain)
- **Multimodal Understanding:** Gemini analyzes energy, motion, vibes, and narrative arc
- **Segment Breakdown:** Each cut classified with energy level, arc stage, shot function
- **Text Overlay Extraction:** On-screen text captured for narrative intent interpretation
- **Music Structure:** Accent moments and phrase boundaries identified

### Stage 3: Clip Analysis (Brain)
- **Comprehensive Metadata:** Energy, motion, primary subject, narrative utility, emotional tone
- **Best Moments:** Pre-computed optimal segments for each energy level
- **Quality Scoring:** 1-5 scale for visual appeal and usefulness
- **Semantic Tagging:** "Best for" and "Avoid for" context classification

### Stage 4: Strategic Planning (Advisor)
- **Text Overlay Intent:** Highest authority signal for narrative direction
- **Arc Stage Guidance:** Editorial intent reasoning for each story stage
- **Library Assessment:** Strengths, editorial tradeoffs, constraint gaps
- **Narrative Subject Locking:** Primary subject enforcement (e.g., "People-Group" for friend videos)
- **Remake Strategy:** Forward-looking advice for Director's Cut quality

### Stage 5: Semantic Editing (Editor)
- **Weighted-Greedy Matching:** Balances energy fidelity, vibe alignment, and novelty
- **Narrative Budgeting:** Tracks "Emotional Capital" to prevent clip fatigue
- **Visual Cooldown:** Prevents back-to-back repetition with dynamic reuse gaps
- **Beat Synchronization:** Snaps cuts to detected BPM for musical alignment
- **Subject Lock Enforcement:** Applies +200 bonus for primary narrative subjects

### Stage 6: Aesthetic Styling (Stylist)
- **Typography Mapping:** Reference text style → High-end fonts (Georgia, Futura, etc.)
- **Color Grading:** Tone and contrast adjustment matching reference look
- **Text Rendering:** Demo-safe filtergraph construction with punctuation reconciliation
- **Visual Effects:** Film grain, light leaks, and other aesthetic treatments

### Stage 7: Post-Render Reflection (Orchestrator)
- **Editorial Debrief:** Library strengths, tradeoffs, and constraint gaps
- **Editorial Strategy:** One-sentence overall editing approach
- **Remake Strategy:** Specific advice for next iteration
- **Intelligence Report:** Complete JSON artifact with all reasoning

---

## 🎯 Key Algorithms

### Narrative Subject Locking (V11.0)
When text overlay demands specific content (e.g., "friends" → People-Group):
```python
if primary_narrative_subject == NarrativeSubject.PEOPLE_GROUP:
    if clip.primary_subject contains "People-Group":
        bonus += 200  # Strong anchor
    elif clip.primary_subject contains "People-Solo":
        bonus += 100  # Acceptable substitute
    else:
        bonus -= 100  # Narrative dilution
```

### Emotional Capital Management
Tracks clip usage to prevent "star" clip fatigue:
```python
if clip_usage_count[clip] == 0:
    bonus += 40  # Discovery bonus
elif clip_usage_count[clip] >= 3:
    bonus -= 30  # Overuse penalty
```

### Adaptive Rhythm
Distinguishes between cinematic holds and high-energy cuts:
```python
if segment.duration > 2.0 and segment.arc_stage in ["Intro", "Outro"]:
    # Respect cinematic hold
    use_full_duration = True
else:
    # Apply beat-sync constraints
    snap_to_nearest_beat()
```

---

## ⚡ Performance & Caching

MIMIC uses tiered hash-based caching for instant (~1s) re-runs:

### 1. Standardization Cache
- **Location:** `data/cache/standardized/`
- **Naming:** `std_{content_hash}.mp4`
- **Benefit:** Clips encoded once, reused forever

### 2. Analysis Cache
- **Location:** `data/cache/`
- **Files:** `ref_{hash}.json`, `clip_comprehensive_{hash}.json`
- **Benefit:** Gemini analysis cached per file content

### 3. Advisor Cache
- **Location:** `data/cache/`
- **Files:** `advisor_{ref_hash}_{library_hash}.json`
- **Benefit:** Strategic guidance reused for same ref+library combination

### 4. Thumbnail Cache
- **Location:** `data/cache/thumbnails/`
- **Naming:** `thumb_{type}_{hash}.jpg`
- **Benefit:** Multi-point sampling eliminates black frames

### Cache Inheritance
Allows reuse of expensive AI analysis even if pacing timestamps shift slightly. Keyed by content hash, not filename.

---

## 🔒 Security & Reliability

### Multi-Key Rotation
- **Capacity:** 28 API keys loaded from `.env`
- **Strategy:** Round-robin with automatic failover
- **Quota:** 560 requests/day total capacity
- **Graceful Degradation:** Advisor can fail without breaking pipeline

### Timeline Integrity
- **Validation:** Mathematical continuity checks ensure zero-frame gaps
- **Precision:** <0.001s tolerance for segment boundaries
- **Beat Sync:** <0.015s deviation from musical anchors

### Production Hardening (V11.0)
- **File Validation:** `.mp4` extension check on all uploads
- **Environment Variables:** `NEXT_PUBLIC_API_URL` for deployment flexibility
- **API Consistency:** Unified `path` field across all asset types
- **Error Handling:** Clear HTTP status codes and error messages

---

## 📊 Data Flow

```
1. User uploads reference + clips
   ↓
2. Backend standardizes clips (cached)
   ↓
3. Brain analyzes reference (cached)
   ↓
4. Brain analyzes clips (cached)
   ↓
5. Advisor generates strategic plan (cached)
   ↓
6. Editor matches clips to segments
   ↓
7. Stylist applies aesthetic treatments
   ↓
8. Processors render final video
   ↓
9. Orchestrator generates intelligence report
   ↓
10. Vault displays results + reasoning
```

---

## 🎨 Frontend Architecture

### Pages
- **`/` (Studio):** Upload interface with identity scanning and progress tracking
- **`/vault`:** Asset browser with search, thumbnails, and intelligence viewer
- **`/gallery`:** Clip library management
- **`/history`:** Session history and iteration tracking
- **`/compare`:** Side-by-side reference vs. output comparison

### Key Components
- **Asset Strip:** Horizontal thumbnail carousel for quick navigation
- **Intelligence Panel:** Editorial decisions, AI insights, recommended actions
- **Temporal Sequence Map:** Visual timeline with energy/vibe indicators
- **Search Bar:** Real-time filtering across all asset types

### State Management
- **React Hooks:** `useState`, `useEffect`, `useMemo` for local state
- **API Client:** Centralized in `lib/api.ts` with caching
- **WebSocket:** Real-time progress updates during generation

---

## 🔍 Architectural Decisions

### Why In-Memory Sessions?
> "Session state is ephemeral by design. All durable artifacts (videos, JSON reports, thumbnails) are persisted to disk with content-based hashing. Session recovery happens via filesystem scan, not memory."

### Why No Locking?
> "MIMIC prioritizes deterministic artifact reconstruction over live session durability. For a single-user creative workflow, explicit locking adds complexity without improving editorial correctness."

### Why Graceful Advisor Degradation?
> "The Advisor is a strategic enhancement, not a critical dependency. If it fails, the base matcher still produces coherent edits using energy/motion matching."

---

## 📈 Performance Metrics

| Operation | Time | Cache Hit |
|-----------|------|-----------|
| Clip Standardization | 2-3s each | 100% on repeat |
| Reference Analysis | 5-8s | 100% on repeat |
| Clip Analysis | 3-5s each | 100% on repeat |
| Advisor Planning | 4-6s | 100% on repeat |
| Matching Algorithm | 1-2s | N/A |
| FFmpeg Rendering | 5-10s | N/A |
| **Total (30-seg edit)** | **15-20s** | **With cache** |
| **Total (first run)** | **2-3 min** | **No cache** |

---

## 🛠️ Technology Stack

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Google Gemini API** - Multimodal AI
- **FFmpeg** - Video processing
- **librosa** - Audio analysis
- **Pillow** - Thumbnail generation

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Sonner** - Toast notifications

---

**Last Updated:** February 1, 2026  
**Version:** V11.0  
**Status:** Production Ready
