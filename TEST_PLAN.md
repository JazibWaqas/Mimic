# 🎯 V14.1 CANONICAL VIBE LAYER - TEST PLAN

## ✅ Code Safety Check: PASSED
- `editor.py` compiles successfully
- `gemini_advisor_prompt.py` compiles successfully
- `canonicalize()` function is properly defined and called
- XRAY output path fixed to root `data/results/`

---

## 🎬 RECOMMENDED TEST SEQUENCE

### **Priority 1: High-Impact Demo Tests** (Run these first)

#### **Test 1: ref19 (F1 Racing)**
**Why**: This was showing 9.1% vibe accuracy. Should jump to 70-90%.
**Expected Improvement**:
- Before: System ignored "Racing" clips because they weren't tagged as "Action"
- After: Canonical map recognizes Racing → ACTION
- Visual: Should see more F1 car footage, less random filler

**Run Command**: Upload `ref19.mp4` in UI

**What to Check**:
1. XRAY log at `data/results/ref19_XRAY.txt`
2. Look for "Vibe Match: ✅ YES" entries (should be 70%+)
3. Final video should feel like an F1 edit, not a random montage

---

#### **Test 2: ref5 (Friends Trip)**
**Why**: This had 33% vibe accuracy. Should jump to 80%+.
**Expected Improvement**:
- Before: "Laughter" and "Joyful" clips weren't recognized as "Joy"
- After: Canonical map recognizes Laughter/Happy/Friends → JOY
- Visual: Should prioritize friend group shots over scenery

**Run Command**: Upload `ref5.mp4` in UI

**What to Check**:
1. XRAY log at `data/results/ref5_XRAY.txt`
2. Vibe Match rate should be 80%+
3. Video should feel like a "friends celebration" not a "travel vlog"

---

### **Priority 2: Edge Case Tests** (Run if P1 succeeds)

#### **Test 3: ref4 (Long Duration Test)**
**Why**: 7.3MB file, likely has complex arc stages
**Expected**: Tests if Advisor + Editor stay synced across longer edits

---

#### **Test 4: ref10 or ref11 (Short Duration)**
**Why**: ~2.6-2.9MB, quick turnaround for iteration testing
**Expected**: Fast feedback loop for debugging

---

## 🔍 DEBUGGING CHECKLIST

### **If Pipeline Fails to Start:**
1. Check terminal for Python errors
2. Verify `data/cache/advisor/` was cleared
3. Check if Gemini API key is valid

### **If Vibe Accuracy is Still Low:**
1. Open XRAY log: `data/results/refXX_XRAY.txt`
2. Look for section: "=== SEGMENT X SCORING ==="
3. Check if "Canonical Match" appears in reasoning
4. If not, check if clip has `emotional_tone` field populated

### **If Video Looks Wrong:**
1. Check XRAY "Winner" vs "Runner-Up" comparison
2. If Runner-Up had higher vibe score but lost, there's a tie-breaker bug
3. If Winner has "Vibe Match: ❌ NO", the canonical map is missing a synonym

---

## 📊 SUCCESS METRICS

### **Minimum Viable Demo (MVD):**
- ✅ ref19 Vibe Accuracy: **≥70%** (up from 9%)
- ✅ ref5 Vibe Accuracy: **≥80%** (up from 33%)
- ✅ Visual coherence: Clips match the reference's "soul"

### **Stretch Goal:**
- ✅ ref19 Vibe Accuracy: **≥90%**
- ✅ No "Subject Override" warnings in XRAY logs
- ✅ Tie-breaker always favors vibe matches

---

## 🚨 KNOWN RISKS & MITIGATIONS

### **Risk 1: Advisor Cache Corruption**
**Symptom**: Advisor still uses old vocabulary (e.g., doesn't mention "ACTION")
**Fix**: Delete `data/cache/advisor/` and re-run

### **Risk 2: Clip Analysis Missing `emotional_tone`**
**Symptom**: Vibe accuracy still low despite canonical map
**Fix**: Check a clip's JSON in `data/cache/clips/`. If `emotional_tone` is empty, re-analyze clips.

### **Risk 3: Gemini Rate Limiting**
**Symptom**: Pipeline fails with "429 Too Many Requests"
**Fix**: Wait 60 seconds, then retry

---

## 🎯 FINAL RECOMMENDATION

**Run in this exact order:**
1. **ref19** (F1) - Proves ACTION category works
2. **ref5** (Friends) - Proves JOY category works
3. If both succeed → **Demo-ready**
4. If either fails → Check XRAY logs and report findings

**Estimated Time**: 
- ref19: ~3-5 minutes
- ref5: ~3-5 minutes
- Total: ~10 minutes for full validation

---

## 📝 NOTES FOR DEBUGGING SESSION

If you encounter issues, capture:
1. Terminal output (last 50 lines)
2. XRAY log file (full content)
3. Advisor cache file name (to check if it regenerated)
4. One sample clip's JSON (to verify `emotional_tone` exists)

**Good luck! The system is ready. 🚀**
