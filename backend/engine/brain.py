"""
Brain module: Gemini 3 API integration for video analysis.

This module handles ALL AI interactions. It NEVER touches the filesystem
directly—paths are provided by the orchestrator.
"""

from __future__ import annotations

import os
import json
import time
from pathlib import Path
from typing import List
import google.generativeai as genai
from models import StyleBlueprint, ClipMetadata, ClipIndex, EnergyLevel, MotionType, Segment

# ============================================================================
# PROMPTS (These are CRITICAL—do not modify without testing)
# ============================================================================

REFERENCE_ANALYSIS_PROMPT = """
You are a professional video editor analyzing the PACING STRUCTURE of this video.

YOUR TASK: Divide the video into 3-8 time-based segments based on editing rhythm.

IMPORTANT: Analyze the STRUCTURE, not the content. We don't care if it's a cat or a car—
we care about WHEN cuts happen, HOW FAST things move, and the RHYTHM of edits.

For each segment, determine:

1. **ENERGY** (visual rhythm intensity):
   - **Low**: Slow camera movement, steady shots, minimal cuts, calm pacing
     Examples: Meditation videos, slow pans, locked-off shots
   - **Medium**: Moderate pacing, some camera movement, occasional cuts
     Examples: Vlogs, talking heads with B-roll, product demos
   - **High**: Rapid cuts, fast motion, intense action, high energy
     Examples: Sports highlights, dance trends, action sequences

2. **MOTION** (camera + subject movement):
   - **Static**: Fixed camera, minimal subject movement
   - **Dynamic**: Panning, zooming, tracking, fast subject motion

RULES:
- Segments should be 2-5 seconds each (unless the video is very short)
- Segments must be contiguous (no gaps or overlaps)
- Base energy on PACING and RHYTHM, not on content emotion
- The last segment must end exactly at the video's total duration

OUTPUT FORMAT (JSON only, no markdown code fences):
{
  "total_duration": 15.5,
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 3.2,
      "duration": 3.2,
      "energy": "High",
      "motion": "Dynamic"
    },
    {
      "id": 2,
      "start": 3.2,
      "end": 8.0,
      "duration": 4.8,
      "energy": "Medium",
      "motion": "Static"
    }
  ]
}

Respond ONLY with valid JSON. Do not include explanations, markdown, or any other text.
"""

CLIP_ANALYSIS_PROMPT = """
You are analyzing a user-uploaded video clip to determine its dominant energy level and motion type.

ANALYZE:
1. **ENERGY** (overall intensity of the clip):
   - **Low**: Calm, slow-paced, minimal movement
   - **Medium**: Moderate activity and pacing
   - **High**: Intense, fast-paced, high energy

2. **MOTION** (camera + subject movement):
   - **Static**: Fixed camera, minimal subject movement
   - **Dynamic**: Active camera work or fast subject motion

RULES:
- Consider the ENTIRE clip (not just the first second)
- If motion varies, choose the dominant type
- Base energy on VISUAL INTENSITY, not audio or emotions

OUTPUT FORMAT (JSON only, no markdown):
{
  "energy": "High",
  "motion": "Dynamic"
}

Respond ONLY with valid JSON matching the schema above.
"""


# ============================================================================
# CONFIGURATION
# ============================================================================

class GeminiConfig:
    """Configuration for Gemini API calls."""
    
    # Model selection - USING GEMINI 3 FOR HACKATHON
    MODEL_NAME = "gemini-3-flash-preview"  # Primary model for Gemini 3 Hackathon
    FALLBACK_MODEL = "gemini-3-pro-preview"  # Use if Flash fails
    EMERGENCY_FALLBACK = "gemini-exp-1206"  # Use if both Gemini 3 models return 404
    
    # Generation config for consistent, structured output
    GENERATION_CONFIG = {
        "temperature": 0.1,  # Low temperature for consistency
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json"  # Force JSON output
    }
    
    # Retry config
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0  # seconds


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def initialize_gemini(api_key: str | None = None) -> genai.GenerativeModel:
    """
    Initialize Gemini API client with automatic fallback.
    
    Args:
        api_key: Optional API key. If None, reads from GEMINI_API_KEY env var.
    
    Returns:
        Configured GenerativeModel instance
    
    Raises:
        ValueError: If API key is not provided or found in environment
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Either pass api_key parameter or set "
            "GEMINI_API_KEY environment variable."
        )
    
    genai.configure(api_key=api_key)
    
    # Try models in order: Gemini 3 Flash → Gemini 3 Pro → Experimental
    for model_name in [GeminiConfig.MODEL_NAME, GeminiConfig.FALLBACK_MODEL, GeminiConfig.EMERGENCY_FALLBACK]:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=GeminiConfig.GENERATION_CONFIG
            )
            print(f"[OK] Using model: {model_name}")
            return model
        except Exception as e:
            print(f"[WARN] Model {model_name} not available: {e}")
            continue
    
    raise ValueError("No Gemini models available. Check API key and model access.")


def _upload_video_with_retry(video_path: str) -> genai.File:
    """
    Upload video to Gemini with retry logic.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Uploaded file object
    
    Raises:
        Exception: If all retries fail
    """
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            print(f"Uploading {Path(video_path).name}... (attempt {attempt + 1})")
            video_file = genai.upload_file(path=video_path)
            
            # Wait for processing to complete
            while video_file.state.name == "PROCESSING":
                print("Waiting for video processing...")
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise Exception(f"Video processing failed: {video_file.state}")
            
            print(f"Upload complete: {video_file.uri}")
            return video_file
            
        except Exception as e:
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to upload video after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            print(f"Upload failed: {e}. Retrying in {GeminiConfig.RETRY_DELAY}s...")
            time.sleep(GeminiConfig.RETRY_DELAY)


def _parse_json_response(response_text: str) -> dict:
    """
    Parse Gemini's JSON response, handling common formatting issues.
    
    Args:
        response_text: Raw response text from Gemini
    
    Returns:
        Parsed JSON as dictionary
    
    Raises:
        ValueError: If response is not valid JSON
    """
    # Remove markdown code fences if present
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]  # Remove ```json
    if text.startswith("```"):
        text = text[3:]  # Remove ```
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {text}")


# ============================================================================
# PUBLIC API
# ============================================================================

def analyze_reference_video(video_path: str, api_key: str | None = None) -> StyleBlueprint:
    """
    Analyze reference video to extract editing structure.
    
    Args:
        video_path: Path to reference video file
        api_key: Optional Gemini API key
    
    Returns:
        StyleBlueprint with timing and energy analysis
    
    Raises:
        Exception: If analysis fails after all retries
        ValueError: If Gemini returns invalid JSON
    """
    print(f"\n{'='*60}")
    print(f"[BRAIN] ANALYZING REFERENCE VIDEO: {Path(video_path).name}")
    print(f"{'='*60}\n")
    
    model = initialize_gemini(api_key)
    
    # Upload video
    video_file = _upload_video_with_retry(video_path)
    
    # Generate analysis
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            print(f"Requesting analysis... (attempt {attempt + 1})")
            response = model.generate_content([video_file, REFERENCE_ANALYSIS_PROMPT])
            
            # Parse and validate
            json_data = _parse_json_response(response.text)
            blueprint = StyleBlueprint(**json_data)
            
            print(f"[OK] Analysis complete: {len(blueprint.segments)} segments")
            return blueprint
            
        except Exception as e:
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze reference after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            print(f"Analysis failed: {e}. Retrying in {GeminiConfig.RETRY_DELAY}s...")
            time.sleep(GeminiConfig.RETRY_DELAY)


def analyze_clip(clip_path: str, api_key: str | None = None) -> tuple[EnergyLevel, MotionType]:
    """
    Analyze a single user clip to determine energy and motion.
    
    Args:
        clip_path: Path to clip file
        api_key: Optional Gemini API key
    
    Returns:
        Tuple of (energy, motion)
    
    Raises:
        Exception: If analysis fails after all retries
    """
    print(f"  Analyzing {Path(clip_path).name}...")
    
    model = initialize_gemini(api_key)
    video_file = _upload_video_with_retry(clip_path)
    
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            response = model.generate_content([video_file, CLIP_ANALYSIS_PROMPT])
            json_data = _parse_json_response(response.text)
            
            energy = EnergyLevel(json_data["energy"])
            motion = MotionType(json_data["motion"])
            
            print(f"    [OK] {energy.value} / {motion.value}")
            return energy, motion
            
        except Exception as e:
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze clip after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            time.sleep(GeminiConfig.RETRY_DELAY)


def analyze_all_clips(clip_paths: List[str], api_key: str | None = None) -> ClipIndex:
    """
    Analyze all user clips and build a ClipIndex.
    
    Args:
        clip_paths: List of paths to clip files
        api_key: Optional Gemini API key
    
    Returns:
        ClipIndex with metadata for all clips
    """
    print(f"\n{'='*60}")
    print(f"[BRAIN] ANALYZING USER CLIPS ({len(clip_paths)} total)")
    print(f"{'='*60}\n")
    
    clip_metadata_list = []
    
    for clip_path in clip_paths:
        # Get duration using ffprobe (from processors module)
        from engine.processors import get_video_duration
        duration = get_video_duration(clip_path)
        
        # Analyze with Gemini
        energy, motion = analyze_clip(clip_path, api_key)
        
        clip_metadata = ClipMetadata(
            filename=Path(clip_path).name,
            filepath=clip_path,
            duration=duration,
            energy=energy,
            motion=motion
        )
        clip_metadata_list.append(clip_metadata)
    
    print(f"\n[OK] All clips analyzed\n")
    return ClipIndex(clips=clip_metadata_list)


# ============================================================================
# FALLBACK MODE
# ============================================================================

def create_fallback_blueprint(video_path: str) -> StyleBlueprint:
    """
    Create a simple linear blueprint when Gemini fails.
    Segments are fixed 2-second intervals.
    
    Args:
        video_path: Path to reference video
    
    Returns:
        StyleBlueprint with even 2-second segments
    """
    print("[WARN] Using fallback mode: Linear 2-second segments")
    
    from engine.processors import get_video_duration
    duration = get_video_duration(video_path)
    
    segments = []
    current_time = 0.0
    segment_id = 1
    
    while current_time < duration:
        end_time = min(current_time + 2.0, duration)
        segments.append(Segment(
            id=segment_id,
            start=current_time,
            end=end_time,
            duration=end_time - current_time,
            energy=EnergyLevel.MEDIUM,  # Default to medium
            motion=MotionType.DYNAMIC
        ))
        current_time = end_time
        segment_id += 1
    
    return StyleBlueprint(total_duration=duration, segments=segments)

