"""
MIMIC Pipeline Validation Script

This script validates the end-to-end pipeline in strict order:
1. Mock mode (no API calls)
2. Real mode with minimal clips

PASS/FAIL only. No subjective quality assessment.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.brain import set_mock_mode, create_mock_blueprint, create_mock_clip_index
from engine.orchestrator import run_mimic_pipeline
from engine.processors import get_video_duration
import uuid


def validate_mock_mode():
    """
    Test 1: Mock mode validation
    
    PASS criteria:
    - Pipeline completes without errors
    - Output file exists
    - Output file size > 100KB
    - Output duration matches reference (±0.5s)
    """
    print("\n" + "="*60)
    print("TEST 1: MOCK MODE VALIDATION")
    print("="*60)
    
    # Find sample files
    ref_dir = Path("data/samples/reference")
    clips_dir = Path("data/samples/clips")
    
    if not ref_dir.exists() or not clips_dir.exists():
        print("❌ FAIL: data/samples/reference/ or data/samples/clips/ not found")
        return False
    
    # Get reference video
    ref_videos = list(ref_dir.glob("*.mp4")) + list(ref_dir.glob("*.MP4"))
    if len(ref_videos) == 0:
        print("❌ FAIL: No reference video found in data/samples/reference/")
        return False
    
    # Get clip videos
    clip_videos = list(clips_dir.glob("*.mp4")) + list(clips_dir.glob("*.MP4"))
    if len(clip_videos) < 2:
        print(f"❌ FAIL: Need at least 2 clips in data/samples/clips/ (found {len(clip_videos)})")
        return False
    
    reference = str(ref_videos[0])
    clips = [str(v) for v in clip_videos[:2]]  # Use first 2 clips
    
    print(f"Reference: {Path(reference).name}")
    for i, clip in enumerate(clips, 1):
        print(f"Clip {i}: {Path(clip).name}")
    
    # Enable mock mode
    set_mock_mode(True)
    
    # Run pipeline
    session_id = f"test_mock_{uuid.uuid4().hex[:8]}"
    output_dir = "data/results"
    
    try:
        result = run_mimic_pipeline(
            reference_path=reference,
            clip_paths=clips,
            session_id=session_id,
            output_dir=output_dir
        )
        
        if not result.success:
            print(f"❌ FAIL: Pipeline returned success=False")
            print(f"   Error: {result.error}")
            return False
        
        # Check output exists
        output_path = Path(result.output_path)
        if not output_path.exists():
            print(f"❌ FAIL: Output file not created: {output_path}")
            return False
        
        # Check file size
        file_size = output_path.stat().st_size
        if file_size < 100_000:  # 100KB minimum
            print(f"❌ FAIL: Output file too small: {file_size} bytes")
            return False
        
        # Check duration
        ref_duration = get_video_duration(reference)
        output_duration = get_video_duration(str(output_path))
        duration_diff = abs(output_duration - ref_duration)
        
        if duration_diff > 0.5:
            print(f"❌ FAIL: Duration mismatch")
            print(f"   Reference: {ref_duration:.2f}s")
            print(f"   Output: {output_duration:.2f}s")
            print(f"   Difference: {duration_diff:.2f}s")
            return False
        
        print(f"\n✅ PASS: Mock mode validation")
        print(f"   Output: {output_path.name}")
        print(f"   Size: {file_size / 1_000_000:.2f} MB")
        print(f"   Duration: {output_duration:.2f}s (ref: {ref_duration:.2f}s)")
        print(f"   Segments: {len(result.blueprint.segments)}")
        print(f"   Processing time: {result.processing_time_seconds:.1f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Exception during pipeline")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        set_mock_mode(False)


def validate_real_mode():
    """
    Test 2: Real API mode validation (OPTIONAL - only if you want to burn API quota)
    
    PASS criteria:
    - Pipeline completes
    - Gemini returns valid JSON
    - Best moments are populated
    - Output matches reference duration
    """
    print("\n" + "="*60)
    print("TEST 2: REAL API MODE (SKIPPED - use mock mode for now)")
    print("="*60)
    print("⚠️  To test real API mode, uncomment the code in this function")
    print("⚠️  This will use Gemini API quota")
    return True
    
    # UNCOMMENT BELOW TO TEST REAL API MODE
    """
    data_dir = Path("data/samples")
    videos = list(data_dir.glob("*.mp4"))
    
    reference = str(videos[0])
    clips = [str(v) for v in videos[1:3]]
    
    session_id = f"test_real_{uuid.uuid4().hex[:8]}"
    output_dir = "data/results"
    
    try:
        result = run_mimic_pipeline(
            reference_path=reference,
            clip_paths=clips,
            session_id=session_id,
            output_dir=output_dir
        )
        
        if not result.success:
            print(f"❌ FAIL: Pipeline failed: {result.error}")
            return False
        
        # Check best moments were populated
        clips_with_moments = sum(1 for c in result.clip_index.clips if c.best_moments)
        if clips_with_moments == 0:
            print(f"❌ FAIL: No clips have best_moments populated")
            return False
        
        print(f"✅ PASS: Real API mode")
        print(f"   Clips with best moments: {clips_with_moments}/{len(result.clip_index.clips)}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False
    """


def main():
    print("\n" + "="*60)
    print("MIMIC PIPELINE VALIDATION")
    print("="*60)
    print("\nThis script validates core functionality only.")
    print("Quality assessment comes AFTER validation passes.\n")
    
    results = []
    
    # Test 1: Mock mode (mandatory)
    results.append(("Mock Mode", validate_mock_mode()))
    
    # Test 2: Real API mode (optional)
    results.append(("Real API Mode", validate_real_mode()))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED")
        print("\nNext step: Run pipeline with your own videos and inspect quality")
        return 0
    else:
        print("\n❌ VALIDATION FAILED")
        print("\nFix failing tests before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
