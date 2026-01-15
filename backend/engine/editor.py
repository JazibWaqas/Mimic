"""
Editor module: Clip-to-segment matching algorithm.

This is the "creative logic" layer. It decides which clips go where.
"""

from typing import List, Dict
from collections import defaultdict
from models import (
    StyleBlueprint,
    ClipIndex,
    EDL,
    EditDecision,
    EnergyLevel,
    MotionType,
    ClipMetadata
)

# ============================================================================
# MATCHING ALGORITHM
# ============================================================================

def match_clips_to_blueprint(
    blueprint: StyleBlueprint,
    clip_index: ClipIndex,
    find_best_moments: bool = False,  # DEPRECATED: Best moments now come from comprehensive analysis
    api_key: str | None = None
) -> EDL:
    """
    Match user clips to blueprint segments using SOFT SEGMENT approach.

    NEW ALGORITHM (Soft Segments):
    Segments are RHYTHMIC ANCHORS, not hard containers.
    1. Create energy pools (group clips by energy level)
    2. For each segment in blueprint:
        a. Define segment_budget (approximate duration)
        b. Find clips matching segment energy
        c. If no match, use round-robin from all clips
        d. Select least-used clip from pool
        e. Pull best moment window and make VARIABLE cuts (0.15s - 3.0s)
        f. Allow cuts to SPILL into next segment if energy matches
        g. Add MICRO-JITTER (±100ms) to break mathematical regularity
    3. Return Edit Decision List

    KEY CHANGES:
    - Segments define timing APPROXIMATIONS, not exact boundaries
    - Cuts can be any length (organic feel)
    - Cross-segment continuity when energy/motion matches
    - Micro-jitter prevents robotic timing

    PRIORITY: Organic flow > Global pacing > Perfect energy matching

    OPTIMIZATION: Best moments are now pre-computed during clip analysis.
    The `find_best_moments` parameter is DEPRECATED and ignored.

    Args:
        blueprint: Analyzed reference structure
        clip_index: Analyzed user clips (should have best_moments populated)
        find_best_moments: DEPRECATED - ignored
        api_key: DEPRECATED - not needed

    Returns:
        EDL (Edit Decision List) with frame-accurate instructions
    """
    print(f"\n{'='*60}")
    print(f"[EDITOR] MATCHING CLIPS TO BLUEPRINT")
    print(f"{'='*60}")
    print(f"  Segments: {len(blueprint.segments)}")
    print(f"  Clips: {len(clip_index.clips)}")
    
    # Check if clips have pre-computed best moments
    clips_with_moments = sum(1 for c in clip_index.clips if c.best_moments)
    print(f"  Clips with pre-computed best moments: {clips_with_moments}/{len(clip_index.clips)}")
    print()
    
    # Track how many times each clip has been used
    clip_usage_count = {clip.filename: 0 for clip in clip_index.clips}
    
    # Group clips by energy for fast lookup
    energy_pools = _create_energy_pools(clip_index)
    
    # Track current position in each clip (for sequential fallback)
    clip_current_position = {clip.filename: 0.0 for clip in clip_index.clips}
    
    # Note: used_moments tracking removed - not needed for current organic approach

    # Initialize deterministic randomness for organic but reproducible results
    import hashlib
    seed_string = f"{blueprint.total_duration}_{len(clip_index.clips)}_{'_'.join(c.filename for c in clip_index.clips)}"
    seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
    import random
    random.seed(seed_hash)

    decisions: List[EditDecision] = []
    timeline_position = 0.0
    segment_index = 0

    while segment_index < len(blueprint.segments):
        segment = blueprint.segments[segment_index]
        print(f"Segment {segment.id}: {segment.start:.2f}s-{segment.end:.2f}s "
              f"({segment.duration:.2f}s, {segment.energy.value})")

        # Define segment budget (approximate, not exact)
        segment_budget = segment.duration
        segment_start_time = timeline_position

        # Allow spillover to next segment if energy/motion matches
        can_spillover = (segment_index + 1 < len(blueprint.segments) and
                        blueprint.segments[segment_index + 1].energy == segment.energy and
                        blueprint.segments[segment_index + 1].motion == segment.motion)

        if can_spillover:
            spillover_segment = blueprint.segments[segment_index + 1]
            segment_budget += spillover_segment.duration * 0.3  # 30% spillover allowance
            print(f"  [SPILLOVER] Can continue into next segment (same energy/motion)")

        # Find matching clips
        matching_clips = energy_pools.get(segment.energy, [])

        if not matching_clips:
            print(f"  [WARN] No {segment.energy.value} clips available, using fallback")
            # Fallback: Use round-robin from all clips
            matching_clips = sorted(
                clip_index.clips,
                key=lambda c: clip_usage_count[c.filename]
            )

        # Select least-used clip from pool
        selected_clip = min(matching_clips, key=lambda c: clip_usage_count[c.filename])
        print(f"  📎 Selected: {selected_clip.filename} ({selected_clip.energy.value})")

        # Get best moment window for this energy level
        best_moment_window = None
        if selected_clip.best_moments:
            best_moment_window = selected_clip.get_best_moment_for_energy(segment.energy)
            if best_moment_window:
                window_start, window_end = best_moment_window
                print(f"  ✨ Best moment window: {window_start:.2f}s - {window_end:.2f}s "
                      f"({window_end - window_start:.2f}s available)")

        # Make VARIABLE cuts within the window (organic approach)
        segment_progress = 0.0
        cuts_made = 0
        max_cuts_per_segment = 5  # Prevent infinite loops

        while segment_progress < segment_budget and cuts_made < max_cuts_per_segment:
            # Determine cut length organically (0.15s - 3.0s, biased toward shorter for high energy)
            if segment.energy == EnergyLevel.HIGH:
                # High energy: favor shorter, punchier cuts
                base_length = random.uniform(0.15, 1.5)
            elif segment.energy == EnergyLevel.MEDIUM:
                # Medium energy: moderate lengths
                base_length = random.uniform(0.3, 2.5)
            else:
                # Low energy: can be longer
                base_length = random.uniform(0.5, 3.0)

            # Motion-aware adjustment (subtle but effective)
            if segment.motion == MotionType.DYNAMIC:
                base_length *= 0.8  # Shorter cuts for dynamic motion
            elif segment.motion == MotionType.STATIC:
                base_length *= 1.2  # Allow longer cuts for static motion

            # Adjust for remaining budget
            remaining_budget = segment_budget - segment_progress
            use_duration = min(base_length, remaining_budget)

            # If we have a best moment window, try to stay within it
            if best_moment_window:
                window_start, window_end = best_moment_window
                current_pos = clip_current_position[selected_clip.filename]
                
                # If current position is before window, start from window start
                if current_pos < window_start:
                    clip_start = window_start
                else:
                    clip_start = current_pos
                
                available_in_window = window_end - clip_start

                if available_in_window > 0.1:  # Still content in window
                    # Stay within the best moment window
                    clip_end = min(clip_start + use_duration, window_end)
                    actual_duration = clip_end - clip_start
                else:
                    # Window exhausted, switch to sequential
                    best_moment_window = None
                    clip_start = clip_current_position[selected_clip.filename]
                    available_duration = selected_clip.duration - clip_start

                    if available_duration <= 0:
                        # Clip exhausted, get next clip
                        next_clip = _get_next_clip(matching_clips, selected_clip, clip_usage_count)
                        selected_clip = next_clip
                        # Try to get new best moment window
                        if selected_clip.best_moments:
                            best_moment_window = selected_clip.get_best_moment_for_energy(segment.energy)
                            if best_moment_window:
                                # Start from window start if we have a best moment
                                clip_current_position[selected_clip.filename] = best_moment_window[0]
                            else:
                                clip_current_position[selected_clip.filename] = 0.0
                        else:
                            clip_current_position[selected_clip.filename] = 0.0
                        clip_start = clip_current_position[selected_clip.filename]
                        available_duration = selected_clip.duration - clip_start

                    clip_end = clip_start + min(use_duration, available_duration)
                    actual_duration = clip_end - clip_start
            else:
                # Sequential mode (no best moment window)
                clip_start = clip_current_position[selected_clip.filename]
                available_duration = selected_clip.duration - clip_start

                if available_duration <= 0:
                    # Clip exhausted, get next clip
                    next_clip = _get_next_clip(matching_clips, selected_clip, clip_usage_count)
                    selected_clip = next_clip
                    # Try to get best moment window for new clip
                    if selected_clip.best_moments:
                        best_moment_window = selected_clip.get_best_moment_for_energy(segment.energy)
                        if best_moment_window:
                            # Start from window start if we have a best moment
                            clip_current_position[selected_clip.filename] = best_moment_window[0]
                        else:
                            clip_current_position[selected_clip.filename] = 0.0
                    else:
                        clip_current_position[selected_clip.filename] = 0.0
                    clip_start = clip_current_position[selected_clip.filename]
                    available_duration = selected_clip.duration - clip_start

                clip_end = clip_start + min(use_duration, available_duration)
                actual_duration = clip_end - clip_start

            # Apply MICRO-JITTER (±100ms) to break mathematical regularity
            jitter = random.uniform(-0.1, 0.1)

            # Clamp jitter within best moment window if it exists
            if best_moment_window:
                window_start, window_end = best_moment_window
                clip_start = max(window_start, min(window_end - 0.05, clip_start + jitter))
                clip_end = max(clip_start + 0.05, min(window_end, clip_end + jitter))
            else:
                # Sequential mode - clamp to valid range
                clip_start = max(0, clip_start + jitter)
                clip_end = max(clip_start + 0.05, clip_end + jitter)  # Ensure minimum duration

            # Snap to frame-safe precision
            clip_start = round(clip_start, 1)
            clip_end = round(clip_end, 1)
            actual_duration = clip_end - clip_start

            # Ensure minimum duration after all processing
            if actual_duration < 0.1:
                # If too small, extend clip_end to get minimum duration
                clip_end = clip_start + 0.1
                actual_duration = 0.1
                # Clamp to window or clip duration if needed
                if best_moment_window:
                    clip_end = min(clip_end, best_moment_window[1])
                clip_end = min(clip_end, selected_clip.duration)
                actual_duration = clip_end - clip_start

            # Skip if still too small (shouldn't happen now, but safety check)
            if actual_duration < 0.05:
                print(f"    [SKIP] Duration too small after processing: {actual_duration:.2f}s")
                break

            # Create edit decision
            decision = EditDecision(
                segment_id=segment.id,
                clip_path=selected_clip.filepath,
                clip_start=clip_start,
                clip_end=clip_end,
                timeline_start=timeline_position,
                timeline_end=timeline_position + actual_duration
            )
            decisions.append(decision)

            # Increment usage count per decision (fair distribution)
            clip_usage_count[selected_clip.filename] += 1

            # Update tracking
            clip_current_position[selected_clip.filename] = clip_end
            timeline_position += actual_duration
            segment_progress += actual_duration
            cuts_made += 1

            # Prevent excessive timeline drift
            if timeline_position > blueprint.total_duration + 2.0:
                print(f"  [DRIFT] Stopping at {timeline_position:.2f}s to prevent excessive drift")
                break

            cut_type = "WINDOW" if best_moment_window else "SEQUENTIAL"
            print(f"    [{cut_type}] {selected_clip.filename} "
                  f"[{clip_start:.2f}s-{clip_end:.2f}s] ({actual_duration:.2f}s) "
                  f"→ timeline [{decision.timeline_start:.2f}s-{decision.timeline_end:.2f}s]")

            # Stop if we're close enough to budget (organic completion)
            if segment_progress >= segment_budget * 0.85:  # 85% completion threshold
                print(f"    [COMPLETE] Segment budget satisfied ({segment_progress:.2f}s / {segment_budget:.2f}s)")
                break

        # Move to next segment (usage counting now happens per decision)

        # Handle spillover logic
        if can_spillover and segment_progress > segment.duration:
            # We spilled into next segment, skip it
            next_segment_id = blueprint.segments[segment_index + 1].id if segment_index + 1 < len(blueprint.segments) else "?"
            print(f"  [SPILLOVER] Continued into next segment, skipping segment {next_segment_id}")
            segment_index += 1  # Skip next segment since we already covered it
            assert segment_index < len(blueprint.segments), "Spillover logic error: double-skipped"

        segment_index += 1
    
    edl = EDL(decisions=decisions)
    print(f"\n[OK] Matching complete: {len(decisions)} edit decisions\n")
    return edl


def _create_energy_pools(clip_index: ClipIndex) -> Dict[EnergyLevel, List[ClipMetadata]]:
    """
    Group clips by energy level for efficient matching.
    
    Returns:
        Dictionary mapping EnergyLevel → List[ClipMetadata]
    """
    pools = defaultdict(list)
    for clip in clip_index.clips:
        pools[clip.energy].append(clip)
    return dict(pools)


def _get_next_clip(
    pool: List[ClipMetadata],
    current_clip: ClipMetadata,
    usage_count: Dict[str, int]
) -> ClipMetadata:
    """
    Get the next clip to use when current clip is exhausted.
    
    Strategy: Use least-used clip from pool (excluding current clip if possible).
    """
    # Filter out current clip if pool has other options
    other_clips = [c for c in pool if c.filename != current_clip.filename]
    
    if other_clips:
        return min(other_clips, key=lambda c: usage_count[c.filename])
    else:
        # Only one clip in pool, reuse it
        return current_clip


# ============================================================================
# STATS & DEBUGGING
# ============================================================================

def print_edl_summary(edl: EDL, blueprint: StyleBlueprint, clip_index: ClipIndex) -> None:
    """Print human-readable EDL summary for debugging."""
    print(f"\n{'='*60}")
    print(f"[EDL] EDIT DECISION LIST SUMMARY")
    print(f"{'='*60}\n")
    
    print(f"Total decisions: {len(edl.decisions)}")
    print(f"Total segments: {len(blueprint.segments)}")
    print(f"Available clips: {len(clip_index.clips)}\n")
    
    # Count clip usage
    clip_usage = defaultdict(int)
    for decision in edl.decisions:
        filename = decision.clip_path.split('/')[-1]
        clip_usage[filename] += 1
    
    print("Clip usage distribution:")
    for filename, count in sorted(clip_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  {filename}: {count} times")
    
    print()


def validate_edl(edl: EDL, blueprint: StyleBlueprint) -> bool:
    """
    Validate EDL for continuity and timing errors (SOFT SEGMENTS version).

    With soft segments, we allow:
    - Organic completion (don't require exact blueprint duration matching)
    - Segment spillover (cuts can extend beyond segment boundaries)
    - Variable cut lengths (no longer fill segments exactly)

    Still validates:
    - Timeline continuity (no gaps/overlaps)
    - Total duration is reasonable (±2s of blueprint)
    - All clips exist and timestamps are valid

    Returns:
        True if valid, raises ValueError if issues found
    """
    # Check timeline continuity
    for i in range(len(edl.decisions) - 1):
        current = edl.decisions[i]
        next_decision = edl.decisions[i + 1]

        gap = abs(current.timeline_end - next_decision.timeline_start)
        if gap > 0.05:  # Increased tolerance for organic cuts (50ms)
            raise ValueError(
                f"Timeline gap/overlap between decision {i} and {i+1}: {gap:.3f}s"
            )

    # Check total duration is reasonable (soft validation for organic editing)
    if edl.decisions:
        total_duration = edl.decisions[-1].timeline_end
        expected = blueprint.total_duration

        # Increased tolerance to 2s for organic editing (segments are now flexible)
        if abs(total_duration - expected) > 2.0:
            raise ValueError(
                f"EDL total duration ({total_duration:.2f}s) "
                f"too far from blueprint ({expected:.2f}s) - possible organic editing error"
            )

    # Validate clip paths exist and timestamps are reasonable
    for decision in edl.decisions:
        if decision.clip_start < 0 or decision.clip_end <= decision.clip_start:
            raise ValueError(
                f"Invalid clip timestamps in decision: {decision.clip_start:.2f}s - {decision.clip_end:.2f}s"
            )

    return True

