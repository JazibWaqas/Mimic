# ADVISOR_FAILURE_ANALYSIS.md

## Evidence-Based Analysis: Why the Advisor Defaults to Blaming the Library

### Executive Summary
The Advisor's consistent pattern of blaming the clip library is not an emergent behavior but a **deterministic outcome** of its architectural design and prompt engineering. This analysis traces the exact logic paths that force this conclusion.

---

## 1. Primary Logic Path: Library Assessment Module

### File Location
`backend/engine/gemini_advisor.py` lines 200-400

### Prompt Engineering Analysis
The Advisor prompt contains three deterministic sections that force library-centric reasoning:

#### Section A: Library Assessment Requirements
```python
# From gemini_advisor_prompt.py (lines 45-65)
"Analyze the user's clip library and identify:
- STRENGTHS: What types of content are well-represented
- GAPS: What types of content are missing or weak
- CONFIDENCE: Overall assessment of library coverage"
```

**Forced Output Structure:**
- `strengths: List[str]` - Must find positive library attributes
- `gaps: List[str]` - Must identify missing content types  
- `confidence: str` - Must rate library adequacy

**Deterministic Outcome:** The prompt **requires** identification of gaps, creating a foundational assumption of library inadequacy.

#### Section B: Creative Audit Requirements
```python
# From gemini_advisor_prompt.py (lines 80-95)
"Compare reference theme against library theme and identify:
- THEMATIC DISSONANCE: Mismatch between reference and library
- CRITICAL NUANCE: Subtle incompatibilities
- THEMATIC ALIGNMENT: Overall compatibility assessment"
```

**Forced Output Structure:**
- `reference_theme: str` - What the reference wants
- `library_theme: str` - What the library has
- `thematic_dissonance: str` - Required description of mismatch

**Deterministic Outcome:** The prompt **mandates** identification of dissonance, ensuring library-blame framing.

#### Section C: Editorial Tradeoffs
```python
# From gemini_advisor_prompt.py (lines 100-120)
"Identify editorial tradeoffs required:
- STRENGTHS: Library advantages to leverage
- EDITORIAL_TRADEOFFS: Compromises due to limitations
- CONSTRAINT_GAPS: Missing content forcing workarounds"
```

**Forced Output Structure:**
- `editorial_tradeoffs: List[str]` - Must list compromises
- `constraint_gaps: List[str]` - Must identify missing elements

**Deterministic Outcome:** The prompt **requires** documentation of limitations and workarounds.

---

## 2. Schema Enforcement: Data Structure Bias

### File Location
`backend/models.py` lines 306-350 (LibraryAlignment, LibraryAssessment classes)

### Structural Analysis
```python
class LibraryAlignment(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    editorial_tradeoffs: List[str] = Field(default_factory=list)  
    constraint_gaps: List[str] = Field(default_factory=list)

class LibraryAssessment(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    confidence: str = Field("Medium")
```

**Architectural Bias:** The data models **only have fields for library limitations**. There are no corresponding fields for:
- System capability limitations
- Algorithm constraint identification
- Process improvement suggestions
- Alternative strategy recommendations

**Deterministic Outcome:** The schema can only express library-centric conclusions.

---

## 3. Causal Chain Analysis

### Input → Processing → Output Flow

#### Step 1: Input Analysis
```python
# Inputs to get_advisor_suggestions()
blueprint: StyleBlueprint  # Reference requirements
clip_index: ClipIndex     # Available material
```

#### Step 2: Prompt Application
```python
# gemini_advisor_prompt.py forces this reasoning pattern:
1. What does the reference want? (Perfect requirements)
2. What does the library have? (Imperfect reality)  
3. What's missing? (Gap identification required)
4. How must we compromise? (Tradeoff documentation required)
```

#### Step 3: Output Generation
```python
# Deterministic output structure:
AdvisorHints:
  library_alignment: LibraryAlignment  # strengths + tradeoffs + gaps
  library_assessment: LibraryAssessment  # strengths + gaps + confidence
  remake_strategy: str  # "Add X, Y, Z to improve library"
```

**Causal Certainty:** The output **must** contain library gaps and tradeoffs because the schema and prompt require them.

---

## 4. Evidence from Code Analysis

### A. Vault Compiler Processing
**File:** `backend/engine/vault_compiler.py` lines 55-85

```python
# Extracts library gaps from advisor output
clean_missing_motifs = []
for gap in advisor.library_alignment.constraint_gaps:
    gap_lower = gap.lower()
    if "fire" in gap_lower: clean_missing_motifs.append("fire")
    elif "eyes" in gap_lower: clean_missing_motifs.append("human_detail")
    # ... more gap processing

library_health = {
    "status_tags": status_tags,
    "missing_motifs": clean_missing_motifs,
    "bottlenecks": ["scarcity_medium_energy", "missing_payoff_shots"]
}
```

**Evidence:** The system **explicitly extracts and processes** library gaps as the primary explanatory factor.

### B. Reflector Prompt Engineering  
**File:** `backend/engine/reflector.py` lines 15-100

```python
# Reflector prompt receives library health as primary causality input
CONTEXT PROVIDED:
- Reference Blueprint Summary: {blueprint_summary}
- Strategic Context (The Plan): {strategic_context}  # Contains library gaps
- Final Edit Decisions (EDL with reasoning): {edl_summary}

HIERARCHY OF JUDGMENT:
1. NARRATIVE ADHERENCE: Did edit respect text overlay intent?
2. SEMANTIC FLOW: Did vibes match?
3. RHYTHMIC PRECISION: Was beat sync correct?
4. MATERIAL QUALITY: The visual appeal of source clips
```

**Missing Signal:** The Reflector receives **no information about**:
- Editor's decision context
- Scoring breakdown
- Alternative considerations
- System constraints vs material limitations

**Deterministic Outcome:** Without system constraint information, the Reflector **must** attribute issues to material quality.

---

## 5. Deterministic vs Emergent Behavior Analysis

### A. Deterministic Patterns (Forced by Design)

#### 1. Required Gap Identification
- **Prompt Requirement:** Must identify `gaps: List[str]`
- **Schema Requirement:** `LibraryAssessment.gaps` field is mandatory
- **Processing Requirement:** Vault compiler extracts gaps as explanatory factors
- **Result:** Library blame is architecturally guaranteed

#### 2. Required Tradeoff Documentation
- **Prompt Requirement:** Must document `editorial_tradeoffs: List[str]`
- **Schema Requirement:** `LibraryAlignment.editorial_tradeoffs` field is mandatory
- **Processing Requirement:** Tradeoffs become primary explanatory factors
- **Result:** System limitations are framed as library inadequacies

#### 3. Required Confidence Assessment
- **Prompt Requirement:** Must rate `confidence: str`
- **Schema Requirement:** `LibraryAssessment.confidence` field is mandatory
- **Processing Requirement:** Low confidence becomes explanatory factor
- **Result:** Library inadequacy is quantified and emphasized

### B. Emergent Patterns (Not Designed)

#### 1. No System Constraint Identification
- **Missing Schema Fields:** No fields for system limitations
- **Missing Prompt Sections:** No request to identify algorithmic constraints
- **Result:** System cannot blame itself even when appropriate

#### 2. No Alternative Strategy Generation
- **Missing Output Fields:** No fields for process improvements
- **Missing Prompt Instructions:** No request for alternative approaches
- **Result:** Only solution is "better library"

---

## 6. Specific Logic Paths That Force Library Blame

### Path 1: Reference-Heavy Library
```python
# When reference demands rare content (e.g., "fire", "macro", "aerial")
# and library lacks these elements:
if reference_requires_rare_content and library_lacks_rare_content:
    gaps.append("fire scenes")
    gaps.append("macro shots") 
    gaps.append("aerial footage")
    confidence = "Low"
    remake_strategy = "Add fire, macro, and aerial footage to library"
```

**Deterministic Outcome:** Rare content requirements automatically trigger library blame.

### Path 2: Energy Mismatch
```python
# When reference has high energy but library lacks high-energy clips:
if reference.energy == "High" and library.energy_distribution["High"] < 2:
    tradeoffs.append("aggressive pacing forced with medium-energy clips")
    gaps.append("scarcity_high_energy")
    confidence = "Medium"
```

**Deterministic Outcome:** Energy distribution issues automatically trigger library blame.

### Path 3: Subject Matter Dissonance
```python
# When reference requires "People-Group" but library has mostly "Place-Nature":
if reference.subject == "People-Group" and library.subject_distribution["People-Group"] < 3:
    thematic_dissonance = "Reference demands social content, library provides nature content"
    gaps.append("group interactions")
    remake_strategy = "Add more people-focused footage"
```

**Deterministic Outcome:** Subject distribution issues automatically trigger library blame.

---

## 7. Why the Advisor Cannot Distinguish Bad Clips vs Bad Placement

### Missing Discrimination Signals

#### A. Editor Decision Context Unavailable
- **What's Missing:** Editor's scoring for each clip
- **Why It Matters:** Cannot distinguish between:
  - Good clip, poorly placed
  - Bad clip, correctly placed
- **Result:** All placement issues attributed to clip quality

#### B. Alternative Analysis Unavailable  
- **What's Missing:** Rejected clip evaluations
- **Why It Matters:** Cannot distinguish between:
  - Best available option chosen
  - Suboptimal choice due to algorithmic limitation
- **Result:** All suboptimal choices attributed to library limitations

#### C. Constraint Identification Unavailable
- **What's Missing:** System constraint documentation
- **Why It Matters:** Cannot distinguish between:
  - Material limitation (bad clips)
  - System limitation (bad algorithm)
- **Result:** All constraints attributed to material limitations

### Architectural Inability
The Advisor **cannot** distinguish these scenarios because:
1. **No Input:** Editor decision context is not passed to Advisor
2. **No Schema:** Fields for system constraint identification don't exist
3. **No Prompt:** Instructions for system self-analysis are absent
4. **No Processing:** Logic for constraint vs material separation is missing

---

## 8. Conclusion: Architectural Determinism

### The Library Blame Pattern is Guaranteed By:

1. **Prompt Engineering:** All three prompt sections require gap/limitation identification
2. **Schema Design:** Only library-centric fields are available
3. **Processing Logic:** Vault compiler extracts gaps as primary explanatory factors
4. **Missing Alternatives:** No fields or logic for system constraint identification
5. **Feedback Loop Absence:** No mechanism to receive Editor decision context

### The Advisor Cannot Behave Differently Because:
- **Architectural Constraint:** The data models only support library-centric conclusions
- **Prompt Constraint:** The instructions require gap identification
- **Processing Constraint:** The downstream logic expects library limitations
- **Information Constraint:** Critical decision context is never provided

### Root Cause
The Advisor defaults to blaming the library because **the system is architected to only express library-centric explanations**. There is no structural capability for system self-critique or constraint identification.

This is not a bug or emergent behavior—it is a **deterministic outcome of the system design**.
