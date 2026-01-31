# MIMIC - AI-Powered Video Style Transfer

**Transform your raw clips into professionally-edited videos by learning from examples.**

MIMIC analyzes a reference video's editing style (cuts, pacing, energy, narrative arc) and automatically recreates that style using your clips. Think "Instagram Reels editor that understands the 'why' behind professional edits."

**Version:** V9.0 - The Aesthetic Era (January 31, 2026)

---

## 🎯 What It Does

1. **Upload a reference video** (the style you want to mimic)
2. **Upload your raw clips** (your content)
3. **MIMIC analyzes both** using Gemini 3 AI
4. **Strategic Planning:** The "Advisor" audits your library and sets an editorial strategy.
5. **Agentic Execution:** The "Editor" executes frame-perfect, beat-synced cuts with **Adaptive Rhythm**.
6. **Aesthetic Styling:** The "Stylist" applies cinematic text overlays and color grading.
7. **The Vault:** Explore the "Whitebox" reasoning behind every decision in a telemetry dashboard.

---

## ✨ Key Features

### **Intelligent Analysis**
- **Scene Detection:** FFmpeg detects every visual cut in the reference
- **BPM Detection:** librosa extracts the music tempo for beat-perfect cuts
- **Semantic Understanding:** Gemini 3 identifies energy, motion, content vibes, and narrative arc
- **Narrative Arc Analysis:** Understands Intro/Build-up/Peak/Outro progression
- **Best Moment Extraction:** Pre-computes optimal segments from each clip

### **Aesthetic Stylist (New in V9.0)**
- **Cinematic Text Overlays:** Intelligent mapping of reference typography to high-end fonts (Georgia, Apple Serif).
- **Adaptive Color Grading:** Automated tone, contrast, and "Look" application based on reference DNA.
- **Dynamic Pacing Governor:** Distinguishes between "Intentionally Long" cinematic holds and high-energy cuts.

### **The Vault**
- **Clinical Telemetry:** View editorial decisions, AI insights, and recommended actions in a sleek dashboard.
- **Fidelity Scoring:** Judge-ready metrics for blueprint adherence, rhythm, and cohesion.
- **Micro-Critique:** Segment-specific feedback explaining *why* a specific cut succeeded or compromised.

### **Agentic Pipeline (Plan -> Execute -> Reflect)**
- **Gemini Advisor:** Strategic planning layer that assessment library gaps and sets the creative direction.
- **Adaptive Rhythm (V9.0):** Respects "Cinematic Holds" of the reference while maintaining surgical beat-sync.
- **Smart Matching:** Tiered energy eligibility, discovery bonuses (+40 pts), and vibe-aware selection (+15 pts).
- **Beat Synchronization:** Snaps cuts to detected BPM for musical alignment.
- **[UPCOMING] Stage 6 Reflector:** A planned post-render AI judgment pass to critique results.

### **Performance & Caching**
- **Cache Inheritance (New):** Reuse high-quality metadata across different pacing attempts (Instant re-runs).
- **Persistent Standardization Cache:** Clips are standardized once and reused forever (hash-based).
- **Reference Cache:** Reference analysis cached with scene hint fingerprinting.
- **Speed:** 15-20 seconds total for 30-segment edits (down from 10+ minutes).

---

## 📋 Recent Updates (V9.0 - January 31, 2026)

### **Major Improvements**
- **✅ Stylist Module:** Integrated a dedicated aesthetic engine for text and color grading.

### **Quality Metrics**
- **Diversity:** Consistently achieves 90-100% unique clip usage.
- **Vibe Matching:** 70-80% semantic accuracy across test references.
- **Energy Coherence:** Tiered system prevents jarring Low→High jumps.
- **Rhythmic Precision:** <0.02s deviation from musical anchors.

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.10+
- FFmpeg installed and in PATH
- Node.js 18+ (for frontend)
- Google Gemini API key(s)

### **Installation**

```bash
# Clone repository
git clone https://github.com/yourusername/Mimic.git
cd Mimic

# Backend setup
python -m venv .venv
.venv\Scripts\activate  # Windows (.venv/bin/activate on Unix)
pip install -r backend/requirements.txt

# Create .env file in backend/
echo "GEMINI_API_KEY=your_key_here" > backend/.env

# Frontend setup (optional)
cd frontend
npm install
```

### **Running the App**

```bash
# Terminal 1: Backend
cd backend
.venv\Scripts\activate
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Option 2: Test Script (Recommended for first run)**
```bash
# Activate venv
.venv\Scripts\activate

# Test with ref4
$env:TEST_REFERENCE = "ref4.mp4"
python test_ref.py

# Output: data/results/mimic_output_ref4_vibes_test.mp4
# X-Ray Log: data/results/ref4_xray_output.txt
```

Visit `http://localhost:3000` (if using frontend)

---

## 📁 Project Structure

```
Mimic/
├── backend/
│   ├── engine/
│   │   ├── orchestrator.py    # Main pipeline controller
│   │   ├── brain.py            # Gemini AI integration
│   │   ├── editor.py           # Tiered matching algorithm
│   │   ├── reflector.py        # Post-render AI reflection (New)
│   │   └── processors.py       # FFmpeg + librosa wrappers
│   ├── models.py               # Pydantic data schemas
│   └── main.py                 # FastAPI server
├── frontend/
│   ├── app/                    # Next.js pages
│   └── components/             # React components
├── data/
│   ├── cache/                  # Analysis + Standardization cache
│   └── results/                # Generated videos + Intelligence reports
└── ContextFiles/               # Extended documentation
```

---

## 🧪 Testing

### **Quick Test with X-Ray Output**
```bash
# Test specific reference
$env:TEST_REFERENCE = "ref4.mp4"
python test_ref.py

# Check results
# Video: data/results/mimic_output_ref4_vibes_test.mp4
# Log: data/results/ref4_xray_output.txt
```

### **X-Ray Output Includes:**
- Blueprint segment list (energy/vibe/arc for each segment)
- Clip registry (all 36 clips with energy/vibes/duration)
- Diversity report (unique clips used, repetitions)
- Energy compromise tracking
- Smart recommendations
- Vibe matching accuracy
- Timeline integrity check
- Material efficiency stats

### **Available Test References:**
- `ref4.mp4` - 14s, 30 segments, Travel/Nature/Friends heavy
- `ref5.mp4` - 16s, 21 segments, Nature/Travel focused
- `ref6.mp4` - 19s, 36 segments, Urban/Friends/Action
- `ref9.mp4` - 16s, 2 segments, Travel/Nature

---

## 🔧 Configuration

### **API Keys**
The system supports multiple Gemini API keys for quota management:

```env
# backend/.env file
GEMINI_API_KEY=primary_key_here

# Commented keys are automatically loaded as backups
#GEMINI_API_KEY=backup_key_1
#GEMINI_API_KEY=backup_key_2
```

**Automatic Rotation:**
- System loads all keys (active + commented)
- On quota limit, rotates to next key
- Currently supports 28 keys (560 requests/day capacity)

### **Cache Management**
```bash
# Clear clip analysis cache (force re-analysis)
Remove-Item data/cache/clip_comprehensive*.json -Force

# Clear reference cache
Remove-Item data/cache/ref_*.json -Force

# Clear standardized clips (force re-encoding)
Remove-Item data/cache/standardized/*.mp4 -Force

# Clear all cache
Remove-Item data/cache/* -Recurse -Force
```

**Note:** Standardized clips use hash-based naming (`std_{hash}.mp4`). If you modify a source clip, the system automatically detects the change and re-standardizes.

---

## 🎨 How It Works (The Action Era Workflow)

1. **Strategic Planning:** Gemini Advisor reviews your library and maps a path through the reference arc.
2. **Selective Assembly:** The Editor performs a weighted-greedy search for clips, balancing novelty vs. fidelity.
3. **Beat Synchronization:** Cuts are mathematically aligned to the reference's rhythmic anchors.
4. **[UPCOMING] Post-Render Audit:** Stage 6 Reflection pass.

---

## 🎨 Data Models

### **Segment** (Reference Analysis)
```json
{
  "id": 1,
  "start": 0.0,
  "end": 0.53,
  "energy": "High",
  "motion": "Dynamic",
  "vibe": "Action",
  "arc_stage": "Intro",
  "reasoning": "Fast camera pan with rapid movement"
}
```

### **ClipMetadata** (Clip Analysis)
```json
{
  "filename": "skateboard.mp4",
  "filepath": "/path/to/standardized/clip_001.mp4",
  "duration": 12.5,
  "energy": "High",
  "motion": "Dynamic",
  "vibes": ["Urban", "Action", "Sports"],
  "content_description": "Person skateboarding in urban plaza",
  "best_moments": {
    "High": {"start": 8.2, "end": 10.5, "reason": "Peak trick"},
    "Medium": {"start": 4.0, "end": 6.2, "reason": "Cruising"},
    "Low": {"start": 0.0, "end": 2.0, "reason": "Setup"}
  }
}
```

### **EditDecision** (Matching Result)
```json
{
  "segment_id": 1,
  "clip_path": "/path/to/clip_001.mp4",
  "clip_start": 8.2,
  "clip_end": 10.5,
  "timeline_start": 0.0,
  "timeline_end": 0.53,
  "reasoning": "🌟 ✨ New | High | Vibe:Action",
  "vibe_match": true
}
```

---

## 🐛 Troubleshooting

### **"All API keys exhausted"**
- **Cause:** Hit 20 requests/day limit on all keys
- **Solution:** Wait for quota reset or add more keys to `.env`

### **"Standardizing clips every time"**
- **Cause:** Cache directory doesn't exist or clips were modified
- **Solution:** Check `data/cache/standardized/` exists. System auto-creates on first run.

### **"Cuts don't align with beats"**
- **Cause:** BPM detection failed or wrong
- **Solution:** Check detected BPM in logs. Verify librosa is installed.

### **"Low diversity (clips repeated)"**
- **Cause:** Not enough clips for the reference length
- **Solution:** Add more clips or use shorter reference. System recommends specific types.

### **"Energy compromises"**
- **Cause:** Inventory doesn't match reference demand
- **Solution:** Check X-Ray recommendations for specific clip types to add

---

## 📚 Documentation

- **README.md** (this file) - Quick start and overview
- **ContextFiles/STATUS.md** - Complete project state and history
- **ContextFiles/ARCHITECTURE.md** - System design and algorithms
- **ContextFiles/DIAGNOSTIC_LOG.md** - Bug history and forensics
- **ContextFiles/NEXT_SESSION.md** - Action plan for next session

---

## 🎯 Current Status

### **Production-Ready Features**
- ✅ Reference analysis (scene cuts + BPM + vibes + semantic fields)
- ✅ Clip analysis (energy + motion + vibes + best moments)
- ✅ Tiered energy matching (prevents jarring transitions)
- ✅ Semantic matching (70-80% vibe accuracy)
- ✅ Beat synchronization (dynamic BPM)
- ✅ Persistent caching (standardized clips, analysis)
- ✅ API key rotation (28 keys, working correctly)
- ✅ Diversity optimization (90%+ unique clip usage)
- ✅ Smart recommendations (inventory gaps + quality improvements)
- ✅ X-Ray diagnostics (complete edit analysis)
- ✅ Timeline integrity (zero gaps/overlaps)
- ✅ Frame-accurate extraction

### **Performance Metrics**
- **Speed:** 15-20s total for 30-segment edits
- **Cache Hit Rate:** 100% on repeat runs
- **Diversity:** 90-100% unique clip usage
- **Vibe Accuracy:** 70-80% semantic matches
- **Timeline Precision:** <0.001s tolerance

### **Next Features**
- [ ] Frontend integration for recommendations
- [ ] Real-time progress updates
- [ ] Batch processing
- [ ] Custom vibe definitions
- [ ] Manual override controls

---

## 🤝 Contributing

This is a hackathon project for the **Gemini API Developer Competition**.

**Focus:** Transforming AI from a "Black Box" tool into a "Whitebox" Agentic Collaborator.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments
- Google Gemini API for Multimodal Reasoning
- FFmpeg for surgical video orchestration
- librosa for rhythmic analysis

**Built with ❤️ for the Gemini API Developer Competition**
