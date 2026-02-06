# MIMIC Demo Prompt — Nostalgic Childhood Reel

## Primary Prompt (Copy this into Creator Mode)

```
A warm, joyful, nostalgic childhood reel that celebrates innocence, happiness, and the beauty of growing up.

This edit should feel like a memory you didn't know you missed.

Start slow and gentle — calm, warm, and peaceful. Let the viewer settle into the world of childhood.
Gradually build through candid laughter, playful energy, and moments of pure joy.
As the music builds, allow the pacing to gently increase — symbolizing how time starts to slip faster as we grow older.
The peak should feel full of life, movement, and celebration, not chaotic or rushed.
End softly and reflectively — a bittersweet, loving goodbye to a phase of life that has passed.

This is not about using every clip quickly.
It's about letting moments breathe, reminiscing, and enjoying how sweet and innocent this time was.
Use as many clips as feel natural, but never rush the emotion.

The viewer should finish this edit feeling:
– warm
– happy
– nostalgic
– slightly bittersweet
– smiling, even if they don't know the kids in the video

Text overlay (subtle, elegant):
"Oh, to be this young again."

Overall feeling:
Joyful. Warm. Full of life. Innocent. Thought-provoking.
A beautiful reminder of how fast time moves — and how precious these moments were.
```

---

## Why This Prompt Works

| Element | Purpose | System Response |
|---------|---------|-----------------|
| **"warm, joyful nostalgia"** | Sets emotional_intent | Generator picks vibes: warmth, joy, innocence |
| **"Start slow and gentle"** | Primes Intro | CDE=Sparse, Long hold, Low energy |
| **"Build gradually"** | Primes Build-up | CDE=Moderate, energy escalation |
| **"Peak with celebration"** | Primes Peak | Medium-High energy, movement clips |
| **"End with peaceful, reflective"** | Primes Outro | CDE=Sparse, Long hold, Low energy |
| **"Text overlay: Oh, to be this young again."** | Direct text instruction | Captured in blueprint.text_overlay |
| **"Not fast. Not frantic."** | Pacing guidance | Expected_hold = Long/Normal, avoids Dense CDE |

---

## Expected Blueprint Output

The system should generate approximately:

| Segment | Duration | Arc Stage | CDE | Energy | Vibe |
|---------|----------|-----------|-----|--------|------|
| 1 | ~8s | Intro | Sparse | Low | calm, warmth, innocence |
| 2 | ~8s | Build-up | Moderate | Medium | laughter, joy, playful |
| 3 | ~8s | Peak | Moderate | High/Med | celebration, movement |
| 4 | ~6s | Outro | Sparse | Low | reflective, bittersweet |

Total: ~30s with 4 segments (compliant with ≤6 segment hard limit)

---

## Recommended Music

For best results, use music that:
- Has a clear emotional arc (quiet → building → climax → resolution)
- BPM around 80-110 (slower = more nostalgic feel)
- Features piano, strings, or acoustic guitar
- Has a "coming of age" or "memory" vibe

**Suggested**: 
- "Time" by Hans Zimmer (if you can get license)
- Any "childhood memories" type instrumental

---

## Demo Talking Points

When presenting this edit, say:

> "MIMIC is more than just an AI editing tool — it's a way for everyone to be the main character of their own story. This edit was made in under 30 seconds from raw clips, but it tells a story worth telling. The AI understood that nostalgia isn't about speed — it's about letting moments breathe, building emotion naturally, and creating something that genuinely moves you."

---

## Clip Curation Tips

For best results, include:
- **2-3 calm/static clips**: Sunsets, peaceful moments, establishing shots
- **4-5 laugh/smile clips**: Candid joy, playful energy
- **3-4 action/movement clips**: Running, playing, celebration
- **2-3 intimate moments**: Close-ups, hugs, tender moments
- **Mix of shot scales**: Wide (landscapes), Medium (groups), Close (faces)

Avoid:
- Dark/night clips (conflicts with warm vibe)
- Adult/formal content (conflicts with childhood innocence)
- Fast-action sports (conflicts with reflective pacing)
