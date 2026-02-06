# 🔬 REFERENCE MODE DIAGNOSTIC TEST PLAN

**Date**: 2026-02-06  
**Version**: Reference Mode Lock (Post-Fix)  
**Purpose**: Validate 3 surgical fixes and collect X-RAY diagnostics

---

## ✅ FIXES APPLIED

1. **Audio Sync** (`orchestrator.py:508`)
   - Changed: `trim_to_shortest=False` → `trim_to_shortest=True`
   - Impact: No more silence padding, music plays to end

2. **Vibe Priority Inversion** (`editor.py:754, 816`)
   - Vibe bonus: +40 → **+60** (PRIMARY SELECTOR)
   - Subject bonus: +25/+10 → **+15/+5** (TIE-BREAKER)
   - Impact: Vibe matching now wins over subject matching

3. **Diversity Enforcement** (`editor.py:1018-1023`)
   - Penalties: 30, 80, 180 → **100, 300, 900** (EXPONENTIAL)
   - Impact: Clip repetition becomes prohibitively expensive

---

## 🎯 TEST CASES (Run in Order)

### Test 1: **ref4** (Baseline Validation)
**Purpose**: Confirm all 3 fixes worked  
**Expected Results**:
- ✅ Audio duration: 14.23s (matches reference exactly)
- ✅ Vibe accuracy: >60% (was 3.3%)
- ✅ No clip repetition (was 5 clips repeated 2x each)
- ✅ Unique clips used: >30/56 (was 23/56)

**What to Check**:
- Compare final video duration to reference audio duration
- Check "Vibe Accuracy" line in log
- Check "CLIPS REPEATED" section (should say "NO CLIPS REPEATED")
- Review XRAY file for vibe override warnings

---

### Test 2: **ref5** (Text Overlay Intelligence)
**Purpose**: Validate semantic interpretation of "stories we'll tell later"  
**Expected Results**:
- ✅ More ACTION clips (Activity-Leisure, Activity-Travel)
- ✅ Fewer SCENIC clips (Place-Nature alone)
- ✅ Vibe accuracy: >50% (was 29.2%)

**What to Check**:
- Subject distribution in log (count People-Group vs Place-Nature)
- XRAY file: Check if "Adventurous" or "Travel" vibes are matched
- Final video: Does it feel like "action/anticipation" or "scenic/calm"?

---

### Test 3: **ref22** (Control - No Regression)
**Purpose**: Ensure fixes didn't break what was already working  
**Expected Results**:
- ✅ Vibe accuracy: ≥35.3% (baseline)
- ✅ No new issues introduced

**What to Check**:
- Compare to previous ref22 log (if available)
- Ensure quality didn't degrade

---

### Test 4: **ref20** (Beat Sync Issues)
**Purpose**: Isolate rhythm/timing problems  
**Expected Results**:
- ✅ Better beat alignment (check beat_alignment_logs)
- ✅ No perceptual lag on cuts

**What to Check**:
- XRAY file: Beat alignment section
- Log: "Beat aligned: YES/NO" for each cut
- Final video: Do cuts feel on-beat or laggy?

---

### Test 5: **NEW - Slow Cinematic Reference**
**Purpose**: Test Long hold + visual cuts (V14.1 edge case)  
**Pick**: A reference with slow, contemplative pacing (2-4s holds)  
**Expected Results**:
- ✅ Sacred cuts preserved (no subdivision)
- ✅ CDE logic respects "Long" holds

**What to Check**:
- Log: "CDE: Sparse" for long segments
- Log: "max_cuts: 1" for sacred visual cuts
- XRAY file: No subdivision warnings

---

## 📊 X-RAY DIAGNOSTIC FILES

Each test will generate: `data/results/{ref_name}_XRAY.txt`

### What's in the XRAY File?

**Per Segment**:
1. **Advisor Input**
   - Primary narrative subject
   - Text overlay intent
   - Dominant narrative

2. **Top 5 Candidates**
   - Clip name, score, vibes, subjects, energy
   - Vibe match: YES/NO
   - Score delta from winner
   - Reasoning breakdown

3. **Selection Decision**
   - Winner clip
   - Final score
   - Vibe match: YES/NO
   - **Subject Override**: ⚠️ YES if subject won over vibe
   - **Vibe Override**: ⚠️ YES if vibe was ignored

4. **Diversity Analysis**
   - Reuse count and penalty
   - Why clip still won despite penalty

---

## 🔍 KEY METRICS TO TRACK

Create a spreadsheet with these columns:

| Test | Audio Match | Vibe Accuracy | Clips Repeated | Subject Overrides | Vibe Overrides |
|------|-------------|---------------|----------------|-------------------|----------------|
| ref4 | ✅ 14.23s   | 65.2%         | 0              | 2                 | 0              |
| ref5 | ✅ 16.65s   | 58.3%         | 0              | 5                 | 1              |
| ...  | ...         | ...           | ...            | ...               | ...            |

**How to Extract**:
- **Audio Match**: Compare final video duration to reference audio
- **Vibe Accuracy**: Search log for "Vibe Accuracy: X%"
- **Clips Repeated**: Count in "CLIPS REPEATED" section
- **Subject Overrides**: Count "⚠️ YES" in XRAY "Subject Override" lines
- **Vibe Overrides**: Count "⚠️ YES" in XRAY "Vibe Override" lines

---

## 🚨 RED FLAGS TO WATCH FOR

1. **Audio Mismatch**: Final video duration ≠ reference audio duration
   - **Diagnosis**: Fix #1 failed, check orchestrator.py:508

2. **Low Vibe Accuracy (<40%)**:
   - **Diagnosis**: Fix #2 failed, check editor.py scoring weights
   - **Check XRAY**: Count "Subject Override: ⚠️ YES" instances

3. **Clip Repetition**:
   - **Diagnosis**: Fix #3 failed, check editor.py diversity penalties
   - **Check XRAY**: Look for "DIVERSITY WARNING" with low penalties

4. **Subject Override Warnings (>30% of segments)**:
   - **Diagnosis**: Subject bonus still too high
   - **Tweak**: Reduce subject bonus further (15 → 10, 5 → 2)

5. **Vibe Override Warnings (>10% of segments)**:
   - **Diagnosis**: Vibe bonus not high enough
   - **Tweak**: Increase vibe bonus further (60 → 80)

---

## 📝 POST-TEST ANALYSIS

After running all 5 tests:

1. **Aggregate Metrics**:
   - Average vibe accuracy across all tests
   - Total clip repetitions across all tests
   - Total subject/vibe overrides

2. **Identify Patterns**:
   - Which segments consistently have overrides?
   - Which vibes are hardest to match?
   - Which subjects dominate unfairly?

3. **Propose Tweaks**:
   - If vibe accuracy still <60%: Increase vibe bonus to +80
   - If repetition still occurs: Increase penalties to 150, 500, 1500
   - If subject overrides >20%: Reduce subject bonus to +10/+2

---

## 🗑️ CLEANUP AFTER TESTING

Once fixes are validated and tweaks are made:

1. **Delete XRAY files**: `data/results/*_XRAY.txt`
2. **Remove XRAY logging code**: Lines 1191-1254 in editor.py
3. **Keep the 3 fixes**: They are permanent

---

## ✅ SUCCESS CRITERIA

Reference Mode is **LOCKED** when:

- ✅ Audio sync: 100% match across all tests
- ✅ Vibe accuracy: >60% average across all tests
- ✅ Clip repetition: 0 across all tests
- ✅ Subject overrides: <10% of segments
- ✅ Vibe overrides: <5% of segments

**If all criteria met**: Reference Mode is production-ready. Delete XRAY logs and move to creative mode development.
