"""
Test ref4 with the new Vibes + BPM system.
This will generate ref4_v4.mp4 with semantic matching and dynamic BPM.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.orchestrator import run_mimic_pipeline
from engine.processors import get_video_duration
import os

# Paths
REFERENCE = Path("data/samples/reference/ref4.mp4")
CLIPS_DIR = Path("data/samples/clips")
RESULTS_DIR = Path("data/results")

# Get all clips (you said you have 20 now)
CLIP_PATHS = sorted([str(CLIPS_DIR / f) for f in os.listdir(CLIPS_DIR) if f.endswith('.mp4')])

print("=" * 80)
print("🎬 TESTING REF4 WITH VIBES + DYNAMIC BPM")
print("=" * 80)

# Get reference info
ref_duration = get_video_duration(str(REFERENCE))
print(f"\n📹 Reference: {REFERENCE.name}")
print(f"   Duration: {ref_duration:.2f}s")
print(f"\n📎 Testing with {len(CLIP_PATHS)} clips")
print(f"   Cache Version: 4.0 (will re-analyze clips for vibes)")
print()

# Run pipeline
session_id = "ref4_v4_vibes_test"

print("🚀 Starting pipeline...")
print("   Step 1: Validating inputs")
print("   Step 2: Scene detection + BPM detection + Reference analysis")
print("   Step 3: Clip analysis (NEW: extracting vibes + content)")
print("   Step 4: Semantic matching (NEW: vibe-aware selection)")
print("   Step 5: Rendering with dynamic BPM sync")
print()

result = run_mimic_pipeline(
    reference_path=str(REFERENCE),
    clip_paths=CLIP_PATHS,
    session_id=session_id,
    output_dir=str(RESULTS_DIR),
    progress_callback=None
)

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
    print(f"   Processing time: {result.processing_time_seconds:.1f}s")
    
    if result.blueprint:
        print(f"\n🎬 Editing Details:")
        print(f"   Segments detected: {len(result.blueprint.segments)}")
        
        # Count unique clips used
        if result.edl:
            unique_clips = set()
            vibe_matches = 0
            for decision in result.edl.decisions:
                unique_clips.add(Path(decision.clip_path).name)
                if decision.vibe_match:
                    vibe_matches += 1
            
            print(f"   Unique clips used: {len(unique_clips)}/{len(CLIP_PATHS)}")
            print(f"   Total cuts: {len(result.edl.decisions)}")
            print(f"   🧠 Vibe matches: {vibe_matches}/{len(result.edl.decisions)} ({vibe_matches/len(result.edl.decisions)*100:.1f}%)")
            
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
    print("\n💡 Check the logs above for '🧠 AI Thinking' messages to see semantic matching in action!")
else:
    print("❌ FAILED")
    print(f"   Error: {result.error}")

print("=" * 80)
