"""
Batch Test Script - Tests multiple reference videos with cached clips.

This script runs the MIMIC pipeline on multiple reference videos
and generates a comparison report.
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
REFERENCE_DIR = Path("data/samples/reference")
CLIPS_DIR = Path("data/samples/clips")
RESULTS_DIR = Path("data/results")

# Reference videos to test
REFERENCES = [
    "ref3.mp4",
    "ref4.mp4", 
    "ref5.mp4"
]

# Get all clips (same clips for all tests)
CLIP_PATHS = sorted([str(CLIPS_DIR / f) for f in os.listdir(CLIPS_DIR) if f.endswith('.mp4')])

print("=" * 80)
print("MIMIC BATCH TEST - Multiple Reference Videos")
print("=" * 80)
print(f"\nFound {len(CLIP_PATHS)} clips:")
for clip in CLIP_PATHS:
    print(f"  - {Path(clip).name}")

results = []

for ref_name in REFERENCES:
    ref_path = REFERENCE_DIR / ref_name
    
    if not ref_path.exists():
        print(f"\n⚠️  SKIPPED: {ref_name} (file not found)")
        continue
    
    print("\n" + "=" * 80)
    print(f"TESTING: {ref_name}")
    print("=" * 80)
    
    # Create session ID from reference name
    ref_basename = ref_name.replace('.mp4', '')
    session_id = f"test_{ref_basename}"
    
    # Get reference duration
    ref_duration = get_video_duration(str(ref_path))
    print(f"\n📹 Reference: {ref_name}")
    print(f"   Duration: {ref_duration:.2f}s")
    
    # Run pipeline
    start_time = time.time()
    
    try:
        result = run_mimic_pipeline(
            reference_path=str(ref_path),
            clip_paths=CLIP_PATHS,
            session_id=session_id,
            output_dir=str(RESULTS_DIR),
            progress_callback=None  # Silent mode
        )
        
        elapsed = time.time() - start_time
        
        if result.success:
            output_name = f"mimic_output_{session_id}.mp4"
            output_path = RESULTS_DIR / output_name
            
            # Get output duration
            try:
                output_duration = get_video_duration(str(output_path))
                duration_diff = abs(output_duration - ref_duration)
                duration_match = "✅" if duration_diff < 0.5 else "⚠️"
                
                print(f"\n✅ SUCCESS")
                print(f"   Output: {output_name}")
                print(f"   Duration: {output_duration:.2f}s {duration_match}")
                print(f"   Difference: {duration_diff:.2f}s")
                print(f"   Processing time: {elapsed:.1f}s")
                
                # Count segments
                segment_count = len(result.blueprint.segments) if result.blueprint else 0
                
                # Count unique clips used
                unique_clips = set()
                if result.edl:
                    for decision in result.edl.decisions:
                        unique_clips.add(Path(decision.clip_path).name)
                
                print(f"   Segments detected: {segment_count}")
                print(f"   Unique clips used: {len(unique_clips)}/{len(CLIP_PATHS)}")
                
                results.append({
                    'reference': ref_name,
                    'status': 'SUCCESS',
                    'ref_duration': ref_duration,
                    'output_duration': output_duration,
                    'duration_diff': duration_diff,
                    'segments': segment_count,
                    'clips_used': len(unique_clips),
                    'processing_time': elapsed,
                    'output_file': output_name
                })
                
            except Exception as e:
                print(f"\n⚠️  Output created but couldn't verify: {e}")
                results.append({
                    'reference': ref_name,
                    'status': 'PARTIAL',
                    'error': str(e),
                    'processing_time': elapsed
                })
        else:
            print(f"\n❌ FAILED")
            print(f"   Error: {result.error}")
            results.append({
                'reference': ref_name,
                'status': 'FAILED',
                'error': result.error,
                'processing_time': elapsed
            })
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ EXCEPTION")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            'reference': ref_name,
            'status': 'EXCEPTION',
            'error': str(e),
            'processing_time': elapsed
        })

# Print summary report
print("\n" + "=" * 80)
print("SUMMARY REPORT")
print("=" * 80)

for r in results:
    print(f"\n📹 {r['reference']}")
    print(f"   Status: {r['status']}")
    
    if r['status'] == 'SUCCESS':
        duration_match = "✅ MATCH" if r['duration_diff'] < 0.5 else f"⚠️  OFF BY {r['duration_diff']:.2f}s"
        clip_usage = "✅ GOOD VARIETY" if r['clips_used'] >= len(CLIP_PATHS) * 0.7 else f"⚠️  ONLY {r['clips_used']} CLIPS"
        
        print(f"   Reference: {r['ref_duration']:.2f}s")
        print(f"   Output: {r['output_duration']:.2f}s - {duration_match}")
        print(f"   Segments: {r['segments']}")
        print(f"   Clips Used: {r['clips_used']}/{len(CLIP_PATHS)} - {clip_usage}")
        print(f"   Time: {r['processing_time']:.1f}s")
        print(f"   File: {r['output_file']}")
    else:
        print(f"   Error: {r.get('error', 'Unknown')}")
        print(f"   Time: {r['processing_time']:.1f}s")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)

# Analyze patterns
successes = [r for r in results if r['status'] == 'SUCCESS']
failures = [r for r in results if r['status'] != 'SUCCESS']

if len(successes) == len(results):
    print("\n✅ All tests passed! Check the outputs:")
    for r in successes:
        print(f"   - data/results/{r['output_file']}")
    print("\n💡 Watch each video and report:")
    print("   1. Are clips repeating back-to-back?")
    print("   2. Are individual cuts too long?")
    print("   3. Does energy/pacing match the reference?")
    print("   4. Is there good variety across clips?")
    
elif len(failures) == len(results):
    print("\n❌ All tests failed. Common issues:")
    errors = [r.get('error', '') for r in failures]
    print(f"   {errors[0]}")
    print("\n💡 This needs immediate debugging.")
    
else:
    print(f"\n⚠️  Mixed results: {len(successes)} passed, {len(failures)} failed")
    print("\n💡 Compare the successful vs failed references to find patterns.")

print("\n" + "=" * 80)
