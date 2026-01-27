"""
Re-cache all clips with v7.0 enhanced analysis.
Run this once to rebuild the clip cache with new fields.
"""

import sys
from pathlib import Path
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.brain import analyze_all_clips

def recache_all_clips():
    """Re-analyze all clips and rebuild cache"""
    
    clips_dir = Path("data/samples/clips")
    
    # Get all clip paths
    clip_paths = sorted([
        str(clips_dir / f) 
        for f in os.listdir(clips_dir) 
        if f.endswith('.mp4')
    ])
    
    print(f"\n{'='*60}")
    print(f"RE-CACHING ALL CLIPS (v7.0)")
    print(f"{'='*60}\n")
    print(f"Found {len(clip_paths)} clips")
    print(f"Location: {clips_dir}")
    print(f"\nThis will:")
    print(f"  - Invalidate old v6.1 cache files")
    print(f"  - Re-analyze with enhanced v7.0 prompt")
    print(f"  - Add: intensity, semantic content, moment roles")
    print(f"\nEstimated time: ~{len(clip_paths) * 45} seconds ({len(clip_paths) * 45 / 60:.1f} minutes)")
    print(f"\n{'='*60}\n")
    
    # Run comprehensive analysis
    result = analyze_all_clips(clip_paths, use_comprehensive=True)
    
    # Summary statistics
    energy_dist = {"Low": 0, "Medium": 0, "High": 0}
    intensity_dist = {1: 0, 2: 0, 3: 0}
    
    for clip in result.clips:
        energy_dist[clip.energy.value] += 1
        intensity_dist[clip.intensity] += 1
    
    print(f"\n{'='*60}")
    print(f"RE-CACHE COMPLETE")
    print(f"{'='*60}\n")
    
    print(f"Total clips analyzed: {len(result.clips)}")
    print(f"\nEnergy Distribution:")
    print(f"  Low:    {energy_dist['Low']:2d} ({energy_dist['Low']/len(result.clips)*100:5.1f}%)")
    print(f"  Medium: {energy_dist['Medium']:2d} ({energy_dist['Medium']/len(result.clips)*100:5.1f}%)")
    print(f"  High:   {energy_dist['High']:2d} ({energy_dist['High']/len(result.clips)*100:5.1f}%)")
    
    print(f"\nIntensity Distribution:")
    print(f"  1 (mild):    {intensity_dist[1]:2d} clips")
    print(f"  2 (clear):   {intensity_dist[2]:2d} clips")
    print(f"  3 (strong):  {intensity_dist[3]:2d} clips")
    
    # Spot check: show 3 random clips
    import random
    sample_clips = random.sample(result.clips, min(3, len(result.clips)))
    
    print(f"\n{'='*60}")
    print(f"SPOT CHECK (3 random clips)")
    print(f"{'='*60}\n")
    
    for clip in sample_clips:
        print(f"{clip.filename}:")
        print(f"  Energy: {clip.energy.value} | Intensity: {clip.intensity} | Motion: {clip.motion.value}")
        print(f"  Subject: {', '.join(clip.primary_subject)}")
        print(f"  Quality: {clip.clip_quality}/5")
        if clip.best_moments:
            roles = [bm.moment_role for bm in clip.best_moments.values()]
            print(f"  Moment Roles: {set(roles)}")
        print()
    
    print(f"{'='*60}")
    print(f"Cache location: data/cache/clip_comprehensive_*.json")
    print(f"{'='*60}\n")
    
    return result

if __name__ == "__main__":
    try:
        result = recache_all_clips()
        print("[SUCCESS] All clips re-cached successfully")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Re-cache failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
