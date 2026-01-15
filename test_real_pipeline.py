"""
Real pipeline test with actual sample videos.
This will run the FULL pipeline end-to-end.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', '')

from engine.orchestrator import run_mimic_pipeline
from utils import ensure_directory

def main():
    print("\n" + "="*70)
    print("REAL PIPELINE TEST - FULL END-TO-END")
    print("="*70 + "\n")
    
    # Paths
    base_dir = Path(__file__).parent
    reference_path = base_dir / "data" / "samples" / "reference" / "refrence2.mp4"
    clips_dir = base_dir / "data" / "samples" / "clips"
    
    # Get ALL clips for testing (use all available)
    clip_paths = sorted(clips_dir.glob("*.mp4"))
    
    print(f"Reference: {reference_path.name}")
    print(f"Clips ({len(clip_paths)}):")
    for i, clip in enumerate(clip_paths, 1):
        size_mb = clip.stat().st_size / (1024 * 1024)
        print(f"  {i}. {clip.name} ({size_mb:.1f} MB)")
    print()
    
    # Create session
    import uuid
    session_id = f"test_{uuid.uuid4().hex[:8]}"
    
    # Output directory
    output_dir = base_dir / "data" / "results"
    ensure_directory(output_dir)
    
    print(f"Session ID: {session_id}")
    print(f"Output dir: {output_dir}\n")
    
    # Progress callback
    def progress_callback(step, total, message):
        print(f"\n[{step}/{total}] {message}")
    
    # Run pipeline
    try:
        result = run_mimic_pipeline(
            reference_path=str(reference_path),
            clip_paths=[str(p) for p in clip_paths],
            session_id=session_id,
            output_dir=str(output_dir),
            api_key=None,  # Will use env var
            progress_callback=progress_callback
        )
        
        print("\n" + "="*70)
        if result.success:
            print("✅ PIPELINE SUCCESS!")
            print("="*70)
            print(f"\nOutput video: {result.output_path}")
            
            # Check output exists
            if Path(result.output_path).exists():
                size_mb = Path(result.output_path).stat().st_size / (1024 * 1024)
                print(f"File size: {size_mb:.1f} MB")
                
                # Get duration
                from engine.processors import get_video_duration
                output_duration = get_video_duration(result.output_path)
                ref_duration = get_video_duration(str(reference_path))
                
                print(f"\nDuration comparison:")
                print(f"  Reference: {ref_duration:.2f}s")
                print(f"  Output:    {output_duration:.2f}s")
                print(f"  Difference: {abs(output_duration - ref_duration):.2f}s")
                
                if abs(output_duration - ref_duration) < 0.5:
                    print("  ✅ Duration matches!")
                else:
                    print("  ⚠️  Duration mismatch")
                
                # EDL stats
                if result.edl:
                    print(f"\nEdit decisions: {len(result.edl.decisions)}")
                    
                    # Count unique clips used
                    unique_clips = set()
                    for decision in result.edl.decisions:
                        clip_name = Path(decision.clip_path).name
                        unique_clips.add(clip_name)
                    
                    print(f"Unique clips used: {len(unique_clips)}/{len(clip_paths)}")
                    
                    if len(unique_clips) < len(clip_paths):
                        print(f"⚠️  Only used: {sorted(unique_clips)}")
                    else:
                        print(f"✅ All clips were used!")
                
                print(f"\n🎬 You can now view the output video at:")
                print(f"   {result.output_path}")
                
            else:
                print(f"❌ Output file not found: {result.output_path}")
                return False
                
        else:
            print("❌ PIPELINE FAILED")
            print("="*70)
            print(f"\nError: {result.error}")
            return False
            
    except Exception as e:
        print("\n" + "="*70)
        print("❌ EXCEPTION OCCURRED")
        print("="*70)
        print(f"\n{e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
