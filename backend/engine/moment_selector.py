"""
Contextual Moment Selection Engine: Advisor-driven clip-to-segment matching.

v14.0 ADVISOR-AS-EDITOR VERSION:
- Builds moment candidates from all available clips
- Calls Advisor to make contextual selections per segment
- Matcher executes Advisor's decisions deterministically
"""

import json
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

import google.generativeai as genai

from models import (
    MomentCandidate, 
    ContextualMomentSelection, 
    SegmentMomentPlan,
    ClipMetadata,
    ClipIndex,
    StyleBlueprint,
    Segment
)
from engine.brain import initialize_gemini, GeminiConfig, rate_limiter, _handle_rate_limit_error, _parse_json_response
from engine.gemini_moment_prompt import CONTEXTUAL_MOMENT_PROMPT


def build_moment_candidates(
    clip_index: ClipIndex,
    target_energy: str,
    segment: Segment,
    beat_grid: List[float],
    previous_selection: Optional[MomentCandidate] = None
) -> List[MomentCandidate]:
    """
    Build a list of all candidate moments from all clips.
    
    Unlike the old system that picked one "best" moment per clip,
    this exposes ALL moments (High/Medium/Low) from ALL clips
    so the Advisor can make contextual decisions.
    
    Args:
        clip_index: All analyzed clips
        target_energy: Preferred energy level (but all levels included)
        segment: The reference segment we're filling
        beat_grid: Beat timestamps for musical alignment scoring
        previous_selection: The previous segment's selection (for continuity)
    
    Returns:
        List of MomentCandidate objects with pre-calculated context scores
    """
    candidates = []
    
    for clip in clip_index.clips:
        if not clip.best_moments:
            continue
        
        # Include ALL energy levels, not just target
        # The Advisor decides which level fits this segment
        for energy_level, moment in clip.best_moments.items():
            # Pre-calculate semantic alignment
            semantic_score = _calculate_semantic_alignment(clip, segment, moment)
            
            # Pre-calculate musical alignment
            musical_alignment = _calculate_musical_alignment(
                moment.start, moment.end, beat_grid
            )
            
            # Pre-calculate narrative continuity
            narrative_continuity = 0.0
            if previous_selection:
                narrative_continuity = _calculate_continuity(
                    previous_selection, clip, moment
                )
            
            candidate = MomentCandidate(
                clip_filename=clip.filename,
                moment_energy_level=energy_level,
                start=moment.start,
                end=moment.end,
                duration=moment.end - moment.start,
                moment_role=moment.moment_role,
                stable_moment=moment.stable_moment,
                reason=moment.reason or "",
                semantic_score=semantic_score,
                musical_alignment=musical_alignment,
                narrative_continuity=narrative_continuity
            )
            candidates.append(candidate)
    
    return candidates


def _calculate_semantic_alignment(
    clip: ClipMetadata, 
    segment: Segment,
    moment
) -> float:
    """
    Calculate how well a clip's content aligns with segment needs.
    Returns 0-1 score based on:
    - Vibe matching
    - Shot function alignment
    - Arc stage appropriateness
    """
    score = 0.0
    checks = 0
    
    # Vibe matching
    segment_vibe = (segment.vibe or "").lower()
    clip_vibes = [v.lower() for v in (clip.vibes or [])]
    if segment_vibe and any(segment_vibe in cv or cv in segment_vibe for cv in clip_vibes):
        score += 0.4
    checks += 1
    
    # Shot function alignment
    seg_func = getattr(segment, 'shot_function', None)
    if seg_func and clip.narrative_utility:
        func_map = {
            "Establish": ["establishing"],
            "Action": ["peak", "build"],
            "Reaction": ["reflection", "build"],
            "Detail": ["transition"],
            "Release": ["reflection"]
        }
        target_utils = func_map.get(seg_func, [])
        clip_utils = [u.lower() for u in clip.narrative_utility]
        if any(tu in clip_utils for tu in target_utils):
            score += 0.3
    checks += 1
    
    # Arc stage appropriateness via moment role
    arc_to_role = {
        "Intro": ["Establishing"],
        "Build-up": ["Build", "Transition"],
        "Peak": ["Climax", "Peak"],
        "Outro": ["Reflection", "Establishing"]
    }
    preferred_roles = arc_to_role.get(segment.arc_stage, [])
    if moment.moment_role in preferred_roles:
        score += 0.3
    checks += 1
    
    return score / checks if checks > 0 else 0.0


def _calculate_musical_alignment(
    moment_start: float,
    moment_end: float,
    beat_grid: List[float]
) -> float:
    """
    Calculate how well a moment aligns with musical structure.
    Returns 0-1 based on:
    - Start on or near beat
    - End on or near beat or phrase boundary
    - Duration aligns with beat intervals
    """
    if not beat_grid:
        return 0.5  # Neutral if no beat data
    
    # Check if start is near a beat (within 0.1s tolerance)
    start_near_beat = any(abs(moment_start - b) < 0.1 for b in beat_grid)
    
    # Check if end is near a beat
    end_near_beat = any(abs(moment_end - b) < 0.1 for b in beat_grid)
    
    # Calculate alignment score
    score = 0.0
    if start_near_beat:
        score += 0.4
    if end_near_beat:
        score += 0.4
    
    # Bonus for duration that aligns with beat intervals
    duration = moment_end - moment_start
    beat_intervals = [beat_grid[i+1] - beat_grid[i] for i in range(len(beat_grid)-1)]
    if beat_intervals:
        avg_interval = sum(beat_intervals) / len(beat_intervals)
        # Check if duration is close to integer multiples of beat interval
        if avg_interval > 0:
            beat_multiple = round(duration / avg_interval)
            if abs(duration - (beat_multiple * avg_interval)) < 0.1:
                score += 0.2
    
    return min(1.0, score)


def _calculate_continuity(
    previous: MomentCandidate,
    current_clip: ClipMetadata,
    current_moment
) -> float:
    """
    Calculate narrative continuity between previous selection and current candidate.
    Returns 0-1 based on:
    - Same clip (avoid immediate reuse)
    - Moment role flow (Build -> Climax, not Climax -> Establishing)
    - Semantic similarity
    """
    score = 0.5  # Neutral baseline
    
    # Same clip penalty (avoid immediate reuse)
    if previous.clip_filename == current_clip.filename:
        score -= 0.3
    
    # Moment role flow
    role_flows = {
        "Establishing": ["Build", "Transition"],
        "Build": ["Climax", "Peak", "Transition"],
        "Transition": ["Build", "Climax", "Reflection"],
        "Climax": ["Reflection", "Transition"],
        "Peak": ["Reflection", "Transition"],
        "Reflection": ["Establishing", "Build"]
    }
    valid_next = role_flows.get(previous.moment_role, [])
    if current_moment.moment_role in valid_next:
        score += 0.3
    
    return max(0.0, min(1.0, score))


def select_moment_with_advisor(
    segment: Segment,
    candidates: List[MomentCandidate],
    beat_grid: List[float],
    blueprint: StyleBlueprint,
    previous_selection: Optional[MomentCandidate] = None,
    cde: str = "Moderate"
) -> Optional[ContextualMomentSelection]:
    """
    Call Gemini Advisor to make contextual moment selection.
    
    This is the core Advisor-as-Editor functionality:
    - Advisor sees all candidates
    - Advisor sees segment context (vibe, timing, music)
    - Advisor decides which moment fits THIS segment best
    
    Args:
        segment: The reference segment to fill
        candidates: All moment candidates from all clips
        beat_grid: Musical timing data
        blueprint: Full blueprint for context
        previous_selection: Previous segment's selection (for continuity)
        cde: Cut Density Expectation for this segment
    
    Returns:
        ContextualMomentSelection with Advisor's decision
    """
    if not candidates:
        return None
    
    # Build the prompt
    segment_beats = [b for b in beat_grid if segment.start <= b < segment.end]
    beat_density = len(segment_beats) / segment.duration if segment.duration > 0 else 0
    
    # Serialize candidates for the prompt
    candidates_json = []
    for c in candidates[:20]:  # Limit to top 20 to keep prompt manageable
        candidates_json.append({
            "clip_filename": c.clip_filename,
            "energy_level": c.moment_energy_level,
            "start": c.start,
            "end": c.end,
            "duration": c.duration,
            "moment_role": c.moment_role,
            "stable": c.stable_moment,
            "reason": c.reason,
            "semantic_score": round(c.semantic_score, 2),
            "musical_alignment": round(c.musical_alignment, 2),
            "continuity": round(c.narrative_continuity, 2)
        })
    
    # Format the prompt
    prompt = CONTEXTUAL_MOMENT_PROMPT.format(
        segment_id=segment.id,
        segment_start=segment.start,
        segment_end=segment.end,
        segment_duration=segment.duration,
        segment_energy=segment.energy.value,
        segment_vibe=segment.vibe or "general",
        arc_stage=segment.arc_stage,
        expected_hold=getattr(segment, 'expected_hold', 'Normal'),
        cut_origin=getattr(segment, 'cut_origin', 'visual'),
        shot_function=getattr(segment, 'shot_function', 'Action'),
        segment_beat_count=len(segment_beats),
        beat_density=round(beat_density, 2),
        phrase_boundaries=_find_phrase_boundaries(segment_beats),
        cde=cde,
        previous_clip=previous_selection.clip_filename if previous_selection else "None",
        previous_moment_role=previous_selection.moment_role if previous_selection else "None",
        arc_progression="",  # Could be filled with actual progress
        moment_candidates=json.dumps(candidates_json, indent=2)
    )
    
    # Call Gemini
    last_error: Exception | None = None
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            model = initialize_gemini()
            current_prompt = prompt
            if attempt > 0:
                current_prompt = f"""{prompt}

CRITICAL: Your previous response was malformed JSON.
Return ONLY valid JSON matching the schema EXACTLY.
Do not add commentary. Do not explain. Only JSON.
"""

            rate_limiter.wait_if_needed()
            response = model.generate_content([current_prompt])

            if not response.candidates or response.candidates[0].finish_reason != 1:
                raise ValueError("Advisor Moment Selection blocked by Gemini")

            selection_data = _parse_json_response(response.text)

            selection_candidate = MomentCandidate(
                clip_filename=selection_data["selection"]["clip_filename"],
                moment_energy_level=selection_data["selection"]["moment_energy_level"],
                start=selection_data["selection"]["clip_start"],
                end=selection_data["selection"]["clip_end"],
                duration=selection_data["selection"]["duration"],
                moment_role="",
                stable_moment=True,
                reason=selection_data["reasoning"]
            )

            return ContextualMomentSelection(
                segment_id=segment.id,
                selection=selection_candidate,
                reasoning=selection_data["reasoning"],
                confidence=selection_data["confidence"],
                alternatives_considered=selection_data.get("alternatives_considered", []),
                continuity_notes=selection_data.get("continuity_notes", "")
            )

        except Exception as e:
            last_error = e
            if _handle_rate_limit_error(e, "moment selection"):
                continue
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise
            time.sleep(GeminiConfig.RETRY_DELAY)

    raise RuntimeError(f"Moment selection failed after retries: {last_error}")


def _find_phrase_boundaries(beat_grid: List[float]) -> List[float]:
    """
    Simple phrase boundary detection: look for gaps > 1.5x average beat interval.
    """
    if len(beat_grid) < 4:
        return []
    
    intervals = [beat_grid[i+1] - beat_grid[i] for i in range(len(beat_grid)-1)]
    avg_interval = sum(intervals) / len(intervals)
    
    boundaries = []
    for i, interval in enumerate(intervals):
        if interval > avg_interval * 1.5:
            boundaries.append(beat_grid[i+1])
    
    return boundaries


def plan_segment_moments(
    segment: Segment,
    selection: ContextualMomentSelection,
    clip_index: ClipIndex,
    beat_grid: List[float]
) -> SegmentMomentPlan:
    """
    Create a complete plan for filling a segment.
    
    If the selected moment can't fill the entire segment duration,
    this function chains additional moments (from same or different clips)
    to complete the duration without gaps.
    
    Args:
        segment: The reference segment
        selection: The Advisor's selected moment
        clip_index: All available clips
        beat_grid: Musical timing data
    
    Returns:
        SegmentMomentPlan with ordered moment sequence
    """
    moments = [selection.selection]
    total_duration = selection.selection.duration
    
    # If selected moment fills segment completely, we're done
    if total_duration >= segment.duration - 0.05:
        return SegmentMomentPlan(
            segment_id=segment.id,
            moments=moments,
            total_duration=total_duration,
            is_single_moment=True,
            chaining_reason=None
        )
    
    # Need to chain additional moments
    remaining = segment.duration - total_duration
    
    # Find compatible follow-up moments
    # Prefer same clip for continuity, but allow switching
    selected_clip = next(
        (c for c in clip_index.clips if c.filename == selection.selection.clip_filename),
        None
    )
    
    chaining_reason = f"Selected moment ({total_duration:.2f}s) insufficient for segment ({segment.duration:.2f}s)"
    
    while remaining > 0.05:
        # Try to find next moment
        next_moment = _find_chain_moment(
            selected_clip, 
            clip_index,
            moments[-1],
            remaining,
            selection.selection.moment_energy_level
        )
        
        if not next_moment:
            break
        
        moments.append(next_moment)
        total_duration += next_moment.duration
        remaining = segment.duration - total_duration
    
    return SegmentMomentPlan(
        segment_id=segment.id,
        moments=moments,
        total_duration=total_duration,
        is_single_moment=(len(moments) == 1),
        chaining_reason=chaining_reason if len(moments) > 1 else None
    )


def _find_chain_moment(
    primary_clip: Optional[ClipMetadata],
    clip_index: ClipIndex,
    previous_moment: MomentCandidate,
    remaining_duration: float,
    target_energy: str
) -> Optional[MomentCandidate]:
    """
    Find a moment that can follow the previous one to fill remaining time.
    
    Priority:
    1. Different moment from same clip (prefer stable if long duration needed)
    2. Moment from different clip (maintain energy/vibe continuity)
    """
    candidates = []
    
    # Check primary clip first
    if primary_clip and primary_clip.best_moments:
        for energy_level, moment in primary_clip.best_moments.items():
            # Skip the moment we already used
            if (energy_level == previous_moment.moment_energy_level and 
                abs(moment.start - previous_moment.start) < 0.1):
                continue
            
            duration = moment.end - moment.start
            if duration >= remaining_duration - 0.05 or moment.stable_moment:
                candidates.append(MomentCandidate(
                    clip_filename=primary_clip.filename,
                    moment_energy_level=energy_level,
                    start=moment.start,
                    end=moment.end,
                    duration=duration,
                    moment_role=moment.moment_role,
                    stable_moment=moment.stable_moment,
                    reason=moment.reason or ""
                ))
    
    # If no suitable same-clip candidate, search other clips
    if not candidates:
        for clip in clip_index.clips:
            if clip.filename == previous_moment.clip_filename:
                continue
            
            if not clip.best_moments:
                continue
            
            for energy_level, moment in clip.best_moments.items():
                duration = moment.end - moment.start
                # Prefer moments that can cover the remaining duration
                if duration >= remaining_duration - 0.1:
                    candidates.append(MomentCandidate(
                        clip_filename=clip.filename,
                        moment_energy_level=energy_level,
                        start=moment.start,
                        end=moment.end,
                        duration=duration,
                        moment_role=moment.moment_role,
                        stable_moment=moment.stable_moment,
                        reason=moment.reason or ""
                    ))
    
    if not candidates:
        return None
    
    # Sort by: stable first, then duration closest to remaining
    candidates.sort(key=lambda c: (
        not c.stable_moment,
        abs(c.duration - remaining_duration)
    ))
    
    return candidates[0]

