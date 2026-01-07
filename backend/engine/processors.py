"""
Processor module: FFmpeg wrappers for video manipulation.

All functions here are PURE: they take input paths, produce output files,
and have no side effects. They do NOT manage state or session data.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Tuple

# ============================================================================
# VIDEO INFORMATION
# ============================================================================

def get_video_duration(video_path: str) -> float:
    """
    Get video duration using ffprobe.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Duration in seconds
    
    Raises:
        RuntimeError: If ffprobe fails
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        raise RuntimeError(f"Failed to get duration for {video_path}: {e}")


def get_video_info(video_path: str) -> dict:
    """
    Get comprehensive video metadata.
    
    Returns:
        Dictionary with width, height, fps, duration, codec, etc.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name,duration",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        raise RuntimeError(f"Failed to get info for {video_path}: {e}")


# ============================================================================
# VIDEO STANDARDIZATION
# ============================================================================

def standardize_clip(input_path: str, output_path: str) -> None:
    """
    Standardize video to 1080x1920 (vertical), 30fps, h.264, AAC audio.
    
    Strategy: Scale to fit within 1080x1920, then crop to exact dimensions.
    This prevents black bars while maintaining aspect ratio.
    
    Args:
        input_path: Source video file
        output_path: Destination for standardized video
    
    Raises:
        RuntimeError: If FFmpeg command fails
    """
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
            "setsar=1"
        ),
        "-r", "30",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-y",  # Overwrite output file
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✅ Standardized: {Path(output_path).name}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"FFmpeg standardization failed:\n"
            f"STDOUT: {e.stdout}\n"
            f"STDERR: {e.stderr}"
        )


# ============================================================================
# AUDIO EXTRACTION
# ============================================================================

def extract_audio(video_path: str, audio_output_path: str) -> bool:
    """
    Extract audio track from video.
    
    Args:
        video_path: Source video
        audio_output_path: Destination for audio file (should end in .aac)
    
    Returns:
        True if audio extracted successfully, False if video has no audio
    
    Raises:
        RuntimeError: If FFmpeg fails unexpectedly
    """
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # No video
        "-acodec", "aac",
        "-b:a", "192k",
        "-y",
        audio_output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✅ Audio extracted: {Path(audio_output_path).name}")
        return True
    except subprocess.CalledProcessError as e:
        # Check if it's a "no audio stream" error
        if "does not contain any stream" in e.stderr or "no audio" in e.stderr.lower():
            print(f"  ⚠️  No audio track found in {Path(video_path).name}")
            return False
        else:
            raise RuntimeError(f"Audio extraction failed: {e.stderr}")


# ============================================================================
# VIDEO SEGMENTATION
# ============================================================================

def extract_segment(
    input_path: str,
    output_path: str,
    start_time: float,
    duration: float
) -> None:
    """
    Extract a segment from a video (precise frame-accurate cutting).
    
    Args:
        input_path: Source video
        output_path: Destination for segment
        start_time: Start time in seconds
        duration: Length of segment in seconds
    """
    cmd = [
        "ffmpeg",
        "-ss", str(start_time),  # Seek to start
        "-i", input_path,
        "-t", str(duration),  # Duration
        "-c", "copy",  # Copy codec (no re-encode = faster)
        "-avoid_negative_ts", "make_zero",
        "-y",
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"    ✅ Segment extracted: {start_time:.2f}s - {start_time + duration:.2f}s")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Segment extraction failed: {e.stderr}")


# ============================================================================
# VIDEO CONCATENATION
# ============================================================================

def concatenate_videos(input_paths: List[str], output_path: str) -> None:
    """
    Concatenate multiple videos into a single file.
    
    CRITICAL: Uses re-encoding (not stream copy) to ensure frame-perfect cuts.
    Stream copy only cuts on keyframes (2-5s apart), causing sync drift.
    
    Args:
        input_paths: List of video files to join (in order)
        output_path: Destination for concatenated video
    
    Raises:
        RuntimeError: If concatenation fails
    """
    # Create a temporary file list for FFmpeg
    concat_list_path = Path(output_path).parent / "concat_list.txt"
    
    with open(concat_list_path, "w") as f:
        for path in input_paths:
            # FFmpeg concat requires absolute paths and "file" prefix
            f.write(f"file '{Path(path).absolute()}'\n")
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-c:v", "libx264",  # Re-encode video for frame-perfect cuts
        "-preset", "ultrafast",  # Fast encoding (keeps total time <60s)
        "-crf", "23",  # Quality (23 = visually lossless)
        "-c:a", "copy",  # Audio can be copied (no precision needed)
        "-y",
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ Concatenated {len(input_paths)} segments (frame-perfect)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Concatenation failed: {e.stderr}")
    finally:
        # Clean up temp file
        if concat_list_path.exists():
            concat_list_path.unlink()


# ============================================================================
# AUDIO/VIDEO MERGING
# ============================================================================

def merge_audio_video(
    video_path: str,
    audio_path: str,
    output_path: str,
    trim_to_shortest: bool = True
) -> None:
    """
    Merge audio track onto video.
    
    OPTIMIZED: Video stream is copied (already encoded), only audio is re-encoded.
    This prevents double-encoding quality loss and speeds up rendering.
    
    Args:
        video_path: Video file (can be silent)
        audio_path: Audio file to overlay
        output_path: Destination for merged video
        trim_to_shortest: If True, trim to shortest input (prevent black frames)
    """
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",  # Don't re-encode video (already encoded in concat step)
        "-c:a", "aac",  # Re-encode audio to AAC
        "-b:a", "192k",
        "-map", "0:v:0",  # Take video from first input
        "-map", "1:a:0",  # Take audio from second input
    ]
    
    if trim_to_shortest:
        cmd.append("-shortest")  # Stop at shortest stream
    
    cmd.extend(["-y", output_path])
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ Audio merged onto video (optimized)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio/video merge failed: {e.stderr}")


# ============================================================================
# SILENT VIDEO (When reference has no audio)
# ============================================================================

def create_silent_video(input_path: str, output_path: str) -> None:
    """
    Create a copy of video with no audio track.
    
    Args:
        input_path: Source video
        output_path: Destination for silent video
    """
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "copy",
        "-an",  # No audio
        "-y",
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ Silent video created")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Silent video creation failed: {e.stderr}")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_output(output_path: str, min_size_kb: int = 100) -> bool:
    """
    Validate that output video was created successfully.
    
    Args:
        output_path: Path to output video
        min_size_kb: Minimum file size in KB (to catch empty files)
    
    Returns:
        True if valid, False otherwise
    """
    path = Path(output_path)
    
    if not path.exists():
        return False
    
    size_kb = path.stat().st_size / 1024
    if size_kb < min_size_kb:
        return False
    
    # Try to probe the file
    try:
        get_video_duration(output_path)
        return True
    except:
        return False

