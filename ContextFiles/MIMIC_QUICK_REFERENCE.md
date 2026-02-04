# 🚀 MIMIC Quick Reference

**Version:** V12.1 - Director vs. Metronome  
**Last Updated:** February 5, 2026

This is your **one-page cheat sheet** for working with MIMIC. Bookmark this for quick command lookups and troubleshooting.

---

## 🎯 Quick Start (3 Commands)

```powershell
# 1. Start Backend
cd backend
.venv\Scripts\activate
python main.py

# 2. Start Frontend (new terminal)
cd frontend
npm run dev

# 3. Open Browser
# Navigate to http://localhost:3000
```

---

## 📁 Key Directories

| Path | Purpose |
|------|---------|
| `backend/engine/` | Core AI pipeline (brain, advisor, editor, stylist) |
| `backend/models.py` | **Single source of truth** for data structures |
| `frontend/app/` | Next.js pages (Studio, Vault, Gallery, etc.) |
| `data/cache/` | Analysis cache + standardized clips |
| `data/results/` | Generated videos + intelligence JSON |
| `data/samples/` | Reference videos + clip library |
| `ContextFiles/` | Extended documentation |

---

## 🔧 Common Commands

### Backend
```powershell
# Run backend server
python main.py

# Test with specific reference
$env:TEST_REFERENCE = "ref13.mp4"
python test_ref.py

# Clear all cache
Remove-Item data/cache/* -Recurse -Force

# Clear only analysis cache (keep standardized clips)
Remove-Item data/cache/*.json -Force

# --- V12.0 PRIME COMMAND ---
# Analyze + Standardize EVERYTHING for zero-latency
python backend/precache_clips.py
```

### Frontend
```powershell
# Development server
npm run dev

# Production build
npm run build
npm start

# Type checking
npm run type-check
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **"All API keys exhausted"** | Wait for quota reset or add more keys to `backend/.env` |
| **"Only .mp4 files supported"** | Convert video to MP4 format |
| **Thumbnails showing black frames** | Already fixed with multi-point sampling |
| **"Session not found"** | Upload files first before generating |
| **CORS errors** | Check `FRONTEND_URL` in `backend/.env` matches browser URL |
| **Port already in use** | Kill process: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess` |

---

## 📊 File Structure Quick Map

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
│   ├── main.py                 # FastAPI server
│   └── .env                    # API keys + config
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Studio (upload + generate)
│   │   ├── vault/page.tsx      # Asset browser + intelligence
│   │   ├── gallery/page.tsx    # Clip library
│   │   └── history/page.tsx    # Session history
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   └── types.ts            # TypeScript interfaces
│   └── .env.local              # Frontend config
├── data/
│   ├── cache/                  # Analysis + standardized clips
│   ├── results/                # Generated videos + JSON
│   └── samples/                # Reference + clips
└── ContextFiles/               # Documentation
```

---

## 🎨 Key Concepts

### Narrative Subject Locking
When text overlay demands specific content (e.g., "friends"), the system enforces primary subject matching with +50-200 bonus for correct subjects.

### Pacing Authority (V12.1)
The "Director" (Narrative intent) now has authority over the "Metronome" (Beat grid). Sacred visual cuts are protected from subdivision, and minimum holds (1.2s-2.5s) ensure emotional registration.

### Cache Inheritance
Reuses expensive AI analysis even if pacing changes. Keyed by content hash, not filename.

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
```env
GEMINI_API_KEY=your_primary_key
#GEMINI_API_KEY=backup_key_1
#GEMINI_API_KEY=backup_key_2
FRONTEND_URL=http://localhost:3000
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Analysis Speed | <30s | 15-20s ✅ |
| Cache Hit Rate | >90% | 100% ✅ |
| Index Load Time| <50ms | 10-20ms ✅ |
| Search Latency | <20ms | ~5ms ✅ |
| Diversity Score | >90% | 100% ✅ |
| Vibe Accuracy | >70% | 80-90% ✅ |
| Timeline Precision | <0.01s | <0.001s ✅ |

---

## 🎯 API Endpoints (Quick Reference)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/identify` | POST | Fast identity scan of reference |
| `/api/upload` | POST | Upload reference + clips |
| `/api/generate/{session_id}` | POST | Start generation pipeline |
| `/api/status/{session_id}` | GET | Check generation progress |
| `/api/results` | GET | List all generated videos |
| `/api/clips` | GET | List all clips |
| `/api/references` | GET | List all references |
| `/api/intelligence` | GET | Get AI analysis for file |
| `/ws/progress/{session_id}` | WS | Real-time progress updates |

---

## 🔍 Debugging Tips

### Check Logs
```powershell
# Backend logs (terminal output)
# Look for [STAGE X] markers

# Intelligence reports
cat data/results/{filename}.json | jq .
```

### Verify Cache
```powershell
# List cached analyses
ls data/cache/*.json

# List standardized clips
ls data/cache/standardized/

# List thumbnails
ls data/cache/thumbnails/
```

### Test Pipeline
```powershell
# Quick test with ref13
$env:TEST_REFERENCE = "ref13.mp4"
python test_ref.py

# Check output
ls data/results/ref13*
```

---

## 📚 Documentation Links

- **README.md** - Project overview + quick start
- **STATUS.md** - Current state + quality metrics
- **ARCHITECTURE.md** - Technical deep dive
- **PRODUCTION_FIXES.md** - Recent hardening changes
- **ONBOARDING.md** - First-time setup guide

---

**Pro Tip:** Keep this file open in a side tab while developing!
