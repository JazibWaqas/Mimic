# MIMIC — AI Video Editor That Thinks Like a Director

**🏆 Built for the Google Gemini API Developer Competition**

> *"The AI video editor that understands the soul behind the edit—and can explain every creative decision it makes."*

MIMIC is an intent-driven video editing system powered by **Google Gemini 3**. Instead of producing black-box edits, MIMIC translates human creative intent into deterministic editorial decisions and provides transparent explanations for every choice it makes.

---

## 🎯 What Makes MIMIC Different

Most AI video editors are black boxes—you upload clips, get a video, and have no idea *why* the AI made those choices. MIMIC is different:

1. **Intent-Driven**: Accepts natural language prompts or reference videos as creative direction
2. **Transparent**: Generates a "Vault Intelligence Report" explaining every editorial decision
3. **Narrative-First**: Understands emotional arcs, pacing, and storytelling—not just visual matching
4. **Agentic**: Plans before executing, reflects after rendering, and suggests improvements

**Example Prompt:**
> "Create a joyful childhood memory video. Start peaceful, build through playful energy, peak with celebration, end bittersweet. Make it feel like a memory you didn't know you missed."

**MIMIC's Response:** A 27-second edit with 12 cuts, perfect beat sync, and a full explanation of why each clip was chosen.

---

## 🧠 Gemini 3 Integration (Hackathon Compliance)

MIMIC uses **Google Gemini 3 Flash** as its core intelligence layer across **6 distinct stages**:

### **1. Multimodal Clip Analysis**
- **What:** Gemini analyzes every uploaded video clip to understand its visual content, emotional tone, energy level, and narrative weight
- **Why:** Enables semantic matching beyond simple object detection
- **API Call:** `gemini-3-flash-preview` with video file upload
- **Output:** Structured metadata (energy: High/Medium/Low, vibes: joy/peace/celebration, best moments, subject matter)

### **2. Blueprint Generation (Prompt Mode)**
- **What:** Gemini converts natural language creative prompts into a structured "Director's Blueprint"
- **Why:** Translates subjective creative intent into deterministic editorial plans
- **API Call:** `gemini-3-flash-preview` with text prompt + music BPM context
- **Output:** 4-segment narrative arc with energy levels, pacing strategy, and emotional beats

### **3. Reference Analysis (Reference Mode)**
- **What:** Gemini analyzes professional edits to extract their "editorial DNA"
- **Why:** Enables style transfer—recreating viral edit structures with user's own clips
- **API Call:** `gemini-3-flash-preview` with reference video + detected cut timestamps
- **Output:** Semantic understanding of each segment's intent, vibe, and narrative purpose

### **4. Strategic Advisory**
- **What:** Gemini reviews the user's clip library against the blueprint to identify gaps
- **Why:** Provides intelligent constraint handling and strategic guidance
- **API Call:** `gemini-3-flash-preview` with blueprint + clip inventory
- **Output:** AdvisorHints with energy overrides, missing motifs, and strategic recommendations

### **5. Vault Translation**
- **What:** Gemini translates technical reasoning into human-readable creative explanations
- **Why:** Makes AI decisions transparent and defensible
- **API Call:** `gemini-3-flash-preview` with structured reasoning data
- **Output:** VaultReport with decision stream, tradeoff explanations, and improvement prescriptions

### **6. Large Context Window Utilization**
- **Why It Matters:** MIMIC holds the entire edit (blueprint + all clip metadata + music structure + narrative arc) in Gemini's context window simultaneously
- **Benefit:** Enables holistic decision-making where each cut serves the *whole* story, not just individual moments

**Total Gemini API Calls Per Edit:** 3-4 (Clip Analysis + Blueprint/Reference + Vault)

---

## ✨ Key Features

### **Two Editing Modes**

#### **Prompt Mode** (Creative Generation)
- Input: Natural language prompt + music + clips
- Output: Original edit created from scratch
- Use Case: "Make me a nostalgic childhood reel"

#### **Reference Mode** (Style Transfer)
- Input: Professional reference video + your clips
- Output: Recreation of reference's structure with your footage
- Use Case: "Recreate this viral TikTok with my vacation clips"

### **The Vault Intelligence Report**
MIMIC's killer feature—a full creative audit that includes:
- **Decision Stream**: Why each clip was chosen for each segment
- **Tradeoff Explanations**: Where the AI compromised and why
- **System Telemetry**: Energy distribution, vibe matching accuracy, diversity metrics
- **Prescriptions**: Specific suggestions for what to film next to improve the edit

### **Hybrid Rhythmic Intelligence**
- Detects BPM from music (librosa)
- Identifies visual cuts from reference (FFmpeg scene detection)
- Merges both into a "Hybrid Sync" system that prioritizes storytelling over rigid beat-snapping

### **Frame-Perfect Rendering**
- 30fps CFR lock (no floating framerates)
- Zero-drift timeline integrity (±0.001s tolerance)
- AAC audio sample lock (no micro-clicks)

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.10+
- FFmpeg installed and in PATH
- Node.js 18+
- Google Gemini API key

### **Installation**

```bash
# Clone repository
git clone https://github.com/JazibWaqas/Mimic.git
cd Mimic

# Backend setup
python -m venv .venv
.\.venv\Scripts\activate  # Windows (.venv/bin/activate on Unix)
pip install -r backend/requirements.txt

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > backend/.env

# Frontend setup
cd frontend
npm install
```

### **Running the App**

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Open http://localhost:3000
```

### **Quick Demo**

1. Navigate to **Studio** page
2. Upload 5-10 video clips (MP4 format)
3. Enter a creative prompt or upload a reference video
4. Click **Execute**
5. View the generated edit
6. Check the **Vault** tab to see AI reasoning

**First run:** ~30 seconds (clips are analyzed)  
**Subsequent runs:** ~15 seconds (cached analysis)

---

## 📁 Project Structure

```
Mimic/
├── backend/
│   ├── engine/
│   │   ├── orchestrator.py    # Main pipeline controller
│   │   ├── brain.py            # Gemini 3 integration (clip analysis, reference analysis)
│   │   ├── generator.py        # Gemini 3 blueprint generation (Prompt Mode)
│   │   ├── editor.py           # Clip matching algorithm
│   │   ├── reflector.py        # Gemini 3 Vault translation
│   │   └── processors.py       # FFmpeg + librosa wrappers
│   ├── models.py               # Pydantic data schemas
│   └── main.py                 # FastAPI server
├── frontend/
│   ├── app/                    # Next.js pages (Studio, Vault, Library)
│   └── components/             # React components
├── data/
│   ├── cache/                  # Analysis + Standardization cache
│   └── results/                # Generated videos + Vault reports
└── .agent/                     # Internal documentation
```

---

## 🛠️ Tech Stack

**AI & Intelligence:**
- Google Gemini 3 Flash (multimodal vision, reasoning, large context)

**Backend:**
- Python 3.11
- FastAPI (REST API + WebSocket streaming)
- Pydantic (data validation)
- FFmpeg (video processing)
- Librosa (BPM detection & audio analysis)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion

---

## 🎬 How It Works (The Pipeline)

### **Stage 1: Input Validation**
- Validates video formats, durations, and file integrity

### **Stage 2: Blueprint Generation**
- **Prompt Mode:** Gemini generates a Director's Blueprint from natural language
- **Reference Mode:** Gemini analyzes reference video structure

### **Stage 3: Clip Analysis**
- Gemini analyzes all user clips in parallel (multimodal vision)
- Extracts energy, vibes, best moments, subject matter
- Results are cached permanently (content-hash based)

### **Stage 4: Strategic Advisory**
- Gemini reviews library vs. blueprint
- Identifies energy gaps, missing motifs
- Provides strategic overrides (e.g., "use Medium energy for Intro")

### **Stage 5: Edit Sequence Creation**
- Weighted scoring algorithm matches clips to blueprint
- Factors: energy match, vibe alignment, diversity, narrative continuity
- Beat synchronization for musical alignment

### **Stage 6: Rendering**
- FFmpeg extracts segments, concatenates, merges audio
- Applies visual styling (color grading, text overlays)
- Enforces 30fps CFR lock for frame-perfect output

### **Stage 7: Vault Generation**
- Gemini translates technical reasoning into human explanations
- Generates decision stream, tradeoff analysis, prescriptions
- Cached by EDL hash for instant retrieval

---

## 📊 Performance Metrics

**From Real Demo Run (text_prompt_text_music_5_v9):**
- **Clips Analyzed:** 24 (all cached after first run)
- **Segments Created:** 4
- **Cuts Made:** 12
- **Processing Time:** 15.1 seconds
- **Gemini Calls:** 2 (Blueprint + Vault, clips were cached)
- **Timeline Drift:** +0.28s (within tolerance)
- **Vibe Matching Accuracy:** 66.7%
- **Diversity:** 100% (no repeated clips)

**System Capabilities:**
- **Clip Library Size:** Tested with 220+ clips
- **Max Edit Duration:** 60+ seconds
- **API Reliability:** 30-key rotation pool for rate limit handling
- **Cache Hit Rate:** 95%+ on subsequent runs

---

## 🎯 Hackathon Compliance Checklist

✅ **NEW Application:** Built specifically for Gemini API Developer Competition  
✅ **Gemini 3 Integration:** Core intelligence layer (6 distinct API usage patterns)  
✅ **Not Prompt-Only:** Full-stack application with backend pipeline, frontend UI, video processing  
✅ **Not Baseline RAG:** Uses multimodal vision, reasoning, and large context windows  
✅ **Agentic Usage:** Plans → Executes → Reflects → Suggests (full agentic loop)  
✅ **Demo Video:** Public YouTube video showing system in action  
✅ **Public Repository:** Open-source codebase with clear documentation  
✅ **Testing Instructions:** Provided in this README  

---

## 🎥 Demo Video

**Watch MIMIC in action:** [YouTube Demo Link](https://youtu.be/p9m0EOVyd5s)

The demo shows:
1. Prompt Mode: Creating a childhood memory edit from natural language
2. Reference Mode: Replicating a professional edit's structure
3. Vault walkthrough: Exploring AI reasoning and decision explanations

---

## 🧪 Testing Instructions

1. **Clone and install** (see Quick Start above)
2. **Add Gemini API key** to `backend/.env`
3. **Start backend:** `cd backend && uvicorn main:app --reload --port 8000`
4. **Start frontend:** `cd frontend && npm run dev`
5. **Navigate to** `http://localhost:3000`
6. **Try Prompt Mode:**
   - Click "Studio"
   - Upload 5-10 clips
   - Enter: "Create a joyful childhood memory video"
   - Click "Execute"
   - View result + check Vault tab
7. **Try Reference Mode:**
   - Upload a reference video
   - Upload your clips
   - Click "Execute"
   - Compare original vs. recreation

**Note:** First run takes ~30s (clip analysis). Subsequent runs are ~15s (cached).

---

## 📚 Extended Documentation

- **README.md** (this file) - Overview and quick start
- **ContextFiles/ARCHITECTURE.md** - Complete system design
- **ContextFiles/SYSTEM_STATE.md** - Current capabilities and roadmap

---

## 🤝 Contributing

This is a hackathon project for the **Gemini API Developer Competition**.

**Philosophy:** Transforming AI from a "Black Box" tool into a transparent, explainable creative partner.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Google Gemini 3** for multimodal reasoning and large context windows
- **FFmpeg** for surgical video processing
- **Librosa** for audio analysis

---

## 💡 The Vision

MIMIC isn't here to replace video editors. It's here to do the heavy lifting—the analysis, the matching, the first assembly—so human directors can focus on the final 10%: the refinement, the soul.

Because at the end of the day, the best edits are still made by humans. MIMIC just makes sure we're starting from a place of intelligence, not guesswork.

**After all, who doesn't like to be the main character of their own story?**

---

**Built with ❤️ for the Gemini API Developer Competition**
