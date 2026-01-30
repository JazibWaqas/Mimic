# MIMIC Architecture Documentation

**Version:** V9.0 - The Aesthetic Era  
**Last Updated:** January 31, 2026

This document provides a complete technical overview of the MIMIC system architecture, detailing the transition to a high-fidelity "Plan -> Execute -> Style -> Reflect" loop.

---

## 🏗️ System Overview

### The Aesthetic Era Stack

MIMIC is built on a 7-stage multimodal pipeline designed to transform raw footage into premium social content.

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│            Vault Dashboard | Interactive Telemetry           │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────┴──────────────────────────────────┐
│                    Backend (FastAPI)                         │
│             Orchestrator Stage Machine (V9.0)                │
└─────┬──────────┬──────────┬──────────┬──────────┬───────────┘
      │          │          │          │          │
┌─────┴────┐ ┌──┴────┐ ┌───┴────┐ ┌──┴─────┐ ┌──┴─────┐
│  Brain   │ │Advisor│ │ Editor │ │Stylist │ │Reflect │
│ (Gemini) │ │(Plan) │ │(Match) │ │(Aesth) │ │(Audit) │
└──────────┘ └───────┘ └────────┘ └────────┘ └────────┘
```

### Module Responsibilities

- **`orchestrator.py`**: The central state machine. Manages Adaptive Rhythm and the handoff between planning, styling, and reflection.
- **`brain.py`**: Multimodal reasoning engine. Uses Gemini 3 for semantic density and "Creative DNA" extraction.
- **`editor.py`**: The "Grammar" engine. Implements tiered energy matching and novelty-bias selection.
- **`stylist.py`**: 
    - **Responsibility:** Aesthetic Post-Processing.
    - **Logic:** Maps reference font styles to high-end typography (Serif/Sans) and applies cinematic color grading.
- **`reflector.py`**: Post-render judicial audit. Judges final video vs. original intent.
- **`processors.py`**: FFmpeg / Librosa operations for surgical cuts and rhythmic detection.

---

## 🌊 Core Stages (Plan -> Execute -> Style -> Reflect)

### Stage 4: High-Precision Editor (Adaptive Rhythm)
MIMIC V9.0 introduces **Adaptive Rhythm**. The editor no longer applies a blind 2-second cut rule. It distinguishes between:
1. **Cinematic Holds**: Respects long, emotional shots found in the reference.
2. **High-Energy Riffs**: Maintain rapid-fire beat-sync in intense sections.
3. **Beat-Snapping**: Every visual cut is mathematically aligned to the nearest musical anchor.

### Stage 5: The Stylist (Visual Excellence)
Before the final render, the Stylist module performs a "Style Transfer":
- **Typography**: Matches reference text placement and style (e.g., "Serif Center" -> Georgia).
- **Color Tone**: Adjusts tone and contrast (Warm/Cool/Neutral) to match the reference look.
- **Clean Aesthetic**: Ensures all overlays follow professional design principles (soft shadows, readable font scales).

---

## ⚡ Performance & Caching

MIMIC uses tiered hash-based caching for instant (~1s) re-runs:
1. **Cache Inheritance**: Allows the system to reuse expensive AI analysis even if pacing timestamps have slightly shifted.
2. **Analysis Cache**: Stores Gemini results keyed by file hash.
3. **Standardization Cache**: Stores `std_{hash}.mp4` files to avoid re-encoding overhead.

---

## 🔒 Security & Reliability
- **Multi-Key Rotation**: 28-key carousel to prevent API quota failures.
- **Timeline Integrity**: Mathematical continuity checks ensure zero-frame gaps.

---

**Last Updated:** January 31, 2026  
**Version:** V9.0  
**Status:** Ready for Demo
