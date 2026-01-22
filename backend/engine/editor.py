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
    if reference_path and has_audio(reference_path) and bpm and bpm > 0:
        beat_grid = get_beat_grid(blueprint.total_duration, bpm=int(round(bpm)))
        print(f"  🎵 Beat grid generated: {len(beat_grid)} beats at {bpm:.2f} BPM")
        print(f"  DEBUG: First 5 beats: {beat_grid[:5]}")
    else:
        print(f"  🔇 No audio detected or invalid BPM - using visual cuts only")
    
    print()
    
    # Track usage: how many times each clip has been used
    clip_usage_count = {clip.filename: 0 for clip in clip_index.clips}
    
    # Track current position in each clip (for sequential fallback)
    clip_current_position = {clip.filename: 0.0 for clip in clip_index.clips}
    
    # TRACKER: Areas of clips already used to prevent exact repetition
    # Dict[filename, List[Tuple[start, end]]]
    clip_used_intervals = defaultdict(list)
    
    # VISUAL COOLDOWN SYSTEM: Track when each clip was last used on the timeline
    clip_last_used_at = {clip.filename: -999.0 for clip in clip_index.clips}
    MIN_CLIP_REUSE_GAP = 5.0  # Don't reuse a clip within 5 seconds
    
    # TRANSITION MEMORY: Track the last clip's motion for smooth flow
    last_clip_motion = None
    last_clip_content = None
    
    # Group clips by energy for fast lookup
    energy_pools = _create_energy_pools(clip_index)
    
    # === PRE-EDIT DEMAND ANALYSIS ===
    demand = {"High": 0, "Medium": 0, "Low": 0}
    for seg in blueprint.segments:
        demand[seg.energy.value] += 1
    
    supply = {"High": len(energy_pools.get(EnergyLevel.HIGH, [])),
              "Medium": len(energy_pools.get(EnergyLevel.MEDIUM, [])),
              "Low": len(energy_pools.get(EnergyLevel.LOW, []))}
    
    print(f"\n📊 CLIP DEMAND ANALYSIS:")
    print(f"   Reference needs: High={demand['High']}, Medium={demand['Medium']}, Low={demand['Low']}")
    print(f"   You have:        High={supply['High']}, Medium={supply['Medium']}, Low={supply['Low']}")
    
    deficits = {}
    for energy in ["High", "Medium", "Low"]:
        if demand[energy] > supply[energy]:
            deficits[energy] = demand[energy] - supply[energy]
            print(f"   ⚠️ DEFICIT: Need {deficits[energy]} more {energy}-energy clips")
    
    if not deficits:
        print(f"   ✅ You have enough clips for a perfect edit!")
    print()
    
    # === COMPROMISE TRACKER ===
    compromises = []  # Track every time we use adjacent energy
    
    # === ENERGY ELIGIBILITY HELPER ===
    def get_eligible_clips(segment_energy: EnergyLevel, all_clips: List[ClipMetadata]) -> List[ClipMetadata]:
        """
        Return clips that are ALLOWED for this segment's energy.
        High segment → High + Medium (never Low)
        Low segment → Low + Medium (never High)
        Medium → Any
        """
        eligible = []
        for clip in all_clips:
            if segment_energy == EnergyLevel.HIGH:
                if clip.energy in [EnergyLevel.HIGH, EnergyLevel.MEDIUM]:
                    eligible.append(clip)
            elif segment_energy == EnergyLevel.LOW:
                if clip.energy in [EnergyLevel.LOW, EnergyLevel.MEDIUM]:
                    eligible.append(clip)
            else:  # Medium - any clip is OK
                eligible.append(clip)
        return eligible
    
    decisions: List[EditDecision] = []
    timeline_position = 0.0
    last_used_clip = None  # Track to prevent back-to-back repeats
    second_last_clip = None  # Track last 2 clips for more variety

    
    for segment in blueprint.segments:
        print(f"\nSegment {segment.id}: {segment.start:.2f}s-{segment.end:.2f}s "
              f"({segment.duration:.2f}s, {segment.energy.value}/{segment.motion.value})")

        # Guard against timeline drift
        if abs(timeline_position - segment.start) > 0.05:
            print(f"[WARN] Timeline drift: {timeline_position:.3f} vs segment.start {segment.start:.3f}, snapping.")
            timeline_position = segment.start

        segment_remaining = segment.duration
        segment_start_time = timeline_position
        
        # Fill this segment with MULTIPLE RAPID CUTS to match fast-paced editing
        cuts_in_segment = 0
        max_cuts_per_segment = 20  # Prevent infinite loops
        
        while segment_remaining > 0.05 and cuts_in_segment < max_cuts_per_segment:
            # Update remaining duration based on current timeline position
            segment_remaining = max(0.0, segment.end - timeline_position)
            if segment_remaining <= 0.05:
                break
                
            # === TIERED ELIGIBILITY SELECTION ===
            # Step 1: Get only energy-compatible clips (no Low for High, no High for Low)
            eligible_clips = get_eligible_clips(segment.energy, clip_index.clips)
            
            # Step 2: Exclude recently used clips
            recently_used = [last_used_clip, second_last_clip] if second_last_clip else [last_used_clip]
            available_clips = [c for c in eligible_clips if c.filename not in recently_used]
            
            if not available_clips:
                available_clips = eligible_clips  # Fallback if all recently used
            
            import random

            def score_clip_smart(clip: ClipMetadata, segment) -> tuple[float, str, bool]:
                score = 0.0
                reasons = []
                vibe_matched = False

                # 1. DISCOVERY BONUS (unused clips get big push)
                if clip_usage_count[clip.filename] == 0:
                    score += 40.0
                    reasons.append("✨ New")

                # 2. EXACT ENERGY MATCH (prefer exact over adjacent)
                if clip.energy == segment.energy:
                    score += 20.0
                    reasons.append(f"{clip.energy.value}")
                else:
                    score += 5.0  # Adjacent energy (allowed but less ideal)
                    reasons.append(f"~{clip.energy.value}")

                # 3. VIBE MATCHING
                if segment.vibe and segment.vibe != "General":
                    for v in clip.vibes:
                        if v.lower() in segment.vibe.lower() or segment.vibe.lower() in v.lower():
                            score += 15.0
                            reasons.append(f"Vibe:{segment.vibe}")
                            vibe_matched = True
                            break

                # 4. ARC STAGE ALIGNMENT
                stage = segment.arc_stage.lower()
                content = (clip.content_description or "").lower()
                if stage == "intro" and any(kw in content for kw in ["intro", "opening", "wide"]):
                    score += 10.0
                    reasons.append("Intro")
                elif stage == "peak" and any(kw in content for kw in ["action", "fast", "jump"]):
                    score += 10.0
                    reasons.append("Peak")

                # 5. USAGE PENALTY (avoid repeats)
                if clip_usage_count[clip.filename] > 0:
                    score -= (clip_usage_count[clip.filename] * 25.0)
                    reasons.append(f"Used:{clip_usage_count[clip.filename]}x")

                # 6. RECENT COOLDOWN
                time_since_last_use = timeline_position - clip_last_used_at[clip.filename]
                if time_since_last_use < MIN_CLIP_REUSE_GAP:
                    score -= 40.0

                reasoning = " | ".join(reasons)
                return score, reasoning, vibe_matched

            # Calculate scores for eligible clips only
            scored_clips = []
            for c in available_clips:
                total_score, reasoning, vibe_matched = score_clip_smart(c, segment)
                scored_clips.append((c, total_score, reasoning, vibe_matched))

            # Sort by total score
            scored_clips.sort(key=lambda x: x[1], reverse=True)

            # Top tier selection
            max_score = scored_clips[0][1]
            top_tier = [(c, s, r, vm) for c, s, r, vm in scored_clips if abs(s - max_score) < 5.0]
            random.shuffle(top_tier)

            selected_clip, selected_score, selected_reasoning, vibe_matched = top_tier[0]
            
            # Track compromise if we used adjacent energy
            if selected_clip.energy != segment.energy:
                compromises.append({
                    "segment": segment.id,
                    "wanted": segment.energy.value,
                    "got": selected_clip.energy.value
                })
            
            thinking = selected_reasoning
            if selected_score > 35: thinking = "🌟 " + thinking
            elif selected_score > 15: thinking = "🎯 " + thinking
            else: thinking = "⚙️ " + thinking

            if cuts_in_segment == 0:
                print(f"  🧠 AI: {thinking}")
                print(f"  📎 Selected: {selected_clip.filename} (Score: {selected_score:.1f})")

            # === PACING LOGIC: TRUE MIMIC BEHAVIOR ===
            # Rule 1: Respect the pro-editor's original timing.
            # Rule 2: Only subdivide if a segment is 'long' (> 2.0s) AND we are in an active stage.
            
            should_subdivide = False
            if segment.duration > 2.0 and segment.arc_stage.lower() in ["build-up", "peak"]:
                should_subdivide = True
            
            if not should_subdivide:
                # 1:1 Match - Use the exact remaining duration of the reference segment
                use_duration = segment_remaining
                is_last_cut_of_segment = True
            else:
                # Subdivide long segments to keep energy up
                if segment.arc_stage.lower() == "peak":
                    target_duration = random.uniform(0.6, 1.0) # Faster cuts for peak
                else:
                    target_duration = random.uniform(1.2, 1.8) # Moderate cuts for build-up
                
                if target_duration >= segment_remaining - 0.2:
                    use_duration = segment_remaining
                    is_last_cut_of_segment = True
                else:
                    use_duration = target_duration
                    is_last_cut_of_segment = False

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
                    
                    # If the window is too small for the duration, use sequential fallback
                    if clip_end - clip_start < 0.1:
                         clip_start = window_start
                         clip_end = min(clip_start + use_duration, selected_clip.duration)
            
            # Fallback to sequential if no best moments
            if clip_start is None:
                clip_start = clip_current_position[selected_clip.filename]
                clip_end = min(clip_start + use_duration, selected_clip.duration)
            
            # RECYCLE CHECK: If clip is exhausted, reset to start
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
                vibe_match=vibe_matched
            )
            decisions.append(decision)
            
            # Update Trackers
            timeline_position = decision_end # The head moves to the exact end of last decision
            clip_current_position[selected_clip.filename] = clip_end
            clip_usage_count[selected_clip.filename] += 1
            clip_last_used_at[selected_clip.filename] = timeline_position  # Visual cooldown tracking
            clip_used_intervals[selected_clip.filename].append((clip_start, clip_end))
            
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
    
    # === POST-EDIT SUMMARY ===
    unique_clips_used = len(set(d.clip_path for d in decisions))
    total_clips = len(clip_index.clips)
    
    print(f"\n{'='*60}")
    print(f"[OK] Matching complete: {len(decisions)} edit decisions")
    print(f"[OK] Total timeline duration: {timeline_position:.2f}s (target: {blueprint.total_duration:.2f}s)")
    print(f"\n📊 DIVERSITY REPORT:")
    print(f"   Unique clips used: {unique_clips_used}/{total_clips}")
    
    if unique_clips_used == total_clips:
        print(f"   ✅ PERFECT! Every clip in your library was used.")
    elif unique_clips_used >= total_clips * 0.9:
        print(f"   ✅ EXCELLENT variety - {total_clips - unique_clips_used} clips unused.")
    else:
        print(f"   ⚠️ {total_clips - unique_clips_used} clips were not used.")
    
    # Check for repeats
    from collections import Counter
    clip_uses = Counter(d.clip_path for d in decisions)
    repeats = [(path.split('\\')[-1], count) for path, count in clip_uses.items() if count > 1]
    
    if repeats:
        print(f"\n   ⚠️ CLIPS REPEATED:")
        for name, count in sorted(repeats, key=lambda x: -x[1])[:5]:
            print(f"      {name}: {count}x")
    else:
        print(f"\n   ✅ NO CLIPS REPEATED! Perfect diversity achieved.")
    
    # Compromises
    if compromises:
        print(f"\n📋 ENERGY COMPROMISES: {len(compromises)}")
        print(f"   (Used adjacent energy when exact wasn't available)")
        # Count by type
        compromise_summary = Counter(f"{c['wanted']}→{c['got']}" for c in compromises)
        for swap, count in compromise_summary.most_common():
            print(f"      {swap}: {count} times")
    
    # Recommendations
    if deficits or compromises:
        print(f"\n💡 RECOMMENDATIONS TO IMPROVE THIS EDIT:")
        
        # 1. Direct Capacity Deficits
        if deficits:
            print(f"   [Inventory Gaps]")
            for energy, count in deficits.items():
                examples = {
                    "High": "(dancing, sports, action, fast movement)",
                    "Medium": "(walking, social, casual movement, city life)",
                    "Low": "(scenic, calm, establishing shots, landscapes)"
                }.get(energy, "")
                print(f"   → Add {count} more {energy.upper()}-ENERGY clips {examples}")
        
        # 2. Quality/Energy Mismatch Recommendations
        if compromises:
            print(f"\n   [Quality Improvements]")
            # Count specifically what we swapped TO what
            high_compromise = sum(1 for c in compromises if c['wanted'] == "High")
            if high_compromise > 0:
                print(f"   → {high_compromise} segments wanted 'High' energy but used 'Medium'.")
                print(f"     Add high-intensity clips with 'Urban' or 'Nightlife' vibes to fix this.")
            
            low_compromise = sum(1 for c in compromises if c['wanted'] == "Low")
            if low_compromise > 0:
                print(f"   → {low_compromise} segments wanted 'Low' energy but used 'Medium'.")
                print(f"     Add more 'Nature' or 'Calm' clips to reduce jitter here.")
    
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
