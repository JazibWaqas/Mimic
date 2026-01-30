# MIMIC Architecture Documentation

**Version:** V8.0 - The Closed-Loop Agentic System  
**Last Updated:** January 30, 2026

This document provides a complete technical overview of the MIMIC system architecture, detailing the transition from a linear workflow to an agentic "Plan -> Execute -> Reflect" loop.

---

## 🏗️ System Overview

### The Action Era Stack

MIMIC is built on a 6-stage multimodal pipeline designed to minimize creative friction while maximizing aesthetic fidelity.

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│            Vault Dashboard | Interactive Telemetry           │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────┴──────────────────────────────────┐
│                    Backend (FastAPI)                         │
│             Orchestrator Stage Machine (V8.0)                │
└─────┬──────────┬──────────┬──────────┬──────────┬───────────┘
      │          │          │          │          │
┌─────┴────┐ ┌──┴────┐ ┌───┴────┐ ┌──┴─────┐ ┌──┴─────┐
│  Brain   │ │Advisor│ │ Editor │ │Process │ │Reflect │
│ (Gemini) │ │(Plan) │ │(Match) │ │(FFmpeg)│ │(Audit) │
└──────────┘ └───────┘ └────────┘ └────────┘ └────────┘
```

### Module Responsibilities

- **`orchestrator.py`**: The central state machine. It manages the handoff between planning, assembly, and reflection.
- **`brain.py`**: Multimodal reasoning engine. Uses Gemini 1.5 Flash/Pro for deep semantic video analysis.
- **`advisor.py`** (Internal to Brain): Generates the creative strategy and evaluates library diversity before matching.
- **`editor.py`**: The deterministic "Grammar" engine. Implements tiered energy matching and novelty-bias selection.
- **`reflector.py`**:
    - **Responsibility:** Post-render judicial audit.
    - **Logic:** Gemini watches the final `.mp4` and judges it based on the original blueprint.
    - **Status:** Under architectural review.
- **`processors.py`**: The "Hands" of the system. Handles surgery-level FFmpeg cuts and librosa rhythmic analysis.

---

## 🌊 Core Stages (Plan -> Execute -> Reflect)

### Stage 4: The Advisor (Strategic Planning)
Before a single cut is made, the Advisor generates a `Master Strategy`. It analyzes the library against the blueprint demand (e.g., "Library has 30 High energy clips, but only 2 Low energy scenic clips") and adjusts matching weights to favor the scenic clips early in the edit.

### Stage 5: The Editor (Multi-Factor Scoring)
Matching is handled by a weighted scoring algorithm:
- **Novelty (+40 pts)**: Prioritizes clips that haven't been seen yet.
- **Vibe Density (+15 pts)**: Rewards clips with high semantic overlap (e.g., "Urban" vs. "Streetwear").
- **Visual Cooldown (-40 pts)**: Penalizes reuse of the same clip within 5 seconds of timeline space.

### Stage 6: The Reflector (Judicial Audit)
The newest addition to the MIMIC stack. The Reflector performs three functions:
1. **Fidelity Scoring**: Measures how well the final render matches the original Reference Blueprint.
2. **Rhythm Check**: Validates that "Peak" visual moments align with "Peak" audio moments.
3. **Editorial Suggestion**: If a segment is weak, it suggests exactly which clip from the library *should* have been used instead for V2.

---

## ⚡ Performance & Caching

MIMIC uses a three-tier hash-based cache to achieve 15-20s render times:
1. **Analysis Cache**: Stores Gemini results keyed by file hash + analysis parameters.
2. **Standardization Cache**: Stores `std_{hash}.mp4` files (1080x1920, 30fps) to avoid expensive re-encoding.
3. **Fingerprint Validation**: Reference analysis is cached only if the visual scene anchors (FFmpeg scene detection) match.

---

## 🔒 Security & Reliability
- **Multi-Key Rotation**: 28-key carousel managed by `api_key_manager.py` to prevent quota failures.
- **Timeline Integrity**: Mathematical continuity checks ensure zero-frame gaps or overlaps in the final EDL.
- **Reflective Fallbacks**: If Gemini fails to provide JSON, a deterministic heuristic blueprint is used.

---

**Last Updated:** January 30, 2026  
**Version:** V8.0  
**Status:** Hackathon Ready
