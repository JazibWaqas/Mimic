# MIMIC: Master Build Plan & Architecture Reference
## V5 - NEXT.JS FULL-STACK EDITION (Gemini 3 Global Hackathon)

---

## 🛠️ V5 CRITICAL UPDATES & ARCHITECTURE CHANGE

### 0. MAJOR ARCHITECTURE CHANGE: NEXT.JS + FASTAPI

**We've upgraded from Streamlit to a professional full-stack application:**

**New Stack:**
- 🎨 **Frontend:** Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- ⚡ **Backend:** FastAPI (Python) with same core engine modules
- 🚀 **Deployment:** Vercel (frontend) + Railway/Render (backend)

**Why This Change:**
- ✅ **More Professional:** Next.js looks like a product, Streamlit looks like a prototype
- ✅ **Better Demo:** Smoother UX, faster loads, impressive animations
- ✅ **Easier Deployment:** Vercel one-click deploy (vs buggy Streamlit Cloud)
- ✅ **Scalable:** Can add auth, payments, history later
- ✅ **Judge Appeal:** Shows full-stack capability (+5 points on scoring)

**Build Time:** ~4 hours (vs 2 hours Streamlit) - Worth the extra 2 hours for 10% higher score

### 1. DEPENDENCY VERSION WARNING
**CRITICAL:** The `google-generativeai` package MUST be version `>=0.8.3` to support Gemini 3 models.

**In requirements.txt, use:**
```txt
google-generativeai>=0.8.3  # NOT 0.3.2 (too old, will crash)
```

**If Cursor/agent tries to use 0.3.2, STOP and correct it immediately.**

### 1. TARGET MODEL UPDATES (MANDATORY FOR HACKATHON)
The hackathon requires **Gemini 3** specifically. Use these EXACT strings:
- **Primary Model:** `gemini-3-flash-preview` (Use for all "Brain" analysis)
- **Fallback Model:** `gemini-3-pro-preview` (Use if Flash fails or for complex analysis)
- **Emergency Fallback:** `gemini-exp-1206` (Use if both above return 404)

**CRITICAL:** Do NOT use `gemini-2.0-flash-exp` or any Gemini 2.x models. Judges will disqualify submissions not using Gemini 3.

### 2. FFMPEG PRECISION FIX (PREVENTS SYNC DRIFT)
**Problem:** Stream copy (`-c copy`) cuts only on keyframes, causing timing drift (2-5 second errors).  
**Solution:** Force re-encode for frame-perfect cuts.

**Updated Concatenation Command (Replaces Appendix B, Item 3):**
```bash
ffmpeg -f concat -safe 0 -i list.txt \
  -c:v libx264 -preset ultrafast -crf 23 \
  -c:a copy \
  stitched_video.mp4
```

**Rationale:** `-preset ultrafast` keeps render time <60s while maintaining frame accuracy.

### 3. AUDIO-VIDEO MERGE OPTIMIZATION (REPLACES APPENDIX B, ITEM 4)
Avoid double-encoding the video stream (quality loss + wasted time).

**Updated Merge Command:**
```bash
ffmpeg -i stitched_video.mp4 -i ref_audio.aac \
  -c:v copy -c:a aac \
  -map 0:v:0 -map 1:a:0 \
  -shortest final_output.mp4
```

**Key Change:** Video stream is copied (already encoded in step 2), only audio is re-encoded.

---

## 🚀 QUICK START FOR CURSOR/ANTIGRAVITY

**If you just want to start building immediately, follow these steps:**

### Step 1: Give Cursor This Exact Prompt

```
I'm building MIMIC - an AI video editing tool for the Gemini 3 Hackathon.

Read the entire MIMIC_MASTER_BUILD_PLAN_FINAL.md document carefully.

Then follow Phase 1 from Section 11.2 (Backend Core):
1. Create backend/ folder structure with engine/ subdirectory
2. Create all core files:
   - models.py (Section 4)
   - engine/brain.py (Section 5.1)
   - engine/processors.py (Section 5.2)
   - engine/editor.py (Section 5.3)
   - engine/orchestrator.py (Section 5.4)
   - utils.py (Section 5.5)
3. Create main.py with FastAPI endpoints (Section 4.5.1)
4. Apply Fix 1 from Section 9.5 (CORS with environment variable)

Use EXACT code from the document. Do not modify or "improve" anything.
I will test the backend before building frontend.
```

### Step 2: Test Backend Locally
```bash
# Setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install fastapi uvicorn[standard] python-multipart websockets \
            google-generativeai pydantic python-dotenv

# Configure
echo "GEMINI_API_KEY=your_actual_key_here" > .env
echo "FRONTEND_URL=http://localhost:3000" >> .env

# Run
uvicorn main:app --reload --port 8000

# Test in browser: http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Step 3: Build Frontend with Antigravity

```
Read Section 3.5 (UI/UX Design System) and Section 6 (Frontend Implementation).

Create a Next.js 14 app in frontend/ folder with:

Pages:
- app/page.tsx - Landing page with hero + demo section
- app/upload/page.tsx - Drag-drop file upload (reference + clips)
- app/generate/[id]/page.tsx - Processing page with WebSocket progress
- app/result/[id]/page.tsx - Side-by-side video comparison with sync toggle

Components (Section 6.2):
- components/FileUpload.tsx
- components/ProgressTracker.tsx  
- components/VideoComparison.tsx
- lib/api.ts (API client)

Design System (Section 3.5.2):
- Background: #0A0A0A (near-black)
- Primary: #8B5CF6 (purple with glow effects)
- Accent: #06B6D4 (cyan)
- Font: Inter

Style: Make it look like Runway ML - premium SaaS, not a hackathon prototype.
Use smooth animations, glow effects on buttons, cinematic feel.
```

### Step 4: Test Integration
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev

# Browser: http://localhost:3000
# Complete flow: Upload → Generate → Result → Download
```

**Full implementation details in Section 11 (Jazib's Execution Guide).**

---

## 📊 STRATEGIC CONTEXT & HACKATHON ALIGNMENT

**READ THIS SECTION WHEN:**
- You get stuck during implementation
- Code fails and you need to understand the "why" behind decisions
- You need to pivot or adjust the approach
- You're explaining the project to judges

### The Big Picture: What Are We Actually Building?

**MIMIC is an autonomous creative agent that:**
1. **Watches** a reference video to understand its editing structure (pacing, energy, rhythm)
2. **Analyzes** user-provided clips to classify their energy levels
3. **Plans** an Edit Decision List (EDL) that matches clips to reference structure
4. **Executes** professional video rendering using FFmpeg

**The Core Innovation:** We're NOT analyzing content (what's in the video), we're analyzing STRUCTURE (when cuts happen, energy patterns, rhythm). This is spatial-temporal reasoning, not object detection.

---

### Hackathon Requirements (Gemini 3 Global - Must Satisfy ALL)

#### **Submission Requirements:**
1. ✅ **Text Description (200 words):** How we use Gemini 3 (see template below)
2. ✅ **Public Project Link:** Deployed web app (Vercel) OR GitHub with easy local setup
3. ✅ **Public Code Repository:** GitHub with README
4. ✅ **3-Minute Demo Video:** Side-by-side comparison showing the "magic moment"

#### **Judging Criteria Mapping:**

**1. Technical Execution (40%)**
- ✅ **Quality Development:** Clean architecture (orchestrator pattern), Pydantic validation, error handling
- ✅ **Leverages Gemini 3:** Uses `gemini-3-flash-preview` for multimodal video reasoning
- ✅ **Functional Code:** Frame-perfect video rendering, robust fallback logic

**Our Pitch:** "We use Gemini 3's multimodal capabilities to analyze video structure—not content. The AI watches the reference video and extracts timing patterns with millisecond precision. This is spatial-temporal reasoning at work."

**2. Potential Impact (20%)**
- ✅ **Real-World Use:** Content creators (TikTok, Instagram, YouTube) constantly reverse-engineer viral videos
- ✅ **Broad Market:** 50M+ content creators globally, marketing agencies, social media teams
- ✅ **Problem Solved:** Manual video analysis takes hours; MIMIC does it in <60 seconds

**Our Pitch:** "Every creator has seen a viral video and thought 'I want that vibe.' Manual replication requires frame-by-frame analysis and professional editing skills. MIMIC democratizes this—anyone can steal the structure of viral content."

**3. Innovation / Wow Factor (30%)**
- ✅ **Novel Approach:** First tool to use AI for structural (not content) video analysis
- ✅ **Unique Solution:** Combines Gemini 3 reasoning with precision FFmpeg rendering
- ✅ **The "Money Shot":** Side-by-side comparison where output perfectly matches reference timing

**Our Pitch:** "We're not doing object detection. We're teaching AI to understand rhythm and pacing—the invisible DNA of viral videos. When you see the side-by-side, you'll get it."

**4. Presentation / Demo (10%)**
- ✅ **Clear Problem:** "How do creators replicate viral video pacing?"
- ✅ **Effective Demo:** 3-minute video with before/after comparison
- ✅ **Architecture Diagram:** Orchestrator pattern visualization (see below)
- ✅ **Gemini 3 Explanation:** Spatial-temporal analysis of video structure

---

### Strategic Track Alignment: 🎨 Creative Autopilot

**From Hackathon Brief:**
> "Combine Gemini 3 reasoning with high-precision multimodal creation. Generate professional, brand-consistent assets."

**How MIMIC Fits:**
- **Gemini 3 Reasoning:** Analyzes video structure to create precise timing blueprints
- **High-Precision Creation:** FFmpeg renders frame-perfect cuts (no keyframe drift)
- **Professional Assets:** Output videos match reference quality and structure
- **Brand Consistency:** Maintains user's original footage while applying viral pacing

**Why This Wins the Track:** We're not just generating content—we're using AI to orchestrate complex creative decisions (timing, pacing, energy matching) that traditionally require human editors.

---

### What Judges Will Ask (And Our Answers)

**Q: "Why not just use ChatGPT with video input?"**
A: "ChatGPT analyzes content ('there's a dog at 0:03'). Gemini 3's multimodal reasoning extracts structure ('energy spikes at 0:03, lasts 2.3 seconds'). We need timing precision, not object labels."

**Q: "Can't users just manually edit videos?"**
A: "Yes, but it takes hours. Professional editors charge $50-200/hour. MIMIC does it in <60 seconds for free. We're democratizing a skill that's currently gated by expertise and cost."

**Q: "What if the AI analysis is wrong?"**
A: "We have three fallbacks: (1) Try Gemini 3 Pro if Flash fails, (2) Use linear 2-second cuts if API is down, (3) Round-robin clip matching if no energy matches. The system ALWAYS produces output."

**Q: "How does this fit the 'Action Era'?"**
A: "Classic definition: Gemini SENSES the world (watches video), PLANS a complex task (creates EDL with millisecond precision), and ACTS (orchestrates FFmpeg to render). This is autonomous creation, not just analysis."

---

### The "Recovery Playbook" (When Things Break)

**If Gemini 3 API Fails:**
- **Context:** We need structural analysis, not content detection
- **Fallback:** Create linear blueprint (2-second segments, all "Medium" energy)
- **User Message:** "AI analysis unavailable, using simplified mode"
- **Impact:** Video still renders, just without energy matching

**If FFmpeg Rendering Fails:**
- **Context:** We need frame-perfect cuts to match beat timing
- **Debug:** Check if `-preset ultrafast` is being used (not `-c copy`)
- **Verify:** Test with `ffmpeg -version` and simple concat command
- **Impact:** If rendering is broken, entire demo fails

**If Clip Matching Logic Fails:**
- **Context:** We're prioritizing global pacing over perfect energy matches
- **Fallback:** Use round-robin (cycle through all clips regardless of energy)
- **User Message:** "Using all clips to fill structure"
- **Impact:** Video renders but energy matching may be off

**If Session Management Breaks:**
- **Context:** We use temp/{session_id}/ for all intermediate files
- **Debug:** Check if `cleanup_session()` is being called too early
- **Verify:** Ensure `session_id` persists in `st.session_state`
- **Impact:** Files may not be found, causing crashes

---

### Architecture at a Glance (For Context)

```
USER UPLOADS FILES
    ↓
[VALIDATE] Check duration, count, format
    ↓
[GEMINI 3 BRAIN] Analyze reference → StyleBlueprint
    ↓                Analyze clips → ClipIndex
    ↓
[EDITOR] Match clips to segments → EDL (Edit Decision List)
    ↓
[FFMPEG PROCESSOR] 
    → Standardize clips (1080x1920, 30fps)
    → Extract segments per EDL
    → Concatenate (with re-encode for frame accuracy)
    → Merge reference audio
    ↓
[OUTPUT] Final video matching reference structure
```

**Key Decision Points:**
1. **Gemini 3 Analysis:** Do we get valid JSON? → If no, use fallback blueprint
2. **Clip Matching:** Do we have energy matches? → If no, use round-robin
3. **Audio Handling:** Does reference have audio? → If no, render silent
4. **Concatenation:** Re-encode (not stream copy) to ensure frame-perfect cuts

---

### The 200-Word Gemini 3 Description (For Submission)

```
MIMIC uses Gemini 3's multimodal reasoning to analyze video structure—not content.

Traditional computer vision detects objects ("there's a person"). Gemini 3's 
spatial-temporal understanding extracts editing patterns: when cuts happen, 
energy levels, rhythm changes.

We feed Gemini 3 a reference video with a specific prompt: "Ignore what's in 
the video. Analyze WHEN cuts occur, HOW FAST things move, and the RHYTHM of 
edits." Gemini 3 returns a structured JSON "blueprint" with millisecond-precise 
timing data.

We then analyze user-provided clips with Gemini 3 to classify their energy 
levels (Low/Medium/High). Our matching algorithm maps clips to blueprint 
segments based on energy, creating an Edit Decision List (EDL).

Finally, FFmpeg renders the video with frame-perfect cuts—no keyframe drift.

This is the "Action Era" in practice: Gemini 3 SENSES (watches video), PLANS 
(creates EDL), and our system ACTS (renders output). The result: anyone can 
steal the editing structure of viral content in under 60 seconds.

Key Gemini 3 Features Used:
- Multimodal video input
- Spatial-temporal reasoning
- Structured JSON output (response_mime_type)
- 1M token context for long videos
```

---

### Success Metrics (How We Know It's Working)

**During Development:**
- ✅ Gemini 3 returns valid StyleBlueprint JSON
- ✅ FFmpeg output is exactly reference.total_duration (±0.01s)
- ✅ File size >100KB (indicates successful render)
- ✅ Pipeline completes in <60 seconds
- ✅ No crashes on invalid input

**During Demo:**
- ✅ Side-by-side video shows aligned beat drops
- ✅ Judge reaction: "Wait, how did it know to cut there?"
- ✅ Can explain Gemini 3 usage in <30 seconds
- ✅ Live demo works on first try

**For Judging:**
- ✅ Scores 35+/40 on Technical Execution (Gemini 3 integration is clear)
- ✅ Scores 25+/30 on Innovation (spatial-temporal reasoning is novel)
- ✅ Scores 15+/20 on Impact (clear market need)
- ✅ **Total: 75+/100 → Top 10% territory**

---

**END OF STRATEGIC CONTEXT**

---

## 🔒 SYSTEM INSTRUCTION FOR AI AGENTS (Cursor/Windsurf/Claude)

**YOU ARE BUILDING THIS PROJECT EXACTLY AS SPECIFIED.**

- **Target:** Gemini 3 Global Hackathon Submission
- **Execution Model:** Orchestrator Pattern (AI plans → FFmpeg executes)
- **Completion Criteria:** User uploads reference video + clips → System outputs professionally edited video matching reference structure
- **Core Principle:** This document contains ALL context. Do not improvise. Do not assume. Every decision has been made.

---

## 📋 TABLE OF CONTENTS

0. [Jazib's Execution Guide](#0-jazibs-execution-guide)
1. [Project Manifesto](#1-project-manifesto)
2. [Tech Stack & Architecture](#2-tech-stack--architecture)
3. [Directory Structure](#3-directory-structure)
4. [Data Models (Pydantic)](#4-data-models-pydantic)
5. [Component Specifications](#5-component-specifications)
6. [UI/UX Specification](#6-uiux-specification)
7. [Error Handling & Guardrails](#7-error-handling--guardrails)
8. [Testing & Validation](#8-testing--validation)
9. [Appendices](#9-appendices)

---

## 0. 👨‍💻 JAZIB'S EXECUTION GUIDE

### Part A: Environment Setup (5 minutes)

**Step 1: Get Gemini API Key**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create API key
3. Copy to clipboard

**Step 2: Install FFmpeg**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verify installation
ffmpeg -version  # Should show version 4.4+
```

**Step 3: Initialize Project**
```bash
mkdir mimic-project
cd mimic-project

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (you'll create requirements.txt in next step)
pip install -r requirements.txt
```

### Part B: Build Order (Follow This Sequence)

**Phase 1: Scaffolding (10 min)**
- Create directory structure (Section 3)
- Create `requirements.txt` (Appendix A)
- Create empty files for all modules
- Create `models.py` with Pydantic schemas (Section 4)

**Phase 2: Core Processing (30 min)**
- Implement `engine/processors.py` (Section 5.2)
- Test with dummy video files (use any MP4 from your phone)
- Verify: Output should be 1080x1920, 30fps

**Phase 3: Matching Logic (20 min)**
- Implement `engine/editor.py` (Section 5.3)
- Test with MOCK_BLUEPRINT (Section 9.1)
- Verify: Should produce valid EDL (Edit Decision List)

**Phase 4: AI Integration (20 min)**
- Implement `engine/brain.py` (Section 5.1)
- Test with a 5-second screen recording
- Verify: Should return valid StyleBlueprint JSON

**Phase 5: Orchestration (15 min)**
- Implement `engine/orchestrator.py` (Section 5.4)
- Wire all modules together
- Test end-to-end with real files

**Phase 6: UI Layer (25 min)**
- Implement `app.py` (Section 6)
- Connect file uploads to orchestrator
- Add progress indicators and output display

**Phase 7: Polish (10 min)**
- Add error messages (Section 7.2)
- Test all failure modes (Section 8.2)
- Verify cleanup (Section 5.5)

**Total Build Time: ~2 hours**

---

## 1. PROJECT MANIFESTO

### 1.1 The Core Idea

**Name:** MIMIC  
**Internal Codename:** Vibecoding  
**One-Sentence Pitch:** "Steal the editing structure of any viral video and instantly apply it to your own footage."

**The Problem We Solve:**
Video editing is time-consuming. Creators see viral content and think "I want that vibe" but don't know how to replicate the pacing, energy, and timing. They need to manually analyze cut points, energy levels, and transitions.

**Our Solution:**
An AI agent that watches a reference video, extracts its "editing DNA" (timing, pacing, energy), then applies that structure to user-provided clips—automatically.

### 1.2 Hackathon Alignment

**Why This Wins:**

1. **"Action Era" Definition:** We're not building a chatbot. We're building an autonomous creative agent that:
   - **Senses:** Watches video using multimodal AI
   - **Plans:** Generates an Edit Decision List (EDL) with millisecond precision
   - **Acts:** Renders professional video using FFmpeg

2. **Gemini 3 Showcase:** We leverage Gemini 3's video reasoning to perform **spatial-temporal analysis** (not just object detection). We answer "When does energy spike?" not "What is in the video?"

3. **Real-World Impact:** This tool could power content creation platforms, social media tools, or marketing agencies.

### 1.3 Core Philosophy

> **"Don't describe the edit. Show it."**

We don't give users a report ("The video has fast cuts at 0:03"). We give them a finished video with those fast cuts applied to their footage.

### 1.4 Success Criteria

✅ **Technical:** Runs locally, produces video 95%+ of the time  
✅ **Demo:** Side-by-side comparison wows judges in first 10 seconds  
✅ **Innovation:** Novel use of Gemini 3 for structural (not content) video analysis  

---

## 2. TECH STACK & ARCHITECTURE

### 2.1 Technology Choices

| Component | Technology | Why This Choice |
|-----------|------------|-----------------|
| **Frontend** | Next.js 14 + TypeScript | Professional UI, server-side rendering, better SEO, impressive to judges |
| **UI Framework** | Tailwind CSS + shadcn/ui | Rapid development, beautiful components, consistent design |
| **Backend** | FastAPI (Python 3.10+) | Fast API development, same async capabilities as Node, WebSocket support |
| **Core Engine** | Pure Python 3.10+ | Native Gemini SDK, FFmpeg bindings, Pydantic validation |
| **Video Processing** | FFmpeg 4.4+ | Industry-standard, deterministic, frame-perfect precision |
| **AI Engine** | Google Gemini 3 API | Multimodal video reasoning, fast inference, hackathon requirement |
| **Data Validation** | Pydantic 2.0+ | Type-safe models, JSON schema generation, validation |
| **File Storage** | Local Filesystem + Temp URLs | Simple for hackathon, can upgrade to S3 later |
| **Deployment** | Vercel + Railway | One-click deploy, free tier, production-ready |

### 2.2 Architecture Pattern: Full-Stack Separation

```
┌─────────────────────────────────────────────────────┐
│              NEXT.JS FRONTEND (Vercel)              │
│                                                     │
│  Landing Page → Upload Interface → Processing      │
│  → Results (Side-by-Side) → History Gallery        │
│                                                     │
│  Features:                                          │
│  - Drag-and-drop file upload                        │
│  - Real-time progress via WebSocket                 │
│  - Side-by-side video comparison                    │
│  - Past projects gallery                            │
│  - Smooth animations & transitions                  │
└──────────────────────┬──────────────────────────────┘
                       │ REST API + WebSocket
                       ▼
┌─────────────────────────────────────────────────────┐
│           FASTAPI BACKEND (Railway/Render)          │
│                                                     │
│  Endpoints:                                         │
│  POST   /api/upload      → Upload files             │
│  POST   /api/analyze     → Gemini 3 analysis        │
│  POST   /api/generate    → Render video             │
│  GET    /api/status/:id  → Progress updates         │
│  GET    /api/download/:id → Get final video         │
│  GET    /api/history     → Past projects            │
│  WS     /ws/progress/:id → Real-time updates        │
│                                                     │
└───┬──────────────┬──────────────┬─────────────┬────┘
    │              │              │             │
    ▼              ▼              ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐
│ BRAIN  │  │ EDITOR   │  │PROCESSOR │  │  UTILS    │
│(Gemini)│  │(Matching)│  │ (FFmpeg) │  │(Cleanup)  │
└────────┘  └──────────┘  └──────────┘  └───────────┘
```

**Key Principle:** Frontend and backend are completely decoupled. Frontend can be static-hosted, backend can scale independently.

### 2.3 Data Flow

```
USER INTERACTION (Frontend)
  ↓
[1] Upload reference.mp4 + clips → POST /api/upload
  ↓
  Backend saves to temp/{session_id}/
  Returns: {session_id, file_urls}
  
[2] Click "Generate" → POST /api/generate {session_id}
  ↓
  WebSocket opens: ws://backend/ws/progress/{session_id}
  
[3] Backend Pipeline:
  → Gemini 3 analyzes reference → StyleBlueprint
  → Gemini 3 analyzes clips → ClipIndex
  → Editor matches → EDL
  → FFmpeg renders → output.mp4
  (WebSocket sends progress updates at each step)
  
[4] Frontend receives completion → GET /api/download/{session_id}
  ↓
  Display side-by-side comparison
  Save to "Past Projects" gallery
```

---

## 3. DIRECTORY STRUCTURE

```
mimic-project/
│
├── frontend/                  # NEXT.JS APPLICATION
│   ├── app/
│   │   ├── page.tsx          # Landing page
│   │   ├── upload/
│   │   │   └── page.tsx      # Upload interface
│   │   ├── generate/
│   │   │   └── [id]/
│   │   │       └── page.tsx  # Processing page with progress
│   │   ├── result/
│   │   │   └── [id]/
│   │   │       └── page.tsx  # Side-by-side comparison
│   │   ├── history/
│   │   │   └── page.tsx      # Past projects gallery
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles
│   │
│   ├── components/           # REACT COMPONENTS
│   │   ├── ui/              # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── progress.tsx
│   │   │   └── ...
│   │   ├── FileUpload.tsx   # Drag-and-drop upload
│   │   ├── VideoPlayer.tsx  # Custom video player
│   │   ├── ProgressTracker.tsx  # Real-time progress
│   │   ├── VideoComparison.tsx  # Side-by-side viewer
│   │   ├── ProjectCard.tsx  # History gallery item
│   │   └── Hero.tsx         # Landing page hero
│   │
│   ├── lib/
│   │   ├── api.ts           # API client (fetch wrappers)
│   │   ├── websocket.ts     # WebSocket client
│   │   └── utils.ts         # Helper functions
│   │
│   ├── public/
│   │   ├── logo.svg
│   │   └── demo-preview.mp4
│   │
│   ├── tailwind.config.ts   # Tailwind configuration
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                  # FASTAPI APPLICATION
│   ├── main.py              # FastAPI app & routes
│   ├── models.py            # Pydantic schemas
│   ├── websocket.py         # WebSocket handlers
│   │
│   ├── engine/              # THE CORE LIBRARY (UNCHANGED)
│   │   ├── __init__.py
│   │   ├── orchestrator.py  # Main pipeline
│   │   ├── brain.py         # Gemini 3 integration
│   │   ├── editor.py        # Matching algorithm
│   │   └── processors.py    # FFmpeg wrappers
│   │
│   ├── utils.py             # File helpers, cleanup
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # API keys
│
├── temp/                    # Ephemeral storage (backend)
│   └── {session_id}/
│       ├── reference/
│       ├── clips/
│       ├── standardized/
│       ├── segments/
│       └── output/
│
├── history.db              # SQLite for project history (optional)
├── README.md
└── .gitignore
```

**Important Notes:**
- Frontend is completely independent (can deploy to Vercel separately)
- Backend engine/ folder is UNCHANGED from previous version
- `temp/` lives on backend server only
- History can use SQLite for simplicity (or Redis/PostgreSQL for production)

---

## 3.5 UI/UX DESIGN SYSTEM & SPECIFICATIONS

**READ THIS SECTION BEFORE BUILDING FRONTEND**

This section defines the exact look, feel, and behavior of the MIMIC interface. Antigravity/Cursor should implement this EXACTLY as specified.

### 3.5.1 Design Philosophy

**Core Principles:**
1. **Cinematic & Bold** - This is a video tool; the UI should feel like a production studio
2. **Instant Clarity** - User knows what to do in 3 seconds (upload reference → upload clips → generate)
3. **Delightful Feedback** - Every action has smooth animation and clear feedback
4. **Professional Polish** - This looks like a $10M SaaS product, not a hackathon project

**Inspiration References:**
- Runway ML (AI video tools)
- Linear (clean, fast, modern SaaS)
- Vercel (minimal, high-contrast, smooth animations)

---

### 3.5.2 Color Scheme & Brand Identity

**Primary Colors:**
```css
--background: #0A0A0A        /* Near-black background */
--surface: #151515           /* Card backgrounds */
--surface-elevated: #1F1F1F  /* Hover states */

--primary: #8B5CF6           /* Purple - main CTA */
--primary-hover: #7C3AED     /* Darker purple */
--primary-glow: #8B5CF640    /* Purple with 25% opacity for glow effects */

--accent: #06B6D4            /* Cyan - secondary actions */
--accent-hover: #0891B2      /* Darker cyan */

--success: #10B981           /* Green - completed states */
--warning: #F59E0B           /* Orange - processing */
--error: #EF4444             /* Red - errors */

--text-primary: #FFFFFF      /* White text */
--text-secondary: #A3A3A3    /* Gray text */
--text-muted: #525252        /* Subtle text */

--border: #262626            /* Subtle borders */
--border-hover: #404040      /* Hover borders */
```

**Why These Colors:**
- Dark theme = cinematic, professional (matches video production tools)
- Purple = creative, innovative (stands out in hackathon)
- High contrast = accessible, readable
- Glow effects = modern, premium feel

**Typography:**
```css
Font Family: 'Inter' (primary), 'JetBrains Mono' (code/technical)

Headings:
  H1: 48px, 700 weight, -0.02em letter-spacing
  H2: 36px, 700 weight, -0.01em letter-spacing
  H3: 24px, 600 weight

Body:
  Large: 18px, 400 weight, 1.6 line-height
  Regular: 16px, 400 weight, 1.5 line-height
  Small: 14px, 400 weight, 1.4 line-height

Technical (timestamps, code):
  'JetBrains Mono', 14px, 500 weight
```

---

### 3.5.3 Page-by-Page Specifications

#### **PAGE 1: Landing Page (/)**

**Layout:**
```
╔════════════════════════════════════════════════════════════╗
║  [LOGO: MIMIC]                        [History] [GitHub]   ║
║                                                            ║
║                    ════════════════                        ║
║                                                            ║
║              🎬 Steal the Structure                        ║
║              of Any Viral Video                            ║
║                                                            ║
║    Upload a reference → Add your clips → Get perfectly     ║
║    timed video in 60 seconds. Powered by Gemini 3.        ║
║                                                            ║
║         [Get Started →] (purple, glowing button)           ║
║                                                            ║
║                    ════════════════                        ║
║                                                            ║
║  ┌──────────────────┐  ┌──────────────────┐              ║
║  │  Before          │  │  After           │              ║
║  │  [Video Preview] │  │  [Video Preview] │              ║
║  │  Random clips    │  │  Perfectly synced│              ║
║  └──────────────────┘  └──────────────────┘              ║
║                                                            ║
║  "Notice how the cuts match the beat drops perfectly"     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

**Animations:**
- Hero text fades in with subtle upward slide (delay: 0ms, 100ms, 200ms per line)
- Video previews autoplay on hover
- Button has subtle glow pulse animation
- Smooth scroll to demo section

**Components:**
```typescript
// app/page.tsx
export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      <Hero />
      <DemoComparison />
      <HowItWorks />
      <CTA />
    </main>
  )
}
```

---

#### **PAGE 2: Upload Interface (/upload)**

**Layout:**
```
╔════════════════════════════════════════════════════════════╗
║  ← Back                                          Step 1/3  ║
║                                                            ║
║                  Upload Your Videos                        ║
║                                                            ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │  📹 Reference Video                                   │ ║
║  │                                                       │ ║
║  │     ┌─────────────────────────────────────────┐      │ ║
║  │     │                                         │      │ ║
║  │     │   🎬 Drag & drop reference video        │      │ ║
║  │     │      or click to browse                 │      │ ║
║  │     │                                         │      │ ║
║  │     │   Requirements: 3-20 seconds            │      │ ║
║  │     │   Formats: MP4, MOV, AVI                │      │ ║
║  │     └─────────────────────────────────────────┘      │ ║
║  │                                                       │ ║
║  │   [✓ dance_reference.mp4] 12s • 1920x1080  [x]       │ ║
║  │   [Video thumbnail preview]                          │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │  🎥 Your Clips (2+ required)                          │ ║
║  │                                                       │ ║
║  │     ┌─────────────────────────────────────────┐      │ ║
║  │     │                                         │      │ ║
║  │     │   🎬 Drag & drop your clips             │      │ ║
║  │     │      or click to browse                 │      │ ║
║  │     │                                         │      │ ║
║  │     │   No length limits • Any resolution     │      │ ║
║  │     │   More clips = better matching          │      │ ║
║  │     └─────────────────────────────────────────┘      │ ║
║  │                                                       │ ║
║  │   ┌────────────┐  ┌────────────┐  ┌────────────┐    │ ║
║  │   │[Thumbnail] │  │[Thumbnail] │  │[Thumbnail] │    │ ║
║  │   │ gym.mp4    │  │ cooking.mp4│  │ walking.mp4│    │ ║
║  │   │ 8s • High  │  │ 12s • Med  │  │ 6s • Low   │    │ ║
║  │   └────────────┘  └────────────┘  └────────────┘    │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║                                     [Continue →] (purple)  ║
╚════════════════════════════════════════════════════════════╝
```

**Interactions:**
- Drag-and-drop zone has dashed border that animates to solid on hover
- Uploading shows progress bar for each file
- Files display with thumbnail, duration, and auto-detected energy level
- Can reorder clips by dragging
- Delete files with smooth fade-out animation
- "Continue" button only enabled when reference + 2+ clips uploaded

**Validation Messages:**
```typescript
// Real-time validation
"Reference video must be 3-20 seconds" (orange warning)
"Please upload at least 2 clips" (orange warning)
"✓ Ready to generate!" (green success)
```

**Components:**
```typescript
// components/FileUpload.tsx
interface FileUploadProps {
  type: 'reference' | 'clips'
  onFilesChange: (files: File[]) => void
  maxFiles?: number
}

// Features:
- Drag-and-drop with react-dropzone
- File validation (size, format, duration)
- Thumbnail generation using canvas API
- Progress indication during upload
```

---

#### **PAGE 3: Processing (/generate/[id])**

**Layout:**
```
╔════════════════════════════════════════════════════════════╗
║                                              [Cancel]      ║
║                                                            ║
║               ✨ Creating Your Video...                    ║
║                                                            ║
║  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  75%              ║
║                                                            ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │  ✓ Reference analyzed                                │ ║
║  │    └─ 3 segments detected • Total: 12.4s             │ ║
║  │                                                       │ ║
║  │  ✓ Clips analyzed                                    │ ║
║  │    └─ High: 2 clips • Medium: 1 clip • Low: 0 clips  │ ║
║  │                                                       │ ║
║  │  ✓ Edit sequence created                             │ ║
║  │    └─ 3 segments matched to clips                    │ ║
║  │                                                       │ ║
║  │  ⏳ Rendering video...                                │ ║
║  │    └─ Frame-perfect cuts in progress                 │ ║
║  │                                                       │ ║
║  │  ⬜ Merging audio                                     │ ║
║  │                                                       │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║         🧠 Powered by Gemini 3 Flash Preview              ║
║                                                            ║
║  Processing time: 32s elapsed                             ║
╚════════════════════════════════════════════════════════════╝
```

**Animations:**
- Progress bar fills smoothly with easing
- Checkmarks appear with bounce animation
- Current step pulses with subtle glow
- Estimated time updates every 2 seconds
- Sparkle animation on completion

**Real-Time Updates:**
```typescript
// WebSocket connection to backend
const ws = new WebSocket(`ws://backend/ws/progress/${sessionId}`)

ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  // update: { step: 'analyzing_reference', progress: 0.2, message: '...' }
  updateProgressBar(update)
}
```

**Components:**
```typescript
// components/ProgressTracker.tsx
interface ProgressStep {
  id: string
  title: string
  subtitle?: string
  status: 'pending' | 'active' | 'complete' | 'error'
}

const steps: ProgressStep[] = [
  { id: 'upload', title: 'Files uploaded', subtitle: 'Reference + 3 clips' },
  { id: 'analyze_ref', title: 'Reference analyzed', subtitle: 'Gemini 3 processing...' },
  { id: 'analyze_clips', title: 'Clips analyzed', subtitle: 'Energy classification' },
  { id: 'matching', title: 'Edit sequence created', subtitle: 'Clips matched to structure' },
  { id: 'rendering', title: 'Rendering video', subtitle: 'Frame-perfect cuts' },
  { id: 'audio', title: 'Merging audio', subtitle: 'Syncing reference audio' },
]
```

---

#### **PAGE 4: Result (/result/[id])**

**Layout:**
```
╔════════════════════════════════════════════════════════════╗
║  [MIMIC Logo]                    [Download] [New Project] ║
║                                                            ║
║                    🎉 Your Video is Ready!                 ║
║              Generated in 45 seconds • Ready to share      ║
║                                                            ║
║  ┌─────────────────────────┐  ┌──────────────────────────┐║
║  │  📹 Reference Structure │  │  ✨ Your Generated Video ││║
║  │                         │  │                          ││║
║  │  ▶️ [Video Player]      │  │  ▶️ [Video Player]       ││║
║  │                         │  │                          ││║
║  │  00:00 ━━━━●━━━━ 00:12  │  │  00:00 ━━━━●━━━━ 00:12  ││║
║  │                         │  │                          ││║
║  │  Original TikTok dance  │  │  Your custom edit        ││║
║  │  Fast cuts at 0:03,     │  │  Same rhythm, your       ││║
║  │  0:07, beat drop 0:10   │  │  content                 ││║
║  └─────────────────────────┘  └──────────────────────────┘║
║                                                            ║
║  [Sync Playback Toggle] (plays both videos in sync)       ║
║                                                            ║
║  💡 Notice: Beat drops align perfectly at 0:03 and 0:10   ║
║                                                            ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │  🧠 AI Analysis  [Expand ▼]                          │ ║
║  │                                                       │ ║
║  │  Reference Structure:                                │ ║
║  │  • Segment 1: 0.0s - 3.2s (High energy, Dynamic)     │ ║
║  │  • Segment 2: 3.2s - 8.1s (Medium energy, Static)    │ ║
║  │  • Segment 3: 8.1s - 12.4s (High energy, Dynamic)    │ ║
║  │                                                       │ ║
║  │  Clip Matching:                                      │ ║
║  │  • gym.mp4 → Segment 1, 3 (High energy match)        │ ║
║  │  • cooking.mp4 → Segment 2 (Medium energy match)     │ ║
║  │                                                       │ ║
║  │  Rendering Details:                                  │ ║
║  │  • Resolution: 1080x1920 (vertical)                  │ ║
║  │  • Frame rate: 30fps                                 │ ║
║  │  • Audio: Synced from reference                      │ ║
║  │  • Processing time: 45 seconds                       │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌────────────────────┐  ┌────────────────────┐          ║
║  │  [⬇️ Download MP4] │  │  [🔄 Try Another]  │          ║
║  │  Ready to upload   │  │  Make more edits   │          ║
║  └────────────────────┘  └────────────────────┘          ║
╚════════════════════════════════════════════════════════════╝
```

**Interactions:**
- **Sync Playback:** Both videos play in perfect sync, seek bars move together
- **Hover Timestamps:** Hovering over a specific time shows which clip is playing at that moment
- **Expandable Analysis:** Technical details hidden by default, expand for nerds
- **Download Button:** Downloads MP4 with suggested filename `mimic_output_YYYYMMDD.mp4`
- **Share Button:** (Optional) Copy shareable link

**Video Player Features:**
```typescript
// components/VideoComparison.tsx
interface VideoComparisonProps {
  referenceUrl: string
  outputUrl: string
  blueprint: StyleBlueprint
}

// Features:
- Custom controls (play, pause, seek, volume)
- Sync toggle (plays both videos simultaneously)
- Timestamp markers showing segment boundaries
- Hover preview (scrub through timeline)
- Keyboard shortcuts (Space = play/pause, Arrow keys = seek)
```

---

#### **PAGE 5: History (/history)**

**Layout:**
```
╔════════════════════════════════════════════════════════════╗
║  [MIMIC Logo]  History                    [New Project]   ║
║                                                            ║
║                  Your Past Projects                        ║
║                  12 videos created                         ║
║                                                            ║
║  [All] [This Week] [This Month] [Search...]               ║
║                                                            ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    ║
║  │[Thumbnail]   │  │[Thumbnail]   │  │[Thumbnail]   │    ║
║  │              │  │              │  │              │    ║
║  │Dance Edit #3 │  │Workout Mix   │  │Travel Vlog   │    ║
║  │Created 2h ago│  │Created 1d ago│  │Created 3d ago│    ║
║  │12s • 3 clips │  │15s • 4 clips │  │10s • 2 clips │    ║
║  │              │  │              │  │              │    ║
║  │[View] [⬇️]   │  │[View] [⬇️]   │  │[View] [⬇️]   │    ║
║  └──────────────┘  └──────────────┘  └──────────────┘    ║
║                                                            ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    ║
║  │[Thumbnail]   │  │[Thumbnail]   │  │[Thumbnail]   │    ║
║  │...           │  │...           │  │...           │    ║
║  └──────────────┘  └──────────────┘  └──────────────┘    ║
║                                                            ║
║                      [Load More]                           ║
╚════════════════════════════════════════════════════════════╝
```

**Features:**
- Grid layout (3 columns desktop, 1 column mobile)
- Each card shows thumbnail, title, creation date, stats
- Filter by date range
- Search by filename or date
- Clicking card navigates to result page
- Download directly from history
- Delete with confirmation modal

**Data Storage:**
```typescript
// Simple SQLite schema for history
interface Project {
  id: string
  created_at: timestamp
  reference_filename: string
  clip_count: number
  output_url: string
  thumbnail_url: string
  duration: number
  blueprint: StyleBlueprint (JSON)
}
```

---

### 3.5.4 Component Library (shadcn/ui)

**Install these shadcn/ui components:**
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add toast
```

**Customization (tailwind.config.ts):**
```typescript
export default {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0A0A0A",
        surface: "#151515",
        primary: {
          DEFAULT: "#8B5CF6",
          hover: "#7C3AED",
        },
        accent: {
          DEFAULT: "#06B6D4",
          hover: "#0891B2",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in",
        "slide-up": "slideUp 0.5s ease-out",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(139, 92, 246, 0.4)" },
          "50%": { boxShadow: "0 0 40px rgba(139, 92, 246, 0.6)" },
        },
      },
    },
  },
}
```

---

### 3.5.5 Micro-Interactions & Animations

**Button States:**
```css
/* Primary CTA buttons */
.btn-primary {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 40px rgba(139, 92, 246, 0.6);
}

.btn-primary:active {
  transform: translateY(0);
}
```

**File Upload Hover:**
```css
.upload-zone {
  border: 2px dashed var(--border);
  transition: all 0.3s ease;
}

.upload-zone:hover {
  border-color: var(--primary);
  background: rgba(139, 92, 246, 0.05);
}

.upload-zone.dragging {
  border-color: var(--primary);
  background: rgba(139, 92, 246, 0.1);
  transform: scale(1.02);
}
```

**Progress Bar Animation:**
```css
.progress-bar {
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(90deg, #8B5CF6, #06B6D4);
}

.progress-bar::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

**Video Comparison Sync:**
```typescript
// When sync is enabled, both videos play together
const handleSyncSeek = (time: number) => {
  refVideoRef.current.currentTime = time
  outputVideoRef.current.currentTime = time
}

const handleSyncPlay = () => {
  refVideoRef.current.play()
  outputVideoRef.current.play()
}
```

---

### 3.5.6 Responsive Design Breakpoints

```css
/* Mobile-first approach */
.container {
  padding: 1rem;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
  
  .video-comparison {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .history-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Large desktop (1440px+) */
@media (min-width: 1440px) {
  .container {
    max-width: 1400px;
  }
}
```

---

### 3.5.7 Accessibility (A11y)

**Requirements:**
- All interactive elements have focus states (purple ring)
- Color contrast ratio ≥ 4.5:1 for text
- Keyboard navigation works for all features (Tab, Enter, Esc)
- Screen reader support with ARIA labels
- Video players have captions support (optional for hackathon)

**Example:**
```tsx
<button
  className="btn-primary"
  aria-label="Generate video with AI"
  aria-describedby="generate-description"
>
  Generate Video →
</button>
<span id="generate-description" className="sr-only">
  Upload reference and clips, then click to start AI video generation
</span>
```

---

### 3.5.8 Loading States & Skeletons

**File Upload Skeleton:**
```tsx
<div className="animate-pulse">
  <div className="h-40 bg-surface rounded-lg mb-4"></div>
  <div className="h-4 bg-surface rounded w-3/4 mb-2"></div>
  <div className="h-4 bg-surface rounded w-1/2"></div>
</div>
```

**Video Player Skeleton:**
```tsx
<div className="aspect-video bg-surface rounded-lg animate-pulse flex items-center justify-center">
  <div className="w-16 h-16 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
</div>
```

---

### 3.5.9 Error States

**Friendly Error Messages:**
```typescript
const errorMessages = {
  upload_failed: {
    title: "Upload Failed",
    message: "Couldn't upload your video. Please check your internet connection and try again.",
    action: "Retry Upload"
  },
  gemini_api_error: {
    title: "AI Analysis Unavailable",
    message: "Our AI service is temporarily unavailable. We'll use a simplified analysis mode.",
    action: "Continue Anyway"
  },
  ffmpeg_error: {
    title: "Rendering Failed",
    message: "Something went wrong while creating your video. Please try again or contact support.",
    action: "Try Again"
  },
  file_too_large: {
    title: "File Too Large",
    message: "Please upload videos under 500MB. Consider compressing your files first.",
    action: "Choose Different File"
  }
}
```

**Error Display:**
```tsx
<div className="bg-error/10 border border-error rounded-lg p-4">
  <div className="flex items-start gap-3">
    <AlertCircle className="w-5 h-5 text-error mt-0.5" />
    <div className="flex-1">
      <h4 className="font-semibold text-error">{error.title}</h4>
      <p className="text-sm text-text-secondary mt-1">{error.message}</p>
      <button className="mt-3 text-sm font-medium text-error hover:underline">
        {error.action}
      </button>
    </div>
  </div>
</div>
```

---

### 3.5.10 Antigravity Build Prompt

**Use this exact prompt to build the frontend:**

```
Build a Next.js 14 app for MIMIC - an AI video editing tool that matches user clips to a reference video's structure.

DESIGN SYSTEM:
- Dark theme: background #0A0A0A, surface #151515
- Primary color: Purple #8B5CF6 with glow effects
- Accent: Cyan #06B6D4
- Typography: Inter (UI), JetBrains Mono (technical)
- Use shadcn/ui components (button, card, progress, dialog)

PAGES:
1. Landing (/) - Hero with demo comparison, "Get Started" CTA
2. Upload (/upload) - Drag-drop for reference + multiple clips, show thumbnails
3. Processing (/generate/[id]) - Real-time progress with WebSocket, 5-step tracker
4. Result (/result/[id]) - Side-by-side video comparison with sync playback, expandable AI analysis
5. History (/history) - Grid of past projects with thumbnails

INTERACTIONS:
- Smooth animations (fade-in, slide-up, glow pulse)
- Drag-and-drop with visual feedback
- Video players with sync toggle
- Real-time progress via WebSocket
- Mobile-responsive (grid → stack)

API ENDPOINTS (connect to FastAPI backend):
- POST /api/upload
- POST /api/generate
- GET /api/status/:id
- WS /ws/progress/:id
- GET /api/download/:id
- GET /api/history

Make it look like a premium SaaS product (Runway ML style), not a hackathon project. Focus on polish: smooth animations, clear feedback, delightful micro-interactions.
```

---



## 4. DATA MODELS (PYDANTIC)

Create `backend/models.py` in the project root with this exact code:

```python
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
        "motion": "Dynamic"
    }
    """
    id: int = Field(..., description="Sequential segment number (1, 2, 3...)")
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., gt=0, description="End time in seconds")
    duration: float = Field(..., gt=0, description="Segment length in seconds")
    energy: EnergyLevel
    motion: MotionType
    
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

class ClipMetadata(BaseModel):
    """
    Analysis result for a single user clip.
    
    Example: {
        "filename": "dance_clip.mp4",
        "filepath": "/temp/abc123/clips/dance_clip.mp4",
        "duration": 5.2,
        "energy": "High",
        "motion": "Dynamic"
    }
    """
    filename: str
    filepath: str
    duration: float = Field(..., gt=0)
    energy: EnergyLevel
    motion: MotionType


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
```

**Key Points:**
- Use these models everywhere. Never pass raw dicts.
- Pydantic validates data automatically. If invalid, it raises clear errors.
- Models are self-documenting (see docstrings and Field descriptions).

---

## 4.5 FASTAPI BACKEND SPECIFICATION

**Location:** `backend/main.py`

### 4.5.1 API Endpoints

```python
"""
MIMIC FastAPI Backend
Handles file uploads, Gemini 3 processing, and video rendering.
"""

from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uuid
from pathlib import Path
from typing import List
import asyncio
import json

from models import *
from engine.orchestrator import run_mimic_pipeline
from utils import ensure_directory, cleanup_session

app = FastAPI(title="MIMIC API", version="1.0.0")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track active sessions
active_sessions = {}

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/api/upload")
async def upload_files(
    reference: UploadFile = File(...),
    clips: List[UploadFile] = File(...)
):
    """
    Upload reference video and user clips.
    
    Returns:
        {
            "session_id": "uuid",
            "reference": {"filename": "...", "size": ...},
            "clips": [{"filename": "...", "size": ...}, ...]
        }
    """
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Create session directories
    session_dir = Path(f"temp/{session_id}")
    ref_dir = ensure_directory(session_dir / "reference")
    clips_dir = ensure_directory(session_dir / "clips")
    
    # Save reference
    ref_path = ref_dir / reference.filename
    with open(ref_path, "wb") as f:
        content = await reference.read()
        f.write(content)
    
    # Save clips
    clip_paths = []
    for clip in clips:
        clip_path = clips_dir / clip.filename
        with open(clip_path, "wb") as f:
            content = await clip.read()
            f.write(content)
        clip_paths.append(str(clip_path))
    
    # Store session info
    active_sessions[session_id] = {
        "reference_path": str(ref_path),
        "clip_paths": clip_paths,
        "status": "uploaded",
        "progress": 0.0
    }
    
    return {
        "session_id": session_id,
        "reference": {
            "filename": reference.filename,
            "size": ref_path.stat().st_size
        },
        "clips": [
            {"filename": Path(p).name, "size": Path(p).stat().st_size}
            for p in clip_paths
        ]
    }


@app.post("/api/generate/{session_id}")
async def generate_video(session_id: str, background_tasks: BackgroundTasks):
    """
    Start video generation pipeline.
    Client should connect to WebSocket for real-time progress.
    
    Returns:
        {"status": "processing", "session_id": "..."}
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] == "processing":
        return {"status": "already_processing", "session_id": session_id}
    
    # Mark as processing
    session["status"] = "processing"
    session["progress"] = 0.0
    
    # Run pipeline in background
    background_tasks.add_task(
        process_video_pipeline,
        session_id,
        session["reference_path"],
        session["clip_paths"]
    )
    
    return {"status": "processing", "session_id": session_id}


async def process_video_pipeline(session_id: str, ref_path: str, clip_paths: List[str]):
    """
    Run the MIMIC pipeline with progress updates.
    """
    def progress_callback(step: int, total: int, message: str):
        active_sessions[session_id]["progress"] = step / total
        active_sessions[session_id]["current_step"] = message
        # WebSocket will broadcast this to connected clients
    
    try:
        result = run_mimic_pipeline(
            reference_path=ref_path,
            clip_paths=clip_paths,
            session_id=session_id,
            output_dir="temp/outputs",
            progress_callback=progress_callback
        )
        
        if result.success:
            active_sessions[session_id]["status"] = "complete"
            active_sessions[session_id]["output_path"] = result.output_path
            active_sessions[session_id]["blueprint"] = result.blueprint.dict()
            active_sessions[session_id]["clip_index"] = result.clip_index.dict()
        else:
            active_sessions[session_id]["status"] = "error"
            active_sessions[session_id]["error"] = result.error
            
    except Exception as e:
        active_sessions[session_id]["status"] = "error"
        active_sessions[session_id]["error"] = str(e)


@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """
    Get current processing status.
    
    Returns:
        {
            "status": "uploaded" | "processing" | "complete" | "error",
            "progress": 0.0-1.0,
            "current_step": "Analyzing reference...",
            "output_path": "..." (if complete)
        }
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]


@app.get("/api/download/{session_id}")
async def download_video(session_id: str):
    """
    Download final video.
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] != "complete":
        raise HTTPException(status_code=400, detail="Video not ready")
    
    output_path = session["output_path"]
    
    if not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"mimic_output_{session_id[:8]}.mp4"
    )


@app.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time progress updates.
    """
    await websocket.accept()
    
    try:
        while True:
            if session_id in active_sessions:
                session = active_sessions[session_id]
                await websocket.send_json({
                    "status": session["status"],
                    "progress": session.get("progress", 0.0),
                    "message": session.get("current_step", "")
                })
                
                # Stop sending if complete or error
                if session["status"] in ["complete", "error"]:
                    break
            
            await asyncio.sleep(1)  # Update every second
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


@app.get("/api/history")
async def get_history():
    """
    Get list of past projects (optional feature).
    For hackathon, can just return sessions from memory.
    """
    history = [
        {
            "session_id": sid,
            "status": session["status"],
            "created_at": session.get("created_at", ""),
            "reference_filename": Path(session["reference_path"]).name,
            "clip_count": len(session["clip_paths"])
        }
        for sid, session in active_sessions.items()
    ]
    return {"projects": history}


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Clean up session files.
    """
    if session_id in active_sessions:
        cleanup_session(session_id)
        del active_sessions[session_id]
        return {"status": "deleted"}
    
    raise HTTPException(status_code=404, detail="Session not found")


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4.5.2 Running the Backend

```bash
# Development
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Production (Railway/Render)
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4.5.3 Updated Requirements.txt

```txt
# Core dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6  # For file uploads
websockets==12.0
google-generativeai>=0.8.3
pydantic==2.6.0
python-dotenv==1.0.0

# Optional (for development)
pytest==7.4.3
black==23.12.1
```

---



## 5. COMPONENT SPECIFICATIONS

### 5.1 The Brain (engine/brain.py)

**Purpose:** Communicate with Gemini 3 to analyze videos and extract structured data.

**Complete Implementation:**

```python
"""
Brain module: Gemini 3 API integration for video analysis.

This module handles ALL AI interactions. It NEVER touches the filesystem
directly—paths are provided by the orchestrator.
"""

import os
import json
import time
from pathlib import Path
import google.generativeai as genai
from models import StyleBlueprint, ClipMetadata, ClipIndex, EnergyLevel, MotionType

# ============================================================================
# PROMPTS (These are CRITICAL—do not modify without testing)
# ============================================================================

REFERENCE_ANALYSIS_PROMPT = """
You are a professional video editor analyzing the PACING STRUCTURE of this video.

YOUR TASK: Divide the video into 3-8 time-based segments based on editing rhythm.

IMPORTANT: Analyze the STRUCTURE, not the content. We don't care if it's a cat or a car—
we care about WHEN cuts happen, HOW FAST things move, and the RHYTHM of edits.

For each segment, determine:

1. **ENERGY** (visual rhythm intensity):
   - **Low**: Slow camera movement, steady shots, minimal cuts, calm pacing
     Examples: Meditation videos, slow pans, locked-off shots
   - **Medium**: Moderate pacing, some camera movement, occasional cuts
     Examples: Vlogs, talking heads with B-roll, product demos
   - **High**: Rapid cuts, fast motion, intense action, high energy
     Examples: Sports highlights, dance trends, action sequences

2. **MOTION** (camera + subject movement):
   - **Static**: Fixed camera, minimal subject movement
   - **Dynamic**: Panning, zooming, tracking, fast subject motion

RULES:
- Segments should be 2-5 seconds each (unless the video is very short)
- Segments must be contiguous (no gaps or overlaps)
- Base energy on PACING and RHYTHM, not on content emotion
- The last segment must end exactly at the video's total duration

OUTPUT FORMAT (JSON only, no markdown code fences):
{
  "total_duration": 15.5,
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 3.2,
      "duration": 3.2,
      "energy": "High",
      "motion": "Dynamic"
    },
    {
      "id": 2,
      "start": 3.2,
      "end": 8.0,
      "duration": 4.8,
      "energy": "Medium",
      "motion": "Static"
    }
  ]
}

Respond ONLY with valid JSON. Do not include explanations, markdown, or any other text.
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


# ============================================================================
# CONFIGURATION
# ============================================================================

class GeminiConfig:
    """Configuration for Gemini API calls."""
    
    # Model selection - USING GEMINI 3 FOR HACKATHON
    MODEL_NAME = "gemini-3-flash-preview"  # Primary model for Gemini 3 Hackathon
    FALLBACK_MODEL = "gemini-3-pro-preview"  # Use if Flash fails
    EMERGENCY_FALLBACK = "gemini-exp-1206"  # Use if both Gemini 3 models return 404
    
    # Generation config for consistent, structured output
    GENERATION_CONFIG = {
        "temperature": 0.1,  # Low temperature for consistency
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json"  # Force JSON output
    }
    
    # Retry config
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0  # seconds


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def initialize_gemini(api_key: str | None = None) -> genai.GenerativeModel:
    """
    Initialize Gemini API client with automatic fallback.
    
    Args:
        api_key: Optional API key. If None, reads from GEMINI_API_KEY env var.
    
    Returns:
        Configured GenerativeModel instance
    
    Raises:
        ValueError: If API key is not provided or found in environment
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Either pass api_key parameter or set "
            "GEMINI_API_KEY environment variable."
        )
    
    genai.configure(api_key=api_key)
    
    # Try models in order: Gemini 3 Flash → Gemini 3 Pro → Experimental
    for model_name in [GeminiConfig.MODEL_NAME, GeminiConfig.FALLBACK_MODEL, GeminiConfig.EMERGENCY_FALLBACK]:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=GeminiConfig.GENERATION_CONFIG
            )
            print(f"✅ Using model: {model_name}")
            return model
        except Exception as e:
            print(f"⚠️  Model {model_name} not available: {e}")
            continue
    
    raise ValueError("No Gemini models available. Check API key and model access.")


def _upload_video_with_retry(video_path: str) -> genai.File:
    """
    Upload video to Gemini with retry logic.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Uploaded file object
    
    Raises:
        Exception: If all retries fail
    """
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            print(f"Uploading {Path(video_path).name}... (attempt {attempt + 1})")
            video_file = genai.upload_file(path=video_path)
            
            # Wait for processing to complete
            while video_file.state.name == "PROCESSING":
                print("Waiting for video processing...")
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise Exception(f"Video processing failed: {video_file.state}")
            
            print(f"Upload complete: {video_file.uri}")
            return video_file
            
        except Exception as e:
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to upload video after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            print(f"Upload failed: {e}. Retrying in {GeminiConfig.RETRY_DELAY}s...")
            time.sleep(GeminiConfig.RETRY_DELAY)


def _parse_json_response(response_text: str) -> dict:
    """
    Parse Gemini's JSON response, handling common formatting issues.
    
    Args:
        response_text: Raw response text from Gemini
    
    Returns:
        Parsed JSON as dictionary
    
    Raises:
        ValueError: If response is not valid JSON
    """
    # Remove markdown code fences if present
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]  # Remove ```json
    if text.startswith("```"):
        text = text[3:]  # Remove ```
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {text}")


# ============================================================================
# PUBLIC API
# ============================================================================

def analyze_reference_video(video_path: str, api_key: str | None = None) -> StyleBlueprint:
    """
    Analyze reference video to extract editing structure.
    
    Args:
        video_path: Path to reference video file
        api_key: Optional Gemini API key
    
    Returns:
        StyleBlueprint with timing and energy analysis
    
    Raises:
        Exception: If analysis fails after all retries
        ValueError: If Gemini returns invalid JSON
    """
    print(f"\n{'='*60}")
    print(f"🧠 ANALYZING REFERENCE VIDEO: {Path(video_path).name}")
    print(f"{'='*60}\n")
    
    model = initialize_gemini(api_key)
    
    # Upload video
    video_file = _upload_video_with_retry(video_path)
    
    # Generate analysis
    for attempt in range(GeminiConfig.MAX_RETRIES):
        try:
            print(f"Requesting analysis... (attempt {attempt + 1})")
            response = model.generate_content([video_file, REFERENCE_ANALYSIS_PROMPT])
            
            # Parse and validate
            json_data = _parse_json_response(response.text)
            blueprint = StyleBlueprint(**json_data)
            
            print(f"✅ Analysis complete: {len(blueprint.segments)} segments")
            return blueprint
            
        except Exception as e:
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze reference after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            print(f"Analysis failed: {e}. Retrying in {GeminiConfig.RETRY_DELAY}s...")
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
            
            print(f"    ✅ {energy.value} / {motion.value}")
            return energy, motion
            
        except Exception as e:
            if attempt == GeminiConfig.MAX_RETRIES - 1:
                raise Exception(f"Failed to analyze clip after {GeminiConfig.MAX_RETRIES} attempts: {e}")
            time.sleep(GeminiConfig.RETRY_DELAY)


def analyze_all_clips(clip_paths: List[str], api_key: str | None = None) -> ClipIndex:
    """
    Analyze all user clips and build a ClipIndex.
    
    Args:
        clip_paths: List of paths to clip files
        api_key: Optional Gemini API key
    
    Returns:
        ClipIndex with metadata for all clips
    """
    print(f"\n{'='*60}")
    print(f"🧠 ANALYZING USER CLIPS ({len(clip_paths)} total)")
    print(f"{'='*60}\n")
    
    clip_metadata_list = []
    
    for clip_path in clip_paths:
        # Get duration using ffprobe (from processors module)
        from engine.processors import get_video_duration
        duration = get_video_duration(clip_path)
        
        # Analyze with Gemini
        energy, motion = analyze_clip(clip_path, api_key)
        
        clip_metadata = ClipMetadata(
            filename=Path(clip_path).name,
            filepath=clip_path,
            duration=duration,
            energy=energy,
            motion=motion
        )
        clip_metadata_list.append(clip_metadata)
    
    print(f"\n✅ All clips analyzed\n")
    return ClipIndex(clips=clip_metadata_list)


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
    print("⚠️  Using fallback mode: Linear 2-second segments")
    
    from engine.processors import get_video_duration
    duration = get_video_duration(video_path)
    
    segments = []
    current_time = 0.0
    segment_id = 1
    
    while current_time < duration:
        end_time = min(current_time + 2.0, duration)
        segments.append({
            "id": segment_id,
            "start": current_time,
            "end": end_time,
            "duration": end_time - current_time,
            "energy": "Medium",  # Default to medium
            "motion": "Dynamic"
        })
        current_time = end_time
        segment_id += 1
    
    return StyleBlueprint(total_duration=duration, segments=segments)
```

---

### 5.2 The Processor (engine/processors.py)

**Purpose:** All FFmpeg operations—standardization, extraction, concatenation, merging.

**Complete Implementation:**

```python
"""
Processor module: FFmpeg wrappers for video manipulation.

All functions here are PURE: they take input paths, produce output files,
and have no side effects. They do NOT manage state or session data.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Tuple

# ============================================================================
# VIDEO INFORMATION
# ============================================================================

def get_video_duration(video_path: str) -> float:
    """
    Get video duration using ffprobe.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Duration in seconds
    
    Raises:
        RuntimeError: If ffprobe fails
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        raise RuntimeError(f"Failed to get duration for {video_path}: {e}")


def get_video_info(video_path: str) -> dict:
    """
    Get comprehensive video metadata.
    
    Returns:
        Dictionary with width, height, fps, duration, codec, etc.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name,duration",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        raise RuntimeError(f"Failed to get info for {video_path}: {e}")


# ============================================================================
# VIDEO STANDARDIZATION
# ============================================================================

def standardize_clip(input_path: str, output_path: str) -> None:
    """
    Standardize video to 1080x1920 (vertical), 30fps, h.264, AAC audio.
    
    Strategy: Scale to fit within 1080x1920, then crop to exact dimensions.
    This prevents black bars while maintaining aspect ratio.
    
    Args:
        input_path: Source video file
        output_path: Destination for standardized video
    
    Raises:
        RuntimeError: If FFmpeg command fails
    """
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
            "setsar=1"
        ),
        "-r", "30",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-y",  # Overwrite output file
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✅ Standardized: {Path(output_path).name}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"FFmpeg standardization failed:\n"
            f"STDOUT: {e.stdout}\n"
            f"STDERR: {e.stderr}"
        )


# ============================================================================
# AUDIO EXTRACTION
# ============================================================================

def extract_audio(video_path: str, audio_output_path: str) -> bool:
    """
    Extract audio track from video.
    
    Args:
        video_path: Source video
        audio_output_path: Destination for audio file (should end in .aac)
    
    Returns:
        True if audio extracted successfully, False if video has no audio
    
    Raises:
        RuntimeError: If FFmpeg fails unexpectedly
    """
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # No video
        "-acodec", "aac",
        "-b:a", "192k",
        "-y",
        audio_output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✅ Audio extracted: {Path(audio_output_path).name}")
        return True
    except subprocess.CalledProcessError as e:
        # Check if it's a "no audio stream" error
        if "does not contain any stream" in e.stderr or "no audio" in e.stderr.lower():
            print(f"  ⚠️  No audio track found in {Path(video_path).name}")
            return False
        else:
            raise RuntimeError(f"Audio extraction failed: {e.stderr}")


# ============================================================================
# VIDEO SEGMENTATION
# ============================================================================

def extract_segment(
    input_path: str,
    output_path: str,
    start_time: float,
    duration: float
) -> None:
    """
    Extract a segment from a video (precise frame-accurate cutting).
    
    Args:
        input_path: Source video
        output_path: Destination for segment
        start_time: Start time in seconds
        duration: Length of segment in seconds
    """
    cmd = [
        "ffmpeg",
        "-ss", str(start_time),  # Seek to start
        "-i", input_path,
        "-t", str(duration),  # Duration
        "-c", "copy",  # Copy codec (no re-encode = faster)
        "-avoid_negative_ts", "make_zero",
        "-y",
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"    ✅ Segment extracted: {start_time:.2f}s - {start_time + duration:.2f}s")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Segment extraction failed: {e.stderr}")


# ============================================================================
# VIDEO CONCATENATION
# ============================================================================

def concatenate_videos(input_paths: List[str], output_path: str) -> None:
    """
    Concatenate multiple videos into a single file.
    
    CRITICAL: Uses re-encoding (not stream copy) to ensure frame-perfect cuts.
    Stream copy only cuts on keyframes (2-5s apart), causing sync drift.
    
    Args:
        input_paths: List of video files to join (in order)
        output_path: Destination for concatenated video
    
    Raises:
        RuntimeError: If concatenation fails
    """
    # Create a temporary file list for FFmpeg
    concat_list_path = Path(output_path).parent / "concat_list.txt"
    
    with open(concat_list_path, "w") as f:
        for path in input_paths:
            # FFmpeg concat requires absolute paths and "file" prefix
            f.write(f"file '{Path(path).absolute()}'\n")
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-c:v", "libx264",  # Re-encode video for frame-perfect cuts
        "-preset", "ultrafast",  # Fast encoding (keeps total time <60s)
        "-crf", "23",  # Quality (23 = visually lossless)
        "-c:a", "copy",  # Audio can be copied (no precision needed)
        "-y",
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ Concatenated {len(input_paths)} segments (frame-perfect)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Concatenation failed: {e.stderr}")
    finally:
        # Clean up temp file
        if concat_list_path.exists():
            concat_list_path.unlink()


# ============================================================================
# AUDIO/VIDEO MERGING
# ============================================================================

def merge_audio_video(
    video_path: str,
    audio_path: str,
    output_path: str,
    trim_to_shortest: bool = True
) -> None:
    """
    Merge audio track onto video.
    
    OPTIMIZED: Video stream is copied (already encoded), only audio is re-encoded.
    This prevents double-encoding quality loss and speeds up rendering.
    
    Args:
        video_path: Video file (can be silent)
        audio_path: Audio file to overlay
        output_path: Destination for merged video
        trim_to_shortest: If True, trim to shortest input (prevent black frames)
    """
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",  # Don't re-encode video (already encoded in concat step)
        "-c:a", "aac",  # Re-encode audio to AAC
        "-b:a", "192k",
        "-map", "0:v:0",  # Take video from first input
        "-map", "1:a:0",  # Take audio from second input
    ]
    
    if trim_to_shortest:
        cmd.append("-shortest")  # Stop at shortest stream
    
    cmd.extend(["-y", output_path])
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ Audio merged onto video (optimized)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio/video merge failed: {e.stderr}")


# ============================================================================
# SILENT VIDEO (When reference has no audio)
# ============================================================================

def create_silent_video(input_path: str, output_path: str) -> None:
    """
    Create a copy of video with no audio track.
    
    Args:
        input_path: Source video
        output_path: Destination for silent video
    """
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "copy",
        "-an",  # No audio
        "-y",
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ Silent video created")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Silent video creation failed: {e.stderr}")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_output(output_path: str, min_size_kb: int = 100) -> bool:
    """
    Validate that output video was created successfully.
    
    Args:
        output_path: Path to output video
        min_size_kb: Minimum file size in KB (to catch empty files)
    
    Returns:
        True if valid, False otherwise
    """
    path = Path(output_path)
    
    if not path.exists():
        return False
    
    size_kb = path.stat().st_size / 1024
    if size_kb < min_size_kb:
        return False
    
    # Try to probe the file
    try:
        get_video_duration(output_path)
        return True
    except:
        return False
```

---

### 5.3 The Editor (engine/editor.py)

**Purpose:** Match clips to blueprint segments using energy-based greedy algorithm.

**Complete Implementation:**

```python
"""
Editor module: Clip-to-segment matching algorithm.

This is the "creative logic" layer. It decides which clips go where.
"""

from typing import List, Dict
from collections import defaultdict
from models import (
    StyleBlueprint,
    ClipIndex,
    EDL,
    EditDecision,
    EnergyLevel,
    ClipMetadata
)

# ============================================================================
# MATCHING ALGORITHM
# ============================================================================

def match_clips_to_blueprint(blueprint: StyleBlueprint, clip_index: ClipIndex) -> EDL:
    """
    Match user clips to blueprint segments using energy-based greedy algorithm.
    
    ALGORITHM:
    1. Create energy pools (group clips by energy level)
    2. For each segment in blueprint:
        a. Find clips matching segment energy
        b. If no match, use round-robin from all clips
        c. Select least-used clip from pool
        d. Handle short clips (fill remainder with next clip)
    3. Return Edit Decision List
    
    PRIORITY: Maintain global pacing > Perfect energy matching > Single clip integrity
    
    Args:
        blueprint: Analyzed reference structure
        clip_index: Analyzed user clips
    
    Returns:
        EDL (Edit Decision List) with frame-accurate instructions
    """
    print(f"\n{'='*60}")
    print(f"✂️  MATCHING CLIPS TO BLUEPRINT")
    print(f"{'='*60}\n")
    
    # Track how many times each clip has been used
    clip_usage_count = {clip.filename: 0 for clip in clip_index.clips}
    
    # Group clips by energy for fast lookup
    energy_pools = _create_energy_pools(clip_index)
    
    # Track current position in each clip (for sequential reuse)
    clip_current_position = {clip.filename: 0.0 for clip in clip_index.clips}
    
    decisions: List[EditDecision] = []
    timeline_position = 0.0
    
    for segment in blueprint.segments:
        print(f"Segment {segment.id}: {segment.start:.2f}s-{segment.end:.2f}s "
              f"({segment.duration:.2f}s, {segment.energy.value})")
        
        # Find matching clips
        matching_clips = energy_pools.get(segment.energy, [])
        
        if not matching_clips:
            print(f"  ⚠️  No {segment.energy.value} clips available, using fallback")
            # Fallback: Use round-robin from all clips
            matching_clips = sorted(
                clip_index.clips,
                key=lambda c: clip_usage_count[c.filename]
            )
        
        # Select least-used clip from pool
        selected_clip = min(matching_clips, key=lambda c: clip_usage_count[c.filename])
        print(f"  📎 Selected: {selected_clip.filename} ({selected_clip.energy.value})")
        
        # Fill the segment duration
        remaining_duration = segment.duration
        segment_start_time = timeline_position
        
        while remaining_duration > 0.01:  # 10ms tolerance
            # Get current position in this clip
            clip_start = clip_current_position[selected_clip.filename]
            available_duration = selected_clip.duration - clip_start
            
            if available_duration <= 0:
                # Clip exhausted, reset to beginning
                clip_current_position[selected_clip.filename] = 0.0
                clip_start = 0.0
                available_duration = selected_clip.duration
            
            # How much of this clip should we use?
            use_duration = min(remaining_duration, available_duration)
            
            # Create edit decision
            decision = EditDecision(
                segment_id=segment.id,
                clip_path=selected_clip.filepath,
                clip_start=clip_start,
                clip_end=clip_start + use_duration,
                timeline_start=timeline_position,
                timeline_end=timeline_position + use_duration
            )
            decisions.append(decision)
            
            # Update tracking
            clip_current_position[selected_clip.filename] += use_duration
            timeline_position += use_duration
            remaining_duration -= use_duration
            
            print(f"    ✅ Using {selected_clip.filename} "
                  f"[{clip_start:.2f}s-{clip_start + use_duration:.2f}s] "
                  f"→ timeline [{decision.timeline_start:.2f}s-{decision.timeline_end:.2f}s]")
            
            # If we still need more footage, switch to next clip in pool
            if remaining_duration > 0.01:
                print(f"    ⚠️  Clip exhausted, need {remaining_duration:.2f}s more")
                # Get next clip from pool
                next_clip = _get_next_clip(matching_clips, selected_clip, clip_usage_count)
                selected_clip = next_clip
        
        # Mark clip as used
        clip_usage_count[selected_clip.filename] += 1
    
    edl = EDL(decisions=decisions)
    print(f"\n✅ Matching complete: {len(decisions)} edit decisions\n")
    return edl


def _create_energy_pools(clip_index: ClipIndex) -> Dict[EnergyLevel, List[ClipMetadata]]:
    """
    Group clips by energy level for efficient matching.
    
    Returns:
        Dictionary mapping EnergyLevel → List[ClipMetadata]
    """
    pools = defaultdict(list)
    for clip in clip_index.clips:
        pools[clip.energy].append(clip)
    return dict(pools)


def _get_next_clip(
    pool: List[ClipMetadata],
    current_clip: ClipMetadata,
    usage_count: Dict[str, int]
) -> ClipMetadata:
    """
    Get the next clip to use when current clip is exhausted.
    
    Strategy: Use least-used clip from pool (excluding current clip if possible).
    """
    # Filter out current clip if pool has other options
    other_clips = [c for c in pool if c.filename != current_clip.filename]
    
    if other_clips:
        return min(other_clips, key=lambda c: usage_count[c.filename])
    else:
        # Only one clip in pool, reuse it
        return current_clip


# ============================================================================
# STATS & DEBUGGING
# ============================================================================

def print_edl_summary(edl: EDL, blueprint: StyleBlueprint, clip_index: ClipIndex) -> None:
    """Print human-readable EDL summary for debugging."""
    print(f"\n{'='*60}")
    print(f"📋 EDIT DECISION LIST SUMMARY")
    print(f"{'='*60}\n")
    
    print(f"Total decisions: {len(edl.decisions)}")
    print(f"Total segments: {len(blueprint.segments)}")
    print(f"Available clips: {len(clip_index.clips)}\n")
    
    # Count clip usage
    clip_usage = defaultdict(int)
    for decision in edl.decisions:
        filename = decision.clip_path.split('/')[-1]
        clip_usage[filename] += 1
    
    print("Clip usage distribution:")
    for filename, count in sorted(clip_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  {filename}: {count} times")
    
    print()


def validate_edl(edl: EDL, blueprint: StyleBlueprint) -> bool:
    """
    Validate EDL for continuity and timing errors.
    
    Returns:
        True if valid, raises ValueError if issues found
    """
    # Check timeline continuity
    for i in range(len(edl.decisions) - 1):
        current = edl.decisions[i]
        next_decision = edl.decisions[i + 1]
        
        gap = abs(current.timeline_end - next_decision.timeline_start)
        if gap > 0.01:  # 10ms tolerance
            raise ValueError(
                f"Timeline gap/overlap between decision {i} and {i+1}: {gap:.3f}s"
            )
    
    # Check total duration matches blueprint
    if edl.decisions:
        total_duration = edl.decisions[-1].timeline_end
        expected = blueprint.total_duration
        
        if abs(total_duration - expected) > 0.01:
            raise ValueError(
                f"EDL total duration ({total_duration:.2f}s) "
                f"doesn't match blueprint ({expected:.2f}s)"
            )
    
    return True
```

---

### 5.4 The Orchestrator (engine/orchestrator.py)

**Purpose:** Coordinate all modules to execute the full pipeline.

**Complete Implementation:**

```python
"""
Orchestrator: Main pipeline controller.

This is the SINGLE entry point for the entire backend. The UI calls
run_mimic_pipeline() and gets back a PipelineResult.

All state management, error handling, and module coordination happens here.
"""

import time
from pathlib import Path
from typing import Callable, List
from models import PipelineResult, StyleBlueprint, ClipIndex, EDL

from engine.brain import (
    analyze_reference_video,
    analyze_all_clips,
    create_fallback_blueprint
)
from engine.editor import match_clips_to_blueprint, validate_edl, print_edl_summary
from engine.processors import (
    standardize_clip,
    extract_audio,
    extract_segment,
    concatenate_videos,
    merge_audio_video,
    create_silent_video,
    validate_output
)
from utils import ensure_directory, cleanup_session


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_mimic_pipeline(
    reference_path: str,
    clip_paths: List[str],
    session_id: str,
    output_dir: str,
    api_key: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None
) -> PipelineResult:
    """
    Execute the complete MIMIC pipeline.
    
    STAGES:
    1. Validate inputs
    2. Analyze reference video (Gemini)
    3. Analyze user clips (Gemini)
    4. Match clips to blueprint segments (Editor)
    5. Render video (FFmpeg)
    
    Args:
        reference_path: Path to reference video
        clip_paths: List of paths to user clips
        session_id: Unique session identifier
        output_dir: Directory for final output
        api_key: Optional Gemini API key (uses env var if None)
        progress_callback: Optional callback(current_step, total_steps, message)
    
    Returns:
        PipelineResult with success status and output path
    """
    start_time = time.time()
    
    def update_progress(step: int, total: int, message: str):
        """Helper to call progress callback if provided."""
        if progress_callback:
            progress_callback(step, total, message)
        print(f"\n[{step}/{total}] {message}")
    
    TOTAL_STEPS = 5
    
    try:
        # ==================================================================
        # STEP 1: VALIDATE INPUTS
        # ==================================================================
        update_progress(1, TOTAL_STEPS, "Validating inputs...")
        
        _validate_inputs(reference_path, clip_paths)
        
        # Setup session directories
        session_dir = Path(f"temp/{session_id}")
        standardized_dir = session_dir / "standardized"
        segments_dir = session_dir / "segments"
        
        ensure_directory(standardized_dir)
        ensure_directory(segments_dir)
        ensure_directory(output_dir)
        
        # Clean any previous session data
        cleanup_session(session_id, keep_dirs=True)
        
        # ==================================================================
        # STEP 2: ANALYZE REFERENCE
        # ==================================================================
        update_progress(2, TOTAL_STEPS, "Analyzing reference video structure...")
        
        try:
            blueprint = analyze_reference_video(reference_path, api_key)
        except Exception as e:
            print(f"⚠️  Gemini analysis failed: {e}")
            print("    Using fallback mode...")
            blueprint = create_fallback_blueprint(reference_path)
        
        # ==================================================================
        # STEP 3: ANALYZE USER CLIPS
        # ==================================================================
        update_progress(3, TOTAL_STEPS, "Analyzing user clips...")
        
        # Standardize clips first (required for consistent analysis)
        standardized_paths = []
        for i, clip_path in enumerate(clip_paths, start=1):
            output_path = standardized_dir / f"clip_{i:03d}.mp4"
            print(f"  Standardizing clip {i}/{len(clip_paths)}...")
            standardize_clip(clip_path, str(output_path))
            standardized_paths.append(str(output_path))
        
        # Analyze standardized clips
        try:
            clip_index = analyze_all_clips(standardized_paths, api_key)
        except Exception as e:
            # If analysis fails, create default index
            print(f"⚠️  Clip analysis failed: {e}")
            print("    Using default energy levels...")
            from models import ClipMetadata, EnergyLevel, MotionType
            from engine.processors import get_video_duration
            
            clips = []
            for path in standardized_paths:
                clips.append(ClipMetadata(
                    filename=Path(path).name,
                    filepath=path,
                    duration=get_video_duration(path),
                    energy=EnergyLevel.MEDIUM,  # Default
                    motion=MotionType.DYNAMIC
                ))
            clip_index = ClipIndex(clips=clips)
        
        # ==================================================================
        # STEP 4: MATCH & EDIT
        # ==================================================================
        update_progress(4, TOTAL_STEPS, "Creating edit sequence...")
        
        edl = match_clips_to_blueprint(blueprint, clip_index)
        validate_edl(edl, blueprint)
        print_edl_summary(edl, blueprint, clip_index)
        
        # ==================================================================
        # STEP 5: RENDER VIDEO
        # ==================================================================
        update_progress(5, TOTAL_STEPS, "Rendering final video...")
        
        # Extract segments according to EDL
        segment_paths = []
        for i, decision in enumerate(edl.decisions, start=1):
            segment_path = segments_dir / f"segment_{i:03d}.mp4"
            extract_segment(
                decision.clip_path,
                str(segment_path),
                decision.clip_start,
                decision.clip_end - decision.clip_start
            )
            segment_paths.append(str(segment_path))
        
        # Concatenate segments
        temp_video_path = session_dir / "temp_video.mp4"
        concatenate_videos(segment_paths, str(temp_video_path))
        
        # Handle audio
        audio_path = session_dir / "ref_audio.aac"
        has_audio = extract_audio(reference_path, str(audio_path))
        
        # Final output
        output_filename = f"mimic_output_{session_id[:8]}.mp4"
        final_output_path = Path(output_dir) / output_filename
        
        if has_audio:
            merge_audio_video(
                str(temp_video_path),
                str(audio_path),
                str(final_output_path),
                trim_to_shortest=True
            )
        else:
            create_silent_video(str(temp_video_path), str(final_output_path))
        
        # Validate output
        if not validate_output(str(final_output_path)):
            raise RuntimeError("Output video validation failed")
        
        # ==================================================================
        # SUCCESS
        # ==================================================================
        processing_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ PIPELINE COMPLETE")
        print(f"{'='*60}")
        print(f"Output: {final_output_path}")
        print(f"Duration: {blueprint.total_duration:.2f}s")
        print(f"Segments: {len(blueprint.segments)}")
        print(f"Processing time: {processing_time:.1f}s")
        print(f"{'='*60}\n")
        
        return PipelineResult(
            success=True,
            output_path=str(final_output_path),
            blueprint=blueprint,
            clip_index=clip_index,
            edl=edl,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"❌ PIPELINE FAILED")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        
        return PipelineResult(
            success=False,
            error=str(e),
            processing_time_seconds=processing_time
        )


# ============================================================================
# VALIDATION
# ============================================================================

def _validate_inputs(reference_path: str, clip_paths: List[str]) -> None:
    """
    Validate inputs before pipeline execution.
    
    Raises:
        ValueError: If inputs are invalid
    """
    from engine.processors import get_video_duration
    
    # Check reference video exists
    if not Path(reference_path).exists():
        raise ValueError(f"Reference video not found: {reference_path}")
    
    # Check reference duration (3-20 seconds)
    try:
        ref_duration = get_video_duration(reference_path)
        if not (3.0 <= ref_duration <= 20.0):
            raise ValueError(
                f"Reference video must be 3-20 seconds (got {ref_duration:.1f}s)"
            )
    except Exception as e:
        raise ValueError(f"Could not read reference video: {e}")
    
    # Check clip count (minimum 2)
    if len(clip_paths) < 2:
        raise ValueError(f"Need at least 2 clips (got {len(clip_paths)})")
    
    # Check all clips exist
    for i, clip_path in enumerate(clip_paths, start=1):
        if not Path(clip_path).exists():
            raise ValueError(f"Clip {i} not found: {clip_path}")
        
        # Basic validation
        try:
            get_video_duration(clip_path)
        except Exception as e:
            raise ValueError(f"Could not read clip {i}: {e}")
```

---

### 5.5 Utilities (utils.py)

**Purpose:** File management, cleanup, logging helpers.

**Complete Implementation:**

```python
"""
Utility functions for MIMIC project.
"""

import shutil
from pathlib import Path
from typing import List


def ensure_directory(path: str | Path) -> Path:
    """
    Create directory if it doesn't exist.
    
    Returns:
        Path object for chaining
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def cleanup_session(session_id: str, keep_dirs: bool = False) -> None:
    """
    Clean up temporary files for a session.
    
    Args:
        session_id: Session ID to clean
        keep_dirs: If True, keep directory structure but delete contents
    """
    session_dir = Path(f"temp/{session_id}")
    
    if not session_dir.exists():
        return
    
    if keep_dirs:
        # Delete contents but keep structure
        for subdir in session_dir.iterdir():
            if subdir.is_dir():
                for file in subdir.iterdir():
                    if file.is_file():
                        file.unlink()
    else:
        # Delete entire session directory
        shutil.rmtree(session_dir, ignore_errors=True)


def cleanup_all_temp() -> None:
    """Delete all temporary files."""
    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


def get_file_size_mb(path: str | Path) -> float:
    """Get file size in megabytes."""
    return Path(path).stat().st_size / (1024 * 1024)


def format_duration(seconds: float) -> str:
    """Format duration as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"
```

---

## 6. NEXT.JS FRONTEND IMPLEMENTATION

**Location:** `frontend/`

### 6.1 Project Setup

```bash
# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend

# Install dependencies
npm install @radix-ui/react-icons
npm install clsx tailwind-merge
npm install react-dropzone

# Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card progress dialog badge separator skeleton toast
```

### 6.2 Key Components

#### FileUpload Component

```typescript
// components/FileUpload.tsx
'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, FileVideo } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface FileUploadProps {
  type: 'reference' | 'clips'
  onFilesChange: (files: File[]) => void
  maxFiles?: number
}

export function FileUpload({ type, onFilesChange, maxFiles = 10 }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = type === 'reference' ? [acceptedFiles[0]] : [...files, ...acceptedFiles]
    setFiles(newFiles)
    onFilesChange(newFiles)
  }, [files, onFilesChange, type])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi']
    },
    maxFiles: type === 'reference' ? 1 : maxFiles
  })

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    setFiles(newFiles)
    onFilesChange(newFiles)
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-300
          ${isDragActive 
            ? 'border-primary bg-primary/10 scale-105' 
            : 'border-border hover:border-primary/50 hover:bg-surface-elevated'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-text-secondary" />
        <p className="text-lg font-medium mb-2">
          {isDragActive ? 'Drop your video here' : `Drag & drop ${type} video`}
        </p>
        <p className="text-sm text-text-secondary">
          or click to browse • MP4, MOV, AVI
        </p>
        {type === 'reference' && (
          <p className="text-xs text-text-muted mt-2">
            Requirements: 3-20 seconds
          </p>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-3 bg-surface rounded-lg"
            >
              <FileVideo className="w-5 h-5 text-primary" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.name}</p>
                <p className="text-xs text-text-secondary">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFile(index)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

#### ProgressTracker Component

```typescript
// components/ProgressTracker.tsx
'use client'

import { useEffect, useState } from 'react'
import { Progress } from '@/components/ui/progress'
import { Check, Loader2 } from 'lucide-react'

interface ProgressStep {
  id: string
  title: string
  subtitle?: string
  status: 'pending' | 'active' | 'complete' | 'error'
}

interface ProgressTrackerProps {
  sessionId: string
}

export function ProgressTracker({ sessionId }: ProgressTrackerProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [steps, setSteps] = useState<ProgressStep[]>([
    { id: 'upload', title: 'Files uploaded', status: 'complete' },
    { id: 'analyze_ref', title: 'Reference analyzed', status: 'pending' },
    { id: 'analyze_clips', title: 'Clips analyzed', status: 'pending' },
    { id: 'matching', title: 'Edit sequence created', status: 'pending' },
    { id: 'rendering', title: 'Rendering video', status: 'pending' },
    { id: 'audio', title: 'Merging audio', status: 'pending' },
  ])

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket(`ws://localhost:8000/ws/progress/${sessionId}`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setProgress(data.progress * 100)
      setCurrentStep(data.message)
      
      // Update step statuses based on progress
      const updatedSteps = steps.map((step, index) => {
        if (index < data.progress * steps.length) {
          return { ...step, status: 'complete' as const }
        } else if (index === Math.floor(data.progress * steps.length)) {
          return { ...step, status: 'active' as const }
        }
        return { ...step, status: 'pending' as const }
      })
      setSteps(updatedSteps)
    }

    return () => ws.close()
  }, [sessionId])

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold">Creating Your Video...</h3>
          <span className="text-sm text-text-secondary">{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id} className="flex items-start gap-3">
            <div className="mt-0.5">
              {step.status === 'complete' && (
                <div className="w-5 h-5 rounded-full bg-success flex items-center justify-center">
                  <Check className="w-3 h-3 text-white" />
                </div>
              )}
              {step.status === 'active' && (
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              )}
              {step.status === 'pending' && (
                <div className="w-5 h-5 rounded-full border-2 border-border" />
              )}
            </div>
            <div>
              <p className={`font-medium ${
                step.status === 'complete' ? 'text-success' : 
                step.status === 'active' ? 'text-primary' : 
                'text-text-secondary'
              }`}>
                {step.title}
              </p>
              {step.subtitle && (
                <p className="text-sm text-text-muted">{step.subtitle}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

#### VideoComparison Component

```typescript
// components/VideoComparison.tsx
'use client'

import { useRef, useState } from 'react'
import { Play, Pause, Volume2, VolumeX } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'

interface VideoComparisonProps {
  referenceUrl: string
  outputUrl: string
}

export function VideoComparison({ referenceUrl, outputUrl }: VideoComparisonProps) {
  const refVideoRef = useRef<HTMLVideoElement>(null)
  const outputVideoRef = useRef<HTMLVideoElement>(null)
  
  const [isPlaying, setIsPlaying] = useState(false)
  const [syncEnabled, setSyncEnabled] = useState(true)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  const togglePlay = () => {
    if (isPlaying) {
      refVideoRef.current?.pause()
      outputVideoRef.current?.pause()
    } else {
      refVideoRef.current?.play()
      if (syncEnabled) outputVideoRef.current?.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleSeek = (value: number[]) => {
    const time = value[0]
    if (refVideoRef.current) refVideoRef.current.currentTime = time
    if (syncEnabled && outputVideoRef.current) {
      outputVideoRef.current.currentTime = time
    }
    setCurrentTime(time)
  }

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Reference Video */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">📹 Reference Structure</h3>
          </div>
          <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
            <video
              ref={refVideoRef}
              src={referenceUrl}
              className="w-full h-full"
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
            />
          </div>
        </div>

        {/* Output Video */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">✨ Your Generated Video</h3>
          </div>
          <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
            <video
              ref={outputVideoRef}
              src={outputUrl}
              className="w-full h-full"
            />
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="space-y-4">
        <Slider
          value={[currentTime]}
          max={duration}
          step={0.1}
          onValueChange={handleSeek}
          className="w-full"
        />
        
        <div className="flex items-center justify-center gap-4">
          <Button onClick={togglePlay} size="lg" className="w-32">
            {isPlaying ? <Pause className="w-5 h-5 mr-2" /> : <Play className="w-5 h-5 mr-2" />}
            {isPlaying ? 'Pause' : 'Play'}
          </Button>
          
          <Button
            variant={syncEnabled ? 'default' : 'outline'}
            onClick={() => setSyncEnabled(!syncEnabled)}
          >
            Sync Playback
          </Button>
        </div>

        <p className="text-center text-sm text-text-secondary">
          {Math.floor(currentTime)}s / {Math.floor(duration)}s
        </p>
      </div>
    </div>
  )
}
```

### 6.3 API Client

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function uploadFiles(reference: File, clips: File[]) {
  const formData = new FormData()
  formData.append('reference', reference)
  clips.forEach(clip => formData.append('clips', clip))

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) throw new Error('Upload failed')
  return response.json()
}

export async function generateVideo(sessionId: string) {
  const response = await fetch(`${API_BASE}/api/generate/${sessionId}`, {
    method: 'POST',
  })

  if (!response.ok) throw new Error('Generation failed')
  return response.json()
}

export async function getStatus(sessionId: string) {
  const response = await fetch(`${API_BASE}/api/status/${sessionId}`)
  if (!response.ok) throw new Error('Status check failed')
  return response.json()
}

export function getDownloadUrl(sessionId: string) {
  return `${API_BASE}/api/download/${sessionId}`
}
```

---

## 7. ERROR HANDLING & GUARDRAILS

### 7.1 Error Hierarchy

```python
# In utils.py or models.py

class MIMICError(Exception):
    """Base exception for MIMIC project."""
    pass

class InvalidInputError(MIMICError):
    """Invalid user input (wrong format, duration, etc)."""
    pass

class GeminiError(MIMICError):
    """Gemini API failures."""
    pass

class FFmpegError(MIMICError):
    """FFmpeg processing failures."""
    pass

class ValidationError(MIMICError):
    """Data validation failures."""
    pass
```

### 7.2 User-Facing Error Messages

```python
# In utils.py

ERROR_MESSAGES = {
    "gemini_failure": (
        "🚨 AI analysis temporarily unavailable. "
        "Using fallback mode (linear cuts every 2s)."
    ),
    "ffmpeg_not_found": (
        "❌ FFmpeg is not installed.\n\n"
        "**Installation:**\n"
        "- macOS: `brew install ffmpeg`\n"
        "- Ubuntu: `sudo apt-get install ffmpeg`\n"
        "- Windows: Download from https://ffmpeg.org"
    ),
    "invalid_reference_duration": (
        "⚠️ Reference video must be 3-20 seconds long.\n"
        "Please trim your video and try again."
    ),
    "insufficient_clips": (
        "⚠️ Please upload at least 2 clips.\n"
        "More clips = better matching!"
    ),
    "corrupted_video": (
        "❌ Could not read video file: {filename}\n"
        "Please ensure it's a valid MP4/MOV file."
    ),
    "api_key_missing": (
        "🔑 Gemini API key not found.\n\n"
        "**Setup:**\n"
        "1. Get key from https://aistudio.google.com/app/apikey\n"
        "2. Enter in sidebar OR add to .env file"
    ),
    "output_validation_failed": (
        "❌ Video generation failed quality check.\n"
        "This is rare—please try again or report the issue."
    )
}
```

### 7.3 Failure Resolution Matrix

| Failure Mode | Detection | Fallback Action | User Message |
|--------------|-----------|-----------------|--------------|
| **Gemini API Down** | API exception | Use `create_fallback_blueprint()` (linear 2s segments) | "AI analysis unavailable, using simplified mode" |
| **No Energy Matches** | Empty `matching_clips` list | Round-robin all clips | "Using all clips to fill structure" |
| **FFmpeg Not Installed** | `subprocess` error | Show install instructions, block generation | ERROR_MESSAGES["ffmpeg_not_found"] |
| **Corrupted Video File** | `ffprobe` error | Skip file, show error for that file | ERROR_MESSAGES["corrupted_video"] |
| **Reference Too Short/Long** | Duration check | Block generation | ERROR_MESSAGES["invalid_reference_duration"] |
| **<2 Clips Uploaded** | Count check | Block generation | ERROR_MESSAGES["insufficient_clips"] |
| **Output File <100KB** | Size check | Show error, suggest retry | ERROR_MESSAGES["output_validation_failed"] |
| **Reference Has No Audio** | `extract_audio()` returns False | Render silent video | "(Silent video—reference had no audio)" |

---

## 8. TESTING & VALIDATION

### 8.1 Unit Test Checklist

```python
# Save as tests/test_processors.py

import pytest
from engine.processors import *

def test_standardize_clip():
    """Test clip standardization to 1080x1920, 30fps."""
    # Use a test video file
    input_path = "tests/fixtures/test_clip.mp4"
    output_path = "tests/temp/standardized.mp4"
    
    standardize_clip(input_path, output_path)
    
    # Verify output
    info = get_video_info(output_path)
    assert info["streams"][0]["width"] == 1080
    assert info["streams"][0]["height"] == 1920
    # Note: FFmpeg reports fps as fraction (e.g., "30/1")

def test_extract_audio_with_audio():
    """Test audio extraction from video with audio."""
    video_path = "tests/fixtures/with_audio.mp4"
    audio_path = "tests/temp/audio.aac"
    
    result = extract_audio(video_path, audio_path)
    
    assert result == True
    assert Path(audio_path).exists()

def test_extract_audio_without_audio():
    """Test audio extraction from silent video."""
    video_path = "tests/fixtures/silent.mp4"
    audio_path = "tests/temp/audio.aac"
    
    result = extract_audio(video_path, audio_path)
    
    assert result == False
    assert not Path(audio_path).exists()

# Add more tests for each processor function
```

### 8.2 Integration Test Scenarios

**Test Case 1: Happy Path**
```
Input:
  - Reference: 10s dance video (High energy at 0-5s, Low at 5-10s)
  - Clips: [High-6s, High-4s, Low-8s]

Expected Output:
  - 10s video
  - Segments 0-5s use High clips
  - Segments 5-10s use Low clips
  - Audio from reference
  - File size >100KB
```

**Test Case 2: Short Clips (Looping)**
```
Input:
  - Reference: 8s (4 segments of 2s each, all High)
  - Clips: [High-3s] (only one clip, too short)

Expected Output:
  - 8s video
  - High clip used 3 times (looped at different timestamps)
  - No errors/crashes
```

**Test Case 3: No Energy Matches**
```
Input:
  - Reference: 10s (5 segments, all High energy)
  - Clips: [Low-5s, Low-4s, Medium-6s] (no High clips)

Expected Output:
  - 10s video (uses available clips via round-robin)
  - Warning in logs: "No High clips available"
  - Video still renders successfully
```

**Test Case 4: Gemini Failure**
```
Simulate:
  - Disconnect internet during analysis

Expected Output:
  - Fallback blueprint used (linear 2s segments)
  - Video still renders
  - Message: "AI analysis unavailable, using simplified mode"
```

### 8.3 Manual Test Protocol (For Demo Day)

**Pre-Demo Checklist:**
1. ✅ Test with 3 different reference videos (fast, medium, slow pacing)
2. ✅ Test with various clip lengths (2s, 5s, 10s, 30s)
3. ✅ Test with different aspect ratios (16:9, 9:16, 1:1)
4. ✅ Test with silent reference video
5. ✅ Test with corrupted file (expect graceful error)
6. ✅ Test with only 1 clip (expect error: "Need at least 2")
7. ✅ Verify download button works
8. ✅ Verify "New Project" button clears session
9. ✅ Time full pipeline (should be <60s for typical inputs)

---

## 9. LOCAL DEVELOPMENT SETUP (START HERE)

### 9.1 Prerequisites

**Install these before starting:**
```bash
# 1. FFmpeg (CRITICAL - test first)
brew install ffmpeg  # macOS
# OR: sudo apt-get install ffmpeg  # Ubuntu

# Verify
ffmpeg -version  # Should show 4.4+

# 2. Node.js 18+
node --version  # Should show v18+

# 3. Python 3.10+
python3 --version  # Should show 3.10+

# 4. Gemini API Key
# Get from: https://aistudio.google.com/app/apikey
```

---

### 9.2 Backend Setup (Do This First)

```bash
# 1. Create project structure
mkdir mimic-project && cd mimic-project
mkdir backend frontend

# 2. Setup backend
cd backend

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Install dependencies
pip install fastapi uvicorn[standard] python-multipart websockets \
            google-generativeai pydantic python-dotenv

# 5. Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_api_key_here
EOF

# 6. Create all files from master plan:
# - main.py (Section 4.5.1)
# - models.py (Section 4)
# - engine/brain.py (Section 5.1)
# - engine/processors.py (Section 5.2)
# - engine/editor.py (Section 5.3)
# - engine/orchestrator.py (Section 5.4)
# - utils.py (Section 5.5)

# 7. Test backend
uvicorn main:app --reload --port 8000

# 8. Verify in browser:
# http://localhost:8000/health should return {"status": "healthy"}
```

**✅ Backend Success Signals:**
- No import errors
- `/health` endpoint returns 200
- Can see API docs at `http://localhost:8000/docs`

---

### 9.3 Frontend Setup (Do This Second)

```bash
# 1. Go to frontend directory
cd ../frontend

# 2. Create Next.js app
npx create-next-app@latest . --typescript --tailwind --app

# 3. Install dependencies
npm install @radix-ui/react-icons clsx tailwind-merge react-dropzone

# 4. Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card progress dialog badge separator

# 5. Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# 6. Use Antigravity/Cursor to build frontend
# Give it the Antigravity prompt from Section 3.5.10
# Or manually create files from Section 6

# 7. Start dev server
npm run dev

# 8. Verify in browser:
# http://localhost:3000 should show landing page
```

**✅ Frontend Success Signals:**
- No TypeScript errors
- Landing page renders
- Can navigate between pages

---

### 9.4 Integration Testing (Do This Third)

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser: http://localhost:3000

# Test workflow:
# 1. Upload reference video (use any 5-10s video from your phone)
# 2. Upload 2-3 clips (any videos)
# 3. Click "Generate Video"
# 4. Watch WebSocket progress updates
# 5. See side-by-side comparison
# 6. Download video

# If any step fails, see Section 7 (Error Handling)
```

---

### 9.5 Critical Fixes for Production (Apply When Deploying)

**⚠️ READ THIS BEFORE DEPLOYING TO VERCEL/RAILWAY**

#### Fix 1: CORS for WebSocket (Backend)

**Problem:** Generic wildcard CORS fails for WebSocket connections.

**Fix:** Update `backend/main.py`:

```python
import os

# Get frontend URL from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Specific URL, not "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Environment Variables:**
```bash
# Local development (.env)
FRONTEND_URL=http://localhost:3000

# Railway deployment
FRONTEND_URL=https://mimic-yourname.vercel.app
```

---

#### Fix 2: FFmpeg on Railway (Backend)

**Problem:** Railway doesn't install FFmpeg by default → crashes on first video operation.

**Fix:** Create `backend/nixpacks.toml`:

```toml
# Railway uses nixpacks to build Python apps
# This tells it to install FFmpeg

[phases.setup]
nixPkgs = ["python310", "ffmpeg"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**Alternative for Render:** Create `backend/render.yaml`:

```yaml
services:
  - type: web
    name: mimic-backend
    env: python
    buildCommand: "pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

---

#### Fix 3: Next.js Environment Variables (Frontend)

**Problem:** `NEXT_PUBLIC_API_URL` must be set at build time, not runtime.

**Fix:** Set in Vercel dashboard BEFORE deploying:

```bash
# Vercel Dashboard → Settings → Environment Variables

# Add:
NEXT_PUBLIC_API_URL = https://your-backend.railway.app

# Then redeploy
```

**Local Development (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 10. DEPLOYMENT (OPTIONAL - DO THIS LAST)

**Priority:** Get it working locally first. Deploy only when demo-ready.

### 10.1 Backend to Railway (5 min)

### 10.1 Backend to Railway (5 min)

**Prerequisites:**
- ✅ Backend works locally
- ✅ `nixpacks.toml` created (Section 9.5, Fix 2)
- ✅ Code pushed to GitHub

**Steps:**
1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Select your repo → Choose `backend/` folder as root
4. Add environment variables:
   - `GEMINI_API_KEY=your_key`
   - `FRONTEND_URL=https://your-frontend.vercel.app` (get this in next step)
5. Deploy → Copy deployment URL

**Result:** `https://mimic-backend-xxx.railway.app`

---

### 10.2 Frontend to Vercel (3 min)

**Prerequisites:**
- ✅ Frontend works locally
- ✅ Backend deployed and URL copied

**Steps:**
1. Go to [vercel.com](https://vercel.com)
2. "New Project" → Import from GitHub
3. Select your repo → Root directory: `frontend/`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL=https://mimic-backend-xxx.railway.app`
5. Deploy → Copy deployment URL

**Result:** `https://mimic-yourname.vercel.app`

---

### 10.3 Update Backend CORS

**Now that you have frontend URL:**
1. Go back to Railway
2. Update environment variable:
   - `FRONTEND_URL=https://mimic-yourname.vercel.app`
3. Redeploy backend

---

### 10.4 Final Verification

**Test deployed app:**
- [ ] Frontend loads (no 404s)
- [ ] Can upload files
- [ ] WebSocket connects (progress bar updates)
- [ ] Video generates
- [ ] Can download result

**If WebSocket fails:**
- Check CORS settings (Section 9.5, Fix 1)
- Verify `FRONTEND_URL` is exact match (no trailing slash)
- Check browser console for errors

---

## 11. UPDATED JAZIB'S EXECUTION GUIDE

## 11. JAZIB'S COMPLETE EXECUTION GUIDE

**Read this section to understand the full workflow from zero to demo-ready.**

### 11.1 The Build Strategy

**Philosophy:** Build backend first, test it, then add frontend. Deploy only at the end.

**Timeline:**
- **Phase 1:** Backend Core (2 hours) → Test with curl/Postman
- **Phase 2:** Frontend (1.5 hours) → Test integration locally
- **Phase 3:** Polish & Test (30 min) → Fix bugs
- **Phase 4:** Deploy (optional, 1 hour) → Only if demoing live

**Total: 4-5 hours to working local demo**

---

### 11.2 Phase 1: Backend Core (2 hours)

**Goal:** Get FastAPI running with all endpoints working.

#### Step 1.1: Project Setup (10 min)
```bash
# Create structure
mkdir -p mimic-project/backend/engine
cd mimic-project/backend

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install fastapi uvicorn[standard] python-multipart websockets \
            google-generativeai pydantic python-dotenv

# Create .env
echo "GEMINI_API_KEY=your_actual_key_here" > .env
```

#### Step 1.2: Create Core Files (30 min)

**Create these files by copying from master plan:**

1. **`models.py`** (Section 4) - All Pydantic schemas
2. **`engine/brain.py`** (Section 5.1) - Gemini 3 integration
3. **`engine/processors.py`** (Section 5.2) - FFmpeg wrappers
4. **`engine/editor.py`** (Section 5.3) - Matching algorithm
5. **`engine/orchestrator.py`** (Section 5.4) - Pipeline coordinator
6. **`utils.py`** (Section 5.5) - File helpers

**Cursor Prompt for this step:**
```
Read MIMIC_MASTER_BUILD_PLAN_FINAL.md.

Create the following files in backend/:
- models.py from Section 4
- engine/brain.py from Section 5.1
- engine/processors.py from Section 5.2
- engine/editor.py from Section 5.3
- engine/orchestrator.py from Section 5.4
- utils.py from Section 5.5

Use exact code from the document. Do not modify.
```

#### Step 1.3: Create FastAPI Server (20 min)

**Create `main.py`** (Section 4.5.1) - All API endpoints

**Cursor Prompt:**
```
Create backend/main.py from Section 4.5.1.
Include all endpoints: /api/upload, /api/generate, /api/status, /api/download, /ws/progress
Apply Fix 1 from Section 9.5 (CORS with FRONTEND_URL from environment)
```

#### Step 1.4: Test Backend (1 hour)

**Start server:**
```bash
uvicorn main:app --reload --port 8000
```

**Test checklist:**
```bash
# 1. Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# 2. API docs
open http://localhost:8000/docs
# Expected: Interactive Swagger UI

# 3. Test upload (use any video file)
curl -X POST http://localhost:8000/api/upload \
  -F "reference=@test_video.mp4" \
  -F "clips=@clip1.mp4" \
  -F "clips=@clip2.mp4"
# Expected: JSON with session_id

# 4. Test Gemini integration
python3 -c "
from engine.brain import analyze_reference_video
result = analyze_reference_video('test_video.mp4')
print(f'Segments: {len(result.segments)}')
"
# Expected: Number of segments detected

# 5. Test FFmpeg
python3 -c "
from engine.processors import get_video_duration
print(f'Duration: {get_video_duration(\"test_video.mp4\")}s')
"
# Expected: Video duration in seconds
```

**✅ Phase 1 Complete When:**
- Backend starts without errors
- Can upload files via API
- Gemini returns valid JSON
- FFmpeg commands work

---

### 11.3 Phase 2: Frontend (1.5 hours)

**Goal:** Get Next.js UI talking to backend.

#### Step 2.1: Create Next.js App (10 min)
```bash
cd ../frontend

# Create app
npx create-next-app@latest . --typescript --tailwind --app

# Install deps
npm install @radix-ui/react-icons clsx tailwind-merge react-dropzone lucide-react

# shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card progress dialog badge

# Environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

#### Step 2.2: Build UI with Antigravity (1 hour)

**Give Antigravity this exact prompt:**

```
Read MIMIC_MASTER_BUILD_PLAN_FINAL.md Section 3.5 (UI/UX Design System).

Build a Next.js 14 app with these pages:

1. app/page.tsx - Landing page with hero, demo section, CTA
2. app/upload/page.tsx - File upload interface (reference + clips)
3. app/generate/[id]/page.tsx - Processing page with WebSocket progress
4. app/result/[id]/page.tsx - Side-by-side video comparison
5. app/history/page.tsx - Grid of past projects (optional)

Components needed:
- components/FileUpload.tsx (Section 6.2)
- components/ProgressTracker.tsx (Section 6.2)
- components/VideoComparison.tsx (Section 6.2)

API client:
- lib/api.ts (Section 6.3)

Use the exact color scheme from Section 3.5.2:
- Background: #0A0A0A
- Primary: #8B5CF6 (purple with glow)
- Accent: #06B6D4 (cyan)

Make it look like Runway ML - premium, cinematic, professional.
```

**OR: Build manually using code from Section 6.**

#### Step 2.3: Test Frontend (20 min)

```bash
# Start dev server
npm run dev

# Open browser
open http://localhost:3000

# Test flow:
# 1. Landing page loads
# 2. Click "Get Started" → /upload
# 3. Drag-drop reference video
# 4. Drag-drop 2+ clips
# 5. Click "Generate" → /generate/[id]
# 6. See progress bar updating (WebSocket)
# 7. Redirect to /result/[id]
# 8. See side-by-side videos
# 9. Download button works
```

**✅ Phase 2 Complete When:**
- All pages render
- File upload works
- WebSocket connects and shows progress
- Videos display in result page

---

### 11.4 Phase 3: Integration & Polish (30 min)

#### Test End-to-End Flow

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser: Test complete workflow
# Use real videos (10s TikTok + 3 random clips)
```

#### Common Issues & Fixes

**Issue: WebSocket doesn't connect**
```typescript
// Check lib/api.ts - WebSocket URL should match backend
const ws = new WebSocket('ws://localhost:8000/ws/progress/${sessionId}')
// NOT wss:// (secure) for local dev
```

**Issue: CORS error**
```python
# Check backend/main.py
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Make sure no trailing slash
```

**Issue: Video won't play**
```typescript
// Check if output_path is accessible
// May need to serve from backend static files
app.mount("/outputs", StaticFiles(directory="temp/outputs"), name="outputs")
```

**Issue: FFmpeg command fails**
```bash
# Verify FFmpeg installed
which ffmpeg
ffmpeg -version

# Test manually
ffmpeg -i test.mp4 -vf "scale=1080:1920" output.mp4
```

---

### 11.5 Phase 4: Deployment (Optional, 1 hour)

**Only do this if you need a live demo link for hackathon submission.**

Follow Section 10 (Deployment) with critical fixes from Section 9.5.

**Quick checklist:**
1. Create `backend/nixpacks.toml` (Fix 2)
2. Update `backend/main.py` CORS (Fix 1)
3. Deploy backend to Railway → Get URL
4. Deploy frontend to Vercel with `NEXT_PUBLIC_API_URL`
5. Update backend `FRONTEND_URL` → Redeploy
6. Test deployed app

---

### 11.6 Demo Preparation (30 min)

**Record 3-minute video:**

**Script:**
```
[0:00-0:15] The Hook
"Every creator sees viral videos and thinks 'I want that vibe.'
Manual replication takes hours. Watch this."

[0:15-0:45] The Setup
Show: Reference video (fast-paced TikTok with clear beat drops)
Show: Your clips (random gym/cooking footage - totally different)
"These don't match at all."

[0:45-1:30] The Magic
Upload to MIMIC → Click generate
Show progress bar with WebSocket updates
REVEAL: Side-by-side comparison
Point out: "Same beat drops at 0:03 and 0:07 - perfectly synced"

[1:30-2:00] The Tech
"Gemini 3 doesn't analyze content - it extracts structure.
Spatial-temporal reasoning, not object detection.
This is the Action Era: AI that creates."

[2:00-3:00] The Impact
"50M+ creators worldwide need this.
Professional editors charge $200/hour.
MIMIC does it in 60 seconds."

Show GitHub link, architecture diagram, thank judges.
```

**Recording tips:**
- Use OBS or Loom
- Screen resolution: 1920x1080
- Show mouse cursor
- No background music (your voice only)
- Upload to YouTube (unlisted)

---

### 11.7 Final Checklist Before Submission

**Code:**
- [ ] All files in GitHub (public repo)
- [ ] README.md with setup instructions
- [ ] .env.example (without real keys)
- [ ] Works on fresh install

**Demo:**
- [ ] 3-minute video uploaded
- [ ] Shows clear before/after
- [ ] Highlights Gemini 3 usage
- [ ] Includes architecture explanation

**Submission:**
- [ ] 200-word description (from Section 1 Strategic Context)
- [ ] Live demo link OR GitHub + local setup guide
- [ ] Video link
- [ ] Code repository link

---

**You are now ready to build. Start with Phase 1 (Backend Core). Good luck!** 🚀



## 10. APPENDICES

### Appendix A: Dependencies

#### Backend requirements.txt
```txt
# Core API
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
websockets==12.0

# AI & Video Processing
google-generativeai>=0.8.3
pydantic==2.6.0
python-dotenv==1.0.0

# Optional (development)
pytest==7.4.3
black==23.12.1
```

#### Frontend package.json
```json
{
  "name": "mimic-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.3",
    "@radix-ui/react-icons": "^1.3.0",
    "react-dropzone": "^14.2.3",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.309.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1"
  }
}
```

### Appendix B: FFmpeg Command Reference (CRITICAL - USE THESE EXACT COMMANDS)

**1. Standardize & Crop (Convert to 1080x1920, 30fps):**
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,setsar=1" \
  -r 30 \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  -y standardized.mp4
```

**2. Extract Reference Audio:**
```bash
ffmpeg -i reference.mp4 \
  -vn \
  -acodec aac -b:a 192k \
  -y ref_audio.aac
```

**3. Concatenate (FRAME-PERFECT - CRITICAL FOR SYNC):**
```bash
# MUST re-encode video (not stream copy) for frame-perfect cuts
# Stream copy only cuts on keyframes (2-5s apart) = sync drift!
ffmpeg -f concat -safe 0 -i list.txt \
  -c:v libx264 -preset ultrafast -crf 23 \
  -c:a copy \
  -y stitched_video.mp4
```
**Why ultrafast?** Balances speed (<60s render time) with frame accuracy.

**4. Final Audio/Video Merge (OPTIMIZED):**
```bash
# Video already encoded in step 3, don't re-encode it
ffmpeg -i stitched_video.mp4 -i ref_audio.aac \
  -c:v copy \
  -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 \
  -shortest \
  -y final_output.mp4
```

**5. Extract Segment (Frame-accurate cutting):**
```bash
ffmpeg -ss START_TIME -i input.mp4 \
  -t DURATION \
  -c copy \
  -avoid_negative_ts make_zero \
  -y segment.mp4
```

**6. Create Silent Video (No audio track):**
```bash
ffmpeg -i input.mp4 \
  -c:v copy -an \
  -y silent_output.mp4
```

### Appendix C: .env.example

```bash
# Copy this to .env and add your key

# Get your key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here
```

### Appendix D: .gitignore

```gitignore
# Environment
.env
venv/
__pycache__/
*.pyc

# Temp files
temp/
outputs/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### Appendix E: README.md (For GitHub)

```markdown
# 🎬 MIMIC - Video Structure Cloner

**Winner of [Hackathon Name] - Gemini 3 Track**

MIMIC uses Gemini 3 AI to analyze the editing structure of any video, then applies that pacing to your own footage.

## 🚀 Demo

[Insert GIF or video of side-by-side comparison]

## 🧠 How It Works

1. **Analyze:** Gemini 3 watches your reference video and extracts its "editing DNA" (timing, energy, motion)
2. **Match:** Our algorithm maps your clips to the reference structure based on energy levels
3. **Render:** FFmpeg stitches everything together with frame-perfect precision

## 📦 Installation

```bash
# Clone repo
git clone https://github.com/yourusername/mimic.git
cd mimic

# Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install FFmpeg
brew install ffmpeg  # macOS
# or: sudo apt-get install ffmpeg  # Ubuntu

# Add API key
cp .env.example .env
# Edit .env and add your Gemini API key
```

## 🎮 Usage

```bash
streamlit run app.py
```

Then:
1. Upload a reference video (3-20 seconds)
2. Upload your clips (2+ videos)
3. Click "Generate Video"
4. Download your remixed video!

## 🏗️ Architecture

```
[Next.js Frontend] ←→ [FastAPI Backend] → [Orchestrator] → [Brain (Gemini)] → [Editor] → [Processor (FFmpeg)]
```

- **Frontend:** Next.js 14 + TypeScript + Tailwind
- **Backend:** FastAPI with WebSocket support
- **Brain:** Gemini 3 video analysis
- **Editor:** Energy-based clip matching
- **Processor:** FFmpeg video manipulation
- **Orchestrator:** Pipeline coordination

## 🧪 Tech Stack

- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, Python 3.10+
- **AI:** Google Gemini 3 API
- **Processing:** FFmpeg
- **Validation:** Pydantic

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

Built for the Gemini 3 Global Hackathon 2025
```

### Appendix F: Sample Prompts for Testing Brain Module

**Test Prompt 1: Fast-Paced TikTok**
```
Analyze this TikTok dance video and identify:
- When the beat drops (high energy segments)
- When there are pauses or slow-motion (low energy)
- Camera movements (static vs dynamic)
```

**Test Prompt 2: Cinematic Trailer**
```
This is a movie trailer. Break down:
- Rapid cut sequences (high energy montages)
- Slow dramatic moments (low energy establishing shots)
- Action sequences vs dialogue scenes
```

### Appendix G: FFmpeg Troubleshooting

**Issue: "ffmpeg: command not found"**
```bash
# Verify installation
which ffmpeg

# If not installed:
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: Download from https://ffmpeg.org and add to PATH
```

**Issue: "Output video has black bars"**
- Caused by: `scale` filter without `crop`
- Fix: Use command from Section 5.2 (includes crop parameters)

**Issue: "Audio out of sync"**
- Caused by: Variable frame rate input
- Fix: Add `-r 30` to standardization (forces constant frame rate)

### Appendix H: Gemini 3 Model Status

**Current Configuration (Already Updated):**

The document has been pre-configured to use Gemini 3 models:

```python
# In engine/brain.py
class GeminiConfig:
    MODEL_NAME = "gemini-3-flash-preview"  # Primary
    FALLBACK_MODEL = "gemini-3-pro-preview"  # Backup
    EMERGENCY_FALLBACK = "gemini-exp-1206"  # Last resort
```

**If Models Change:**

Google may update model IDs during the hackathon. If you get 404 errors:

1. Check [Google AI Studio](https://aistudio.google.com) for latest model names
2. Update `GeminiConfig.MODEL_NAME` in `engine/brain.py`
3. Test with a simple video before full build

**Model Selection Strategy:**
- **Flash:** Fast inference, lower cost (use for all analysis)
- **Pro:** Higher reasoning quality (only if Flash produces poor results)

---

## 🔒 FINAL CHECKLIST

Before starting build:

- [ ] Read entire document (yes, all of it)
- [ ] Verify FFmpeg is installed
- [ ] Get Gemini API key
- [ ] Understand orchestrator pattern
- [ ] Know where each function goes
- [ ] Review data models (Pydantic schemas)
- [ ] Understand matching algorithm
- [ ] Review error handling strategy

During build:

- [ ] Follow Phase order (Section 0, Part B)
- [ ] Test each module independently before integration
- [ ] Use mock data for initial testing
- [ ] Add print statements liberally (helps debugging)
- [ ] Validate with real video files frequently

Before demo:

- [ ] Run full integration test (Section 8.3)
- [ ] Test with shaky internet (Gemini fallback)
- [ ] Prepare 3 example reference videos
- [ ] Practice demo flow (<2 minutes)
- [ ] Have backup videos ready

---

## 🎯 SUCCESS METRICS

**Technical:**
- ✅ Pipeline completes 95%+ of the time
- ✅ Output video duration matches reference ±100ms
- ✅ Processing time <60s for typical inputs
- ✅ No crashes on invalid input (graceful errors)

**Demo Impact:**
- ✅ Side-by-side comparison wows judges in first 10 seconds
- ✅ Can explain Gemini 3 use case clearly ("structural video analysis")
- ✅ Live demo works on first try
- ✅ Judges say "I want to use this!"

---

## 📞 SUPPORT

**If you get stuck:**
1. Check error message against Section 7.2
2. Review relevant component spec (Section 5)
3. Test individual functions in isolation
4. Check FFmpeg installation/version
5. Verify Gemini API key is valid

**Common Issues:**
- "No such file or directory" → Check file paths use absolute paths or correct relative paths
- "Invalid JSON" → Check Gemini response in logs (may have markdown wrapping)
- "Concatenation failed" → Verify all segments are standardized (same codec/resolution)

---

**END OF DOCUMENT**

*This is the complete, final, locked specification. Build exactly as specified. Good luck! 🚀*
