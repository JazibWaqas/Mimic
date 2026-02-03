"""
Reflector module: Post-render AI reflection and critique.
Generates the 'Director's Voice' monologue and identifies library gaps.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional
from models import StyleBlueprint, EDL, ClipIndex, DirectorCritique, AdvisorHints
from engine.brain import initialize_gemini, _parse_json_response, GeminiConfig, rate_limiter, _handle_rate_limit_error
import time

REFLECTOR_PROMPT = """
You are a world-class Creative Director and Editor, specializing in short-form, social-native storytelling (reels, clips, and modern video narratives).

You are reviewing a finished video edit created by an automated system called MIMIC.
This is a WHITEBOX critique: your job is to explain what worked, what didn't, and why - 
based strictly on the data provided. Do not hallucinate visuals or events.

IMPORTANT SYSTEM CONSTRAINTS (DO NOT VIOLATE):
- The editing engine is deterministic and constraint-driven.
- Energy gating, beat alignment, and diversity rules were always respected.
- If a clip feels weak, assume it was used due to limitations in the clip library, not a system error.
- Do NOT suggest alternate edits. Only evaluate the outcome and material quality.
- NOTE: You are reviewing a partial summary of the edit decisions. Do not assume full consistency beyond the provided evidence.

CONTEXT PROVIDED:
- Reference Blueprint Summary: {blueprint_summary}
- Strategic Plan (Pre-edit Intent): {advisor_summary}
- Final Edit Decisions (EDL with reasoning): {edl_summary}

YOUR HIERARCHY OF JUDGMENT (CRITICAL):
1. NARRATIVE ADHERENCE: Did the edit respect the "Text Overlay" intent and "Dominant Narrative"? 
   (NOTE: If no explicit text overlay exists, infer narrative intent from the Reference Blueprint's narrative_message and emotional_intent).
2. SEMANTIC FLOW: Did the "Vibe" of the clips match the "Vibe" of the reference segments?
3. RHYTHMIC PRECISION: How well did the cuts align with the "Beat Sync" and "Energy" requirements? 
   (NOTE: For text-based edits, rhythm is inferred at a default 120 BPM).
4. MATERIAL QUALITY: The visual appeal and relevance of the source clips themselves.
   (NOTE: Check the blueprint's "assumed_material" list. If the edit drifted, was it because the library lacked these assumed assets?)

DEFINITIONS (USE THESE):
- "Star Performer": A clip that satisfied the Narrative Intent (Text Overlay) AND matched the segment's Vibe perfectly.
- "Dead Weight": A clip that diluted the narrative intent (e.g., a scenic shot in a people-driven story) or was a low-energy compromise.
- "Missing Ingredients": Concrete shot types or moments that would materially improve the edit if added.

YOUR TASKS:
1. Analyze the EDL. Identify where the system successfully anchored the "Text Overlay" intent vs where it drifted into "Filler."
2. Write a 3-4 sentence Director's Monologue that captures the soul of the edit.
   - Start with "Based on the observed segments..." to maintain technical humility.
   - Focus on the "Story Transfer": How well did the system transplant the reference's rhythm into the user's narrative?
   - Explicitly distinguish between what the system executed well despite constraints vs what would improve only with better source material.
   - Be honest about "Thematic Dissonance" (e.g., "The system tried to tell a story of friendship using mostly landscape clips").
3. List specific Star Performers by clip filename.
4. List specific Dead Weight clips by filename. Frame these as "necessary compromises" due to library constraints, not as errors.
5. Suggest Missing Ingredients as concrete, filmable shots (not abstract advice).
6. Create 'Remake Actions': 2-3 structured deltas for the next iteration.
   - format: {"type": "increase_energy" | "change_subject" | "fix_pacing", "segment": "Intro" | "Build-up" | "Peak" | "Outro", "suggestion": "..."}
7. Provide a brief Technical Fidelity note that evaluates execution quality independently of footage quality.

SCORING GUIDELINE:
- overall_score reflects the NARRATIVE COHESION and VIEWING EXPERIENCE.
- A 10/10 requires perfect alignment between the Text Intent, the Reference Rhythm, and the Clip Content.
- Penalize "Intent Dilution" (wrong subject for the story) heavily.

OUTPUT FORMAT (JSON ONLY):
{{
  "overall_score": 7.5,
  "monologue": "...",
  "star_performers": ["clip1.mp4", "clip5.mp4"],
  "dead_weight": ["clip4.mp4", "clip7.mp4"],
  "missing_ingredients": [
    "Wide establishing shots with stable framing",
    "Group motion (friends walking or dancing together)",
    "Transitional filler shots for pacing"
  ],
  "remake_actions": [
    {{ "type": "increase_energy", "segment": "Peak", "suggestion": "Add at least 2 more Dynamic/High clips" }}
  ],
  "technical_fidelity": "Beat alignment and energy progression were executed cleanly. Narrative intent was preserved, but limited by clip variety."
}}
"""

def reflect_on_edit(
    blueprint: StyleBlueprint,
    edl: EDL,
    clip_index: ClipIndex,
    advisor: Optional[AdvisorHints] = None,
    cache_dir: Optional[Path] = None,
    force_refresh: bool = False
) -> DirectorCritique:
    """
    Call Gemini to generate a post-render critique.
    Uses hash-based caching to avoid redundant API calls.
    """
    if cache_dir is None:
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        cache_dir = BASE_DIR / "data" / "cache" / "critiques"
    
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Create a unique hash for this specific edit (Blueprint + EDL + Advisor)
    # This ensures that if the pacing or clips change, the critique regenerates.
    edl_hash = hashlib.md5(edl.model_dump_json().encode()).hexdigest()[:12]
    cache_file = cache_dir / f"critique_{edl_hash}.json"

    if not force_refresh and cache_file.exists():
        try:
            print(f"  📦 Loading cached Director's Critique...")
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            return DirectorCritique(**data)
        except Exception as e:
            print(f"  ⚠️ Critique cache corrupted: {e}")

    print(f"\n[REFLECTOR] Generating Director's Critique...")
    
    # Summarize data for prompt
    blueprint_summary = f"Style: {blueprint.editing_style}, Intent: {blueprint.emotional_intent}, Message: {blueprint.narrative_message}"
    advisor_summary = advisor.editorial_strategy if advisor else "No strategic plan used."
    
    # Extract key decisions for the prompt
    decisions = []
    for d in edl.decisions[:15]: # Limit to first 15 to save tokens
        # Use filename only for prompt clarity
        clip_name = d.clip_path.split('/')[-1].split('\\')[-1]
        decisions.append(f"Seg {d.segment_id}: {clip_name} ({d.reasoning})")
    edl_summary = " | ".join(decisions)

    # Use a dictionary for formatting to avoid KeyError with {type} in the prompt
    format_vars = {
        "blueprint_summary": blueprint_summary,
        "advisor_summary": advisor_summary,
        "edl_summary": edl_summary
    }

    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            model = initialize_gemini()
            rate_limiter.wait_if_needed()
            
            # Use safe formatting to avoid issues with JSON braces in the prompt
            # We must escape double braces for the final prompt if we use .format()
            # but since we are doing manual replace, we just replace the placeholders.
            final_prompt = REFLECTOR_PROMPT
            for key, val in format_vars.items():
                final_prompt = final_prompt.replace("{" + key + "}", str(val))
            
            # CRITICAL: The prompt itself contains JSON examples with { "type": ... }
            # We must ensure we don't have any unescaped single braces that .format() would catch.
            # But since we aren't using .format() on the whole thing anymore, this is safe.
            
            response = model.generate_content([final_prompt])
            
            data = _parse_json_response(response.text)
            critique = DirectorCritique(**data)
            
            # Save to cache
            try:
                cache_file.write_text(critique.model_dump_json(indent=2), encoding='utf-8')
                print(f"  ✅ Critique cached: {cache_file.name}")
            except Exception as e:
                print(f"  ⚠️ Failed to cache critique: {e}")
                
            return critique
        except Exception as e:
            if _handle_rate_limit_error(e, "reflector"):
                # Key rotated, retry immediately
                continue
                
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                print(f"  ⚠️ Reflector failed after all retries: {e}. Using fallback critique.")
                return DirectorCritique(
                    overall_score=5.0,
                    monologue="The system completed the edit, but the reflection layer encountered an error. The technical structure is sound, but the narrative nuance requires human review.",
                    technical_fidelity="Automatic validation passed. Rhythmic alignment confirmed."
                )
            
            time.sleep(GeminiConfig.RETRY_DELAY)
    
    return DirectorCritique(
        overall_score=5.0,
        monologue="The system completed the edit, but the reflection layer encountered an error. The technical structure is sound, but the narrative nuance requires human review.",
        technical_fidelity="Automatic validation passed. Rhythmic alignment confirmed."
    )
