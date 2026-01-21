# 🗂️ Project Onboarding Guide

This guide is for **first‑time contributors** who clone the repository and need to get everything up and running from scratch. Follow the steps in order; each step explains **what to install**, **which files to edit**, and **where to look** for the core logic.

---

## 1️⃣ Clone the Repository
```bash
# If you don't have Git installed, download it from https://git-scm.com/downloads
git clone https://github.com/your‑username/Mimic.git
cd Mimic
```

---

## 2️⃣ Install System Prerequisites
| Tool | Why it’s needed | Installation command (Windows PowerShell) |
|------|----------------|-------------------------------------------|
| **Python 3.10+** | Runs the FastAPI backend and all engine scripts. | `winget install Python.Python.3.10` |
| **Node.js 18+** | Builds the Next.js frontend. | `winget install OpenJS.Nodejs` |
| **FFmpeg 6.0+** | Handles video standardisation, cutting, and stitching. | `winget install ffmpeg` |
| **Git** | Version control (already used for cloning). | `winget install Git.Git` |

> Verify each tool is on your `PATH`:
> ```powershell
> python --version
> node --version
> ffmpeg -version
> git --version
> ```

---

## 3️⃣ Backend Setup
1. **Create a virtual environment** and activate it:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # Windows PowerShell
   ```
2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Configure environment variables** – copy the example and fill in your Gemini API key:
   ```powershell
   # In backend folder create .env if it does not exist
   New-Item -Path . -Name .env -ItemType File -Force
   Add-Content .env "GEMINI_API_KEY=YOUR_KEY_HERE"
   Add-Content .env "FRONTEND_URL=http://localhost:3000"
   ```
4. **Run the backend** (it will listen on `http://localhost:8000`):
   ```powershell
   python main.py
   ```
5. **Verify it works** – open another terminal and run:
   ```powershell
   curl http://localhost:8000/health
   ```
   You should see `{ "status": "healthy" }`.

### Core Backend Files to Explore
| File | Purpose |
|------|---------|
| `engine/brain.py` | Gemini 3 integration, prompts, and caching. |
| `engine/editor.py` | **Rapid‑Cuts** matching algorithm – the heart of the editing logic. |
| `engine/orchestrator.py` | Orchestrates the whole pipeline (calls brain, editor, processors). |
| `engine/processors.py` | FFmpeg wrappers for standardisation, cutting, and concatenation. |
| `models.py` | Pydantic data schemas – the single source of truth for data structures. |
| `main.py` | FastAPI routes and WebSocket progress updates. |

---

## 4️⃣ Frontend Setup
1. **Install Node dependencies**:
   ```powershell
   cd ../frontend   # from the repo root
   npm install
   ```
2. **Create the environment file** (`.env.local`) so the UI knows where the backend lives:
   ```powershell
   New-Item -Path . -Name .env.local -ItemType File -Force
   Add-Content .env.local "NEXT_PUBLIC_API_URL=http://localhost:8000"
   ```
3. **Run the development server** (it will be reachable at `http://localhost:3000`):
   ```powershell
   npm run dev
   ```
4. **Open the UI** in your browser and verify the landing page loads.

### Core Frontend Files to Explore
| File | Purpose |
|------|---------|
| `app/upload/page.tsx` | Upload UI – handles Auto & Manual modes. |
| `app/generate/[id]/page.tsx` | Shows real‑time progress via WebSocket. |
| `app/result/[id]/page.tsx` | Side‑by‑side video comparison and download button. |
| `lib/api.ts` | API client that talks to the FastAPI backend. |
| `components/…` | Reusable UI components (buttons, progress bars, video player). |

---

## 5️⃣ End‑to‑End Test (No UI Required)
Run the provided script to ensure the whole pipeline works with sample data:
```powershell
cd ..   # back to repo root
python test_real_pipeline.py
```
It will:
* Pick a reference video from `data/samples/reference/`.
* Use a few clips from `data/samples/clips/`.
* Execute the full backend pipeline.
* Print a short report (duration match, clip usage, output path).

---

## 6️⃣ Where to Find Project‑Wide Documentation
* **`CURRENT_FLOW.md`** – step‑by‑step description of the pipeline logic (the “what happens when”).
* **`IMPORTANT_FILES.md`** – a concise map of every source file and how they are linked.
* **`STATUS.md`** – current development state, known issues, and next milestones.
* **`MIMIC_CURSOR_LAUNCH_CHECKLIST.md`** – the quick‑launch checklist you just read.
* **`README.md`** – the central hub with navigation links and prerequisites.

---

## 7️⃣ Common Gotchas & Fixes
| Issue | Quick Fix |
|-------|-----------|
| **Gemini model not found** | Verify your API key is correct and that your account has Gemini 3 access. |
| **FFmpeg not on PATH** | Re‑install via `winget install ffmpeg` and restart the terminal. |
| **CORS/WebSocket errors** | Ensure `FRONTEND_URL` in `backend/.env` matches the URL you open in the browser (`http://localhost:3000`). |
| **Port already in use** | Kill the existing process: `lsof -ti:8000 | xargs kill -9` (backend) or `lsof -ti:3000 | xargs kill -9` (frontend). |

---

## 8️⃣ Ready to Contribute?
When all the checkboxes in **`MIMIC_CURSOR_LAUNCH_CHECKLIST.md`** are green, you have a fully functional local copy. From there you can:
* Add new matching heuristics in `engine/editor.py`.
* Extend the UI with new pages or components.
* Write tests in `tests/` (create the folder if you need it).
* Update the documentation files to keep everything in sync.

Happy hacking! 🎉
