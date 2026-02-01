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
- **`stylist.py`**: Aesthetic post-processing. Maps reference font styles to high-end typography and applies cinematic color grading.
- **`reflector.py`**: The "Director's Voice." Performs post-render AI reflection to judge narrative cohesion and generate a Director's Monologue.
- **`processors.py`**: FFmpeg / Librosa operations for surgical cuts, beat detection, and thumbnail generation.
- **`main.py`**: FastAPI server with file management, session tracking, and intelligence serving.

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
- **Weighted-Greedy Matching:** Balances energy fidelity, vibe alignment, and novelty.
- **Narrative Budgeting:** Tracks "Emotional Capital" to prevent clip fatigue.
- **Beat Synchronization:** Snaps cuts to detected BPM for musical alignment.
- **Subject Lock Enforcement:** Applies +200 bonus for primary narrative subjects.

### Stage 6: Aesthetic Styling (Stylist)
- **Typography Mapping:** Reference text style → High-end fonts (Georgia, Futura, etc.).
- **Color Grading:** Tone and contrast adjustment matching reference look.
- **Text Rendering:** Demo-safe filtergraph construction with punctuation reconciliation.

### Stage 7: Post-Render Reflection (Reflector)
- **Director's Monologue:** A 3-4 sentence AI reflection on the edit's "soul" and story transfer.
- **Hierarchy of Judgment:** Prioritizes Narrative Adherence > Semantic Flow > Rhythmic Precision.
- **Remake Checklist:** Concrete, filmable shot suggestions to reach a 10/10 score.
- **Critique Caching:** Hash-based caching for instant Director notes in the Vault.

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
- **Benefit:** Clips encoded once, reused forever.

### 2. Analysis Cache
- **Location:** `data/cache/`
- **Files:** `ref_{hash}.json`, `clip_comprehensive_{hash}.json`
- **Benefit:** Gemini analysis cached per file content.

### 3. Critique Cache (New)
- **Location:** `data/cache/`
- **Files:** `critique_{edl_hash}.json`
- **Benefit:** Director notes appear instantly in the Vault for known edits.

---

## 🔒 Security & Reliability

### Multi-Key Rotation
- **Capacity:** 28 API keys loaded from `.env`.
- **Strategy:** Round-robin with automatic failover.
- **Quota:** 560 requests/day total capacity.

### Production Hardening (V11.0)
- **File Validation:** `.mp4` extension check on all uploads.
- **Environment Variables:** `NEXT_PUBLIC_API_URL` for deployment flexibility.
- **API Consistency:** Unified `path` field across all asset types.

---

## 🎨 Frontend Architecture

### Pages
- **`/` (Studio):** Upload interface with identity scanning and progress tracking.
- **`/vault`:** Asset browser with the new **Director's Review** panel.
- **`/gallery`:** Clip library management.
- **`/history`:** Session history and iteration tracking.

### Key Components
- **Director's Review Panel:** Displays Monologue, Score, and Remake Checklist.
- **Editorial Ledger:** Real-time list of edit decisions with AI reasoning.
- **Temporal Sequence Map:** Visual timeline with energy/vibe indicators.

---

**Last Updated:** February 1, 2026  
**Version:** V11.0  
**Status:** Production Ready
