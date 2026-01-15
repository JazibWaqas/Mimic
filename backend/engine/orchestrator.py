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
    extract_segment,
    concatenate_videos,
    merge_audio_video,
    create_silent_video,
    validate_output
)
from utils import ensure_directory, cleanup_session


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
        
        ensure_directory(temp_session_dir)
        ensure_directory(standardized_dir)
        ensure_directory(segments_dir)
        ensure_directory(output_dir)
        
        # Note: Uploaded files stay in data/uploads/ (permanent)
        # Only temp/ files (standardized, segments) can be cleaned up
        
        # ==================================================================
        # STEP 2: ANALYZE REFERENCE
        # ==================================================================
        update_progress(2, TOTAL_STEPS, "Analyzing reference video structure with Gemini AI...")
        
        try:
            blueprint = analyze_reference_video(reference_path, api_key)
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
            from engine.processors import get_video_duration
            
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
            
        # 2. Standardize clips for rendering
        standardized_paths = []
        for i, clip_path in enumerate(clip_paths, start=1):
            output_path = standardized_dir / f"clip_{i:03d}.mp4"
            print(f"  Standardizing clip {i}/{len(clip_paths)}...")
            standardize_clip(clip_path, str(output_path))
            standardized_paths.append(str(output_path))
            
            # Update the filepath in the clip index to the standardized one
            # Find the corresponding metadata and update path
            original_filename = Path(clip_path).name
            for clip_meta in clip_index.clips:
                if clip_meta.filename == original_filename:
                    clip_meta.filepath = str(output_path)
                    break
        
        print(f"[OK] All clips standardized and ready for render.")
        
        # ==================================================================
        # STEP 4: MATCH & EDIT
        # ==================================================================
        update_progress(4, TOTAL_STEPS, "Creating edit sequence...")
        
        edl = match_clips_to_blueprint(
            blueprint, 
            clip_index, 
            find_best_moments=True, 
            api_key=api_key,
            reference_path=reference_path  # For beat grid detection
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
        has_audio = extract_audio(reference_path, str(audio_path))
        
        # Final output (use full session_id to prevent collisions)
        output_filename = f"mimic_output_{session_id}.mp4"
        final_output_path = Path(output_dir) / output_filename
        
        # Remove old file if it exists (force regeneration)
        if final_output_path.exists():
            print(f"[WARN] Removing existing output file: {final_output_path}")
            final_output_path.unlink()
        
        if has_audio:
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
        
        print(f"\n{'='*60}")
        print(f"[OK] PIPELINE COMPLETE")
        print(f"{'='*60}")
        print(f"Output: {final_output_path}")
        print(f"Duration: {blueprint.total_duration:.2f}s")
        print(f"Segments: {len(blueprint.segments)}")
        print(f"Processing time: {processing_time:.1f}s")
        print(f"{'='*60}\n")
        
        return PipelineResult(
            success=True,
            output_path=str(final_output_path),
            blueprint=blueprint,
            clip_index=clip_index,
            edl=edl,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"[ERROR] PIPELINE FAILED")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        
        return PipelineResult(
            success=False,
            error=str(e),
            processing_time_seconds=processing_time
        )


# ============================================================================
# VALIDATION
# ============================================================================

def _validate_inputs(reference_path: str, clip_paths: List[str]) -> None:
    """
    Validate inputs before pipeline execution.
    
    Raises:
        ValueError: If inputs are invalid
    """
    from engine.processors import get_video_duration
    
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


def run_mimic_pipeline_manual(
    blueprint: StyleBlueprint,
    clip_index: ClipIndex,
    clip_paths: List[str],
    session_id: str,
    output_dir: str,
    progress_callback: Callable[[int, int, str], None] | None = None
) -> PipelineResult:
    """
    MANUAL MODE: Run pipeline with pre-analyzed JSON from AI Studio.
    Skips Gemini API calls entirely - only does matching + rendering.
    
    Args:
        blueprint: Pre-analyzed reference structure (from AI Studio)
        clip_index: Pre-analyzed clip metadata (from AI Studio)
        clip_paths: Paths to user clips
        session_id: Unique session identifier
        output_dir: Where to save final video
        progress_callback: Optional progress updates
    
    Returns:
        PipelineResult with success/failure status
    """
    start_time = time.time()
    
    def update_progress(step: int, total: int, message: str):
        if progress_callback:
            progress_callback(step, total, message)
        print(f"\n[{step}/{total}] {message}")
    
    TOTAL_STEPS = 3  # Standardize, Match, Render
    
    try:
        print(f"\n{'='*60}")
        print(f"[MANUAL MODE] Using pre-analyzed JSON")
        print(f"{'='*60}\n")
        
        # Setup directories
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        temp_session_dir = BASE_DIR / "temp" / session_id
        standardized_dir = temp_session_dir / "standardized"
        segments_dir = temp_session_dir / "segments"
        
        ensure_directory(temp_session_dir)
        ensure_directory(standardized_dir)
        ensure_directory(segments_dir)
        ensure_directory(output_dir)
        
        # STEP 1: STANDARDIZE CLIPS
        update_progress(1, TOTAL_STEPS, "Standardizing clips...")
        
        standardized_paths = []
        for i, clip_path in enumerate(clip_paths, start=1):
            output_path = standardized_dir / f"clip_{i:03d}.mp4"
            print(f"  Standardizing clip {i}/{len(clip_paths)}...")
            standardize_clip(clip_path, str(output_path))
            standardized_paths.append(str(output_path))
        
        # Update clip_index with standardized paths
        for i, clip_meta in enumerate(clip_index.clips):
            clip_meta.filepath = standardized_paths[i]
        
        # STEP 2: MATCH CLIPS TO BLUEPRINT
        update_progress(2, TOTAL_STEPS, "Creating edit sequence...")
        
        # Manual mode - no best moment analysis (saves API calls)
        edl = match_clips_to_blueprint(blueprint, clip_index, find_best_moments=False)
        
        # Validate EDL but don't fail - allow debugging even if timing is off
        try:
            validate_edl(edl, blueprint)
        except ValueError as e:
            print(f"[WARN] EDL validation failed: {e}")
            print("[WARN] Continuing anyway to allow debugging...")
        
        print_edl_summary(edl, blueprint, clip_index)
        
        # STEP 3: RENDER
        update_progress(3, TOTAL_STEPS, "Rendering final video...")
        
        # Extract segments
        segment_files = []
        for i, decision in enumerate(edl.decisions, start=1):
            segment_path = segments_dir / f"segment_{i:03d}.mp4"
            extract_segment(
                decision.clip_path,
                str(segment_path),
                decision.clip_start,
                decision.clip_end
            )
            segment_files.append(str(segment_path))
            print(f"    [OK] Segment extracted: {decision.clip_start:.2f}s - {decision.clip_end:.2f}s")
        
        # Concatenate
        stitched_path = temp_session_dir / "stitched.mp4"
        concatenate_videos(segment_files, str(stitched_path))
        
        # Create silent output (no reference audio in manual mode)
        output_filename = f"mimic_output_{session_id}.mp4"
        output_path = Path(output_dir) / output_filename
        
        # Remove old file if it exists (force regeneration)
        if output_path.exists():
            print(f"[WARN] Removing existing output file: {output_path}")
            output_path.unlink()
        create_silent_video(str(stitched_path), str(output_path))
        
        # Validate
        validate_output(str(output_path), blueprint.total_duration)
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"[OK] MANUAL MODE COMPLETE")
        print(f"{'='*60}")
        print(f"Output: {output_path}")
        print(f"Duration: {blueprint.total_duration:.2f}s")
        print(f"Segments: {len(edl.decisions)}")
        print(f"Processing time: {elapsed:.1f}s")
        print(f"{'='*60}\n")
        
        return PipelineResult(
            success=True,
            output_path=str(output_path),
            blueprint=blueprint,
            clip_index=clip_index,
            edl=edl,
            processing_time_seconds=elapsed
        )
        
    except Exception as e:
        print(f"\n[ERROR] Manual pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        
        return PipelineResult(
            success=False,
            error=str(e),
            processing_time_seconds=time.time() - start_time
        )
