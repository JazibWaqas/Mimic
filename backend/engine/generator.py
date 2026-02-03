"""
Blueprint Generator: Text-to-Edit-DNA system.
Allows users to describe an edit in natural language and generates a full StyleBlueprint.
This bypasses the need for a reference video while maintaining the same deterministic execution.
"""

import json
from typing import Optional
from models import StyleBlueprint, EnergyLevel, MotionType, Segment
from engine.brain import initialize_gemini, _parse_json_response, GeminiConfig, rate_limiter, _handle_rate_limit_error

GENERATOR_PROMPT = """
You are a world-class Creative Director and Edit Producer.
Your task is to generate a 'Style Blueprint' (Editing DNA) based on a user's text description.

This blueprint will be used by an automated engine to assemble raw clips into a cohesive narrative.

USER DESCRIPTION:
{user_prompt}

TARGET DURATION: {target_duration} seconds

AUTHORSHIP BOUNDARY:
You are defining EDITORIAL INTENT AND STRUCTURE, not execution guarantees. 
Specify PREFERENCES for shot types, scales, and functions. 
Segment boundaries represent intended pacing, not guaranteed cut points. The engine may subdivide or merge segments to preserve rhythm and feasibility.
The engine will optimize for the best possible match under library constraints, and the Reflector will explain any necessary tradeoffs.

TASK:
1. Define the overall narrative message and emotional intent.
2. Create a 'Plan Summary': A 2-3 sentence human-readable explanation of the editing strategy.
3. Define the 'Text Overlay': Create 1-3 short, impactful lines of text to be displayed on the video that capture the core emotion.
4. Define 'Text Style': Specify font style, animation, placement, and color effects.
5. Define 'Visual Aesthetics': Specify color grading (tone, contrast, specific look) and visual effects (e.g., film grain, light leaks).
6. Design a sequence of segments (cuts) that follow a professional story arc (Intro -> Build-up -> Peak -> Outro).
   - For each segment, provide 'Emotional Guidance': What should the viewer feel? (e.g., "anticipation", "pure joy", "peaceful reflection").
   - Use the user's description of energy shifts and key moments to guide the segment density.
   - If the user specifies a 'chaotic peak', increase the number of short segments in the Peak stage.
   - If the user specifies 'cinematic wide shots', increase the duration of segments in that stage.
   - Use richer vocabulary for vibes: Wide vs Tight, Observational vs Participatory, Momentum vs Restraint, Breath vs Impact.
7. Identify "Assumed Material": What specific types of footage are you assuming the user has provided to make this vision work? (e.g., "wide landscapes", "people laughing").
8. For each segment, specify:
   - Start/End times (must sum to total duration, no gaps).
   - Preferred Energy Level (Low/Medium/High).
   - Preferred Motion Type (Static/Dynamic).
   - Intended Shot Function (Establish/Action/Reaction/Detail/Transition).
   - Expected Hold (Short/Normal/Long).
   - Emotional Guidance (1-3 words).
   - Note: Shot scale (Wide/Close) is ADVISORY only; the engine prioritizes energy and vibe matching.

CRITICAL RULES:
- Total duration must be EXACTLY {target_duration} seconds.
- Segments must be continuous (Segment 2 start = Segment 1 end).
- Use professional editorial reasoning for every decision.
- If the user’s description conflicts with standard pacing rules, prioritize emotional intent over mechanical symmetry.
- Do not over-specify micro-details that depend on specific clip content; focus on the "soul" of the segment.

OUTPUT FORMAT (JSON ONLY):
{{
  "total_duration": {target_duration},
  "editing_style": "...",
  "emotional_intent": "...",
  "plan_summary": "...",
  "arc_description": "...",
  "text_overlay": "...",
  "text_style": {{
    "font_style": "...",
    "animation": "...",
    "placement": "...",
    "color_effects": "..."
  }},
  "color_grading": {{
    "tone": "...",
    "contrast": "...",
    "specific_look": "..."
  }},
  "visual_effects": ["...", "..."],
  "narrative_message": "...",
  "intent_clarity": "Clear",
  "assumed_material": ["...", "..."],
  "must_have_content": ["...", "..."],
  "should_have_content": ["...", "..."],
  "avoid_content": ["...", "..."],
  "pacing_feel": "...",
  "visual_balance": "...",
  "segments": [
    {{
      "id": 1,
      "start": 0.0,
      "end": 2.5,
      "duration": 2.5,
      "energy": "Low",
      "motion": "Static",
      "vibe": "...",
      "reasoning": "...",
      "arc_stage": "Intro",
      "shot_scale": "Wide",
      "shot_function": "Establish",
      "expected_hold": "Long"
    }},
    ...
  ]
}}
"""

def generate_blueprint_from_text(
    user_prompt: str,
    target_duration: float = 15.0,
    api_key: Optional[str] = None
) -> StyleBlueprint:
    """
    Call Gemini to generate a full StyleBlueprint from a text prompt.
    Uses robust retry and key rotation logic.
    """
    print(f"\n[GENERATOR] Synthesizing Blueprint from prompt: '{user_prompt[:50]}...'")
    
    # Use safe formatting to avoid issues with JSON braces in the prompt
    final_prompt = GENERATOR_PROMPT
    final_prompt = final_prompt.replace("{user_prompt}", user_prompt)
    final_prompt = final_prompt.replace("{target_duration}", str(target_duration))

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
            
            print(f"  ✅ Blueprint successfully synthesized (Attempt {attempt + 1})")
            return StyleBlueprint(**data)
            
        except Exception as e:
            print(f"  ⚠️ Blueprint Generation attempt {attempt + 1} failed: {e}")
            if _handle_rate_limit_error(e, "blueprint generation"):
                # Key rotated, retry immediately
                continue
                
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                print(f"  ❌ Blueprint Generation failed after all retries.")
                raise e
                
            time.sleep(GeminiConfig.RETRY_DELAY)

    raise Exception("Failed to generate blueprint after all retries and key rotations.")
