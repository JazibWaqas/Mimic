# MIMIC System Intelligence Audit (Forensic Analysis)

This document is a forensic audit of the **actual data artifacts** generated and stored by the MIMIC system. It details exactly what the system "knows" at every stage of the pipeline, based on a direct inspection of the `data/` directory.

**Date of Audit**: 2026-02-07
**System Version**: v14.x (inferred from codebase)
**Data Schema Version**: 12.1 (Reference), 7.0 (Clips)

---

## 1. The Three Pillars of Intelligence

The system maintains three distinct types of intelligence, each with a specific schema and purpose.

### A. Reference Intelligence (The "Eyes")
*   **Location**: `data/cache/references/ref_{hash}_v{ver}.json`
*   **Purpose**: Deconstructs a reference video into a reusable *Blueprint*.
*   **Key Capabilities**: Precise timestamping of emotional arcs, text event extraction, and shot function analysis.

**Actual Data Example (from `ref_0bbf...json`):**
```json
{
  "narrative_message": "The visceral, high-stakes intensity of professional racing captured through rhythmic precision.",
  "text_events": [
    {
      "content": "NERVES",
      "start": 0.53,
      "end": 1.07,
      "sync_driver": "Lyric",
      "role": "Emphasis",
      "confidence": "High"
    }
  ],
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 0.24,
      "vibe": "Preparation",
      "shot_scale": "CU",
      "shot_function": "Establish",
      "continuity_hook": {
        "opens": "Driver movement",
        "resolves": "None",
        "type": "Physical-Action"
      }
    }
  ]
}
```
*   **Observation**: The system tracks *continuity hooks* (what opens/closes a shot), allowing for "invisible cuts" logic.

### B. Clip Intelligence (The "Library Mind")
*   **Location**: `data/cache/clips/clip_comprehensive_{hash}.json`
*   **Purpose**: Deep understanding of every second of raw footage.
*   **Key Capabilities**: Finding "Best Moments" relative to energy levels, identifying subjects, and preventing misuse (Safety fencing).

**Actual Data Example (from `clip_...89c.json`):**
```json
{
  "content_description": "A racing driver and a Formula 1 car being tested in a high-tech wind tunnel.",
  "energy": "High",
  "narrative_utility": ["Establishing", "Build", "Peak"],
  "best_moments": {
    "High": {
      "start": 10.0,
      "end": 13.0,
      "moment_role": "Peak",
      "reason": "Powerful wide shot of the car in the wind tunnel with high visual intensity."
    },
    "Low": {
      "start": 0.0,
      "end": 1.5,
      "moment_role": "Establishing",
      "reason": "Calm, focused shot of the driver establishing the human element."
    }
  },
  "best_for": ["Cinematic montages", "High-energy peaks"],
  "avoid_for": ["Calm reflective outros", "Intimate close-up moments"]
}
```
*   **Observation**: The system knows *exactly* which 3 seconds of a 2-minute clip are "Peak" versus "Establishing".

### C. Result Intelligence (The "Director's Brain")
*   **Location**: `data/results/{name}.json`
*   **Purpose**: The complete logic trace of *why* the edit was made, plus a post-mortem critique.
*   **Key Capabilities**: Decision stream reasoning, gap analysis, and specific actionable feedback.

**Actual Data Example (from `text_prompt_...v2.json`):**
```json
{
  "blueprint": {
    "text_prompt": "A warm, joyful, nostalgic childhood reel...",
    "plan_summary": "A breathy, intentional edit that prioritizes emotional resonance..."
  },
  "edl": {
    "decisions": [
      {
        "segment_id": 2,
        "clip_path": ".../clip_001.mp4",
        "reasoning": "🌟 Serving as a strategic 'Action' shot... visual content captures 'joy, playfulness'...",
        "vibe_match": true
      }
    ]
  },
  "critique": {
    "overall_score": 8.2,
    "monologue": "The transition from 'Action' shots... into the dense montage... creates a compelling emotional crescendo...",
    "star_performers": ["clip_001.mp4", "clip_010.mp4"],
    "dead_weight": ["clip_012.mp4"],
    "missing_ingredients": [
      "Macro close-ups of childhood artifacts (e.g., worn toys)...",
      "Visual metaphors for the passage of time..."
    ],
    "remake_actions": [
      {
        "type": "change_subject",
        "segment": "Intro",
        "suggestion": "Replace generic establishing shots with specific 'memory-trigger' objects..."
      }
    ]
  }
}
```

---

## 2. Unlocked Capabilities (Recommendations)

The system currently *generates* massive intelligence but displays only a fraction of it. Here is how we can operationalize this data for the user.

### A. The "Remake Video" Action Plan
**Current State**: The user sees the video and thinks "It's okay."
**Opportunity**: Use `critique.remake_actions` and `critique.missing_ingredients` to give the user a specific "ToDo List" to fix the video.

**Script / UI Concept:**
> **"This edit is an 8.2/10. Want a 10?"**
> *   **Action**: Your library lacks *Macro Close-ups*. Upload 2-3 shots of toys or photos to fix the "Intro" segment.
> *   **Action**: `clip_012.mp4` was used but labeled as "Dead Weight". Delete it?
> *   **Action**: The "Peak" segment needs a *breather*. Do you have a shot of a child sleeping or resting?

### B. "Why This Clip?" Inspector
**Current State**: User sees a clip in the timeline.
**Opportunity**: Hovering over a clip in the timeline should show the specific `edl.decision.reasoning` and the `clip_intelligence.best_moments` context.

**Script / UI Concept:**
> **Clip 3 (00:04 - 00:06)**
> *   **Role**: *Build-Up*
> *   **AI Reasoning**: "Chosen because it contains 'candid laughter' which matched the 'joyful' vibe requirement."
> *   **Alternative**: "Clip 015 was also a candidate but had lower resolution."

### C. Smart Library Filtering (Pre-Edit)
**Current State**: User dumps clips and hopes for the best.
**Opportunity**: Use `clip_intelligence.avoid_for` and `best_for` to warn the user *before* they generate.

**Script / UI Concept:**
> **"Wait! You are making a 'Reflective' edit..."**
> *   ⚠️ 12 of your clips are tagged `avoid_for: ["Calm reflective outros"]`.
> *   ✅ Only 3 clips are `best_for: ["Intimate close-up moments"]`.
> *   **Advice**: Your library is too high-energy for this prompt. Add more static/slow motion shots.

---

## 3. Data Format Summary

| Intelligence Type | Format | Primary Consumers | Status |
| :--- | :--- | :--- | :--- |
| **Blueprint** | Strict Struct (Pydantic) | Generator (Engine) | ✅ Robust |
| **Clip Metadata** | JSON + Text Tags | Matcher (Engine), Library UI | ✅ Robust |
| **EDL / Decisions** | List[Object] | Renenderer, Frontend Timeline | ✅ Robust |
| **Reflections** | Natural Language + Lists | Frontend "AI Insight" Box | ✅ **Underutilized** |
| **Comparisons** | *Missing* | *None* | ❌ **gap** |

### The Missing Piece: Relative Delta
We cite `overall_score: 8.2`, but we don't store the *delta* of previous runs.
*   **Recommendation**: When running `v2`, explicitly load `v1`'s JSON and generate a `progress_report`: "Energy flow improved by 15%, but color consistency dropped."

---

## 4. Conclusion
The MIMIC system is not just an editor; it is a **critique engine**. The data in `data/results/*.json` proves that the AI fully understands *why* an edit fails or succeeds.

**Immediate Win**: Expose `critique.missing_ingredients` and `critique.remake_actions` in the UI immediately. This transforms the tool from a "Random Video Generator" into a "Collaborative Director" that tells the user exactly how to help it succeed.
