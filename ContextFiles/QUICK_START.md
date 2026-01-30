# MIMIC - Quick Start Guide for New Sessions

**Version:** V7.1 - Semantic Maturation  
**Status:** 🟡 **FINAL POLISH IN PROGRESS**  
**Last Updated:** January 30, 2026

---

## 🎯 What is MIMIC?

MIMIC is an AI-powered video editing system that learns from professional reference videos and automatically recreates that editing style using your raw clips.

**Current Goal:** Implementing **Stage 6 Reflector** - a closed-loop AI judge that watches the final render to provide critical feedback.

---

## ⚡ Quick Start (5 minutes)

### 1. Test the System
```bash
# Activate environment
.venv\Scripts\activate

# Run test (with reflection enabled)
$env:TEST_REFERENCE = "ref4.mp4"
python test_ref.py
```

### 2. Explore the Vault
After running a test, open the **Vault Dashboard** (via Frontend) to see:
- **Judicial Review:** Holistic AI scores on fidelity and rhythm.
- **Editorial Reasoning:** Why each specific clip was matches to each segment.
- **Recommended Actions:** Strategic feedback for your next iteration.

---

## 📁 Key Files to Know

### Core Engine
```
backend/engine/
├── orchestrator.py    # Pipeline controller (V8.0 Stage Machine)
├── brain.py           # Gemini 3 Analysis & Strategic Advisor
├── editor.py          # Grammar matching (Novelty/Vibe/Arc)
├── reflector.py       # NEW: Post-render AI judge
└── processors.py      # FFmpeg & Librosa "The Hands"
```

---

## 🧠 The Agentic Loop

1. **Plan:** The Advisor audits your library and creates a strategy.
2. **Execute:** The Editor performs frame-accurate, beat-synced cuts.
3. **Reflect:** The Reflector watches the final output and judges its own work.

**Innovation:** The first video editor with a "Whitebox" reasoning system.

---

## 🎨 Scoring & Intelligence (V8.0)
```
Novelty Bonus:       +40 (Prioritize unused material)
Vibe Density:        +15 (Semantic tag alignment)
Arc Consistency:     +10 (Intro/Peak relevance)
Visual Cooldown:     -40 (Prevent repetitive usage)
```

---

## 🚀 Performance
- **Cached Run:** 15-20s (including AI Reflection).
- **Cache Hit Rate:** 100% on repeat runs.
- **Throughput:** Supported by 28-key API rotation carousel.

---

## 🔧 Common Commands

```bash
# Run End-to-End Test
python test_ref.py

# Launch Backend
cd backend && uvicorn main:app --reload

# Launch Frontend (The Vault)
cd frontend && npm run dev
```

---

**Next:** Review `ContextFiles/SESSION_SUMMARY.md` for the latest milestone details. 🚀
