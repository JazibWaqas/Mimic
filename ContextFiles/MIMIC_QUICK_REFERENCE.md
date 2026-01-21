# 🧭 MIMIC - QUICK RECOVERY REFERENCE

**Use this when:** Code breaks, you're stuck, or need to understand the "why" behind a decision.

---

## 🎯 THE CORE IDEA (30 Seconds)

**What:** An AI agent that watches a viral video, extracts its editing structure (timing/pacing/energy), then applies that structure to user-provided clips.

**Why:** Content creators spend hours reverse-engineering viral videos. MIMIC does it in 60 seconds.

**How:**
1. FFmpeg runs visual scene detection → extracts physical cut timestamps.
2. Gemini 3 watches reference video using scene timestamps as anchors → extracts timing blueprint using compact codes (`HD, MS, LS`).
3. Gemini 3 analyzes user clips → classifies energy levels.
4. Editor matches clips to blueprint segments → aligns clips to physical visual anchors.
5. FFmpeg renders video → frame-perfect cuts matching reference rhythm.

**The Magic Moment:** Side-by-side comparison showing output perfectly matching reference beat drops.

---

## 🏆 HACKATHON ALIGNMENT

### We're Competing in: 🎨 Creative Autopilot Track

**Why We Win:**
- Uses Gemini 3 for **spatial-temporal video reasoning** (not just object detection)
- Combines AI reasoning with **precision tooling** (FFmpeg frame-perfect rendering)
- Produces **professional assets** (videos matching reference quality)
- **"Action Era" exemplar:** AI senses → plans → acts (no human in the loop)

### Judging Breakdown (How to Score 75+/100)

| Criteria | Weight | Our Strategy | Target Score |
|----------|--------|--------------|--------------|
| **Technical Execution** | 40% | Gemini 3 multimodal, clean architecture, robust fallbacks | 35/40 |
| **Innovation** | 30% | Novel: Structure analysis (not content), spatial-temporal reasoning | 25/30 |
| **Impact** | 20% | 50M+ creators, solves $50-200/hr editing problem in 60s | 15/20 |
| **Presentation** | 10% | 3-min demo with side-by-side, clear Gemini 3 explanation | 9/10 |
| **TOTAL** | 100% | | **84/100** |

---

## 🔧 THE CRITICAL PATH (What Must Work)

### 1. Gemini 3 API Connection
**Must:** Return valid JSON from video input  
**Fallback:** Linear blueprint (2s segments)  
**Test:** `python -c "from engine.brain import analyze_reference_video; print('OK')"`

### 2. FFmpeg Frame-Perfect Rendering
**Must:** Use `-c:v libx264 -preset ultrafast` (NOT `-c copy`)  
**Why:** Stream copy only cuts on keyframes (2-5s apart) = sync drift  
**Test:** Create 10s video, cut at 3.5s, verify duration is exactly 3.5s

### 3. Clip Matching Logic
**Must:** Match clips to segments by energy level  
**Fallback:** Round-robin if no matches  
**Test:** Mock blueprint with [High, Low, High], verify correct clips selected

### 4. Backend-Frontend Communication
**Must:** WebSocket connects for real-time progress updates  
**Why:** User sees live progress, not just loading spinner  
**Test:** Open browser console, should see WebSocket connection established

### 5. Session Management
**Must:** Files persist in `temp/{session_id}/` across pipeline steps  
**Why:** Standardization → Analysis → Rendering happens sequentially  
**Test:** Upload files, check `temp/{session_id}/clips/` exists

---

## 🚨 COMMON FAILURES & FIXES

### "Model gemini-3-flash-preview not found"
**Cause:** Wrong SDK version or API access  
**Fix:**
```bash
pip show google-generativeai  # Must be >=0.8.3
pip install --upgrade google-generativeai
```
**Fallback:** Try `gemini-3-pro-preview` or `gemini-exp-1206`

### "Output video duration doesn't match reference"
**Cause:** Using `-c copy` for concatenation (keyframe snapping)  
**Fix:** Change to `-c:v libx264 -preset ultrafast -crf 23` in `concatenate_videos()`  
**Why:** Re-encoding allows frame-perfect cuts

### "Clips don't match energy levels"
**Cause:** No clips match segment energy, matching fails  
**Fix:** This is expected! System should fall back to round-robin  
**Check:** Look for log message "No {energy} clips available, using fallback"

### "WebSocket connection failed / Progress bar not updating"
**Cause:** CORS not configured or wrong frontend URL  
**Fix:** Check `backend/main.py`:
```python
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Must be exact match
    ...
)
```
**Check:** Browser console should show `WebSocket connected`

### "Backend crashes on file upload"
**Cause:** Session directory doesn't exist  
**Fix:** Ensure `ensure_directory(f"temp/{session_id}/clips")` is called BEFORE saving files  
**Check:** `ls -la temp/` should show session folders

### "Audio out of sync"
**Cause:** Video duration ≠ audio duration  
**Fix:** Use `-shortest` flag in `merge_audio_video()` to trim to shortest stream  
**Why:** Prevents black frames or audio overrun

### "Frontend can't connect to backend"
**Cause:** Wrong API URL or backend not running  
**Fix:** 
```bash
# Check .env.local in frontend/
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local

# Verify backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

## 📐 ARCHITECTURE DECISION LOGIC

### When Gemini 3 Analyzes a Video, It Should:
✅ **DO:** Identify timing patterns (when cuts happen, energy shifts)  
✅ **DO:** Classify energy as Low/Medium/High based on motion/pacing  
❌ **DON'T:** Describe content ("there's a person dancing")  
❌ **DON'T:** Interpret meaning ("this is a happy video")

**Prompt Focus:** "Analyze STRUCTURE, not content. Return timing data."

### When Editor Matches Clips to Segments:
✅ **DO:** Prioritize energy matching (High clips → High segments)  
✅ **DO:** Use round-robin if no matches (output > perfection)  
✅ **DO:** Allow clip reuse (loop clips if not enough footage)  
❌ **DON'T:** Require 1:1 clip-to-segment mapping  
❌ **DON'T:** Fail if pool is empty (fallback to all clips)

**Priority:** Global pacing > Energy matching > Single clip integrity

### When FFmpeg Renders Video:
✅ **DO:** Re-encode during concatenation (frame-perfect cuts)  
✅ **DO:** Copy video stream during audio merge (no double-encode)  
✅ **DO:** Use `-shortest` to handle duration mismatches  
❌ **DON'T:** Use stream copy for concatenation (causes drift)  
❌ **DON'T:** Re-encode twice (quality loss + slow)

**Goal:** Frame accuracy + speed + quality

---

## 🎬 THE DEMO SCRIPT (For Context)

**[0:00-0:15] The Hook**
"Creators see viral videos and want to replicate the vibe. Manual analysis takes hours. Watch this."

**[0:15-0:45] The Setup**
- Show reference video (fast-paced TikTok with obvious beat drops)
- Show your random clips (gym, cooking, walking—completely different content)
- "These don't match at all."

**[0:45-1:30] The Magic**
- Upload to MIMIC, click "Generate Video"
- Show side-by-side comparison
- **Point out:** "Same beat drops. Same energy spikes. Same rhythm."
- "Gemini 3 didn't analyze content—it understood structure."

**[1:30-2:00] The Technical Flex**
- "Spatial-temporal reasoning: Gemini 3 watches videos and extracts timing patterns"
- "This is the Action Era: AI that creates, not just analyzes"
- "Professional editors charge $200/hour. MIMIC does it in 60 seconds."

**[2:00-2:30] The Closer**
- Show code snippet (Gemini 3 API call)
- Show architecture diagram
- "50M+ creators worldwide need this tool"

**[2:30-3:00] Q&A Buffer**
- "Want to try it? Here's the GitHub link."
- "Any questions about the Gemini 3 integration?"

---

## 📝 THE 200-WORD SUBMISSION TEXT

Use this for the hackathon submission form:

```
MIMIC uses Gemini 3's multimodal reasoning to analyze video structure—not 
content. Traditional computer vision detects objects. Gemini 3's spatial-
temporal understanding extracts editing patterns: when cuts happen, energy 
levels, rhythm changes.

We feed Gemini 3 a reference video with a specific prompt: "Ignore what's in 
the video. Analyze WHEN cuts occur, HOW FAST things move, and the RHYTHM of 
edits." Gemini 3 returns a structured JSON "blueprint" with millisecond-precise 
timing data.

We then analyze user-provided clips to classify their energy levels. Our 
matching algorithm maps clips to blueprint segments based on energy, creating 
an Edit Decision List (EDL). FFmpeg renders the video with frame-perfect cuts.

This is the "Action Era" in practice: Gemini 3 SENSES (watches video), PLANS 
(creates EDL), and our system ACTS (renders output). The result: anyone can 
steal the editing structure of viral content in under 60 seconds.

Key Gemini 3 Features Used:
- Multimodal video input
- Spatial-temporal reasoning
- Structured JSON output (response_mime_type)
- 1M token context for long videos
```

---

## 🔑 KEY DECISIONS (Why We Made Them)

### Why Gemini 3 (Not GPT-4V or Claude)?
- **Video reasoning:** Gemini 3 has native video understanding
- **Structured output:** `response_mime_type="application/json"` forces valid JSON
- **Hackathon requirement:** Must use Gemini 3 to compete
- **Context window:** 1M tokens = can handle long reference videos

### Why FFmpeg (Not OpenCV or MoviePy)?
- **Speed:** FFmpeg is 10x faster than Python libraries
- **Precision:** Frame-perfect cuts with re-encoding
- **Professional:** Industry-standard tool for video production
- **Reliability:** Battle-tested, deterministic output

### Why Next.js + FastAPI (Not Streamlit)?
- **Professional UI:** Looks like a product, not a prototype
- **Better deployment:** Vercel is more reliable than Streamlit Cloud
- **WebSocket support:** Real-time progress updates
- **Scalability:** Can add auth, payments, database later
- **Judge appeal:** Shows full-stack capability (+5 points)

### Why Energy-Based Matching (Not ML Embeddings)?
- **Interpretability:** Users understand "High/Medium/Low energy"
- **Speed:** No model training or inference needed
- **Gemini 3 capability:** AI can classify energy from video
- **Robustness:** Simple fallback logic (round-robin)

---

## 💡 WHEN CURSOR ASKS "WHY?"

### "Why do we need frame-perfect cuts?"
**Answer:** Reference videos have beats at specific timestamps (e.g., 3.5s, 7.2s). 
If we cut on keyframes (every 2-5s), we'll be off-beat. Judges will notice.

### "Why not just use stream copy? It's faster."
**Answer:** Stream copy (`-c copy`) only cuts on keyframes. For a 30fps video, 
keyframes might be every 60-150 frames (2-5 seconds apart). If Gemini 3 says 
"cut at 3.5s" but the nearest keyframe is at 5.0s, we're 1.5 seconds off—
the beat sync is completely wrong.

### "Why do we need three Gemini models?"
**Answer:** APIs fail. If `gemini-3-flash-preview` is down during the demo, 
we automatically try `gemini-3-pro-preview`, then `gemini-exp-1206`. This 
ensures the demo never crashes due to API issues.

### "Why do we prioritize pacing over perfect matches?"
**Answer:** If we can't find a "High" energy clip for a "High" segment, we 
STILL need to render something. Using a "Medium" clip is better than crashing. 
The global pacing (timing) is more important than perfect energy matching.

### "Why is this better than manual editing?"
**Answer:** Professional video editors:
1. Watch reference frame-by-frame to identify cuts (~30 min)
2. Mark timing in editing software (~15 min)
3. Manually trim and arrange clips (~45 min)
4. Review and adjust (~30 min)
**Total: 2+ hours, $50-200 cost**

MIMIC does steps 1-3 automatically in <60 seconds.

### "Why separate frontend and backend?"
**Answer:** 
- **Development:** Test backend with curl before UI exists
- **Deployment:** Can scale backend independently (add queue, workers)
- **Debugging:** Isolate issues to frontend vs backend
- **Professional:** Shows proper architecture (not all-in-one script)

---

## 🎯 SUCCESS SIGNALS (How to Know It's Working)

### During Build:
✅ No import errors (`python -c "import engine.brain"`)  
✅ Gemini 3 returns valid JSON (test with 5s video)  
✅ FFmpeg commands run without errors  
✅ Test video duration matches expected (±0.01s)  
✅ Backend `/health` endpoint returns 200  
✅ Frontend pages render without errors  
✅ WebSocket connects in browser console  

### During Demo:
✅ Upload works (files appear in backend session folder)  
✅ Progress bar updates in real-time (WebSocket working)  
✅ Output video appears (file size >100KB)  
✅ Side-by-side shows aligned timing  
✅ Download button works  
✅ Judges say "Wait, how did it do that?"  

### For Submission:
✅ 3-min video recorded and uploaded  
✅ GitHub repo is public with clear README  
✅ 200-word description emphasizes Gemini 3 usage  
✅ Demo link works (deployed or local setup guide)  

---

**When in doubt:** Re-read the Strategic Context section in the main document. 
It explains the "why" behind every technical decision.
