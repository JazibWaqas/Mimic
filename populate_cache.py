"""
MIMIC Cache Population Script (v5.0)

This script iterates through all clips in data/samples/clips and performs
the comprehensive Gemini analysis to populate the cache.

Safety Features:
- No silent failures (hard fail instead of default data)
- Sequential processing to avoid RPM limits
- Key rotation handling
- Automatic resumability (skips already cached clips)
"""

import sys
import os
import json
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.brain import analyze_all_clips, CACHE_VERSION
from utils.api_key_manager import get_key_manager

# Configuration
CLIPS_DIR = Path("data/samples/clips")
CACHE_DIR = Path("data/cache")

def main():
    print("=" * 80)
    print(f"🚀 MIMIC CACHE POPULATOR (Version {CACHE_VERSION})")
    print("=" * 80)

    # 1. Check directories
    if not CLIPS_DIR.exists():
        print(f"❌ Error: Clips directory not found at {CLIPS_DIR}")
        return

    # 2. Get list of clips
    clip_paths = sorted([
        str(CLIPS_DIR / f) for f in os.listdir(CLIPS_DIR) 
        if f.lower().endswith(('.mp4', '.mov', '.avi'))
    ])
    
    total_clips = len(clip_paths)
    if total_clips == 0:
        print("❌ No clips found to analyze.")
        return

    print(f"📁 Found {total_clips} clips in {CLIPS_DIR}")
    
    # 3. Check status
    key_manager = get_key_manager()
    print(f"🔑 Keys loaded: {key_manager.get_all_keys_count()}")
    print(f"🔑 Keys remaining: {key_manager.get_remaining_keys_count()}")
    print("-" * 80)

    # 4. Start Analysis
    start_time = time.time()
    print(f"🎬 Starting analysis of {total_clips} clips...")
    print(f"   Note: This will skip clips already in cache (v{CACHE_VERSION})")
    print()

    successful_clips = []
    failed_clips = []

    for clip_path in clip_paths:
        try:
            # Analyze a single clip (use the internal list version with 1 clip)
            # This allows us to catch errors per CLIP instead of per BATCH
            index_chunk = analyze_all_clips([clip_path])
            if index_chunk.clips:
                successful_clips.extend(index_chunk.clips)
        except Exception as e:
            print(f"   ⚠️  FAILED {Path(clip_path).name}: {e}")
            failed_clips.append((clip_path, str(e)))
        
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("✅ CACHE POPULATION FINISHED")
    print("=" * 80)
    print(f"📊 Summary:")
    print(f"    Total Clips: {total_clips}")
    print(f"    Successful: {len(successful_clips)}")
    print(f"    Failed: {len(failed_clips)}")
    print(f"    Total Time: {elapsed:.1f}s")
    
    if failed_clips:
        print("\n❌ Failed Clips:")
        for path, err in failed_clips:
            print(f"   - {Path(path).name}: {err[:100]}...")
    
    print()
    print("🎉 Done! Use successfully cached clips in your pipeline.")

if __name__ == "__main__":
    main()
