"""
Data models for MIMIC project.
These are the ONLY valid data structures. Do not create ad-hoc dictionaries.
"""

from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import List

# ============================================================================
# ENUMS (Controlled Vocabularies)
# ============================================================================

class EnergyLevel(str, Enum):
    """
    Energy classification based on visual rhythm (NOT content).
    
    Low: Slow motion, steady shots, minimal cuts (meditation, landscapes)
    Medium: Moderate pacing, some variation (vlogs, interviews)
    High: Rapid cuts, fast motion, intense action (sports, dance trends)
    """
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class MotionType(str, Enum):
    """
    Camera/subject movement classification.
    
    Static: Fixed camera, minimal subject movement
    Dynamic: Panning, zooming, fast subject motion
    """
    STATIC = "Static"
    DYNAMIC = "Dynamic"


# ============================================================================
# REFERENCE VIDEO ANALYSIS
# ============================================================================

class Segment(BaseModel):
    """
    A single time-based segment from the reference video.
    
    Example: {
        "id": 1,
        "start": 0.0,
        "end": 2.3,
        "duration": 2.3,
        "energy": "High",
        "motion": "Dynamic",
        "vibe": "Action",
        "reasoning": "Rapid visual movement detected in reference shots."
    }
    """
    id: int = Field(..., description="Sequential segment number (1, 2, 3...)")
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., gt=0, description="End time in seconds")
    duration: float = Field(..., gt=0, description="Segment length in seconds")
    energy: EnergyLevel
    motion: MotionType
    vibe: str = Field("General", description="The aesthetic/content vibe (e.g. Nature, Urban, Action)")
    reasoning: str = Field("", description="AI's thinking about why this segment has this profile")
    arc_stage: str = Field("Main", description="The role of this segment in the video's story arc (e.g. Intro, Build-up, Peak, Outro)")
    
    @field_validator('end')
    @classmethod
    def end_after_start(cls, v, info):
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError('end must be greater than start')
        return v
    
    @field_validator('duration')
    @classmethod
    def duration_matches(cls, v, info):
        if 'start' in info.data and 'end' in info.data:
            expected = info.data['end'] - info.data['start']
            if abs(v - expected) > 0.01:  # Allow 10ms float precision
                raise ValueError(f'duration must equal end - start')
        return v


class StyleBlueprint(BaseModel):
    """
    Complete analysis of reference video structure.
    This is the "editing DNA" we'll apply to user clips.
    """
    total_duration: float = Field(..., gt=0, description="Total video length in seconds")
    segments: List[Segment] = Field(..., min_length=1, description="Ordered list of segments")
    
    # Professional Editing Metadata
    editing_style: str = Field("General", description="The editing style (e.g. Cinematic, Vlog, Montage, TikTok/Reel)")
    emotional_intent: str = Field("Dynamic", description="The intended mood/emotion (e.g. Nostalgic, Energetic, Peaceful)")
    arc_description: str = Field("", description="Description of the video's structural story arc")
    
    # Enhanced Narrative Analysis (v7.0+)
    text_overlay: str = Field("", description="On-screen text extracted from reference video")
    narrative_message: str = Field("", description="What the edit is trying to communicate in one sentence")
    intent_clarity: str = Field("Implicit", description="How explicit the intent is: Clear, Implicit, or Ambiguous")
    
    # Content Requirements (Intent-Level)
    must_have_content: List[str] = Field(default_factory=list, description="3-5 types of moments this edit fundamentally relies on")
    should_have_content: List[str] = Field(default_factory=list, description="2-3 types of moments that would strengthen the edit")
    avoid_content: List[str] = Field(default_factory=list, description="Content types that would clash with narrative intent")
    
    # Experience Goals (Felt, Not Mechanical)
    pacing_feel: str = Field("", description="How the edit feels rhythmically (e.g., breathable, relentless)")
    visual_balance: str = Field("", description="What the edit emphasizes (e.g., people-centric, place-centric)")
    
    overall_reasoning: str = Field("", description="AI's holistic thinking about this video's structure")
    ideal_material_suggestions: List[str] = Field(default_factory=list, description="Suggestions for the user on what clips would work best")
    
    @field_validator('segments')
    @classmethod
    def validate_segments(cls, v, info):
        if not v:
            raise ValueError('Must have at least one segment')
        
        # Check sequential IDs
        for i, seg in enumerate(v, start=1):
            if seg.id != i:
                raise ValueError(f'Segment IDs must be sequential starting from 1')
        
        # Check continuity (no gaps/overlaps)
        for i in range(len(v) - 1):
            if abs(v[i].end - v[i+1].start) > 0.01:
                raise ValueError(f'Gap/overlap between segments {i+1} and {i+2}')
        
        # Check total duration matches last segment end
        if 'total_duration' in info.data:
            expected = v[-1].end
            if abs(info.data['total_duration'] - expected) > 0.01:
                raise ValueError(f'total_duration must equal last segment end')
        
        return v


# ============================================================================
# USER CLIP ANALYSIS
# ============================================================================

class BestMoment(BaseModel):
    """
    A single best moment within a clip for a specific energy profile.
    
    Example: {
        "start": 8.2,
        "end": 10.5,
        "reason": "Peak action moment with fast motion"
    }
    """
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., gt=0, description="End time in seconds")
    reason: str | None = Field(None, description="Why this moment was selected")
    
    @field_validator('end')
    @classmethod
    def end_after_start(cls, v, info):
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError('end must be greater than start')
        return v


class ClipMetadata(BaseModel):
    """
    Comprehensive analysis result for a single user clip.
    
    Contains overall energy/motion PLUS pre-computed best moments for each
    energy level, enabling instant lookup during segment matching without
    additional API calls.
    
    Example: {
        "filename": "dance_clip.mp4",
        "filepath": "/temp/abc123/clips/dance_clip.mp4",
        "duration": 15.2,
        "energy": "High",
        "motion": "Dynamic",
        "best_moments": {
            "High": {"start": 8.2, "end": 10.5, "reason": "Peak dance move"},
            "Medium": {"start": 4.0, "end": 6.2, "reason": "Moderate movement"},
            "Low": {"start": 0.0, "end": 2.0, "reason": "Calm intro"}
        }
    }
    """
    filename: str
    filepath: str
    duration: float = Field(..., gt=0)
    energy: EnergyLevel
    motion: MotionType
    vibes: List[str] = Field(default_factory=list, description="Aesthetic/Content tags for semantic matching")
    content_description: str | None = Field(None, description="Detailed AI description of what is happening in the clip")
    
    # Pre-computed best moments for each energy level (filled during comprehensive analysis)
    best_moments: dict[str, BestMoment] | None = Field(
        None, 
        description="Best moments keyed by energy level (High/Medium/Low)"
    )
    
    # Legacy fields for backward compatibility (deprecated - use best_moments instead)
    best_moment_start: float | None = Field(None, ge=0, description="DEPRECATED: Use best_moments instead")
    best_moment_end: float | None = Field(None, gt=0, description="DEPRECATED: Use best_moments instead")
    
    def get_best_moment_for_energy(self, energy: EnergyLevel) -> tuple[float, float] | None:
        """
        Get the best moment timestamps for a specific energy level.
        
        Returns:
            Tuple of (start, end) or None if not available
        """
        if self.best_moments and energy.value in self.best_moments:
            moment = self.best_moments[energy.value]
            return (moment.start, moment.end)
        
        # Fallback to legacy fields
        if self.best_moment_start is not None and self.best_moment_end is not None:
            return (self.best_moment_start, self.best_moment_end)
        
        return None
    
    @field_validator('best_moment_end')
    @classmethod
    def validate_best_moment(cls, v, info):
        if v is not None and 'best_moment_start' in info.data:
            start = info.data.get('best_moment_start')
            if start is not None and v <= start:
                raise ValueError('best_moment_end must be greater than best_moment_start')
            if 'duration' in info.data and v > info.data['duration']:
                raise ValueError('best_moment_end cannot exceed clip duration')
        return v


class ClipIndex(BaseModel):
    """Collection of all analyzed user clips."""
    clips: List[ClipMetadata] = Field(..., min_length=1)


# ============================================================================
# EDIT DECISION LIST (EDL)
# ============================================================================

class EditDecision(BaseModel):
    """
    A single edit instruction: "Use clip X from time A to B".
    
    Example: {
        "segment_id": 1,
        "clip_path": "/temp/xyz/clips/dance.mp4",
        "clip_start": 0.0,
        "clip_end": 2.3,
        "timeline_start": 0.0,
        "timeline_end": 2.3
    }
    """
    segment_id: int = Field(..., ge=1)
    clip_path: str
    clip_start: float = Field(..., ge=0, description="Start time in source clip")
    clip_end: float = Field(..., gt=0, description="End time in source clip")
    timeline_start: float = Field(..., ge=0, description="Start time in final video")
    timeline_end: float = Field(..., gt=0, description="End time in final video")
    
    # Matching metadata for Thinking UI
    reasoning: str = Field("", description="Why this clip was chosen for this segment")
    vibe_match: bool = Field(False, description="Did the vibes match?")


class EDL(BaseModel):
    """
    Complete Edit Decision List for video assembly.
    This is the "recipe" for FFmpeg to follow.
    """
    decisions: List[EditDecision]
    
    @field_validator('decisions')
    @classmethod
    def validate_timeline(cls, v):
        if not v:
            raise ValueError('EDL cannot be empty')
        
        # Check timeline continuity
        for i in range(len(v) - 1):
            if abs(v[i].timeline_end - v[i+1].timeline_start) > 0.01:
                raise ValueError(f'Timeline gap/overlap between decisions {i} and {i+1}')
        
        return v


# ============================================================================
# PIPELINE RESULT
# ============================================================================

class PipelineResult(BaseModel):
    """
    Final output from orchestrator.run_mimic_pipeline().
    """
    success: bool
    output_path: str | None = None
    blueprint: StyleBlueprint | None = None
    clip_index: ClipIndex | None = None
    edl: EDL | None = None
    error: str | None = None
    processing_time_seconds: float | None = None

