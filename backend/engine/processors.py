"""
Processor module: FFmpeg wrappers for video manipulation.

All functions here are PURE: they take input paths, produce output files,
and have no side effects. They do NOT manage state or session data.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Optional

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


def has_audio(video_path: str) -> bool:
    """
    Check if video has an audio track.
    
    Args:
        video_path: Path to video file
    
    Returns:
        True if video has audio, False otherwise
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return "audio" in result.stdout.lower()
    except Exception:
        return False


def get_beat_grid(duration: float, bpm: int = 120) -> List[float]:
    """
    Generate beat timestamps assuming fixed BPM.

    This creates a "beat grid" for aligning cuts to music, even without
    real beat detection. Works well for most electronic/pop music.

    Args:
        duration: Total video duration in seconds
        bpm: Beats per minute (default 120 = common pop/electronic tempo)

    Returns:
        List of beat timestamps in seconds [0.0, 0.5, 1.0, 1.5, ...]

    Examples:
        120 BPM = 0.5s per beat (2 beats/second)
        140 BPM = 0.428s per beat
        100 BPM = 0.6s per beat
    """
    # Guardrail: avoid division by zero / nonsense BPMs
    if bpm is None or bpm <= 0:
        return []
    beat_interval = 60.0 / bpm
    timestamps = []
    t = 0.0

    while t < duration:
        timestamps.append(t)
        t += beat_interval

    return timestamps


def align_to_nearest_beat(time: float, beat_grid: List[float], tolerance: float = 0.15) -> float:
    """
    Snap a time value to the nearest beat on the grid.
    
    Args:
        time: Original time in seconds
        beat_grid: List of beat timestamps from get_beat_grid()
        tolerance: Maximum distance to snap (default 0.15s)
    
    Returns:
        Nearest beat timestamp, or original time if no beat is close enough
    
    Example:
        align_to_nearest_beat(1.23, [0.0, 0.5, 1.0, 1.5]) → 1.0
        align_to_nearest_beat(0.75, [0.0, 0.5, 1.0, 1.5]) → 0.5
    """
    if not beat_grid:
        return time
    
    # Find nearest beat
    nearest_beat = min(beat_grid, key=lambda t: abs(t - time))
    
    # Only snap if within tolerance
    if abs(nearest_beat - time) <= tolerance:
        return nearest_beat
    
    return time


def remove_audio(input_path: str, output_path: str) -> str:
    """
    Remove audio track from video (bypass recitation blocks).
    Uses stream copying for speed.
    """
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-an",  # No audio
        "-vcodec", "copy",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Failed to remove audio: {e}")


def detect_bpm(audio_path: str) -> float:
    """
    Detect the tempo (BPM) of an audio file using librosa.
    
    Args:
        audio_path: Path to the audio file (wav preferred)
    
    Returns:
        Detected BPM as a float, or 120.0 as fallback
    """
    try:
        import librosa
        import numpy as np
        
        print(f"  [BEAT] Detecting BPM for {Path(audio_path).name}...")
        y, sr = librosa.load(audio_path)
        
        # tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        # Note: librosa 0.10.0+ returns tempo as an array if not specified
        tempo_result = librosa.beat.beat_track(y=y, sr=sr)
        
        # Handle both old and new librosa versions
        if isinstance(tempo_result, tuple):
            tempo = tempo_result[0]
        else:
            tempo = tempo_result
            
        # If it's still an array/list, get the first element
        if hasattr(tempo, "__len__"):
            tempo = float(tempo[0])
        else:
            tempo = float(tempo)

        # Guardrail: librosa can yield 0.0 or NaN. Treat as invalid.
        if not (tempo > 0 and tempo < 300):   # pick sane upper bound
            raise ValueError(f"Invalid tempo {tempo}")

        print(f"  [OK] Detected BPM: {tempo:.2f}")
        return tempo
    except Exception as e:
        print(f"  [WARN] BPM detection failed: {e}. Falling back to 120.0")
        return 120.0


def extract_audio_wav(video_path: str, wav_output_path: str) -> bool:
    """
    Extract audio from video to a WAV file for BPM analysis.

    Args:
        video_path: Source video path
        wav_output_path: Output WAV file path

    Returns:
        True if extraction succeeded, False if failed/no audio
    """
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        "-y",
        wav_output_path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="ignore") if isinstance(e.stderr, (bytes, bytearray)) else (e.stderr or "")
        if "does not contain any stream" in stderr or "no audio" in stderr.lower():
            return False
        print(f"  [WARN] WAV audio extraction failed: {stderr}")
        return False


# ============================================================================
# VIDEO STANDARDIZATION
# ============================================================================

def standardize_clip(input_path: str, output_path: str, energy: Optional["EnergyLevel"] = None, is_reference: bool = False) -> None:
    """
    Standardize video to 1080x1920 (vertical), 30fps, h.264, AAC audio.
    
    v12.6: UNIFORM CINEMATIC PRESERVE
    - Removed conditional geometry logic (aspect ratio, energy-based cropping)
    - Single mode: preserve source framing, scale to fit 1080 width, pad to 1920 height
    - Optimized for premium cinematic sources (Top Gun, F1, professional footage)
    - High quality settings for 3K+ OLED displays (CRF 18, slow preset)
    
    Args:
        input_path: Source video file
        output_path: Destination for standardized video
        energy: DEPRECATED - no longer used for geometry decisions
        is_reference: DEPRECATED - no longer special-cased
    """
    # UNIFORM CINEMATIC PRESERVE
    # Always preserve source framing, never crop, never zoom
    geometry_filters = "scale=1080:-2:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    
    print(f"  [GEOMETRY] Mode: cinematic_preserve (uniform)")

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", (
            f"{geometry_filters},"
            "fps=30,"                           # Force consistent 30fps
            "format=yuv420p,"                   # Ensure maximal compatibility
            "setsar=1"
        ),
        "-c:v", "h264_qsv",         # Intel QuickSync GPU encode (5-10x faster than libx264)
        "-global_quality", "23",     # QSV quality level (lower=better, 23 is high quality)
        "-preset", "slow",          # Better compression efficiency
        "-c:a", "aac",
        "-b:a", "256k",             # Improved audio bitrate
        "-ar", "48000",             # Higher sample rate
        "-map_metadata", "-1",      # Strip all metadata
        "-metadata:s:v:0", "rotate=0", 
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",      # Explicit pixel format for compatibility
        "-y",
        output_path
    ]

    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  [OK] Standardized: {Path(output_path).name}")
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
        print(f"  [OK] Audio extracted: {Path(audio_output_path).name}")
        return True
    except subprocess.CalledProcessError as e:
        # Check if it's a "no audio stream" error
        if "does not contain any stream" in e.stderr or "no audio" in e.stderr.lower():
            print(f"  [WARN] No audio track found in {Path(video_path).name}")
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
        "-y",
        "-ss", str(start_time),  # Seek to start (before -i for accuracy)
        "-i", input_path,
        "-t", str(duration),  # Duration
        "-c:v", "libx264",  # Re-encode for frame-accurate cuts
        "-preset", "ultrafast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-avoid_negative_ts", "make_zero",
        output_path
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"    [OK] Segment extracted: {start_time:.2f}s - {start_time + duration:.2f}s")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Segment extraction failed: {e.stderr}")


# ============================================================================
# ADVANCED DIAGNOSTICS (NEW)
# ============================================================================

def detect_scene_changes(video_path: str, threshold: float = 0.3) -> List[float]:
    """
    Use FFmpeg visual analysis to find ACTUAL cut points in a video.
    
    Returns:
        List of timestamps (seconds) where a scene change was detected.
    """
    print(f"  [DIAGNOSTIC] Detecting visual scene changes (threshold={threshold})...")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-filter:v", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null",
        "-"
    ]
    
    try:
        # Scene detection info goes to stderr
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stderr
        
        timestamps = []
        import re
        # Look for 'pts_time:9.833333' pattern
        matches = re.findall(r"pts_time:([\d\.]+)", output)
        for m in matches:
            ts = float(m)
            # Clamp to >= 0.1s to avoid issues with start of video
            if ts >= 0.1 and ts not in timestamps:
                timestamps.append(ts)
        
        # Sort and filter close timestamps
        timestamps.sort()
        final_ts = []
        if timestamps:
            final_ts.append(timestamps[0])
            for i in range(1, len(timestamps)):
                # CRITICAL: Lowered from 0.3s to 0.15s to capture fast-paced edits
                # Music videos and reels often have cuts every 0.2-0.3s
                if timestamps[i] - final_ts[-1] > 0.15:
                    final_ts.append(timestamps[i])
        
        print(f"  [OK] Detected {len(final_ts)} visual cuts.")
        return final_ts
    except Exception as e:
        print(f"  [WARN] Scene detection failed: {e}")
        return []

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
        print(f"  [OK] Concatenated {len(input_paths)} segments (frame-perfect)")
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
    
    P1 SAFEGUARD (v12.6): Video duration is AUTHORITATIVE.
    If audio < video, audio is padded with silence to match video duration.
    This enforces the invariant: "Video timing is sacred, audio adapts."
    
    OPTIMIZED: Video stream is copied (already encoded), only audio is re-encoded.
    This prevents double-encoding quality loss and speeds up rendering.
    
    Args:
        video_path: Video file (can be silent)
        audio_path: Audio file to overlay
        output_path: Destination for merged video
        trim_to_shortest: DEPRECATED - kept for API compatibility but ignored
    """
    # P1 SAFEGUARD: Detect durations and pad audio if needed
    try:
        video_duration = get_video_duration(video_path)
        audio_duration = get_video_duration(audio_path)
    except Exception as e:
        print(f"  [WARN] Could not detect durations, proceeding without padding: {e}")
        video_duration = None
        audio_duration = None
    
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
    
    # P1 SAFEGUARD: Audio padding if needed
    if video_duration and audio_duration and audio_duration < video_duration:
        pad_duration = video_duration - audio_duration
        print(f"  [AUDIO PAD] Video is {pad_duration:.2f}s longer than audio - padding with silence")
        # Use apad filter to pad audio with silence to match video duration
        cmd.extend(["-af", f"apad=pad_dur={pad_duration:.3f}"])
    
    # CRITICAL: Never use -shortest (video timing is sacred)
    # trim_to_shortest parameter is ignored for safety
    
    cmd.extend(["-y", output_path])
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  [OK] Audio merged onto video (optimized)")
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
        print(f"  [OK] Silent video created")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Silent video creation failed: {e.stderr}")


# ============================================================================
# THUMBNAIL GENERATION (NEW)
# ============================================================================

def generate_thumbnail(video_path: str, thumbnail_path: str, time: float = 2.0) -> bool:
    """
    Extract a single frame from video to use as thumbnail.
    Optimized: calls ffprobe once.
    """
    Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        duration = get_video_duration(video_path)
    except Exception:
        duration = 0

    # Try multiple offsets: 2.0s, 5.0s, 0.5s, 0.0s
    for offset in [time, 5.0, 0.5, 0.0]:
        if duration > 0 and offset > duration:
            continue
            
        cmd = [
            "ffmpeg", "-v", "error",
            "-ss", str(offset),
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "4",
            "-y",
            thumbnail_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            if Path(thumbnail_path).exists() and Path(thumbnail_path).stat().st_size > 2000:
                return True
        except Exception:
            continue
            
    return False


def convert_to_mp4(input_path: str, output_path: str) -> None:
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-y",
        output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or "Unknown FFmpeg error"
        raise RuntimeError(f"MP4 conversion failed: {stderr}")


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

