# MINIMAL_REFLECTOR_REQUIREMENTS.md

## Factual Dependency List for Truthful Reflector Reasoning

### Overview
This document specifies the minimum set of additional signals required for a Reflector to provide truthful, accurate, and useful post-render analysis. These are not suggestions for improvement—they are factual dependencies required for basic reasoning capability.

---

## Core Principle: Without Context, No Truthful Judgment

The Reflector currently receives only execution outputs (EDL) and high-level summaries. To provide truthful analysis, the Reflector needs access to the decision context that influenced those outputs.

---

## 1. Decision Quality Assessment Requirements

### 1.1 Scoring Transparency
**Dependency:** Complete scoring breakdown for each selected clip
**Why Required:** Without scoring data, Reflector cannot distinguish between:
- Good clip, well-chosen
- Poor clip, best available option
- Good clip, poorly placed

**Minimum Data Schema:**
```json
{
  "segment_id": int,
  "selected_clip": {
    "filename": str,
    "final_score": float,
    "score_breakdown": {
      "energy_match": float,
      "vibe_match": float,
      "narrative_anchor": float,
      "advisor_bonus": float,
      "musical_alignment": float,
      "continuity_score": float,
      "novelty_bonus": float,
      "usage_penalty": float
    }
  }
}
```

### 1.2 Alternative Analysis
**Dependency:** Evaluation of rejected alternatives for each segment
**Why Required:** Without alternative data, Reflector cannot assess:
- Whether chosen clip was actually best option
- What trade-offs were made
- Whether better alternatives existed

**Minimum Data Schema:**
```json
{
  "segment_id": int,
  "rejected_alternatives": [
    {
      "filename": str,
      "final_score": float,
      "rejection_reasons": [str],
      "ranking_position": int
    }
  ]
}
```

### 1.3 Constraint Documentation
**Dependency:** Record of all constraints that influenced decisions
**Why Required:** Without constraint data, Reflector cannot distinguish:
- Material limitations vs system limitations
- Intended compromises vs forced compromises
- Algorithmic constraints vs editorial choices

**Minimum Data Schema:**
```json
{
  "segment_id": int,
  "constraints_applied": [
    {
      "constraint_type": str,  # "energy", "subject", "timing", "diversity"
      "constraint_source": str,  # "blueprint", "advisor", "system"
      "constraint_strength": float,  # 0.0-1.0
      "impact_on_decision": str   # "eliminated", "penalized", "prioritized"
    }
  ]
}
```

---

## 2. System vs Material Distinction Requirements

### 2.1 Algorithmic Limitation Identification
**Dependency:** System's self-assessment of its own limitations
**Why Required:** Without this data, Reflector cannot distinguish:
- Bad algorithm vs bad data
- System constraint vs material constraint
- Design limitation vs content inadequacy

**Minimum Data Schema:**
```json
{
  "system_limitations": [
    {
      "limitation_type": str,    # "scoring_bias", "category_gap", "timing_constraint"
      "affected_segments": [int],
      "description": str,
      "workaround_applied": str
    }
  ]
}
```

### 2.2 Material Quality Assessment
**Dependency:** Objective assessment of available material quality
**Why Required:** Without material quality data, Reflector cannot determine:
- Whether system made best possible choices
- Whether material limited edit quality
- Whether different material would have worked better

**Minimum Data Schema:**
```json
{
  "material_assessment": {
    "overall_quality": float,     # 0.0-1.0
    "energy_distribution": dict,    # {"High": 0.2, "Medium": 0.5, "Low": 0.3}
    "subject_coverage": dict,       # {"People-Group": 0.1, "Place-Nature": 0.7}
    "vibe_coverage": dict,         # {"celebration": 0.1, "nature": 0.6}
    "critical_gaps": [str]         # ["fire", "macro", "group_interactions"]
  }
}
```

---

## 3. Temporal Intelligence Requirements

### 3.1 Timing Decision Context
**Dependency:** Complete timing and rhythm decision data
**Why Required:** Without timing context, Reflector cannot evaluate:
- Appropriateness of cut durations
- Quality of beat alignment
- Validity of subdivision decisions

**Minimum Data Schema:**
```json
{
  "segment_id": int,
  "timing_decisions": {
    "target_duration": float,
    "actual_duration": float,
    "subdivision_applied": bool,
    "subdivision_reasoning": str,
    "beat_snap_attempts": int,
    "beat_snap_successes": int,
    "human_jitter_applied": float,
    "cde_category": str    # "Sparse", "Moderate", "Dense"
  }
}
```

### 3.2 Musical Intelligence Data
**Dependency:** Musical phrasing and rhythm analysis
**Why Required:** Without musical data, Reflector cannot assess:
- Appropriateness of rhythmic editing
- Quality of musical phrase adherence
- Validity of beat-based decisions

**Minimum Data Schema:**
```json
{
  "musical_context": {
    "tempo": float,
    "phrase_boundaries": [float],
    "beat_confidence": str,    # "Observed", "Inferred"
    "rhythmic_complexity": str,  # "Simple", "Moderate", "Complex"
    "genre_adaptations": [str]
  }
}
```

---

## 4. Narrative Intelligence Requirements

### 4.1 Story Construction Logic
**Dependency:** Record of narrative flow decisions
**Why Required:** Without narrative data, Reflector cannot evaluate:
- Quality of story progression
- Appropriateness of emotional arc
- Effectiveness of subject continuity

**Minimum Data Schema:**
```json
{
  "narrative_decisions": [
    {
      "segment_id": int,
      "story_function": str,        # "setup", "development", "climax", "resolution"
      "emotional_intent": str,      # "anticipation", "excitement", "release"
      "subject_continuity": str,     # "maintained", "introduced", "transitioned"
      "scale_progression": str,      # "wide_to_medium", "medium_to_close"
      "narrative_link": {
        "from_segment": int,
        "link_type": str,          # "causal", "thematic", "contrast"
        "link_strength": float       # 0.0-1.0
      }
    }
  ]
}
```

### 4.2 Subject Lock Enforcement Data
**Dependency:** Complete record of subject locking decisions
**Why Required:** Without subject lock data, Reflector cannot assess:
- Appropriateness of subject enforcement
- Quality of subject consistency
- Validity of subject-based rejections

**Minimum Data Schema:**
```json
{
  "subject_lock_decisions": [
    {
      "segment_id": int,
      "primary_subject_required": str,
      "clip_subject_provided": str,
      "lock_strength_applied": float,    # 0.0-1.0
      "match_result": str,               # "exact", "partial", "mismatch"
      "penalty_applied": float,
      "supporting_subject_allowed": bool
    }
  ]
}
```

---

## 5. Advisor Integration Requirements

### 5.1 Strategic Guidance Implementation
**Dependency:** Record of how Advisor guidance was applied
**Why Required:** Without this data, Reflector cannot evaluate:
- Whether strategic guidance was followed
- Effectiveness of Advisor suggestions
- Quality of strategic vs tactical decisions

**Minimum Data Schema:**
```json
{
  "advisor_implementation": [
    {
      "segment_id": int,
      "guidance_type": str,          # "subject_lock", "energy_override", "vibe_guidance"
      "guidance_followed": bool,
      "deviation_reason": str,
      "guidance_effectiveness": float   # 0.0-1.0
    }
  ]
}
```

### 5.2 Moment Selection Context
**Dependency:** Complete v14.0 contextual moment selection data
**Why Required:** Without moment context, Reflector cannot evaluate:
- Quality of moment-to-segment matching
- Appropriateness of moment chaining
- Validity of Advisor moment selections

**Minimum Data Schema:**
```json
{
  "moment_selection_decisions": [
    {
      "segment_id": int,
      "candidates_considered": int,
      "advisor_selection": {
        "clip_filename": str,
        "moment_start": float,
        "moment_end": float,
        "selection_reasoning": str,
        "confidence": str,           # "High", "Medium", "Low"
        "alternatives_rejected": int
      },
      "editor_execution": {
        "followed_advisor": bool,
        "deviation_reason": str,
        "chaining_applied": bool,
        "chaining_reasoning": str
      }
    }
  ]
}
```

---

## 6. Minimum Viable Dataset

### Absolute Minimum for Basic Truthfulness
For the Reflector to provide any truthful analysis beyond generic summaries, it requires:

1. **Per-Segment Decision Context:**
   - Selected clip score breakdown
   - Top 3 rejected alternatives with scores
   - Primary constraint that forced the decision

2. **Global Material Assessment:**
   - Overall library quality score
   - Critical missing elements
   - Energy/subject/vibe coverage percentages

3. **System Limitation Disclosure:**
   - Any algorithmic constraints applied
   - Known system biases or limitations
   - Workarounds or compensations used

### Enhanced Dataset for Full Truthfulness
For comprehensive truthful analysis, add:

4. **Complete Alternative Analysis:**
   - All evaluated candidates with full scoring
   - Rejection reasoning for each non-selected option

5. **Temporal Intelligence:**
   - Beat alignment quality metrics
   - Subdivision decision context
   - Musical phrase adherence

6. **Narrative Flow Assessment:**
   - Story progression decisions
   - Emotional arc tracking
   - Subject continuity evaluation

---

## 7. Implementation Priority

### Phase 1: Critical Foundation (Must Have)
1. **Scoring Transparency** - Without this, all judgment is speculation
2. **Alternative Analysis** - Without this, trade-off analysis is impossible
3. **Material Assessment** - Without this, system vs material cannot be distinguished

### Phase 2: Enhanced Capability (Should Have)
4. **Constraint Documentation** - Enables system vs material distinction
5. **Temporal Intelligence** - Enables rhythm and pacing assessment
6. **Narrative Intelligence** - Enables story construction evaluation

### Phase 3: Complete Context (Nice to Have)
7. **Advisor Integration** - Enables strategic assessment
8. **Moment Selection Context** - Enables v14.0 feature evaluation

---

## 8. Success Criteria

### With Phase 1 Data:
- Reflector can distinguish good vs bad decisions
- Reflector can identify material vs system limitations
- Reflector can provide specific, actionable feedback

### With Phase 2 Data:
- Reflector can evaluate timing and rhythm quality
- Reflector can assess narrative construction
- Reflector can provide nuanced trade-off analysis

### With Phase 3 Data:
- Reflector can evaluate strategic intelligence
- Reflector can assess all system features
- Reflector can provide comprehensive improvement guidance

---

## 9. Root Dependency: Context Preservation

The fundamental requirement is **context preservation**. The Reflector needs access to the same decision context that the Editor used. This is not a design preference—it is a factual dependency for truthful reasoning.

**Without context preservation, the Reflector cannot:**
- Make truthful quality assessments
- Distinguish between types of failures
- Provide specific, actionable guidance
- Evaluate system intelligence

**With context preservation, the Reflector can:**
- Provide accurate quality assessments
- Distinguish material vs system limitations
- Offer specific improvement recommendations
- Evaluate system intelligence honestly

---

## Conclusion

These requirements represent the **minimum factual dependencies** for truthful Reflector reasoning. They are not design suggestions or feature requests—they are the essential data needed for the Reflector to fulfill its basic purpose of providing honest, accurate post-render analysis.

The current system provides approximately **5%** of this required data, explaining why the Reflector defaults to generic summaries and library-centric blame patterns.
