"""
Orchestrator: Main pipeline controller.

This is the SINGLE entry point for the entire backend. The UI calls
run_mimic_pipeline() and gets back a PipelineResult.

All state management, error handling, and module coordination happens here.
"""

import time
import sys

# Fix Windows console encoding for print statements
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass
import hashlib
import shutil
from pathlib import Path
from typing import Callable, List
from models import PipelineResult, StyleBlueprint, ClipIndex, EDL

from engine.brain import (
    analyze_reference_video,
    analyze_all_clips,
    create_fallback_blueprint
)
from engine.editor import match_clips_to_blueprint, validate_edl, print_edl_summary
from engine.processors import (
    standardize_clip,
    extract_audio,
    extract_audio_wav,
    extract_segment,
    concatenate_videos,
    merge_audio_video,
    create_silent_video,
    validate_output,
    detect_scene_changes,
    detect_bpm,
    get_beat_grid,
    get_video_duration
)
from utils import ensure_directory, cleanup_session
from collections import defaultdict, Counter


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _merge_scene_and_beat_timestamps(
    scene_timestamps: List[float],
    beat_grid: List[float],
    max_gap: float = 2.0
) -> List[float]:
    """
    Merge visual scene cuts with beat-aligned timestamps.
    
    This ensures no segment is longer than max_gap seconds by inserting
    beat-aligned cut points where visual detection missed cuts.
    
    Args:
        scene_timestamps: Detected visual cut points
        beat_grid: Beat-aligned timestamps from BPM detection
        max_gap: Maximum allowed gap between timestamps (seconds)
    
    Returns:
        Combined list of timestamps (sorted, deduplicated)
    """
    combined = set(scene_timestamps)  # Start with visual cuts
    
    # Add beat timestamps to fill gaps
    all_timestamps = sorted(scene_timestamps + [0.0])  # Include start
    
    for i in range(len(all_timestamps) - 1):
        start = all_timestamps[i]
        end = all_timestamps[i + 1]
        gap = end - start
        
        # If gap exceeds max_gap, insert beat-aligned timestamps
        if gap > max_gap:
            # Find beats within this gap
            for beat in beat_grid:
                if start < beat < end:
                    # Only add if it creates reasonable subdivision
                    if beat - start >= 0.3 and end - beat >= 0.3:
                        combined.add(beat)
    
    return sorted(list(combined))


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_mimic_pipeline(
    reference_path: str,
    clip_paths: List[str],
    session_id: str,
    output_dir: str,
    api_key: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None
) -> PipelineResult:
    """
    Execute the complete MIMIC pipeline.
    
    STAGES:
    1. Validate inputs
    2. Analyze reference video (Gemini)
    3. Analyze user clips (Gemini)
    4. Match clips to blueprint segments (Editor)
    5. Render video (FFmpeg)
    
    Args:
        reference_path: Path to reference video
        clip_paths: List of paths to user clips
        session_id: Unique session identifier
        output_dir: Directory for final output
        api_key: Optional Gemini API key (uses env var if None)
        progress_callback: Optional callback(current_step, total_steps, message)
    
    Returns:
        PipelineResult with success status and output path
    """
    start_time = time.time()
    
    # Setup file logging and results naming
    ref_name = Path(reference_path).stem
    # Use 'master' if no session_id is provided, otherwise first 12 chars
    tag = session_id if len(session_id) < 12 else session_id[:12]
    base_output_name = f"{ref_name}_{tag}"
    
    log_path = Path(output_dir) / f"{base_output_name}.log"
    json_report_path = Path(output_dir) / f"{base_output_name}.json"
    
    log_file = None
    original_stdout = sys.stdout
    
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, s):
            for f in self.files:
                f.write(s)
                try: 
                    f.flush()
                except Exception: 
                    pass
        def flush(self):
            for f in self.files:
                try: 
                    f.flush()
                except Exception: 
                    pass
    
    try:
        log_file = open(log_path, 'w', encoding='utf-8')
        sys.stdout = Tee(original_stdout, log_file)
        print("=" * 80)
        print(f"PIPELINE RUN: {Path(reference_path).name.upper()}")
        print("=" * 80)
        print(f"Session ID: {session_id}")
        print(f"Reference: {Path(reference_path).name}")
        print(f"Clips: {len(clip_paths)}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    except Exception as e:
        print(f"[WARN] Could not create log file: {e}")
        log_file = None
    
    def update_progress(step: int, total: int, message: str):
        """Helper to call progress callback if provided."""
        if progress_callback:
            progress_callback(step, total, message)
        print(f"\n[{step}/{total}] {message}")
    
    TOTAL_STEPS = 5
    
    try:
        # ==================================================================
        # STEP 1: VALIDATE INPUTS
        # ==================================================================
        update_progress(1, TOTAL_STEPS, "Validating inputs...")
        
        _validate_inputs(reference_path, clip_paths)
        
        # Setup session directories
        # Use absolute path to ensure consistency regardless of CWD
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        
        # Permanent uploads are in data/uploads/{session_id}/
        # Temporary processing files go to temp/{session_id}/
        temp_session_dir = BASE_DIR / "temp" / session_id
        standardized_dir = temp_session_dir / "standardized"
        segments_dir = temp_session_dir / "segments"
        
        # PERSISTENT CACHE FOR STANDARDIZED CLIPS
        persistent_standardized_cache = BASE_DIR / "data" / "cache" / "standardized"
        
        ensure_directory(temp_session_dir)
        ensure_directory(standardized_dir)
        ensure_directory(segments_dir)
        ensure_directory(output_dir)
        ensure_directory(persistent_standardized_cache)
        
        # Note: Uploaded files stay in data/uploads/ (permanent)
        # Only temp/ files (standardized, segments) can be cleaned up
        
        # ==================================================================
        # STEP 2: ANALYZE REFERENCE
        # ==================================================================
        update_progress(2, TOTAL_STEPS, "Detecting visual cuts and analyzing reference structure...")
        
        # Setup audio analysis path
        audio_analysis_path = temp_session_dir / "ref_analysis_audio.wav"
        ref_bpm = 120.0
        
        try:
            # 2a. Detect visual cuts first (LOWERED threshold for subtle cuts)
            scene_timestamps = detect_scene_changes(reference_path, threshold=0.15)
            
            # 2b. Extract audio and detect BPM (Dynamic Rhythm)
            if extract_audio_wav(reference_path, str(audio_analysis_path)):
                ref_bpm = detect_bpm(str(audio_analysis_path))
            
            # 2c. HYBRID DETECTION: Merge visual cuts + beat-aligned subdivision
            # This ensures no segment is longer than ~2 seconds (critical for rhythm-based edits)
            ref_duration = get_video_duration(reference_path)
            beat_grid = get_beat_grid(ref_duration, int(ref_bpm))
            combined_timestamps = _merge_scene_and_beat_timestamps(
                scene_timestamps, 
                beat_grid, 
                max_gap=2.0
            )
            
            print(f"  [HYBRID] Visual cuts: {len(scene_timestamps)}, Beat-enhanced: {len(combined_timestamps)}")
            
            # 2d. Analyze with Gemini using hybrid timestamps
            blueprint = analyze_reference_video(
                reference_path, 
                api_key=api_key,
                scene_timestamps=combined_timestamps
            )
            print(f"[OK] Gemini successfully analyzed reference: {len(blueprint.segments)} segments found.")
        except Exception as e:
            print(f"[ERROR] Gemini reference analysis failed: {e}")
            print("    FALLING BACK to linear 2-second segments. Results will be generic.")
            blueprint = create_fallback_blueprint(reference_path)
        
        # ==================================================================
        # STEP 3: ANALYZE USER CLIPS
        # ==================================================================
        update_progress(3, TOTAL_STEPS, "Analyzing user clips with Gemini AI...")
        
        # 1. Analyze ORIGINAL clips first (allows better caching)
        try:
            # We pass clip_paths (originals) to leverage the cache
            clip_index = analyze_all_clips(clip_paths, api_key)
            print(f"[OK] Gemini successfully analyzed {len(clip_index.clips)} clips (using originals for cache).")
        except Exception as e:
            print(f"[ERROR] Gemini clip analysis failed: {e}")
            print("    FALLING BACK to default energy levels. Edit quality will be reduced.")
            from models import ClipMetadata, EnergyLevel, MotionType
            
            clips = []
            for path in clip_paths:
                clips.append(ClipMetadata(
                    filename=Path(path).name,
                    filepath=path,
                    duration=get_video_duration(path),
                    energy=EnergyLevel.MEDIUM,
                    motion=MotionType.DYNAMIC
                ))
            clip_index = ClipIndex(clips=clips)
            
        # 2. Standardize clips for rendering (with persistent caching)
        standardized_paths = []
        for i, clip_path in enumerate(clip_paths, start=1):
            input_p = Path(clip_path)
            output_path = standardized_dir / f"clip_{i:03d}.mp4"
            
            # Generate a unique cache key for this specific file state
            # (path + scale_params + size + mtime)
            file_stat = input_p.stat()
            cache_key_source = f"{input_p.absolute()}_{file_stat.st_size}_{file_stat.st_mtime}"
            cache_hash = hashlib.md5(cache_key_source.encode()).hexdigest()
            cached_filename = f"std_{cache_hash}.mp4"
            cached_path = persistent_standardized_cache / cached_filename
            
            if cached_path.exists():
                print(f"  [CACHE] Using standardized clip {i}/{len(clip_paths)}: {input_p.name}")
                shutil.copy2(str(cached_path), str(output_path))
            else:
                print(f"  Standardizing clip {i}/{len(clip_paths)}: {input_p.name}...")
                standardize_clip(clip_path, str(output_path))
                # Save to persistent cache
                shutil.copy2(str(output_path), str(cached_path))
                
            standardized_paths.append(str(output_path))
            
            # Update the filepath in the clip index to the standardized one
            original_filename = input_p.name
            for clip_meta in clip_index.clips:
                if clip_meta.filename == original_filename:
                    clip_meta.filepath = str(output_path)
                    break
        
        print(f"[OK] All clips standardized (cached or new) and ready for render.")
        
        # ==================================================================
        # STEP 4: MATCH & EDIT
        # ==================================================================
        update_progress(4, TOTAL_STEPS, "Creating edit sequence...")
        
        edl = match_clips_to_blueprint(
            blueprint, 
            clip_index, 
            find_best_moments=True, 
            api_key=api_key,
            reference_path=reference_path,  # For beat grid detection
            bpm=ref_bpm  # Dynamic BPM detected in Step 2
        )
        
        # Validate EDL but don't fail - allow debugging even if timing is off
        try:
            validate_edl(edl, blueprint)
        except ValueError as e:
            print(f"[WARN] EDL validation failed: {e}")
            print("[WARN] Continuing anyway to allow debugging...")
        
        print_edl_summary(edl, blueprint, clip_index)
        
        # ==================================================================
        # STEP 5: RENDER VIDEO
        # ==================================================================
        update_progress(5, TOTAL_STEPS, "Rendering final video...")
        
        # Extract segments according to EDL
        segment_paths = []
        for i, decision in enumerate(edl.decisions, start=1):
            segment_path = segments_dir / f"segment_{i:03d}.mp4"
            extract_segment(
                decision.clip_path,
                str(segment_path),
                decision.clip_start,
                decision.clip_end - decision.clip_start
            )
            segment_paths.append(str(segment_path))
        
        # Concatenate segments
        temp_video_path = temp_session_dir / "temp_video.mp4"
        concatenate_videos(segment_paths, str(temp_video_path))
        
        # Handle audio
        audio_path = temp_session_dir / "ref_audio.aac"
        audio_extracted = extract_audio(reference_path, str(audio_path))
        
        # Final output (use full session_id to prevent collisions)
        output_filename = f"{base_output_name}.mp4"
        final_output_path = Path(output_dir) / output_filename
        
        # Remove old file if it exists (force regeneration)
        if final_output_path.exists():
            print(f"[WARN] Removing existing output file: {final_output_path}")
            final_output_path.unlink()
        
        if audio_extracted:
            merge_audio_video(
                str(temp_video_path),
                str(audio_path),
                str(final_output_path),
                trim_to_shortest=True
            )
        else:
            create_silent_video(str(temp_video_path), str(final_output_path))
        
        # Validate output
        if not validate_output(str(final_output_path)):
            raise RuntimeError("Output video validation failed")
        
        # ==================================================================
        # SUCCESS
        # ==================================================================
        processing_time = time.time() - start_time
        
        output_duration = get_video_duration(str(final_output_path))
        ref_duration = blueprint.total_duration
        
        print(f"\n{'='*80}")
        print("✅ SUCCESS!")
        print(f"{'='*80}")
        print(f"\n📊 Basic Results:")
        print(f"   Output: {final_output_path.name}")
        print(f"   Duration: {output_duration:.2f}s (ref: {ref_duration:.2f}s)")
        print(f"   Difference: {abs(output_duration - ref_duration):.2f}s")
        print(f"   Processing time: {processing_time:.1f}s")
        
        # Print comprehensive analysis (matching test_ref.py style)
        _print_comprehensive_analysis(blueprint, edl, clip_index, clip_paths)
        
        print(f"\n{'='*80}")
        print(f"🎉 Watch the result: {final_output_path}")
        print(f"{'='*80}\n")
        
        result = PipelineResult(
            success=True,
            output_path=str(final_output_path),
            blueprint=blueprint,
            clip_index=clip_index,
            edl=edl,
            processing_time_seconds=processing_time
        )
        
        # SAVE INTELLIGENCE REPORT FOR FRONTEND (Master Whitebox File)
        try:
            print(f"[PROCESS] Exporting master intelligence report...")
            with open(json_report_path, "w", encoding="utf-8") as jf:
                json_data = result.model_dump_json(indent=2)
                jf.write(json_data)
                jf.flush()
                # Force OS to write to disk
                import os
                os.fsync(jf.fileno())
            print(f"[OK] Intelligence report saved: {json_report_path} ({len(json_data)} bytes)")
        except Exception as e:
            print(f"[WARN] Failed to save JSON report: {e}")
            import traceback
            traceback.print_exc()

        # Restore stdout and close log file
        if log_file:
            sys.stdout = original_stdout
            log_file.close()
            print(f"[OK] Analysis log saved: {log_path}")
        
        # CLEANUP CACHE CLUTTER (Muted videos)
        try:
            for muted_vid in Path("data/cache").glob("muted_*.mp4"):
                muted_vid.unlink()
        except:
            pass
            
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print("❌ FAILED")
        print(f"{'='*80}")
        print(f"   Error: {str(e)}")
        print(f"{'='*80}\n")
        
        import traceback
        traceback.print_exc()
        
        # Restore stdout and close log file even on error
        if log_file:
            sys.stdout = original_stdout
            log_file.close()
            print(f"Error log saved: {log_path}")
        
        return PipelineResult(
            success=False,
            error=str(e),
            processing_time_seconds=processing_time
        )


# ============================================================================
# VALIDATION
# ============================================================================

def _print_comprehensive_analysis(blueprint: StyleBlueprint, edl: EDL, clip_index: ClipIndex, clip_paths: List[str]) -> None:
    """Print comprehensive debugging analysis matching test_ref.py style."""
    if not blueprint or not edl:
        return
    
    print(f"\n{'='*80}")
    print("🧠 COMPREHENSIVE SYSTEM ANALYSIS")
    print(f"{'='*80}")
    
    # 1. Reference Analysis Breakdown
    print(f"\n📹 Reference Analysis:")
    print(f"   Editing Style: {blueprint.editing_style}")
    print(f"   Emotional Intent: {blueprint.emotional_intent}")
    arc_desc = blueprint.arc_description[:100] + "..." if len(blueprint.arc_description) > 100 else blueprint.arc_description
    print(f"   Arc Description: {arc_desc}")
    print(f"   Total Segments: {len(blueprint.segments)}")
    
    # 1.5. Blueprint Full Detail
    print(f"\n📑 BLUEPRINT FULL SEGMENT LIST:")
    for i, seg in enumerate(blueprint.segments):
        print(f"   {i+1:02d}: {seg.start:5.2f}-{seg.end:5.2f}s | {seg.energy.value:6} | Vibe: {seg.vibe:10} | {seg.arc_stage}")
    
    # 2. Arc Stage Distribution
    arc_stages = Counter([seg.arc_stage for seg in blueprint.segments])
    print(f"\n📈 Arc Stage Distribution:")
    for stage, count in arc_stages.most_common():
        pct = (count / len(blueprint.segments)) * 100
        print(f"   {stage}: {count} segments ({pct:.1f}%)")
    
    # 3. Vibe Distribution
    vibes = Counter([seg.vibe for seg in blueprint.segments if seg.vibe != "General"])
    if vibes:
        print(f"\n🎨 Vibe Distribution:")
        for vibe, count in vibes.most_common():
            pct = (count / len(blueprint.segments)) * 100
            print(f"   {vibe}: {count} segments ({pct:.1f}%)")
    
    # 4. Clip Usage Analysis
    clip_usage = defaultdict(int)
    clip_reasoning = defaultdict(list)
    for decision in edl.decisions:
        clip_name = Path(decision.clip_path).name
        clip_usage[clip_name] += 1
        clip_reasoning[clip_name].append(decision.reasoning)
    
    print(f"\n📎 Clip Usage Analysis:")
    print(f"   Unique clips used: {len(clip_usage)}/{len(clip_paths)}")
    print(f"   Most used clips:")
    for clip_name, count in sorted(clip_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
        pct = (count / len(edl.decisions)) * 100
        print(f"     {clip_name}: {count} times ({pct:.1f}%)")
    
    # 5. Reasoning Breakdown
    smart_matches = sum(1 for d in edl.decisions if "✨ Smart Match" in d.reasoning)
    good_fits = sum(1 for d in edl.decisions if "🎯 Good Fit" in d.reasoning)
    constraint_relax = sum(1 for d in edl.decisions if "⚙️ Constraint Relaxation" in d.reasoning)
    
    print(f"\n🧠 AI Reasoning Breakdown:")
    if len(edl.decisions) > 0:
        print(f"   ✨ Smart Match: {smart_matches} ({smart_matches/len(edl.decisions)*100:.1f}%)")
        print(f"   🎯 Good Fit: {good_fits} ({good_fits/len(edl.decisions)*100:.1f}%)")
        print(f"   ⚙️ Constraint Relaxation: {constraint_relax} ({constraint_relax/len(edl.decisions)*100:.1f}%)")
    
    # 6. Vibe Matching Stats
    vibe_matches = sum(1 for d in edl.decisions if d.vibe_match)
    print(f"\n🎨 Vibe Matching:")
    if len(edl.decisions) > 0:
        print(f"   Matches: {vibe_matches}/{len(edl.decisions)} ({vibe_matches/len(edl.decisions)*100:.1f}%)")
    
    # 7. Cut Statistics by Arc Stage
    print(f"\n📏 Cut Statistics by Arc Stage:")
    for stage in ["Intro", "Build-up", "Peak", "Outro", "Main"]:
        stage_decisions = []
        for decision in edl.decisions:
            for seg in blueprint.segments:
                if seg.start <= decision.timeline_start < seg.end:
                    if seg.arc_stage == stage:
                        stage_decisions.append(decision.timeline_end - decision.timeline_start)
                    break
        
        if stage_decisions:
            avg = sum(stage_decisions) / len(stage_decisions)
            print(f"   {stage}: {len(stage_decisions)} cuts, avg {avg:.2f}s")
    
    # 8. Overall Cut Statistics
    durations = [(d.timeline_end - d.timeline_start) for d in edl.decisions]
    if durations:
        avg_cut = sum(durations) / len(durations)
        min_cut = min(durations)
        max_cut = max(durations)
        
        print(f"\n📏 Overall Cut Statistics:")
        print(f"   Total cuts: {len(edl.decisions)}")
        print(f"   Average cut: {avg_cut:.2f}s")
        print(f"   Shortest cut: {min_cut:.2f}s")
        print(f"   Longest cut: {max_cut:.2f}s")
    
    # 9. Sample Reasoning Examples
    print(f"\n💭 Sample AI Reasoning (first 5 decisions):")
    for i, decision in enumerate(edl.decisions[:5], 1):
        clip_name = Path(decision.clip_path).name
        reasoning_preview = decision.reasoning[:80] + "..." if len(decision.reasoning) > 80 else decision.reasoning
        print(f"   {i}. {clip_name}: {reasoning_preview}")
    
    # 10. Clip Index Stats
    if clip_index:
        print(f"\n📦 CLIP REGISTRY ({len(clip_index.clips)} total):")
        for i, clip in enumerate(sorted(clip_index.clips, key=lambda x: x.filename)):
            vibes_str = ", ".join(clip.vibes[:3]) if hasattr(clip, 'vibes') and clip.vibes else "N/A"
            print(f"   {i+1:02d}: {clip.filename:15} | {clip.energy.value:6} | {clip.duration:5.1f}s | Vibes: {vibes_str}")
        
        clips_with_moments = sum(1 for c in clip_index.clips if hasattr(c, 'best_moments') and c.best_moments)
        clips_with_vibes = sum(1 for c in clip_index.clips if hasattr(c, 'vibes') and c.vibes)
        
        print(f"\n📋 Metadata Coverage:")
        print(f"   Best Moments: {clips_with_moments}/{len(clip_index.clips)}")
        print(f"   Vibes: {clips_with_vibes}/{len(clip_index.clips)}")
    
    # 11. Temporal Drift Check
    gaps = []
    overlaps = []
    for i in range(1, len(edl.decisions)):
        gap = edl.decisions[i].timeline_start - edl.decisions[i-1].timeline_end
        if abs(gap) > 0.001:
            if gap > 0:
                gaps.append((i, gap))
            else:
                overlaps.append((i, abs(gap)))
    
    print(f"\n🔍 Temporal Precision Check:")
    if gaps:
        print(f"   ⚠️ WARNING: Timeline Gaps Detected ({len(gaps)}):")
        for i, gap in gaps[:5]:
            print(f"     Gap after decision {i}: {gap:.6f}s")
        if len(gaps) > 5:
            print(f"     ... and {len(gaps) - 5} more gaps")
    elif overlaps:
        print(f"   ⚠️ WARNING: Timeline Overlaps Detected ({len(overlaps)}):")
        for i, overlap in overlaps[:5]:
            print(f"     Overlap after decision {i}: {overlap:.6f}s")
        if len(overlaps) > 5:
            print(f"     ... and {len(overlaps) - 5} more overlaps")
    else:
        print(f"   ✅ TIMELINE INTEGRITY: No gaps or overlaps detected (all within 0.001s tolerance)")
    
    # 12. Material Efficiency Stats
    if clip_index:
        total_available_duration = sum(c.duration for c in clip_index.clips)
        used_unique_duration = sum(d.clip_end - d.clip_start for d in edl.decisions)
        
        unique_segments = set()
        for decision in edl.decisions:
            clip_name = Path(decision.clip_path).name
            segment_key = f"{clip_name}:{decision.clip_start:.2f}-{decision.clip_end:.2f}"
            unique_segments.add(segment_key)
        
        print(f"\n📦 Material Efficiency:")
        print(f"   Total source duration available: {total_available_duration:.2f}s")
        print(f"   Total duration used in edit: {used_unique_duration:.2f}s")
        print(f"   Unique clip segments used: {len(unique_segments)}")
        if total_available_duration > 0:
            utilization = (used_unique_duration / total_available_duration) * 100
            print(f"   Utilization Ratio: {utilization:.1f}%")
            if utilization < 10:
                print(f"   💡 Note: Low utilization suggests clips may not match reference vibes well")


def _validate_inputs(reference_path: str, clip_paths: List[str]) -> None:
    """
    Validate inputs before pipeline execution.
    
    Raises:
        ValueError: If inputs are invalid
    """
    
    # Check reference video exists
    if not Path(reference_path).exists():
        raise ValueError(f"Reference video not found: {reference_path}")
    
    # Check reference duration (3-20 seconds)
    try:
        ref_duration = get_video_duration(reference_path)
        if not (3.0 <= ref_duration <= 60.0):
            raise ValueError(
                f"Reference video must be 3-60 seconds (got {ref_duration:.1f}s)"
            )
    except Exception as e:
        raise ValueError(f"Could not read reference video: {e}")
    
    # Check clip count (minimum 2)
    if len(clip_paths) < 2:
        raise ValueError(f"Need at least 2 clips (got {len(clip_paths)})")
    
    # Check all clips exist
    for i, clip_path in enumerate(clip_paths, start=1):
        if not Path(clip_path).exists():
            raise ValueError(f"Clip {i} not found: {clip_path}")
        
        # Basic validation
        try:
            get_video_duration(clip_path)
        except Exception as e:
            raise ValueError(f"Could not read clip {i}: {e}")
