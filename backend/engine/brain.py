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
REFERENCE_CACHE_VERSION = "8.0"  # v8.0: Editorial intelligence (shot_function, relation_to_previous, expected_hold, camera_movement), visual style (color_grading, visual_effects), music structure, text styling (Jan 31, 2026)
CLIP_CACHE_VERSION = "7.0"        # v7.0: Enhanced analysis with intensity, motion granularity, semantic content, and moment roles (Jan 27, 2026)
# v5.0: Fixed string corruption bug + vibes loading (Jan 21, 2026)
# v4.0: Added vibes, content_description, and reasoning (Jan 19, 2026)
# v3.0: Comprehensive clip analysis with best moments (Jan 9, 2025)
# v2.0: Updated to detect actual cut points (Jan 9, 2025)
# v1.0: Initial prompt (3-8 segments, basic energy/motion)

# ============================================================================
# PROMPTS (These are CRITICAL—do not modify without testing)
# ============================================================================

REFERENCE_ANALYSIS_PROMPT = """
You are a professional video editor, creative director, and post-production supervisor analyzing a REFERENCE VIDEO.

Your task is to extract EVERY aspect of this video's creative DNA — not just how it looks, but why each editorial decision works. This analysis will be used to recreate the EXACT editorial structure, semantic intent, and stylistic execution with different footage.

Think like a human editor, not a tagging system.

---

## 1. TEXT & NARRATIVE CONTEXT

- text_overlay:
  Extract ALL readable on-screen text that appears in the video.
  If multiple text elements appear, list them all separated by " | ".

- text_style:
  Describe the typography and text design:
  * Font style (e.g., Bold Sans-serif, Handwritten, Serif, Monospace)
  * Text animation (e.g., Static, Fade-in, Typewriter, Slide, Glitch)
  * Text placement (e.g., Center, Top-third, Bottom-third, Corner)
  * Text color and effects (e.g., White with glow, Gradient, Outline, Shadow)

- narrative_message:
  In ONE sentence, explain what this edit is trying to communicate emotionally or philosophically.

- intent_clarity:
  "Clear" | "Implicit" | "Ambiguous"

---

## 2. VISUAL STYLE & AESTHETICS

- color_grading:
  * Tone: Warm | Cool | Neutral | Desaturated | Vibrant
  * Contrast: High | Medium | Low
  * Specific look (e.g., Vintage film, Analog VHS, Teal-Orange, Moody dark)

- aspect_ratio:
  16:9 | 9:16 | 1:1 | 4:5 | 21:9 | Other

- visual_effects:
  List ALL recurring effects (Film grain, Light leaks, VHS noise, Chromatic aberration, Slow motion, Speed ramps, Vignette, Glitch, None).

- shot_variety:
  * Dominant scale: Extreme CU | CU | Medium | Wide | Extreme Wide | Mixed
  * Variety level: Consistent | Moderate | High variety

---

## 3. EDITING STYLE & RHYTHM

- editing_style:
  (Cinematic montage, Memory reel, Travel edit, Music video, Vlog, Documentary)

- cut_style:
  Hard cuts | Cross dissolves | Match cuts | Jump cuts | Mixed

- transition_effects:
  (Whip pans, Zooms, Morphs, None)

- emotional_intent:
  (Nostalgic, Reflective, Energetic, Playful, Dramatic, Peaceful)

- arc_description:
  Describe the emotional and energy progression over time.

- pacing_feel:
  Breathable | Relentless | Steady | Syncopated | Reflective

- visual_balance:
  People-centric | Place-centric | Balanced | Action-focused | Atmosphere-focused

---

## 4. AUDIO & MUSIC RELATIONSHIP

- music_sync:
  Tightly synced | Loosely synced | Independent

- audio_style:
  * Genre
  * Vocal presence: Instrumental | Vocals | Mixed
  * Energy: High | Mid | Slow/Ambient

---

## 5. CONTENT REQUIREMENTS (EDITORIAL CONSTRAINTS)

- must_have_content:
  3–5 moment types this edit fundamentally relies on (describe meaning, not mechanics).

- should_have_content:
  2–3 moment types that would strengthen the edit.

- avoid_content:
  Content that would break the emotional or narrative intent.

---

## 6. SEGMENT STRUCTURE (CUT-TO-CUT)

Identify EVERY REAL CUT and define segments.

For EACH segment:

- energy: Low | Medium | High
- motion: Static | Dynamic
- vibe: Single-word visible subject or activity
- shot_scale: Extreme CU | CU | Medium | Wide | Extreme Wide
- arc_stage: Intro | Build-up | Peak | Outro

### Editorial Intelligence (REQUIRED)

- shot_function:
  Establish | Action | Reaction | Detail | Transition | Release | Button

- relation_to_previous:
  Setup | Payoff | Contrast | Continuation | None

- expected_hold:
  Short | Normal | Long

- camera_movement:
  Locked | Handheld | Smooth pan | Erratic | Mixed

Rules:
- Detect REAL cuts only
- Segment IDs must be sequential
- Final segment must end exactly at total_duration

---

## 7. MUSIC STRUCTURE (EDITORIAL)

Analyze music structurally, not technically.

- music_structure:
  * phrases (intro, main, breakdown, resolve)
  * accent_moments (drops, emphasized beats)
  * ending_type (hard stop, fade, loop)

---

## OUTPUT REQUIREMENTS

- Output VALID JSON ONLY
- No markdown
- No explanations
- Fill ALL fields (use "" or [] if not applicable)

---

## JSON SCHEMA

{
  "text_overlay": "",
  "text_style": {
    "font_style": "",
    "animation": "",
    "placement": "",
    "color_effects": ""
  },
  "narrative_message": "",
  "intent_clarity": "",

  "color_grading": {
    "tone": "",
    "contrast": "",
    "specific_look": ""
  },
  "aspect_ratio": "",
  "visual_effects": [],
  "shot_variety": {
    "dominant_scale": "",
    "variety_level": ""
  },

  "editing_style": "",
  "cut_style": "",
  "transition_effects": [],
  "emotional_intent": "",
  "arc_description": "",
  "pacing_feel": "",
  "visual_balance": "",

  "music_sync": "",
  "audio_style": {
    "genre": "",
    "vocal_presence": "",
    "energy": ""
  },

  "must_have_content": [],
  "should_have_content": [],
  "avoid_content": [],

  "music_structure": {
    "phrases": [],
    "accent_moments": [],
    "ending_type": ""
  },

  "total_duration": 0.0,

  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 1.0,
      "duration": 1.0,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "People",
      "shot_scale": "Wide",
      "arc_stage": "Intro",
      "shot_function": "Establish",
      "relation_to_previous": "None",
      "expected_hold": "Normal",
      "camera_movement": "Handheld"
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
You are a professional video editor analyzing a USER-UPLOADED CLIP.

Your goal is to extract EDITING-RELEVANT INTELLIGENCE so this clip can be
used correctly inside an automated video editing system.

You are NOT judging artistic taste.
You are NOT comparing to other clips.
You are extracting structure, usability, and constraints.

---

## 1. ENERGY & MOTION CLASSIFICATION

### ENERGY (choose ONE based on PEAK visual intensity):

- LOW:
  Minimal visual change. Calm landscapes, still moments, slow movement,
  contemplative or quiet scenes.

- MEDIUM:
  Noticeable but controlled activity. Walking, casual interaction,
  steady camera movement, moderate pacing.

- HIGH:
  Intense visual activity or rapid change. Dancing, running, laughter,
  celebrations, action, fast camera movement.

IMPORTANT RULE:
If the clip contains ANY clear burst of HIGH energy, classify the clip as HIGH.
Do NOT default to MEDIUM when uncertain — lean toward LOW or HIGH.

### INTENSITY (within the chosen ENERGY level):
Choose ONE of: 1 | 2 | 3

- 1 = Mild / restrained
- 2 = Clear / expressive
- 3 = Strong / chaotic / peak-level

Intensity is ONLY used to compare clips within the SAME energy level.

---

### MOTION PROFILE (choose ONE based on DOMINANT motion source):

- STILL:
  Completely fixed camera with NO camera movement at all.
  Subjects may move minimally, but the camera frame is locked.

- GENTLE:
  Slow camera movement (pans, tilts, drifts) OR calm subject motion (walking).
  IMPORTANT: Even VERY SLOW camera movement counts as GENTLE, not STILL.

- ACTIVE:
  Energetic subject movement OR noticeable camera movement
  (running, dancing, tracking shots).

- KINETIC:
  Rapid camera movement and/or chaotic subject action.
  Highly unstable, intense, or visually aggressive motion.

CRITICAL RULE:
If you observe ANY camera movement (even subtle panning or tilting),
the motion CANNOT be STILL. Choose at least GENTLE.

---

## 2. SEMANTIC CONTENT ANALYSIS

### PRIMARY SUBJECT (choose 1–2 max):

- People-Solo
- People-Group
- People-Crowd
- Place-Nature
- Place-Urban
- Place-Indoor
- Activity-Travel
- Activity-Celebration
- Activity-Leisure
- Object-Animal
- Object-Vehicle
- Object-Landmark

### NARRATIVE UTILITY (choose 1–3 roles this clip can serve):

- Establishing (sets context or location)
- Transition (connects moments or movement)
- Build (increases engagement or anticipation)
- Peak (climactic, memorable moment)
- Reflection (calm, closing, or emotional pause)

### EMOTIONAL TONE (choose 1–2):

- Joyful
- Nostalgic
- Energetic
- Peaceful
- Adventurous
- Intimate
- Dramatic

---

## 3. EDITING USABILITY

### CLIP_QUALITY:
Rate overall visual appeal and usefulness for editing on a 1–5 scale.

- 1 = Unusable (blurry, extremely shaky, poor framing)
- 2 = Weak (acceptable but not compelling)
- 3 = Usable (solid, fits purpose)
- 4 = Strong (visually appealing, well-composed)
- 5 = Exceptional (standout, viral-worthy)

IMPORTANT:
Reserve 5 for truly exceptional clips.
Most clips should fall in the 3–4 range.

### BEST_FOR:
List 2–3 specific editing contexts where this clip excels.
Examples: "High-energy peaks", "Opening establishing shots", "Transitions"

### AVOID_FOR:
List 1–2 contexts that would clash with this clip's characteristics.
Examples: "Calm reflective outros", "Intimate close-up moments"

### CONTENT_DESCRIPTION:
ONE short sentence describing what is visibly happening.
Describe content, not interpretation.

---

## 4. BEST MOMENTS (TEMPORAL SELECTION)

For EACH energy level (High / Medium / Low),
identify the SINGLE BEST continuous moment lasting approximately 2–4 seconds.

For each moment, provide:
- start (seconds, decimal)
- end (seconds, decimal)
- moment_role: Establishing | Build | Climax | Transition | Reflection
- stable_moment: true if visually consistent for full duration, false otherwise
- reason: Brief explanation (max 20 words)

RULES:
- All timestamps in SECONDS
- start >= 0, end > start, end <= clip duration
- ALL three energy levels MUST be present
- If no perfect match exists, choose the closest available moment

---

## OUTPUT REQUIREMENTS

- Output VALID JSON ONLY.
- No markdown, no extra text.
- Do NOT assume future footage.
- Do NOT reference other clips.
- Be consistent and deterministic.

---

## JSON SCHEMA

{
  "energy": "High",
  "intensity": 3,
  "motion": "Active",

  "primary_subject": ["People-Group", "Activity-Celebration"],
  "narrative_utility": ["Peak", "Build"],
  "emotional_tone": ["Joyful", "Energetic"],

  "clip_quality": 4,
  "best_for": ["High-energy peaks", "Celebration montages"],
  "avoid_for": ["Calm reflective outros"],

  "content_description": "Friends laughing and celebrating together outdoors",

  "best_moments": {
    "High": {
      "start": 8.2,
      "end": 11.0,
      "moment_role": "Climax",
      "stable_moment": true,
      "reason": "Peak movement and expressive action"
    },
    "Medium": {
      "start": 4.0,
      "end": 6.5,
      "moment_role": "Build",
      "stable_moment": true,
      "reason": "Sustained motion with moderate intensity"
    },
    "Low": {
      "start": 0.5,
      "end": 2.8,
      "moment_role": "Establishing",
      "stable_moment": true,
      "reason": "Calm setup with minimal motion"
    }
  }
}
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
    
    # GEMINI 3 GLOBAL HACKATHON - ONLY GEMINI 3 MODELS ALLOWED
    MODEL_NAME = "gemini-3-flash-preview"  # Primary model
    PRO_MODEL = "gemini-3-pro-preview"      # Pro tier for complex analysis
    
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
    
    # Use Gemini 3 Flash (default) - NO FALLBACKS
    model_name = GeminiConfig.MODEL_NAME
    
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GeminiConfig.GENERATION_CONFIG,
            safety_settings=GeminiConfig.SAFETY_SETTINGS
        )
        print(f"[OK] Using Gemini 3 model: {model_name}")
        return model
    except Exception as e:
        raise ValueError(f"Failed to initialize Gemini 3 model '{model_name}': {e}")


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
                    arc_stage=segment.arc_stage,
                    shot_scale=segment.shot_scale,
                    shot_function=segment.shot_function,
                    relation_to_previous=segment.relation_to_previous,
                    expected_hold=segment.expected_hold,
                    camera_movement=segment.camera_movement
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
                arc_stage=segment.arc_stage,
                shot_scale=segment.shot_scale,
                shot_function=segment.shot_function,
                relation_to_previous=segment.relation_to_previous,
                expected_hold=segment.expected_hold,
                camera_movement=segment.camera_movement
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
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    cache_dir = BASE_DIR / "data" / "cache"
    ref_cache_dir = cache_dir / "references"
    muted_cache_dir = cache_dir / "muted"
    
    ref_cache_dir.mkdir(parents=True, exist_ok=True)
    muted_cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Cache key includes file hash AND number of hints to ensure fresh analysis if hints change
    from utils import get_file_hash, save_hash_registry
    file_hash = get_file_hash(video_path)
    
    # Try primary cache first
    matches = list(ref_cache_dir.glob(f"ref_{file_hash}_*.json"))
    
    # v12.5 Hardened: Legacy 12-char fallback
    if not matches and len(file_hash) > 12:
        legacy_hash = file_hash[:12]
        matches = list(ref_cache_dir.glob(f"ref_{legacy_hash}_*.json"))
        
    if matches:
        # Use the most specific/recent one
        cache_file = sorted(matches)[-1]
    else:
        # Define where we WOULD save a new one (using modern 32-char)
        if scene_timestamps:
            import hashlib
            hint_hash = hashlib.md5(",".join(map(lambda x: f"{x:.2f}", scene_timestamps)).encode()).hexdigest()[:8]
            cache_file = ref_cache_dir / f"ref_{file_hash}_h{hint_hash}.json"
        else:
            cache_file = ref_cache_dir / f"ref_{file_hash}_hints0.json"

    # Try primary cache first, then fallback to any existing cache for this video (Cache Inheritance)
    if not cache_file.exists():
        fallback_candidates = list(ref_cache_dir.glob(f"ref_{file_hash}_*.json"))
        # Also check legacy if current is missing
        if not fallback_candidates and len(file_hash) > 12:
            fallback_candidates = list(ref_cache_dir.glob(f"ref_{file_hash[:12]}_*.json"))
            
        if fallback_candidates:
            # Sort to get the most substantial one (more data = better intelligence)
            fallback_candidates.sort(key=lambda x: x.stat().st_size, reverse=True)
            print(f"[CACHE] Inheriting intelligence from previous analysis: {fallback_candidates[0].name}")
            cache_file = fallback_candidates[0]
        elif fallback_cache_file and fallback_cache_file.exists():
            print(f"[CACHE] Falling back to general analysis: {fallback_cache_file.name}")
            cache_file = fallback_cache_file
    
    if cache_file.exists():
        cache_type = "Hybrid Rhythmic" if "hints0" not in cache_file.name else "General"
        print(f"[CACHE] Found {cache_type} analysis: {cache_file.name}")
        try:
            # Read cache with UTF-8 encoding to handle emojis/unicode from Gemini
            with open(cache_file, encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check cache version (file is now closed, safe to delete if needed)
            cache_version = cache_data.get("_cache_version", "1.0")
            if cache_version != REFERENCE_CACHE_VERSION:
                print(f"[CACHE] Reference version mismatch ({cache_version} vs {REFERENCE_CACHE_VERSION}). Re-analyzing...")
                cache_file.unlink()  # Safe: file is closed
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
    muted_path = str(muted_cache_dir / f"muted_{file_hash}.mp4")
    if not Path(muted_path).exists():
        print(f"[BRAIN] Creating muted copy for analysis: {muted_path}")
        remove_audio(video_path, muted_path)
    
    analysis_video_path = muted_path
    
    analysis_video_path = muted_path
    
    prompt = REFERENCE_ANALYSIS_PROMPT
    if scene_timestamps:
        rounded_hints = [round(t, 2) for t in scene_timestamps]
        constraint_intro = f"""
### EDITORIAL CONSTRAINT: SCENE DETECTION HINTS
You MUST use these exact cut boundaries for your segment analysis.
Cut boundaries (seconds): {rounded_hints}
Total duration: {duration}

Rules for hinted analysis:
1. Every segment MUST start and end exactly on these timestamps.
2. Do NOT add or remove segments.
3. For each segment, provide the full editorial intelligence required below.

---
"""
        prompt = constraint_intro + REFERENCE_ANALYSIS_PROMPT
    
    # Inject actual duration into the schema if possible (search and replace last occurrence)
    if '"total_duration": 0.0,' in prompt:
        prompt = prompt.replace('"total_duration": 0.0,', f'"total_duration": {duration},')
    elif '"total_duration": 15.5,' in prompt:
        prompt = prompt.replace('"total_duration": 15.5,', f'"total_duration": {duration},')

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
            
            # Save ORIGINAL to cache with UTF-8 encoding
            cache_data = {
                **json_data,
                "_cache_version": REFERENCE_CACHE_VERSION,
                "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
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
    Analyze all user clips in PARALLEL using Gemini 3.
    Leverages multiple API keys to bypass sequential latency.
    """
    import concurrent.futures
    print(f"\n{'='*60}")
    print(f"[BRAIN] PARALLEL ANALYSIS: {len(clip_paths)} clips")
    print(f"[BRAIN] Model: gemini-3-flash-preview")
    print(f"{'='*60}\n")

    clip_metadata_list = [None] * len(clip_paths)

    def process_single_clip(index, clip_path):
        from engine.processors import get_video_duration
        duration = get_video_duration(clip_path)
        
        # Each thread gets its own model instance/key rotation context
        model = initialize_gemini(api_key)
        try:
            return _analyze_single_clip_comprehensive(model, clip_path, duration)
        except Exception as e:
            print(f"    [ERROR] Parallel analysis failed for {Path(clip_path).name}: {e}")
            raise e

    # Use ThreadPoolExecutor for I/O bound API calls
    # 5 workers is a safe balance for 28 keys to avoid hitting global IP limits
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_clip = {executor.submit(process_single_clip, i, path): i for i, path in enumerate(clip_paths)}
        for future in concurrent.futures.as_completed(future_to_clip):
            idx = future_to_clip[future]
            try:
                clip_metadata_list[idx] = future.result()
            except Exception as e:
                # Propagate failure to orchestrator
                raise e
    
    print(f"\n[OK] All {len(clip_paths)} clips analyzed in parallel")
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
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    cache_dir = BASE_DIR / "data" / "cache"
    clip_cache_dir = cache_dir / "clips"
    clip_cache_dir.mkdir(parents=True, exist_ok=True)
    
    from utils import get_file_hash
    file_hash = get_file_hash(clip_path)
    
    cache_file = clip_cache_dir / f"clip_comprehensive_{file_hash}.json"
    if not cache_file.exists() and len(file_hash) >= 12:
        legacy_file = clip_cache_dir / f"clip_comprehensive_{file_hash[:12]}.json"
        if legacy_file.exists():
            cache_file = legacy_file

    if cache_file.exists():
        try:
            # Read cache with UTF-8 encoding
            with open(cache_file, encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check cache version (file is now closed, safe to delete if needed)
            cache_version = cache_data.get("_cache_version", "1.0")
            if cache_version != CLIP_CACHE_VERSION:
                print(f"    [CACHE] Clip version mismatch ({cache_version} vs {CLIP_CACHE_VERSION}) - invalidating...")
                cache_file.unlink()  # Safe: file is closed
            else:
                    # Reconstruct ClipMetadata from cache
                    energy = EnergyLevel(cache_data["energy"])
                    
                    # Map new motion types to legacy enum (for v7.0 cache compatibility)
                    motion_str = cache_data.get("motion", "Dynamic")
                    motion_map = {
                        "STILL": "Static",
                        "GENTLE": "Dynamic",
                        "ACTIVE": "Dynamic",
                        "KINETIC": "Dynamic",
                        "Static": "Static",
                        "Dynamic": "Dynamic"
                    }
                    motion = MotionType(motion_map.get(motion_str, "Dynamic"))
                    
                    best_moments = None
                    if "best_moments" in cache_data:
                        best_moments = {
                            level: BestMoment(**moment_data)
                            for level, moment_data in cache_data["best_moments"].items()
                        }
                    
                    # Load v7.0+ fields (with fallbacks for backward compatibility)
                    intensity = cache_data.get("intensity", 2)
                    primary_subject = cache_data.get("primary_subject", [])
                    narrative_utility = cache_data.get("narrative_utility", [])
                    emotional_tone = cache_data.get("emotional_tone", [])
                    clip_quality = cache_data.get("clip_quality", 3)
                    best_for = cache_data.get("best_for", [])
                    avoid_for = cache_data.get("avoid_for", [])
                    
                    # Legacy fields
                    vibes = cache_data.get("vibes", [])
                    content_description = cache_data.get("content_description", "")
                    
                    # VIBE DERIVATION: If vibes are empty, derive from primary_subject for matcher compatibility
                    # This gives the matcher baseline semantic literacy without making it too smart
                    # The Advisor still has access to full V7 data for strategic reasoning
                    if not vibes and primary_subject:
                        vibes = [
                            subject.split('-')[1] if '-' in subject else subject
                            for subject in primary_subject
                        ]
                    
                    print(f"    [CACHE] Loaded: {energy.value}/{motion.value}/intensity={intensity} with {len(best_moments) if best_moments else 0} best moments")
                    if primary_subject:
                        print(f"    [CACHE] Subject: {', '.join(primary_subject)}")
                    if vibes:
                        print(f"    [CACHE] Derived vibes: {', '.join(vibes)}")
                    
                    return ClipMetadata(
                        filename=Path(clip_path).name,
                        filepath=clip_path,
                        duration=duration,
                        energy=energy,
                        motion=motion,
                        intensity=intensity,
                        primary_subject=primary_subject,
                        narrative_utility=narrative_utility,
                        emotional_tone=emotional_tone,
                        clip_quality=clip_quality,
                        best_for=best_for,
                        avoid_for=avoid_for,
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
            motion_str = json_data.get("motion", "Dynamic")
            
            # Map new motion types to legacy enum for backward compatibility
            motion_map = {
                "STILL": "Static",
                "GENTLE": "Dynamic",
                "ACTIVE": "Dynamic", 
                "KINETIC": "Dynamic",
                "Static": "Static",
                "Dynamic": "Dynamic"
            }
            motion = MotionType(motion_map.get(motion_str, "Dynamic"))
            
            # Parse v7.0+ enhanced fields
            intensity = json_data.get("intensity", 2)
            primary_subject = json_data.get("primary_subject", [])
            narrative_utility = json_data.get("narrative_utility", [])
            emotional_tone = json_data.get("emotional_tone", [])
            clip_quality = json_data.get("clip_quality", 3)
            best_for = json_data.get("best_for", [])
            avoid_for = json_data.get("avoid_for", [])
            
            # Legacy fields (maintained for backward compatibility)
            vibes = json_data.get("vibes", [])
            content_description = json_data.get("content_description", "")
            
            # Parse best moments with enhanced fields
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
                        moment_role=moment_data.get("moment_role", ""),
                        stable_moment=moment_data.get("stable_moment", True),
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
                        moment_role="Transition",
                        stable_moment=True,
                        reason=f"Fallback: {level} moment not detected"
                    )
            
            # Save to cache (v7.0+ enhanced format)
            cache_data = {
                "energy": energy.value,
                "motion": motion_str,  # Save the raw motion string (STILL/GENTLE/ACTIVE/KINETIC)
                "intensity": intensity,
                "primary_subject": primary_subject,
                "narrative_utility": narrative_utility,
                "emotional_tone": emotional_tone,
                "clip_quality": clip_quality,
                "best_for": best_for,
                "avoid_for": avoid_for,
                "vibes": vibes,
                "content_description": content_description,
                "best_moments": {
                    level: {
                        "start": bm.start, 
                        "end": bm.end, 
                        "moment_role": bm.moment_role,
                        "stable_moment": bm.stable_moment,
                        "reason": bm.reason or ""
                    }
                    for level, bm in best_moments.items()
                },
                "_cache_version": CLIP_CACHE_VERSION,
                "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            # VIBE DERIVATION: If vibes are empty, derive from primary_subject for matcher compatibility
            if not vibes and primary_subject:
                vibes = [
                    subject.split('-')[1] if '-' in subject else subject
                    for subject in primary_subject
                ]
            
            print(f"    [OK] {energy.value}/{motion_str}/intensity={intensity} with best moments:")
            for level, bm in best_moments.items():
                print(f"        {level}: {bm.start:.2f}s - {bm.end:.2f}s ({bm.moment_role})")
            if primary_subject:
                print(f"    Subject: {', '.join(primary_subject)}")
            if vibes:
                print(f"    Derived vibes: {', '.join(vibes)}")
            
            return ClipMetadata(
                filename=Path(clip_path).name,
                filepath=str(clip_path),
                duration=duration,
                energy=energy,
                motion=motion,
                intensity=intensity,
                primary_subject=primary_subject,
                narrative_utility=narrative_utility,
                emotional_tone=emotional_tone,
                clip_quality=clip_quality,
                best_for=best_for,
                avoid_for=avoid_for,
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
            with open(cache_file, 'w', encoding='utf-8') as f:
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
