"""
Blueprint Generator: Text-to-Edit-DNA system (v14.7 Prompt Mode).

Allows users to describe an edit in natural language and generates a full StyleBlueprint.
This bypasses the need for a reference video while maintaining the same deterministic execution.

v14.7 PROMPT MODE ENHANCEMENTS:
- Nostalgia-first design: Fewer cuts, longer holds, emotional pacing
- Explicit CDE (Cut Density Expectation) guidance per segment
- Explicit cut_origin for Editor compatibility
- Optional BPM awareness for music-synchronized phrasing
- Fallback blueprint for graceful degradation
"""

import json
import hashlib
from typing import Optional
from pathlib import Path
from models import StyleBlueprint, EnergyLevel, MotionType, Segment
from engine.brain import initialize_gemini, _parse_json_response, GeminiConfig, rate_limiter, _handle_rate_limit_error

# ============================================================================
# PROMPT MODE GENERATOR PROMPT (v14.7 Nostalgia-First Design)
# ============================================================================
# This prompt is designed for emotional, memory-driven edits.
# It produces StyleBlueprints optimized for nostalgia, personal moments, and
# cinematic storytelling with intentional rhythm (not hyper-fragmentation).
# ============================================================================

GENERATOR_PROMPT = """
You are a world-class Creative Director and Edit Producer specializing in EMOTIONAL, MEMORY-DRIVEN video edits.

Your task is to generate a 'Style Blueprint' (Editing DNA) based on a user's text description.
This blueprint will be used by an automated engine to assemble raw clips into a cohesive narrative.

USER DESCRIPTION:
{user_prompt}

TARGET DURATION: {target_duration} seconds
{music_context}

---

## NOSTALGIA-FIRST PHILOSOPHY (CRITICAL)

You are designing an edit for PERSONAL, EMOTIONAL footage. This is NOT a fast-paced commercial or action reel.

NOSTALGIA RULES:
- FEWER cuts, not more. Let moments breathe.
- LONGER holds on meaningful content.
- GENTLE build-up — don't rush to the peak.
- EMOTIONAL peak near music swell, not arbitrary middle.
- SOFT landing outro — never abrupt endings.
- Preference for: Peace, Joy, Reflection, Warmth, Memory.
- AVOID hyper-fragmentation unless explicitly requested.

NOSTALGIA ≠ SLOW. Nostalgia = INTENTIONAL RHYTHM.

---

## AUTHORSHIP BOUNDARY

You define EDITORIAL INTENT AND STRUCTURE, not execution guarantees.
- Segment boundaries represent intended emotional pacing.
- The engine may adjust cuts to match the beat grid and clip availability.
- Specify PREFERENCES for shot types, not mandates.
- Focus on the "soul" of the segment, not micro-details.

---

## MUSIC-AWARE PHRASING
{music_guidance}

---

## ARC PLAN REQUIREMENTS

Design a clear 4-stage emotional arc:

| Stage    | Duration  | Purpose                              | Energy   | CDE      |
|----------|-----------|--------------------------------------|----------|----------|
| Intro    | 15-25%    | Set the scene, establish tone        | Low      | Sparse   |
| Build-up | 25-35%    | Escalate anticipation gently         | Medium   | Moderate |
| Peak     | 25-35%    | Emotional climax, payoff             | High/Med | Moderate |
| Outro    | 15-25%    | Resolution, soft landing             | Low      | Sparse   |

---

## SEGMENT SPECIFICATION

For EACH segment, you MUST specify:

1. **id**: Sequential integer (1, 2, 3, ...)
2. **start / end / duration**: Continuous, no gaps. Sum = target_duration exactly.
3. **energy**: Low | Medium | High
4. **motion**: Static | Dynamic
5. **vibe**: 1-3 emotional keywords (e.g., "warmth, nostalgia, joy")
6. **reasoning**: 1-2 sentences explaining WHY this segment exists
7. **arc_stage**: Intro | Build-up | Peak | Outro
8. **shot_scale**: Wide | Medium | Close (advisory only)
9. **shot_function**: Establish | Action | Reaction | Detail | Transition | Release
10. **expected_hold**: Short | Normal | Long
11. **cut_origin**: "visual" (narrative-driven) | "beat" (music-driven)
12. **cde**: "Sparse" | "Moderate" | "Dense" (Cut Density Expectation)
13. **emotional_guidance**: What should the viewer FEEL? (e.g., "peaceful reflection")

---

## CDE (CUT DENSITY EXPECTATION) GUIDELINES

| CDE      | Meaning                                           | Use Case                    |
|----------|---------------------------------------------------|-----------------------------|
| Sparse   | 1 clip per segment preferred. Let it breathe.    | Intro, Outro, Emotional     |
| Moderate | 1-2 cuts allowed if needed. Natural pacing.      | Build-up, Standard scenes   |
| Dense    | Multiple quick cuts permitted. Energy-driven.    | Action peaks, celebrations  |

FOR NOSTALGIA EDITS:
- Default to "Sparse" for Intro and Outro.
- Use "Moderate" for Build-up.
- Use "Moderate" (not Dense) even for Peak unless user requests intensity.

---

## CRITICAL RULES

1. Total duration must be EXACTLY {target_duration} seconds.
2. Segments must be CONTINUOUS (Segment 2 start = Segment 1 end).
3. Prefer FEWER segments with LONGER holds over many short cuts.
4. For a 20-30 second edit, aim for 4-6 segments (not 10+).
5. Use professional editorial reasoning for every decision.
6. If user description conflicts with standard pacing, prioritize EMOTIONAL INTENT.
7. **HARD LIMIT**: If target_duration ≤ 30 seconds, NEVER produce more than 6 segments.
8. **DURATION FIX**: If segment durations don't sum exactly to target_duration, adjust the FINAL segment duration to ensure the total equals target_duration exactly.

---

## OUTPUT FORMAT (JSON ONLY)

{{
  "total_duration": {target_duration},
  "editing_style": "Nostalgic/Emotional/Cinematic/etc.",
  "emotional_intent": "The core feeling this edit should evoke",
  "plan_summary": "2-3 sentence human-readable editing strategy",
  "arc_description": "How emotion and energy evolve over time",
  "text_overlay": "1-3 short, impactful lines (or empty string if none)",
  "text_style": {{
    "font_style": "Serif/Sans-serif/Handwritten/etc.",
    "animation": "Fade/Typewriter/Static/etc.",
    "placement": "Center/Top-third/Bottom-third",
    "color_effects": "Warm/Cool/White/etc."
  }},
  "color_grading": {{
    "tone": "Warm/Cool/Neutral",
    "contrast": "Low/Medium/High",
    "specific_look": "Vintage Film/Modern Clean/etc."
  }},
  "visual_effects": ["film grain", "light leaks"],
  "narrative_message": "The story being told",
  "intent_clarity": "Clear",
  "assumed_material": ["wide landscapes", "people laughing", "etc."],
  "must_have_content": ["specific required types"],
  "should_have_content": ["preferred types"],
  "avoid_content": ["types to avoid"],
  "pacing_feel": "Breathable/Reflective/Steady",
  "visual_balance": "People-centric/Place-centric/Balanced",
  "peak_density": "Sparse/Moderate/Dense",
  "segments": [
    {{
      "id": 1,
      "start": 0.0,
      "end": 5.0,
      "duration": 5.0,
      "energy": "Low",
      "motion": "Static",
      "vibe": "warmth, nostalgia",
      "reasoning": "Open with a calm establishing shot to set the emotional tone.",
      "arc_stage": "Intro",
      "shot_scale": "Wide",
      "shot_function": "Establish",
      "expected_hold": "Long",
      "cut_origin": "visual",
      "cde": "Sparse",
      "emotional_guidance": "peaceful anticipation"
    }},
    ...
  ]
}}
"""


def create_fallback_blueprint(target_duration: float, user_prompt: str = "") -> StyleBlueprint:
    """
    Create a safe, minimal fallback blueprint if Gemini synthesis fails.
    
    This ensures the pipeline NEVER crashes during demo.
    Produces a balanced 4-segment arc optimized for nostalgia.
    
    Args:
        target_duration: Total duration in seconds
        user_prompt: Original user prompt (for logging)
    
    Returns:
        StyleBlueprint: A safe, minimal blueprint
    """
    print(f"  [FALLBACK] Creating emergency blueprint for {target_duration}s edit")
    
    # Calculate segment durations (balanced 4-stage arc)
    intro_dur = round(target_duration * 0.20, 2)
    buildup_dur = round(target_duration * 0.30, 2)
    peak_dur = round(target_duration * 0.30, 2)
    outro_dur = round(target_duration - intro_dur - buildup_dur - peak_dur, 2)
    
    # Build segment boundaries
    intro_end = intro_dur
    buildup_end = intro_end + buildup_dur
    peak_end = buildup_end + peak_dur
    outro_end = target_duration
    
    fallback_data = {
        "total_duration": target_duration,
        "editing_style": "Nostalgic Fallback",
        "emotional_intent": "Warm memories",
        "plan_summary": "A balanced 4-stage arc with gentle pacing. Fallback mode due to synthesis failure.",
        "arc_description": "Intro sets scene, Build-up escalates, Peak delivers emotion, Outro resolves.",
        "text_overlay": "",
        "text_style": {
            "font_style": "Sans-serif",
            "animation": "Fade",
            "placement": "Center",
            "color_effects": "White"
        },
        "color_grading": {
            "tone": "Warm",
            "contrast": "Medium",
            "specific_look": "Natural"
        },
        "visual_effects": [],
        "narrative_message": "A moment to remember",
        "intent_clarity": "Clear",
        "assumed_material": ["people", "places", "moments"],
        "must_have_content": [],
        "should_have_content": [],
        "avoid_content": [],
        "pacing_feel": "Breathable",
        "visual_balance": "Balanced",
        "peak_density": "Moderate",
        "text_prompt": user_prompt,
        "segments": [
            {
                "id": 1,
                "start": 0.0,
                "end": intro_end,
                "duration": intro_dur,
                "energy": "Low",
                "motion": "Static",
                "vibe": "calm, establishing",
                "reasoning": "Open with a calm establishing shot.",
                "arc_stage": "Intro",
                "shot_scale": "Wide",
                "shot_function": "Establish",
                "expected_hold": "Long",
                "cut_origin": "visual",
                "cde": "Sparse",
                "emotional_guidance": "peaceful anticipation"
            },
            {
                "id": 2,
                "start": intro_end,
                "end": buildup_end,
                "duration": buildup_dur,
                "energy": "Medium",
                "motion": "Dynamic",
                "vibe": "anticipation, warmth",
                "reasoning": "Build energy and anticipation.",
                "arc_stage": "Build-up",
                "shot_scale": "Medium",
                "shot_function": "Action",
                "expected_hold": "Normal",
                "cut_origin": "visual",
                "cde": "Moderate",
                "emotional_guidance": "growing excitement"
            },
            {
                "id": 3,
                "start": buildup_end,
                "end": peak_end,
                "duration": peak_dur,
                "energy": "Medium",
                "motion": "Dynamic",
                "vibe": "joy, memory",
                "reasoning": "Emotional peak with meaningful moments.",
                "arc_stage": "Peak",
                "shot_scale": "Close",
                "shot_function": "Reaction",
                "expected_hold": "Normal",
                "cut_origin": "visual",
                "cde": "Moderate",
                "emotional_guidance": "emotional payoff"
            },
            {
                "id": 4,
                "start": peak_end,
                "end": outro_end,
                "duration": outro_dur,
                "energy": "Low",
                "motion": "Static",
                "vibe": "reflection, peace",
                "reasoning": "Soft landing to close the narrative.",
                "arc_stage": "Outro",
                "shot_scale": "Wide",
                "shot_function": "Release",
                "expected_hold": "Long",
                "cut_origin": "visual",
                "cde": "Sparse",
                "emotional_guidance": "peaceful resolution"
            }
        ]
    }
    
    print(f"  [FALLBACK] Generated 4-segment fallback blueprint")
    return StyleBlueprint(**fallback_data)


def generate_blueprint_from_text(
    user_prompt: str,
    target_duration: float = 15.0,
    api_key: Optional[str] = None,
    bpm: Optional[float] = None,
    beat_count: Optional[int] = None
) -> StyleBlueprint:
    """
    Call Gemini to generate a full StyleBlueprint from a text prompt.
    Uses robust retry and key rotation logic.
    
    v14.7 ENHANCEMENTS:
    - Optional BPM awareness for music-synchronized phrasing
    - Fallback blueprint for graceful degradation
    - Nostalgia-first prompt design
    
    Args:
        user_prompt: Natural language description of desired edit
        target_duration: Target duration in seconds (HARD CONSTRAINT)
        api_key: Optional Gemini API key override
        bpm: Optional BPM for music-aware phrasing
        beat_count: Optional beat count for phrase calculation
    
    Returns:
        StyleBlueprint: Generated blueprint ready for Editor consumption
    """
    import time
    
    print(f"\n[GENERATOR] Synthesizing Blueprint from prompt: '{user_prompt[:50]}...'")
    if bpm:
        print(f"  🎵 Music-aware mode: {bpm:.1f} BPM")
    
    # Define cache directory
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    cache_dir = BASE_DIR / "data" / "cache" / "blueprints"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique hash for this prompt + duration + bpm combo (determinism)
    cache_key = f"{user_prompt}_{target_duration}_{bpm or 'none'}"
    prompt_hash = hashlib.md5(cache_key.encode()).hexdigest()[:12]
    cache_file = cache_dir / f"blueprint_{prompt_hash}.json"
    
    # 1. Check Cache (Deterministic execution)
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"  [CACHE] Hit! Reusing synthesized blueprint: {cache_file.name}")
            return StyleBlueprint(**data)
        except Exception as e:
            print(f"  [WARN] Failed to load cached blueprint: {e}")
    
    # 2. Build music context for the prompt
    music_context = ""
    music_guidance = ""
    
    if bpm and bpm > 0:
        beat_interval = 60.0 / bpm
        beats_in_duration = int(target_duration / beat_interval)
        phrase_length = 4  # Typical phrase = 4 beats
        phrases_in_duration = beats_in_duration // phrase_length
        
        music_context = f"""
MUSIC INFORMATION:
- BPM: {bpm:.1f}
- Beat interval: {beat_interval:.3f} seconds
- Estimated beats in edit: {beats_in_duration}
- Estimated musical phrases (4-beat): {phrases_in_duration}
"""
        music_guidance = f"""
When designing segments, consider musical phrasing:
- A 4-beat phrase at {bpm:.1f} BPM = {phrase_length * beat_interval:.2f} seconds
- Align major segment transitions to phrase boundaries when possible
- Peak should align with a strong downbeat or phrase start
- Outro should start on a resolving phrase
- DO NOT force all cuts to beats — vibes matter more than math
"""
    else:
        music_context = "(No music information available — design based on narrative pacing)"
        music_guidance = """
Design segments based on narrative flow and emotional pacing.
Since no BPM is provided, focus on visual rhythm and story arc.
"""
    
    # 3. Build final prompt
    final_prompt = GENERATOR_PROMPT
    final_prompt = final_prompt.replace("{user_prompt}", user_prompt)
    final_prompt = final_prompt.replace("{target_duration}", str(target_duration))
    final_prompt = final_prompt.replace("{music_context}", music_context)
    final_prompt = final_prompt.replace("{music_guidance}", music_guidance)
    
    # 4. Generate with retry logic
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            model = initialize_gemini(api_key)
            rate_limiter.wait_if_needed()
            response = model.generate_content([final_prompt])
            
            # Check for safety/recitation blocks
            if not response.candidates or response.candidates[0].finish_reason != 1:
                reason = "UNKNOWN"
                if response.candidates:
                    from google.generativeai.types import FinishReason
                    reason = FinishReason(response.candidates[0].finish_reason).name
                raise ValueError(f"Gemini blocked the response. Reason: {reason}")
            
            data = _parse_json_response(response.text)
            
            # Ensure total_duration is a float
            data["total_duration"] = float(data.get("total_duration", target_duration))
            
            # Add the original text prompt to the blueprint
            data["text_prompt"] = user_prompt
            
            # Ensure segments have required fields for Editor compatibility
            for seg in data.get("segments", []):
                # Default cut_origin to "visual" if not specified
                if "cut_origin" not in seg:
                    seg["cut_origin"] = "visual"
                # Default CDE to "Moderate" if not specified
                if "cde" not in seg:
                    seg["cde"] = "Moderate"
            
            # Save to Cache immediately
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"  [CACHE] Saved new blueprint synthesis: {cache_file.name}")
            except Exception as e:
                print(f"  [WARN] Failed to save blueprint cache: {e}")
            
            print(f"  ✅ Blueprint successfully synthesized (Attempt {attempt + 1})")
            return StyleBlueprint(**data)
            
        except Exception as e:
            print(f"  ⚠️ Blueprint Generation attempt {attempt + 1} failed: {e}")
            if _handle_rate_limit_error(e, "blueprint generation"):
                # Key rotated, retry immediately
                continue
            
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                print(f"  ❌ Blueprint Generation failed after all retries. Using fallback.")
                return create_fallback_blueprint(target_duration, user_prompt)
            
            time.sleep(GeminiConfig.RETRY_DELAY)
    
    # Final fallback (should never reach here, but safety first)
    print(f"  ❌ Unexpected failure path. Using fallback blueprint.")
    return create_fallback_blueprint(target_duration, user_prompt)
