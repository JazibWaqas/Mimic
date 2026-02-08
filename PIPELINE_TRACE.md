# PIPELINE_TRACE.md
## Complete Data Flow Analysis: Clip Ingestion to Vault Report Generation

### Overview
This document traces the complete flow of intelligence through the MIMIC system, documenting what data is known, what is passed forward, what is discarded, and where information is irreversibly lost.

---

## Stage 1: Pre-Analysis (Processors)
**Files:** `backend/engine/processors.py`
**Functions:** `detect_scene_changes()`, `detect_bpm()`, `standardize_clip()`

### Inputs Received
- Reference video file path
- Clip file paths (original user uploads)
- Audio source (reference or dedicated music file)

### Outputs Produced
- Scene change timestamps (visual cuts)
- BPM detection results
- Standardized MP4 files (vertical format, consistent codec)

### Data Schema
```python
scene_changes: List[float]  # Visual cut timestamps
beat_grid: List[float]     # Beat-aligned timestamps
ref_bpm: float            # Beats per minute
standardized_path: str     # Path to processed clip
```

### Confidence/Uncertainty Signals
- Scene detection threshold: 0.12 (hardcoded)
- BPM confidence: "Observed" vs "Inferred" based on audio availability
- Standardization success/failure flags

### Information Irreversibly Lost
- Original video codecs and container formats
- Original audio quality metadata
- File modification times (replaced by hash-based identity)

---

## Stage 2: Reference Analysis (Brain)
**Files:** `backend/engine/brain.py`
**Functions:** `analyze_reference_video()`

### Inputs Received
- Reference video path
- Scene timestamps from Stage 1
- Audio confidence flag
- API key for Gemini access

### Outputs Produced
- `StyleBlueprint` object with complete editorial DNA
- Segment-by-segment analysis with 40+ fields each

### Data Schema (Key Fields)
```python
StyleBlueprint:
  total_duration: float
  segments: List[Segment]
  text_overlay: str
  narrative_message: str
  editing_style: str
  emotional_intent: str
  arc_description: str
  text_events: List[TextEvent]
  
Segment (per segment):
  id: int
  start/end/duration: float
  energy: EnergyLevel (Low/Medium/High)
  motion: MotionType (Static/Dynamic)
  vibe: str (12 categories: nature, urban, travel, friends, etc.)
  arc_stage: str (Intro, Build-up, Peak, Outro, Main)
  shot_scale: str (Extreme CU, CU, Medium, Wide, Extreme Wide)
  shot_function: str (Establish, Action, Reaction, Detail, Transition, Release, Button)
  expected_hold: str (Short, Normal, Long)
  cut_origin: str (visual, beat)  # Critical for Pacing Authority
  cde: str (Sparse, Moderate, Dense)  # Cut Density Expectation
  # ... 30+ additional fields for editorial intelligence
```

### Confidence/Uncertainty Signals
- Gemini response parsing success/failure
- Schema validation errors
- Audio confidence: "Observed" vs "Inferred"
- Reference cache version hits/misses

### Information Irreversibly Lost
- Raw Gemini response (only parsed structured data saved)
- Alternative interpretations rejected by schema validation
- Audio waveform analysis details
- Visual feature extraction intermediate results

---

## Stage 3: Clip Analysis (Brain)
**Files:** `backend/engine/brain.py`
**Functions:** `analyze_all_clips()`

### Inputs Received
- Clip file paths (original uploads)
- API key for Gemini access

### Outputs Produced
- `ClipIndex` containing `ClipMetadata` for each clip
- Pre-computed best moments for each energy level

### Data Schema
```python
ClipMetadata:
  filename: str
  filepath: str
  duration: float
  energy: EnergyLevel
  motion: MotionType
  intensity: int (1-3)
  primary_subject: List[str]  # People-Group, Place-Nature, etc.
  narrative_utility: List[str]
  emotional_tone: List[str]  # nostalgic, joyful, energetic, etc.
  clip_quality: int (1-5)
  best_for: List[str]
  avoid_for: List[str]
  vibes: List[str]  # Legacy semantic tags
  content_description: str
  best_moments: Dict[str, BestMoment]  # High/Medium/Low
  
BestMoment:
  start: float
  end: float
  moment_role: str  # Establishing, Build, Climax, Transition, Reflection
  stable_moment: bool
  reason: str
```

### Confidence/Uncertainty Signals
- Per-clip analysis success/failure
- Quality score confidence
- Best moment stability assessment

### Information Irreversibly Lost
- Alternative moment candidates within each clip
- Frame-level analysis results
- Audio analysis details for clips
- Visual feature extraction intermediate data

---

## Stage 4: Strategic Planning (Advisor)
**Files:** `backend/engine/gemini_advisor.py`
**Functions:** `get_advisor_suggestions()`

### Inputs Received
- `StyleBlueprint` from Stage 2
- `ClipIndex` from Stage 3
- API key for Gemini access

### Outputs Produced
- `AdvisorHints` with editorial guidance and moment selection plans

### Data Schema
```python
AdvisorHints:
  text_overlay_intent: str  # Highest authority signal
  dominant_narrative: str
  arc_stage_guidance: Dict[str, ArcStageGuidance]
  library_alignment: LibraryAlignment
  editorial_strategy: str
  primary_narrative_subject: NarrativeSubject
  allowed_supporting_subjects: List[NarrativeSubject]
  subject_lock_strength: float
  segment_moment_plans: Dict[str, SegmentMomentPlan]  # v14.0
  
ArcStageGuidance:
  primary_emotional_carrier: str
  supporting_material: str
  intent_diluting_material: str
  reasoning: str
  recommended_clips: List[str]  # 8-12 specific filenames
  required_energy: str

SegmentMomentPlan:
  segment_id: int
  moments: List[MomentCandidate]
  total_duration: float
  is_single_moment: bool
  chaining_reason: str
```

### Confidence/Uncertainty Signals
- JSON parsing success/failure
- Schema validation results
- Cache hit/miss status
- Prompt version compatibility

### Information Irreversibly Lost
- Raw Gemini advisory responses
- Alternative strategic considerations
- Detailed reasoning for rejected clip recommendations
- Moment selection trade-off analysis

---

## Stage 5: Semantic Editing (Editor)
**Files:** `backend/engine/editor.py`, `backend/engine/moment_selector.py`
**Functions:** `match_clips_to_blueprint()`, `build_moment_candidates()`, `select_moment_with_advisor()`

### Inputs Received
- `StyleBlueprint` from Stage 2
- `ClipIndex` from Stage 3
- `AdvisorHints` from Stage 4
- Beat grid from Stage 1
- Edit mode (REFERENCE/PROMPT)

### Outputs Produced
- `EDL` (Edit Decision List) with final clip selections
- Edit reasoning for each decision

### Data Schema
```python
EditDecision:
  segment_id: int
  clip_path: str
  clip_start: float
  clip_end: float
  timeline_start: float
  timeline_end: float
  reasoning: str  # Why this clip was chosen
  vibe_match: bool

EDL:
  decisions: List[EditDecision]
```

### Editor's Internal Knowledge (Not Passed Forward)
- Complete scoring breakdown for all rejected alternatives
- Semantic alignment scores (0-100) for non-selected clips
- Musical alignment calculations
- Narrative continuity assessments
- CDE (Cut Density Expectation) calculations
- Energy eligibility filtering results
- Cooldown and variety system state
- Subject lock enforcement decisions
- Advisor bias application details

### Information Irreversibly Lost
- Complete candidate pool evaluation
- Detailed scoring matrices
- Rejected clip reasoning
- Temporal trade-off analysis
- Alternative moment chains considered

---

## Stage 6: Aesthetic Styling (Stylist)
**Files:** `backend/engine/stylist.py`
**Functions:** `apply_visual_styling()`

### Inputs Received
- Concatenated video path from Editor
- `StyleBlueprint` text overlay and styling data
- Optional `StyleConfig` overrides

### Outputs Produced
- Styled video with text overlays and color grading

### Data Schema
```python
StyleConfig:
  text: TextStyleConfig
  color: ColorConfig
  texture: TextureConfig
```

### Information Irreversibly Lost
- Intermediate rendering steps
- Font fallback decisions
- Color grading adjustment parameters
- Text positioning calculations

---

## Stage 7: Post-Render Reflection (Reflector)
**Files:** `backend/engine/reflector.py`, `backend/engine/vault_compiler.py`
**Functions:** `generate_vault_report()`, `compile_vault_reasoning()`

### Inputs Received
- `StyleBlueprint` from Stage 2
- `EDL` from Stage 5
- `AdvisorHints` from Stage 4
- Placeholder `DirectorCritique`

### Outputs Produced
- `VaultReport` with human-readable intelligence summary

### Data Schema
```python
VaultReport:
  header: str
  advisor: VaultReportSection
  decision_stream: List[VaultDecision]
  friction_log: List[str]
  post_mortem: Dict[str, Any]
  next_steps: List[str]
  technical: List[str]

VaultDecision:
  segment_id: int
  what_i_tried: str
  decision: str
  what_if: str
```

### Information Irreversibly Lost
- Editor's complete decision context
- Detailed scoring rationale
- Alternative moment considerations
- Temporal continuity reasoning
- CDE-based subdivision logic
- Subject lock enforcement details

---

## Critical Data Loss Points

### 1. Editor → Reflector Information Gap
The Editor knows but Reflector never receives:
- Complete scoring breakdown (energy, vibe, semantic, musical scores)
- Rejected alternatives and why they were rejected
- CDE calculations and subdivision decisions
- Subject lock enforcement strength
- Advisor bias application details
- Moment selection trade-offs

### 2. Advisor → Editor Information Compression
Advisor provides but Editor usage is limited:
- Detailed arc stage reasoning compressed to scoring bonuses
- Recommended clips treated as suggestions, not requirements
- Subject lock strength applied as generic bonus
- Library alignment constraints implemented as simple penalties

### 3. Brain → Downstream Schema Filtering
Gemini generates but schema validation discards:
- Alternative interpretations of segments/clips
- Confidence scores for individual attributes
- Detailed reasoning for borderline cases
- Cross-references between related segments

### 4. Cache-Induced Information Loss
Hash-based caching loses:
- Timestamp of analysis (replaced by content hash)
- API model version used
- Prompt version that generated the analysis
- Intermediate processing parameters

---

## Data Flow Summary

```
Reference Video → Brain → Blueprint (40+ fields per segment)
                    ↓
User Clips → Brain → ClipIndex (15+ fields per clip)
                    ↓
Blueprint + ClipIndex → Advisor → Hints (strategic guidance)
                                        ↓ (Major information loss)
Blueprint + ClipIndex + Hints → Editor → EDL (final decisions)
                                                    ↓ (Complete knowledge loss)
Blueprint + EDL + Hints → Reflector → Vault Report (summary)
```

### Key Findings
1. **Massive Information Asymmetry:** Editor's rich decision context (100+ data points per decision) is reduced to EDL (6 fields) before reaching Reflector
2. **Loss of Rationale:** All scoring, trade-offs, and alternative considerations are discarded between Editor and Reflector
3. **Flattened Intelligence:** Multi-dimensional analysis is compressed to linear decisions
4. **No Feedback Loop:** Reflector cannot access the decision context needed to provide meaningful critique

### Root Cause
The system treats `EDL` as the complete intelligence artifact, when it's actually just the execution output. The rich analytical context from the Editor stage is never preserved for downstream reflection.
