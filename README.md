# MIMIC - AI-Powered Video Style Transfer

**Transform your raw clips into professionally-edited videos by learning from examples.**

MIMIC analyzes a reference video's editing style (cuts, pacing, energy, narrative arc) and automatically recreates that style using your clips. Think "Instagram Reels editor that understands the 'why' behind professional edits."

**Version:** V7.0 - Enhanced Analysis & Gemini Advisor (January 27, 2026)

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

### **Smart Matching (V7.0)**
- **Tiered Energy Eligibility:** High segments can use High+Medium clips, Low can use Low+Medium, Medium can use any
- **Discovery Bonus:** Prioritizes unused clips (+40 points) to maximize variety
- **Vibe-Aware Selection:** Aligns Urban clips with Urban segments, Nature with Nature, etc. (+15 points)
- **Arc Stage Coherence:** Uses establishing shots for Intros, rapid cuts for Peaks (+10 points)
- **Beat Synchronization:** Snaps cuts to detected BPM for musical alignment
- **Variety Optimization:** 5-second cooldown prevents visual monotony (-40 points)
- **Usage Penalty:** Discourages clip repetition (-25 points per reuse)

### **Performance & Caching**
- **Persistent Standardization Cache:** Clips are standardized once and reused forever (hash-based)
- **Gemini Analysis Cache:** AI analysis is cached per clip (never re-analyzed)
- **Reference Cache:** Reference analysis cached with scene hint fingerprinting
- **Speed:** 15-20 seconds total for 30-segment edits (down from 10+ minutes)

### **Transparent AI**
- **Reasoning Logs:** See why the AI chose each clip
- **Diversity Reports:** Track unique clip usage and repetitions
- **Energy Compromise Tracking:** Know when exact energy wasn't available
- **Material Suggestions:** Get specific recommendations on what clips to add
- **X-Ray Output:** Complete diagnostic logs for every edit

---

## 📋 Recent Updates (V7.0 - January 27, 2026)

### **Major Improvements**
- **✅ Enhanced Reference Analysis:** Extracts narrative intent, content requirements, experience goals, and text overlays
- **✅ Enhanced Clip Analysis:** Fixed energy bias, added intensity, granular motion types, semantic content analysis
- **✅ Gemini Advisor:** Strategic planning layer that provides clip suggestions per arc stage and library assessment
- **✅ Tiered Energy Matching:** Intelligent energy eligibility prevents jarring transitions
- **✅ Persistent Standardization Cache:** `data/cache/standardized/` stores hash-based standardized clips
- **✅ Discovery Bonus System:** Prioritizes unused clips for maximum variety
- **✅ Compromise Tracking:** System logs every energy tradeoff and suggests improvements
- **✅ Smart Recommendations:** Actionable feedback on inventory gaps and quality improvements
- **✅ X-Ray Diagnostics:** Ultra-detailed test output with blueprint, clip registry, and reasoning

### **Performance Gains**
- **Standardization:** Cached clips copy in <1s (vs 5-10min re-encoding)
- **Total Pipeline:** 15-20s for 30-segment edits (previously 600s+)
- **Cache Hit Rate:** 100% on repeat runs with same clips

### **Quality Improvements**
- **Diversity:** Consistently achieves 90%+ unique clip usage
- **Vibe Matching:** 70-80% semantic accuracy across test references
- **Timeline Integrity:** Zero gaps/overlaps with mathematical continuity enforcement
- **Energy Coherence:** Tiered system prevents Low→High jumps

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

**Option 1: Full Stack**
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
│   │   └── processors.py       # FFmpeg + librosa wrappers
│   ├── utils/
│   │   └── api_key_manager.py  # Multi-key rotation (28 keys)
│   ├── models.py               # Pydantic data schemas
│   └── main.py                 # FastAPI server
├── frontend/
│   ├── app/                    # Next.js pages
│   └── components/             # React components
├── data/
│   ├── samples/                # Test videos
│   │   ├── reference/          # Reference videos (ref4.mp4, ref5.mp4, etc.)
│   │   └── clips/              # User clips (36 clips for testing)
│   ├── cache/                  # Analysis cache
│   │   ├── standardized/       # Persistent standardized clips (hash-based)
│   │   ├── clip_comprehensive_*.json  # Clip analysis cache
│   │   └── ref_*_h*.json       # Reference analysis cache
│   └── results/                # Generated videos + X-Ray logs
├── ContextFiles/               # Documentation
│   ├── STATUS.md               # Complete project state
│   ├── ARCHITECTURE.md         # System design (NEW)
│   └── ...
├── test_ref.py                 # X-Ray test runner
└── README.md                   # This file
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

## 📊 How It Works

### **Pipeline Stages**

**Stage 1: Validation**
```
1. Check reference video exists
2. Check clip directory has files
3. Validate API key is present
```

**Stage 2: Reference Analysis**
```
1. Detect visual scene cuts (FFmpeg)
2. Extract audio and detect BPM (librosa)
3. Analyze segments with Gemini:
   - Energy level (Low/Medium/High)
   - Motion type (Static/Dynamic)
   - Content vibe (Nature, Urban, Action, etc.)
   - Arc stage (Intro/Build-up/Peak/Outro)
   - Reasoning for classification
4. Cache results with scene hint fingerprint
```

**Stage 3: Clip Analysis**
```
1. For each clip, analyze with Gemini:
   - Overall energy and motion
   - Content description
   - Aesthetic vibes (2-4 tags)
   - Best moments for each energy level
2. Cache results (never re-analyzed)
3. Standardize clips for rendering:
   - Check persistent cache (data/cache/standardized/)
   - If cached: copy in <1s
   - If new: standardize and save to cache
```

**Stage 4: Intelligent Matching**
```
1. Pre-edit demand analysis:
   - Count required High/Medium/Low clips
   - Compare to available inventory
   - Report deficits

2. For each reference segment:
   - Filter clips by tiered energy eligibility
   - Score each eligible clip:
     * Discovery bonus: +40 if unused
     * Energy match: +20 exact, +5 adjacent
     * Vibe match: +15 if semantic match
     * Arc stage: +10 if relevant
     * Usage penalty: -25 per previous use
     * Cooldown: -40 if used <5s ago
   - Select highest-scoring clip
   - Extract best moment for segment's energy
   - Record reasoning and vibe match status
   
3. Post-edit summary:
   - Diversity report (unique clips used)
   - Compromise tracking (energy tradeoffs)
   - Smart recommendations (what to add)
```

**Stage 5: Rendering**
```
1. Generate beat grid from detected BPM
2. Snap cut points to nearest beats (within tolerance)
3. Extract clip segments via FFmpeg (frame-accurate)
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
