# 🚀 MIMIC PROJECT - CURSOR LAUNCH CHECKLIST

## ⚡ Pre-Flight Checks (Do These First)

### 1. Environment Setup
- [ ] **FFmpeg installed and working** (`ffmpeg -version` shows 4.4+)
- [ ] **Python 3.10+ installed** (`python3 --version`)
- [ ] **Node.js 18+ installed** (`node --version`)
- [ ] **Gemini API key obtained** from https://aistudio.google.com/app/apikey
- [ ] **Cursor/Windsurf IDE ready**

### 2. Create Project Folder
```bash
mkdir mimic-project
cd mimic-project
mkdir backend frontend
```

### 3. Critical Files Setup
- [ ] Copy `MIMIC_MASTER_BUILD_PLAN_FINAL.md` into project root
- [ ] Create `backend/.env` file with:
  ```
  GEMINI_API_KEY=your_key_here
  FRONTEND_URL=http://localhost:3000
  ```

---

## 🎯 The Cursor Prompt for Backend (Copy This Exactly)

```
I'm building MIMIC - an AI video editing tool for the Gemini 3 Hackathon.

Read the entire MIMIC_MASTER_BUILD_PLAN_FINAL.md document carefully.

CRITICAL INSTRUCTIONS:
1. We're using Next.js + FastAPI architecture (NOT Streamlit)
2. In requirements.txt, google-generativeai must be >=0.8.3 (for Gemini 3 support)
3. Apply Fix 1 from Section 9.5 (CORS with FRONTEND_URL environment variable)

Please start Phase 1 from Section 11.2 (Backend Core):
1. Create backend/ folder structure with engine/ subdirectory
2. Create requirements.txt with correct versions
3. Create all core files:
   - models.py (Section 4)
   - engine/brain.py (Section 5.1)
   - engine/processors.py (Section 5.2)
   - engine/editor.py (Section 5.3)
   - engine/orchestrator.py (Section 5.4)
   - utils.py (Section 5.5)
4. Create main.py with FastAPI endpoints (Section 4.5.1)

Use EXACT code from the document. Do not modify.
I will test the backend before building frontend.
```

---

## 📋 Build Phase Checklist

### Phase 1: Backend Core (2 hours)

#### Step 1.1: Scaffolding (10 min)
- [ ] `backend/` directory created
- [ ] `backend/engine/` subdirectory created
- [ ] `backend/requirements.txt` created with `google-generativeai>=0.8.3`
- [ ] `backend/models.py` created
- [ ] Virtual environment created

**Verification:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip list | grep google-generativeai  # Should show >=0.8.3
python -c "from models import StyleBlueprint; print('✅ Models OK')"
```

#### Step 1.2: Core Engine (30 min)
- [ ] `engine/brain.py` implemented (Gemini 3 integration)
- [ ] `engine/processors.py` implemented (FFmpeg wrappers)
- [ ] `engine/editor.py` implemented (matching algorithm)
- [ ] `engine/orchestrator.py` implemented (pipeline)
- [ ] `utils.py` implemented (file helpers)

**Verification:**
```bash
python -c "from engine.brain import analyze_reference_video; print('✅ Brain OK')"
python -c "from engine.processors import standardize_clip; print('✅ Processors OK')"
python -c "from engine.editor import match_clips_to_blueprint; print('✅ Editor OK')"
```

#### Step 1.3: FastAPI Server (20 min)
- [ ] `main.py` created with all endpoints
- [ ] CORS configured with `FRONTEND_URL`
- [ ] WebSocket handler implemented

**Verification:**
```bash
uvicorn main:app --reload --port 8000

# In another terminal:
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Check API docs:
open http://localhost:8000/docs
```

#### Step 1.4: Backend Testing (1 hour)
- [ ] Health check works
- [ ] Gemini 3 API connects
- [ ] FFmpeg commands execute
- [ ] File upload works
- [ ] Session management works

**Test Script:**
```bash
# 1. Test Gemini
python -c "
from engine.brain import analyze_reference_video
result = analyze_reference_video('test_video.mp4')
print(f'✅ Segments detected: {len(result.segments)}')
"

# 2. Test FFmpeg
python -c "
from engine.processors import get_video_duration
print(f'✅ Duration: {get_video_duration(\"test_video.mp4\")}s')
"

# 3. Test upload endpoint
curl -X POST http://localhost:8000/api/upload \
  -F "reference=@test_video.mp4" \
  -F "clips=@clip1.mp4" \
  -F "clips=@clip2.mp4"
# Expected: JSON with session_id
```

**✅ Phase 1 Complete When:**
- Backend starts without errors
- `/health` returns 200
- Can upload files via API
- Gemini returns valid JSON
- FFmpeg renders test video

---

### Phase 2: Frontend (1.5 hours)

#### Step 2.1: Next.js Setup (10 min)
```bash
cd frontend

# Create Next.js app
npx create-next-app@latest . --typescript --tailwind --app

# Install dependencies
npm install @radix-ui/react-icons clsx tailwind-merge react-dropzone lucide-react

# Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card progress dialog badge separator

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

- [ ] Next.js app created
- [ ] Dependencies installed
- [ ] shadcn/ui configured
- [ ] Environment variables set

#### Step 2.2: Build UI with Antigravity (1 hour)

**Antigravity Prompt:**
```
Read MIMIC_MASTER_BUILD_PLAN_FINAL.md Section 3.5 (UI/UX Design System).

Build a Next.js 14 app with these pages:

1. app/page.tsx - Landing page with hero + demo section
2. app/upload/page.tsx - File upload interface (reference + clips)
3. app/generate/[id]/page.tsx - Processing page with WebSocket progress
4. app/result/[id]/page.tsx - Side-by-side video comparison with sync toggle

Components (Section 6.2):
- components/FileUpload.tsx
- components/ProgressTracker.tsx
- components/VideoComparison.tsx
- lib/api.ts (API client with WebSocket support)

Design System (Section 3.5.2):
- Background: #0A0A0A
- Primary: #8B5CF6 (purple with glow effects)
- Accent: #06B6D4 (cyan)
- Font: Inter

Make it look like Runway ML - premium, cinematic, professional.
Use smooth animations, glow effects on buttons, responsive design.
```

- [ ] Landing page created
- [ ] Upload interface created
- [ ] Processing page with WebSocket created
- [ ] Result page with video comparison created
- [ ] All components implemented
- [ ] API client with WebSocket support

#### Step 2.3: Frontend Testing (20 min)
```bash
npm run dev
# Open: http://localhost:3000
```

- [ ] Landing page loads without errors
- [ ] Can navigate to /upload
- [ ] File upload accepts videos
- [ ] TypeScript compiles without errors

**✅ Phase 2 Complete When:**
- All pages render
- No console errors
- File upload UI works
- Routing works

---

### Phase 3: Integration Testing (30 min)

#### Test Complete Workflow
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser: http://localhost:3000
```

**Test Scenarios:**

1. **Happy Path:**
   - [ ] Upload 10s reference video
   - [ ] Upload 3 clips (5-10s each)
   - [ ] Click "Generate"
   - [ ] See progress bar updating (WebSocket)
   - [ ] Video completes in <60s
   - [ ] Side-by-side comparison shows
   - [ ] Download button works

2. **Edge Cases:**
   - [ ] Upload 15s reference + 1 short clip (should loop)
   - [ ] Upload with no audio (should render silently)
   - [ ] Try with different video resolutions

3. **Error Handling:**
   - [ ] Disconnect internet during generation (fallback blueprint)
   - [ ] Upload invalid file format
   - [ ] Upload file too large

**✅ Phase 3 Complete When:**
- Complete end-to-end flow works
- WebSocket shows real-time progress
- Output video matches reference timing
- Download works

---

## 🔥 Critical Success Indicators

### After Backend Setup:
```bash
# No import errors
python -c "import engine.brain, engine.editor, engine.processors, engine.orchestrator"

# Gemini 3 accessible
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-3-flash-preview')
print('✅ Gemini 3 accessible')
"

# FFmpeg works
ffmpeg -version
python -c "from engine.processors import get_video_duration; print('✅ FFmpeg OK')"

# API running
curl http://localhost:8000/health
```

### After Frontend Setup:
```bash
# No TypeScript errors
cd frontend && npm run build

# Environment variables
grep NEXT_PUBLIC_API_URL .env.local

# API client works
# Check browser console for successful fetch to backend
```

---

## 🚨 Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'google.generativeai'"
**Fix:**
```bash
pip show google-generativeai  # Must be >=0.8.3
pip install --upgrade google-generativeai
```

### Issue: "Model gemini-3-flash-preview not found"
**Fix:**
- Verify API key is correct in `.env`
- Try fallback: `gemini-3-pro-preview` or `gemini-exp-1206`
- Check if you have Gemini 3 API access

### Issue: "ffmpeg: command not found"
**Fix:**
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org and add to PATH
```

### Issue: "WebSocket connection failed"
**Fix:**
- Check CORS in `backend/main.py`:
  ```python
  FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
  allow_origins=[FRONTEND_URL]  # Must match exactly
  ```
- Verify backend is running on port 8000
- Check browser console for error details

### Issue: "Frontend can't reach backend"
**Fix:**
```bash
# Check .env.local
cat frontend/.env.local
# Should be: NEXT_PUBLIC_API_URL=http://localhost:8000

# Test backend directly
curl http://localhost:8000/health
```

### Issue: "Port already in use"
**Fix:**
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

---

## 🎬 Final Demo Test (Before Submission)

### Test Scenario 1: Professional Demo
1. Use a viral TikTok as reference (10-15s with clear beat drops)
2. Use 3 random clips (gym, cooking, walking)
3. Generate video
4. **Expected:** Side-by-side shows perfect beat alignment
5. Record this for demo video

### Test Scenario 2: Edge Case
1. Use 20s reference
2. Use only 2 short clips (5s each)
3. **Expected:** Clips loop to fill 20s, no crashes

### Test Scenario 3: Failure Recovery
1. Disconnect internet mid-generation
2. **Expected:** Fallback blueprint used, warning shown, video still renders

---

## 📊 Performance Benchmarks

**Target Metrics:**
- Reference analysis: <15 seconds
- Per-clip analysis: <10 seconds each
- Video rendering: <30 seconds
- **Total pipeline: <60 seconds** for typical input

**If Slower:**
- Check FFmpeg preset (should be `ultrafast`)
- Verify using Gemini 3 Flash (not Pro)
- Check video resolution (standardizes to 1080x1920)

---

## ✅ Pre-Submission Checklist

### Code Quality:
- [ ] No hardcoded API keys (use `.env`)
- [ ] No absolute file paths
- [ ] Temp files cleaned up after run
- [ ] Error messages are user-friendly
- [ ] TypeScript/Python type hints present

### Documentation:
- [ ] `README.md` with setup instructions
- [ ] `.env.example` files (without real keys)
- [ ] Demo video recorded (3 minutes)
- [ ] Architecture diagram (optional)

### Testing:
- [ ] Tested on 3+ different reference videos
- [ ] Tested with various clip lengths
- [ ] Tested failure modes (no internet, corrupt file)
- [ ] Tested on fresh install (new virtual env + `npm install`)

### Hackathon Requirements:
- [ ] Uses Gemini 3 models (check logs)
- [ ] Demonstrates "Action Era" (sense → plan → act)
- [ ] Has clear value proposition
- [ ] Works in live demo (practiced 3+ times)

---

## 🏆 Demo Day Strategy

### The 2-Minute Pitch

**[0:00-0:15] The Hook**
"Creators see viral videos and think 'I want that vibe.' But replicating the pacing takes hours. MIMIC does it in 60 seconds."

**[0:15-0:45] The Setup**
- Show reference video (fast-paced TikTok)
- Show your clips (random gym/cooking footage)
- "These don't match at all. Watch this."

**[0:45-1:30] The Magic Moment**
- Upload to MIMIC
- Show WebSocket progress updates
- **Reveal:** Side-by-side comparison
- **Point out:** "Same beat drops. Perfect sync. Gemini 3 understood the structure."

**[1:30-2:00] The Technical Flex**
- "Gemini 3 analyzes spatial-temporal patterns, not content"
- "This is the Action Era: AI that creates, not just analyzes"
- "Next.js + FastAPI architecture, frame-perfect FFmpeg rendering"

### Backup Plan
If live demo fails:
- [ ] Pre-recorded demo video ready
- [ ] Show the code (Gemini 3 API calls)
- [ ] Walk through architecture diagram
- [ ] Explain technical decisions

---

## 📞 Emergency Recovery

**If Backend Breaks:**
```bash
# Check logs
tail -f backend/uvicorn.log

# Restart
pkill -f uvicorn
cd backend && uvicorn main:app --reload
```

**If Frontend Breaks:**
```bash
# Check browser console
# Check terminal for errors

# Rebuild
cd frontend
rm -rf .next
npm run dev
```

**If WebSocket Fails:**
- Fall back to polling (`GET /api/status/{id}` every 2 seconds)
- User still sees progress, just slower updates

---

**You are cleared for launch. Build something amazing!** 🚀
