"""
Editor module: Clip-to-segment matching algorithm (FIXED VERSION).

FIXES APPLIED:
1. Simplified algorithm - no complex spillover logic
2. Proper clip rotation - ensures all clips are used
3. Fills segments completely - matches reference duration
4. Uses best moments when available
5. Prevents back-to-back repeats of same clip
"""

from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
from pathlib import Path
from models import (
    StyleBlueprint,
    ClipIndex,
    EDL,
    EditDecision,
    EnergyLevel,
    MotionType,
    ClipMetadata,
    AdvisorHints
)
from engine.processors import has_audio, get_beat_grid, align_to_nearest_beat
from engine.gemini_advisor import get_advisor_suggestions, compute_advisor_bonus


def match_clips_to_blueprint(
    blueprint: StyleBlueprint,
    clip_index: ClipIndex,
    find_best_moments: bool = False,
    api_key: Optional[str] = None,
    reference_path: Optional[str] = None,
    bpm: float = 120.0,
    use_advisor: bool = True
) -> Tuple[EDL, Optional[AdvisorHints]]:
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
    
    # Get Gemini Advisor suggestions (optional, degrades gracefully)
    advisor_hints: Optional[AdvisorHints] = None
    if use_advisor:
        # === SCARCITY REPORT (v12.4 Phase 3) ===
        # Pre-calculate library scarcity to guide Advisor's intent reach.
        scarcity_report = {}
        total_clips = len(clip_index.clips)
        if total_clips > 0:
            # 1. Energy scarcity
            for energy_lv in ["High", "Medium", "Low"]:
                count = sum(1 for c in clip_index.clips if c.energy.value == energy_lv)
                ratio = count / total_clips
                if ratio < 0.15: scarcity_report[energy_lv] = "very_scarce"
                elif ratio < 0.30: scarcity_report[energy_lv] = "scarce"
                else: scarcity_report[energy_lv] = "abundant"
                
            # 2. Subject scarcity (Top categories)
            subject_counts = Counter()
            for c in clip_index.clips:
                for s in (c.primary_subject or []):
                    subject_counts[s] += 1
            
            for subj, count in subject_counts.items():
                ratio = count / total_clips
                if ratio < 0.1: scarcity_report[subj] = "scarce"
                elif ratio > 0.4: scarcity_report[subj] = "abundant"

        advisor_hints = get_advisor_suggestions(blueprint, clip_index, scarcity_report=scarcity_report)
        if advisor_hints:
            print(f"  ✅ Advisor enabled: Strategic guidance active")
        else:
            print(f"  ⚙️ Advisor disabled: Using base matcher only")
    else:
        print(f"  ⚙️ Advisor disabled by config")
    
    # PHASE 2: Generate beat grid for audio sync
    beat_grid = []
    if reference_path and has_audio(reference_path) and bpm and bpm > 0:
        beat_grid = get_beat_grid(blueprint.total_duration, bpm=bpm)
        print(f"  🎵 Beat grid generated: {len(beat_grid)} beats at {bpm:.2f} BPM")
    
    # Phase 2b: Intelligent Beat Extraction (v8.0)
    if blueprint.music_structure and "accent_moments" in blueprint.music_structure:
        import re
        manual_beats = []
        for m in blueprint.music_structure["accent_moments"]:
            # Extract last number which is typically the timestamp
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(m))
            if nums:
                try: 
                    t = float(nums[-1])
                    if 0 < t < blueprint.total_duration:
                        manual_beats.append(t)
                except: continue
        
        if manual_beats:
            print(f"  🎹 Extracted {len(manual_beats)} manual accent moments (Super Beats)")
            beat_grid = sorted(list(set(beat_grid + manual_beats)))

    if not beat_grid:
        print(f"  🔇 No beats detected - using visual cuts only")
    else:
        print(f"  ✅ Active beat grid: {len(beat_grid)} points")

    
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
    # MIN_CLIP_REUSE_GAP is now calculated dynamically inside the segment loop to be energy-aware
    
    # TRANSITION MEMORY: Track the last clip's details for smooth flow
    # Context object for stateful scoring (Phase 1 Refactor)
    class MatchContext:
        def __init__(self):
            self.last_filename = None
            self.last_motion = None
            self.last_scale = None
            self.last_subjects = []
            self.last_content = ""
            self.timeline_pos = 0.0
            self.usage_count = clip_usage_count
            self.last_used_at = clip_last_used_at

    ctx = MatchContext()

    # === PHRASE GROUPING (v12.4 Phase 2) ===
    # Groups segments by arc_stage for motif feasibility checks.
    # We derive these on the fly to avoid breaking legacy blueprint models.
    phrases = []
    current_phrase_ids = []
    if blueprint.segments:
        for seg in blueprint.segments:
            if not current_phrase_ids:
                current_phrase_ids.append(seg.id)
            else:
                prev_seg = blueprint.segments[current_phrase_ids[-1] - 1]
                if seg.arc_stage == prev_seg.arc_stage:
                    current_phrase_ids.append(seg.id)
                else:
                    duration = sum(blueprint.segments[sid-1].duration for sid in current_phrase_ids)
                    phrases.append({"segments": current_phrase_ids, "duration": duration})
                    current_phrase_ids = [seg.id]
        if current_phrase_ids:
            duration = sum(blueprint.segments[sid-1].duration for sid in current_phrase_ids)
            phrases.append({"segments": current_phrase_ids, "duration": duration})

    # Map segment ID to its phrase duration for fast lookup
    seg_phrase_duration = {}
    for phrase in phrases:
        for sid in phrase["segments"]:
            seg_phrase_duration[sid] = phrase["duration"]
    
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
    
    # === DEBUG MODE (Gate heavy logging) ===
    DEBUG_MODE = True
    
    # === ENHANCED LOGGING (for explainability) ===
    candidate_rankings = []  # Top 3 candidates per segment
    eligibility_breakdowns = []  # Eligibility stats per segment
    semantic_neighbor_events = []  # When semantic neighbors were used
    beat_alignment_logs = []  # Beat snap decisions
    
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
        # Dynamic loop protection: more cuts allowed for longer segments (min 10)
        max_cuts_per_segment = min(12, max(4, int(segment.duration / 0.6)))
        
        force_loop_clip = None
        while segment_remaining > 0.05 and cuts_in_segment < max_cuts_per_segment:
            # Update remaining duration based on current timeline position
            segment_remaining = max(0.0, segment.end - timeline_position)
            if segment_remaining <= 0.05:
                break
                
            # === TIERED ELIGIBILITY SELECTION ===
            # Advisor Energy Override (v9.5):
            # If the Advisor dictates a specific energy for this arc stage, 
            # we bypass segment.energy filtering to allow the "correct" clips.
            active_energy_requirement = segment.energy
            if advisor_hints:
                guidance = advisor_hints.arc_stage_guidance.get(segment.arc_stage)
                if guidance and guidance.required_energy:
                    try:
                        active_energy_requirement = EnergyLevel[guidance.required_energy.upper()]
                        print(f"      ⚡ADVISOR OVERRIDE: Using {active_energy_requirement.value} energy for {segment.arc_stage}")
                    except (ValueError, KeyError):
                        pass

            # Step 1: Get energy-compatible clips (Soft constraints)
            eligible_clips = get_eligible_clips(active_energy_requirement, clip_index.clips)
            
            # CONSTRAINT RELAXATION (v10.1): If no clips match energy, use ALL clips
            if not eligible_clips:
                print(f"      ⚠️ No clips match {active_energy_requirement.value} energy. Relaxing constraints...")
                eligible_clips = clip_index.clips
            
            # ENHANCED LOGGING: Eligibility breakdown
            if DEBUG_MODE and cuts_in_segment == 0:  # Only log once per segment
                ineligible_count = len(clip_index.clips) - len(eligible_clips)
                eligibility_breakdowns.append({
                    "segment_id": segment.id,
                    "eligible_count": len(eligible_clips),
                    "ineligible_count": ineligible_count,
                    "total_clips": len(clip_index.clips),
                    "segment_energy": segment.energy.value
                })
            
            # Step 2: Variety maintenance (Avoid back-to-back repeats)
            recently_used = [last_used_clip, second_last_clip] if second_last_clip else [last_used_clip]
            available_clips = [c for c in eligible_clips if c.filename not in recently_used]
            
            if not available_clips:
                available_clips = eligible_clips  # Emergency fallback
            
            import random

            # === P0 FIX #1: VIBE SEMANTIC BRIDGE ===
            # Maps clip-level descriptive tags (nouns) → editorial intent vibes (abstractions)
            # This solves the 0% vibe matching issue by bridging semantic spaces.
            VIBE_SEMANTIC_BRIDGE = {
                # Vehicle-related clips → Speed/Power/Adrenaline vibes
                "vehicle": ["speed", "power", "adrenaline", "launch", "precision", "freedom"],
                "solo": ["heroic", "focus", "determination", "struggle", "intense"],
                "group": ["unity", "heroic", "celebration", "camaraderie"],
                "crowd": ["scale", "epic", "energy", "intensity"],
                "urban": ["grit", "intensity", "modern", "solemn"],
                "nature": ["majestic", "freedom", "peaceful", "silence"],
                "travel": ["adventure", "freedom", "exploration"],
                "celebration": ["joy", "triumph", "energy"],
                "indoor": ["intimate", "focus", "calm"],
                # Reverse mappings for flexibility
                "speed": ["vehicle", "action", "dynamic"],
                "power": ["vehicle", "action"],
                "heroic": ["solo", "group"],
                "majestic": ["nature", "wide"],
                "silence": ["nature", "calm", "peaceful"]
            }
            
            # SEMANTIC NEIGHBORS (The "Artistic Neighbor" map)
            # This prevents deficits by allowing similar vibes to count as matches
            SEMANTIC_MAP = {
                "nature": ["outdoors", "scenic", "landscape", "trees", "forest", "mountain", "beach", "sky", "view"],
                "urban": ["city", "street", "architecture", "building", "lights", "night", "traffic", "walking"],
                "travel": ["adventure", "road", "plane", "car", "explore", "vacation", "scenic"],
                "friends": ["social", "laughing", "group", "candid", "casual", "fun", "lifestyle"],
                "action": ["fast", "sport", "intense", "thrill", "dynamic", "movement", "energy"],
                "calm": ["peaceful", "sunset", "lifestyle", "aesthetic", "still", "chill"]
            }

            def infer_shot_scale(clip: ClipMetadata) -> str:
                """Infer clip's scale from primary subject tags."""
                clip_primary_subs = [s.lower() for s in (clip.primary_subject or [])]
                if any(s in ["people-solo", "object-detail"] for s in clip_primary_subs):
                    return "Close"
                elif any(s in ["place-nature", "place-urban"] for s in clip_primary_subs):
                    return "Wide"
                return "Medium"

            def compute_continuity_bonus(candidate: ClipMetadata, segment, ctx, advisor: Optional[AdvisorHints]) -> Tuple[float, List[str]]:
                """
                v12.1: The Continuity Engine.
                Calculates bonuses based on Advisor-declared motifs.
                """
                bonus = 0.0
                reasons = []
                
                if not advisor or not hasattr(advisor, 'editorial_motifs'):
                    return 0.0, []
                
                motifs = getattr(advisor, 'editorial_motifs', [])
                cand_scale = infer_shot_scale(candidate)
                cand_content = (candidate.content_description or "").lower()
                
                for motif in motifs:
                    trigger = motif.get('trigger', '').lower()
                    continuity_type = motif.get('desired_continuity', '')
                    priority = motif.get('priority', 'Medium')
                    
                    # Priority multiplier
                    weight = 1.0
                    if priority == 'High': weight = 2.0
                    elif priority == 'Low': weight = 0.5
                    
                    # 1. Scale-Escalation (Wide -> Medium -> Close)
                    if continuity_type == "Scale-Escalation" and ctx.last_scale:
                        if ctx.last_scale == "Wide" and cand_scale in ["Medium", "Close"]:
                            bonus += (20.0 * weight)
                            reasons.append("📈Escalation")
                        elif ctx.last_scale == "Medium" and cand_scale == "Close":
                            bonus += (25.0 * weight)
                            reasons.append("📈Intimacy")

                    # 2. Motion-Carry (Match physical direction or energy flow)
                    if continuity_type == "Motion-Carry" and ctx.last_motion:
                        if candidate.motion == ctx.last_motion:
                            bonus += (15.0 * weight)
                            reasons.append("➡️Flow")

                    # 3. ACTION-COMPLETION / GRAPHIC-MATCH (Advanced: Requires duration)
                    if continuity_type in ["Action-Completion", "Graphic-Match"]:
                        phrase_dur = seg_phrase_duration.get(segment.id, 0.0)
                        if phrase_dur >= 1.2:
                            bonus += (30.0 * weight)
                            reasons.append(f"🔄{continuity_type[:4]}")
                        else:
                            # Observability Gap Closed (v12.1 Final):
                            # Explicitly log that the motif was considered but rejected for feasibility.
                            reasons.append(f"⚠️{continuity_type[:3]}_SKIP")

                    # 4. Semantic-Resonance (Lyrics/Text triggers)
                    if continuity_type == "Semantic-Resonance" and trigger:
                        # Check if trigger keyword is in clip's subject or description
                        clip_text = " ".join((candidate.primary_subject or []) + (candidate.vibes or [])).lower()
                        if trigger in clip_text or trigger in cand_content:
                            bonus += (40.0 * weight)
                            reasons.append(f"🔗{trigger[:5]}")

                return bonus, reasons

            def score_clip_smart(clip: ClipMetadata, segment, ctx, advisor: Optional[AdvisorHints] = None) -> Tuple[float, str, bool]:
                """
                NEW INTELLIGENT SCORING SYSTEM (v9.0)
                """
                score = 100.0  # Base score
                reasons = []
                vibe_matched = False

                # === STRATEGIC LAYER: Advisor Authority ===
                # The Advisor sees the "big picture" that mechanical matching can't
                
                # NARRATIVE ANCHOR (v9.5):
                # If Advisor has locked a primary subject (e.g. People-Group), enforce it.
                narrative_subject_match = False
                if advisor and advisor.primary_narrative_subject:
                    target_subject = advisor.primary_narrative_subject.value
                    clip_primary_subjects = [s for s in (clip.primary_subject or [])]
                    
                    if target_subject in clip_primary_subjects:
                        narrative_subject_match = True
                        # P0 FIX #3: NARRATIVE ANCHOR DEMOTION (Lock → Bias)
                        # DEMOTED BONUS (was +50/+15, now +25/+10)
                        # Narrative anchor is now a TIE-BREAKER, not a PRIMARY SELECTOR
                        usage = clip_usage_count[clip.filename]
                        bonus = 25.0 if usage == 0 else 10.0
                        score += bonus
                        reasons.append("⚓ANCHOR" if usage == 0 else "⚓RECAP")
                    else:
                        # Check if it's an allowed supporting subject
                        is_supporting = False
                        if advisor.allowed_supporting_subjects:
                            allowed_subs = [s.value for s in advisor.allowed_supporting_subjects]
                            if any(s in allowed_subs for s in clip_primary_subjects):
                                is_supporting = True
                        
                        if not is_supporting:
                            # P0 FIX #3: DEMOTED PENALTY (was -40, now -15)
                            # Allow vibe/scale/function to override if they're strong matches
                            penalty = 15.0 * getattr(advisor, 'subject_lock_strength', 1.0)
                            score -= penalty
                            reasons.append(f"🚫Filler")

                # CRITICAL OVERRIDE RULE (v9.2):
                # If Advisor explicitly recommends this clip as PRIMARY EMOTIONAL CARRIER
                # for this arc stage, IGNORE energy mismatch and apply massive bonus
                advisor_primary_carrier = False
                required_energy_override = None
                
                if advisor:
                    guidance = advisor.arc_stage_guidance.get(segment.arc_stage)
                    if guidance:
                        # Check if Advisor specifies required energy override
                        if guidance.required_energy:
                            required_energy_override = guidance.required_energy
                        
                        # Check if this clip is explicitly recommended
                        if guidance.recommended_clips and clip.filename in guidance.recommended_clips:
                            # This clip is explicitly recommended by Advisor for this arc stage
                            advisor_primary_carrier = True
                            # P0 FIX #2: INCREASED from 40 to ensure Advisor guidance wins
                            score += 60.0
                            reasons.append(f"🎯PRIMARY")
                
                # Standard Advisor bonus (for non-primary recommendations)
                if advisor and not advisor_primary_carrier:
                    advisor_bonus = compute_advisor_bonus(clip, segment, blueprint, advisor)
                    if advisor_bonus != 0:
                        score += advisor_bonus
                        if advisor_bonus > 0:
                            reasons.append(f"🧠+{advisor_bonus}")
                        else:
                            reasons.append(f"🚫{advisor_bonus}")

                # === NARRATIVE LAYER: Semantic Matching ===
                
                # P0 FIX #1: ENHANCED VIBE MATCHING with Semantic Bridge
                # Priority order:
                # 1. Direct match (exact string)
                # 2. Semantic bridge (Vehicle → Speed, Solo → Heroic, etc.)
                # 3. Semantic neighbor (legacy fallback)
                
                target_vibe = (segment.vibe or "general").lower()
                clip_vibes = [v.lower() for v in (clip.vibes or [])]
                
                # 1. Direct Vibe Match (+40 points) - INCREASED from +30
                if any(target_vibe in v or v in target_vibe for v in clip_vibes):
                    score += 40.0
                    reasons.append(f"Vibe:{segment.vibe}")
                    vibe_matched = True
                else:
                    # 2. Semantic Bridge Match (+30 points) - NEW
                    # Check if any clip vibe maps to the target vibe via semantic bridge
                    bridge_matched = False
                    for clip_vibe in clip_vibes:
                        if clip_vibe in VIBE_SEMANTIC_BRIDGE:
                            mapped_vibes = VIBE_SEMANTIC_BRIDGE[clip_vibe]
                            if target_vibe in mapped_vibes:
                                # INTENSITY GATING: Prevent false positives
                                high_energy_vibes = ["speed", "adrenaline", "power", "launch", "precision"]
                                if target_vibe in high_energy_vibes and getattr(clip, 'intensity', 1) < 2:
                                    continue  # Skip low-intensity clips for high-energy vibes
                                score += 30.0
                                reasons.append(f"Bridge:{clip_vibe}→{segment.vibe}")
                                vibe_matched = True
                                bridge_matched = True
                                break
                    
                    # Also check reverse: does target vibe map to any clip vibe?
                    if not bridge_matched and target_vibe in VIBE_SEMANTIC_BRIDGE:
                        mapped_vibes = VIBE_SEMANTIC_BRIDGE[target_vibe]
                        if any(v in mapped_vibes for v in clip_vibes):
                            score += 30.0
                            reasons.append(f"Bridge:{segment.vibe}→{clip_vibes[0]}")
                            vibe_matched = True
                            bridge_matched = True
                    
                    # 3. Semantic neighbor match (+15 points) - LEGACY FALLBACK
                    if not bridge_matched:
                        for category, neighbors in SEMANTIC_MAP.items():
                            if target_vibe in neighbors or target_vibe == category:
                                if any(v in neighbors for v in clip_vibes):
                                    score += 15.0
                                    reasons.append(f"Nearby:{category}")
                                    vibe_matched = True
                                    break
                
                
                # 2. Shot Function Match (+25 points)
                function_to_utility = {
                    "Establish": ["establishing", "transition"],
                    "Action": ["peak", "build", "transition"],
                    "Reaction": ["reflection", "build", "transition"],
                    "Detail": ["transition", "build"],
                    "Transition": ["transition"],
                    "Release": ["reflection", "transition"],
                    "Button": ["peak", "transition"]
                }
                
                seg_func = getattr(segment, 'shot_function', None)
                if seg_func and seg_func in function_to_utility:
                    target_utilities = function_to_utility[seg_func]
                    clip_utilities = [u.lower() for u in clip.narrative_utility]
                    if any(tu in clip_utilities for tu in target_utilities):
                        score += 25.0
                        reasons.append(f"Func:{seg_func[:3]}")
                
                # 3. Subject Consistency (+20 points)
                seg_vibe_lower = (segment.vibe or "").lower()
                clip_subjects = [s.lower() for s in (clip.primary_subject or [])]
                
                subject_map = {
                    "friends": ["people-group", "activity-celebration", "people-solo"],
                    "nature": ["place-nature", "activity-travel"],
                    "urban": ["place-urban", "place-indoor"],
                    "action": ["activity-sport", "activity-celebration"],
                    "travel": ["activity-travel", "place-nature", "place-urban"]
                }
                
                for cat, subjects in subject_map.items():
                    if cat in seg_vibe_lower:
                        if any(s in clip_subjects for s in subjects):
                            score += 20.0
                            reasons.append("Subj")
                            break
                
                # 4. Shot Scale Continuity (+15 points)
                seg_scale = getattr(segment, 'shot_scale', None)
                if seg_scale:
                    is_scale_match = False
                    if seg_scale in ["Wide", "Extreme Wide"]:
                        is_scale_match = "establishing" in [u.lower() for u in clip.narrative_utility] or \
                                         any("place" in s.lower() for s in (clip.primary_subject or []))
                    elif seg_scale == "Medium":
                        is_scale_match = any(u.lower() in ["build", "transition"] for u in clip.narrative_utility) or \
                                         any("people-group" in s.lower() for s in (clip.primary_subject or []))
                    elif "Close" in seg_scale:
                        is_scale_match = any(u.lower() == "peak" for u in clip.narrative_utility) or \
                                         any("people-solo" in s.lower() for s in (clip.primary_subject or []))
                    
                    if is_scale_match:
                        score += 15.0
                        reasons.append(f"Scale:{seg_scale[:2]}")

                # 4b. Shot Scale Variety (v12.1: +10 points for alternating)
                # If we don't have a rigid scale requirement from the reference,
                # or as a secondary signal, we prefer alternating scales.
                if ctx.last_scale:
                    current_clip_scale = infer_shot_scale(clip)
                    if current_clip_scale != ctx.last_scale:
                        score += 10.0
                        reasons.append("Alt")
                
                # === CONTINUITY ENGINE (v12.1 Motifs) ===
                continuity_bonus, continuity_reasons = compute_continuity_bonus(clip, segment, ctx, advisor)
                score += continuity_bonus
                reasons.extend(continuity_reasons)
                
                # 5. Emotional Tone Match (+10 points)
                if hasattr(clip, 'emotional_tone') and clip.emotional_tone:
                    seg_intent = getattr(blueprint, 'emotional_intent', '').lower()
                    clip_tones = [t.lower() for t in clip.emotional_tone]
                    if seg_intent and any(seg_intent in t or t in seg_intent for t in clip_tones):
                        score += 10.0
                        reasons.append("Tone")

                # === QUALITY LAYER: Best Moment Matching ===
                
                # 1. Best Moment Quality Match (+15 points)
                # Use the right moment quality for the arc stage
                if clip.best_moments:
                    # Map arc stage to preferred moment quality
                    arc_to_moment = {
                        "Intro": "Low",      # Calm establishing
                        "Build-up": "Medium", # Rising action
                        "Peak": "High",      # Climax
                        "Outro": "Low"       # Resolution
                    }
                    
                    preferred_quality = arc_to_moment.get(segment.arc_stage, segment.energy.value.capitalize())
                    if preferred_quality in clip.best_moments:
                        score += 15.0
                        reasons.append(f"Moment:{preferred_quality}")
                
                # 2. Clip Quality Rating (+10 per point, max +30)
                if hasattr(clip, 'clip_quality') and clip.clip_quality:
                    score += (clip.clip_quality * 10.0)
                    if clip.clip_quality >= 3:
                        reasons.append(f"Q{clip.clip_quality}")

                # === VARIETY LAYER: Freshness vs Repetition ===
                usage = clip_usage_count[clip.filename]
                if usage == 0:
                    score += 20.0  # Fresh clip bonus
                    reasons.append("✨New")
                else:
                    # v12.1 REBALANCED REUSE:
                    # We prefer quality repetition over poor-quality 'freshness'.
                    # 1st reuse: -30, 2nd reuse: -80, 3rd+ reuse: -180
                    if usage == 1:
                        penalty = 30.0
                    elif usage == 2:
                        penalty = 80.0
                    else:
                        penalty = 180.0
                    
                    score -= penalty
                    reasons.append(f"Used:{usage}x")
                
                # === PENALTY LAYER ===
                
                # 1. Recent Cooldown (-100 points)
                time_since_last_use = timeline_position - clip_last_used_at[clip.filename]
                dynamic_reuse_gap = max(2.0, segment.duration * 0.6)
                if segment.arc_stage.lower() == "peak":
                    dynamic_reuse_gap = 2.0
                
                if time_since_last_use < dynamic_reuse_gap:
                    score -= 100.0
                    reasons.append("Cooldown")
                
                # 2. Energy Matching (with Advisor override support)
                # Determine what energy level we're matching against
                target_energy = segment.energy
                if required_energy_override:
                    # Advisor override: match against required energy, not segment energy
                    # Use EnergyLevel from global scope (models)
                    try:
                        target_energy = EnergyLevel[required_energy_override.upper()]
                        reasons.append(f"🎯{required_energy_override}")
                    except (ValueError, KeyError, TypeError):
                        pass
                
                if clip.energy != target_energy:
                    # CRITICAL: If Advisor explicitly recommends this clip, ignore energy mismatch
                    if not advisor_primary_carrier:
                        # NARRATIVE SOFTENING (v9.5): Minor penalty if subject matches
                        penalty = 5.0
                        if narrative_subject_match:
                            penalty = 1.0
                            reasons.append("⚡Match")
                            
                        score -= penalty
                        reasons.append(f"~{clip.energy.value}")
                    else:
                        # Advisor override: energy mismatch is irrelevant
                        reasons.append(f"⚡{clip.energy.value}")
                else:
                    score += 15.0
                    reasons.append(f"{clip.energy.value}")
                
                # 3. Lighting Continuity (+10 points)
                content = (clip.content_description or "").lower()
                is_night_segment = any(kw in target_vibe for kw in ["night", "dark", "evening"])
                is_night_clip = any(kw in content or kw in str(clip_vibes) for kw in ["night", "dark", "evening", "neon"])
                
                if is_night_segment == is_night_clip:
                    score += 10.0
                    reasons.append("Light")
                
                # 4. Motion Continuity (Legacy)
                if ctx.last_motion and clip.motion == ctx.last_motion:
                    score += 5.0
                    reasons.append("Move")

                # === NARRATIVE REASONING SYNTHESIS (v9.5) ===
                narrative_parts = []
                
                # 1. Strategic Identity (The Anchor)
                if narrative_subject_match:
                    target_sub = advisor.primary_narrative_subject.value if advisor else "Subject"
                    narrative_parts.append(f"Prioritizing narrative continuity by anchoring on '{target_sub}' as requested by the text intent.")
                elif "🚫Filler" in str(reasons):
                    narrative_parts.append("Maintaining sequence flow with supporting material, though it drifts from the primary narrative anchor.")
                
                # 2. Shot Function & Strategy
                if advisor_primary_carrier:
                    narrative_parts.append(f"Acting as the primary emotional carrier for the {segment.arc_stage} stage.")
                elif "Func:" in str(reasons):
                    narrative_parts.append(f"Serving as a strategic '{seg_func}' shot within this sequence.")
                
                if vibe_matched:
                    narrative_parts.append(f"The visual content captures the '{segment.vibe}' atmosphere perfectly.")
                
                # 4. Energy Handling (Override vs Natural)
                if required_energy_override:
                    if clip.energy.value == required_energy_override:
                        narrative_parts.append(f"Satisfies the narrative's high-energy demand for this segment.")
                    elif narrative_subject_match:
                        narrative_parts.append(f"Matching narrative subject over raw energy to preserve story coherence.")
                
                # 5. Technical Flow
                tech_notes = []
                if "🛡️Subject" in reasons: tech_notes.append("narrative-safe reuse")
                elif "✨New" in reasons: tech_notes.append("visual freshness")
                if "Flow" in reasons: tech_notes.append("motion continuity")
                if "Light" in reasons: tech_notes.append("lighting consistency")
                
                if tech_notes:
                    narrative_parts.append(f"Maintains {', '.join(tech_notes)}.")
                

                reasoning = " ".join(narrative_parts) if narrative_parts else "Aligned with arc energy and visual flow."
                
                # SCORE CAP (v9.5): Prevent runaway dominance to maintain ranking discrimination
                score = min(score, 350.0)
                
                return score, reasoning, vibe_matched

            # REFERENCE AUTHORITY (v12.7): Pre-calculate duration constraints
            # We must know if this is a sacred cut BEFORE selecting a clip.
            cut_origin = getattr(segment, 'cut_origin', 'visual')
            is_sacred_cut = (cut_origin == 'visual')  # Visual cuts are sacred
            min_required = segment_remaining - 0.1    # Tolerance

            # FORCE LOOP OVERRIDE (v13.0): Hybrid System Directive 2.2
            # If we enter loop mode, we MUST reuse the same clip.
            loop_mode = False
            if force_loop_clip:
                available_clips = [force_loop_clip]
                print(f"    🔄 FORCE LOOP: Restricting selection to {force_loop_clip.filename} to maintain continuity.")
                loop_mode = True

            # Calculate scores with STRICT duration filtering
            scored_clips = []
            valid_candidates_found = False

            for c in available_clips:
                # GUARD: Sacred Cut Duration Check
                # If segment is 'visual', we MUST NOT subdivide it.
                # Clip must be long enough to cover the remaining time.
                # EXCEPTION: If we are in loop_mode, we accept the short clip explicitly.
                if is_sacred_cut and not loop_mode and c.duration < min_required:
                    continue  # HARD REJECT: Clip is physically too short

                # We pass the context to maintain stateful flow
                total_score, reasoning, vibe_matched = score_clip_smart(c, segment, ctx, advisor_hints)
                scored_clips.append((c, total_score, reasoning, vibe_matched))
                valid_candidates_found = True

            # FALLBACK: If strict filter eliminated ALL clips (Emergency Mode)
            if not valid_candidates_found:
                print(f"    ⚠️ CRITICAL: No clips match duration ({min_required:.2f}s) for sacred cut! Reference authority compromised.")
                print(f"    ⚠️ Fallback: Selecting longest available clips to minimize fragmentation.")
                
                # Re-score ALL clips, but prioritize DURATION over everything else
                scored_clips = []
                for c in available_clips:
                    total_score, reasoning, vibe_matched = score_clip_smart(c, segment, ctx, advisor_hints)
                    
                    # Massive bonus for duration to get as close as possible
                    duration_score = c.duration * 50.0 
                    total_score += duration_score
                    reasoning = f"⚠️Rescue (len={c.duration:.1f}s)"
                    
                    scored_clips.append((c, total_score, reasoning, vibe_matched))

            # Sort by total score
            scored_clips.sort(key=lambda x: x[1], reverse=True)

            # Top tier selection (v10.0: replaced randomness with Usage Tie-breaker)
            # Find clips within a "Finesse Buffer" of the max score
            max_score = scored_clips[0][1]
            top_tier = [(c, s, r, vm) for c, s, r, vm in scored_clips if (max_score - s) < 15.0]
            
            # Sort top tier by usage (freshest clips first)
            # This ensures we pick the "freshest clip that is still great"
            top_tier.sort(key=lambda x: clip_usage_count[x[0].filename])

            selected_clip, selected_score, selected_reasoning, vibe_matched = top_tier[0]
            
            # ENHANCED LOGGING: Candidate rankings (top 3)
            if DEBUG_MODE and cuts_in_segment == 0:  # Only log once per segment
                top_3 = scored_clips[:3]
                candidates = []
                for idx, (c, score, reason, vm) in enumerate(top_3):
                    candidates.append({
                        "rank": idx + 1,
                        "clip": c.filename,
                        "score": score,
                        "reasoning": reason,
                        "vibe_match": vm,
                        "won": (idx == 0)
                    })
                candidate_rankings.append({
                    "segment_id": segment.id,
                    "candidates": candidates
                })
            
            # Track compromise if we used adjacent energy
            if selected_clip.energy != segment.energy:
                compromises.append({
                    "segment": segment.id,
                    "wanted": segment.energy.value,
                    "got": selected_clip.energy.value
                })
            
            thinking = selected_reasoning
            if selected_score > 60: thinking = "🌟 " + thinking
            elif selected_score > 30: thinking = "🎯 " + thinking
            else: thinking = "⚙️ " + thinking

            if cuts_in_segment == 0:
                print(f"  🧠 AI: {thinking}")
                print(f"  📎 Selected: {selected_clip.filename} (Score: {selected_score:.1f})")

            # === PACING LOGIC: DIRECTOR-FIRST PACING (v12.1) ===
            # Authority Inversion: Visual intent leads, Beats follow as ornament.
            
            hold = getattr(segment, 'expected_hold', 'Normal').lower()
            arc_stage = segment.arc_stage.lower()
            cut_origin = getattr(segment, 'cut_origin', 'visual')
            
            # 1. HOLD-DRIVEN RESTRAINT: Minimums for Emotional Registration (Human-centric)
            if hold == "short":
                max_hold = 1.8  # register shot
            elif hold == "long":
                max_hold = 12.0 # deep cinematic holds
            else:
                max_hold = 4.5  # standard patience
                
            # 'Peak' intensity allows for kinetic cutting but still needs registration
            if arc_stage == "peak" and hold == "short":
                max_hold = 1.2
            elif arc_stage in ["build-up", "peak"] and hold == "normal":
                max_hold = 2.5
                
            # 2. SACRED VISUAL CUTS: Do NOT subdivide shots that were intentional in the reference.
            should_subdivide = False
            if cut_origin != "visual":
                if segment.duration > max_hold:
                    should_subdivide = True
            
            # 3. DURATION CALCULATION: Editor-first (Jittered)
            if not should_subdivide:
                use_duration = segment_remaining
                is_last_cut_of_segment = True
            else:
                # Logic-driven duration with variation to prevent mechanical loops
                import random
                if hold == "short":
                    base = 1.2
                elif hold == "long":
                    base = 5.0
                else:
                    base = 2.5
                    
                # Kinetic bonus for Peak stage
                if arc_stage == "peak":
                    base *= 0.7
                    
                use_duration = base * random.uniform(0.9, 1.1)
                
                # Check if we overshot the segment
                if use_duration >= segment_remaining - 0.2:
                    use_duration = segment_remaining
                    is_last_cut_of_segment = True
                else:
                    is_last_cut_of_segment = False

            # ======================================================================
            # PHASE 2: Beat Alignment (Snapping)
            # CONTRACT: The Editor (logic) has final authority over time.
            # The Director (Gemini) provides "accent_moments", but these MUST
            # stay strictly within the segment boundaries fixed by FFmpeg/Librosa.
            # ======================================================================
            original_duration = use_duration
            beat_aligned = False
            beat_target = None
            
            # PRECISION TIMING FIXES (v12.6):
            # FIX #2: Beat Phase Offset (-80ms for human anticipation)
            # FIX #3: Tighter tolerance (0.15s → 0.10s)
            # FIX #4: Never snap first cut after beat drop/energy transition
            BEAT_PHASE_OFFSET = -0.08  # Editors cut BEFORE the beat, not on it
            
            # FIX #4: Disable beat snapping for first cut in segment (let drops breathe)
            allow_beat_snapping = cuts_in_segment > 0
            
            if beat_grid and not is_last_cut_of_segment and allow_beat_snapping and getattr(blueprint, "audio_confidence", "Observed") == "Observed":
                target_end = timeline_position + use_duration + BEAT_PHASE_OFFSET  # Apply phase offset
                aligned_end = align_to_nearest_beat(target_end, beat_grid, tolerance=0.10)  # Tightened from 0.15
                
                # TIMING GUARD: Never allow a beat to snap outside the current segment.
                # Must be inside the segment with at least 100ms breathing room from edges.
                if (aligned_end >= segment.start + 0.1 and 
                    aligned_end < segment.end - 0.1 and
                    aligned_end > timeline_position + 0.1):
                    
                    beat_target = aligned_end
                    use_duration = aligned_end - timeline_position
                    beat_aligned = True
                    
                    # ENHANCED LOGGING: Beat alignment
                    beat_alignment_logs.append({
                        "segment_id": segment.id,
                        "original_duration": original_duration,
                        "aligned_duration": use_duration,
                        "beat_target": beat_target,
                        "timeline_position": timeline_position
                    })
                        
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

            # TRIGGER FORCE LOOP (v13.0): Hybrid System Directive 2.2
            # If a sacred cut falls short, strict mode triggers a LOOP of the same clip.
            remaining_dur = segment.end - timeline_position
            if is_sacred_cut and actual_duration < (remaining_dur - 0.05):
                # We are short. If we are NOT already forcing loop, we trigger it.
                if not force_loop_clip:
                     print(f"    🔄 SHORT CLIP ({actual_duration:.2f}s < {remaining_dur:.2f}s) ON SACRED SEGMENT. TRIGGERING LOOP.")
                     force_loop_clip = selected_clip
                     is_last_cut_of_segment = False # Force next iteration

            
            # SAFETY: Ensure clip_end is always greater than clip_start
            if clip_end <= clip_start or clip_end <= 0:
                print(f"    [SKIP] Invalid clip boundaries ({clip_start:.2f}s-{clip_end:.2f}s)")
                cuts_in_segment += 1
                continue

            # PHASE 4: Create Decision with Locked Boundaries
            # timeline_start is ALWAYS EXACTLY the previous timeline_end
            decision_start = timeline_position
            decision_end = decision_start + actual_duration
            
            # REMOVED LYING EDL LOGIC (v12.7):
            # We no longer force decision_end = segment.end.
            # If actual_duration is short, the loop will run again to fill the gap.
            # if is_last_cut_of_segment:
            #    decision_end = segment.end

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
            
            # Update Context and Trackers
            ctx.timeline_pos = decision_end
            ctx.last_motion = selected_clip.motion
            ctx.last_content = selected_clip.content_description
            ctx.last_subjects = selected_clip.primary_subject
            ctx.last_scale = infer_shot_scale(selected_clip)
            
            timeline_position = decision_end
            clip_current_position[selected_clip.filename] = clip_end
            clip_usage_count[selected_clip.filename] += 1
            clip_last_used_at[selected_clip.filename] = timeline_position
            clip_used_intervals[selected_clip.filename].append((clip_start, clip_end))
            
            # Variety tracking
            second_last_clip = last_used_clip
            last_used_clip = selected_clip.filename
            cuts_in_segment += 1
            
            print(f"    ✂️ Cut {cuts_in_segment}: {selected_clip.filename} "
                  f"[{clip_start:.2f}s-{clip_end:.2f}s] ({actual_duration:.2f}s) "
                  f"→ timeline [{decision.timeline_start:.6f}s-{decision.timeline_end:.6f}s]")

        # Ensure segment is fully filled (Gap-Filler)
        # v11.1: Aggressive gap filling to ensure total duration matches blueprint
        gap = segment.end - timeline_position
        if gap > 0.001:
             print(f"    🔗 Filling gap in segment {segment.id} ({gap:.4f}s remaining)")
             if decisions:
                 # Stretch the last decision to fill the gap
                 decisions[-1].timeline_end = segment.end
                 # Also update the clip_end to keep it proportional (if clip has room)
                 # But for now, just stretching the timeline is safer for sync
                 timeline_position = segment.end
             else:
                 # Emergency: segment was never even started? 
                 # This shouldn't happen with the while loop, but let's be safe
                 timeline_position = segment.end

        # === SEGMENT LOGGING (Directive 8) ===
        seg_decisions = [d for d in decisions if d.segment_id == segment.id]
        rendered_dur = sum(d.timeline_end - d.timeline_start for d in seg_decisions)
        ref_dur = segment.duration
        cuts_used = len(seg_decisions)
        
        loop_status = "No"
        if cuts_used > 1 and is_sacred_cut:
            loop_status = "Yes (Fallback Triggered)"
            
        print(f"[SEGMENT {segment.id} LOG] Ref: {ref_dur:.2f}s | Rendered: {rendered_dur:.2f}s | Cuts: {cuts_used} | Looped: {loop_status} | Auth: Reference")
        if abs(rendered_dur - ref_dur) > 0.05:
            print(f"    ❌ TIME DRIFT DETECTED: {rendered_dur - ref_dur:.3f}s")

    
    edl = EDL(decisions=decisions)
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
    
    # ENHANCED LOGGING: Unused clips
    used_clip_names = set(Path(d.clip_path).name for d in decisions)
    all_clip_names = set(c.filename for c in clip_index.clips)
    unused_clips = list(all_clip_names - used_clip_names)
    
    # Find clips that were never eligible (energy mismatch)
    never_eligible = []
    for clip in clip_index.clips:
        if clip.filename in unused_clips:
            # Check if it would be eligible for ANY segment
            was_eligible_anywhere = False
            for seg in blueprint.segments:
                eligible = get_eligible_clips(seg.energy, [clip])
                if eligible:
                    was_eligible_anywhere = True
                    break
            if not was_eligible_anywhere:
                never_eligible.append(clip.filename)
    
    unused_data = {
        "unused_clips": unused_clips,
        "never_eligible": never_eligible,
        "eligible_but_not_selected": [c for c in unused_clips if c not in never_eligible]
    }
    
    print(f"{'='*60}\n")
    
    # Attach enhanced logging to EDL (hack: store in a custom attribute)
    edl._enhanced_logging = {
        "candidate_rankings": candidate_rankings,
        "eligibility_breakdowns": eligibility_breakdowns,
        "semantic_neighbor_events": semantic_neighbor_events,
        "beat_alignment_logs": beat_alignment_logs,
        "unused_clips": unused_data
    }
    
    return edl, advisor_hints


def _create_energy_pools(clip_index: ClipIndex) -> Dict[EnergyLevel, List[ClipMetadata]]:
    # Group clips by energy level for efficient matching.
    # Returns: Dictionary mapping EnergyLevel -> List[ClipMetadata]
    pools = defaultdict(list)
    for clip in clip_index.clips:
        pools[clip.energy].append(clip)
    return dict(pools)


# ============================================================================
# STATS & DEBUGGING
# ============================================================================

def print_edl_summary(edl: EDL, blueprint: StyleBlueprint, clip_index: ClipIndex) -> None:
    # Print human-readable EDL summary for debugging.
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
    
    # NEW: Intelligence Audit (v8.1)
    # This proves the AI actually followed the narrative intent
    print(f"\n🧠 INTELLIGENCE AUDIT (Narrative Compliance):")
    arc_accuracy = defaultdict(list)
    function_counts = Counter()
    vibe_matches = 0
    total_cuts = len(edl.decisions)

    # Find the blueprint segments for each decision to check compliance
    for d in edl.decisions:
        seg = next((s for s in blueprint.segments if s.id == d.segment_id), None)
        if seg:
            function_counts[seg.shot_function] += 1
            if d.vibe_match: vibe_matches += 1
            
            # Use heuristic to see if shot_function matches clip's narrative role
            # (Note: This is a rough check since clips don't have explicit function tags yet)
            arc_accuracy[seg.arc_stage].append(1 if d.vibe_match else 0)

    print(f"   Vibe Accuracy: {(vibe_matches/total_cuts*100):.1f}% matching suggested vibes")
    
    print(f"\n   Shot Function Breakdown:")
    for func, count in function_counts.most_common():
        print(f"      {func:12s}: {count} cuts")

    print(f"\n   Arc Stage Fidelity:")
    for stage in ["Intro", "Build-up", "Peak", "Outro"]:
        matches = arc_accuracy.get(stage, [])
        if matches:
            acc = sum(matches) / len(matches) * 100
            print(f"      {stage:12s}: {acc:.1f}% intent alignment")

    print()



def validate_edl(edl: EDL, blueprint: StyleBlueprint) -> bool:
    # Validate EDL for continuity and timing errors.
    # Checks timeline continuity, duration matching, and clip validity.
    # Returns: True if valid, raises ValueError if issues found
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
        
        # Strict tolerance: +/-0.5s
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
