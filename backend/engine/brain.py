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
# CACHE VERSIONING
# ============================================================================

# Increment this when prompts change to invalidate old caches
CACHE_VERSION = "2.0"  # v2.0: Updated to detect actual cut points (Jan 9, 2025)
# v1.0: Initial prompt (3-8 segments, basic energy/motion)

# ============================================================================
# PROMPTS (These are CRITICAL—do not modify without testing)
# ============================================================================

REFERENCE_ANALYSIS_PROMPT = """
You are a professional video editor analyzing the EDITING STRUCTURE and CUT PATTERN of this video.

YOUR TASK: Identify EVERY significant cut/edit point and create segments that match the exact editing rhythm.

CRITICAL: This video's "DNA" is its CUT TIMING. You must detect:
- When cuts happen (scene changes, shot transitions)
- How frequently cuts occur (rapid cuts = many short segments, slow cuts = fewer long segments)
- The exact timing of each edit point

For videos with MANY CUTS: Create many short segments (0.5-2 seconds each)
For videos with FEW CUTS: Create fewer longer segments (2-5 seconds each)

For each segment, determine:

1. **ENERGY** (visual rhythm intensity):
   - **Low**: Slow camera movement, steady shots, minimal cuts, calm pacing
     Examples: Meditation videos, slow pans, locked-off shots
   - **Medium**: Moderate pacing, some camera movement, occasional cuts
     Examples: Vlogs, talking heads with B-roll, product demos
   - **High**: Rapid cuts, fast motion, intense action, high energy
     Examples: Sports highlights, dance trends, action sequences, TikTok edits

2. **MOTION** (camera + subject movement):
   - **Static**: Fixed camera, minimal subject movement
   - **Dynamic**: Panning, zooming, tracking, fast subject motion

RULES:
- Detect ACTUAL CUT POINTS - each major cut should create a new segment boundary
- Segment length should match cut frequency: Rapid cuts = 0.5-1.5s segments, Slow cuts = 2-5s segments
- For videos with many rapid cuts, create 10-30+ segments (one per major cut)
- For videos with few cuts, create 3-8 segments
- Segments must be contiguous (no gaps or overlaps)
- Base energy on PACING and CUT FREQUENCY, not on content emotion
- The last segment must end exactly at the video's total duration
- IMPORTANT: If you see rapid cuts (multiple cuts per second), create a segment for EACH significant cut

OUTPUT FORMAT (JSON only, no markdown code fences):
{
  "total_duration": 15.5,
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 0.8,
      "duration": 0.8,
      "energy": "High",
      "motion": "Dynamic"
    },
    {
      "id": 2,
      "start": 0.8,
      "end": 1.5,
      "duration": 0.7,
      "energy": "High",
      "motion": "Dynamic"
    },
    {
      "id": 3,
      "start": 1.5,
      "end": 4.0,
      "duration": 2.5,
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

BEST_MOMENT_PROMPT_TEMPLATE = """
You are a professional video editor analyzing a clip to find the SINGLE BEST MOMENT that matches a specific energy and motion profile.

TARGET PROFILE:
- Energy: {target_energy}
- Motion: {target_motion}
- Desired Duration: {target_duration:.2f} seconds

YOUR TASK:
Watch the ENTIRE clip and identify the SINGLE BEST continuous moment (lasting approximately {target_duration:.2f} seconds) that best matches the target profile.

CRITERIA FOR "BEST MOMENT":
1. The moment should have energy level matching "{target_energy}"
2. The moment should have motion type matching "{target_motion}"
3. The moment should be visually compelling and "viral-worthy"
4. The moment should be continuous (no cuts within it)
5. If multiple moments match, choose the MOST INTENSE or MOST DYNAMIC one

OUTPUT FORMAT (JSON only, no markdown):
{{
  "best_moment_start": 12.5,
  "best_moment_end": 15.2,
  "reason": "Brief explanation of why this moment matches (max 50 words)"
}}

IMPORTANT:
- Provide timestamps in SECONDS (decimal format, e.g., 12.5 not 12:30)
- best_moment_start must be >= 0
- best_moment_end must be > best_moment_start
- best_moment_end must be <= clip duration
- The duration (best_moment_end - best_moment_start) should be approximately {target_duration:.2f} seconds
- If no good moment exists, return the closest match you can find

Respond ONLY with valid JSON. Do not include explanations, markdown, or any other text.
"""


# ============================================================================
# CONFIGURATION
# ============================================================================

class GeminiConfig:
    """Configuration for Gemini API calls."""
    
    # Model selection - USING GEMINI 3 FOR HACKATHON
    MODEL_NAME = "gemini-3-flash-preview"  # Primary Hackathon Model
    FALLBACK_MODEL = "gemini-1.5-flash"     # Reliable Backup (High Quota)
    PRO_MODEL = "gemini-3-pro-preview"      # Higher tier backup
    EMERGENCY_FALLBACK = "gemini-2.0-flash-exp"
    
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
    
    # Try models in order: Gemini 3 Flash → Gemini 1.5 Flash (Backup) → Gemini 3 Pro
    models_to_try = [
        GeminiConfig.MODEL_NAME, 
        GeminiConfig.FALLBACK_MODEL, 
        GeminiConfig.PRO_MODEL,
        GeminiConfig.EMERGENCY_FALLBACK
    ]
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=GeminiConfig.GENERATION_CONFIG
            )
            print(f"[OK] Using model: {model_name}")
            return model
        except Exception as e:
            print(f"[WARN] Model {model_name} could not be initialized: {e}")
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
    Parse Gemini's JSON response, handling common formatting issues and cut-off text.
    """
    text = response_text.strip()
    
    # Remove markdown code fences
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Emergency repair for "unterminated string" or cut-off JSON
        print("[WARN] Attempting to repair malformed JSON...")
        # If it ends with a comma or incomplete object, try to close it
        text = text.strip()
        if text.endswith(","):
            text = text[:-1]
        
        # Count braces
        open_braces = text.count("{")
        close_braces = text.count("}")
        open_brackets = text.count("[")
        close_brackets = text.count("]")
        
        # Add missing closures
        text += "]" * (open_brackets - close_brackets)
        text += "}" * (open_braces - close_braces)
        
        try:
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"Failed to parse or repair JSON: {e}\nRaw: {response_text}")


# ============================================================================
# PUBLIC API
# ============================================================================

def analyze_reference_video(video_path: str, api_key: str | None = None) -> StyleBlueprint:
    """
    Analyze reference video to extract editing structure.
    
    QUOTA OPTIMIZATION: Checks cache first to avoid redundant API calls.
    Cache key is based on file hash, so same video = instant result.
    """
    print(f"\n{'='*60}")
    print(f"[BRAIN] ANALYZING REFERENCE VIDEO: {Path(video_path).name}")
    print(f"{'='*60}\n")
    
    # Check cache first
    cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Use file hash as cache key (same video = same hash)
    import hashlib
    with open(video_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:12]
    
    cache_file = cache_dir / f"ref_{file_hash}.json"
    
    if cache_file.exists():
        print(f"[CACHE] Found cached analysis: {cache_file.name}")
        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
                
                # Check cache version
                cache_version = cache_data.get("_cache_version", "1.0")  # Default to 1.0 for old caches
                if cache_version != CACHE_VERSION:
                    print(f"[CACHE] Version mismatch (cached: {cache_version}, current: {CACHE_VERSION})")
                    print(f"[CACHE] Prompt changed - invalidating cache and re-analyzing...")
                    cache_file.unlink()  # Delete old cache
                else:
                    # Remove metadata before validation
                    blueprint_data = {k: v for k, v in cache_data.items() if not k.startswith("_")}
                    blueprint = StyleBlueprint(**blueprint_data)
                    print(f"[OK] Loaded from cache (v{CACHE_VERSION}): {len(blueprint.segments)} segments")
                    return blueprint
        except Exception as e:
            print(f"[WARN] Cache corrupted or invalid: {e}. Re-analyzing...")
    
    # Cache miss - call API
    model = initialize_gemini(api_key)
    video_file = _upload_video_with_retry(video_path)
    
    # Generate analysis
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            print(f"Requesting analysis (attempt {attempt + 1})...")
            response = model.generate_content([video_file, REFERENCE_ANALYSIS_PROMPT])
            
            # Parse and validate
            json_data = _parse_json_response(response.text)
            blueprint = StyleBlueprint(**json_data)
            
            # Save to cache with version metadata
            cache_data = {
                **json_data,
                "_cache_version": CACHE_VERSION,
                "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            print(f"[CACHE] Saved to {cache_file.name} (v{CACHE_VERSION})")
            
            print(f"[OK] Analysis complete: {len(blueprint.segments)} segments")
            return blueprint
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                print(f"[QUOTA] Rate limit hit. Waiting 10s before retry...")
                time.sleep(10.0)
            
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze reference after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            
            print(f"Analysis failed: {e}. Retrying in {GeminiConfig.RETRY_DELAY}s...")
            time.sleep(GeminiConfig.RETRY_DELAY)


def find_best_moment(
    clip_path: str,
    target_energy: EnergyLevel,
    target_motion: MotionType,
    target_duration: float,
    api_key: str | None = None
) -> tuple[float, float]:
    """
    Find the best moment within a clip that matches target energy/motion profile.
    
    This uses Gemini 3's spatial-temporal reasoning to identify the most compelling
    moment within the clip, rather than just using sequential cuts.
    
    Args:
        clip_path: Path to clip file
        target_energy: Desired energy level
        target_motion: Desired motion type
        target_duration: Desired duration in seconds
        api_key: Optional Gemini API key
    
    Returns:
        Tuple of (start_time, end_time) in seconds
    
    Raises:
        Exception: If analysis fails
    """
    print(f"  Finding best moment in {Path(clip_path).name} for {target_energy.value}/{target_motion.value} ({target_duration:.2f}s)...")
    
    prompt = BEST_MOMENT_PROMPT_TEMPLATE.format(
        target_energy=target_energy.value,
        target_motion=target_motion.value,
        target_duration=target_duration
    )
    
    model = initialize_gemini(api_key)
    video_file = _upload_video_with_retry(clip_path)
    
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            response = model.generate_content([video_file, prompt])
            json_data = _parse_json_response(response.text)
            
            start = float(json_data["best_moment_start"])
            end = float(json_data["best_moment_end"])
            
            # Validate timestamps
            from engine.processors import get_video_duration
            clip_duration = get_video_duration(clip_path)
            
            if start < 0 or end <= start or end > clip_duration:
                print(f"    [WARN] Invalid timestamps from AI, using fallback")
                # Fallback: use first N seconds
                start = 0.0
                end = min(target_duration, clip_duration)
            else:
                print(f"    [OK] Best moment: {start:.2f}s - {end:.2f}s ({json_data.get('reason', 'N/A')})")
            
            return start, end
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                print(f"    [QUOTA] Rate limit hit. Waiting 10s...")
                time.sleep(10.0)
            
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                print(f"    [WARN] Best moment analysis failed, using fallback: {e}")
                # Fallback: use first N seconds
                from engine.processors import get_video_duration
                clip_duration = get_video_duration(clip_path)
                return 0.0, min(target_duration, clip_duration)
            
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
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                print(f"    [QUOTA] Rate limit hit on clip. Waiting 10s...")
                time.sleep(10.0)
                
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze clip after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            time.sleep(GeminiConfig.RETRY_DELAY)


def analyze_all_clips(clip_paths: List[str], api_key: str | None = None) -> ClipIndex:
    """
    Analyze all user clips and build a ClipIndex.
    
    OPTIMIZATION: Reuses single model instance for all clips to minimize API overhead.
    """
    print(f"\n{'='*60}")
    print(f"[BRAIN] ANALYZING USER CLIPS ({len(clip_paths)} total)")
    print(f"{'='*60}\n")
    
    # Initialize model ONCE for all clips
    model = initialize_gemini(api_key)
    
    clip_metadata_list = []
    
    for clip_path in clip_paths:
        from engine.processors import get_video_duration
        duration = get_video_duration(clip_path)
        
        # Analyze with Gemini (reusing model instance)
        try:
            energy, motion = _analyze_single_clip(model, clip_path)
        except Exception as e:
            print(f"    [WARN] Analysis failed for {Path(clip_path).name}: {e}")
            print(f"    Using default: Medium/Dynamic")
            energy = EnergyLevel.MEDIUM
            motion = MotionType.DYNAMIC
        
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


def _analyze_single_clip(model: genai.GenerativeModel, clip_path: str) -> tuple[EnergyLevel, MotionType]:
    """
    Internal helper: Analyze one clip using an existing model instance.
    
    QUOTA OPTIMIZATION: Caches results per clip to avoid redundant analysis.
    """
    print(f"  Analyzing {Path(clip_path).name}...")
    
    # Check cache
    cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    import hashlib
    with open(clip_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:12]
    
    cache_file = cache_dir / f"clip_{file_hash}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
                
                # Check cache version (clip analysis prompt hasn't changed, but check anyway)
                cache_version = cache_data.get("_cache_version", "1.0")
                if cache_version != CACHE_VERSION:
                    print(f"    [CACHE] Version mismatch - invalidating...")
                    cache_file.unlink()
                else:
                    energy = EnergyLevel(cache_data["energy"])
                    motion = MotionType(cache_data["motion"])
                    print(f"    [CACHE] {energy.value} / {motion.value}")
                    return energy, motion
        except Exception as e:
            print(f"    [WARN] Cache corrupted: {e}. Re-analyzing...")
    
    # Cache miss - call API
    video_file = _upload_video_with_retry(clip_path)
    
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            response = model.generate_content([video_file, CLIP_ANALYSIS_PROMPT])
            json_data = _parse_json_response(response.text)
            
            energy = EnergyLevel(json_data["energy"])
            motion = MotionType(json_data["motion"])
            
            # Save to cache with version metadata
            cache_data = {
                "energy": energy.value,
                "motion": motion.value,
                "_cache_version": CACHE_VERSION,
                "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"    [OK] {energy.value} / {motion.value}")
            return energy, motion
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                print(f"    [QUOTA] Rate limit hit on clip. Waiting 10s...")
                time.sleep(10.0)
                
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze clip after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            time.sleep(GeminiConfig.RETRY_DELAY)


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

