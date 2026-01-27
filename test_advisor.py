"""
Test script for Gemini Advisor system.

Tests the advisor on ref5.mp4 with the full clip library.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.brain import analyze_reference_video, analyze_all_clips
from engine.gemini_advisor import get_advisor_suggestions
from models import ClipIndex

def test_advisor():
    print("[TEST] Testing Gemini Advisor on ref5.mp4")
    print("="*60)
    
    ref_path = "data/samples/reference/ref5.mp4"
    clips_dir = "data/samples/clips"
    
    print("\n[1] Loading reference from cache...")
    blueprint = analyze_reference_video(ref_path)
    
    if not blueprint:
        print("[FAIL] Could not analyze reference video")
        return
    
    print(f"[PASS] Reference loaded:")
    print(f"  - Duration: {blueprint.total_duration:.1f}s")
    print(f"  - Segments: {len(blueprint.segments)}")
    print(f"  - Intent: {blueprint.narrative_message}")
    print(f"  - Intent Clarity: {blueprint.intent_clarity}")
    print(f"  - Must-Have Content: {blueprint.must_have_content}")
    print(f"  - Should-Have Content: {blueprint.should_have_content}")
    
    print("\n[2] Loading clip library from cache...")
    clip_paths = [str(p) for p in Path(clips_dir).glob("*.mp4")]
    print(f"  - Found {len(clip_paths)} clips")
    
    clip_index = analyze_all_clips(clip_paths, use_comprehensive=True)
    
    if not clip_index or not clip_index.clips:
        print("[FAIL] Could not analyze clips")
        return
    
    print(f"[PASS] Clips analyzed: {len(clip_index.clips)}")
    
    energy_dist = {}
    for clip in clip_index.clips:
        energy_dist[clip.energy.value] = energy_dist.get(clip.energy.value, 0) + 1
    print(f"  - Energy distribution: {energy_dist}")
    
    print("\n[3] Getting Advisor suggestions...")
    advisor_hints = get_advisor_suggestions(blueprint, clip_index)
    
    if not advisor_hints:
        print("[FAIL] Advisor returned None")
        return
    
    print(f"[PASS] Advisor suggestions generated")
    print(f"\n[ADVISOR OUTPUT]")
    print(f"="*60)
    print(f"Overall Strategy: {advisor_hints.overall_strategy}")
    print(f"\nLibrary Assessment:")
    print(f"  Confidence: {advisor_hints.library_assessment.confidence}")
    print(f"  Strengths: {advisor_hints.library_assessment.strengths}")
    print(f"  Gaps: {advisor_hints.library_assessment.gaps}")
    
    print(f"\nArc Stage Suggestions:")
    for stage, suggestion in advisor_hints.arc_stage_suggestions.items():
        print(f"\n  {stage}:")
        print(f"    Recommended Clips: {suggestion.recommended_clips}")
        print(f"    Reasoning: {suggestion.reasoning}")
        print(f"    Content Alignment: {suggestion.content_alignment}")
    
    print(f"\n{'='*60}")
    print(f"[SUCCESS] Advisor test complete!")
    
    print(f"\n[4] Verifying clip recommendations exist...")
    all_recommended = set()
    for suggestion in advisor_hints.arc_stage_suggestions.values():
        all_recommended.update(suggestion.recommended_clips)
    
    available_filenames = {clip.filename for clip in clip_index.clips}
    
    valid = all(rec in available_filenames for rec in all_recommended)
    
    if valid:
        print(f"[PASS] All {len(all_recommended)} recommended clips exist in library")
    else:
        missing = all_recommended - available_filenames
        print(f"[WARN] {len(missing)} recommended clips not found: {missing}")
    
    print("\n[DONE]")

if __name__ == "__main__":
    test_advisor()
