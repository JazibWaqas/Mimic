"""
Gemini Advisor: Strategic clip selection guidance system.

The Advisor provides high-level suggestions that BIAS the matcher
without replacing it. This maintains determinism while adding
narrative intelligence.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from models import (
    StyleBlueprint,
    ClipIndex,
    ClipMetadata,
    Segment,
    AdvisorHints,
    ArcStageSuggestion,
    LibraryAssessment
)
from engine.gemini_advisor_prompt import ADVISOR_PROMPT
from engine.brain import initialize_gemini, _parse_json_response, GeminiConfig, rate_limiter, _handle_rate_limit_error
import time


def get_advisor_suggestions(
    blueprint: StyleBlueprint,
    clip_index: ClipIndex,
    cache_dir: Path = Path("data/cache"),
    force_refresh: bool = False
) -> Optional[AdvisorHints]:
    """
    Get Gemini's strategic suggestions for clip selection.
    
    This generates or retrieves cached advisor hints that influence
    the matcher's scoring without controlling it.
    
    Args:
        blueprint: Analyzed reference structure with narrative intent
        clip_index: Analyzed user clips with semantic metadata
        cache_dir: Directory for caching advisor results
        force_refresh: If True, bypass cache and regenerate
    
    Returns:
        AdvisorHints if successful, None if failure (graceful degradation)
    """
    print(f"\n{'='*60}")
    print(f"[ADVISOR] GENERATING STRATEGIC GUIDANCE")
    print(f"{'='*60}")
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    ref_hash = hashlib.md5(
        (blueprint.narrative_message + str(blueprint.segments)).encode()
    ).hexdigest()[:12]
    
    library_hash = hashlib.md5(
        "".join(sorted(c.filename for c in clip_index.clips)).encode()
    ).hexdigest()[:12]
    
    cache_file = cache_dir / f"advisor_{ref_hash}_{library_hash}.json"
    
    if not force_refresh and cache_file.exists():
        try:
            print(f"  📦 Loading cached advisor hints...")
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            
            cache_version = data.get("cache_version", "1.0")
            if cache_version != "1.0":
                print(f"  ⚠️ Cache version mismatch ({cache_version} vs 1.0), regenerating...")
                cache_file.unlink()
            else:
                hints = AdvisorHints(**data)
                print(f"  ✅ Loaded from cache: {cache_file.name}")
                return hints
        except Exception as e:
            print(f"  ⚠️ Cache corrupted, regenerating: {e}")
    
    print(f"  🧠 Calling Gemini for strategic guidance...")
    
    blueprint_summary = _format_blueprint_summary(blueprint)
    library_summary = _format_clip_library_summary(clip_index)
    
    prompt = ADVISOR_PROMPT.format(
        blueprint_summary=blueprint_summary,
        clip_library_summary=library_summary
    )
    
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            model = initialize_gemini()
            
            rate_limiter.wait_if_needed()
            response = model.generate_content([prompt])
            
            if not response.candidates or response.candidates[0].finish_reason != 1:
                reason = "UNKNOWN"
                if response.candidates:
                    from google.generativeai.types import FinishReason
                    reason = FinishReason(response.candidates[0].finish_reason).name
                raise ValueError(f"Gemini blocked the response. Reason: {reason}")
            
            data = _parse_json_response(response.text)
            
            cached_at = datetime.utcnow().isoformat()
            
            arc_suggestions = {}
            for stage, suggestion_data in data.get('arc_stage_suggestions', {}).items():
                arc_suggestions[stage] = ArcStageSuggestion(**suggestion_data)
            
            library_assessment = LibraryAssessment(**data.get('library_assessment', {}))
            
            hints = AdvisorHints(
                arc_stage_suggestions=arc_suggestions,
                library_assessment=library_assessment,
                overall_strategy=data.get('overall_strategy', ''),
                cached_at=cached_at
            )
            
            cache_file.write_text(hints.model_dump_json(indent=2), encoding='utf-8')
            print(f"  ✅ Advisor hints generated and cached")
            print(f"  📊 Confidence: {hints.library_assessment.confidence}")
            print(f"  💡 Strategy: {hints.overall_strategy}")
            
            return hints
            
        except Exception as e:
            print(f"  ⚠️ Advisor attempt {attempt + 1} failed: {e}")
            if _handle_rate_limit_error(e, "advisor"):
                continue
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                print(f"  ❌ Advisor failed after all retries")
                print(f"  ⚙️ Falling back to base matcher (no advisor influence)")
                return None
            time.sleep(GeminiConfig.RETRY_DELAY)
    
    return None


def compute_advisor_bonus(
    clip: ClipMetadata,
    segment: Segment,
    blueprint: StyleBlueprint,
    advisor_hints: Optional[AdvisorHints]
) -> int:
    """
    Compute advisor scoring bonus for a specific clip in a segment.
    
    This is ADDITIVE to the base matcher score. The bonus can be positive
    (recommended clip) or negative (clip should be avoided).
    
    Args:
        clip: Candidate clip being scored
        segment: Current segment being filled
        blueprint: Reference analysis with narrative intent
        advisor_hints: Advisor suggestions (can be None for graceful degradation)
    
    Returns:
        Bonus score (typically in range -30 to +85)
    """
    if not advisor_hints:
        return 0
    
    bonus = 0
    
    arc_suggestions = advisor_hints.arc_stage_suggestions.get(segment.arc_stage)
    if arc_suggestions and clip.filename in arc_suggestions.recommended_clips:
        if blueprint.intent_clarity == "Clear":
            bonus += 40
        elif blueprint.intent_clarity == "Implicit":
            bonus += 25
        else:
            bonus += 15
    
    exact_must, category_must = _match_content_requirements(
        clip, blueprint.must_have_content
    )
    if exact_must:
        bonus += 20
    elif category_must:
        bonus += 10
    
    exact_should, category_should = _match_content_requirements(
        clip, blueprint.should_have_content
    )
    if exact_should:
        bonus += 10
    elif category_should:
        bonus += 5
    
    if clip.clip_quality >= 4:
        bonus += 5
    
    if segment.arc_stage in ["Intro", "Outro"]:
        if clip.best_moments:
            energy_key = segment.energy.value.capitalize()
            best_moment = clip.best_moments.get(energy_key)
            if best_moment and best_moment.stable_moment:
                bonus += 10
    
    for avoid_context in clip.avoid_for:
        if segment.arc_stage.lower() in avoid_context.lower():
            bonus -= 30
            break
    
    return bonus


def _match_content_requirements(
    clip: ClipMetadata,
    requirements: list[str]
) -> Tuple[bool, bool]:
    """
    Check if clip matches content requirements.
    
    Uses a two-tier matching system:
    - Exact: Full subject name appears in requirement text
    - Category: Subject category (first part before dash) appears in requirement
    
    Args:
        clip: Clip with primary_subject field
        requirements: List of content requirement strings from reference
    
    Returns:
        Tuple of (exact_match, category_match)
    """
    exact_match = False
    category_match = False
    
    clip_categories = {s.split('-')[0].lower() for s in clip.primary_subject}
    
    for req in requirements:
        req_lower = req.lower()
        
        for subject in clip.primary_subject:
            subject_clean = subject.lower().replace('-', ' ')
            if subject_clean in req_lower or any(part in req_lower for part in subject_clean.split()):
                exact_match = True
                break
        
        for cat in clip_categories:
            if cat in req_lower:
                category_match = True
                break
    
    return exact_match, category_match


def _format_blueprint_summary(blueprint: StyleBlueprint) -> str:
    """
    Format blueprint into a concise summary for the Gemini prompt.
    """
    lines = []
    
    lines.append(f"Duration: {blueprint.total_duration:.1f}s")
    lines.append(f"Editing Style: {blueprint.editing_style}")
    lines.append(f"Emotional Intent: {blueprint.emotional_intent}")
    
    if blueprint.text_overlay:
        lines.append(f"Text Overlay: \"{blueprint.text_overlay}\"")
    
    lines.append(f"\nNarrative Message: {blueprint.narrative_message}")
    lines.append(f"Intent Clarity: {blueprint.intent_clarity}")
    
    if blueprint.must_have_content:
        lines.append(f"\nMust-Have Content:")
        for item in blueprint.must_have_content:
            lines.append(f"  - {item}")
    
    if blueprint.should_have_content:
        lines.append(f"\nShould-Have Content:")
        for item in blueprint.should_have_content:
            lines.append(f"  - {item}")
    
    if blueprint.avoid_content:
        lines.append(f"\nAvoid Content:")
        for item in blueprint.avoid_content:
            lines.append(f"  - {item}")
    
    lines.append(f"\nPacing Feel: {blueprint.pacing_feel}")
    lines.append(f"Visual Balance: {blueprint.visual_balance}")
    lines.append(f"Arc Description: {blueprint.arc_description}")
    
    arc_stages = {}
    for seg in blueprint.segments:
        stage = seg.arc_stage
        if stage not in arc_stages:
            arc_stages[stage] = []
        arc_stages[stage].append(seg)
    
    lines.append(f"\nArc Stage Breakdown:")
    for stage, segments in arc_stages.items():
        energy_counts = {}
        for seg in segments:
            energy_counts[seg.energy.value] = energy_counts.get(seg.energy.value, 0) + 1
        energy_str = ", ".join(f"{count}x {energy}" for energy, count in energy_counts.items())
        lines.append(f"  {stage}: {len(segments)} segments ({energy_str})")
    
    return "\n".join(lines)


def _format_clip_library_summary(clip_index: ClipIndex) -> str:
    """
    Format clip library into a concise summary for the Gemini prompt.
    """
    lines = []
    lines.append(f"Total Clips: {len(clip_index.clips)}\n")
    
    for clip in clip_index.clips:
        clip_info = [
            f"Filename: {clip.filename}",
            f"Duration: {clip.duration:.1f}s",
            f"Energy: {clip.energy.value} (intensity: {clip.intensity})",
            f"Motion: {clip.motion.value}",
            f"Primary Subject: {', '.join(clip.primary_subject)}",
            f"Narrative Utility: {', '.join(clip.narrative_utility)}",
            f"Emotional Tone: {', '.join(clip.emotional_tone)}",
            f"Quality: {clip.clip_quality}/5",
            f"Best For: {', '.join(clip.best_for)}",
        ]
        
        if clip.avoid_for:
            clip_info.append(f"Avoid For: {', '.join(clip.avoid_for)}")
        
        if clip.content_description:
            clip_info.append(f"Content: {clip.content_description}")
        
        lines.append("  " + " | ".join(clip_info))
    
    return "\n".join(lines)
