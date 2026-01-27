"""
End-to-end test for enhanced clip analysis (v7.0)
Tests: motion detection, intensity, semantic fields, best moments
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.brain import analyze_all_clips
from models import ClipMetadata

def test_clip_analysis():
    """Run comprehensive analysis on clip45.mp4 and verify all fields"""
    
    clip_path = "data/samples/clips/clip45.mp4"
    
    print(f"\n{'='*60}")
    print(f"TESTING CLIP ANALYSIS v7.0")
    print(f"{'='*60}\n")
    print(f"Analyzing: {clip_path}")
    
    # Run analysis
    result = analyze_all_clips([clip_path])
    clip = result.clips[0]
    
    # Verification checks
    checks_passed = 0
    checks_total = 0
    
    print(f"\n{'='*60}")
    print(f"VERIFICATION CHECKS")
    print(f"{'='*60}\n")
    
    # Check 1: Energy not defaulting to Medium
    checks_total += 1
    energy_check = clip.energy.value in ["Low", "High"]
    if energy_check:
        print(f"[PASS] Energy: {clip.energy.value} (not Medium bias)")
        checks_passed += 1
    else:
        print(f"[WARN] Energy: {clip.energy.value} (Medium - acceptable but check if correct)")
    
    # Check 2: Motion for slow pan
    checks_total += 1
    motion_check = clip.motion.value == "Dynamic"  # GENTLE maps to Dynamic
    if motion_check:
        print(f"[PASS] Motion: {clip.motion.value} (detected movement)")
        checks_passed += 1
    else:
        print(f"[FAIL] Motion: {clip.motion.value} (should detect pan as Dynamic)")
    
    # Check 3: Intensity present
    checks_total += 1
    intensity_check = 1 <= clip.intensity <= 3
    if intensity_check:
        print(f"[PASS] Intensity: {clip.intensity} (valid range)")
        checks_passed += 1
    else:
        print(f"[FAIL] Intensity: {clip.intensity} (out of range)")
    
    # Check 4: Primary subject populated
    checks_total += 1
    subject_check = len(clip.primary_subject) > 0
    if subject_check:
        print(f"[PASS] Primary Subject: {clip.primary_subject}")
        checks_passed += 1
    else:
        print(f"[FAIL] Primary Subject: empty")
    
    # Check 5: Best moments all present
    checks_total += 1
    moments_check = (
        clip.best_moments is not None and
        "High" in clip.best_moments and
        "Medium" in clip.best_moments and
        "Low" in clip.best_moments
    )
    if moments_check:
        print(f"[PASS] Best Moments: All 3 energy levels present")
        checks_passed += 1
    else:
        print(f"[FAIL] Best Moments: Missing levels")
    
    # Check 6: Moment roles populated
    checks_total += 1
    if clip.best_moments:
        roles = [bm.moment_role for bm in clip.best_moments.values()]
        roles_check = all(role for role in roles)
        if roles_check:
            print(f"[PASS] Moment Roles: {set(roles)}")
            checks_passed += 1
        else:
            print(f"[FAIL] Moment Roles: Some empty")
    
    # Check 7: Stable moment flags
    checks_total += 1
    if clip.best_moments:
        stable_check = all(hasattr(bm, 'stable_moment') for bm in clip.best_moments.values())
        if stable_check:
            stable_values = [bm.stable_moment for bm in clip.best_moments.values()]
            print(f"[PASS] Stable Moment Flags: {stable_values}")
            checks_passed += 1
        else:
            print(f"[FAIL] Stable Moment Flags: Missing")
    
    # Check 8: Legacy fields backward compatible
    checks_total += 1
    legacy_check = hasattr(clip, 'vibes') and hasattr(clip, 'content_description')
    if legacy_check:
        print(f"[PASS] Legacy Fields: Present (backward compat)")
        checks_passed += 1
    else:
        print(f"[FAIL] Legacy Fields: Missing")
    
    # Detailed output
    print(f"\n{'='*60}")
    print(f"FULL ANALYSIS RESULT")
    print(f"{'='*60}\n")
    
    print(f"Energy: {clip.energy.value}")
    print(f"Motion: {clip.motion.value}")
    print(f"Intensity: {clip.intensity}")
    print(f"Primary Subject: {clip.primary_subject}")
    print(f"Narrative Utility: {clip.narrative_utility}")
    print(f"Emotional Tone: {clip.emotional_tone}")
    print(f"Clip Quality: {clip.clip_quality}/5")
    print(f"Best For: {clip.best_for}")
    print(f"Avoid For: {clip.avoid_for}")
    
    print(f"\nBest Moments:")
    if clip.best_moments:
        for level, bm in clip.best_moments.items():
            print(f"  {level:6s}: {bm.start:5.2f}s - {bm.end:5.2f}s | {bm.moment_role:12s} | Stable: {bm.stable_moment}")
    
    print(f"\nLegacy Fields:")
    print(f"  Vibes: {clip.vibes}")
    print(f"  Content: {clip.content_description}")
    
    # Final verdict
    print(f"\n{'='*60}")
    print(f"TEST RESULT: {checks_passed}/{checks_total} checks passed")
    print(f"{'='*60}\n")
    
    if checks_passed == checks_total:
        print("[SUCCESS] ALL CHECKS PASSED - Ready for full re-cache")
        return True
    elif checks_passed >= checks_total - 2:
        print("[WARN] MOSTLY PASSING - Review failures before full re-cache")
        return False
    else:
        print("[FAIL] MULTIPLE FAILURES - Fix issues before proceeding")
        return False

if __name__ == "__main__":
    try:
        success = test_clip_analysis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[CRASH] TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
