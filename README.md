
# 🎬 MIMIC - AI Video Structural Replication

MIMIC uses Gemini 3's multimodal reasoning to analyze the "editing DNA" of viral videos and apply it to your raw footage.

## 📁 Repository Structure

```text
├── data/
│   ├── samples/
│   │   ├── reference/   # Put viral videos here (the "blueprint")
│   │   └── clips/       # Put your raw clips here
│   └── results/         # All finished videos appear here ✨
├── backend/             # FastAPI Engine
├── frontend/            # Next.js UI
├── temp/                # Ephemeral AI processing (Auto-cleaned)
└── test_mimic.py        # One-click end-to-end engine test
```

## 🚀 Quick Start (Engine Only)

1. Ensure FFmpeg is installed and `backend/.env` has your `GEMINI_API_KEY`.
2. Run the organized test:
   ```bash
   python test_mimic.py
   ```

## 🌐 Full App Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🧠 The AI Magic
MIMIC doesn't analyze content ("what is in the video"). It analyzes **spatial-temporal structure** ("when do the cuts happen and what is the energy?"). This allows for frame-perfect replication of viral pacing regardless of the subject matter.
