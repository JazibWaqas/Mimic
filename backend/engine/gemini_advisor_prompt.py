"""
Gemini Advisor Prompt: Strategic clip selection guidance.

This prompt analyzes a reference video and a clip library to provide
high-level strategic suggestions WITHOUT making actual clip selections.
"""

ADVISOR_PROMPT = """
You are a creative strategist analyzing a reference video and a library of available clips.

Your goal: Suggest 3-5 clips per arc stage that best match the reference's narrative intent.

You are NOT selecting exact timestamps.
You are NOT generating an EDL.
You are providing STRATEGIC GUIDANCE to influence a deterministic matching algorithm.

---

## REFERENCE VIDEO ANALYSIS:

{blueprint_summary}

---

## AVAILABLE CLIP LIBRARY:

{clip_library_summary}

---

## YOUR TASK:

For each arc stage (Intro, Build-up, Peak, Outro):
- Recommend 3-5 clips that match the narrative intent and content requirements
- Explain WHY these clips work for that stage
- Note which must_have or should_have content requirements they satisfy

Also provide:
- Library strengths (what types of content are well-represented)
- Library gaps (what types of content are missing or weak)
- Overall confidence in library coverage ("High" | "Medium" | "Low")
  Confidence reflects how well the available library can satisfy must_have_content across ALL arc stages.
- A one-sentence overall strategy for the edit

---

## RULES:

1. Use ONLY clip filenames from the provided library
2. Clips can appear in multiple arc stages if appropriate
3. If library lacks suitable content for a stage, note it in gaps
4. Be specific and actionable
5. Focus on semantic/narrative fit, not technical qualities
6. Each arc stage MUST list between 3 and 5 clips. Never fewer, never more.
7. Reasoning should describe the group of clips as a whole, not individual clips.

---

## OUTPUT REQUIREMENTS:

- Output VALID JSON ONLY
- No markdown, no extra text
- Be consistent and deterministic

---

## JSON SCHEMA:

{{
  "arc_stage_suggestions": {{
    "Intro": {{
      "recommended_clips": ["clip45.mp4", "clip52.mp4", "clip30.mp4"],
      "reasoning": "Low-energy establishing shots with scenic landscapes match calm opening intent",
      "content_alignment": ["must_have: Scenic landscapes"]
    }},
    "Build-up": {{
      "recommended_clips": ["clip20.mp4", "clip28.mp4"],
      "reasoning": "Travel transit clips with gentle motion build momentum",
      "content_alignment": ["must_have: Travel transit"]
    }},
    "Peak": {{
      "recommended_clips": ["clip1.mp4", "clip.mp4", "clip12.mp4"],
      "reasoning": "High-energy group interactions match celebratory peak intent",
      "content_alignment": ["must_have: Candid group interactions", "should_have: Golden hour"]
    }},
    "Outro": {{
      "recommended_clips": ["clip45.mp4", "clip18.mp4"],
      "reasoning": "Reflective moments with stable frames for soft resolution",
      "content_alignment": []
    }}
  }},
  "library_assessment": {{
    "strengths": ["Strong People-Group coverage", "Good energy distribution"],
    "gaps": ["Limited nighttime urban clips", "Few solo reflection moments"],
    "confidence": "High"
  }},
  "overall_strategy": "Prioritize people-centric clips in Peak, balance with scenic establishing shots in Intro/Outro."
}}
"""
