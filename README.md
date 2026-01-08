# 🎬 MIMIC - AI Video Structural Replication

**Steal the editing structure of any viral video and apply it to your own footage.**

MIMIC uses Gemini 3's multimodal reasoning to analyze the "editing DNA" of viral videos (timing, pacing, energy) and automatically applies it to your raw clips.

---

## 🚀 Quick Start

### Prerequisites
- **FFmpeg** installed ([download](https://ffmpeg.org/download.html))
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Gemini API Key** ([get one](https://aistudio.google.com/app/apikey))

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_actual_key_here" > .env
echo "FRONTEND_URL=http://localhost:3000" >> .env

# Start server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

### 3. Open App
Navigate to [http://localhost:3000](http://localhost:3000)

---

## 🎯 Two Modes of Operation

### 🤖 Auto Mode (Full AI Pipeline)
- Upload reference video + clips
- Gemini 3 analyzes everything automatically
- **Quota:** Uses ~14 API calls per video (reference + 6 clips)
- **Best for:** Production use with paid API tier

### ✍️ Manual Mode (Quota-Free Testing)
- Analyze videos once in [AI Studio](https://aistudio.google.com)
- Paste the JSON analysis into the UI
- System skips API calls and goes straight to rendering
- **Quota:** 0 API calls - test unlimited times!
- **Best for:** Development, testing, demo preparation

---

## 📋 Manual Mode Workflow

1. **Analyze Reference in AI Studio:**
   - Upload your reference video to AI Studio
   - Use the prompt from `backend/engine/brain.py` (REFERENCE_ANALYSIS_PROMPT)
   - Copy the JSON output

2. **Analyze Each Clip:**
   - Upload each clip to AI Studio
   - Use the CLIP_ANALYSIS_PROMPT
   - Compile results into a ClipIndex JSON

3. **Upload to MIMIC:**
   - Switch to "Manual Mode" in the upload page
   - Paste both JSON analyses
   - Upload your clips
   - Click "Render Video" → Done!

**Example JSON formats are shown in the UI placeholders.**

---

## 📁 Project Structure

```
Mimic/
├── backend/              # FastAPI + Core Engine
│   ├── engine/
│   │   ├── brain.py      # Gemini 3 integration
│   │   ├── editor.py     # Clip matching algorithm
│   │   ├── processors.py # FFmpeg wrappers
│   │   └── orchestrator.py # Pipeline controller
│   ├── main.py           # API endpoints
│   └── models.py         # Pydantic schemas
│
├── frontend/             # Next.js 14 + TypeScript
│   ├── app/
│   │   ├── upload/       # Dual-mode upload page
│   │   ├── generate/     # Real-time progress
│   │   ├── result/       # Side-by-side comparison
│   │   └── history/      # Past projects
│   └── components/       # Reusable UI components
│
├── data/
│   ├── cache/            # AI analysis cache (quota saver)
│   ├── results/          # Final rendered videos
│   └── samples/          # Test videos
│
└── temp/                 # Session-based processing files
```

---

## 🧠 How It Works

1. **Analysis Phase:**
   - Gemini 3 watches the reference video
   - Extracts timing structure (segments, energy levels, motion)
   - Analyzes each user clip for energy/motion

2. **Matching Phase:**
   - Algorithm matches clips to reference segments by energy
   - Creates an Edit Decision List (EDL) with frame-perfect timing

3. **Rendering Phase:**
   - FFmpeg standardizes clips (1080x1920, 30fps)
   - Extracts and concatenates segments per EDL
   - Merges reference audio (auto mode) or creates silent video (manual mode)

---

## ✅ Current Status

### Completed Features
- ✅ Full backend pipeline (brain, editor, processors, orchestrator)
- ✅ FastAPI with WebSocket progress tracking
- ✅ Next.js frontend with 5 pages
- ✅ Dual-mode operation (Auto + Manual)
- ✅ Intelligent caching system (quota optimization)
- ✅ Real-time progress updates
- ✅ Side-by-side video comparison
- ✅ Project history gallery

### Known Limitations
- **Free Tier Quota:** Auto mode limited to ~1-2 videos/day (use Manual mode for testing)
- **Manual Mode Audio:** No reference audio (silent output) - can be added if needed
- **Video Format:** Optimized for vertical (1080x1920) TikTok/Instagram content

---

## 🐛 Troubleshooting

**"429 Quota Exceeded" Error:**
- Switch to Manual Mode
- Or wait 24 hours for quota reset
- Or upgrade to paid Gemini API tier

**Videos Not Processing:**
- Check backend logs: `uvicorn` terminal
- Ensure FFmpeg is installed: `ffmpeg -version`
- Verify `.env` has valid `GEMINI_API_KEY`

**Frontend Can't Connect:**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Verify CORS settings in `backend/main.py`

**Cache Not Working:**
- Check `data/cache/` directory exists
- Ensure backend has write permissions

---

## 🎥 For Demo/Hackathon

1. **Pre-analyze 3-5 reference videos** in AI Studio
2. **Save JSON outputs** to `data/samples/`
3. **Use Manual Mode** during live demo (instant, no quota risk)
4. **Show side-by-side** comparison to judges
5. **Explain:** "We analyzed the structure once, now we can apply it to any footage"

---

## 📚 Documentation

- **Master Plan:** `MIMIC_MASTER_BUILD_PLAN_FINAL.md` - Complete architecture
- **Quick Reference:** `MIMIC_QUICK_REFERENCE.md` - API endpoints
- **Launch Checklist:** `MIMIC_CURSOR_LAUNCH_CHECKLIST.md` - Deployment steps

---

## 🔗 Links

- **AI Studio:** https://aistudio.google.com
- **Gemini API Docs:** https://ai.google.dev/docs
- **FFmpeg Download:** https://ffmpeg.org/download.html

---

**Built for Gemini 3 Global Hackathon** | Powered by Gemini 3 Flash + Next.js + FastAPI
