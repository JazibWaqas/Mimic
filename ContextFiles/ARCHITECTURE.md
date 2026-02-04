# MIMIC Architecture Documentation

**Version:** V12.1 - Content-First Authority  
**Last Updated:** February 4, 2026

This document provides a complete technical overview of the MIMIC system architecture, governed by the [Identity Contract](#ii-the-identity-contract-v121).

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
- **Stateful Continuity-Aware Scoring:** Balances energy fidelity, vibe alignment, and novelty with rolling context.
- **Narrative Budgeting:** Tracks "Emotional Capital" to prevent clip fatigue.
- **Beat Synchronization:** Snaps cuts to detected BPM for musical alignment (when audio detectable).
- **Subject Lock Enforcement:** Applies strong narrative bonus (≈ +50 initial, decaying on reuse), balanced against reuse bonuses.

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

**Last Updated:** February 4, 2026
**Version:** V12.1
