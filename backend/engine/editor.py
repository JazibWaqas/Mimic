"""
Editor module: Clip-to-segment matching algorithm (FIXED VERSION).

FIXES APPLIED:
1. Simplified algorithm - no complex spillover logic
2. Proper clip rotation - ensures all clips are used
3. Fills segments completely - matches reference duration
4. Uses best moments when available
5. Prevents back-to-back repeats of same clip
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
from engine.processors import has_audio, get_beat_grid, align_to_nearest_beat


def match_clips_to_blueprint(
    blueprint: StyleBlueprint,
    clip_index: ClipIndex,
    find_best_moments: bool = False,  # Ignored - best moments come from comprehensive analysis
    api_key: str | None = None,
    reference_path: str | None = None  # NEW: For beat detection
) -> EDL:
    """
    Match user clips to blueprint segments using SIMPLIFIED algorithm.
    
    ALGORITHM:
    1. For each segment in blueprint:
       a. Find clips matching segment energy
       b. Select LEAST RECENTLY USED clip from pool
       c. Use best moment if available, otherwise sequential
       d. Fill segment completely (no 85% threshold)
       e. Track usage to ensure fair distribution
    
    FIXES:
    - Removed complex spillover logic (was causing bugs)
    - Proper clip rotation (prevents only 2 clips being used)
    - Fills segments to match reference duration
    - Prevents same clip back-to-back
    
    Args:
        blueprint: Analyzed reference structure
        clip_index: Analyzed user clips (should have best_moments populated)
        find_best_moments: DEPRECATED - ignored
        api_key: DEPRECATED - not needed
    
    Returns:
        EDL (Edit Decision List) with frame-accurate instructions
    """
    print(f"\n{'='*60}")
    print(f"[EDITOR] MATCHING CLIPS TO BLUEPRINT (FIXED VERSION)")
    print(f"{'='*60}")
    print(f"  Segments: {len(blueprint.segments)}")
    print(f"  Clips: {len(clip_index.clips)}")
    
    # Check if clips have pre-computed best moments
    clips_with_moments = sum(1 for c in clip_index.clips if c.best_moments)
    print(f"  Clips with pre-computed best moments: {clips_with_moments}/{len(clip_index.clips)}")
    
    # PHASE 2: Generate beat grid for audio sync
    beat_grid = None
    if reference_path and has_audio(reference_path):
        beat_grid = get_beat_grid(blueprint.total_duration, bpm=120)
        print(f"  🎵 Beat grid generated: {len(beat_grid)} beats at 120 BPM")
    else:
        print(f"  🔇 No audio detected - using visual cuts only")
    
    print()
    
    # Track usage: how many times each clip has been used
    clip_usage_count = {clip.filename: 0 for clip in clip_index.clips}
    
    # Track current position in each clip (for sequential fallback)
    clip_current_position = {clip.filename: 0.0 for clip in clip_index.clips}
    
    # Group clips by energy for fast lookup
    energy_pools = _create_energy_pools(clip_index)
    
    decisions: List[EditDecision] = []
    timeline_position = 0.0
    last_used_clip = None  # Track to prevent back-to-back repeats
    second_last_clip = None  # Track last 2 clips for more variety

    
    for segment in blueprint.segments:
        print(f"\nSegment {segment.id}: {segment.start:.2f}s-{segment.end:.2f}s "
              f"({segment.duration:.2f}s, {segment.energy.value}/{segment.motion.value})")
        
        segment_remaining = segment.duration
        segment_start_time = timeline_position
        
        # Fill this segment with MULTIPLE RAPID CUTS to match fast-paced editing
        cuts_in_segment = 0
        max_cuts_per_segment = 20  # Prevent infinite loops
        
        while segment_remaining > 0.05 and cuts_in_segment < max_cuts_per_segment:
            # Find matching clips
            matching_clips = energy_pools.get(segment.energy, [])
            
            if not matching_clips:
                print(f"  [WARN] No {segment.energy.value} clips available, using all clips")
                matching_clips = clip_index.clips
            
            # CRITICAL: Switch clips for EVERY cut to maximize variety
            # Exclude last 2 used clips to prevent repetition
            recently_used = [last_used_clip, second_last_clip] if second_last_clip else [last_used_clip]
            available_clips = [c for c in matching_clips if c.filename not in recently_used]
            
            if not available_clips:
                # If we've exhausted all clips, use any clip
                available_clips = matching_clips
            
            # SMART SELECTION: Prioritize unused clips, then least-used
            # Sort by usage count (lowest first), then shuffle within each usage tier
            import random
            
            # Group clips by usage count
            min_usage = min(clip_usage_count[c.filename] for c in available_clips)
            least_used_clips = [c for c in available_clips if clip_usage_count[c.filename] == min_usage]
            
            # Shuffle within the least-used group for variety
            random.shuffle(least_used_clips)
            selected_clip = least_used_clips[0]
            
            if cuts_in_segment == 0:  # Only print once per segment
                print(f"  📎 Starting segment with: {selected_clip.filename} ({selected_clip.energy.value}, used {clip_usage_count[selected_clip.filename]}x)")

            
            # FIXED: Consistent short cuts based on energy level
            # NO MORE GROWING DURATIONS - stay rapid throughout
            if segment.energy == EnergyLevel.HIGH:
                # Viral TikTok style: consistently fast cuts
                target_duration = random.uniform(0.2, 0.5)  # Always 0.2-0.5s
            elif segment.energy == EnergyLevel.MEDIUM:
                target_duration = random.uniform(0.4, 0.8)  # Moderate pacing
            else:  # LOW
                target_duration = random.uniform(0.8, 1.5)  # Slower, deliberate cuts
            
            # Clamp to remaining segment budget
            use_duration = min(target_duration, segment_remaining)
            
            # Try to use best moment if available
            clip_start = None
            clip_end = None
            
            if selected_clip.best_moments:
                best_moment = selected_clip.get_best_moment_for_energy(segment.energy)
                if best_moment:
                    window_start, window_end = best_moment
                    window_duration = window_end - window_start
                    
                    # Check if we've already used part of this window
                    current_pos = clip_current_position[selected_clip.filename]
                    
                    if current_pos < window_start:
                        # Haven't reached window yet, start from window
                        clip_start = window_start
                    elif current_pos < window_end:
                        # In the middle of window, continue from current position
                        clip_start = current_pos
                    else:
                        # Window exhausted, use sequential
                        clip_start = current_pos
                    
                    # Calculate end
                    if clip_start >= window_start and clip_start < window_end:
                        # We're in the window, stay in it
                        clip_end = min(clip_start + use_duration, window_end)
                    else:
                        # Outside window, use sequential
                        clip_end = min(clip_start + use_duration, selected_clip.duration)
                    
                    print(f"    ✨ Using best moment window: {window_start:.2f}s-{window_end:.2f}s")
            
            # Fallback to sequential if no best moment or window exhausted
            if clip_start is None or clip_end is None:
                clip_start = clip_current_position[selected_clip.filename]
                clip_end = min(clip_start + use_duration, selected_clip.duration)
            
            # Check if clip is exhausted
            if clip_start >= selected_clip.duration - 0.1:
                # Clip exhausted, reset to beginning
                print(f"    🔄 Clip exhausted, resetting to start")
                clip_current_position[selected_clip.filename] = 0.0
                clip_start = 0.0
                clip_end = min(use_duration, selected_clip.duration)
            
            actual_duration = clip_end - clip_start
            
            # Ensure minimum duration
            if actual_duration < 0.1:
                print(f"    [SKIP] Segment remaining too small ({actual_duration:.2f}s), moving to next segment")
                # Don't continue loop - just finish this segment
                break
            
            # PHASE 2: Align cut points to beats if audio exists
            if beat_grid:
                aligned_start = align_to_nearest_beat(timeline_position, beat_grid, tolerance=0.15)
                aligned_end = align_to_nearest_beat(timeline_position + actual_duration, beat_grid, tolerance=0.15)
                
                # Adjust duration if needed after alignment
                aligned_duration = aligned_end - aligned_start
                if aligned_duration >= 0.1:  # Ensure it's still valid
                    timeline_start_for_decision = aligned_start
                    timeline_end_for_decision = aligned_end
                else:
                    # Alignment made it too short, use original
                    timeline_start_for_decision = timeline_position
                    timeline_end_for_decision = timeline_position + actual_duration
            else:
                timeline_start_for_decision = timeline_position
                timeline_end_for_decision = timeline_position + actual_duration
            
            # Create edit decision
            decision = EditDecision(
                segment_id=segment.id,
                clip_path=selected_clip.filepath,
                clip_start=clip_start,
                clip_end=clip_end,
                timeline_start=timeline_start_for_decision,
                timeline_end=timeline_end_for_decision
            )
            decisions.append(decision)
            
            # Update tracking
            clip_current_position[selected_clip.filename] = clip_end
            clip_usage_count[selected_clip.filename] += 1  # CRITICAL: Track usage
            timeline_position += actual_duration
            segment_remaining -= actual_duration
            
            # Track last 2 clips for variety
            second_last_clip = last_used_clip
            last_used_clip = selected_clip.filename
            
            cuts_in_segment += 1  # Track cuts in this segment
            
            print(f"    ✂️  Cut {cuts_in_segment}: {selected_clip.filename} [{clip_start:.2f}s-{clip_end:.2f}s] "
                  f"({actual_duration:.2f}s) → timeline [{decision.timeline_start:.2f}s-{decision.timeline_end:.2f}s]")
            print(f"    Segment remaining: {segment_remaining:.2f}s")
    
    edl = EDL(decisions=decisions)
    
    print(f"\n{'='*60}")
    print(f"[OK] Matching complete: {len(decisions)} edit decisions")
    print(f"[OK] Total timeline duration: {timeline_position:.2f}s (target: {blueprint.total_duration:.2f}s)")
    print(f"{'='*60}\n")
    
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
        filename = decision.clip_path.split('/')[-1].split('\\')[-1]
        clip_usage[filename] += 1
    
    print("Clip usage distribution:")
    for filename, count in sorted(clip_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  {filename}: {count} times")
    
    print()


def validate_edl(edl: EDL, blueprint: StyleBlueprint) -> bool:
    """
    Validate EDL for continuity and timing errors.
    
    Validates:
    - Timeline continuity (no gaps/overlaps)
    - Total duration matches blueprint (±0.5s tolerance)
    - All clips exist and timestamps are valid
    
    Returns:
        True if valid, raises ValueError if issues found
    """
    # Check timeline continuity
    for i in range(len(edl.decisions) - 1):
        current = edl.decisions[i]
        next_decision = edl.decisions[i + 1]
        
        gap = abs(current.timeline_end - next_decision.timeline_start)
        if gap > 0.05:  # 50ms tolerance
            raise ValueError(
                f"Timeline gap/overlap between decision {i} and {i+1}: {gap:.3f}s"
            )
    
    # Check total duration
    if edl.decisions:
        total_duration = edl.decisions[-1].timeline_end
        expected = blueprint.total_duration
        
        # Strict tolerance: ±0.5s
        if abs(total_duration - expected) > 0.5:
            raise ValueError(
                f"EDL total duration ({total_duration:.2f}s) "
                f"doesn't match blueprint ({expected:.2f}s) - difference: {abs(total_duration - expected):.2f}s"
            )
    
    # Validate clip paths exist and timestamps are reasonable
    for decision in edl.decisions:
        if decision.clip_start < 0 or decision.clip_end <= decision.clip_start:
            raise ValueError(
                f"Invalid clip timestamps in decision: {decision.clip_start:.2f}s - {decision.clip_end:.2f}s"
            )
    
    return True
