# MIMIC Backend

FastAPI backend for MIMIC - AI video editing tool using Gemini 3.

## Setup

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Start server:**
```bash
uvicorn main:app --reload --port 8000
```

## Verify Installation

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# API docs
open http://localhost:8000/docs
```

## API Endpoints

- `POST /api/upload` - Upload reference video and clips
- `POST /api/generate/{session_id}` - Start video generation
- `GET /api/status/{session_id}` - Get processing status
- `GET /api/download/{session_id}` - Download final video
- `WS /ws/progress/{session_id}` - WebSocket for real-time progress
- `GET /health` - Health check

## Project Structure

```
backend/
├── main.py              # FastAPI app & routes
├── models.py            # Pydantic schemas
├── utils.py             # File helpers
├── requirements.txt     # Dependencies
├── engine/
│   ├── brain.py         # Gemini 3 integration
│   ├── editor.py        # Clip matching algorithm
│   ├── processors.py    # FFmpeg wrappers
│   └── orchestrator.py  # Main pipeline
└── temp/                # Session storage
```

## Requirements

- Python 3.10+
- FFmpeg 4.4+ (must be installed system-wide)
- Gemini API key from https://aistudio.google.com/app/apikey

