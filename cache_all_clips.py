"""
Cache All Clips - Comprehensive Analysis

Analyzes ALL clips in data/samples/clips/ and caches them.
Once cached, you can use any reference video without re-analyzing clips.
"""

import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "backend" / ".env")

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.brain import analyze_all_clips

def main():
    print("\n" + "="*60)
    print("CACHING ALL CLIPS - COMPREHENSIVE ANALYSIS")
    print("="*60)
    
    clips_dir = Path("data/samples/clips")
    
    # Get all clips (avoiding duplicates on case-insensitive systems)
    all_files = list(clips_dir.glob("*.mp4")) + list(clips_dir.glob("*.MP4"))
    # Use a dictionary to keep unique paths by case-insensitive name
    unique_files = {f.name.lower(): f for f in all_files}
    clip_files = sorted(unique_files.values())
    clip_paths = [str(f) for f in clip_files]
    
    import os
    api_key = os.getenv("GEMINI_API_KEY")
    key_hint = f"{api_key[:8]}...{api_key[-4:]}" if api_key else "MISSING"
    print(f"\n[DEBUG] Using API Key: {key_hint}")
    
    print(f"\nFound {len(clip_paths)} unique clips:")
    for i, clip in enumerate(clip_paths, 1):
        print(f"  {i}. {Path(clip).name}")
    
    print(f"\n⚠️  This will use ~{len(clip_paths)} Gemini API calls")
    print("⚠️  Each clip gets: energy, motion, + best moments for High/Medium/Low")
    print("\nStarting analysis...\n")
    
    # Analyze all clips with comprehensive mode
    clip_index = analyze_all_clips(
        clip_paths=clip_paths,
        use_comprehensive=True  # This is the key - gets best moments for all energy levels
    )
    
    print("\n" + "="*60)
    print("CACHE COMPLETE")
    print("="*60)
    
    # Show summary
    for clip in clip_index.clips:
        print(f"\n{clip.filename}:")
        print(f"  Energy: {clip.energy.value}, Motion: {clip.motion.value}")
        if clip.best_moments:
            print(f"  Best moments:")
            for level, moment in clip.best_moments.items():
                print(f"    {level}: {moment.start:.2f}s - {moment.end:.2f}s")
                print(f"         → {moment.reason}")
        else:
            print(f"  ⚠️  No best moments (analysis may have failed)")
    
    print(f"\n✅ All {len(clip_paths)} clips cached!")
    print("✅ You can now use ANY reference video without re-analyzing clips")
    print("\nCache location: data/cache/clip_comprehensive_*.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
