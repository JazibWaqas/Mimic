"""
Real API Test - No Mock Mode

Tests the actual pipeline with Gemini API.
"""

import sys
from pathlib import Path

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "backend" / ".env")

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.orchestrator import run_mimic_pipeline
import uuid

def main():
    print("\n" + "="*60)
    print("REAL API TEST - COMPREHENSIVE CLIP ANALYSIS")
    print("="*60)
    
    # Use the new reference video
    reference = "data/samples/reference/lifes_too_fun.mp4"
    
    # Use first 3 clips
    clips = [
        "data/samples/clips/clip.mp4",
        "data/samples/clips/clip1.mp4",
        "data/samples/clips/clip2.mp4"
    ]
    
    # Check files exist
    if not Path(reference).exists():
        print(f"❌ Reference not found: {reference}")
        print("   Using old reference instead...")
        reference = "data/samples/reference/refrence_vid.mp4"
    
    for clip in clips:
        if not Path(clip).exists():
            print(f"❌ Clip not found: {clip}")
            return 1
    
    print(f"\nReference: {Path(reference).name}")
    for i, clip in enumerate(clips, 1):
        print(f"Clip {i}: {Path(clip).name}")
    
    print("\n⚠️  This will use Gemini API quota")
    print("⚠️  Comprehensive analysis: 1 reference + 3 clips = 4 API calls\n")
    
    # Run pipeline
    session_id = f"real_test_{uuid.uuid4().hex[:8]}"
    output_dir = "data/results"
    
    result = run_mimic_pipeline(
        reference_path=reference,
        clip_paths=clips,
        session_id=session_id,
        output_dir=output_dir
    )
    
    if not result.success:
        print(f"\n❌ FAILED: {result.error}")
        return 1
    
    # Check results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"✅ Output: {result.output_path}")
    print(f"✅ Duration: {result.blueprint.total_duration:.2f}s")
    print(f"✅ Segments: {len(result.blueprint.segments)}")
    print(f"✅ Processing time: {result.processing_time_seconds:.1f}s")
    
    # Check best moments
    clips_with_moments = sum(1 for c in result.clip_index.clips if c.best_moments)
    print(f"\n📊 Clips with best moments: {clips_with_moments}/{len(result.clip_index.clips)}")
    
    if clips_with_moments > 0:
        print("\nBest moments found:")
        for clip in result.clip_index.clips:
            if clip.best_moments:
                print(f"\n  {clip.filename} ({clip.energy.value}/{clip.motion.value}):")
                for level, moment in clip.best_moments.items():
                    print(f"    {level}: {moment.start:.2f}s - {moment.end:.2f}s")
    
    print("\n✅ TEST COMPLETE")
    print(f"   Watch the output: {result.output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
