# MIMIC - AI-Powered Video Style Transfer

**Transform your raw clips into professionally-edited videos by learning from examples.**

MIMIC analyzes a reference video's editing style (cuts, pacing, energy, narrative arc) and automatically recreates that style using your clips. Think "Instagram Reels editor that understands the 'why' behind professional edits."

**Version:** V6.1 - Semantic Reference Analysis + System Hardening (January 22, 2026)

---

## 🎯 What It Does

1. **Upload a reference video** (the style you want to mimic)
2. **Upload your raw clips** (your content)
3. **MIMIC analyzes both** using Gemini 3 AI
4. **Get a professionally-edited video** matching the reference's rhythm

**Example:**
- Reference: A fast-paced TikTok dance video (30 cuts in 15 seconds)
- Your Clips: Random footage of you dancing
- Output: Your footage edited with the same fast-paced style

---

## ✨ Key Features

### **Intelligent Analysis**
- **Scene Detection:** FFmpeg detects every visual cut in the reference
- **BPM Detection:** librosa extracts the music tempo for beat-perfect cuts
- **Semantic Understanding:** Gemini 3 identifies energy, motion, content vibes, and narrative arc
- **Narrative Arc Analysis:** Understands Intro/Build-up/Peak/Outro progression
- **Best Moment Extraction:** Pre-computes optimal segments from each clip

### **Smart Matching**
- **Semantic Matching:** Matches clips to segments based on content themes and arc relevance
- **Vibe-Aware Selection:** Aligns Urban clips with Urban segments, Nature with Nature, etc.
- **Arc Stage Coherence:** Uses establishing shots for Intros, rapid cuts for Peaks
- **Beat Synchronization:** Snaps cuts to detected BPM for musical alignment
- **Variety Optimization:** 5-second cooldown prevents visual monotony

### **Transparent AI**
- **Reasoning Logs:** See why the AI chose each clip
- **Material Suggestions:** Get feedback on missing clip types
- **Thinking Display:** Watch the AI's decision-making process

---

## 📋 Recent Updates (V6.1 - January 22, 2026)

### **Major Improvements**
- **✅ Semantic Reference Analysis:** Reference videos now generate complete vibe/arc_stage/reasoning metadata even with scene hints
- **✅ System Hardening:** Fixed ZeroDivisionError crashes, frame-accurate extraction, and API key rotation issues
- **✅ Cache Enhancement:** V6.1 version with improved invalidation using hint-based hashing
- **✅ Error Resilience:** Cross-platform error handling and timeline drift protection

### **Technical Fixes**
- **ZeroDivisionError Prevention:** BPM safety guards and validation
- **Frame-Accurate Cutting:** Re-encoding instead of stream copy for precise timestamps
- **API Key Rotation:** Model propagation across all clips
- **Timeline Integrity:** Mathematical continuity enforcement
- **Robust Parsing:** Improved JSON extraction and error handling
- **Independent Cache Versioning:** Reference and clip caches versioned separately for efficiency

### **Quality Improvements**
- **Semantic Matching:** Vibe and arc stage alignment for better content coherence
- **Reference Fidelity:** Preserves original cut rhythm when scene hints exist
- **Variety Optimization:** Prevents repetition with cooldown system
- **Professional Pacing:** Adaptive timing based on narrative arc stage

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.10+
- FFmpeg installed and in PATH
- Node.js 18+ (for frontend)
- Google Gemini API key

### **Installation**

```bash
# Clone repository
git clone https://github.com/yourusername/Mimic.git
cd Mimic

# Backend setup
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Frontend setup
cd ../frontend
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

Visit `http://localhost:3000`

---

## 📁 Project Structure

```
Mimic/
├── backend/
│   ├── engine/
│   │   ├── orchestrator.py    # Main pipeline controller
│   │   ├── brain.py            # Gemini AI integration
│   │   ├── editor.py           # Clip matching algorithm
│   │   └── processors.py       # FFmpeg + librosa wrappers
│   ├── utils/
│   │   └── api_key_manager.py  # Multi-key rotation
│   ├── models.py               # Pydantic data schemas
│   └── main.py                 # FastAPI server
├── frontend/
│   ├── app/                    # Next.js pages
│   └── components/             # React components
├── data/
│   ├── samples/                # Test videos
│   ├── cache/                  # Analysis cache
│   └── results/                # Generated videos
├── STATUS.md                   # Complete project context
├── DIAGNOSTIC_LOG.md           # Bug forensics
├── NEXT_SESSION.md             # Action plan
└── README.md                   # This file
```

---

## 🧪 Testing

### **Quick Test**
```bash
# Test with sample data
python test_ref4_v4.py
```

### **Check API Keys**
```bash
# Verify all keys are working
python test_api_keys.py
```

### **Manual Test**
1. Place reference video in `data/samples/reference/`
2. Place clips in `data/samples/clips/`
3. Run pipeline via API or test script

---

## 🔧 Configuration

### **API Keys**
The system supports multiple Gemini API keys for quota management:

```env
# .env file
GEMINI_API_KEY=primary_key_here

# Commented keys are automatically loaded as backups
#GEMINI_API_KEY=backup_key_1
#GEMINI_API_KEY=backup_key_2
```

**Automatic Rotation:**
- System loads all keys (active + commented)
- On quota limit, rotates to next key
- Supports up to 11 keys (220 requests/day capacity)

### **Cache Management**
```bash
# Clear clip cache (force re-analysis)
Remove-Item data/cache/clip_comprehensive*.json -Force

# Clear reference cache
Remove-Item data/cache/ref_*.json -Force

# Clear all cache
Remove-Item data/cache/*.json -Force
```

---

## 📊 How It Works

### **Pipeline Stages**

**Stage 1: Reference Analysis**
```
1. Detect visual scene cuts (FFmpeg)
2. Extract audio and detect BPM (librosa)
3. Analyze segments with Gemini:
   - Energy level (Low/Medium/High)
   - Motion type (Static/Dynamic)
   - Content vibe (Nature, Urban, Action, etc.)
   - Reasoning for classification
```

**Stage 2: Clip Analysis**
```
1. Analyze each clip with Gemini:
   - Overall energy and motion
   - Content description
   - Aesthetic vibes (2-4 tags)
   - Best moments for each energy level
2. Cache results for future use
```

**Stage 3: Intelligent Matching**
```
1. For each reference segment:
   - Score clips by vibe match (10 points)
   - Penalize frequently-used clips (-0.1 per use)
   - Select highest-scoring clip
   - Extract best moment for segment's energy
   - Record reasoning for selection
```

**Stage 4: Rendering**
```
1. Generate beat grid from detected BPM
2. Snap cut points to nearest beats
3. Extract clip segments via FFmpeg
4. Concatenate segments
5. Merge with reference audio
6. Output final video
```

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
  "reasoning": "Fast camera pan with rapid movement"
}
```

### **ClipMetadata** (Clip Analysis)
```json
{
  "filename": "skateboard.mp4",
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
  "clip_path": "/path/to/clip",
  "clip_start": 8.2,
  "clip_end": 10.5,
  "reasoning": "Semantic Match: Vibe 'Action' matches clip tags",
  "vibe_match": true
}
```

---

## 🐛 Troubleshooting

### **"All API keys exhausted"**
- **Cause:** Hit 20 requests/day limit on all keys
- **Solution:** Wait for quota reset (time unknown) or add more keys

### **"No vibes in cache"**
- **Cause:** Old cache from before vibes feature
- **Solution:** Delete cache and re-run analysis

### **"403 Permission Denied"**
- **Cause:** Trying to access file uploaded by different key
- **Solution:** Should be fixed - if persists, check upload is inside retry loop

### **"Cuts don't align with beats"**
- **Cause:** BPM detection failed or wrong
- **Solution:** Check detected BPM in logs, verify librosa is installed

---

## 📚 Documentation

- **STATUS.md** - Complete project context and current state
- **DIAGNOSTIC_LOG.md** - Bug history and forensics
- **NEXT_SESSION.md** - Immediate action plan
- **FIXES_APPLIED.md** - Chronological fix log
- **ONBOARDING.md** - New developer guide

---

## 🎯 Roadmap

### **Current Status: MVP Complete & Tested**
- ✅ Reference analysis (scene cuts + BPM + vibes + semantic fields)
- ✅ Clip analysis (energy + motion + vibes + best moments)
- ✅ Semantic matching (vibe-aware selection, 69%+ match rate)
- ✅ Beat synchronization (dynamic BPM)
- ✅ API key rotation (28 keys, working correctly)
- ✅ Full pipeline tested (ref4, ref5, refrence2 successfully rendered)
- ✅ Timeline integrity verified (no gaps/overlaps)
- ✅ Frame-accurate extraction confirmed

### **Next Features:**
- [ ] Material suggestions UI
- [ ] Reasoning display in frontend
- [ ] Demo video recording
- [ ] Hackathon submission

---

## 🤝 Contributing

This is a hackathon project for the Gemini API Developer Competition.

**Theme:** Action Era - Creative Autopilot  
**Focus:** Vibe Engineering - Understanding and matching aesthetic themes

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Google Gemini API for video analysis
- FFmpeg for video processing
- librosa for audio analysis
- Next.js and FastAPI for the stack

---

**Built with ❤️ for the Gemini API Developer Competition**
