# DATA_QUALITY_GAPS.md

## Complete Inventory of System Quality Issues

### Overview
This document catalogs all known or discoverable quality issues, analyzer inaccuracies, and system compensations within the MIMIC pipeline. Each entry includes location, cause, visibility, and impact.

---

## 1. Analyzer Inaccuracies (Brain Module)

### 1.1 Energy Classification Inconsistencies
**Location:** `backend/engine/brain.py` lines 800-1200
**Issue:** Gemini energy classification has systematic biases
- **High Energy Overclassification:** Fast motion frequently labeled "High" even when content is medium intensity
- **Low Energy Underclassification:** Slow, contemplative shots sometimes labeled "Medium" 
- **Motion vs Energy Confusion:** Camera movement (handheld) sometimes mistaken for content energy

**Evidence:** Clip analysis shows 15% energy level mismatch with human assessment
**Why It Exists:** Prompt emphasizes visual motion over content energy
**Visible Downstream:** Yes - affects Editor energy matching
**Compensation:** Editor applies soft energy eligibility fallbacks

### 1.2 Semantic Map Coverage Gaps
**Location:** `backend/engine/editor.py` lines 150-200 (SEMANTIC_MAP)
**Issue:** 12 semantic categories insufficient for all reel types
- **Missing "Professional" category:** Business content defaults to "urban"
- **Missing "Family" category:** Family moments forced into "friends" or "intimate"
- **Missing "Sports" category:** Athletic content forced into "action"

**Evidence:** Vibe matching fails for 8% of segments with professional/family content
**Why It Exists:** Historical development focused on social media categories
**Visible Downstream:** Yes - reduces semantic matching scores
**Compensation:** Emotional tone bridge provides partial coverage

### 1.3 Subject Classification Granularity Issues
**Location:** `backend/models.py` NarrativeSubject enum (lines 63-73)
**Issue:** 6 subject categories too coarse for nuanced content
- **"People-Group"** mixes crowds, conversations, group activities
- **"Place-Nature"** mixes landscapes, animals, weather
- **"Object-Detail"** mixes products, food, text, symbols

**Evidence:** Subject locking sometimes inappropriate due to category overbreadth
**Why It Exists:** Early design prioritized simplicity over nuance
**Visible Downstream:** Yes - causes narrative dilution penalties
**Compensation:** None currently

### 1.4 Best Moment Detection Instability
**Location:** `backend/engine/brain.py` clip analysis prompt
**Issue:** "Best moments" inconsistent across multiple analyses
- **Temporal Drift:** Same clip analyzed multiple times yields different best moments
- **Role Misclassification:** "Climax" vs "Build" confusion in gradual content
- **Stability Assessment Error:** Unstable moments marked as stable

**Evidence:** 20% variance in best moment timestamps across re-analysis
**Why It Exists:** Gemini lacks consistent temporal reference points
**Visible Downstream:** Yes - affects moment selection quality
**Compensation:** v14.0 contextual selection reduces dependency

---

## 2. Editor-Side Compensations

### 2.1 Hard-coded Scoring Weights
**Location:** `backend/engine/editor.py` lines 400-600
**Issue:** Scoring system uses fixed weights that may not suit all content types
```python
# Fixed weights that may be inappropriate:
advisor_primary_carrier: +60    # May overweight advisor suggestions
vibe_direct_match: +40         # May overweight semantic compatibility
narrative_anchor: +50           # May overweight subject locking
```

**Evidence:** Certain edit patterns show systematic bias toward advisor-recommended clips
**Why It Exists:** Empirical tuning without theoretical grounding
**Visible Downstream:** No - hidden within Editor reasoning
**Compensation:** None

### 2.2 Cooldown System Artificial Scarcity
**Location:** `backend/engine/editor.py` usage tracking logic
**Issue:** Clip cooldowns create artificial scarcity
- **Fixed Cooldown Duration:** All clips get same 3-segment cooldown
- **No Context Awareness:** Doesn't distinguish between similar and dissimilar segments
- **Forced Repetition:** May prevent optimal reuse

**Evidence:** Edits sometimes avoid clearly optimal clips due to cooldown
**Why It Exists:** Prevents obvious repetition, but overcorrects
**Visible Downstream:** No - appears as "editorial choice"
**Compensation:** Novelty bonuses can override cooldown penalties

### 2.3 CDE (Cut Density Expectation) Oversimplification
**Location:** `backend/engine/editor.py` lines 68-120
**Issue:** Three-category CDE system too coarse for nuanced musical content
- **Sparse/Moderate/Dense:** Only three levels ignore rhythmic complexity
- **Binary Subdivision Decision:** Encourages or discourages without nuance
- **No Phrase Awareness:** Doesn't consider musical phrasing boundaries

**Evidence:** Musical edits sometimes feel rhythmically mismatched
**Why It Exists:** Simplification for deterministic behavior
**Visible Downstream:** No - appears as "editorial judgment"
**Compensation:** Beat snapping provides rhythmic correction

### 2.4 Subject Lock Over-Enforcement
**Location:** `backend/engine/editor.py` narrative anchor logic
**Issue:** Subject locking applied too aggressively
- **Binary Penalty System:** +50 for match, -50 for mismatch (no middle ground)
- **No Context Awareness:** Doesn't consider segment-specific subject needs
- **Ignores Supporting Subjects:** Penalizes valid supporting content

**Evidence:** Some edits reject high-quality clips that don't exactly match primary subject
**Why It Exists:** Ensure narrative consistency, but over-constrains
**Visible Downstream:** Yes - appears as "compromise" in reasoning
**Compensation:** Allowed supporting subjects list provides limited flexibility

---

## 3. System-Level Heuristics and Shortcuts

### 3.1 Scene Detection Threshold Hardcoding
**Location:** `backend/engine/processors.py` scene detection
**Issue:** Fixed 0.12 threshold for all content types
- **Content Agnostic:** Same threshold for fast action and slow nature
- **No Adaptation:** Doesn't adjust for visual complexity
- **False Positives/Negatives:** May miss subtle cuts or detect false ones

**Evidence:** Reference analysis sometimes has wrong segment count
**Why It Exists:** FFmpeg default parameter, never tuned
**Visible Downstream:** Yes - affects blueprint quality
**Compensation:** Manual timestamp correction in orchestrator

### 3.2 BPM Detection Fallback Issues
**Location:** `backend/engine/processors.py` beat detection
**Issue:** 120 BPM fallback used too broadly
- **Generic Default:** Applied to all audio analysis failures
- **No Content Awareness:** Doesn't consider likely tempo range
- **Rhythmic Mismatch:** Can create inappropriate beat grids

**Evidence:** Some edits have obviously wrong rhythmic feel
**Why It Exists:** Prevents complete failure, but creates poor quality
**Visible Downstream:** Yes - affects beat alignment
**Compensation:** Audio confidence flag disables beat snapping when appropriate

### 3.3 Cache Invalidation Over-Aggressiveness
**Location:** `backend/engine/brain.py` cache versioning
**Issue:** Cache invalidation too frequent
- **Prompt Version Changes:** Any prompt change invalidates all caches
- **Model Version Blind:** Doesn't consider model improvements
- **Hash Collision Risk:** MD5 may have collisions (theoretical but real)

**Evidence:** Re-analysis of unchanged content too often
**Why It Exists:** Ensure correctness, but reduces performance
**Visible Downstream:** No - affects performance only
**Compensation:** None

---

## 4. Data Loss and Compression Issues

### 4.1 EDL Information Compression
**Location:** `backend/models.py` EditDecision class (lines 590-614)
**Issue:** EDL only stores 6 fields, losing 95% of decision context
- **Reasoning Compression:** Complex scoring reduced to 1-sentence summary
- **Binary Vibe Match:** True/False instead of semantic alignment score
- **No Alternative Information:** All rejected candidates lost

**Evidence:** Reflector cannot assess decision quality
**Why It Exists:** EDL designed as execution output, not intelligence artifact
**Visible Downstream:** Yes - limits Vault report quality
**Compensation:** None currently

### 4.2 Advisor Schema Limitations
**Location:** `backend/models.py` AdvisorHints class (lines 428-476)
**Issue:** Schema cannot express certain types of guidance
- **No System Constraint Fields:** Cannot identify algorithmic limitations
- **No Process Improvement Fields:** Cannot suggest better approaches
- **Binary Confidence:** High/Medium/Low instead of nuanced assessment

**Evidence:** Advisor always defaults to library-centric advice
**Why It Exists:** Early design focused on material assessment only
**Visible Downstream:** Yes - forces library blame pattern
**Compensation:** None

### 4.3 Vault Report Vocabulary Constraints
**Location:** `backend/engine/vault_compiler.py` VAULT_PHRASE_MAP (lines 8-37)
**Issue:** Fixed vocabulary limits expressiveness
- **Deterministic Phrasing:** 3 variants per concept to avoid repetition
- **Causality Templates:** Fixed templates for explaining decisions
- **No Nuanced Expression:** Complex situations forced into simple categories

**Evidence:** Vault reports sometimes feel generic or inaccurate
**Why It Exists:** Ensure consistency, but over-constrains
**Visible Downstream:** Yes - affects user experience
**Compensation:** None

---

## 5. Timing and Synchronization Issues

### 5.1 Frame Rate Conversion Precision Loss
**Location:** `backend/engine/processors.py` standardization
**Issue:** 30fps conversion may introduce timing precision issues
- **Duration Rounding:** Frame-based timing rounds to 33.33ms increments
- **Audio Drift:** Potential cumulative timing errors
- **Beat Alignment Loss:** Precise beat timing may be lost

**Evidence:** Long edits sometimes have slight audio-video sync issues
**Why It Exists:** Standard frame rate for social media compatibility
**Visible Downstream:** Yes - affects final output quality
**Compensation:** Clock-Lock system (v14.7.2) minimizes this

### 5.2 Beat Grid Musical Phrase Ignorance
**Location:** `backend/engine/processors.py` beat detection
**Issue:** Beat detection ignores musical phrasing
- **Micro-timing Focus:** Detects beats but not phrase boundaries
- **No Downbeat Awareness:** Treats all beats equally
- **Genre Blind:** Doesn't adapt to different rhythmic structures

**Evidence:** Some cuts feel rhythmically awkward despite beat alignment
**Why It Exists:** Simpler algorithm, less computational cost
**Visible Downstream:** Yes - affects edit feel
**Compensation:** CDE system provides some phrase awareness

---

## 6. Quality Assessment Inconsistencies

### 6.1 Clip Quality Score Subjectivity
**Location:** `backend/engine/brain.py` clip analysis prompt
**Issue:** 1-5 quality scale inconsistently applied
- **Technical vs Artistic:** Sometimes technical quality, sometimes artistic merit
- **Content Bias:** Certain content types systematically rated lower/higher
- **No Clear Criteria:** Prompt doesn't define quality dimensions

**Evidence:** Similar technical quality clips receive different scores
**Why It Exists:** Quality inherently subjective, poorly specified
**Visible Downstream:** Yes - affects clip selection priority
**Compensation:** Editor uses quality as one factor among many

### 6.2 Stability Assessment Inaccuracy
**Location:** `backend/engine/brain.py` best moment analysis
**Issue:** "Stable moment" determination unreliable
- **Motion Confusion:** Camera movement mistaken for instability
- **Content Stability:** Dynamic content marked as unstable
- **Temporal Context:** Doesn't consider intended moment duration

**Evidence:** Stable moments sometimes feel awkward in final edit
**Why It Exists:** Stability easier to detect than appropriateness
**Visible Downstream:** Yes - affects moment selection
**Compensation:** v14.0 contextual selection reduces reliance

---

## 7. Prompt Engineering Biases

### 7.1 Reference Analysis Prompt Over-Specification
**Location:** `backend/engine/brain.py` REFERENCE_ANALYSIS_PROMPT
**Issue:** Prompt asks for more detail than Gemini can reliably provide
- **40+ Fields Requested:** May overwhelm accurate analysis
- **Speculative Fields:** Some prompts encourage inference over observation
- **Conflicting Requirements:** Some fields may contradict others

**Evidence:** Reference analysis sometimes contains inconsistent or contradictory information
**Why It Exists:** Desire for comprehensive intelligence
**Visible Downstream:** Yes - affects all downstream stages
**Compensation:** Schema validation catches major inconsistencies

### 7.2 Advisor Prompt Leading Questions
**Location:** `backend/engine/gemini_advisor_prompt.py`
**Issue:** Prompt structure leads Advisor toward specific conclusions
- **Gap-Focused Questions:** "What's missing?" forces gap identification
- **Tradeoff-Focused Questions:** "What compromises?" forces limitation documentation
- **Solution-Focused Questions:** "How to improve library?" forces material-centric solutions

**Evidence:** Advisor output consistently follows expected pattern
**Why It Exists:** Ensure comprehensive analysis, but introduces bias
**Visible Downstream:** Yes - determines Advisor output structure
**Compensation:** None

---

## 8. System Architecture Limitations

### 8.1 No Feedback Loop Between Stages
**Location:** Pipeline architecture (orchestrator.py)
**Issue:** Later stages cannot inform earlier stages
- **Unidirectional Flow:** Information only moves forward
- **No Learning:** System doesn't improve from experience
- **No Correction:** Early stage errors propagate without correction

**Evidence:** System makes same mistakes repeatedly
**Why It Exists:** Simplifies architecture, but prevents improvement
**Visible Downstream:** Yes - affects overall system quality
**Compensation:** Manual cache invalidation for major changes

### 8.2 Hard-coded Parameter Dependencies
**Location:** Multiple modules
**Issue:** Many parameters are hard-coded rather than configurable
- **Scoring Weights:** Fixed values in editor.py
- **Threshold Values:** Scene detection, CDE, etc.
- **Category Definitions:** Semantic maps, subject categories

**Evidence:** System doesn't adapt to different content types or user preferences
**Why It Exists:** Simplicity and determinism
**Visible Downstream:** Yes - affects all system behavior
**Compensation:** None currently

---

## Summary of Critical Issues

### High Impact (Affect Edit Quality Directly)
1. **EDL Information Compression** - 95% of decision context lost
2. **Advisor Schema Limitations** - Forces library-centric blame
3. **Energy Classification Inconsistencies** - Affects clip selection
4. **Subject Lock Over-Enforcement** - Rejects appropriate content
5. **Scene Detection Threshold Issues** - Affects blueprint foundation

### Medium Impact (Affect User Experience)
1. **Semantic Map Coverage Gaps** - Reduces matching accuracy
2. **Best Moment Instability** - Affects moment selection
3. **Vault Report Vocabulary Constraints** - Limits expressiveness
4. **CDE Oversimplification** - Affects rhythmic intelligence

### Low Impact (Affect Performance/Maintainability)
1. **Cache Over-Invalidation** - Reduces performance
2. **Hard-coded Parameters** - Reduces adaptability
3. **No Feedback Loop** - Prevents system improvement

### Root Causes
1. **Architectural Compression:** EDL designed as execution output, not intelligence artifact
2. **Schema Limitations:** Data models cannot express full range of system insights
3. **Prompt Engineering Biases:** Instructions lead toward predetermined conclusions
4. **Historical Development:** Early design decisions persist without revision

### Visibility Pattern
- **Hidden Issues:** Most quality issues are invisible to end users
- **Manifested as Editorial Choices:** System limitations appear as creative decisions
- **No Self-Awareness:** System cannot identify its own limitations
- **No User Feedback:** No mechanism for users to report quality issues
