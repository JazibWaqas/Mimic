# MIMIC: Gemini 3 Hackathon Execution Plan

Last Updated: January 27, 2026
Deadline: February 10, 2026 (14 days remaining)
Target: Top 10 guaranteed, Top 3 stretch goal

## 1. HACKATHON CONTEXT

### Competition Overview

Event: Gemini 3 Global Hackathon by Google DeepMind
Participants: 100,000+ registered competitors, 3 months to build
Prize Pool: $100,000 total
Grand Prize: $50,000
Second Place: $20,000
Third Place: $10,000
Honorable Mentions: $2,000 × 10 winners

### Submission Requirements

- 3-minute demo video (hard limit - judges will not watch beyond 3 minutes)
- Public code repository (GitHub with clear README)
- ~200 word Gemini integration description (explaining how Gemini 3 is central)
- Working demo (local deployment acceptable, cloud optional)

### Judging Criteria (Exact Weights)

- Technical Execution (40%): Code quality, Gemini 3 leverage, functionality, architectural soundness
- Innovation/Wow Factor (30%): Novel approach, unique solution, addresses significant problem creatively
- Potential Impact (20%): Real-world utility, broad market appeal, problem significance
- Presentation/Demo (10%): Clear problem definition, effective presentation, quality documentation

### What Google Explicitly Wants

Direct quotes from hackathon guidelines:
"Gemini 3 isn't just a chatbot—it's a multimodal reasoning engine. Don't just build a text interface; build something that senses and reacts."
"In the Action Era, if a single prompt can solve it, it is not an application. We are looking for orchestrators building robust systems."
Strategic tracks they're promoting:

- 🧠 Marathon Agent: Autonomous systems for multi-hour tasks with self-correction
- ☯️ Vibe Engineering: Agents that write AND verify code through testing loops
- 👨‍🏫 Real-Time Teacher: Live multimodal learning with Gemini Live API
- 🎨 Creative Autopilot: High-precision multimodal creation with reasoning

Key technical expectations:

- Spatial-temporal video understanding (not just object recognition)
- Multi-step orchestration (not single-prompt solutions)
- Planning → execution → reflection workflows
- Visible intelligence (white-box, not black-box systems)

### What Google Explicitly DOESN'T Want

Anti-patterns that will hurt scoring:
❌ Baseline RAG: Simple data retrieval (Gemini 3 has 1M context natively)
❌ Prompt-only wrappers: System prompts in basic UI with no orchestration
❌ Simple vision analyzers: Basic object identification (obsolete capability)
❌ Generic chatbots: Nutrition bots, job screeners, personality analyzers
❌ Medical advice generators: Diagnostic or mental health advice tools
### Past Winner Analysis (What Actually Works)

2024-2025 Winners Pattern Recognition:

**ViddyScribe (Best Web):** Video accessibility for blind users

Why it won: Deep social impact + multimodal reasoning + clear utility
Lesson: Accessibility angles resonate strongly with judges

**Outdraw AI (Most Creative - $50k equivalent):** Human vs AI drawing game

Why it won: Fun, creative, novel interaction model - NO social impact needed
Lesson: Pure creativity and wow factor can win without social good

**Gaze Link (Best Android):** Eye-tracking communication for ALS patients

Why it won: Profound impact + sophisticated multimodal integration
Lesson: Medical utility (not advice) scores highly

**SurgAgent (ODSC 1st Place):** Multi-agent medical diagnosis with explainable reasoning

Why it won: Complex orchestration + transparency + clear reasoning chains
Lesson: Visible intelligence and multi-step workflows impress judges

Key takeaways:

- Social impact dominated BUT creative tools (Outdraw AI) can win on novelty alone
- Deep Gemini integration matters more than feature count
- Polish and clear demos beat feature-heavy prototypes
- Explainability and visible reasoning are highly valued

### Current Reality Check

Time constraints:

- Available: ~3-4 hours/day for 14 days = 42-56 hours total
- Already invested: 17 days building core system (proof of execution velocity)

Competitive landscape:

- Advantages: Working end-to-end system, ability to ship fast, novel technical insight
- Disadvantages: Late start (2 weeks vs 3 months), competing against top engineers worldwide

Risk assessment:

- Current system as-is: 60/100 → Top 30-40% (competent but forgettable)
- With planned enhancements: 75-85/100 → Top 10-15% (strong honorable mention candidate)
- With perfect execution + demo: 85-90/100 → Top 3 possible (requires flawless polish)

## 2. PROJECT DEFINITION

### What MIMIC Actually Is

One-sentence definition:
A video editing system that uses Gemini 3's spatial-temporal reasoning to extract the editing structure (cut timing, pacing, energy flow, narrative arc) from any reference video and applies that structure to user-provided clips, creating a new video with the same rhythm but entirely different content.

Core technical insight:

Structure ≠ Content. You can transfer WHEN cuts happen without caring WHAT the content is. This enables "editing by example" - steal the rhythm from any viral video and apply it to your own footage.

### What It Is NOT (Critical Distinctions)
❌ NOT a template system: Doesn't use pre-made editing templates or presets
❌ NOT content matching: Doesn't try to find similar visual content or recreate scenes
❌ NOT auto-editing: Doesn't make creative decisions from scratch - it mimics existing decisions
❌ NOT a general editor: Not trying to compete with Premiere/CapCut on features
❌ NOT agentic yet: Currently deterministic pipeline (but we'll add reflection loops)
### Current System Architecture (What Already Works)

The 5-Stage Pipeline:
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: INPUT VALIDATION                                   │
├─────────────────────────────────────────────────────────────┤
│ • Reference video: 3-60 seconds (hard limits)               │
│ • Clip library: Minimum 2 clips (practical: 20-60 clips)   │
│ • File format validation (MP4, MOV, AVI supported)          │
│ • Duration checks, corruption detection                     │
│ • Temp directory setup                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: REFERENCE ANALYSIS (Gemini + FFmpeg + librosa)    │
├─────────────────────────────────────────────────────────────┤
│ • FFmpeg: Detect scene cuts (visual discontinuities)        │
│ • librosa: Detect BPM from audio track (beat detection)     │
│ • Gemini 3 Flash: Analyze reference video → StyleBlueprint  │
│                                                              │
│   Gemini extracts:                                          │
│   ✓ Segments: 15-40 cut-to-cut segments with timestamps    │
│   ✓ Energy per segment: High/Medium/Low                    │
│   ✓ Motion per segment: Dynamic/Static                     │
│   ✓ Vibe per segment: Nature/Urban/Friends/Travel/etc      │
│   ✓ Arc stage: Intro/Build-up/Peak/Outro                   │
│   ✓ Editing style: "Cinematic Montage" / "Vlog" / etc      │
│   ✓ Emotional intent: "Nostalgic" / "Energetic" / etc      │
│   ✓ Overall reasoning: Why this structure works            │
│   ✓ Material suggestions: What clips would improve this    │
│                                                              │
│ • Cache result: JSON file with hash-based key               │
│   (Persistent cache - never re-analyze same reference)      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: CLIP ANALYSIS & STANDARDIZATION (Gemini + FFmpeg) │
├─────────────────────────────────────────────────────────────┤
│ For EACH clip in library:                                   │
│                                                              │
│ • Check comprehensive analysis cache (hash-based)           │
│ • If cache miss:                                            │
│   → Gemini 3 Flash analyzes clip:                           │
│     ✓ Overall energy: High/Medium/Low                       │
│     ✓ Overall motion: Dynamic/Static                        │
│     ✓ Vibes: 2-4 semantic tags (Nature, Urban, etc)        │
│     ✓ Content description: 1-sentence summary              │
│     ✓ Best moments: Pre-computed windows for each energy:  │
│       • High energy moment: timestamps + reason            │
│       • Medium energy moment: timestamps + reason          │
│       • Low energy moment: timestamps + reason             │
│                                                              │
│ • Check standardization cache (separate cache)             │
│ • If cache miss:                                            │
│   → FFmpeg standardizes clip:                               │
│     ✓ Resolution: 1080x1920 (vertical format)              │
│     ✓ Frame rate: 30fps                                     │
│     ✓ Codec: H.264                                          │
│     ✓ Cache standardized file                               │
│                                                              │
│ • Result: ClipIndex with all metadata + standardized files │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: INTELLIGENT MATCHING (Deterministic Algorithm)    │
├─────────────────────────────────────────────────────────────┤
│ For EACH segment in reference blueprint:                    │
│                                                              │
│ 1. ELIGIBILITY FILTERING (Energy gating):                   │
│    • High segments → accept High + Medium clips only        │
│    • Low segments → accept Low + Medium clips only          │
│    • Medium segments → accept any energy level              │
│                                                              │
│ 2. MULTI-FACTOR SCORING (each eligible clip):               │
│    • Discovery bonus: +50 (unused clips)                    │
│    • Reuse penalty: -20 per previous use                    │
│    • Direct vibe match: +30                                 │
│    • Semantic neighbor match: +15 (e.g., "urban"→"city")   │
│    • Lighting match: +10 (night/day consistency)           │
│    • Motion continuity: +5 (flow preservation)             │
│    • Energy exact match: +15                                │
│    • Energy adjacent: -5 (compromise penalty)              │
│    • Temporal cooldown: -100 (if used <5s ago on timeline) │
│                                                              │
│ 3. SELECTION:                                                │
│    • Top-tier: All clips within 5 points of max score       │
│    • Random shuffle among top-tier (introduces variety)     │
│    • Select winner                                           │
│                                                              │
│ 4. EXTRACTION:                                               │
│    • Use pre-computed best moment (if available)            │
│    • Otherwise: sequential extraction from clip             │
│    • Extract exact duration needed for segment              │
│                                                              │
│ 5. BEAT SYNCHRONIZATION:                                     │
│    • Generate beat grid from BPM (reference audio)          │
│    • Align cut endpoints to nearest beat (±150ms tolerance) │
│    • Subdivide long segments (>3s) into rapid cuts:         │
│      - Peak stage: 1-beat cuts                              │
│      - Build-up: 1-2 beat cuts                              │
│      - Intro/Outro: 2-4 beat cuts                           │
│                                                              │
│ 6. TRACKING:                                                 │
│    • Update clip usage counts                                │
│    • Track timeline position for cooldown                    │
│    • Record compromises (energy mismatches)                 │
│    • Enforce diversity (prevent same clip back-to-back)     │
│                                                              │
│ • Result: EDL (Edit Decision List) - frame-accurate         │
│   instructions for each segment                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: RENDERING (FFmpeg)                                 │
├─────────────────────────────────────────────────────────────┤
│ • Extract each segment from source clips (frame-accurate)   │
│ • Concatenate all segments in timeline order                │
│ • Merge reference audio track (preserve rhythm)             │
│ • Validate timeline continuity:                              │
│   - Check for gaps (error if gap >50ms)                     │
│   - Check for overlaps (error if detected)                  │
│   - Verify total duration matches reference (±0.5s)         │
│ • Output: Final MP4                                          │
│   - Format: 1080x1920, 30fps, H.264 video, AAC audio       │
│   - Location: /mnt/user-data/outputs/{session_id}.mp4      │
└─────────────────────────────────────────────────────────────┘

Processing time benchmarks:

- Cached (all analysis complete): 15-20 seconds
- Partial cache (new reference): 60-90 seconds
- Full uncached (reference + 55 clips): 450-650 seconds (~10 minutes)

Demo strategy: MUST pre-cache everything for live presentation

What's cached (persistent across runs):

- ✅ Gemini reference analysis (JSON, hash-based key)
- ✅ Gemini clip analysis (JSON per clip, hash-based key)
- ✅ Standardized video files (MP4, hash + size + mtime key)
- ❌ NOT cached: EDL decisions (recomputed each synthesis)
- ❌ NOT cached: Final output videos

### Performance Reality (Real Data from Testing)

Best case - ref4.mp4:
- 30 segments, 55 clips in library
- Vibe match: 100% (30/30 perfect semantic matches)
- Diversity: 100% (30 unique clips used, zero repeats)
- Energy compromises: 2 (6.7% - used Medium for High segments)
- Processing: 18.9 seconds (fully cached)
- Output quality: Excellent - smooth flow, beat-aligned cuts

Average case - ref5.mp4:

- 21 segments, 55 clips in library
- Vibe match: 96.2% (25/26 matches)
- Diversity: 100% (21 unique clips, zero repeats)
- Energy compromises: 6 (23.1% - more challenging energy distribution)
- Processing: 19.7 seconds (fully cached)
- Output quality: Very good - minor compromises barely noticeable

Worst case - ref3.mp4:

- 15 segments, 55 clips in library
- Vibe match: 53.3% (8/15 matches - significant vibe gap)
- Diversity: 100% (15 unique clips, zero repeats)
- Energy compromises: 1 (6.7% - good energy alignment)
- Processing: 64.2 seconds (cache miss on reference)
- Output quality: Acceptable - system degraded gracefully

Root cause analysis for worst case:

Reference used abstract, specific vibes ("Celebration", "Social", "Summer", "Golden Hour", "Nostalgic") that didn't map well to the generic clip library vibes ("Nature", "Travel", "Friends", "Urban"). System couldn't find exact matches but still produced coherent output using semantic neighbors.

Key insight:

System performs best (90-100% vibe match) when reference vibes align with clip library contents. Even in worst-case mismatches, system always produces output and degrades quality gracefully rather than failing. This robustness is a strength for demo.

### The Current Problem: Gemini Looks Like "Just Classification"

What Gemini currently does:

- Analyzes reference video → extracts segments with energy/motion/vibe/arc
- Analyzes each clip → extracts energy/motion/vibes/best_moments
- Returns structured data (JSON)

What Gemini does NOT do:

- Make matching decisions (your algorithm does this)
- Reason about narrative flow (your algorithm scores clips)
- Plan the overall edit strategy (deterministic selection)
- Reflect on output quality (no feedback loop)

Why this is a problem for judges:

Judge's question: "Why does this need Gemini 3?"
Current answer: "For video classification and metadata extraction"
Judge's reaction: ❌ "That's just using Gemini as a labeling tool. The smart part is your deterministic algorithm, not the AI."

What judges expect to see:

- Gemini planning (not just analyzing)
- Gemini reasoning about creative decisions (not just classifying)
- Gemini reflecting on its own work (closing the loop)
- Multi-step orchestration where Gemini's intelligence is central to outcomes

The gap we need to close:

Make Gemini's role shift from "data provider" to "creative collaborator" through strategic planning and reflection capabilities.

## 3. STRATEGIC POSITIONING

### Our Core Narrative

Positioning statement:
"MIMIC uses Gemini 3's spatial-temporal reasoning to reverse-engineer viral editing styles, then collaborates with deterministic algorithms to execute edits with musical precision. It's creative intelligence meets computational precision - AI creative direction + engineering execution."

Why this framing works:

- ✅ Emphasizes Gemini's multimodal video understanding (spatial-temporal)
- ✅ Positions Gemini as strategic collaborator (not just classifier)
- ✅ Acknowledges engineering depth without hiding it
- ✅ Fits "Action Era" narrative (plan → execute workflow)
- ✅ Honest about what Gemini does vs what code does

### Primary Angle: Fun, Cool Creative Tool

Why we're NOT going for social impact:

Honest assessment:

- I built this to make my own Instagram edits faster (authentic motivation)
- Core insight (structure transfer) is genuinely novel and interesting on its own merits
- Forcing a social impact angle would feel inauthentic - judges detect this
- Outdraw AI won $50k equivalent with pure "fun drawing game" - no social good required

What we're leaning into:

- ✅ The technical insight is clever (structure ≠ content)
- ✅ The output is visually satisfying (cuts aligned to music)
- ✅ The use case is real (creators actually want this)
- ✅ The demo will be memorable (side-by-side rhythm transfer is obvious)
- ✅ It's FUN - judges are human and enjoy cool toys

Comparison to Outdraw AI strategy:

- They positioned as "creative AI interaction" not "social good"
- Focused on wow factor and novelty
- Clear visual demo (drawing happening in real-time)
- Judges appreciated the creativity angle alone

Our equivalent:

- Position as "creative editing collaboration"
- Focus on structure transfer novelty
- Clear visual demo (rhythm transfer obvious in side-by-side)
- Judges appreciate the technical creativity

### What We're Explicitly NOT Claiming

Be honest about limitations to build credibility:
❌ NOT claiming "agentic" - System is mostly deterministic, not fully autonomous with self-correction (though we'll add reflection for partial credit)
❌ NOT claiming social impact - This is a productivity/creativity tool, not accessibility/education/healthcare
❌ NOT claiming revolutionary - This is a clever application of existing tech, not breakthrough AI research
❌ NOT claiming editor replacement - This is an accelerator for specific use cases, not general editing
❌ NOT claiming perfect quality - Output depends on clip library quality, we'll be honest about limitations
Why honesty matters:

Judges are experienced engineers. Overhyping backfires. Honest, clear positioning builds trust and differentiates from projects making wild claims.

### Target Outcome

Realistic goal hierarchy:

**Minimum viable success: Top 10 (Honorable Mention - $2,000)**

- Probability: 70-80% if we execute plan
- Requirements: Working demo, clear value prop, visible Gemini integration

**Stretch goal: Top 5**

- Probability: 40-50% with excellent execution
- Requirements: Above + memorable demo + technical depth obvious

**Moonshot: Top 3 (Podium - $10k-50k)**

- Probability: 20-30% with perfect execution + luck
- Requirements: Above + wow factor + polish + judges love the concept

What moves us up the ladder:

- Quality over quantity (3 polished features > 10 half-baked)
- Demo clarity (judges "get it" in first 30 seconds)
- Visible intelligence (can see Gemini thinking, not black box)
- Technical credibility (sophisticated engineering obvious)
- Memorable moment (side-by-side comparison is visceral)

### 3.5 SYSTEM ROLES & EXECUTION FLOW (High-Level Architecture)
This section explains how MIMIC works conceptually, independent of implementation details.

#### The Core System Loop

MIMIC operates as a four-phase creative system:

Understand → Plan → Execute → Explain

Each phase has a clearly defined responsibility and owner.

#### Roles in the System

**Gemini 3 — Creative Strategist & Judge**
Gemini is responsible for reasoning, not execution.
Gemini’s roles:
Understanding


Extracts structure, intent, and narrative arc from reference videos


Analyzes clips semantically (vibes, motion, energy, best moments)


Planning


Provides high-level narrative guidance before execution


Suggests which clips best support each arc phase


Judgment


Evaluates multiple completed edits


Selects the execution that best matches the original intent


Reflection


Explains why the chosen edit worked


Identifies compromises and improvement opportunities


Gemini never performs low-level editing decisions.

Deterministic Engine — Precision Executor
The engine is responsible for doing, not reasoning.
Engine responsibilities:
Enforce constraints (energy gating, diversity, cooldowns)


Score clips deterministically


Align cuts to beats with frame accuracy


Generate valid EDLs


Render final video output


The engine guarantees:
Reproducibility


Stability


Predictable behavior



Vault — Glass-Box Explanation Layer
Vault is where intelligence becomes visible.
Vault shows:
What the system understood


What it planned


What it executed


Why one result was chosen


Where compromises occurred


Vault never edits or executes.

User — Observer & Beneficiary
The user:
Provides inputs


Triggers execution


Observes results


Optionally improves results by adding better material


The user is never burdened with creative micro-decisions.

End-to-End Flow (Conceptual)
Reference + Clips
        ↓
Gemini Understanding
        ↓
Gemini Planning (Advisor)
        ↓
Deterministic Execution (Multiple EDLs)
        ↓
Gemini Judgment (Arbiter)
        ↓
Final Render
        ↓
Vault Explanation & Reflection

This flow is fixed and non-negotiable.

Why This Architecture Matters
Avoids prompt-wrapper anti-pattern


Preserves determinism and reliability


Makes Gemini’s intelligence visible and meaningful


Aligns directly with Google’s “Action Era” framing


Scales to more autonomy later without redesign



### 4. What NOT to change (important)
You do not need to:
Rewrite earlier architecture sections


Change the demo script


Add new pages


Reframe positioning


Revisit Advisor scope


This addition completes the system. It doesn’t complicate it.

### 5. Final confirmation (answering your implicit question)
“Is this now a real orchestrated Gemini system and not just prompts?”
Yes. Unequivocally.
You now have:
Gemini understanding inputs


Gemini planning strategy


Gemini judging outcomes


Gemini explaining results


Deterministic execution in between


That is exactly what Google means by:
“orchestrators building robust systems”

4. THE DEMO (This Is What Wins)
The Single Most Important Thing
The "Magic Moment":
 Side-by-side comparison of reference video and generated output playing synchronized, with cuts visibly aligned to beat drops. This instantly proves structure transfer works - same rhythm, different content, undeniable visual evidence.
Why this moment is critical:
Judges can SEE the concept in 5 seconds (no explanation needed)
Visceral satisfaction (cuts hitting beats is emotionally satisfying)
Proves technical depth (frame-accurate alignment is hard)
Shows Gemini's value (extracted structure successfully transferred)
Demo design principle:
 Everything else in the demo exists to set up and amplify this single moment.
3-Minute Demo Script (Exact Timing)
┌─────────────────────────────────────────────────────────────┐
│ 0:00-0:30 | THE HOOK (Establish Problem + Promise)          │
├─────────────────────────────────────────────────────────────┤
│ VISUAL: Frustrated creator struggling in editing software   │
│                                                              │
│ VOICEOVER:                                                   │
│ "Creating viral edits takes hours - finding clips, timing   │
│  cuts to beats, matching energy flow across the edit.       │
│  Professional editors make this look easy. But what if you  │
│  could just... steal their technique?"                       │
│                                                              │
│ VISUAL: Quick cuts showing reference videos (viral edits)   │
│                                                              │
│ TEXT OVERLAY: "What if you could borrow editing DNA?"       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 0:30-1:30 | GEMINI INTELLIGENCE (Show AI Thinking)          │
├─────────────────────────────────────────────────────────────┤
│ VISUAL: MIMIC interface - Studio page                       │
│                                                              │
│ ACTION: Upload reference video (show thumbnail)             │
│ ACTION: Upload source clips (show grid of 20-30 clips)     │
│ ACTION: Click "Execute Synthesis" button                    │
│                                                              │
│ VISUAL: Real-time intelligence stream appears:              │
│                                                              │
│   "🧠 Gemini analyzing reference structure..."              │
│   "✓ Detected 30 segments, BPM 128"                         │
│   "✓ Arc: Intro → Build-up → Peak → Outro"                 │
│   ""                                                         │
│   "🎬 Gemini planning narrative strategy..."                │
│   "✓ Intro: Nature clips to establish calm"                │
│   "   Recommended: clips 28, 33, 30"                        │
│   "✓ Build-up: Travel movement creates momentum"           │
│   "   Recommended: clips 32, 47, 56"                        │
│   "✓ Peak: Friends celebration for emotional climax"       │
│   "   Recommended: clips 37, 26, 6, 22"                     │
│   ""                                                         │
│   "⚙️ Executing with beat synchronization..."               │
│   "✓ Matching clips to segments... 12/30 complete"         │
│   "✓ Aligning cuts to beat grid..."                         │
│   "✓ Rendering output..."                                   │
│                                                              │
│ VOICEOVER:                                                   │
│ "Gemini 3's spatial-temporal reasoning extracts the editing │
│  DNA - when cuts happen, how energy flows, what the arc is. │
│  Then it plans which clips will tell that same story."      │
│                                                              │
│ WHY THIS WORKS:                                              │
│ • Makes Gemini's intelligence VISIBLE (not a black box)    │
│ • Shows multi-step process (plan → execute)                │
│ • Demonstrates "Action Era" orchestration                   │
│ • Fills time while processing happens                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 1:30-2:15 | THE REVEAL (Magic Moment)                       │
├─────────────────────────────────────────────────────────────┤
│ VISUAL: Transition to Vault page - side-by-side view        │
│                                                              │
│ LAYOUT:                                                      │
│   ┌────────────────┬────────────────┐                       │
│   │  REFERENCE     │  YOUR EDIT     │                       │
│   │  (Original)    │  (Generated)   │                       │
│   └────────────────┴────────────────┘                       │
│         [Synced playback controls]                          │
│                                                              │
│ ACTION: Play both videos synchronized                        │
│                                                              │
│ VISUAL EFFECTS:                                              │
│ • Energy graph overlay (High/Medium/Low waves)              │
│ • Beat markers pulse when cuts happen                       │
│ • Cuts visibly aligned between videos                       │
│                                                              │
│ SLOW-MO MOMENT (2-3 seconds):                               │
│ • Zoom into beat alignment                                  │
│ • Show cut happening on EXACT same beat in both videos     │
│ • Resume normal speed                                        │
│                                                              │
│ TEXT OVERLAYS (appear during playback):                     │
│ • "Same rhythm"                                              │
│ • "Different content"                                        │
│ • "60 seconds to create vs 2+ hours manual editing"        │
│                                                              │
│ VOICEOVER:                                                   │
│ "Watch the structure transfer in action. Same beats, same   │
│  energy flow, same narrative arc - but entirely different   │
│  clips telling a new story."                                 │
│                                                              │
│ WHY THIS WORKS:                                              │
│ • Instantly proves the concept (seeing is believing)        │
│ • Emotionally satisfying (cuts hitting beats feels good)    │
│ • Shows technical precision (frame-accurate alignment)      │
│ • Differentiates from templates (same structure ≠ template) │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2:15-2:50 | THE INTELLIGENCE (Prove It's Not Magic)         │
├─────────────────────────────────────────────────────────────┤
│ VISUAL: Stay in Vault, scroll down to show intelligence     │
│                                                              │
│ SECTION 1: Match Quality Metrics (5 seconds)                │
│   ┌─────────────────────────────────────┐                   │
│   │ 📊 MATCH QUALITY                    │                   │
│   │ • Vibe Match: 100% (30/30)          │                   │
│   │ • Energy Alignment: 93% (2 adjacent)│                   │
│   │ • Beat Sync: 85% of cuts aligned    │                   │
│   │ • Diversity: 30 unique clips, 0 reps│                   │
│   └─────────────────────────────────────┘                   │
│                                                              │
│ SECTION 2: Timeline Visualization (5 seconds)               │
│   • Show segment-by-segment breakdown                       │
│   • Hover over segment: "Wanted Urban/High, Got clip23"    │
│   • Color-coded by energy level                             │
│                                                              │
│ SECTION 3: Gemini's Reflection (10 seconds)                │
│   ┌─────────────────────────────────────┐                   │
│   │ 🤖 GEMINI REFLECTION                │                   │
│   │                                      │                   │
│   │ "Execution matched intent well.     │                   │
│   │  Intro used Nature clips as planned.│                   │
│   │  Peak required 2 energy compromises │                   │
│   │  (High→Medium) due to limited       │                   │
│   │  high-energy clips in library.      │                   │
│   │                                      │                   │
│   │  Recommendation: Add 3 more clips   │                   │
│   │  with 'Celebration' vibe for better │                   │
│   │  peak segment matching."            │                   │
│   └─────────────────────────────────────┘                   │
│                                                              │
│ SECTION 4: Why This Works (5 seconds)                      │
│   Auto-generated summary:                                   │
│   "This edit preserves the reference's pacing with 30 cuts, │
│    aligns 85% of cuts to beats, and maintains energy flow  │
│    across all arc stages."                                  │
│                                                              │
│ VOICEOVER:                                                   │
│ "The system doesn't just execute - it understands what it   │
│  did. Gemini planned the strategy, the algorithm executed   │
│  with precision, and Gemini reflects on the result."        │
│                                                              │
│ WHY THIS WORKS:                                              │
│ • Proves this isn't a black box (transparency)             │
│ • Shows Gemini's multi-step role (plan → reflect)          │
│ • Demonstrates technical depth (metrics are real)           │
│ • Closes the loop (reflection = Action Era hallmark)       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2:50-3:00 | THE IMPACT (Broader Vision)                     │
├─────────────────────────────────────────────────────────────┤
│ VISUAL: Quick montage (3-4 examples, 2 seconds each)       │
│                                                              │
│ Example 1: Cinematic travel reference → smooth travel edit  │
│ Example 2: Energetic party reference → energetic party edit │
│ Example 3: Calm nostalgic reference → calm nostalgic edit   │
│                                                              │
│ TEXT OVERLAY:                                                │
│ "Any style. Your content. Instant."                         │
│                                                              │
│ VISUAL: MIMIC logo + tagline                                │
│                                                              │
│ VOICEOVER:                                                   │
│ "Structure transfer for everyone. Powered by Gemini 3."     │
│                                                              │
│ FINAL FRAME:                                                 │
│ • Project name: MIMIC                                        │
│ • Tagline: "Borrow the rhythm, tell your story"            │
│ • GitHub link (very briefly visible)                        │
│                                                              │
│ WHY THIS WORKS:                                              │
│ • Shows versatility (not one-trick pony)                    │
│ • Reinforces core value prop                                │
│ • Ends on confident note                                    │
│ • Doesn't overstay welcome (judges appreciate brevity)     │
└─────────────────────────────────────────────────────────────┘

What MUST Be Visible in Demo
Non-negotiable elements:
✅ Gemini's strategic reasoning streaming in real-time (or convincing simulation)
✅ Side-by-side comparison showing rhythm transfer with visual beat alignment
✅ Beat synchronization proof - cuts visibly hitting beats in both videos
✅ Intelligence transparency - metrics, timeline, reflection panel
✅ Clear before/after - time comparison (hours vs seconds)
Why each matters:
Streaming reasoning → Proves Gemini is thinking, not just labeling
Side-by-side → Instant visceral proof of concept
Beat sync → Shows technical sophistication
Transparency → Differentiates from black-box AI tools
Time comparison → Shows practical utility
What Must NEVER Be Shown
Demo red flags (instant credibility loss):
❌ Loading spinners without context - Looks broken, wastes precious seconds
❌ Code or terminal output - Not accessible to non-technical judges
❌ Errors or failures - Even recoverable errors destroy confidence
❌ Confusing UI navigation - If judges are confused, you've lost
❌ The 53% vibe match case - Only demo best-case scenarios (ref4/ref5 quality)
❌ Overly technical jargon - Keep language accessible
❌ Long explanations - Show, don't tell
Quality bar: Every second of the demo must serve the narrative. If you can't explain why something is in the demo in one sentence, cut it.

## 5. THE APPLICATION (3-Page Architecture)
### Design Philosophy

Core principles:
Studio executes - Action happens here, zero friction
Library stores - Asset organization, boring by design
Vault explains - Intelligence lives here, this is where you win
Navigation flow:
Studio (Create) ←→ Library (Browse) ←→ Vault (Analyze)
     ↓                                        ↑
     └─────────── Output appears ─────────────┘

Why 3 pages only:
Judges can mentally model the app in 10 seconds
Clear separation of concerns (action vs data vs intelligence)
Matches "Action Era" pattern (orchestrator with stages)
Prevents feature bloat (no room for unnecessary features)

### PAGE 1: STUDIO (The Action Page)

Purpose: Execute synthesis with zero friction - prove this is an autonomous orchestrator.

User journey:
1. Upload reference video → see thumbnail + duration
2. Upload source clips → see grid of thumbnails
3. Click "Execute Synthesis" → sit back and watch

What's visible DURING execution:
┌─────────────────────────────────────────────────────────────┐
│ MIMIC STUDIO                                          [Home] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📹 REFERENCE VIDEO                                   │   │
│  │ ┌────────────┐                                       │   │
│  │ │ Thumbnail  │  awesome_edit.mp4                     │   │
│  │ │  [Image]   │  Duration: 14.2s                      │   │
│  │ └────────────┘                                       │   │
│  │ [Change Reference]                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🎬 SOURCE CLIPS (24)                                 │   │
│  │ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐                 │   │
│  │ │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │ │ 6 │ ...              │   │
│  │ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘                 │   │
│  │ [Add More Clips] [Clear All]                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        [Execute Synthesis] ← BIG BUTTON              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🧠 LIVE INTELLIGENCE                                 │   │
│  │ ┌────────────────────────────────────────────────┐   │   │
│  │ │                                                │   │   │
│  │ │ Analyzing reference structure...               │   │   │
│  │ │ ✓ Detected 30 segments, BPM 128                │   │   │
│  │ │ ✓ Arc: Intro → Build-up → Peak → Outro        │   │   │
│  │ │                                                │   │   │
│  │ │ Gemini planning narrative strategy...          │   │   │
│  │ │ ✓ Intro: Nature clips for calm opening        │   │   │
│  │ │ ✓ Build-up: Travel movement creates momentum  │   │   │
│  │ │ ✓ Peak: Friends celebration for climax        │   │   │
│  │ │                                                │   │   │
│  │ │ Executing with beat synchronization...         │   │   │
│  │ │ ✓ Matching clips... 12/30 segments complete   │   │   │
│  │ │ ✓ Aligning cuts to beat grid...               │   │   │
│  │ │ ✓ Rendering output...                         │   │   │
│  │ │                                                │   │   │
│  │ │ [████████████████░░░░] 80%                     │   │   │
│  │ │                                                │   │   │
│  │ └────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Live intelligence stream shows:
Stage transitions: "Analyzing reference..." → "Planning strategy..." → "Executing..." → "Rendering..."
Key decisions: "Intro: Nature clips recommended" (shows Gemini planning)
Progress indicators: "12/30 segments complete"
Beat sync events: "Aligning cuts to beat grid..."
Completion: "✓ Output ready! View in Vault"
What's NOT shown here:
❌ No detailed metrics (that's for Vault)
❌ No AI recommendations (distracting during execution)
❌ No clip analysis details (too much info)
❌ No user decisions required (autonomous execution)
Implementation notes:
WebSocket connection for real-time updates
Updates stream from backend as pipeline executes
Can simulate real-time for demo (replay cached log with delays)
Auto-redirect to Vault when complete
Preserve execution log for Vault display
Why this page design works:
Proves "Action Era" - system plans and executes without bothering user
Makes Gemini's intelligence VISIBLE during process
Zero cognitive load for user (upload → click → watch)
Fills time productively (no boring loading spinners)
Sets up expectation for intelligence in Vault

### PAGE 2: LIBRARY (The Asset Index)

Purpose: Prove this is a real application with state management, not a demo script.

Layout:
┌─────────────────────────────────────────────────────────────┐
│ MIMIC LIBRARY                               [Studio] [Vault] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Filters: [All] [References] [Clips] [Outputs]             │
│  Sort by: [Date ▼] [Name] [Duration]                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ REFERENCES (3)                                       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ ┌────────┐                                           │   │
│  │ │[Image] │  ref4.mp4                                 │   │
│  │ │        │  14.2s · 30 segments · BPM 128            │   │
│  │ │        │  Style: Cinematic Montage                 │   │
│  │ └────────┘  Added: Jan 25, 2026                      │   │
│  │                                              [View]   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ ┌────────┐                                           │   │
│  │ │[Image] │  ref5.mp4                                 │   │
│  │ │        │  16.6s · 21 segments · BPM 140            │   │
│  │ └────────┘  ...                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ CLIPS (55)                                           │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐                       │   │
│  │ │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │ ...                   │   │
│  │ │   │ │   │ │   │ │   │ │   │                       │   │
│  │ └───┘ └───┘ └───┘ └───┘ └───┘                       │   │
│  │ clip28.mp4  clip39.mp4  clip54.mp4 ...               │   │
│  │ Nature      Friends     Urban                         │   │
│  │ Medium      Medium      High                          │   │
│  │                                              [View]   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ OUTPUTS (2)                                          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ ┌────────┐                                           │   │
│  │ │[Image] │  output_session_abc123.mp4                │   │
│  │ │        │  14.2s · From ref4.mp4                    │   │
│  │ │        │  Vibe match: 100% · 30 clips used         │   │
│  │ └────────┘  Created: Jan 26, 2026                    │   │
│  │                                     [View] [Compare]  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘

What this page contains:
References: Thumbnails, duration, segment count, BPM, editing style
Clips: Thumbnails, filename, primary vibe, energy level
Outputs: Thumbnails, duration, source reference, basic metrics, creation date
Intelligence level: Very low (organizational only)
Just metadata display
No Gemini reasoning shown here
No analysis panels
Basic filters/search
What clicking "View" does:
References → Opens Vault Mode A (analysis view)
Clips → Opens Vault Mode A (clip intelligence view)
Outputs → Opens Vault Mode B (dual compare view)
Why this page is boring by design:
Judges don't score Library functionality highly
Exists to prove state management (real app, not script)
Provides navigation to intelligent features (in Vault)
Keeps UI clean and unsurprising
Implementation notes:
Read from cache files + outputs directory
No database needed (filesystem is enough)
Thumbnails generated on demand (FFmpeg)
Simple React components, no complexity

### PAGE 3: VAULT (The Intelligence Core)

Purpose: This is where you WIN the hackathon. All intelligence lives here.

Two modes, same page:

#### VAULT MODE A: Knowledge X-Ray (Read-Only Intelligence)

When shown: Click "View" on any Reference/Clip in Library

Example: Viewing a Reference
┌─────────────────────────────────────────────────────────────┐
│ VAULT: ref4.mp4 (Reference Analysis)          [Studio] [Lib] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📹 VIDEO PREVIEW                                     │   │
│  │ [Video player with playback controls]                │   │
│  │ Duration: 14.2s · BPM: 128                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🧠 GEMINI ANALYSIS                                   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Editing Style: Cinematic Montage                     │   │
│  │ Emotional Intent: Dynamic                            │   │
│  │ Arc Description: Fast-paced travel montage with      │   │
│  │                  friends, building from calm intro   │   │
│  │                  to energetic peak.                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📊 STRUCTURE BREAKDOWN (30 segments)                 │   │
│  │                                                       │   │
│  │ Timeline visualization:                              │   │
│  │ ┌─────────────────────────────────────────────────┐  │   │
│  │ │Intro    Build-up        Peak          Outro     │  │   │
│  │ │░░▓▓▓▓▓▓▓▓████████████████▓▓▓░░                 │  │   │
│  │ │                                                  │  │   │
│  │ │Legend: ░Low ▓Medium █High (energy)              │  │   │
│  │ └─────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │ Segment details (collapsible):                       │   │
│  │ ▼ Segment 1: 0.00s-0.53s (0.53s)                    │   │
│  │   Energy: Medium | Motion: Dynamic | Vibe: Nature   │   │
│  │   Arc Stage: Intro                                  │   │
│  │   Reasoning: "Opening shot of river raft sets calm  │   │
│  │               but dynamic tone."                     │   │
│  │                                                       │   │
│  │ ▶ Segment 2: 0.53s-0.93s (0.40s) ...                │   │
│  │ ▶ Segment 3: 0.93s-1.40s (0.47s) ...                │   │
│  │   [Show first 5, collapse rest with "Show all"]     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 💡 MATERIAL SUGGESTIONS                              │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Gemini recommends for best results:                  │   │
│  │ • High-quality travel footage                        │   │
│  │ • Candid shots of friends                            │   │
│  │ • Scenic nature views                                │   │
│  │ • Action-oriented travel activities                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Use This Reference in Studio →]                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Example: Viewing a Clip
┌─────────────────────────────────────────────────────────────┐
│ VAULT: clip28.mp4 (Clip Analysis)              [Studio] [Lib]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📹 VIDEO PREVIEW                                     │   │
│  │ [Video player]                                       │   │
│  │ Duration: 45.2s                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🧠 GEMINI ANALYSIS                                   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Overall Energy: Medium                               │   │
│  │ Overall Motion: Dynamic                              │   │
│  │ Vibes: Nature, Travel, Hiking                        │   │
│  │ Content: "First-person perspective of walking along  │   │
│  │          a rocky trail through a pine forest."       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ⭐ BEST MOMENTS (Pre-computed by Gemini)             │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ High Energy: 31.0s - 34.0s (3.0s)                    │   │
│  │ └─ "Navigating rockier section with more camera      │   │
│  │     movement and dynamic perspective."               │   │
│  │                                                       │   │
│  │ Medium Energy: 5.0s - 8.0s (3.0s)                    │   │
│  │ └─ "Steady walking on trail, representing overall    │   │
│  │     pace of the hike."                               │   │
│  │                                                       │   │
│  │ Low Energy: 21.0s - 24.0s (3.0s)                     │   │
│  │ └─ "Slightly flatter, more stable part with minimal  │   │
│  │     camera shake."                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Why Mode A matters:
Proves system has deep understanding (not surface-level)
Shows Gemini's pre-computed intelligence
Transparent about what data exists
Judges see this is a "glass box" not "black box"

#### VAULT MODE B: Dual Compare (The Money Shot)

When shown: Click "View" or "Compare" on any Output in Library

This is your demo centerpiece - the page that wins the hackathon.
┌─────────────────────────────────────────────────────────────┐
│ VAULT: output_session_abc123.mp4                [Studio] [Lib]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🎬 SIDE-BY-SIDE COMPARISON                           │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  ┌────────────────────┬───────────────────────┐      │   │
│  │  │   REFERENCE        │   YOUR EDIT           │      │   │
│  │  │   ref4.mp4         │   output_abc123.mp4   │      │   │
│  │  │                    │                       │      │   │
│  │  │  [Video player]    │  [Video player]       │      │   │
│  │  │                    │                       │      │   │
│  │  └────────────────────┴───────────────────────┘      │   │
│  │                                                       │   │
│  │  Energy graph overlay:                               │   │
│  │  ┌─────────────────────────────────────────────┐     │   │
│  │  │ High  █     ██████     ██████               │     │   │
│  │  │ Med   ██████      ██████      ███████       │     │   │
│  │  │ Low   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │     │   │
│  │  └─────────────────────────────────────────────┘     │   │
│  │                                                       │   │
│  │  [⏯ Play Both] [⏸ Pause] [🔁 Loop] [⚡ Show Beats]  │   │
│  │                                                       │   │
│  │  Playback position: 5.2s / 14.2s                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📊 MATCH QUALITY                                     │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Vibe Match:       ████████████████████░  100% (30/30)│   │
│  │  Energy Alignment: ████████████████████░   93% (2 adj)│   │
│  │  Beat Sync:        ████████████████░░░░░   85% aligned│   │
│  │  Diversity:        ████████████████████░  100% (30/30)│   │
│  │                                                       │   │
│  │  Quality Score: 94.5/100 ⭐⭐⭐⭐⭐                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ✨ WHY THIS EDIT WORKS                               │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ This edit preserves the reference's pacing with 30   │   │
│  │ cuts, aligns 85% of cuts to beats (BPM 128), and     │   │
│  │ maintains energy flow across all arc stages. The     │   │
│  │ clip library provided excellent vibe coverage for    │   │
│  │ Nature and Friends segments, with only 2 energy      │   │
│  │ compromises required during peak moments.            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🤖 GEMINI REFLECTION                                 │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Intent vs Execution Analysis:                        │   │
│  │                                                       │   │
│  │ ✅ Intro strategy executed as planned                │   │
│  │    Planned: Nature clips for calm opening            │   │
│  │    Actual: Used clips 28, 33, 30 (Nature)            │   │
│  │                                                       │   │
│  │ ✅ Build-up momentum achieved                        │   │
│  │    Planned: Travel movement                          │   │
│  │    Actual: Used clips 32, 47, 56 (Travel/Urban)      │   │
│  │                                                       │   │
│  │ ⚠️  Peak required 2 energy compromises               │   │
│  │    Wanted: High energy for segments 13, 24           │   │
│  │    Got: Medium energy (limited High clips available) │   │
│  │                                                       │   │
│  │ 💡 Recommendation:                                   │   │
│  │    Add 3 more High-energy clips with "Celebration"   │   │
│  │    or "Action" vibes for better peak matching.       │   │
│  │                                                       │   │
│  │ Overall: Execution matched intent well despite       │   │
│  │ library constraints. Strong vibe coherence and       │   │
│  │ beat alignment resulted in satisfying output.        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📈 DETAILED BREAKDOWN                      [Expand ▼]│   │
│  │                                                       │   │
│  │ Timeline with segment-by-segment analysis:           │   │
│  │ [Collapsible - shows EDL with reasoning per segment] │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🔄 TRY AGAIN                                         │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Want a different result?                             │   │
│  │                                                       │   │
│  │ [Re-synthesize (Same Clips)]                         │   │
│  │ └─ Explore alternate valid executions with same      │   │
│  │    clips (different random tie-breaks)               │   │
│  │                                                       │   │
│  │ [Improve Edit (Add Recommended Clips)]               │   │
│  │ └─ System will guide you to add clips that improve   │   │
│  │    match quality based on Gemini's recommendations   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Download Output] [Share Link] [Use in New Edit]           │
│                                                              │
└─────────────────────────────────────────────────────────────┘

"Improve Edit" flow (when clicked):
┌─────────────────────────────────────────────────────────────┐
│ IMPROVE THIS EDIT                                      [Back]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  System diagnosis identified opportunities to improve this  │
│  edit. Follow Gemini's recommendations:                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 💡 RECOMMENDED IMPROVEMENTS                          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │ 1. Add 3 High-energy clips                           │   │
│  │    Why: Peak segments (13, 24) required energy       │   │
│  │    compromises. High-energy clips will improve match.│   │
│  │    Suggested vibes: "Celebration", "Action", "Party" │   │
│  │                                                       │   │
│  │ 2. Add 2 Urban/Night clips                           │   │
│  │    Why: Segments 5, 12 wanted Urban vibe but used    │   │
│  │    semantic neighbors. Direct matches would improve. │   │
│  │    Suggested content: City lights, nightlife,        │   │
│  │    architectural shots                               │   │
│  │                                                       │   │
│  │ 3. Optional: Add calm Nature clips                   │   │
│  │    Why: Intro segments worked well but more variety  │   │
│  │    would enable alternate executions.                │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📤 ADD NEW CLIPS                                     │   │
│  │ [Upload Files] [Choose from Library]                 │   │
│  │                                                       │   │
│  │ After uploading, system will re-analyze and          │   │
│  │ re-synthesize with improved clip library.            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Cancel] [Upload & Re-synthesize →]                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Why Vault Mode B is your winning feature:
Side-by-side comparison - Instant visual proof of concept (the magic moment)
Match quality metrics - Shows technical sophistication with real numbers
"Why This Works" - Auto-generated summary demonstrates understanding
Gemini reflection - Closes the loop (plan → execute → reflect = Action Era)
Try again options - Shows system flexibility without manual editing
Improve flow - System self-diagnoses and guides user (intelligence collaboration)
Implementation notes for Vault:
Dual video players with synchronized playback (React + video.js or similar)
Energy graph overlay using canvas or SVG
Beat markers pulse on cut events (visual satisfaction)
Gemini reflection generated via post-synthesis API call
"Why This Works" is template-based from metrics (can be enhanced)
"Improve" recommendations derived from compromise analysis
## 6. FEATURE PRIORITIES (What We Are Actually Building)
This section defines the exact features we are implementing, how they fit into the system, and why they exist.
This is an internal engineering plan, not marketing copy.
The guiding constraint is:
We must make the system’s intelligence observable without turning it into a manual editor.

Revised Strategy: Lightweight Gemini Advisor (NOT Full Director)
Critical realization
A full “Gemini Director” (Gemini choosing clips per segment) costs 2–3 days, adds fragility, and produces minimal visible improvement in a 3-minute demo.
Instead, we implement a Lightweight Gemini Advisor:
Gemini provides high-level narrative guidance
Our algorithm still makes all final decisions
Gemini’s output is bias, not control
This unlocks reflection, planning narrative, and Action Era framing
Why this approach is better
✅ 1 day instead of 3
✅ Low integration risk
✅ Keeps system deterministic and constraint-driven
✅ Enables “Gemini suggested X, system chose Y” reflection
✅ Graceful fallback if Gemini fails
✅ Clearly not a prompt wrapper

### TIER 1 — MUST BUILD (Non-Negotiable)

These features define the project.

If something is not here, it is optional or cut.

Feature 1: Lightweight Gemini Advisor (Planning Layer)
Location: Backend (analysis stage) + surfaced later in Vault
Purpose: High-level planning, not execution
What it does
Gemini receives:
Reference blueprint summary (arc stages, segment counts, durations)
Clip library summary (metadata only: vibes, energy, motion, tags)
Gemini outputs:
3–5 suggested clips per arc stage
A short explanation of why those clips fit the narrative
Gemini does not:
Pick clips per segment
Override scoring
Evaluate video quality
See final output video
Output shape (conceptual)
{
  "Intro": ["clip28", "clip33", "clip30"],
  "Build-up": ["clip32", "clip47", "clip56"],
  "Peak": ["clip37", "clip26", "clip6", "clip22"],
  "Outro": ["clip27", "clip51"],
  "reasoning": "These clips progress from calm to energetic with increasing motion density."
}

How it integrates
During scoring, clips suggested by Gemini receive a small bonus
Bonus does not override energy, vibe, or diversity constraints
If Gemini fails → system runs unchanged
Why we are building this
Makes Gemini a planner, not a classifier
Enables later reflection
Supports “Action Era” narrative without destabilizing execution
Easy to cache and replay for demos

Feature 1.5: Multi-EDL Gemini Arbitration (Decision Layer)
Location: Backend (post-matching, pre-render) + surfaced in Vault
 Purpose: Select the best execution among multiple valid edits

What it does
After the deterministic engine generates multiple valid Edit Decision Lists (EDLs) for the same input:
Gemini evaluates each EDL as a complete outcome


Gemini selects the EDL that best matches the original reference intent


Only the selected EDL is rendered as the final output


This allows the system to explore creative variability without sacrificing determinism or constraints.

What Gemini sees
Gemini does not see raw video or timelines.
For each EDL, Gemini receives a structured summary:
Reference intent (from Stage 2 analysis)


Energy flow vs reference


Vibe match percentage


Number and type of compromises


Clip diversity


Arc-stage alignment


High-level execution notes


This mirrors how a human editor evaluates edits: by outcome quality, not frame-level mechanics.

What Gemini outputs
{
  "selected_edl": "EDL_B",
  "reasoning": "EDL_B maintains peak energy longer and aligns better with the celebratory intent.",
  "rejected": {
    "EDL_A": "Peak resolves too early",
    "EDL_C": "Intro lacks calm setup"
  }
}


What Gemini does NOT do
Does not choose clips per segment


Does not override constraints


Does not edit timelines


Does not judge aesthetics (“good/bad”)


Does not generate video


Gemini decides between executions, not how they are built.

How it integrates
Engine generates N EDLs (N=2–3)


Gemini selects the best EDL


System renders only the chosen one


All EDLs remain visible in Vault for transparency and “Try Again”



Why we are building this
Makes Gemini a decision-maker, not just a planner


Enables outcome-level reasoning (“this edit is better than that one”)


Strengthens Action-Era narrative (analyze → plan → execute → judge)


Zero risk to stability (all EDLs already valid)


Fully cacheable



Why this is NOT redundant with the Advisor
Advisor biases search


Arbiter selects outcome


They operate on opposite sides of execution



That’s it.
 One feature. No bloat. No overlap.

Feature 2: Real-Time Intelligence Stream (Studio Page)
Location: Studio
Purpose: Show orchestration while the system runs
What this shows
A live, human-readable execution feed:
🧠 Analyzing reference structure
✓ Detected 30 segments | BPM 128
✓ Arc: Intro → Build-up → Peak → Outro

🎬 Gemini providing narrative guidance
✓ Intro: Nature-focused clips
✓ Peak: High-energy group motion

⚙️ Executing synthesis
✓ Evaluating clips (12 / 30 segments)
✓ Resolving energy constraints
✓ Aligning cuts to beat grid

✅ Output ready → View in Vault

What it does NOT show
Scores
Metrics
Recommendations
User controls
Clip swapping
Why this exists
Proves this is a multi-stage system
Makes Gemini’s involvement visible
Avoids black-box perception
Keeps Studio focused on execution, not analysis
Studio rule:
The system runs autonomously.
Explanation happens later.

Feature 3: Side-by-Side Synchronized Playback (Vault Mode B)
Location: Vault → Compare Mode
Purpose: The primary demo “wow moment”
What it does
Reference and output videos play in sync
Scrubbing controls both
Cuts align temporally
Optional overlays:
Beat markers
Energy bands
Why this is critical
This visually proves structure transfer without explanation:
Same rhythm
Same pacing
Different content
This is stronger than any metric.

Feature 4: Forensics Panel (Vault Mode B)
Location: Vault → Compare Mode
Purpose: Explain why the edit works
A. Match Quality Metrics
Displayed metrics are computed from real system data:
Vibe match (% of segments with exact vibe)
Energy alignment (compromises counted)
Beat sync (cuts aligned to beats)
Diversity (unique clips used)
These are descriptive, not judgmental.

B. “Why This Works” Auto-Summary
A deterministic text summary generated from metrics + EDL:
Number of cuts
Beat alignment
Energy continuity
Constraint satisfaction
No Gemini required here.

C. Gemini Reflection (Post-Execution)
Gemini is shown:
Its own advisor hints
The actual execution (EDL + compromises)
Gemini answers:
Did execution align with the plan?
Where did it diverge?
Why were compromises necessary?
What would improve future runs?
Important constraint:
Gemini critiques intent alignment, not aesthetics.
Why this matters
This closes the loop:
Plan → Execute → Reflect
Almost no hackathon projects do this.

Feature 5: Vault Mode A — Analysis Views (Read-Only)
Location: Vault → Analysis
Purpose: Prove deep pre-computed intelligence
What exists here
Reference blueprint timeline
Segments
Arc stages
Energy levels
Clip analysis
Vibes
Motion
Best moments
Output metadata
Cut count
Segment mapping
Constraints
Read-only
No editing
No reruns
Why this exists
Proves the system actually understands its inputs
Makes cached intelligence visible
Establishes trust

Feature 6: Controlled Variability (“Try Again”)
Location: Vault → Compare Mode
Purpose: Creative exploration without chaos
What it does
Re-runs synthesis
Same reference
Same clips
Same analysis
Different tie-break resolutions
What it does NOT do
Reanalyze
Retrain
Randomize blindly
Why this exists
Turns non-determinism into a feature
Allows live interaction in demos
Reinforces collaboration narrative

### TIER 2 — NICE TO HAVE (Only If Time Remains)

Feature 7: “Improve Edit” Flow
Gemini reflection highlights missing clip types
User can upload more clips
System re-executes with improved constraints
Skip if demo timeline is tight.

Feature 8: Energy Graph Overlay
Energy (Low / Medium / High) plotted over time
Synced to playback
Purely visual polish.

### TIER 3 — EXPLICITLY CUT
We will not build:
Manual EDL editing
Clip locking / timeline dragging
Clip quality scoring
“Viral” prediction
Multi-reference blending
Auth, cloud scaling, batch jobs
These weaken the autonomous narrative and waste time.

### Final Internal Summary
Studio: Autonomous execution (no thinking UI)
Library: Asset navigation only
Vault: Intelligence, transparency, proof
Core idea to preserve everywhere:
Gemini provides intent.
The engine executes with constraints.
The system explains itself afterward.
## 7. CONSTRAINTS & GUARDRAILS
Time Constraints
Hard facts:
Deadline: February 10, 2026 @ 6:00am GMT+5 (Pakistan time)
Days remaining: 14 days
Realistic work capacity: 3-4 hours/day = 42-56 hours total
Must reserve: 8-10 hours for demo video production
Must reserve: 1 day (6 hours) for buffer/emergency fixes
Net development time: ~30-40 hours for features
Implication:
 Cannot build everything. Must ruthlessly prioritize Tier 1 features and cut aggressively if behind schedule.

Technical Constraints
Non-negotiables:
✅ No core pipeline rewrites - Current 5-stage system works reliably
✅ Must not break existing functionality - All changes are additive
✅ Caching must be preserved - Demo requires instant processing
✅ UI polish over feature breadth - 3 polished features > 10 half-baked
Technology stack locked:
Backend: Python, FastAPI, FFmpeg, librosa, Gemini 3 Flash API
Frontend: Next.js 16, React, TypeScript, Tailwind CSS
No major dependency changes allowed (risk of breaking things)

Demo Constraints
Hard limits:
✅ 3-minute maximum - Judges will not watch beyond this
✅ Must pre-cache everything - Cannot show 10-minute processing
✅ Must use best-case example - Only show ref4/ref5 quality (90-100% vibe match)
✅ Must be self-explanatory - No assumptions about voiceover or judge knowledge
Acceptable for demo:
✅ Simulated "real-time" streaming (replay cached log with delays)
✅ Pre-selected reference + clips (optimized for demo quality)
✅ UI polish only on demo path (Library can be rough)
✅ Mock some metrics if real computation is complex
NOT acceptable (would disqualify):
❌ Fake video output (must be real synthesis)
❌ Non-functional features shown (everything must work)
❌ Misleading claims about capabilities

Acceptable Hackiness
For a hackathon demo, these shortcuts are FINE:
Pre-cached analysis:


Reference and all clips analyzed ahead of time
Demo shows instant processing (from cache)
Honest in documentation that caching exists
Simulated real-time streaming:


Intelligence stream can replay cached log
Add realistic delays between messages
Visually indistinguishable from live
Demo-optimized content:


Hand-pick reference + clips for 100% vibe match
Ensure output quality is excellent
Not hiding capability - showing best case
Partial UI polish:


Studio + Vault pages polished (demo path)
Library can be functional but less polished
Focus effort where judges will look
Template-based generation:


"Why This Works" can be template + metrics
Don't need complex NLG for this
As long as it's accurate
Why these are acceptable:
Common in hackathon demos (judges expect this)
Doesn't misrepresent core capabilities
Allows focus on impressive features
Time-efficient way to show potential

## 8. SUCCESS METRICS
Minimum Viable Success: Top 10 (Honorable Mention - $2,000)
Requirements:
✅ Working demo (no crashes, smooth execution)
✅ Clear value proposition (judges "get it" in 30 seconds)
✅ Visible Gemini integration (can see AI thinking)
✅ Side-by-side comparison shows rhythm transfer
✅ Technical execution is solid (no obvious bugs)
Probability if we execute plan: 70-80%
Why achievable:
We already have working core system
Tier 1 features are buildable in time available
Demo script is strong
Positioning is clear and honest

Stretch Goal: Top 5
Additional requirements beyond Top 10:
✅ Memorable demo (judges remember after seeing 100 projects)
✅ Technical depth is obvious (forensics panel shows sophistication)
✅ Gemini integration is convincing (reflection feature closes loop)
✅ Polish is high (UI doesn't look like prototype)
Probability with excellent execution: 40-50%
What moves us up:
Demo video quality (professional editing, clear pacing)
Side-by-side moment is viscerally satisfying
Gemini reflection demonstrates intelligence
Forensics panel proves non-trivial engineering

Moonshot: Top 3 (Podium - $10k-50k)
Additional requirements beyond Top 5:
✅ Wow factor (judges are genuinely impressed)
✅ Output quality is excellent (judges think "I'd use this")
✅ Presentation is polished (rivals professional product demos)
✅ Concept resonates (judges love the core idea)
✅ Luck (right judges see it, mood is right, competition isn't insane)
Probability with perfect execution: 20-30%
Why difficult:
100,000+ competitors, many with 3 months vs our 2 weeks
No social impact angle (accessibility/health projects score higher)
Gemini integration is good but not revolutionary
Competing against top global engineers
But possible if:
Demo is exceptionally well-executed
Side-by-side moment is memorable
Judges appreciate creative tools category (like Outdraw AI)
Technical depth surprises them
We get lucky with judge assignment

How We'll Know We're On Track
Positive signals by day:
Day 2: Gemini Advisor works, produces reasonable suggestions, integrates cleanly
 Day 4: Intelligence stream looks good in UI, feels convincing
 Day 5: Side-by-side comparison is visually impressive, cuts align to beats
 Day 7: Forensics panel shows metrics, reflection makes sense
 Day 8: Vault Mode A displays intelligence nicely
 Day 9: All pages connected, no major bugs
 Day 11: Demo content quality is excellent (100% vibe match, smooth output)
 Day 13: Demo video draft looks professional, clear narrative

Red Flags (Need to Course-Correct)
Immediate action required if:
Gemini Advisor produces nonsensical suggestions → Simplify prompt or skip feature
Intelligence stream feels fake/unconvincing → Remove or simplify messaging
Side-by-side doesn't look impressive → Improve visual design or cut beat markers
Running out of time for Tier 1 features → Cut Tier 2, focus on demo
Demo content quality is poor (low vibe match) → Re-shoot clips or change reference
Demo video is confusing after first cut → Simplify narrative, cut complexity
Decision framework:
 If something isn't working by midpoint, cut it. Better to have 3 polished features than 5 half-working ones.

## 9. IMPLEMENTATION GUIDANCE
For Claude Code / Cursor / Antigravity
Core principles when implementing:
Don't break what works


Current 5-stage pipeline is solid and tested
All new code must be ADDITIVE not replacement
Test existing functionality after each change
Keep fallbacks for when new features fail
Gemini Advisor is a suggestion layer


Does NOT control matching (algorithm still decides)
Provides +50 score bonus to suggested clips
Graceful fallback if API fails (zero bonus, continue normally)
Cache hints to avoid repeated calls
Cache everything possible


Gemini Advisor hints: cache with reference_hash + clip_library_hash key
Gemini Reflection: cache with edl_hash key
All existing caches must continue working
Demo must feel instant (everything pre-cached)
UI changes are overlays


Don't rebuild existing pages from scratch
Add new components alongside existing structure
Studio/Vault pages get enhanced, not replaced
Keep Library simple (don't over-invest here)
The demo script is gospel


Every feature must serve the 3-minute demo
If it doesn't appear in demo script, it's lower priority
Visual impact > technical complexity
Judges will only see what's in the demo
Gemini prompt engineering


Temperature: 0.2 (consistent but not robotic)
Always request JSON output for parsing
Include clear instructions and constraints
Test prompts with multiple references before committing
Error handling for demo


Demo path must be bulletproof (no errors visible to user)
Log errors verbosely for debugging
Graceful degradation (if Gemini fails, show default text)
Non-demo paths can have simpler error handling
Timeline is aggressive


14 days for 5 major features + demo video
Cut scope aggressively if falling behind
Tier 1 must be done, Tier 2 is negotiable
Demo quality > feature completeness

File Structure Guidance
New files to create:
backend/engine/
  └── gemini_advisor.py          # Lightweight advisor function
      - get_advisor_hints()
      - format_hints_for_scoring()
      - cache management

backend/engine/
  └── gemini_reflection.py       # Post-synthesis reflection
      - generate_reflection()
      - compare_intent_vs_execution()
      - cache management

backend/engine/
  └── enhanced_logging.py        # Intelligence stream events
      - log_reference_analysis()
      - log_advisor_hints()
      - log_matching_progress()
      - format_for_websocket()

frontend/components/
  └── DualVideoPlayer.tsx        # Side-by-side component
  └── EnergyGraphOverlay.tsx     # Timeline visualization
  └── MetricsPanel.tsx           # Match quality display
  └── ReflectionPanel.tsx        # Gemini reflection display
  └── IntelligenceStream.tsx     # Live logging component

frontend/app/vault/
  └── [mode]/page.tsx            # Mode A: analysis, Mode B: compare

Files to modify:
backend/engine/orchestrator.py
  - Add call to gemini_advisor before matching
  - Add call to gemini_reflection after matching
  - Add WebSocket event emissions

backend/engine/editor.py
  - Modify score_clip_smart() to use advisor hints
  - Add reasoning tracking for reflection

backend/main.py
  - Add WebSocket endpoint for intelligence stream
  - Add API endpoint for reflection generation

frontend/app/studio/page.tsx
  - Add IntelligenceStream component
  - Add WebSocket connection

frontend/app/vault/page.tsx
  - Expand with Mode A and Mode B views
  - Add DualVideoPlayer, MetricsPanel, ReflectionPanel


Testing Strategy
Before demo:
End-to-end pipeline test:


Run with ref4 + 55 clips (best case)
Verify 100% vibe match, 0 repeats
Check all caches populate correctly
Ensure output video quality is excellent
Gemini Advisor test:


Test with ref4, ref5, ref3
Verify hints make sense
Check cache works (same inputs = same hints)
Test fallback when Gemini fails
UI component test:


Side-by-side plays synchronized
Energy graph updates correctly
Metrics display accurate numbers
Reflection text is readable
Demo simulation:


Run through entire demo script
Time each section (must fit in 3 minutes)
Verify no errors or loading delays
Check visual polish
On demo day:
Pre-cache reference + clips + advisor hints
Test full flow once before recording
Have backup plan if something breaks

## 10. THE HONEST ASSESSMENT
What This Project Actually Is
Strengths:
✅ Novel technical insight (structure transfer is genuinely interesting)
✅ Working end-to-end system (rare in hackathons - most are half-broken)
✅ Solid engineering (caching, beat sync, timeline validation are sophisticated)
✅ Fast execution capability (built core system in 17 days, can iterate quickly)
✅ Visually impressive output (when it works, side-by-side is satisfying)
✅ Real use case (creators actually want this functionality)
Weaknesses:
❌ Not fully "agentic" yet (mostly deterministic, reflection is only partially closed-loop)
❌ No social impact angle (productivity tool, not accessibility/education/health)
❌ Gemini integration could be deeper (adding advisor + reflection helps but isn't revolutionary)
❌ Quality variance (53-100% vibe match depending on clip library - not always excellent)
❌ Late to competition (2 weeks vs 3 months for most competitors)
Realistic scoring estimate:
Criteria
Current
With Plan
Perfect Execution
Technical Execution (40%)
28/40
34/40
38/40
Innovation (30%)
18/30
24/30
27/30
Impact (20%)
10/20
12/20
14/20
Presentation (10%)
6/10
8/10
10/10
TOTAL
62/100
78/100
89/100

Translation:
Current system: Top 30-40% (competent but forgettable)
With planned features: Top 10-15% (strong honorable mention candidate)
Perfect execution + luck: Top 3-5% (podium possible)

The Gap We Need to Close
To move from 62 → 78 (Top 10 range):
Show Gemini planning (not just classifying)


Solution: Gemini Advisor provides high-level strategy
Shows in real-time intelligence stream
Judges see "AI thinks, then code executes"
Close the loop (reflection)


Solution: Gemini Reflection compares intent vs execution
Shows in Vault forensics panel
Proves system understands what it did
Make intelligence visible (transparency)


Solution: Forensics panel, timeline visualization, metrics
Judges see this is not a black box
Technical depth becomes obvious
Perfect the demo (memorable moment)


Solution: Side-by-side with beat alignment
Viscerally satisfying (cuts hit beats)
Instant proof of concept
Polish presentation (professional quality)


Solution: Invest in demo video production
Clean UI, smooth pacing, clear narrative
Looks like a product, not a prototype

## 11. FINAL COMMITMENT & EXECUTION LOCK
This section exists to freeze the vision and ensure all future implementation decisions align with the intended system behavior.
If something contradicts this section, it should not be built.

### 11.1 What MIMIC Is (Final, Unchanging Definition)
MIMIC is not an editor, a recommender engine, or a generative video model.
MIMIC is:
A structure-transfer system that collaborates with Gemini 3 to extract, plan, execute, and explain video editing decisions—while keeping execution deterministic and transparent.
Key invariants:
Gemini reasons, but does not control
The system acts, but does not guess
The user observes, but is not burdened with decisions
This definition is final.

### 11.2 System Philosophy (Non-Negotiable)
Every feature must satisfy all three of the following:
Observable Intelligence
The system must visibly show what it knows, what it planned, or what it learned
Black-box behavior is unacceptable
Autonomous Execution
The user should never be asked to make creative micro-decisions
Upload → Execute → Observe → Reflect is the core loop
Post-Hoc Explainability
Explanation happens after execution, not during
Vault is the only place where “why” is answered
If a feature violates any of these, it is cut.

### 11.3 Page Responsibility Contract (Hard Boundaries)
Each page has a single job.
No overlap. No exceptions.
Studio
Purpose: Execute
Allowed: Live intelligence stream, progress, planning hints
Forbidden: Metrics, recommendations, reflection, decisions
Library
Purpose: Navigate
Allowed: Thumbnails, metadata, filters
Forbidden: Intelligence, reasoning, Gemini output
Vault
Purpose: Explain & Prove
Allowed: Analysis, metrics, reflection, comparisons
Forbidden: Editing controls, execution triggers (except “Try Again”)
If intelligence leaks into Studio, or execution leaks into Vault, the design is wrong.

11.4 Gemini’s Role (Locked Scope)
Gemini is a collaborator, not a director.
Gemini IS used for:
Reference structure understanding
Clip semantic understanding
High-level narrative planning (Advisor)
Post-execution reflection (intent vs outcome)
Gemini IS NOT used for:
Segment-by-segment clip selection
Aesthetic judgment (“good/bad clip”)
Viral prediction
Quality scoring
Manual editing suggestions
This constraint protects:
Determinism
Reliability
Demo stability
Technical credibility

### 11.5 The Only Loops That Exist
There are exactly two loops in the system:
Execution Loop
Analyze → Plan → Execute → Render
Fully autonomous
No user intervention
Improvement Loop (Optional)
Reflect → Recommend missing material → Re-execute
Triggered only in Vault
Requires user to add clips, not tweak logic
There are no live-edit loops, no human-in-the-middle loops, and no prompt-iteration loops.

11.6 What “Success” Looks Like Internally
Before worrying about judges, the system is considered successful if:
A new engineer can open Vault and understand:
What the system extracted
Why each decision was made
Where compromises occurred
The demo can run end-to-end without explanation
The side-by-side comparison makes the concept obvious in <5 seconds
Gemini’s contribution is visible but not overstated
No feature feels like a gimmick or filler
If these are true, judges will follow.

### 11.7 Cursor / Claude Operating Instructions
When working on this project, Cursor/Claude must:
Respect Tier 1 priority strictly
Never introduce new pages
Never add manual controls
Never “improve” creativity by adding randomness
Never collapse reasoning into a single Gemini call
Prefer clarity over cleverness
Prefer robustness over ambition
If unsure:
Default to not adding the feature.

### 11.8 Final Mental Model (For Everyone Involved)
Think of MIMIC as:
Gemini = Creative Strategist
Engine = Precision Editor
Vault = Glass Box Explanation
User = Observer & Beneficiary
Not:
Gemini as editor
User as director
System as magic

### 11.9 Final Statement
This project does not win by doing more.
It wins by doing one thing exceptionally clearly:
Showing that creative structure can be understood, transferred, executed, and explained.
If we preserve that clarity, everything else is noise.

END OF PLAN




