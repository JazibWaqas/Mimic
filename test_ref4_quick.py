"""
Quick test with ref4.mp4 to demonstrate the fixes.
"""

import os
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.orchestrator import run_mimic_pipeline
from engine.processors import get_video_duration

# Paths
REFERENCE = Path("data/samples/reference/ref4.mp4")
CLIPS_DIR = Path("data/samples/clips")
RESULTS_DIR = Path("data/results")

# Get all clips
CLIP_PATHS = sorted([str(CLIPS_DIR / f) for f in os.listdir(CLIPS_DIR) if f.endswith('.mp4')])

print("=" * 80)
print("🎬 TESTING FIXES WITH REF4")
print("=" * 80)

# Get reference info
ref_duration = get_video_duration(str(REFERENCE))
print(f"\n📹 Reference: {REFERENCE.name}")
print(f"   Duration: {ref_duration:.2f}s")
print(f"\n📎 Testing with {len(CLIP_PATHS)} clips\n")

# Run pipeline
session_id = "test_ref4_fixed"
start_time = time.time()

result = run_mimic_pipeline(
    reference_path=str(REFERENCE),
    clip_paths=CLIP_PATHS,
    session_id=session_id,
    output_dir=str(RESULTS_DIR),
    progress_callback=None
)

elapsed = time.time() - start_time

# Report results
print("\n" + "=" * 80)
if result.success:
    output_path = RESULTS_DIR / f"mimic_output_{session_id}.mp4"
    output_duration = get_video_duration(str(output_path))
    
    print("✅ SUCCESS!")
    print(f"\n📊 Results:")
    print(f"   Output: {output_path.name}")
    print(f"   Duration: {output_duration:.2f}s (ref: {ref_duration:.2f}s)")
    print(f"   Difference: {abs(output_duration - ref_duration):.2f}s")
    print(f"   Processing time: {elapsed:.1f}s")
    
    if result.blueprint:
        print(f"\n🎬 Editing Details:")
        print(f"   Segments detected: {len(result.blueprint.segments)}")
        
        # Count unique clips used
        if result.edl:
            unique_clips = set()
            for decision in result.edl.decisions:
                unique_clips.add(Path(decision.clip_path).name)
            
            print(f"   Unique clips used: {len(unique_clips)}/{len(CLIP_PATHS)}")
            print(f"   Total cuts: {len(result.edl.decisions)}")
            
            # Show cut distribution
            if result.edl.decisions:
                durations = [(d.timeline_end - d.timeline_start) for d in result.edl.decisions]
                avg_cut = sum(durations) / len(durations)
                min_cut = min(durations)
                max_cut = max(durations)
                
                print(f"\n📏 Cut Statistics:")
                print(f"   Average cut: {avg_cut:.2f}s")
                print(f"   Shortest cut: {min_cut:.2f}s")
                print(f"   Longest cut: {max_cut:.2f}s")
                
    print(f"\n🎉 Watch the result: {output_path}")
else:
    print("❌ FAILED")
    print(f"   Error: {result.error}")

print("=" * 80)
