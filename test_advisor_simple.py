"""
Simple Advisor test - loads everything from cache, no re-analysis.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from models import StyleBlueprint, ClipIndex, ClipMetadata, BestMoment, EnergyLevel, MotionType
from engine.gemini_advisor import get_advisor_suggestions

def load_reference_from_cache(ref_name="ref5.mp4"):
    cache_dir = Path("data/cache")
    
    import hashlib
    ref_path = f"data/samples/reference/{ref_name}"
    with open(ref_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:12]
    
    cache_file = cache_dir / f"ref_{file_hash}_hints0.json"
    
    if not cache_file.exists():
        print(f"[ERROR] No cache found for {ref_name}")
        return None
    
    data = json.loads(cache_file.read_text())
    blueprint_data = {k: v for k, v in data.items() if not k.startswith("_")}
    return StyleBlueprint(**blueprint_data)

def load_clips_from_cache():
    cache_dir = Path("data/cache")
    clip_files = list(cache_dir.glob("clip_comprehensive_*.json"))
    
    print(f"Loading {len(clip_files)} clips from cache...")
    
    clips = []
    for cache_file in clip_files:
        try:
            data = json.loads(cache_file.read_text())
            
            best_moments = {}
            if "best_moments" in data and data["best_moments"]:
                for energy, moment_data in data["best_moments"].items():
                    best_moments[energy] = BestMoment(**moment_data)
            
            clip = ClipMetadata(
                filename=data["filename"],
                filepath=data["filepath"],
                duration=data["duration"],
                energy=EnergyLevel(data["energy"]),
                motion=MotionType(data["motion"]),
                intensity=data.get("intensity", 2),
                primary_subject=data.get("primary_subject", []),
                narrative_utility=data.get("narrative_utility", []),
                emotional_tone=data.get("emotional_tone", []),
                clip_quality=data.get("clip_quality", 3),
                best_for=data.get("best_for", []),
                avoid_for=data.get("avoid_for", []),
                vibes=data.get("vibes", []),
                content_description=data.get("content_description"),
                best_moments=best_moments if best_moments else None
            )
            clips.append(clip)
        except Exception as e:
            print(f"[WARN] Failed to load {cache_file.name}: {e}")
    
    return ClipIndex(clips=clips)

def main():
    print("="*60)
    print("[TEST] ADVISOR SIMPLE TEST (Cache-Only)")
    print("="*60)
    
    print("\n[1] Loading reference from cache...")
    blueprint = load_reference_from_cache("ref5.mp4")
    
    if not blueprint:
        return
    
    print(f"[PASS] Reference loaded:")
    print(f"  Duration: {blueprint.total_duration:.1f}s")
    print(f"  Segments: {len(blueprint.segments)}")
    print(f"  Intent: {blueprint.narrative_message}")
    print(f"  Intent Clarity: {blueprint.intent_clarity}")
    
    print("\n[2] Loading clips from cache...")
    clip_index = load_clips_from_cache()
    
    print(f"[PASS] {len(clip_index.clips)} clips loaded")
    
    energy_dist = {}
    for clip in clip_index.clips:
        energy_dist[clip.energy.value] = energy_dist.get(clip.energy.value, 0) + 1
    print(f"  Energy: {energy_dist}")
    
    print("\n[3] Calling Advisor...")
    advisor_hints = get_advisor_suggestions(blueprint, clip_index)
    
    if not advisor_hints:
        print("[FAIL] Advisor returned None")
        return
    
    print(f"\n{'='*60}")
    print(f"[ADVISOR OUTPUT]")
    print(f"{'='*60}")
    print(f"\nOverall Strategy:")
    print(f"  {advisor_hints.overall_strategy}")
    
    print(f"\nLibrary Assessment:")
    print(f"  Confidence: {advisor_hints.library_assessment.confidence}")
    print(f"  Strengths: {advisor_hints.library_assessment.strengths}")
    print(f"  Gaps: {advisor_hints.library_assessment.gaps}")
    
    print(f"\nArc Stage Suggestions:")
    for stage, suggestion in advisor_hints.arc_stage_suggestions.items():
        print(f"\n  {stage}:")
        print(f"    Clips: {suggestion.recommended_clips}")
        print(f"    Why: {suggestion.reasoning}")
        if suggestion.content_alignment:
            print(f"    Aligns: {suggestion.content_alignment}")
    
    print(f"\n{'='*60}")
    print(f"[SUCCESS] Advisor test complete!")

if __name__ == "__main__":
    main()
