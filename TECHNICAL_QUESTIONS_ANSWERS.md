# Technical Questions - Code Evidence

## Gemini Integration Depth

### 1. Exact Prompts Sent to Gemini

**File:** `backend/engine/brain.py`

**Reference Analysis Prompt (lines 37-80):**
```python
REFERENCE_ANALYSIS_PROMPT = """
You are a professional video editor. Analyze the EDITING DNA and EMOTIONAL ARC of this video.

YOUR TASK: Identify EVERY significant cut point and create segments that match the exact editing rhythm.

1. **OVERALL ANALYSIS**:
   - editing_style: (e.g., Cinematic, Vlog, Montage)
   - emotional_intent: (e.g., Nostalgic, Energetic, Peaceful)
   - arc_description: How the energy flows (e.g., "Slow build to fast climax").

2. **SEGMENT ANALYSIS**:
   For each cut-to-cut segment:
   - ENERGY: (Low/Medium/High)
   - MOTION: (Static/Dynamic)
   - VIBE: Aesthetic keyword (e.g., Nature, Urban, Candid)
   - ARC_STAGE: (Intro, Build-up, Peak, Outro)

RULES:
- Detect ACTUAL CUTS.
- Last segment MUST end at total_duration.
- Output VALID JSON ONLY.

JSON SCHEMA:
{
  "total_duration": 15.5,
  "editing_style": "...",
  "emotional_intent": "...",
  "arc_description": "...",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 3.2,
      "duration": 3.2,
      "energy": "Low",
      "motion": "Dynamic",
      "vibe": "Nature",
      "arc_stage": "Intro"
    }
  ],
  "overall_reasoning": "...",
  "ideal_material_suggestions": ["..."]
}
"""
```

**Clip Comprehensive Analysis Prompt (lines 148-205):**
```python
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
```

**Scene-Hinted Prompt (when scene_timestamps provided, lines 640-678):**
```python
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
...
"""
```

### 2. Token Count / Context Window Usage

**File:** `backend/engine/brain.py` (line 297)

```python
GENERATION_CONFIG = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192  # Increased for deep reference analysis
}
```

**Evidence:**
- `max_output_tokens: 8192` - This is the OUTPUT limit, not input
- No explicit token counting in code - Gemini handles this automatically
- Input: Video file (multimodal) + text prompt (~500-1000 tokens)
- Output: JSON response (typically 2000-5000 tokens for reference analysis, 500-1000 for clip analysis)
- **NOT using 1M context window** - We're using standard Gemini 3 Flash which has ~1M input capacity, but we're only sending single videos (~10-60 seconds) which is nowhere near that limit

### 3. Multiple Clips at Once?

**File:** `backend/engine/brain.py` (lines 876-932)

```python
def analyze_all_clips(clip_paths: List[str], api_key: str | None = None, use_comprehensive: bool = True) -> ClipIndex:
    ...
    for i, clip_path in enumerate(clip_paths):
        print(f"\n[{i+1}/{len(clip_paths)}] Processing {Path(clip_path).name}")
        ...
        model = initialize_gemini(api_key)
        try:
            if use_comprehensive:
                clip_metadata = _analyze_single_clip_comprehensive(model, clip_path, duration)
```

**Answer:** NO - Clips are analyzed ONE AT A TIME. Each clip gets its own API call in a loop (line 901).

### 4. Temperature/Reasoning Settings

**File:** `backend/engine/brain.py` (lines 283-298)

```python
class GeminiConfig:
    MODEL_NAME = "gemini-3-flash-preview"
    FALLBACK_MODEL = "gemini-1.5-flash"
    PRO_MODEL = "gemini-3-pro-preview"
    EMERGENCY_FALLBACK = "gemini-2.0-flash-exp"
    
    GENERATION_CONFIG = {
        "temperature": 0.1,  # Low temperature for consistency
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192
    }
    
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
```

**API Call (lines 379-383):**
```python
model = genai.GenerativeModel(
    model_name=model_name,
    generation_config=GeminiConfig.GENERATION_CONFIG,
    safety_settings=GeminiConfig.SAFETY_SETTINGS
)
```

**Answer:** 
- Temperature: 0.1 (very low for consistency)
- No reasoning mode explicitly set (using default)
- Safety settings: All set to BLOCK_NONE (for hackathon)

### 5. Post-Processing of Gemini Response

**File:** `backend/engine/brain.py` (lines 425-493)

```python
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
```

**Post-processing steps:**
1. Extract JSON from response text (handles markdown code blocks)
2. Parse JSON
3. Clean enum values (handles hallucinations like "LowLow" → "Low")
4. Validate and normalize energy/motion fields

### 1b. Actual Gemini Output Examples

**What Gemini Actually Returns - Reference Analysis:**

**Example 1: Best Performance (ref4) - File: `data/cache/ref_5782cea3a492_hda4304ec.json`**
```json
{
  "total_duration": 14.230975,
  "editing_style": "Cinematic Montage",
  "emotional_intent": "Dynamic",
  "arc_description": "Video with multiple scene changes",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 0.53,
      "duration": 0.53,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Nature",
      "arc_stage": "Intro",
      "reasoning": "Scene change to a blue raft on a river."
    },
    {
      "id": 2,
      "start": 0.53,
      "end": 0.93,
      "duration": 0.4,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Travel",
      "arc_stage": "Intro",
      "reasoning": "Scene change to a hand reaching out of a car window towards snowy mountains."
    },
    {
      "id": 3,
      "start": 0.93,
      "end": 1.4,
      "duration": 0.47,
      "energy": "High",
      "motion": "Dynamic",
      "vibe": "Friends",
      "arc_stage": "Intro",
      "reasoning": "Scene change to a group of friends in life jackets posing by a river."
    }
    // ... 27 more segments with similar detail
  ],
  "overall_reasoning": "The video is a fast-paced cinematic montage of travel memories with friends, featuring a repeating loop of short clips that create a dynamic and nostalgic feel.",
  "ideal_material_suggestions": [
    "High-quality travel footage",
    "Candid shots of friends",
    "Scenic nature views",
    "Action-oriented travel activities"
  ]
}
```

**What this shows:**
- Gemini identifies specific visual content ("blue raft", "hand reaching out", "group of friends in life jackets")
- Understands temporal structure (30 segments with precise timestamps)
- Extracts semantic vibes accurately (Nature, Travel, Friends)
- Recognizes editing patterns ("repeating loop", "fast-paced")
- Provides actionable suggestions

**Example 2: Average Performance (ref3) - File: `data/cache/ref_319465008ef0_hints0.json`**
```json
{
  "total_duration": 15.5,
  "editing_style": "Cinematic Montage",
  "emotional_intent": "Nostalgic & Joyful",
  "arc_description": "A rapid-fire collection of memories that maintains a high emotional peak throughout, celebrating friendship through diverse shared experiences and travel highlights.",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 1.0,
      "duration": 1.0,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Travel",
      "arc_stage": "Intro"
    },
    {
      "id": 2,
      "start": 1.0,
      "end": 2.0,
      "duration": 1.0,
      "energy": "High",
      "motion": "Dynamic",
      "vibe": "Celebration",
      "arc_stage": "Build-up"
    },
    {
      "id": 3,
      "start": 2.0,
      "end": 3.0,
      "duration": 1.0,
      "energy": "High",
      "motion": "Dynamic",
      "vibe": "Social",
      "arc_stage": "Build-up"
    }
    // ... 12 more segments
  ],
  "overall_reasoning": "The video employs a very strict rhythmic editing pattern, with cuts occurring almost exactly every second. This creates a 'heartbeat' effect that drives the viewer through a variety of locations and activities, reinforcing the theme of a shared life journey. The consistent text overlay acts as a thematic anchor across the diverse visual content.",
  "ideal_material_suggestions": [
    "Slow-motion shots of group laughter to emphasize emotional connection.",
    "Wide-angle drone shots of the group in vast landscapes to show the scale of their travels.",
    "Close-up candid shots of friends' faces during high-energy moments like the party or karaoke.",
    "Golden hour lighting for outdoor shots to enhance the nostalgic, warm aesthetic."
  ]
}
```

**What this shows:**
- Gemini detects abstract editing patterns ("heartbeat effect", "strict rhythmic pattern")
- Understands emotional intent ("Nostalgic & Joyful")
- Provides sophisticated suggestions ("Golden hour lighting", "slow-motion shots")
- Struggles with abstract vibes ("Social", "Candid", "Summer") - harder to match

**Example 3: Good Performance (ref5) - File: `data/cache/ref_d04cf94d4d8a_h32e59bfd.json`**
```json
{
  "total_duration": 16.64585,
  "editing_style": "Cinematic Montage",
  "emotional_intent": "Dynamic",
  "arc_description": "Video with multiple scene changes",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 0.77,
      "duration": 0.77,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Travel",
      "arc_stage": "Intro",
      "reasoning": "Intro shot from a moving bus, setting the travel theme."
    },
    {
      "id": 3,
      "start": 1.73,
      "end": 7.6,
      "duration": 5.87,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Nature",
      "arc_stage": "Build-up",
      "reasoning": "Montage of travel activities and scenery, building the narrative of the trip."
    }
    // ... 19 more segments
  ],
  "overall_reasoning": "The video is a classic travel montage, starting with the journey, building up with scenic views and activities, and peaking with high-energy social moments among friends. The rapid-fire cuts in the middle create a rhythmic build-up to the final celebration."
}
```

**What this shows:**
- Gemini understands narrative structure ("starting with journey", "building up", "peaking")
- Recognizes montage techniques ("rapid-fire cuts", "rhythmic build-up")
- Provides contextual reasoning for each segment

**What Gemini Actually Returns - Clip Analysis:**

**Example 1: Hiking Clip - File: `data/cache/clip_comprehensive_02c224a130e3.json`**
```json
{
  "energy": "Medium",
  "motion": "Dynamic",
  "vibes": ["Nature", "Travel", "Hiking"],
  "content_description": "A first-person perspective of walking along a rocky, uneven trail through a pine forest.",
  "best_moments": {
    "High": {
      "start": 31.0,
      "end": 34.0,
      "reason": "Navigating a rockier section with more camera movement and dynamic perspective."
    },
    "Medium": {
      "start": 5.0,
      "end": 8.0,
      "reason": "Steady walking on the trail, representing the overall pace of the hike."
    },
    "Low": {
      "start": 21.0,
      "end": 24.0,
      "reason": "A slightly flatter, more stable part of the walk with minimal camera shake."
    }
  }
}
```

**What this shows:**
- Gemini understands camera perspective ("first-person")
- Recognizes terrain characteristics ("rocky, uneven", "pine forest")
- Identifies energy variations within a single clip (High at 31s, Low at 21s)
- Provides reasoning for each best moment selection

**Example 2: Beach Wave Clip - File: `data/cache/clip_comprehensive_1a7017635be8.json`**
```json
{
  "energy": "High",
  "motion": "Dynamic",
  "vibes": ["Nature", "Beach", "Action"],
  "content_description": "A wave crashes onto a beach, eventually splashing over the camera lens.",
  "best_moments": {
    "High": {
      "start": 5.0,
      "end": 8.0,
      "reason": "The wave crashes directly into the camera, creating a high-energy splash and white foam."
    },
    "Medium": {
      "start": 2.5,
      "end": 5.0,
      "reason": "The wave builds up and begins to break, showing moderate motion and anticipation."
    },
    "Low": {
      "start": 0.0,
      "end": 2.5,
      "reason": "The opening shot shows relatively calm water before the main wave reaches the camera."
    }
  }
}
```

**What this shows:**
- Gemini understands temporal progression ("builds up", "crashes", "before main wave")
- Recognizes visual effects ("white foam", "splash")
- Identifies narrative arc within clip (calm → build-up → peak)

**Example 3: Beach Camels Clip - File: `data/cache/clip_comprehensive_23583adca7b6.json`**
```json
{
  "energy": "Medium",
  "motion": "Dynamic",
  "vibes": ["Travel", "Beach", "Animals"],
  "content_description": "A group of people and camels are gathered on a crowded beach under an overcast sky.",
  "best_moments": {
    "High": {
      "start": 1.2,
      "end": 3.2,
      "reason": "Dynamic camera movement panning across people towards the camels, creating a sense of discovery."
    },
    "Medium": {
      "start": 0.0,
      "end": 2.0,
      "reason": "Initial pan showing the beach environment and the scale of the crowd."
    },
    "Low": {
      "start": 2.5,
      "end": 4.272472,
      "reason": "The camera movement slows down as it focuses on the camels standing on the sand."
    }
  }
}
```

**What this shows:**
- Gemini understands camera techniques ("panning", "focuses")
- Recognizes emotional impact ("sense of discovery")
- Identifies multiple subjects and their relationships ("people and camels", "crowded beach")
- Understands pacing ("slows down")

**Intelligence Level Assessment:**

**Spatial-Temporal Understanding:**
- ✅ Recognizes camera movement and perspective
- ✅ Understands temporal progression within clips
- ✅ Identifies energy variations across time

**Semantic Understanding:**
- ✅ Extracts concrete vibes accurately (Nature, Travel, Beach)
- ⚠️ Struggles with abstract vibes (Social, Candid, Summer)
- ✅ Provides detailed content descriptions

**Editing Intelligence:**
- ✅ Recognizes editing patterns (montage, rhythmic cuts)
- ✅ Understands narrative structure (intro → build-up → peak → outro)
- ✅ Provides actionable suggestions for material selection

**Precision:**
- ✅ Frame-accurate timestamps (0.53s, 0.93s, etc.)
- ✅ Consistent JSON structure
- ✅ Validates against clip duration

---

## Matching Algorithm

### 6. Complete Matching Algorithm - Gemini vs Deterministic

**File:** `backend/engine/editor.py` (lines 26-522)

**Where Gemini's output is used:**

**Lines 200-268:** Scoring function uses Gemini-extracted data:
```python
def score_clip_smart(clip: ClipMetadata, segment, last_motion, last_vibe) -> tuple[float, str, bool]:
    score = 0.0
    reasons = []
    vibe_matched = False

    # 1. DISCOVERY & REUSE (Deterministic)
    usage = clip_usage_count[clip.filename]
    if usage == 0:
        score += 50.0
        reasons.append("✨ New")
    else:
        score -= (usage * 20.0)
        reasons.append(f"Used:{usage}x")

    # 2. SEMANTIC PROXIMITY (Uses Gemini vibes)
    target_vibe = (segment.vibe or "general").lower()  # FROM GEMINI REFERENCE ANALYSIS
    clip_vibes = [v.lower() for v in clip.vibes]  # FROM GEMINI CLIP ANALYSIS
    
    # Check for direct match
    if any(target_vibe in v or v in target_vibe for v in clip_vibes):
        score += 30.0
        reasons.append(f"Vibe:{segment.vibe}")
        vibe_matched = True
    else:
        # Check for semantic neighbor match (Deterministic mapping)
        neighbor_hit = False
        for category, neighbors in SEMANTIC_MAP.items():
            if target_vibe in neighbors or target_vibe == category:
                if any(v in neighbors for v in clip_vibes):
                    score += 15.0
                    reasons.append(f"Nearby:{category}")
                    neighbor_hit = True
                    vibe_matched = True
                    break

    # 3. CINEMATIC FLOW (Uses Gemini content_description)
    content = (clip.content_description or "").lower()  # FROM GEMINI CLIP ANALYSIS
    
    # 4. ENERGY ARC ALIGNMENT (Uses Gemini energy classification)
    if clip.energy == segment.energy:  # BOTH FROM GEMINI
        score += 15.0
        reasons.append(f"{clip.energy.value}")
    else:
        score -= 5.0
        reasons.append(f"~{clip.energy.value}")

    # 5. RECENT COOLDOWN (Deterministic)
    time_since_last_use = timeline_position - clip_last_used_at[clip.filename]
    if time_since_last_use < MIN_CLIP_REUSE_GAP:
        score -= 100.0
        reasons.append("Cooldown")

    return score, reasoning, vibe_matched
```

**Lines 352-375:** Best moment selection uses Gemini pre-computed data:
```python
if selected_clip.best_moments:  # FROM GEMINI COMPREHENSIVE ANALYSIS
    best_moment = selected_clip.get_best_moment_for_energy(segment.energy)
    if best_moment:
        window_start, window_end = best_moment  # GEMINI PRE-COMPUTED TIMESTAMPS
        current_pos = clip_current_position[selected_clip.filename]
        
        if window_start <= current_pos < window_end:
            clip_start = current_pos
        else:
            clip_start = window_start
        
        clip_end = min(clip_start + use_duration, window_end)
```

**Deterministic parts:**
- Usage tracking (lines 82-93)
- Energy eligibility filtering (lines 129-146)
- Beat alignment (lines 344-350)
- Timeline management (lines 148-161)
- Duration calculation (lines 304-342)

**Answer:** Gemini provides the DATA (vibes, energy, best moments, content_description). The matching ALGORITHM is deterministic scoring based on that data.

### 7. Could Matching Be Replaced with Gemini Prompt?

**Current approach:** Pre-analyze clips → deterministic matching

**Alternative Gemini prompt would be:**
```
You are matching clips to segments. Given:
- Reference segments: [list of segments with vibes/energy]
- Available clips: [list of clips with vibes/energy/best_moments]

For each segment, select the best clip and exact timestamps.
Consider: vibe matching, energy compatibility, diversity, flow.

Output JSON with edit decisions.
```

**Why current approach is better:**
- Faster: 1 API call per clip upfront vs 1 call per segment during matching
- More reliable: Deterministic matching ensures timeline integrity
- Cheaper: 55 clip analyses vs potentially 30+ matching calls
- Better control: Can enforce rules (no repeats, cooldowns, etc.)

---

## Current Capabilities

### 8. Data Available But Not Surfaced in UI

**File:** `backend/engine/orchestrator.py` (lines 393-558)

**X-Ray data printed but not returned to frontend:**

```python
def _print_comprehensive_analysis(blueprint: StyleBlueprint, edl: EDL, clip_index: ClipIndex, clip_paths: List[str]) -> None:
    # 1. Reference Analysis Breakdown
    print(f"\n📹 Reference Analysis:")
    print(f"   Editing Style: {blueprint.editing_style}")
    print(f"   Emotional Intent: {blueprint.emotional_intent}")
    print(f"   Arc Description: {blueprint.arc_description}")
    
    # 2. Blueprint Full Detail
    print(f"\n📑 BLUEPRINT FULL SEGMENT LIST:")
    for i, seg in enumerate(blueprint.segments):
        print(f"   {i+1:02d}: {seg.start:5.2f}-{seg.end:5.2f}s | {seg.energy.value:6} | Vibe: {seg.vibe:10} | {seg.arc_stage}")
    
    # 3. Arc Stage Distribution
    # 4. Vibe Distribution
    # 5. Clip Usage Analysis
    # 6. Reasoning Breakdown
    # 7. Vibe Matching Stats
    # 8. Cut Statistics
    # 9. Sample Reasoning Examples
    # 10. Clip Index Stats
    # 11. Temporal Precision Check
    # 12. Material Efficiency Stats
```

**Available in PipelineResult but not exposed via API:**
- `blueprint` (full StyleBlueprint)
- `clip_index` (full ClipIndex with all metadata)
- `edl` (all edit decisions with reasoning)

**File:** `backend/main.py` (lines 323-324)
```python
active_sessions[session_id]["blueprint"] = result.blueprint.model_dump() if result.blueprint else None
active_sessions[session_id]["clip_index"] = result.clip_index.model_dump() if result.clip_index else None
```

**Answer:** All X-Ray data is stored in session but `/api/status` endpoint doesn't return it. Only returns basic status/progress.

### 9. End-to-End Flow When User Clicks "Generate"

**File:** `backend/main.py` (lines 201-235)

```python
@app.post("/api/generate/{session_id}")
async def generate_video(session_id: str, background_tasks: BackgroundTasks):
    session = active_sessions[session_id]
    session["status"] = "processing"
    
    background_tasks.add_task(
        process_video_pipeline,
        session_id,
        session.get("reference_path"),
        session.get("clip_paths")
    )
```

**File:** `backend/main.py` (lines 238-340) → calls `run_mimic_pipeline`

**File:** `backend/engine/orchestrator.py` (lines 52-386)

**Complete flow:**
1. **Validate inputs** (lines 133-158)
   - Check reference exists, duration 3-60s
   - Check clip count >= 2
   - Setup temp directories

2. **Analyze reference** (lines 162-186)
   - Detect scene changes (FFmpeg)
   - Detect BPM (librosa)
   - Call `analyze_reference_video()` → Gemini API
   - Returns StyleBlueprint

3. **Analyze clips** (lines 191-247)
   - Call `analyze_all_clips()` → Loop of Gemini API calls (one per clip)
   - Standardize clips (FFmpeg, cached)
   - Returns ClipIndex

4. **Match clips** (lines 252-270)
   - Call `match_clips_to_blueprint()` → Deterministic algorithm
   - Uses Gemini-extracted vibes/energy/best_moments
   - Returns EDL

5. **Render** (lines 275-320)
   - Extract segments (FFmpeg)
   - Concatenate (FFmpeg)
   - Merge audio (FFmpeg)
   - Validate output

**Decision points:**
- Line 184: Gemini fails → fallback blueprint
- Line 199: Gemini fails → default energy levels
- Line 264: EDL validation fails → continue anyway (warning)

### 10. Feedback Loop / Iteration

**Answer:** NO feedback loop. Everything is single-pass.

**Evidence:**
- `run_mimic_pipeline()` runs once and returns
- No retry logic for matching (only for API calls)
- No iterative refinement of edit decisions
- No user feedback integration

---

## Technical Constraints

### 11. Single Gemini API Call Duration

**No explicit timing in code**, but from X-Ray logs:
- Reference analysis: ~20-60 seconds (includes video upload + processing wait)
- Clip analysis: ~5-15 seconds per clip (includes upload + processing)

**File:** `backend/engine/brain.py` (lines 411-422)
```python
def _upload_video_with_retry(video_path: str) -> genai.File:
    video_file = genai.upload_file(path=video_path)
    
    # Wait for processing to complete
    while video_file.state.name == "PROCESSING":
        print(f"Waiting for video processing (state: {video_file.state.name})...")
        time.sleep(20)  # Wait 20 seconds between checks
        video_file = genai.get_file(video_file.name)
```

**Answer:** 
- Upload + processing wait: 20-60s per video
- Actual API call: ~2-5 seconds
- Total per clip: ~5-15s (cached clips: instant)

### 12. Practical Demo Time Limit

**From X-Ray logs:**
- Best case (ref4): 18.9s total (cached)
- Average case (ref3): 64.2s total (1 new reference analysis)
- Worst case: 450-650s uncached (55 clips × ~10s each)

**File:** `backend/engine/orchestrator.py` (line 325)
```python
processing_time = time.time() - start_time
```

**Answer:** 
- Cached: 15-20s (acceptable for demo)
- Uncached: 7-10 minutes (too long for live demo)
- **Demo strategy:** Pre-cache reference + clips before presentation

### 13. Caching Logic

**File:** `backend/engine/brain.py`

**Reference caching (lines 582-624):**
```python
# Cache key includes file hash AND number of hints
with open(video_path, 'rb') as f:
    file_hash = hashlib.md5(f.read()).hexdigest()[:12]

if scene_timestamps:
    hint_hash = hashlib.md5(",".join(map(lambda x: f"{x:.2f}", scene_timestamps)).encode()).hexdigest()[:8]
    cache_file = cache_dir / f"ref_{file_hash}_h{hint_hash}.json"
else:
    cache_file = cache_dir / f"ref_{file_hash}_hints0.json"

if cache_file.exists():
    with open(cache_file) as f:
        cache_data = json.load(f)
        cache_version = cache_data.get("_cache_version", "1.0")
        if cache_version != REFERENCE_CACHE_VERSION:
            cache_file.unlink()  # Invalidate on version mismatch
        else:
            blueprint = StyleBlueprint(**blueprint_data)
            return blueprint  # RETURN CACHED
```

**Clip caching (lines 950-1001):**
```python
with open(clip_path, 'rb') as f:
    file_hash = hashlib.md5(f.read()).hexdigest()[:12]

cache_file = cache_dir / f"clip_comprehensive_{file_hash}.json"

if cache_file.exists():
    cache_data = json.load(f)
    cache_version = cache_data.get("_cache_version", "1.0")
    if cache_version != CLIP_CACHE_VERSION:
        cache_file.unlink()  # Invalidate on version mismatch
    else:
        # Reconstruct ClipMetadata from cache
        return ClipMetadata(...)  # RETURN CACHED
```

**Standardization caching (lines 221-236 in orchestrator.py):**
```python
cache_key_source = f"{input_p.absolute()}_{file_stat.st_size}_{file_stat.st_mtime}"
cache_hash = hashlib.md5(cache_key_source.encode()).hexdigest()
cached_filename = f"std_{cache_hash}.mp4"
cached_path = persistent_standardized_cache / cached_filename

if cached_path.exists():
    shutil.copy2(str(cached_path), str(output_path))  # USE CACHED
else:
    standardize_clip(clip_path, str(output_path))
    shutil.copy2(str(output_path), str(cached_path))  # SAVE TO CACHE
```

**What's cached:**
- ✅ Gemini reference analysis (JSON)
- ✅ Gemini clip analysis (JSON)
- ✅ Standardized video files (MP4)
- ❌ NOT cached: EDL (recomputed each time)
- ❌ NOT cached: Final output video

**Cache invalidation:**
- Cache version mismatch → invalidate
- File hash change → new cache entry
- Scene hints change → new reference cache entry

---

## Gemini Intelligence Level Analysis

### What Gemini Demonstrates

**1. Visual Understanding:**
- Recognizes specific objects ("blue raft", "camels", "prayer flags")
- Understands camera techniques ("first-person perspective", "panning", "focuses")
- Identifies settings ("pine forest", "crowded beach", "snowy mountains")
- Recognizes visual effects ("white foam", "steam rising")

**2. Temporal Reasoning:**
- Identifies energy variations within clips (High at 31s, Low at 21s in hiking clip)
- Understands progression ("wave builds up", "camera movement slows down")
- Recognizes editing rhythm ("cuts occurring almost exactly every second")
- Provides frame-accurate timestamps

**3. Semantic Classification:**
- Concrete vibes: Excellent (Nature, Travel, Beach, Friends) - 100% match rate
- Abstract vibes: Struggles (Social, Candid, Summer, Freedom) - 53% match rate
- Content description: Detailed and accurate ("A first-person perspective of walking along a rocky, uneven trail")

**4. Editing Intelligence:**
- Recognizes editing styles ("Cinematic Montage", "rapid-fire collection")
- Understands emotional arcs ("Nostalgic & Joyful", "Dynamic")
- Identifies narrative structure (Intro → Build-up → Peak → Outro)
- Provides sophisticated suggestions ("Golden hour lighting", "slow-motion shots")

**5. Best Moment Selection:**
- Identifies visually compelling moments ("Peak dance move", "wave crashes directly into camera")
- Understands energy context ("most intense, action-packed, viral-worthy")
- Provides reasoning for each selection
- Handles edge cases (clips shorter than 2 seconds)

### Where Gemini Excels

1. **Concrete visual analysis** - Recognizes objects, settings, camera work
2. **Temporal structure extraction** - Identifies cuts, pacing, rhythm
3. **Energy classification** - Accurately categorizes High/Medium/Low
4. **Content description** - Detailed, accurate descriptions of what's happening

### Where Gemini Struggles

1. **Abstract semantic matching** - Vibes like "Social", "Candid", "Summer" are harder to match
2. **Consistency** - Sometimes provides reasoning, sometimes doesn't (ref3 segments lack reasoning field)
3. **Edge cases** - Very short clips (< 2s) or clips with minimal variation

### System's Use of Gemini Intelligence

**Reference Analysis:**
- Gemini extracts temporal structure (when cuts happen)
- Gemini classifies energy/motion/vibe for each segment
- System uses this to create a "blueprint" for matching

**Clip Analysis:**
- Gemini pre-analyzes all clips upfront (one call per clip)
- Gemini identifies best moments for each energy level
- Gemini extracts semantic vibes and content description
- System uses this metadata for deterministic matching

**Key Insight:** Gemini provides the INTELLIGENCE (understanding what's in videos). The system provides the LOGIC (how to match clips to segments). This hybrid approach is faster, cheaper, and more reliable than having Gemini do the matching directly.
