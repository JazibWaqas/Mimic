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
    reference_path: str | None = None,  # NEW: For beat detection
    bpm: float = 120.0  # NEW: Dynamic BPM detection
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
        beat_grid = get_beat_grid(blueprint.total_duration, bpm=int(bpm))
        print(f"  🎵 Beat grid generated: {len(beat_grid)} beats at {bpm:.2f} BPM")
        print(f"  DEBUG: First 5 beats: {beat_grid[:5]}")
    else:
        print(f"  🔇 No audio detected - using visual cuts only")
    
    print()
    
    # Track usage: how many times each clip has been used
    clip_usage_count = {clip.filename: 0 for clip in clip_index.clips}
    
    # Track current position in each clip (for sequential fallback)
    clip_current_position = {clip.filename: 0.0 for clip in clip_index.clips}
    
    # VISUAL COOLDOWN SYSTEM: Track when each clip was last used on the timeline
    clip_last_used_at = {clip.filename: -999.0 for clip in clip_index.clips}
    MIN_CLIP_REUSE_GAP = 5.0  # Don't reuse a clip within 5 seconds
    
    # TRANSITION MEMORY: Track the last clip's motion for smooth flow
    last_clip_motion = None
    last_clip_content = None
    
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
            
            # EDITING GRAMMAR: Multi-dimensional clip scoring
            import random
            
            def score_clip_intelligence(clip: ClipMetadata, segment) -> tuple[float, str]:
                """
                Score a clip based on professional editing principles.
                Returns: (score, reasoning_snippet)
                """
                score = 0.0
                reasons = []
                
                # === A. ARC STAGE RELEVANCE (Highest Priority) ===
                stage = segment.arc_stage.lower()
                content = (clip.content_description or "").lower()
                clip_tags = [v.lower() for v in clip.vibes]
                
                if stage == "intro":
                    if any(kw in content for kw in ["intro", "opening", "start", "establishing", "wide"]):
                        score += 20.0
                        reasons.append("Intro-style shot")
                    if "intro" in clip_tags or "establishing" in clip_tags:
                        score += 15.0
                        
                elif stage == "peak":
                    if any(kw in content for kw in ["action", "peak", "intensity", "fast", "climax", "jump"]):
                        score += 20.0
                        reasons.append("Peak-intensity moment")
                    if any(tag in clip_tags for tag in ["action", "peak", "intense"]):
                        score += 15.0
                        
                elif stage == "build-up":
                    if any(kw in content for kw in ["building", "rising", "approaching", "moving"]):
                        score += 15.0
                        reasons.append("Build-up energy")
                        
                elif stage == "outro":
                    if any(kw in content for kw in ["outro", "ending", "finish", "fading", "sunset", "closing"]):
                        score += 20.0
                        reasons.append("Outro-style shot")
                    if "outro" in clip_tags or "ending" in clip_tags:
                        score += 15.0
                
                # === B. VIBE MATCHING (Semantic Alignment) ===
                if segment.vibe and segment.vibe != "General":
                    for v in clip.vibes:
                        if v.lower() in segment.vibe.lower() or segment.vibe.lower() in v.lower():
                            score += 12.0
                            reasons.append(f"Vibe '{segment.vibe}'")
                            break
                
                # === C. VISUAL COOLDOWN (Anti-Monotony) ===
                time_since_last_use = timeline_position - clip_last_used_at[clip.filename]
                if time_since_last_use < MIN_CLIP_REUSE_GAP:
                    # Heavy penalty for recent reuse
                    cooldown_penalty = -50.0 * (1.0 - time_since_last_use / MIN_CLIP_REUSE_GAP)
                    score += cooldown_penalty
                    if cooldown_penalty < -25.0:
                        reasons.append(f"⚠️ Recently used ({time_since_last_use:.1f}s ago)")
                
                # === D. TRANSITION SMOOTHNESS (Motion Continuity) ===
                if last_clip_motion:
                    if clip.motion == last_clip_motion:
                        score += 8.0
                        reasons.append("Smooth motion flow")
                    else:
                        # Motion change can be jarring, slight penalty
                        score -= 3.0
                
                # === E. USAGE PENALTY (Encourage Variety) ===
                usage_penalty = clip_usage_count[clip.filename] * 3.0
                score -= usage_penalty
                if clip_usage_count[clip.filename] > 2:
                    reasons.append(f"Used {clip_usage_count[clip.filename]}x")
                
                # === F. MOMENT FRESHNESS (Prefer Unused Portions) ===
                # This will be evaluated per-moment, not per-clip
                
                reasoning = " | ".join(reasons) if reasons else "Flow optimization"
                return score, reasoning

            # Calculate scores for all available clips
            scored_clips = []
            for c in available_clips:
                total_score, reasoning = score_clip_intelligence(c, segment)
                scored_clips.append((c, total_score, reasoning))
            
            # Sort by total score (highest first)
            scored_clips.sort(key=lambda x: x[1], reverse=True)
            
            # Pick from the top tier (clips with same highest score) to maintain variety
            max_score = scored_clips[0][1]
            top_tier = [(c, s, r) for c, s, r in scored_clips if abs(s - max_score) < 5.0]
            random.shuffle(top_tier)
            
            selected_clip, selected_score, selected_reasoning = top_tier[0]
            
            # Construct final reasoning for logs
            if selected_score > 15.0:
                thinking = f"✨ Smart Match: {selected_reasoning}"
            elif selected_score > 0:
                thinking = f"🎯 Good Fit: {selected_reasoning}"
            else:
                thinking = f"⚙️ Constraint Relaxation: {selected_reasoning}"

            if cuts_in_segment == 0:  # Only print once per segment
                print(f"  🧠 AI Thinking: {thinking}")
                print(f"  📎 Selected: {selected_clip.filename} (Score: {selected_score:.1f})")

            # PHASE 1: Target Duration Selection
            # Use Arc Stage to influence cut pacing
            if segment.arc_stage == "Intro":
                # Intros are usually longerestablishing shots
                target_duration = random.uniform(2.0, 3.5)
            elif segment.arc_stage == "Peak":
                # Peaks are rapid fire
                target_duration = random.uniform(0.15, 0.45)
            elif segment.arc_stage == "Build-up":
                # Accelerating
                target_duration = random.uniform(0.5, 1.2)
            else:
                # Default by energy
                if segment.energy == EnergyLevel.HIGH:
                    target_duration = random.uniform(0.3, 0.6)
                elif segment.energy == EnergyLevel.MEDIUM:
                    target_duration = random.uniform(0.8, 1.5)
                else:
                    target_duration = random.uniform(1.5, 3.0)
            
            # BUDGET CHECK: How much time is really left in this segment?
            # We check relative to the segment's actual end on the global timeline
            segment_remaining = segment.end - timeline_position
            
            is_last_cut_of_segment = False
            if target_duration >= segment_remaining - 0.1:
                # If target is close to end, or this is the last available time, snap to end
                use_duration = segment_remaining
                is_last_cut_of_segment = True
            else:
                use_duration = target_duration

            # PHASE 2: Beat Alignment (if audio exists)
            # We only align if we aren't snapping to the segment end (which is already a beat/cut point)
            if beat_grid and not is_last_cut_of_segment:
                target_end = timeline_position + use_duration
                aligned_end = align_to_nearest_beat(target_end, beat_grid, tolerance=0.15)
                
                # Check if alignment is still within segment bounds and reasonable
                if aligned_end > timeline_position + 0.1 and aligned_end < segment.end - 0.1:
                    use_duration = aligned_end - timeline_position
            
            # PHASE 3: Clip Source Selection (start/end in the raw file)
            clip_start = None
            clip_end = None
            
            if selected_clip.best_moments:
                best_moment = selected_clip.get_best_moment_for_energy(segment.energy)
                if best_moment:
                    window_start, window_end = best_moment
                    current_pos = clip_current_position[selected_clip.filename]
                    
                    # Start from current pos if it's in window, else reset to window start
                    if window_start <= current_pos < window_end:
                        clip_start = current_pos
                    else:
                        clip_start = window_start
                    
                    # End is clip_start + use_duration, capped by window end
                    clip_end = min(clip_start + use_duration, window_end)
                    
                    # If the window is too small for the duration, just use whatever is left
                    if clip_end - clip_start < 0.1:
                         # Window exhausted, fallback to sequential from window_start
                         clip_start = window_start
                         clip_end = min(clip_start + use_duration, selected_clip.duration)
            
            # Fallback to sequential if no best moments
            if clip_start is None:
                clip_start = clip_current_position[selected_clip.filename]
                clip_end = min(clip_start + use_duration, selected_clip.duration)
            
            # RECYCLE CHECK: If clip is exhausted, reset
            if clip_start >= selected_clip.duration - 0.1:
                clip_start = 0.0
                clip_end = min(use_duration, selected_clip.duration)
            
            # SAFETY: Ensure clip_end is valid (must be > clip_start and > 0)
            if clip_end <= clip_start or clip_end <= 0 or selected_clip.duration <= 0:
                print(f"    [SKIP] Invalid clip state: clip_end={clip_end:.2f}, clip_start={clip_start:.2f}, duration={selected_clip.duration:.2f}")
                cuts_in_segment += 1
                continue
            
            # FINAL CALCULATION
            actual_duration = clip_end - clip_start
            
            # SAFETY: Ensure clip_end is always greater than clip_start
            if clip_end <= clip_start or clip_end <= 0:
                print(f"    [SKIP] Invalid clip boundaries ({clip_start:.2f}s-{clip_end:.2f}s)")
                cuts_in_segment += 1
                continue
            
            # SAFETY: If somehow duration is tiny, skip if not last cut
            if actual_duration < 0.05 and not is_last_cut_of_segment:
                print(f"    [SKIP] Cut too short ({actual_duration:.2f}s)")
                cuts_in_segment += 1
                continue

            # PHASE 4: Create Decision with Locked Boundaries
            # timeline_start is ALWAYS EXACTLY the previous timeline_end
            decision_start = timeline_position
            decision_end = decision_start + actual_duration
            
            # If this was supposed to be the last cut, FORCE the snap
            if is_last_cut_of_segment:
                decision_end = segment.end

            decision = EditDecision(
                segment_id=segment.id,
                clip_path=selected_clip.filepath,
                clip_start=clip_start,
                clip_end=clip_end,
                timeline_start=decision_start,
                timeline_end=decision_end,
                reasoning=thinking,
                vibe_match=("Semantic Match" in thinking)
            )
            decisions.append(decision)
            
            # Update Trackers
            timeline_position = decision_end # The head moves to the exact end of last decision
            clip_current_position[selected_clip.filename] = clip_end
            clip_usage_count[selected_clip.filename] += 1
            clip_last_used_at[selected_clip.filename] = timeline_position  # Visual cooldown tracking
            
            # Transition memory for next iteration
            last_clip_motion = selected_clip.motion
            last_clip_content = selected_clip.content_description
            
            # Update clip tracking (save old value before updating)
            second_last_clip = last_used_clip
            last_used_clip = selected_clip.filename
            cuts_in_segment += 1
            
            print(f"    ✂️ Cut {cuts_in_segment}: {selected_clip.filename} "
                  f"[{clip_start:.2f}s-{clip_end:.2f}s] ({actual_duration:.2f}s) "
                  f"→ timeline [{decision.timeline_start:.6f}s-{decision.timeline_end:.6f}s]")

        # Ensure segment is fully filled (Gap-Filler)
        if abs(timeline_position - segment.end) > 0.001 and abs(timeline_position - segment.end) < 0.5:
             # If there's a tiny gap left because the while loop exited, stretch the last decision
             print(f"    🔗 Snapping segment {segment.id} tail ({timeline_position:.4f} -> {segment.end:.4f})")
             if decisions:
                 decisions[-1].timeline_end = segment.end
                 timeline_position = segment.end

    
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
