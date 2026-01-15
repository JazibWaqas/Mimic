# 🎬 MIMIC - AI Video Structural Replication

**Steal the editing structure of any viral video and apply it to your own footage.**

MIMIC uses Gemini 3's multimodal reasoning to analyze the "editing DNA" of viral videos (timing, pacing, energy) and automatically applies it to your raw clips using a high-precision, frame-perfect rendering engine.

---

## 🧭 Project Navigation (For Developers & AI Agents)

*Use this section to quickly understand the project architecture and logic flow.*

### 📂 Key Documentation
- **[CURRENT_FLOW.md](./CURRENT_FLOW.md)**: The definitive step-by-step logic of the pipeline (Jan 15, 2026).
- **[IMPORTANT_FILES.md](./IMPORTANT_FILES.md)**: Map of the codebase and how files are linked.
- **[STATUS.md](./STATUS.md)**: Current development state and upcoming milestones.
- **[FIXES_APPLIED.md](./FIXES_APPLIED.md)**: Detailed report on the major Editor rewrite and Rapid Cuts fix.
- **[MIMIC_QUICK_REFERENCE.md](./MIMIC_QUICK_REFERENCE.md)**: The "Why" behind technical decisions and Hackathon strategy.

### 🧠 Core Methodology
1.  **Editing DNA**: We extract cut points, energy levels, and motion patterns from a reference video.
2.  **Comprehensive Analysis**: Gemini 3 analyzes each user clip *once* to find the best moments for Low, Medium, and High energy needs.
3.  **Rapid Cuts Algorithm**: In `editor.py`, we split segments into multiple rapid cuts (0.2s - 1.5s) to match the high-tempo feel of viral content.
4.  **Frame-Perfect Render**: Using FFmpeg re-encoding (not just stream copying) to ensure every cut aligns exactly with the reference timing.

---

## 🏗️ Repository Structure

```
Mimic/
├── backend/                # FastAPI Application
│   ├── engine/             # The Processing Core
│   │   ├── brain.py        # Gemini 3 API, Prompts, & Caching
│   │   ├── editor.py       # THE MATCHING ENGINE (Rapid Cuts Algorithm)
│   │   ├── processors.py   # FFmpeg execution logic
│   │   └── orchestrator.py # Pipeline controller (Entry point)
│   ├── main.py             # REST & WebSocket Endpoints
│   └── models.py           # Pydantic data schemas
├── frontend/               # Next.js 15 Application
│   ├── app/                # Pages (Upload, Generate, Result)
│   └── components/         # UI Library (shadcn/ui + custom)
├── data/                   # Persistent Storage
│   ├── cache/              # AI Analysis Cache (JSON)
│   ├── results/            # Final MP4 Outputs
│   ├── uploads/            # Raw user uploads (Permanent session storage)
│   └── samples/            # Test assets (Reference & clips)
└── temp/                   # Intermediate processing (Safe to clear)
```

---

## � Prerequisites

- **Python 3.10+** (recommended via `pyenv` or system install)
- **Node.js 18+** (npm comes with it)
- **FFmpeg 6.0+** – must be on your `PATH` (`ffmpeg -version` to verify)
- **Gemini API key** – create a `.env` file in `backend/` with:
  ```
  GEMINI_API_KEY=your_key_here
  FRONTEND_URL=http://localhost:3000
  ```
- **Git** – to clone the repository.

Once the above are installed, you can run the backend and frontend in separate terminals as described in the QUICK START section.
---

## �🚀 QUICK START: TESTING VIA FRONTEND

To test the full experience (UI + Backend), follow these steps in **two separate terminals**.

### 1. Start the Backend
*The backend handles the AI analysis and FFmpeg rendering.*
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt

# Ensure your .env has:
# GEMINI_API_KEY=your_key_here
# FRONTEND_URL=http://localhost:3000

python main.py               # Runs on http://localhost:8000
```

### 2. Start the Frontend
*The frontend is the user interface.*
```powershell
cd frontend
npm install

# Ensure your .env.local has:
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev                  # Runs on http://localhost:3000
```

### 3. Usage
1. Open **[http://localhost:3000](http://localhost:3000)** in your browser.
2. Go to the **Upload** page.
3. Select a reference video (from `data/samples/reference/`).
4. Select 2-5 user clips (from `data/samples/clips/`).
5. Click **Generate** and watch the progress bar!

---

## 🛠️ Modes of Operation

### 🤖 Auto Mode
- Uses Gemini 3 API for fresh analysis.
- **Highly Automated**: Just upload and click generate.
- **Quota Saver**: Uses comprehensive analysis to minimize API calls (1 call per clip).

### ✍️ Manual Mode
- Bypass the API by providing pre-analyzed JSON.
- **Infinite Testing**: Test rendering logic and new edit styles without hitting API limits.
- **Demo Ready**: Ideal for hackathon presentations to ensure 100% reliability.

---

## ⚠️ Legacy Content
The following documents are kept for historical context but **may contain outdated code samples**:
- `MIMIC_MASTER_BUILD_PLAN_FINAL.md` (See `CURRENT_FLOW.md` for current logic)
- `MIMIC_CURSOR_LAUNCH_CHECKLIST.md`

---

**Built for the Gemini 3 Global Hackathon** | *Agentic AI Video Orchestration*
