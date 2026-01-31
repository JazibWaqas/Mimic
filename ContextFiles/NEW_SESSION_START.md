# 🎬 MIMIC - New Session Onboarding

**Welcome to MIMIC V11.0 - The Collaborative Director**  
**Last Updated:** February 1, 2026  
**Status:** Production Ready / Demo Grade

---

## 🎯 What is MIMIC?

MIMIC is an **AI-powered video style transfer system** that analyzes a reference video's editing style (cuts, pacing, energy, narrative arc) and automatically recreates that style using your raw clips.

Think: **"Instagram Reels editor that understands the 'why' behind professional edits."**

### The Core Innovation
MIMIC is not a black box. It's a **whitebox collaborative director** that:
1. **Analyzes** your reference video's "Editorial DNA"
2. **Plans** a strategic approach based on your clip library
3. **Executes** the edit with narrative intelligence
4. **Reflects** on the result with a detailed critique
5. **Advises** on how to reach "Director's Cut" quality

---

## 🏗️ System Architecture (7-Stage Pipeline)

```
Stage 1: Pre-Analysis → Scene cuts, BPM detection, clip standardization
Stage 2: Reference Analysis → Energy, motion, vibes, narrative arc (Gemini)
Stage 3: Clip Analysis → Semantic metadata, best moments (Gemini)
Stage 4: Strategic Planning → Editorial guidance, library assessment (Gemini Advisor)
Stage 5: Semantic Editing → Narrative-aware clip matching with subject locking
Stage 6: Aesthetic Styling → Typography, color grading, text rendering
Stage 7: Post-Render Reflection → AI critique with remake strategy
```

---

## ✨ Key Features (What Makes It Special)

### 1. **Narrative Intelligence**
- **Subject Locking:** If reference says "friends," system enforces People-Group clips (+200 bonus)
- **Emotional Capital:** Tracks clip usage to prevent "star" clip fatigue
- **Arc-Aware Matching:** Different strategies for Intro/Build-up/Peak/Outro

### 2. **Whitebox Transparency**
- **Editorial Debrief:** See exactly what worked, what was compromised, and why
- **Constraint Gaps:** System identifies missing content types
- **Remake Strategy:** AI provides specific advice for next iteration

### 3. **Production Quality**
- **100% Diversity:** Zero clip repetitions in demo mode
- **Beat-Perfect Sync:** <0.015s deviation from musical anchors
- **Adaptive Rhythm:** Respects cinematic holds while maintaining energy
- **Demo-Safe Rendering:** 0% crash rate with hardened FFmpeg filters

### 4. **Performance**
- **15-20 second** total time for 30-segment edits (with cache)
- **100% cache hit rate** on repeat runs
- **28-key API rotation** for high-throughput demos

---

## 📁 Project Structure (What's Where)

```
Mimic/
├── backend/
│   ├── engine/
│   │   ├── orchestrator.py    # 7-stage pipeline controller
│   │   ├── brain.py            # Gemini multimodal analysis
│   │   ├── gemini_advisor.py   # Strategic planning & critique
│   │   ├── editor.py           # Narrative-aware matching
│   │   ├── stylist.py          # Aesthetic post-processing
│   │   └── processors.py       # FFmpeg + librosa wrappers
│   ├── models.py               # Pydantic schemas (SOURCE OF TRUTH)
│   └── main.py                 # FastAPI server
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Studio (upload + generate)
│   │   ├── vault/page.tsx      # Asset browser + intelligence
│   │   ├── gallery/page.tsx    # Clip library
│   │   └── history/page.tsx    # Session history
│   └── lib/
│       ├── api.ts              # API client
│       └── types.ts            # TypeScript interfaces
├── data/
│   ├── cache/                  # Analysis + standardized clips
│   ├── results/                # Generated videos + JSON intelligence
│   └── samples/                # Reference videos + clip library
└── ContextFiles/               # Extended documentation
```

---

## 🚀 Quick Start (3 Steps)

### 1. Start Backend
```powershell
cd backend
.venv\Scripts\activate
python main.py
```

### 2. Start Frontend
```powershell
cd frontend
npm run dev
```

### 3. Open Browser
Navigate to `http://localhost:3000`

---

## 🎨 The Workflow (How Users Interact)

### Studio Page (Upload + Generate)
1. **Upload Reference:** Drag-drop a professionally edited video
2. **Upload Clips:** Add your raw footage (36 clips recommended)
3. **Generate:** Click "Start MIMIC" and watch real-time progress
4. **Navigate to Vault:** Auto-redirected when complete

### Vault Page (Review + Refine)
1. **View Result:** See your generated video with intelligence overlay
2. **Read Debrief:** Understand editorial decisions and tradeoffs
3. **Check Remake Strategy:** Get specific advice for improvement
4. **Refine:** Click "Remake Video" to iterate with new clips

---

## 🔑 Key Concepts (For Understanding the Code)

### 1. **Content-Based Hashing**
- Files identified by content hash, not filename
- Enables deduplication and cache inheritance
- Format: `std_{hash}.mp4`, `clip_comprehensive_{hash}.json`

### 2. **Pydantic Models**
- `models.py` is the **single source of truth** for data structures
- All data validated at boundaries
- Backend and frontend share same schema

### 3. **Graceful Degradation**
- Advisor can fail without breaking pipeline
- Falls back to base matcher (energy + motion only)
- Always produces a result, even with constraints

### 4. **Session State**
- In-memory by design (single-user workflow)
- Durable artifacts on disk (videos, JSON, thumbnails)
- Recovery via filesystem scan, not memory

---

## 📊 Current Status (V11.0)

| Component | Status | Confidence |
|-----------|--------|------------|
| Reference Analysis | ✅ Complete | 98% |
| Clip Analysis | ✅ Complete | 98% |
| Strategic Advisor | ✅ Complete | 98% |
| Semantic Editor | ✅ Complete | 100% |
| Aesthetic Stylist | ✅ Complete | 98% |
| Post-Render Reflection | ✅ Complete | 95% |
| Vault Dashboard | ✅ Complete | 98% |

**Overall:** 🏆 **Production Ready / Demo Grade**

---

## 🔧 Recent Improvements (Feb 1, 2026)

### Production Hardening
- ✅ File extension validation (`.mp4` only)
- ✅ Environment variable support (`NEXT_PUBLIC_API_URL`)
- ✅ API response consistency (`path` field unified)
- ✅ Thumbnail infrastructure verified (all asset types)

### Bug Fixes
- ✅ Orchestrator AttributeError (Pydantic model access)
- ✅ Type safety improvements (TypeScript interfaces)
- ✅ URL configuration (no hardcoded localhost)

---

## 📚 Documentation Map

| File | Purpose |
|------|---------|
| **README.md** | Project overview + quick start |
| **STATUS.md** | Current state + quality metrics |
| **ARCHITECTURE.md** | Technical deep dive (7 stages) |
| **MIMIC_QUICK_REFERENCE.md** | One-page cheat sheet |
| **PRODUCTION_FIXES.md** | Recent hardening changes |
| **ONBOARDING.md** | First-time setup guide |

---

## 🎯 What to Focus On (For New Contributors)

### If You're Reviewing Code:
1. **Start with `models.py`** - Understand data structures first
2. **Read `orchestrator.py`** - See the 7-stage pipeline flow
3. **Check `editor.py`** - Core matching algorithm with narrative intelligence
4. **Review `vault/page.tsx`** - Frontend intelligence display

### If You're Testing:
1. **Run `test_ref.py`** - Quick end-to-end test
2. **Check `data/results/`** - See generated videos + JSON
3. **Open Vault** - Review intelligence reports
4. **Try refinement** - Click "Remake Video" workflow

### If You're Debugging:
1. **Check terminal logs** - Look for `[STAGE X]` markers
2. **Inspect cache** - `data/cache/*.json` for analysis
3. **Review intelligence JSON** - `data/results/{filename}.json`
4. **Verify thumbnails** - `data/cache/thumbnails/`

---

## 🐛 Common Issues (Quick Fixes)

| Problem | Solution |
|---------|----------|
| "All API keys exhausted" | Wait for quota reset or add more keys |
| "Only .mp4 files supported" | Convert video to MP4 |
| "Session not found" | Upload files before generating |
| CORS errors | Check `FRONTEND_URL` in `.env` |
| Port in use | Kill process on port 8000/3000 |

---

## 🎬 Demo Readiness

**Status:** ✅ **READY FOR FINAL DEMONSTRATION**

### Verified References:
- `ref1.mp4` - 14s, Travel/Nature/Friends
- `ref10.mp4` - 16s, Nature/Travel
- `ref12.mp4` - 19s, Urban/Friends/Action
- `ref13.mp4` - Latest test, fully stable

### Quality Assurance:
- ✅ 100% diversity (0 repetitions)
- ✅ 0% crash rate (hardened filters)
- ✅ <20s generation time (with cache)
- ✅ Complete intelligence reports
- ✅ Thumbnail coverage (all assets)

---

## 🚀 Next Steps (For This Session)

1. **Review the documentation** - Ensure accuracy
2. **Test the system** - Run `test_ref.py` with ref13
3. **Check the Vault** - Verify intelligence display
4. **Prepare demo** - Identify best reference + clip combinations

---

**Welcome aboard! You're now ready to work with MIMIC V11.0.**

For questions, check the documentation files or review the code with the structure guide above.
