# MIMIC — Gemini 3 Hackathon Execution Plan (FINAL)

**Last Updated:** January 31, 2026  
**Deadline:** February 10, 2026  
**Target Outcome:** Top 10 Guaranteed · Top 3 Stretch but very much the goal
**Project Phase:** Core system complete → Demo polish + intelligence surfacing

---

## 1. HACKATHON CONTEXT

### Competition Overview

- **Event:** Gemini 3 Global Hackathon (Google DeepMind)
- **Participants:** 100,000+ registered competitors
- **Build Time:** ~3 months total (we are finishing in 9 days)
- **Prize Pool:** $100,000
  - Grand Prize: $50,000
  - 2nd: $20,000
  - 3rd: $10,000
  - Honorable Mentions: $2,000 × 10

### Submission Requirements

- **3-minute demo video** (hard cutoff, judges will stop watching)
- **Public GitHub repository**
- **~200-word Gemini integration explanation**
- **Working demo** (local deployment acceptable)

### Judging Criteria (Exact Weights)

| Category | Weight |
|-------|-------|
| Technical Execution | 40% |
| Innovation / Wow Factor | 30% |
| Potential Impact | 20% |
| Presentation / Demo | 10% |

### What Google Explicitly Wants

Direct guidance distilled from the hackathon brief:

- Gemini 3 is a **multimodal reasoning engine**, not a chatbot
- Avoid single-prompt “wrappers”
- Show **planning, orchestration, and reflection**
- Intelligence must be **visible** (glass-box systems)
- Emphasis on **Action Era** workflows:
  - Understand → Plan → Execute → Explain

### What Google Explicitly Does NOT Want

Anti-patterns that score poorly:

- ❌ Prompt-only tools
- ❌ Template-based editors
- ❌ Simple classification demos
- ❌ Black-box generation
- ❌ Generic chatbots
- ❌ Overclaimed “agentic” systems without proof

---

## 2. PROJECT DEFINITION

### What MIMIC Is (One Sentence)

MIMIC is a translation engine that converts human creative intent into deterministic editorial structure, executes under real-world constraints, and explains the outcome transparently.

### Core Insight

**Structure ≠ Content**

Editing quality is driven by:
- When cuts happen
- How energy flows
- How narrative arcs progress

MIMIC transfers **editing decisions**, not visual content.

### What MIMIC Is NOT

- ❌ Not a template system
- ❌ Not a generative video model
- ❌ Not a general-purpose editor
- ❌ Not a fully autonomous creative agent
- ❌ Not a black box

MIMIC is a **collaborative system**:
- Gemini reasons
- The engine executes
- The system explains itself

---

## 3. CURRENT SYSTEM STATUS (REALITY CHECK)

### Pipeline Execution

- **End-to-end works:**  
  Reference + clips → click → final rendered video  
- **No flaky steps**
- **Styling is basic**, but execution is stable

### Caching

Fully implemented and reliable:
- Reference analysis cached
- Clip analysis cached
- Standardized clips cached
- Cache keys include:
  - File hash
  - Duration / mtime
  - Config version

Demo will always run **from cache**.

### Determinism

- Same inputs → **mostly identical outputs**
- Controlled variability exists (tie-breaking)
- This is **intentional** to avoid robotic repetition

---

## 4. GEMINI INTEGRATION (ACTUAL, NOT PROMISED)

### Reference Analysis (Gemini)

Gemini currently extracts:
- Arc stages (Intro / Build / Peak / Outro)
- Segment-level reasoning text
- Emotional intent
- Editing style
- Material suggestions

This is **full semantic reasoning**, not labeling.

### Clip Analysis (Gemini)

Gemini outputs:
- Energy & motion classification
- Best moments (timestamps)
- Reasoning text for each best moment
- Semantic vibes
- Content descriptions

### Advisor (Gemini)

- **Exists and is functional**
- Provides high-level narrative guidance
- Biases scoring (does not override logic)
- Cached and deterministic

### Reflection (Gemini)

- ❌ Not implemented yet
- Will be added as **post-render critique**
- Strictly compares:
  - Planned intent vs executed outcome
  - Compromises
  - Improvement suggestions

---

## 5. SYSTEM ARCHITECTURE (MENTAL MODEL)

### The Creative Loop
Understand → Plan → Execute → Explain


### Roles

**Gemini 3 — Creative Strategist**
- Understands intent
- Plans narrative direction
- Reflects on outcome
- Never edits timelines

**Deterministic Engine — Precision Executor**
- Enforces constraints
- Scores clips
- Aligns cuts to beats
- Generates valid EDLs
- Renders final video

**Vault — Glass Box**
- Shows what the system understood
- Shows what it did
- Shows why it worked

**User — Observer**
- Uploads content
- Triggers execution
- Observes intelligence
- No micro-decisions required

---

## 6. APPLICATION STRUCTURE (LOCKED)

### Three Pages Only

This is intentional and final.

#### 1. Studio — Execution Page

**Purpose:** Show how MIMIC works

- Upload reference video
- Upload clips
- Click execute
- Watch live intelligence stream

Studio shows:
- Stage transitions
- Gemini analysis messages
- Advisor hints
- Execution progress

Studio does **not** show:
- Metrics
- Reflection
- Forensics
- Manual controls

---

#### 2. Library — Asset Browser (Low Priority)

**Purpose:** Prove this is a real application

- View references
- View clips
- View outputs
- Basic sorting/filtering

Judges do not need to focus here.

---

#### 3. Vault — Intelligence & Proof Page (MOST IMPORTANT)

**Purpose:** Prove MIMIC’s intelligence

Vault shows:
- Final rendered edit (single video)
- Gemini reasoning
- Segment breakdowns
- Match metrics
- Narrative explanations
- (Upcoming) Gemini reflection

No side-by-side comparison.

Vault is where you **talk and prove**, not execute.

---

## 7. DEMO STRATEGY (VISION-LOCKED — NO SIDE-BY-SIDE)

### Core Demo Philosophy

This demo is not about comparison — it is about **conviction**.

Side-by-side playback was intentionally removed because:
- It encourages nitpicking instead of understanding
- It visually weakens a strong standalone edit
- It shifts focus from *reasoning* to *pixel matching*

Instead, the demo is designed to make judges **feel** the intelligence first,
and then **see the evidence**.

The demo focuses on:
- **Two flawless edits**
- **Clear narrative intent**
- **Visible reasoning**
- **Confidence over coverage**

The goal is simple:
> Make it obvious that MIMIC understands *why* edits work — not just *what* they look like.

---

### The Two-Edit Demo Structure (Non-Negotiable)

The demo is built around **two edits produced by the same system**:

1. **A professional, aspirational edit** (credibility)
2. **A personal, emotional edit** (generalization)

This pairing is deliberate and critical.

---

### EDIT A — Professional / Aspirational Edit

**Purpose:**  
Establish technical credibility and taste.

**What the audience should think:**  
> “This feels expensive. This could replace part of a real editor’s workflow.”

**Edit characteristics:**
- High-quality cinematic footage (travel / lifestyle / documentary-style montage)
- Clean cuts, no heavy effects
- Music-driven pacing
- Clear narrative arc: Intro → Build → Peak → Outro
- Mix of wide, medium, and detail shots
- Rhythm and shot purpose are visually obvious

**What this edit proves:**
- MIMIC understands editorial structure, not templates
- Shot selection is intentional (establishing, transition, payoff)
- The system can replicate *professional rhythm* with different footage
- Lack of effects is a design choice, not a limitation

This edit carries the **technical weight** of the demo.

---

### EDIT B — Personal / Emotional Edit

**Purpose:**  
Prove generalization, emotional intelligence, and accessibility.

**What the audience should think:**  
> “I would actually use this.”

**Footage choice (locked intent):**
- Personal clips featuring friends (candid, imperfect, real)
- Natural moments: laughter, movement, shared experiences
- Emotion over visual quality

**What this edit proves:**
- The same system works on amateur footage
- Narrative intent matters more than camera quality
- MIMIC is not a pro-only tool — it is a storytelling platform

This edit carries the **emotional weight** of the demo.

---

### Demo Flow (3 Minutes, Tight):

High level explanation:
i think have an ides for the demo and this might be the correct way so id introduce the system id explain how we go wayyyy beyond simole template based editing we understsnd intent we understand shot composition we understand all these things i show an example of an edit that i found so this is a viral edit that influencers etc made and then we show how mimic would make this edit right so given different materials and the high quality stuff and all that blah blah and i show a proffesional edit(recomend what genre or type of edit would look best, slow, fast cuts, mix of everything etc) so i show a very high quality edit and show the reasoning etc, then what i do is i explain mimic is actually a genuinely intelligent system which understants narrative intent, when to use what shot how to tell a story and we can see this through our build blueprint system so id so u can describe the type of edit u want give your clips (these will be my personal clips i ahve to decide what i want so maybee like a nostalgic clip with my childhood videos(they are very cute) or it could be a friends related video since i have alot of fun clips with my friends) and have an edit made and then ill show that edit show how the system reasoned and made this edit and i can then say so mimic is really a platform for essentially everyone its more than just an Ai eiditng tool or productivity tool its just fun it allows everyone to enjoy and reminess about their experiences their and be the main character of their own story with quality high level edits that go beyond simple templates to actually tell the story worth telling

#### 0:00–0:30 — The Problem & Reframe

- Briefly acknowledge the status quo:
  - Most viral edits today are template-based
- Reframe the problem:
  - Editing quality comes from *intent, rhythm, and shot purpose*
- Claim:
  - MIMIC understands **why** edits work, not just how to copy them

---

#### 0:30–1:30 — Studio: How MIMIC Thinks

- Upload reference video
- Upload clips
- Execute edit
- Show live system logs:
  - Gemini analyzing narrative structure
  - Arc detection (Intro / Build / Peak / Outro)
  - Advisor guidance
  - Execution progress

Narration emphasis:
> “Gemini understands narrative intent and structure.  
> The engine executes those decisions deterministically.”

---

#### 1:30–2:30 — Vault: The Proof

- Play the **professional edit**
- Pause selectively to point out:
  - Arc progression
  - Energy flow
  - Beat alignment
  - Shot purpose

Scroll Vault panels:
- Segment-level reasoning
- Match quality
- Material constraints respected
- Why specific moments were chosen

This is where intelligence becomes undeniable.

---

#### 2:30–3:00 — Generalization & Vision

- Introduce the personal edit:
  - Same system
  - Different footage
  - Same level of care
- Show the edit briefly
- Close with the vision:

> “MIMIC isn’t just an AI editing tool.  
> It’s a storytelling platform — for professionals, for friends, for anyone who wants their moments told with intent.”

**Tagline:**  
**“Borrow the rhythm. Tell your story.”**

---

## 8. FEATURE PRIORITIES (DEMO-ALIGNED)

### TIER 1 — MUST BUILD (Before Anything Else)

1. **Two Perfect Demo Edits**
   - Professional edit (Edit A)
   - Personal edit (Edit B)
   - Fully pre-cached and deterministic

2. **Reflection Layer (Gemini)**
   - Post-render critique
   - Intent vs execution
   - Compromises explained
   - Cached by EDL hash

3. **Vault Polish**
   - Cinematic layout
   - Clear reasoning panels
   - No raw JSON exposed

---

### TIER 2 — NICE TO HAVE (Only If Ahead)

- Improved text styling
- Energy / arc visualization
- “Improve edit” recommendations

---

### EXPLICITLY CUT (Reaffirmed)

- Side-by-side playback
- Manual editing controls
- Timeline dragging
- Filter marketplaces
- Over-agentic behavior
- Effect-heavy styling agents

If a feature distracts from **story, intent, and reasoning**, it is cut.


## 9. RISK ASSESSMENT

### Biggest Risk

**Demo polish** — not intelligence.

The system is already smarter than the UI currently shows.

### “Do Not Touch” Zones

- `editor.py` — weighted-greedy matcher is stable
- `orchestrator.py` — pipeline flow is hardened

Tweaks are allowed, rewrites are not.

---

## 10. HONEST ASSESSMENT

### Current Output Quality

- Best output: **7.5 / 10**
- Technically strong
- Lacks “director soul” → fixed via better references + reflection

### With This Plan

- Technical Execution: 34–38 / 40
- Innovation: 24–27 / 30
- Impact: 12–14 / 20
- Presentation: 8–10 / 10

**Total:** 78–90 / 100

Top 10 is very realistic.  
Top 3 is possible with exceptional demo execution.

---

## 11. FINAL LOCK

### What MIMIC Is (Final)

MIMIC is a **structure-transfer system** that collaborates with Gemini 3 to:
- Understand editing intent
- Plan narrative strategy
- Execute deterministically
- Explain outcomes transparently

### Non-Negotiables

- Gemini reasons, does not control
- Engine executes, does not guess
- User observes, does not micromanage
- Vault explains everything

If a feature violates this:
**It is cut.**

---

**END OF PLAN**

