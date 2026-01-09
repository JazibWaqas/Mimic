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
    Match user clips to blueprint segments using energy-based greedy algorithm.
    
    ALGORITHM:
    1. Create energy pools (group clips by energy level)
    2. For each segment in blueprint:
        a. Find clips matching segment energy
        b. If no match, use round-robin from all clips
        c. Select least-used clip from pool
        d. Use PRE-COMPUTED best moment for that energy level (from comprehensive analysis)
        e. Create edit decision with timestamps
        f. If clip exhausted, switch to next clip
    3. Return Edit Decision List
    
    PRIORITY: Maintain global pacing > Perfect energy matching > Single clip integrity
    
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
    
    # Track which best moments have been used (to avoid repeating exact same moment)
    used_moments = set()  # (filename, energy_level)
    
    decisions: List[EditDecision] = []
    timeline_position = 0.0
    
    for segment in blueprint.segments:
        print(f"Segment {segment.id}: {segment.start:.2f}s-{segment.end:.2f}s "
              f"({segment.duration:.2f}s, {segment.energy.value})")
        
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
        
        # Get best moment for this clip's energy level
        best_moment = None
        if selected_clip.best_moments:
            # Use the segment's target energy to look up best moment
            best_moment = selected_clip.get_best_moment_for_energy(segment.energy)
            if best_moment:
                print(f"  ✨ Using pre-computed best moment for {segment.energy.value}: "
                      f"{best_moment[0]:.2f}s - {best_moment[1]:.2f}s")
        
        # Fill the segment duration
        remaining_duration = segment.duration
        segment_start_time = timeline_position
        
        # Safety counter to prevent infinite loops
        max_iterations = 10
        iteration = 0
        
        while remaining_duration > 0.1:  # 100ms tolerance (increased from 10ms to avoid rounding issues)
            iteration += 1
            if iteration > max_iterations:
                print(f"    [WARN] Max iterations reached, accepting {remaining_duration:.2f}s gap")
                break
            
            # Determine clip start position
            if best_moment is not None:
                # Use pre-computed best moment
                moment_key = (selected_clip.filename, segment.energy.value)
                best_start, best_end = best_moment
                best_duration = best_end - best_start
                
                if best_duration >= remaining_duration:
                    # Best moment is long enough, use portion of it
                    clip_start = best_start
                    clip_end = best_start + remaining_duration
                    use_duration = remaining_duration
                    print(f"    [BEST MOMENT] Using {use_duration:.2f}s from {clip_start:.2f}s")
                else:
                    # Best moment is shorter than needed, use it fully and continue
                    clip_start = best_start
                    clip_end = best_end
                    use_duration = best_duration
                    print(f"    [BEST MOMENT] Using full moment ({use_duration:.2f}s), "
                          f"need {remaining_duration - use_duration:.2f}s more")
                    # Clear best_moment so next iteration uses sequential
                    best_moment = None
            else:
                # Fallback to sequential cutting
                clip_start = clip_current_position[selected_clip.filename]
                available_duration = selected_clip.duration - clip_start
                
                if available_duration <= 0:
                    # Clip exhausted, reset to beginning
                    clip_current_position[selected_clip.filename] = 0.0
                    clip_start = 0.0
                    available_duration = selected_clip.duration
                
                use_duration = min(remaining_duration, available_duration)
                clip_end = clip_start + use_duration
                
                # Update tracking for sequential mode
                clip_current_position[selected_clip.filename] += use_duration
                print(f"    [SEQUENTIAL] Using {clip_start:.2f}s - {clip_end:.2f}s ({use_duration:.2f}s)")
            
            # Snap timestamps to 0.1s precision (frame-safe)
            clip_start = round(clip_start, 1)
            clip_end = round(clip_end, 1)
            use_duration = clip_end - clip_start
            
            # Skip if duration is too small after rounding
            if use_duration < 0.05:
                print(f"    [SKIP] Duration too small after rounding: {use_duration:.2f}s")
                break
            
            # Create edit decision
            decision = EditDecision(
                segment_id=segment.id,
                clip_path=selected_clip.filepath,
                clip_start=clip_start,
                clip_end=clip_end,
                timeline_start=timeline_position,
                timeline_end=timeline_position + use_duration
            )
            decisions.append(decision)
            
            # Update timeline
            timeline_position += use_duration
            remaining_duration -= use_duration
            
            print(f"    [OK] {selected_clip.filename} "
                  f"[{clip_start:.2f}s-{clip_end:.2f}s] "
                  f"→ timeline [{decision.timeline_start:.2f}s-{decision.timeline_end:.2f}s]")
            
            # If we still need more footage, switch to next clip in pool
            if remaining_duration > 0.01:
                print(f"    [WARN] Need {remaining_duration:.2f}s more")
                # Get next clip from pool
                next_clip = _get_next_clip(matching_clips, selected_clip, clip_usage_count)
                selected_clip = next_clip
                # Get new best moment for new clip
                if selected_clip.best_moments:
                    best_moment = selected_clip.get_best_moment_for_energy(segment.energy)
                else:
                    best_moment = None
        
        # Mark clip as used
        clip_usage_count[selected_clip.filename] += 1
    
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
    Validate EDL for continuity and timing errors.
    
    Returns:
        True if valid, raises ValueError if issues found
    """
    # Check timeline continuity
    for i in range(len(edl.decisions) - 1):
        current = edl.decisions[i]
        next_decision = edl.decisions[i + 1]
        
        gap = abs(current.timeline_end - next_decision.timeline_start)
        if gap > 0.02:  # 20ms tolerance (allow for rounding)
            raise ValueError(
                f"Timeline gap/overlap between decision {i} and {i+1}: {gap:.3f}s"
            )
    
    # Check total duration matches blueprint
    if edl.decisions:
        total_duration = edl.decisions[-1].timeline_end
        expected = blueprint.total_duration
        
        # Increased tolerance to 0.1s to account for timestamp rounding in editor
        if abs(total_duration - expected) > 0.1:
            raise ValueError(
                f"EDL total duration ({total_duration:.2f}s) "
                f"doesn't match blueprint ({expected:.2f}s)"
            )
    
    return True

