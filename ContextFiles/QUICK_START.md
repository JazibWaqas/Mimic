# MIMIC - Quick Start Guide for New Sessions

**Version:** V7.0  
**Status:** ✅ Production Ready  
**Last Updated:** January 23, 2026

---

## 🎯 What is MIMIC?

MIMIC is an AI-powered video editing system that learns from professional reference videos and automatically recreates that editing style using your raw clips.

**Think:** "Instagram Reels editor that understands the 'why' behind professional edits"

---

## ⚡ Quick Start (5 minutes)

### 1. Test the System
```bash
# Activate environment
.venv\Scripts\activate

# Run test
$env:TEST_REFERENCE = "ref4.mp4"
python test_ref.py

# Check output
# Video: data/results/mimic_output_ref4_vibes_test.mp4
# Log: data/results/ref4_xray_output.txt
```

### 2. Understand the Output

**X-Ray Log Contains:**
- Blueprint (what the reference needs)
- Clip Registry (what you have)
- Diversity Report (how well clips were used)
- Recommendations (what to add)

**Example Recommendation:**
```
💡 RECOMMENDATIONS TO IMPROVE THIS EDIT:
   [Inventory Gaps]
   → Add 5 more MEDIUM-ENERGY clips (walking, social, casual movement, city life)
```

---

## 📁 Key Files to Know

### Core Engine
```
backend/engine/
├── orchestrator.py    # Pipeline controller (START HERE)
├── brain.py           # Gemini AI integration
├── editor.py          # Matching algorithm (tiered energy, scoring)
└── processors.py      # FFmpeg wrappers
```

### Configuration
```
backend/.env           # API keys (28 Gemini keys)
data/cache/            # Analysis + standardized clips
test_ref.py            # X-Ray test runner
```

### Documentation
```
README.md                      # Overview + quick start
ContextFiles/ARCHITECTURE.md   # System design + algorithms
ContextFiles/STATUS.md         # Current state + metrics
ContextFiles/NEXT_SESSION.md   # Action plan
```

---

## 🧠 How It Works (30 seconds)

1. **Analyze Reference** → Gemini identifies energy, vibes, arc stages
2. **Analyze Clips** → Gemini extracts energy, vibes, best moments
3. **Match Intelligently** → Tiered energy + vibe matching + diversity optimization
4. **Render** → FFmpeg extracts segments, concatenates, merges audio

**Key Innovation:** Tiered energy matching prevents jarring transitions while maximizing clip diversity.

---

## 🎨 Core Concepts

### Energy Levels
- **High:** Dancing, sports, action, fast movement
- **Medium:** Walking, social, casual movement, city life
- **Low:** Scenic, calm, establishing shots, landscapes

### Tiered Matching
- High segment → Can use High OR Medium clips
- Low segment → Can use Low OR Medium clips
- Medium segment → Can use ANY clips

**Why?** Prevents Low→High jumps while allowing graceful degradation.

### Scoring System
```
Discovery Bonus:     +40 (prioritize unused clips)
Energy Match:        +20 (exact) or +5 (adjacent)
Vibe Match:          +15 (semantic alignment)
Arc Stage:           +10 (intro/peak relevance)
Usage Penalty:       -25 per reuse
Cooldown:            -40 if used <5s ago
```

**Result:** 90%+ unique clip usage, 70-80% vibe accuracy

---

## 🚀 Performance

### Speed
- **First Run:** 450-650s (analyzing + standardizing)
- **Cached Run:** 15-20s (everything cached)
- **Bottleneck:** Segment extraction (8-10s for 30 segments)

### Caching
```
data/cache/standardized/std_{hash}.mp4  # Persistent, hash-based
data/cache/clip_comprehensive_{hash}.json  # Analysis cache
data/cache/ref_{hash}_h{hints}.json  # Reference cache
```

**Cache Hit Rate:** 100% on repeat runs

---

## 🔧 Common Tasks

### Test Different Reference
```bash
$env:TEST_REFERENCE = "ref5.mp4"
python test_ref.py
```

### Clear Cache
```bash
# Clear all cache
Remove-Item data/cache/* -Recurse -Force

# Clear only standardized clips
Remove-Item data/cache/standardized/*.mp4 -Force
```

### Add More Clips
```
1. Add .mp4 files to data/samples/clips/
2. Run test_ref.py
3. System auto-analyzes new clips
```

### Check API Keys
```bash
python test_api_keys.py
```

---

## 📊 Current Metrics

### Quality (Tested on ref4, ref5, ref6, ref9)
- **Diversity:** 90-100% unique clips
- **Vibe Matching:** 70-80% accuracy
- **Timeline Precision:** <0.001s gaps
- **Energy Coherence:** 94-98%

### Performance
- **Total Time:** 15-20s (cached)
- **Cache Hit Rate:** 100%
- **Memory Usage:** ~500MB peak

---

## 🐛 Troubleshooting

### "All API keys exhausted"
→ Wait for quota reset or add more keys to `.env`

### "Standardizing every time"
→ Check `data/cache/standardized/` exists and has write permissions

### "Low diversity"
→ Add more clips or check X-Ray recommendations

### "Cuts don't align with beats"
→ Check detected BPM in logs, verify librosa installed

---

## 📚 Deep Dive Documents

**Want to understand the algorithms?**
→ Read `ContextFiles/ARCHITECTURE.md`

**Want to see the full history?**
→ Read `ContextFiles/STATUS.md`

**Want to know what's next?**
→ Read `ContextFiles/NEXT_SESSION.md`

**Want to understand a specific module?**
→ Check docstrings in the code

---

## 🎯 Next Steps (From NEXT_SESSION.md)

### Immediate Priorities
1. **Frontend Integration** - Display recommendations in UI
2. **Demo Video** - Record compelling demo for hackathon
3. **Final Testing** - Validate all references work perfectly

### Time Estimate
14-20 hours to hackathon-ready

---

## 💡 Pro Tips

1. **Always check X-Ray logs** - They tell you everything about the edit
2. **Cache is your friend** - Never clear unless debugging
3. **Diversity > Perfection** - System prioritizes variety over semantic perfection
4. **Trust the recommendations** - They're based on actual deficits
5. **Test with ref4 first** - It's the most reliable reference

---

## 🔍 Quick Reference

### File Paths
```
Reference Videos:  data/samples/reference/ref*.mp4
User Clips:        data/samples/clips/*.mp4
Output Videos:     data/results/mimic_output_*.mp4
X-Ray Logs:        data/results/*_xray_output.txt
Cache:             data/cache/
```

### Key Commands
```bash
# Test
python test_ref.py

# Clear cache
Remove-Item data/cache/* -Recurse -Force

# Check keys
python test_api_keys.py

# Run backend
cd backend && uvicorn main:app --reload

# Run frontend
cd frontend && npm run dev
```

---

## 🎉 You're Ready!

**System Status:** ✅ Production Ready  
**Documentation:** ✅ Complete  
**Testing:** ✅ Validated  
**Performance:** ✅ Optimized

**Next:** Pick a task from NEXT_SESSION.md and start building!

---

**Questions?** Check the documentation or review the code docstrings.  
**Issues?** See Troubleshooting section above.  
**Ready to ship?** Follow the pre-submission checklist in NEXT_SESSION.md.

**Good luck! 🚀**
