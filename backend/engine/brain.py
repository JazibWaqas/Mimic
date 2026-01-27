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
from models import StyleBlueprint, ClipMetadata, ClipIndex, EnergyLevel, MotionType, Segment, BestMoment
from utils.api_key_manager import get_key_manager, get_api_key, rotate_api_key

# ============================================================================
# CACHE VERSIONING
# ============================================================================

# Separate cache versioning for reference vs clip analysis
# Reference and clip analysis use different prompts and should be versioned independently
REFERENCE_CACHE_VERSION = "7.0"  # v7.0: Enhanced narrative analysis with text overlay, content requirements, and experience goals (Jan 27, 2026)
CLIP_CACHE_VERSION = "6.1"        # v6.0: Deep semantic analysis + editing grammar intelligence (Jan 21, 2026)
# v5.0: Fixed string corruption bug + vibes loading (Jan 21, 2026)
# v4.0: Added vibes, content_description, and reasoning (Jan 19, 2026)
# v3.0: Comprehensive clip analysis with best moments (Jan 9, 2025)
# v2.0: Updated to detect actual cut points (Jan 9, 2025)
# v1.0: Initial prompt (3-8 segments, basic energy/motion)

# ============================================================================
# PROMPTS (These are CRITICAL—do not modify without testing)
# ============================================================================

REFERENCE_ANALYSIS_PROMPT = """
You are a professional video editor analyzing a REFERENCE VIDEO.

Your goal is to extract the EDITING STRUCTURE and CREATIVE INTENT of this video
so it can be applied to other footage.

You are NOT selecting clips.
You are NOT judging visual quality.
You are extracting intent, structure, and constraints.

---

## 1. TEXT & NARRATIVE CONTEXT (if present)

- text_overlay:
  Extract any readable on-screen text that appears in the video.
  If none exists, return an empty string.

- narrative_message:
  Interpret what the edit is trying to communicate or evoke for the viewer
  in ONE clear sentence.
  Focus on intent and purpose, not describing the footage itself.

- intent_clarity:
  How explicit the intent is in the reference.
  One of: "Clear", "Implicit", "Ambiguous"

### Text Interpretation Rule
If on-screen text appears to function primarily as:
- song lyrics
- timestamps, dates, counters, or calendars
- rapidly changing or decorative visual elements

then treat the text as a STRUCTURAL or MOOD device, not authorial intent.

In these cases:
- Set intent_clarity to "Implicit"
- Base narrative_message primarily on visual progression and pacing
- Do NOT infer story meaning directly from the literal text content

---

## 2. OVERALL EDITING ANALYSIS

- editing_style:
  (e.g., Cinematic, Vlog, Travel Montage, Memory Reel)

- emotional_intent:
  The dominant emotional tone the edit aims to evoke
  (e.g., Nostalgic, Energetic, Reflective)

- arc_description:
  Describe how energy evolves across the timeline
  (e.g., "Calm intro → steady build → energetic peak → soft outro")

---

## 3. CONTENT REQUIREMENTS (INTENT-LEVEL, NOT CLIP SELECTION)

Describe what TYPES of moments make this edit work.
Be semantic and experiential, not technical.

- must_have_content:
  3–5 types of moments this edit fundamentally relies on

- should_have_content:
  2–3 types of moments that would strengthen the edit

- avoid_content:
  Content types that would clash with the narrative intent of this edit.
  Avoid absolute exclusions when context could make them compatible.

Rules:
- Do NOT reference specific clips.
- Do NOT describe camera techniques.
- Describe meaning, not mechanics.

---

## 4. EXPERIENCE GOALS (FELT, NOT MECHANICAL)

- pacing_feel:
  How the edit FEELS rhythmically
  (e.g., breathable, relentless, reflective)

- visual_balance:
  What the edit emphasizes overall
  (e.g., people-centric, place-centric, balanced)

Describe the viewer experience, not BPM, cut speed, or timing.

---

## 5. SEGMENT STRUCTURE (CUT-TO-CUT)

Identify EVERY actual cut and define segments that match the exact editing rhythm.

For EACH segment:
- ENERGY: Low | Medium | High
- MOTION: Static | Dynamic
- VIBE: Single-word or short reusable noun phrase describing visible content
  (people, place, or activity)
- ARC_STAGE: Intro | Build-up | Peak | Outro

Rules:
- Detect REAL cuts only.
- Segment IDs must be sequential.
- Last segment MUST end exactly at total_duration.
- VIBE must describe visible content categories.
  Avoid abstract concepts, lighting conditions, or emotions as vibes.

---

## OUTPUT REQUIREMENTS

- Output VALID JSON ONLY.
- No markdown, no explanations.
- Do NOT assume future footage.
- Do NOT predict outcomes.
- Analysis must be reusable for applying this structure to DIFFERENT content.

---

## JSON SCHEMA

{
  "text_overlay": "",
  "narrative_message": "",
  "intent_clarity": "",
  "must_have_content": [],
  "should_have_content": [],
  "avoid_content": [],
  "pacing_feel": "",
  "visual_balance": "",
  "total_duration": 15.5,
  "editing_style": "",
  "emotional_intent": "",
  "arc_description": "",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 1.0,
      "duration": 1.0,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Candid",
      "arc_stage": "Intro"
    }
  ],
  "overall_reasoning": "",
  "ideal_material_suggestions": []
}
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

# NEW: Comprehensive clip analysis - gets EVERYTHING in one call
# This is the KEY optimization: instead of calling API per-segment,
# we analyze each clip ONCE and get best moments for ALL energy profiles
CLIP_COMPREHENSIVE_PROMPT = """
You are a professional video editor analyzing a clip to understand its energy profile and find the BEST MOMENTS for different editing needs.

WATCH THE ENTIRE CLIP carefully and provide:

1. **OVERALL CLASSIFICATION:**
   - Energy: The DOMINANT energy level (Low/Medium/High)
   - Motion: The DOMINANT motion type (Static/Dynamic)
   - Content Description: A brief 1-sentence description of what is happening in the clip
   - Vibes: 2-4 aesthetic/content tags (e.g., "Nature", "Urban", "Action", "Calm", "Friends", "Food", "Travel")

2. **BEST MOMENTS FOR EACH ENERGY LEVEL:**
   For each energy level, identify the SINGLE BEST continuous moment (2-4 seconds):
   
   - **High Energy Moment:** The most intense, action-packed, viral-worthy part
   - **Medium Energy Moment:** A moderately paced but visually interesting part
   - **Low Energy Moment:** The calmest, most stable, least dynamic part

WHAT MAKES A "BEST MOMENT":
- Visually compelling and suitable for that energy level
- Continuous footage (no cuts within the moment)
- Representative of that energy profile
- If clip doesn't have a perfect match, pick the closest available

OUTPUT FORMAT (JSON only, no markdown):
{
  "energy": "High",
  "motion": "Dynamic",
  "content_description": "A person dancing energetically in a neon-lit urban setting",
  "vibes": ["Urban", "Action", "Nightlife"],
  "best_moments": {
    "High": {
      "start": 8.2,
      "end": 10.5,
      "reason": "Peak dance move with fast motion"
    },
    "Medium": {
      "start": 4.0,
      "end": 6.2,
      "reason": "Walking transition with moderate movement"
    },
    "Low": {
      "start": 0.0,
      "end": 2.0,
      "reason": "Calm opening with minimal motion"
    }
  }
}

RULES:
- All timestamps in SECONDS (decimal like 8.2, not 8:12)
- start >= 0, end > start, end <= clip duration
- Each moment should be 2-4 seconds (adjust if clip is shorter)
- ALL three energy levels MUST have a best moment entry
- Choose the most visually interesting/compelling parts

Respond ONLY with valid JSON.
"""


# ============================================================================
# RATE LIMITING (Prevents hitting Gemini quotas)
# ============================================================================

from collections import deque

class RateLimiter:
    """
    Track and enforce Gemini API rate limits.
    
    Gemini 3 limits (approximate):
    - 15 requests/minute for flash models
    - 1500 requests/day
    
    This class ensures we don't exceed the per-minute limit by tracking
    request timestamps and waiting if necessary.
    """
    
    def __init__(self, max_requests_per_minute: int = 14):  # Leave 1 buffer
        self.max_rpm = max_requests_per_minute
        self.request_times: deque = deque(maxlen=max_requests_per_minute)
        self._enabled = True
    
    def wait_if_needed(self) -> float:
        """
        Block if we've hit rate limit, return time waited.
        
        Returns:
            Float: seconds waited (0 if no wait needed)
        """
        if not self._enabled:
            return 0.0
            
        now = time.time()
        
        # Remove requests older than 60 seconds
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
        
        waited = 0.0
        if len(self.request_times) >= self.max_rpm:
            # Wait until oldest request is 60s old
            sleep_time = 60 - (now - self.request_times[0]) + 0.5
            if sleep_time > 0:
                print(f"[RATE LIMIT] Waiting {sleep_time:.1f}s to avoid quota...")
                time.sleep(sleep_time)
                waited = sleep_time
        
        self.request_times.append(time.time())
        return waited
    
    def disable(self):
        """Disable rate limiting (for testing)."""
        self._enabled = False
    
    def enable(self):
        """Re-enable rate limiting."""
        self._enabled = True
    
    @property
    def requests_in_last_minute(self) -> int:
        """Get current request count in the last minute."""
        now = time.time()
        return sum(1 for t in self.request_times if now - t <= 60)


# Global rate limiter instance (DISABLED - we use key rotation instead)
rate_limiter = RateLimiter()
rate_limiter.disable()  # Gemini API enforces its own limits, we just rotate keys on 429


# ============================================================================
# CONFIGURATION
# ============================================================================

class GeminiConfig:
    """Configuration for Gemini API calls."""
    
    # Model selection - USING GEMINI 3 FOR HACKATHON
    MODEL_NAME = "gemini-3-flash-preview"  # Primary 2.0 Model
    FALLBACK_MODEL = "gemini-1.5-flash"     # Reliable Backup (High Quota)
    PRO_MODEL = "gemini-3-pro-preview"      # Higher tier backup
    EMERGENCY_FALLBACK = "gemini-2.0-flash-exp"
    
    # Generation config for consistent, structured output
    GENERATION_CONFIG = {
        "temperature": 0.1,  # Low temperature for consistency
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192  # Increased for deep reference analysis
    }

    # Safety settings to prevent false positive blocks during hackathon
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    # Retry config
    MAX_RETRIES = 5
    RETRY_DELAY = 1.0  # seconds


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def _handle_rate_limit_error(e: Exception, operation: str = "API call") -> bool:
    """
    Handle rate limit errors by rotating to the next API key.
    
    Args:
        e: The exception that occurred
        operation: Description of the operation (for logging)
    
    Returns:
        True if key was rotated, False if not a rate limit error or all keys exhausted
    """
    error_msg = str(e).lower()
    if "429" not in error_msg and "quota" not in error_msg:
        return False
    
    print(f"[QUOTA] Rate limit detected during {operation}")
    
    new_key = rotate_api_key(f"Rate limit during {operation}")
    if new_key:
        print(f"[QUOTA] Rotated to new API key, re-initializing genai...")
        genai.configure(api_key=new_key)
        return True
    else:
        print(f"[QUOTA] All API keys exhausted. Waiting 15s before retry...")
        time.sleep(15)
        return False


def initialize_gemini(api_key: str | None = None) -> genai.GenerativeModel:
    """
    Initialize Gemini API client with automatic fallback.
    
    Args:
        api_key: Optional API key. If None, uses API key manager.
    
    Returns:
        Configured GenerativeModel instance
    
    Raises:
        ValueError: If API key is not provided or found in environment
    """
    if api_key is None:
        api_key = get_api_key()
    
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
                generation_config=GeminiConfig.GENERATION_CONFIG,
                safety_settings=GeminiConfig.SAFETY_SETTINGS
            )
            print(f"[OK] Using model: {model_name}")
            return model
        except Exception as e:
            print(f"[WARN] Model {model_name} could not be initialized: {e}")
            continue
    
    raise ValueError("No Gemini models available. Check API key and model access.")


def _upload_video_with_retry(video_path: str) -> genai.File:
    """
    Upload video to Gemini with retry logic (NO key rotation - caller handles that).
    
    Args:
        video_path: Path to video file
    
    Returns:
        Uploaded file object
    
    Raises:
        Exception: If upload fails
    """
    # Single upload attempt - caller will retry with new key if needed
    rate_limiter.wait_if_needed()
    print(f"Uploading {Path(video_path).name}...")
    video_file = genai.upload_file(path=video_path)
    
    # Wait for processing to complete
    while video_file.state.name == "PROCESSING":
        print(f"Waiting for video processing (state: {video_file.state.name})...")
        time.sleep(20)
        rate_limiter.wait_if_needed()
        video_file = genai.get_file(video_file.name)
    
    if video_file.state.name == "FAILED":
        raise Exception(f"Video processing failed: {video_file.state}")
    
    print(f"Upload complete: {video_file.uri}")
    return video_file


def _parse_json_response(response_text: str) -> dict:
    """
    Parse Gemini's JSON response using brace balancing for robustness.
    """
    import re
    text = response_text.strip()

    # First try the simple regex for well-formed responses
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)

    # Use brace balancing to extract the outermost JSON object
    start_idx = text.find('{')
    if start_idx == -1:
        raise ValueError("No JSON object found in response")

    brace_count = 0
    end_idx = start_idx

    for i in range(start_idx, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i
                break

    if brace_count != 0:
        raise ValueError(f"Unbalanced braces in JSON response. Final count: {brace_count}")

    json_text = text[start_idx:end_idx + 1]

    try:
        data = json.loads(json_text)

        # Only clean the specific enum fields, NOT all strings
        # This prevents corrupting "reason" fields that contain words like "high" or "dynamic"
        from models import EnergyLevel, MotionType
        valid_energies = [e.value for e in EnergyLevel]
        valid_motions = [m.value for m in MotionType]

        def clean_enum_value(value: str, valid_values: list) -> str:
            """Clean a single enum value, handling hallucinations like 'LowLow'."""
            for v in valid_values:
                if v.lower() in value.lower():
                    return v
            return value

        # Only clean the top-level energy and motion fields
        if "energy" in data and isinstance(data["energy"], str):
            data["energy"] = clean_enum_value(data["energy"], valid_energies)
        if "motion" in data and isinstance(data["motion"], str):
            data["motion"] = clean_enum_value(data["motion"], valid_motions)

        # Clean energy/motion in segments if present (for reference analysis)
        if "segments" in data and isinstance(data["segments"], list):
            for seg in data["segments"]:
                if isinstance(seg, dict):
                    if "energy" in seg:
                        seg["energy"] = clean_enum_value(seg["energy"], valid_energies)
                    if "motion" in seg:
                        seg["motion"] = clean_enum_value(seg["motion"], valid_motions)

        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nExtracted text: {json_text[:200]}...")


# ============================================================================
# PUBLIC API
# ============================================================================

def subdivide_segments(blueprint: StyleBlueprint, max_segment_duration: float = 2.0) -> StyleBlueprint:
    """
    Split long segments into smaller chunks if they exceed the max duration.
    
    With real scene detection, we want to respect the original cuts more,
    so we increase the default max duration to 2.0s.
    """
    new_segments = []
    segment_id = 1
    
    for segment in blueprint.segments:
        if segment.duration > max_segment_duration:
            # Calculate how many splits we need
            num_splits = int(segment.duration / max_segment_duration) + 1
            split_duration = segment.duration / num_splits
            
            # Create sub-segments
            for i in range(num_splits):
                start_t = segment.start + (i * split_duration)
                end_t = segment.start + ((i + 1) * split_duration)
                
                # Snap last sub-segment to original end to avoid float drift
                if i == num_splits - 1:
                    end_t = segment.end
                    
                new_segments.append(Segment(
                    id=segment_id,
                    start=start_t,
                    end=end_t,
                    duration=end_t - start_t,
                    energy=segment.energy,
                    motion=segment.motion,
                    vibe=segment.vibe,
                    reasoning=segment.reasoning,
                    arc_stage=segment.arc_stage
                ))
                segment_id += 1
        else:
            # Keep segment as-is but update ID
            new_segments.append(Segment(
                id=segment_id,
                start=segment.start,
                end=segment.end,
                duration=segment.duration,
                energy=segment.energy,
                motion=segment.motion,
                vibe=segment.vibe,
                reasoning=segment.reasoning,
                arc_stage=segment.arc_stage
            ))
            segment_id += 1
    
    print(f"[SUBDIVISION] {len(blueprint.segments)} segments -> {len(new_segments)} segments (max {max_segment_duration:.1f}s each)")
    
    # Create new blueprint with subdivided segments, preserving style metadata
    return StyleBlueprint(
        total_duration=blueprint.total_duration,
        segments=new_segments,
        editing_style=blueprint.editing_style,
        emotional_intent=blueprint.emotional_intent,
        arc_description=blueprint.arc_description,
        overall_reasoning=blueprint.overall_reasoning,
        ideal_material_suggestions=blueprint.ideal_material_suggestions
    )


def analyze_reference_video(
    video_path: str, 
    api_key: str | None = None,
    scene_timestamps: List[float] | None = None
) -> StyleBlueprint:
    """
    Analyze reference video to extract editing structure.
    
    QUOTA OPTIMIZATION: Checks cache first.
    TEMPORAL HINTS: Uses scene_timestamps to ground Gemini's analysis.
    """
    print(f"\n{'='*60}")
    print(f"[BRAIN] ANALYZING REFERENCE VIDEO: {Path(video_path).name}")
    if scene_timestamps:
        print(f"[BRAIN] Using {len(scene_timestamps)} visual scene anchors.")
    print(f"{'='*60}\n")
    
    # Check cache first
    cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Cache key includes file hash AND number of hints to ensure fresh analysis if hints change
    import hashlib
    with open(video_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:12]
    
    if scene_timestamps:
        import hashlib
        hint_hash = hashlib.md5(",".join(map(lambda x: f"{x:.2f}", scene_timestamps)).encode()).hexdigest()[:8]
        cache_file = cache_dir / f"ref_{file_hash}_h{hint_hash}.json"
    else:
        cache_file = cache_dir / f"ref_{file_hash}_hints0.json"
    
    if cache_file.exists():
        print(f"[CACHE] Found cached analysis: {cache_file.name}")
        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
                
                # Check cache version
                cache_version = cache_data.get("_cache_version", "1.0")
                if cache_version != REFERENCE_CACHE_VERSION:
                    print(f"[CACHE] Reference version mismatch ({cache_version} vs {REFERENCE_CACHE_VERSION}). Re-analyzing...")
                    cache_file.unlink()
                else:
                    blueprint_data = {k: v for k, v in cache_data.items() if not k.startswith("_")}
                    blueprint = StyleBlueprint(**blueprint_data)

                    # Apply subdivision only if cache was not created with scene hints
                    # (preserve original rhythm when mimicking detected cuts)
                    if "hints0" in cache_file.name:
                        blueprint = subdivide_segments(blueprint)
                        print(f"[OK] Loaded from cache: {len(blueprint.segments)} segments (subdivided)")
                    else:
                        print(f"[OK] Loaded from cache: {len(blueprint.segments)} segments (preserved original rhythm)")

                    return blueprint
        except Exception as e:
            print(f"[WARN] Cache issue: {e}. Re-analyzing...")
    
    # Prepare Prompt
    from .processors import get_video_duration, remove_audio
    duration = get_video_duration(video_path)
    
    # Bypass recitation blocks by muting reference for analysis
    # This is safe because we only need visual rhythm/energy for analysis
    muted_path = str(cache_dir / f"muted_{file_hash}.mp4")
    if not Path(muted_path).exists():
        print(f"[BRAIN] Creating muted copy for analysis: {muted_path}")
        remove_audio(video_path, muted_path)
    
    analysis_video_path = muted_path
    
    if scene_timestamps:
        rounded_hints = [round(t, 2) for t in scene_timestamps]
        prompt = f"""
You are a professional video editor.

You MUST use these exact cut boundaries to define segments.
Cut boundaries (seconds): {rounded_hints}
Total duration: {duration}

Rules:
- Create segments exactly between [0.0] + cut_boundaries + [total_duration].
- Do NOT invent new cut times.
- For each segment, fill: energy, motion, vibe, arc_stage, reasoning.
- arc_stage must be one of: Intro, Build-up, Peak, Outro (choose best).
- vibe must be a short keyword: Nature, Urban, Action, Calm, Friends, Travel, etc.
- Output VALID JSON ONLY matching the schema below.
- Last segment end must equal total_duration exactly.

JSON schema:
{{
  "total_duration": {duration},
  "editing_style": "Cinematic Montage",
  "emotional_intent": "Dynamic",
  "arc_description": "Video with multiple scene changes",
  "segments": [
    {{
      "id": 1,
      "start": 0.0,
      "end": 1.23,
      "duration": 1.23,
      "energy": "Low|Medium|High",
      "motion": "Static|Dynamic",
      "vibe": "Nature",
      "arc_stage": "Intro|Build-up|Peak|Outro",
      "reasoning": "Based on scene change detection"
    }}
  ],
  "overall_reasoning": "Analysis based on visual scene changes",
  "ideal_material_suggestions": ["Varied content matching detected segments"]
}}
"""
    else:
        prompt = REFERENCE_ANALYSIS_PROMPT

    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            # Re-initialize model (handles key rotation if needed)
            model = initialize_gemini(api_key)
            video_file = _upload_video_with_retry(analysis_video_path)
            
            rate_limiter.wait_if_needed()
            response = model.generate_content([video_file, prompt])
            
            # Check for safety/recitation blocks
            if not response.candidates or response.candidates[0].finish_reason != 1:
                reason = "UNKNOWN"
                if response.candidates:
                    from google.generativeai.types import FinishReason
                    reason = FinishReason(response.candidates[0].finish_reason).name
                raise ValueError(f"Gemini blocked the response. Reason: {reason}")

            json_data = _parse_json_response(response.text)
            
            # Reconstruct from codes if that was the prompt used
            if "codes" in json_data:
                print(f"[BRAIN] Reconstructing from codes: {json_data['codes']}")
                codes = [c.strip().upper() for c in json_data["codes"].split(",")]
                energy_map = {"H": "High", "M": "Medium", "L": "Low"}
                motion_map = {"D": "Dynamic", "S": "Static"}
                
                full_timestamps = [0.0] + (scene_timestamps or []) + [duration]
                reconstructed_segments = []
                
                for i in range(len(full_timestamps) - 1):
                    # Use provided code or fallback to Medium/Dynamic
                    code = codes[i] if i < len(codes) else "MD"
                    e_code = code[0] if len(code) > 0 else "M"
                    m_code = code[1] if len(code) > 1 else "D"
                    
                    reconstructed_segments.append({
                        "id": i + 1,
                        "start": full_timestamps[i],
                        "end": full_timestamps[i+1],
                        "duration": full_timestamps[i+1] - full_timestamps[i],
                        "energy": energy_map.get(e_code, "Medium"),
                        "motion": motion_map.get(m_code, "Dynamic")
                    })
                json_data["segments"] = reconstructed_segments
                del json_data["codes"]

            blueprint = StyleBlueprint(**json_data)

            # Apply subdivision only if no scene hints (preserve original rhythm when mimicking)
            if not scene_timestamps:
                blueprint = subdivide_segments(blueprint)
                print(f"[OK] Applied subdivision: {len(blueprint.segments)} segments")
            else:
                print(f"[OK] Preserved original cut rhythm: {len(blueprint.segments)} segments (no subdivision)")
            
            # Save ORIGINAL to cache
            cache_data = {
                **json_data,
                "_cache_version": REFERENCE_CACHE_VERSION,
                "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"[OK] Analysis complete: {len(blueprint.segments)} segments.")
            return blueprint
            
        except Exception as e:
            print(f"[RETRY DEBUG] Reference analysis attempt {attempt + 1} failed: {e}")
            import traceback
            # traceback.print_exc()
            if _handle_rate_limit_error(e, "reference analysis"):
                continue
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze reference: {e}")
            time.sleep(GeminiConfig.RETRY_DELAY)
            
    raise Exception("Failed to analyze reference video after all retries and key rotations.")


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
            if _handle_rate_limit_error(e, "best moment analysis"):
                # Key rotated, retry immediately
                continue
            
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
            if _handle_rate_limit_error(e, "clip analysis"):
                # Key rotated, retry immediately
                continue
                
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze clip after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            time.sleep(GeminiConfig.RETRY_DELAY)


def analyze_all_clips(clip_paths: List[str], api_key: str | None = None, use_comprehensive: bool = True) -> ClipIndex:
    """
    Analyze all user clips and build a ClipIndex with comprehensive best moment data.
    
    OPTIMIZATION: 
    - Uses comprehensive prompt to get energy, motion, AND best moments in ONE call per clip
    - Rate limiting to prevent quota issues
    - Caching to avoid redundant analysis
    
    Args:
        clip_paths: List of paths to user clips
        api_key: Optional Gemini API key
        use_comprehensive: If True, use comprehensive prompt (default). 
                          If False, use legacy simple prompt.
    
    Returns:
        ClipIndex with full best_moments data for each clip
    """
    print(f"\n{'='*60}")
    print(f"[BRAIN] ANALYZING USER CLIPS ({len(clip_paths)} total)")
    print(f"[BRAIN] Mode: {'COMPREHENSIVE (energy + best moments)' if use_comprehensive else 'SIMPLE (energy only)'}")
    print(f"{'='*60}\n")

    clip_metadata_list = []

    for i, clip_path in enumerate(clip_paths):
        print(f"\n[{i+1}/{len(clip_paths)}] Processing {Path(clip_path).name}")

        from engine.processors import get_video_duration
        duration = get_video_duration(clip_path)

        # Initialize model for each clip to handle key rotation properly
        model = initialize_gemini(api_key)
        try:
            if use_comprehensive:
                clip_metadata = _analyze_single_clip_comprehensive(model, clip_path, duration)
            else:
                # Legacy mode - just energy/motion
                energy, motion = _analyze_single_clip_simple(model, clip_path)
                clip_metadata = ClipMetadata(
                    filename=Path(clip_path).name,
                    filepath=clip_path,
                    duration=duration,
                    energy=energy,
                    motion=motion
                )
        except Exception as e:
            print(f"    [ERROR] Analysis failed for {Path(clip_path).name}: {e}")
            # DO NOT use defaults - this would poison the cache
            # Let the exception propagate to the orchestrator
            raise Exception(f"Failed to analyze {Path(clip_path).name}: {e}")
        
        clip_metadata_list.append(clip_metadata)
    
    print(f"\n[OK] All {len(clip_paths)} clips analyzed")
    print(f"[OK] Rate limiter status: {rate_limiter.requests_in_last_minute} requests in last minute\n")
    return ClipIndex(clips=clip_metadata_list)


def _analyze_single_clip_comprehensive(
    model: genai.GenerativeModel, 
    clip_path: str, 
    duration: float
) -> ClipMetadata:
    """
    Analyze one clip comprehensively: energy, motion, AND best moments for all energy levels.
    
    This is the KEY function - ONE API call gets EVERYTHING we need for matching.
    
    Returns:
        ClipMetadata with best_moments populated for High/Medium/Low energy
    """
    print(f"  Analyzing comprehensively: {Path(clip_path).name}...")
    
    # Check cache
    cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    import hashlib
    with open(clip_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:12]
    
    cache_file = cache_dir / f"clip_comprehensive_{file_hash}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
                
                # Check cache version
                cache_version = cache_data.get("_cache_version", "1.0")
                if cache_version != CLIP_CACHE_VERSION:
                    print(f"    [CACHE] Clip version mismatch ({cache_version} vs {CLIP_CACHE_VERSION}) - invalidating...")
                    cache_file.unlink()
                else:
                    # Reconstruct ClipMetadata from cache
                    energy = EnergyLevel(cache_data["energy"])
                    motion = MotionType(cache_data["motion"])
                    
                    best_moments = None
                    if "best_moments" in cache_data:
                        best_moments = {
                            level: BestMoment(**moment_data)
                            for level, moment_data in cache_data["best_moments"].items()
                        }
                    
                    # Load vibes and content_description from cache
                    vibes = cache_data.get("vibes", [])
                    content_description = cache_data.get("content_description", "")
                    
                    print(f"    [CACHE] Loaded: {energy.value}/{motion.value} with {len(best_moments) if best_moments else 0} best moments")
                    if vibes:
                        print(f"    [CACHE] Vibes: {', '.join(vibes)}")
                    
                    return ClipMetadata(
                        filename=Path(clip_path).name,
                        filepath=clip_path,
                        duration=duration,
                        energy=energy,
                        motion=motion,
                        vibes=vibes,
                        content_description=content_description,
                        best_moments=best_moments
                    )
        except Exception as e:
            print(f"    [WARN] Cache corrupted: {e}. Re-analyzing...")
    
    
    # Cache miss - call API with retry and key rotation
    rate_limiter.wait_if_needed()
    
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            # CRITICAL: Upload with CURRENT key (re-upload if key rotated)
            video_file = _upload_video_with_retry(clip_path)
            
            print(f"    Requesting comprehensive analysis (attempt {attempt + 1})...")
            response = model.generate_content([video_file, CLIP_COMPREHENSIVE_PROMPT])
            json_data = _parse_json_response(response.text)
            
            # Parse overall classification
            energy = EnergyLevel(json_data["energy"])
            motion = MotionType(json_data["motion"])
            
            # Parse vibes and content (NEW)
            vibes = json_data.get("vibes", [])
            content_description = json_data.get("content_description", "")
            
            # Parse best moments
            best_moments = {}
            if "best_moments" in json_data:
                for level_name, moment_data in json_data["best_moments"].items():
                    # Validate timestamps
                    start = float(moment_data.get("start", 0))
                    end = float(moment_data.get("end", min(start + 2.0, duration)))
                    
                    # Clamp to valid range
                    start = max(0.0, min(start, duration - 0.1))
                    end = max(start + 0.1, min(end, duration))
                    
                    best_moments[level_name] = BestMoment(
                        start=start,
                        end=end,
                        reason=moment_data.get("reason", "")
                    )
            
            # Ensure all three energy levels have entries
            for level in ["High", "Medium", "Low"]:
                if level not in best_moments:
                    # Create fallback based on position in clip
                    if level == "High":
                        start = duration * 0.5  # Middle of clip
                    elif level == "Medium":
                        start = duration * 0.25
                    else:
                        start = 0.0
                    end = min(start + 2.5, duration)
                    best_moments[level] = BestMoment(
                        start=start,
                        end=end,
                        reason=f"Fallback: {level} moment not detected"
                    )
            
            # Save to cache (INCLUDING vibes and content!)
            cache_data = {
                "energy": energy.value,
                "motion": motion.value,
                "vibes": vibes,
                "content_description": content_description,
                "best_moments": {
                    level: {"start": bm.start, "end": bm.end, "reason": bm.reason or ""}
                    for level, bm in best_moments.items()
                },
                "_cache_version": CLIP_CACHE_VERSION,
                "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"    [OK] {energy.value}/{motion.value} with best moments:")
            for level, bm in best_moments.items():
                print(f"        {level}: {bm.start:.2f}s - {bm.end:.2f}s")
            if vibes:
                print(f"    Vibes: {', '.join(vibes)}")
            
            return ClipMetadata(
                filename=Path(clip_path).name,
                filepath=clip_path,
                duration=duration,
                energy=energy,
                motion=motion,
                vibes=vibes,
                content_description=content_description,
                best_moments=best_moments
            )
            
        except Exception as e:
            if _handle_rate_limit_error(e, "comprehensive clip analysis"):
                # Key rotated, REINITIALIZE MODEL
                model = initialize_gemini()
                continue
                
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze clip after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            time.sleep(GeminiConfig.RETRY_DELAY)


def _analyze_single_clip_simple(model: genai.GenerativeModel, clip_path: str) -> tuple[EnergyLevel, MotionType]:
    """
    Legacy simple clip analysis - just energy and motion (no best moments).
    
    Use this only if you don't need best moment data upfront.
    """
    print(f"  Analyzing (simple): {Path(clip_path).name}...")
    
    # Check cache
    cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    import hashlib
    with open(clip_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:12]
    
    cache_file = cache_dir / f"clip_simple_{file_hash}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
                cache_version = cache_data.get("_cache_version", "1.0")
                if cache_version != CLIP_CACHE_VERSION:
                    cache_file.unlink()
                else:
                    energy = EnergyLevel(cache_data["energy"])
                    motion = MotionType(cache_data["motion"])
                    print(f"    [CACHE] {energy.value} / {motion.value}")
                    return energy, motion
        except Exception as e:
            print(f"    [WARN] Cache corrupted: {e}. Re-analyzing...")
    
    # Cache miss - call API with rate limiting
    rate_limiter.wait_if_needed()
    
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            # CRITICAL: Upload with CURRENT key (re-upload if key rotated)
            video_file = _upload_video_with_retry(clip_path)
            
            response = model.generate_content([video_file, CLIP_ANALYSIS_PROMPT])
            json_data = _parse_json_response(response.text)
            
            energy = EnergyLevel(json_data["energy"])
            motion = MotionType(json_data["motion"])
            
            # Save to cache
            cache_data = {
                "energy": energy.value,
                "motion": motion.value,
                "_cache_version": CLIP_CACHE_VERSION,
                "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"    [OK] {energy.value} / {motion.value}")
            return energy, motion
            
        except Exception as e:
            if _handle_rate_limit_error(e, "comprehensive clip analysis"):
                # Key rotated, REINITIALIZE MODEL
                model = initialize_gemini()
                continue
                
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


# ============================================================================
# MOCK BRAIN MODE (For testing without API calls)
# ============================================================================

# Global mock mode flag
_MOCK_MODE = False


def set_mock_mode(enabled: bool = True):
    """
    Enable or disable mock mode for testing.
    
    When mock mode is enabled:
    - analyze_reference_video returns a synthetic blueprint
    - analyze_all_clips returns synthetic clip data with mock best moments
    - NO API calls are made
    
    Use this to test FFmpeg/rendering logic without burning API quota.
    """
    global _MOCK_MODE
    _MOCK_MODE = enabled
    print(f"[BRAIN] Mock mode: {'ENABLED' if enabled else 'DISABLED'}")


def is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return _MOCK_MODE


def create_mock_blueprint(video_path: str, segment_count: int = 8) -> StyleBlueprint:
    """
    Create a mock blueprint for testing.
    
    Args:
        video_path: Path to reference video (used for duration only)
        segment_count: Number of segments to create
    
    Returns:
        StyleBlueprint with alternating energy levels
    """
    print(f"[MOCK] Creating mock blueprint with {segment_count} segments")
    
    from engine.processors import get_video_duration
    duration = get_video_duration(video_path)
    
    segment_duration = duration / segment_count
    segments = []
    
    energy_cycle = [EnergyLevel.HIGH, EnergyLevel.MEDIUM, EnergyLevel.LOW]
    motion_cycle = [MotionType.DYNAMIC, MotionType.STATIC]
    
    current_time = 0.0
    for i in range(segment_count):
        end_time = min(current_time + segment_duration, duration)
        segments.append(Segment(
            id=i + 1,
            start=round(current_time, 2),
            end=round(end_time, 2),
            duration=round(end_time - current_time, 2),
            energy=energy_cycle[i % 3],
            motion=motion_cycle[i % 2]
        ))
        current_time = end_time
    
    blueprint = StyleBlueprint(total_duration=duration, segments=segments)
    print(f"[MOCK] Created: {len(segments)} segments, {duration:.2f}s total")
    return blueprint


def create_mock_clip_index(clip_paths: List[str]) -> ClipIndex:
    """
    Create a mock ClipIndex for testing.
    
    Each clip gets:
    - Random-ish energy and motion based on filename hash
    - Mock best moments at predictable positions (start, middle, end)
    
    Args:
        clip_paths: List of paths to user clips
    
    Returns:
        ClipIndex with mock analysis data
    """
    print(f"[MOCK] Creating mock clip index for {len(clip_paths)} clips")
    
    from engine.processors import get_video_duration
    
    clips = []
    for i, clip_path in enumerate(clip_paths):
        duration = get_video_duration(clip_path)
        
        # Assign energy based on index (deterministic but varied)
        energies = [EnergyLevel.HIGH, EnergyLevel.MEDIUM, EnergyLevel.LOW]
        energy = energies[i % 3]
        motion = MotionType.DYNAMIC if i % 2 == 0 else MotionType.STATIC
        
        # Create mock best moments at predictable positions
        best_moments = {}
        for level in ["High", "Medium", "Low"]:
            if level == "High":
                start = max(0.0, duration * 0.6)  # Later in clip (usually more action)
            elif level == "Medium":
                start = max(0.0, duration * 0.3)  # Middle-ish
            else:
                start = 0.0  # Beginning (usually calm)
            
            end = min(start + 2.5, duration)
            best_moments[level] = BestMoment(
                start=round(start, 1),
                end=round(end, 1),
                reason=f"Mock {level} moment for testing"
            )
        
        clip = ClipMetadata(
            filename=Path(clip_path).name,
            filepath=clip_path,
            duration=duration,
            energy=energy,
            motion=motion,
            best_moments=best_moments
        )
        clips.append(clip)
        print(f"  [MOCK] {clip.filename}: {energy.value}/{motion.value}")
    
    return ClipIndex(clips=clips)
