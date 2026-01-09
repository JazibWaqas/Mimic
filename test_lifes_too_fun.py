"""
Test with Life's Too Fun reference video

All clips are already cached, so this will only analyze the reference.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "backend" / ".env")

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.orchestrator import run_mimic_pipeline
import uuid

def main():
    import os
    api_key = os.getenv("GEMINI_API_KEY")
    key_hint = f"{api_key[:8]}...{api_key[-4:]}" if api_key else "MISSING"
    print(f"\n[DEBUG] Using API Key: {key_hint}")

    print("\n" + "="*60)
    print("TESTING: Reference2 with All Cached Clips")
    print("="*60)
    
    # Use refrence2
    reference = "data/samples/reference/refrence2.mp4"
    
    # Use ALL 8 clips (they're already cached!)
    clips_dir = Path("data/samples/clips")
    clip_files = sorted(clips_dir.glob("*.mp4"))
    clips = [str(f) for f in clip_files]
    
    print(f"\nReference: {Path(reference).name}")
    print(f"Clips: {len(clips)} (all cached - no API calls for clips!)")
    
    print("\n⚠️  Will analyze reference video with Gemini")
    print("⚠️  Clips will load from cache (instant)\n")
    
    session_id = f"lifes_too_fun_{uuid.uuid4().hex[:8]}"
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
    
    print("\n" + "="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"Output: {result.output_path}")
    print(f"Duration: {result.blueprint.total_duration:.2f}s")
    print(f"Segments: {len(result.blueprint.segments)}")
    print(f"Edit decisions: {len(result.edl.decisions)}")
    print(f"Processing time: {result.processing_time_seconds:.1f}s")
    
    # Show which clips were used
    clip_usage = {}
    for decision in result.edl.decisions:
        clip_name = Path(decision.clip_path).name
        clip_usage[clip_name] = clip_usage.get(clip_name, 0) + 1
    
    print("\nClip usage:")
    for clip_name, count in sorted(clip_usage.items(), key=lambda x: -x[1]):
        print(f"  {clip_name}: {count} times")
    
    print(f"\n🎬 Watch your video: {result.output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
