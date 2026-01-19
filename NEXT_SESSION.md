# Next Session - Immediate Action Plan

**Created:** January 19, 2026, 23:32 PKT  
**Purpose:** Clear, actionable steps for the next coding session

---

## ⏰ Before You Start

### **Check API Quota Status:**
```powershell
cd c:\Users\OMNIBOOK\Documents\GitHub\Mimic
python test_api_keys.py
```

**Expected Output:**
```
✅ Fresh keys:     X/11
❌ Exhausted keys: Y/11
```

**If all keys still exhausted:** Wait longer, quotas reset at unknown time.  
**If some keys fresh:** Proceed with testing.

---

## 🧹 Step 1: Clear Bad Cache (REQUIRED)

**Why:** 9 clips were cached before the vibes bug was fixed. They have `vibes: null`.

```powershell
# Delete all clip caches
Remove-Item data/cache/clip_comprehensive*.json -Force

# Verify deletion
ls data/cache/clip_comprehensive*.json
# Should show: "Cannot find path" (good!)
```

**DO NOT skip this step.** Bad cache will break semantic matching.

---

## 🧪 Step 2: Run Full Test

```powershell
python test_ref4_v4.py
```

### **What to Watch For:**

#### ✅ **Success Indicators:**
- `[OK] High/Dynamic with best moments:`
- `Vibes: Urban, Action, Nightlife` ← **MUST SEE THIS**
- `[API KEY MANAGER] Rotated to key X/11` ← Key rotation working
- `🧠 AI Thinking: Semantic Match: Vibe 'X' matches...` ← Semantic matching working
- `🎵 Beat grid generated: X beats at Y BPM` ← Dynamic BPM working
- `✅ SUCCESS!` at the end

#### ❌ **Failure Indicators:**
- `Using default: Medium/Dynamic` ← Should NEVER appear
- `403 Permission Denied` ← Upload/analysis key mismatch (should be fixed)
- `All keys exhausted` before 20/20 clips ← Quota issue
- No "Vibes:" in logs ← Bug #7 not actually fixed

### **Expected Timeline:**
- **Total Time:** 5-10 minutes
- **Per Clip:** 20-40 seconds (upload + analysis)
- **Key Rotations:** 1-2 (depending on quota timing)

---

## 📊 Step 3: Verify Results

### **Check Cache:**
```powershell
# Verify vibes are saved
Get-ChildItem data/cache/clip_comprehensive*.json | ForEach-Object { 
    $c = Get-Content $_.FullName | ConvertFrom-Json
    [PSCustomObject]@{ 
        File = $_.Name
        HasVibes = ($c.vibes -ne $null)
        Vibes = ($c.vibes -join ", ")
        Energy = $c.energy
    } 
} | Format-Table -AutoSize
```

**Expected Output:**
```
File                                 HasVibes Vibes                  Energy
----                                 -------- -----                  ------
clip_comprehensive_abc123.json       True     Urban, Action, Sports  High
clip_comprehensive_def456.json       True     Nature, Calm           Medium
...
```

**All clips MUST have `HasVibes = True`.**

### **Check Output Video:**
```powershell
# Find the output
ls data/results/mimic_output_ref4_v4*.mp4

# Play it
start data/results/mimic_output_ref4_v4_vibes_test.mp4
```

**Manual Verification:**
- [ ] Cuts align with music beats
- [ ] Pacing matches reference video
- [ ] No jarring transitions
- [ ] Clips seem thematically appropriate

---

## 🐛 Step 4: If Test Fails

### **Scenario A: "All keys exhausted" before completion**

**Diagnosis:** Quotas haven't reset yet or we're using more requests than expected.

**Action:**
1. Check how many clips were analyzed: Look for `[X/20] Processing...` in logs
2. If X < 20, wait longer for quota reset
3. If X = 20 but matching failed, check logs for other errors

### **Scenario B: No vibes in logs**

**Diagnosis:** Bug #7 fix didn't work, or Gemini isn't returning vibes.

**Action:**
1. Check one cache file manually: `Get-Content data/cache/clip_comprehensive_*.json | Select -First 1`
2. If `vibes: null`, the fix didn't work - review `brain.py` lines 939-995
3. If `vibes: []` (empty array), Gemini isn't returning data - check prompt

### **Scenario C: 403 errors after rotation**

**Diagnosis:** Bug #3 fix didn't work, upload still outside retry loop.

**Action:**
1. Check `brain.py` line 943 and 1065
2. Verify upload is INSIDE the `for attempt in range(...)` loop
3. Not before it

### **Scenario D: Defaults appear**

**Diagnosis:** Bug #6 fix didn't work, fallback still active.

**Action:**
1. Check `brain.py` lines 863-867
2. Should be `raise Exception(...)`, not `clip_metadata = ClipMetadata(...)`
3. If correct, the error is happening at orchestrator level (acceptable)

---

## ✅ Step 5: Success Checklist

Once test completes successfully:

- [ ] All 20 clips analyzed
- [ ] All clips have vibes in cache
- [ ] Output video exists
- [ ] Video plays correctly
- [ ] Cuts align with beats
- [ ] No errors in logs (except expected quota warnings)

**If all checked:** You're ready to move to next features (Material Suggestions, UI updates).

---

## 🚀 Step 6: Next Features (After Successful Test)

### **Priority 1: Material Suggestions**
Implement the gap analysis that warns users about missing clip types.

**Files to modify:**
- `backend/engine/orchestrator.py` - Add gap analysis after Step 3
- `backend/models.py` - Add MaterialSuggestions model
- Frontend - Display suggestions in UI

### **Priority 2: Reasoning Display**
Show the AI's "thinking" in the frontend.

**Files to modify:**
- Frontend progress component - Add reasoning display
- Backend - Ensure reasoning is included in API response

### **Priority 3: Multiple Reference Tests**
Test with different reference videos to verify system robustness.

**Test videos to try:**
- Slow-paced vlog (low energy, few cuts)
- Fast-paced action (high energy, many cuts)
- Music video (beat-driven, varied energy)

---

## 📝 Notes for Next Developer

### **Context You Need:**
- Read `STATUS.md` first - complete project overview
- Read `DIAGNOSTIC_LOG.md` - understand what bugs were fixed
- All code is in `backend/` and `frontend/`
- Test scripts are in root directory

### **Common Pitfalls:**
1. **Don't skip cache clearing** - Old cache will break everything
2. **Check API keys first** - No point testing if quotas exhausted
3. **Watch for vibes in logs** - If missing, something's wrong
4. **Verify cache after test** - Make sure data is actually saved

### **Quick Commands:**
```powershell
# Test API keys
python test_api_keys.py

# Clear cache
Remove-Item data/cache/clip_comprehensive*.json -Force

# Run test
python test_ref4_v4.py

# Check results
ls data/results/*.mp4
```

---

**Good luck! The system is ready - just waiting for API quotas to reset.**
