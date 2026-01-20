# Next Session - Critical Architecture Fixes Required

**Created:** January 20, 2026, 11:00 AM
**Purpose:** Address fundamental architectural blockers before any testing
**Priority:** FIX MATH ISSUES → THEN TEST API

---

## 🚨 CRITICAL BLOCKERS (MUST FIX FIRST)

**The system cannot produce working videos until these 3 architectural issues are resolved:**

1. **Timeline Primitive Mismatch** - Gemini moments ≠ Reference segments (causes gaps)
2. **Float Precision Errors** - Accumulating micro-gaps break FFmpeg
3. **Cache Poisoning** - Defaults permanently corrupt matching data

**These are deeper than API issues - they're mathematical impossibilities that no amount of key rotation can fix.**

---

## 🔧 Step 1: Fix Timeline Primitive Mismatch

**Problem:** System matches variable-duration "best moments" to fixed-duration segments, creating gaps.

**Required Change:** Modify Gemini prompts to return start points, not full moments. Code must force exact duration extraction.

**Files to examine:**
- `backend/engine/brain.py` - Clip analysis prompt (lines ~800-900)
- `backend/engine/editor.py` - Matching logic (lines ~100-200)
- `backend/engine/processors.py` - FFmpeg extraction commands

**Success Criteria:**
- Segments fill completely (no gaps)
- Clip moments get trimmed to exact reference durations
- Timeline validation passes

---

## 🔧 Step 2: Fix Float Precision Boundary Enforcement

**Problem:** Python floats accumulate precision errors, creating invisible gaps.

**Required Change:** Add boundary enforcement in `EditDecision` creation.

**Code Location:** `backend/engine/editor.py` - EditDecision creation loop

**Implementation:**
```python
# Force continuity regardless of float precision
if i > 0:
    decision.timeline_start = previous_decision.timeline_end
```

**Success Criteria:**
- No micro-gaps in timeline
- Consistent rendering across runs
- Pydantic validation passes

---

## 🔧 Step 3: Implement Cache Sanitation Policy

**Problem:** System caches defaults as truth, permanently poisoning data.

**Required Change:** Add "stale data" detection and rejection.

**Implementation:**
- Check for `vibes: null` or `"Medium"` defaults
- Flag as "STALE" and never cache
- Fail loudly instead of silently defaulting

**Files:** `backend/engine/brain.py` - Cache saving logic (lines ~880-920)

**Success Criteria:**
- Cache contains only real Gemini responses
- No "Medium/Dynamic" defaults in JSON files
- Fresh analysis on corrupted cache entries

---

## 🧪 Step 4: Validate Fixes (AFTER Implementation)

**Only then proceed to API testing:**

```powershell
# Clear ALL cache (fresh start)
Remove-Item data/cache/*.json -Force

# Run minimal test (1-2 clips first)
python test_minimal.py  # Create this - tests just ref4 + 2 clips

# Check for timeline validation errors
# Verify no gaps in EditDecision objects
# Confirm cache has real data
```

**Expected Outcome:**
- Timeline validation passes
- FFmpeg renders successfully
- Cache contains genuine analysis data

---

## 🎯 Step 5: API Testing (AFTER Architecture Fixes)

**Only if Steps 1-3 work:**

### **Check API Quota Status:**
```powershell
cd c:\Users\OMNIBOOK\Documents\GitHub\Mimic
python test_api_keys.py
```

### **Clear Cache & Test:**
```powershell
# Fresh analysis with fixed architecture
Remove-Item data/cache/clip_comprehensive*.json -Force
python test_ref4_v4.py
```

### **Success Indicators (Architecture + API):**
- ✅ No timeline validation errors
- ✅ No "Using default" messages
- ✅ Vibes appear in logs and cache
- ✅ FFmpeg concat succeeds
- ✅ Output video renders

---

## 📋 Implementation Checklist

**Before Coding Session:**
- [ ] Read `DIAGNOSTIC_LOG.md` Bugs #8-10
- [ ] Understand primitive mismatch concept
- [ ] Review float precision issues
- [ ] Plan cache sanitation logic

**During Coding:**
- [ ] Modify Gemini prompts for start points
- [ ] Add boundary enforcement in editor.py
- [ ] Implement cache staleness checks
- [ ] Test with minimal clips first

**After Implementation:**
- [ ] Run validation tests
- [ ] Confirm timeline continuity
- [ ] Verify cache integrity
- [ ] Only then test full pipeline

---

## 🚨 Why This Order Matters

**Architecture fixes FIRST, API testing SECOND.**

- **If timeline math is broken:** No video output possible, even with working API
- **If cache is poisoned:** API calls wasted on corrupted data
- **If primitives don't match:** System fundamentally cannot work

**Fix the math, then worry about API limits.**

---

## 📚 Context for Next Developer

**Must Read:**
- `DIAGNOSTIC_LOG.md` - New architectural bugs #8-10
- `STATUS.md` - Current system overview
- Focus on `backend/engine/editor.py` and `backend/engine/brain.py`

**Key Concept:** The system was built assuming Gemini moments would perfectly fit reference segments. They don't. The architecture must force the fit.

**Goal:** Make the timeline math work reliably before optimizing AI usage.

---

**Next Session Focus:** Fix architectural math issues. API testing comes after proven timeline continuity.
