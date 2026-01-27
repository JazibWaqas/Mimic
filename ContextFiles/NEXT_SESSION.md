# MIMIC - Next Session Action Plan

**Last Updated:** January 27, 2026  
**Current Version:** V7.0 (Enhanced Analysis + Advisor)  
**Status:** ✅ Core complete, ⚠️ Reference cache fallback fix needed

---

## 🎯 Session Objectives

### Primary Goal (IMMEDIATE)
Fix reference cache fallback issue and validate Advisor system with proper reference data.

### Secondary Goals
- Test Advisor output quality and tune bonus weights
- Integrate Advisor suggestions into UI
- Create demo video
- Polish user experience
- Final testing and validation

---

## 📋 Immediate Tasks (Priority Order)

### 1. Fix Reference Cache Fallback (CRITICAL - DO FIRST)

**Issue:** When orchestrator detects scene timestamps and finds old hash-based cache (wrong version), it deletes it but doesn't check fallback `hints0.json` before re-analyzing.

**Location:** `backend/engine/brain.py` lines 870-888

**Fix Required:**
After deleting wrong-version cache (line 872), check if `fallback_cache_file` exists and is valid before proceeding to re-analysis.

**Code Change:**
```python
if cache_version != REFERENCE_CACHE_VERSION:
    print(f"[CACHE] Reference version mismatch ({cache_version} vs {REFERENCE_CACHE_VERSION}). Re-analyzing...")
    cache_file.unlink()
    # ADD: Check fallback before re-analyzing
    if fallback_cache_file and fallback_cache_file.exists():
        # Try loading fallback
        # If valid, use it; otherwise continue to re-analysis
```

**Testing:**
1. Run `test_ref.py` with ref5.mp4
2. Verify it uses `ref_d04cf94d4d8a_hints0.json` (v7.0) instead of re-analyzing
3. Confirm reference analysis shows v7.0 fields (narrative_message, must_have_content, etc.)

**Estimated Time:** 30 minutes

---

### 2. Test Advisor with Proper Reference (HIGH PRIORITY)

**Task:** Re-run pipeline with fixed cache to validate Advisor output

**Steps:**
1. Fix cache fallback (Task 1)
2. Run `test_ref.py` with ref5.mp4
3. Verify Advisor receives proper v7.0 reference data
4. Check Advisor suggestions are meaningful
5. Validate Advisor bonus improves clip selection

**Expected Output:**
- Advisor suggestions per arc stage
- Library assessment (strengths/gaps/confidence)
- Overall strategy
- Improved clip selection based on narrative intent

**Estimated Time:** 1 hour

---

### 3. Frontend Integration (MEDIUM PRIORITY)

**Task:** Display smart recommendations in UI

**Current State:**
- Recommendations are generated in backend (`editor.py`)
- Logged to console and X-Ray output
- Not visible in frontend UI

**Implementation:**
```typescript
// Add to PipelineResult interface
interface PipelineResult {
  // ... existing fields
  recommendations?: {
    inventory_gaps?: {
      energy: string;  // "High", "Medium", "Low"
      count: number;
      examples: string;
    }[];
    quality_improvements?: {
      type: string;  // "energy_compromise"
      count: number;
      suggestion: string;
    }[];
  };
  diversity_report?: {
    unique_clips_used: number;
    total_clips: number;
    repeated_clips?: {
      name: string;
      count: number;
    }[];
  };
}
```

**Files to Modify:**
- `backend/models.py` - Add recommendation fields to PipelineResult
- `backend/engine/orchestrator.py` - Include recommendations in return
- `frontend/components/ResultsPanel.tsx` - Display recommendations

**Estimated Time:** 2-3 hours

---

### 2. Real-Time Progress Updates (MEDIUM PRIORITY)

**Task:** Show live progress during pipeline execution

**Current State:**
- Progress callback exists but not used
- Frontend shows loading spinner only

**Implementation:**
```python
# Backend: orchestrator.py
def update_progress(step, total, message):
    if progress_callback:
        progress_callback({
            "step": step,
            "total": total,
            "message": message,
            "percentage": (step / total) * 100
        })
```

```typescript
// Frontend: Use WebSocket or SSE
const [progress, setProgress] = useState({
  step: 0,
  total: 5,
  message: "Initializing...",
  percentage: 0
});
```

**Files to Modify:**
- `backend/main.py` - Add WebSocket endpoint
- `frontend/app/page.tsx` - Connect to WebSocket
- `frontend/components/ProgressBar.tsx` - Create component

**Estimated Time:** 3-4 hours

---

### 3. Demo Video Recording (HIGH PRIORITY)

**Task:** Create compelling demo video for hackathon

**Script Outline:**
1. **Intro (10s)**
   - "Transform your raw clips into professional edits"
   - Show MIMIC logo

2. **Problem (15s)**
   - "Editing videos is time-consuming"
   - "Professional edits require skill and experience"

3. **Solution (20s)**
   - "MIMIC learns from professional examples"
   - Show reference video upload
   - Show clip upload

4. **Magic (30s)**
   - "AI analyzes the reference style"
   - Show analysis visualization
   - "Matches your clips to the rhythm"
   - Show matching process

5. **Result (20s)**
   - Side-by-side comparison
   - Show diversity report
   - Show recommendations

6. **Call to Action (5s)**
   - "Try MIMIC today"
   - GitHub link

**Tools Needed:**
- Screen recording (OBS Studio)
- Video editing (DaVinci Resolve or similar)
- Voiceover (optional)

**Estimated Time:** 4-6 hours

---

### 4. UI Polish (MEDIUM PRIORITY)

**Task:** Improve user experience and visual design

**Improvements:**
- [ ] Add drag-and-drop for file uploads
- [ ] Show clip thumbnails in upload area
- [ ] Display reference video preview
- [ ] Add "Example References" section
- [ ] Improve error messages
- [ ] Add tooltips for technical terms

**Files to Modify:**
- `frontend/components/UploadSection.tsx`
- `frontend/components/ResultsPanel.tsx`
- `frontend/app/globals.css`

**Estimated Time:** 3-4 hours

---

### 5. Final Testing (HIGH PRIORITY)

**Task:** Comprehensive testing before submission

**Test Cases:**
```bash
# Test all reference videos
$env:TEST_REFERENCE = "ref4.mp4"; python test_ref.py
$env:TEST_REFERENCE = "ref5.mp4"; python test_ref.py
$env:TEST_REFERENCE = "ref6.mp4"; python test_ref.py
$env:TEST_REFERENCE = "ref9.mp4"; python test_ref.py

# Test with different clip counts
# Test with edge cases (very short/long references)
# Test error handling (missing files, invalid formats)
```

**Validation Checklist:**
- [ ] All references produce valid output
- [ ] Diversity >90% on all tests
- [ ] Vibe matching >70% on all tests
- [ ] Timeline integrity maintained
- [ ] Cache working correctly
- [ ] API key rotation working
- [ ] Error messages are helpful

**Estimated Time:** 2-3 hours

---

## 🔧 Technical Debt (Optional)

### Low Priority Improvements

**1. Parallel Segment Extraction**
- Current: Sequential FFmpeg calls (8-10s)
- Potential: Parallel processing (2-3s)
- Trade-off: CPU usage, complexity

**2. Segment Cache**
- Cache extracted segments
- Reuse across edits
- Trade-off: Disk space

**3. GPU Acceleration**
- Use NVENC for encoding
- Potential 10x speedup
- Trade-off: Requires NVIDIA GPU

**Note:** These are not critical for hackathon submission

---

## 📝 Documentation Tasks

### 1. Update README with Demo Link
```markdown
## 🎬 Demo

Watch MIMIC in action: [YouTube Link]

Try it yourself: [Live Demo Link] (if deployed)
```

### 2. Create SUBMISSION.md
```markdown
# Hackathon Submission

## Project: MIMIC - AI-Powered Video Style Transfer

### Category: Action Era - Creative Autopilot

### Description:
[Compelling description highlighting Gemini API usage]

### Key Features:
- Semantic video analysis
- Vibe-aware matching
- Smart recommendations

### Technical Highlights:
- 28 Gemini API keys for quota management
- Tiered energy matching algorithm
- Persistent caching for performance

### Demo:
[Link to demo video]

### Try It:
[Link to GitHub]
```

---

## 🎯 Success Criteria

### Must Have (For Submission)
- ✅ Core pipeline working (DONE)
- ✅ Consistent quality (DONE)
- ✅ Documentation complete (DONE)
- [ ] Demo video recorded
- [ ] Frontend shows recommendations
- [ ] All tests passing

### Nice to Have
- [ ] Real-time progress updates
- [ ] Live deployment
- [ ] Batch processing
- [ ] Custom vibe definitions

---

## 🚀 Deployment Checklist

### If Deploying to Cloud

**Backend (Railway/Render):**
```bash
# Environment variables needed
GEMINI_API_KEY=...
# (all 28 keys)

# Requirements
python 3.10+
ffmpeg
librosa dependencies
```

**Frontend (Vercel):**
```bash
# Environment variables
NEXT_PUBLIC_API_URL=https://api.mimic.app
```

**Storage:**
- Consider cloud storage for cache (S3/GCS)
- Or disable cache for cloud deployment

---

## 📊 Time Estimate

### Total Time: 14-20 hours

**Breakdown:**
- Frontend Integration: 2-3h
- Progress Updates: 3-4h
- Demo Video: 4-6h
- UI Polish: 3-4h
- Final Testing: 2-3h

**Recommended Schedule:**
- Day 1 (4-5h): Frontend integration + Testing
- Day 2 (4-5h): Progress updates + UI polish
- Day 3 (4-6h): Demo video + Final polish
- Day 4 (2h): Submission preparation

---

## 🎬 Demo Video Script (Detailed)

### Scene 1: Hook (0:00 - 0:10)
**Visual:** MIMIC logo animation  
**Text:** "What if AI could learn your editing style?"  
**Voiceover:** "Introducing MIMIC - AI-powered video style transfer"

### Scene 2: Problem (0:10 - 0:25)
**Visual:** Frustrated person editing videos  
**Text:** "Video editing is time-consuming and requires expertise"  
**Voiceover:** "Creating professional edits takes hours of work and years of experience"

### Scene 3: Solution (0:25 - 0:45)
**Visual:** MIMIC interface  
**Text:** "Upload a reference video"  
**Action:** Drag ref4.mp4 into interface  
**Text:** "Upload your raw clips"  
**Action:** Drag 36 clips into interface  
**Voiceover:** "MIMIC learns from professional examples and applies that style to your content"

### Scene 4: Magic (0:45 - 1:15)
**Visual:** Analysis visualization  
**Text:** "AI analyzes the reference"  
**Show:** Scene detection, BPM detection, energy levels  
**Text:** "Understands your clips"  
**Show:** Clip analysis with vibes  
**Text:** "Matches them intelligently"  
**Show:** Matching algorithm with scores  
**Voiceover:** "Using Google's Gemini AI, MIMIC understands not just what's in the video, but the vibe and energy"

### Scene 5: Result (1:15 - 1:35)
**Visual:** Side-by-side comparison  
**Left:** Reference video  
**Right:** Generated edit  
**Text:** "Same rhythm, your content"  
**Show:** Diversity report (97% unique clips)  
**Show:** Vibe matching (80% accuracy)  
**Voiceover:** "The result? A professional edit that matches the reference's rhythm perfectly"

### Scene 6: Smart Features (1:35 - 1:50)
**Visual:** Recommendations panel  
**Text:** "Get smart recommendations"  
**Show:** "Add 5 more Medium-energy clips"  
**Show:** "2 segments wanted High energy but used Medium"  
**Voiceover:** "MIMIC even tells you what clips to add to improve your edit"

### Scene 7: Call to Action (1:50 - 2:00)
**Visual:** GitHub repo  
**Text:** "Open Source on GitHub"  
**Text:** "Built with Gemini API"  
**Text:** "Try MIMIC today"  
**Voiceover:** "Try MIMIC today and transform your video editing workflow"

---

## 🔍 Pre-Submission Checklist

### Code Quality
- [ ] All files have proper docstrings
- [ ] No commented-out debug code
- [ ] No hardcoded paths
- [ ] Environment variables documented
- [ ] Requirements.txt up to date

### Documentation
- [ ] README.md complete
- [ ] ARCHITECTURE.md complete
- [ ] STATUS.md up to date
- [ ] Code comments clear
- [ ] API documentation exists

### Testing
- [ ] All test references work
- [ ] Error handling tested
- [ ] Cache invalidation tested
- [ ] API key rotation tested
- [ ] Edge cases handled

### Demo
- [ ] Demo video recorded
- [ ] Demo video uploaded
- [ ] Screenshots taken
- [ ] Example outputs ready

### Submission
- [ ] Hackathon form filled
- [ ] Demo link added
- [ ] GitHub repo public
- [ ] README has demo section
- [ ] License file present

---

## 💡 Ideas for Future Sessions

### Feature Ideas
1. **Style Presets**
   - Pre-defined styles (TikTok, YouTube, Instagram)
   - One-click application

2. **Collaborative Editing**
   - Share references
   - Community clip library

3. **Advanced Customization**
   - Manual vibe definitions
   - Custom energy thresholds
   - Override individual matches

4. **Analytics Dashboard**
   - Edit history
   - Clip usage stats
   - Quality trends

5. **Mobile App**
   - iOS/Android support
   - On-device processing
   - Cloud sync

---

## 📞 Support & Resources

### If Issues Arise

**API Key Issues:**
- Check `.env` file format
- Verify keys are active
- Test with `test_api_keys.py`

**Cache Issues:**
- Clear cache: `Remove-Item data/cache/* -Recurse -Force`
- Check disk space
- Verify write permissions

**FFmpeg Issues:**
- Verify FFmpeg in PATH: `ffmpeg -version`
- Check video format compatibility
- Review FFmpeg logs

**Performance Issues:**
- Check cache hit rate in logs
- Verify SSD (not HDD) for cache
- Monitor CPU/memory usage

---

## 🎉 Celebration Checklist

### When Submission is Complete
- [ ] Take screenshots of final product
- [ ] Save all test outputs
- [ ] Backup code to multiple locations
- [ ] Document lessons learned
- [ ] Celebrate! 🎊

---

**Next Session Start:** Review this document first  
**First Task:** Frontend recommendation integration  
**Goal:** Hackathon-ready in 14-20 hours

**Good luck! 🚀**
