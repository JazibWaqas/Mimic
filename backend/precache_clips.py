"""
Pre-cache all clips in data/samples/clips/ for quota-free future tests.
This analyzes all clips once via Gemini API, then they're cached forever.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from engine.brain import analyze_all_clips

load_dotenv()

def main():
    base_dir = Path(__file__).parent.parent
    clips_dir = base_dir / "data" / "samples" / "clips"
    
    if not clips_dir.exists():
        print(f"ERROR: Clips directory not found: {clips_dir}")
        return
    
    clip_files = sorted(clips_dir.glob("*.mp4"))
    
    if not clip_files:
        print(f"ERROR: No MP4 files found in {clips_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"PRE-CACHING {len(clip_files)} CLIPS")
    print(f"{'='*60}\n")
    print("This will call Gemini API once for each clip.")
    print("After this, all clips will be cached (0 API calls on future tests).\n")
    
    clip_paths = [str(f) for f in clip_files]
    
    try:
        clip_index = analyze_all_clips(clip_paths)
        
        print(f"\n{'='*60}")
        print(f"SUCCESS: All {len(clip_index.clips)} clips cached!")
        print(f"{'='*60}\n")
        print("Now you can test with different reference videos:")
        print("- Reference video: 1 API call per new reference")
        print("- All clips: 0 API calls (cached)")
        print(f"\nTotal API calls used: {len(clip_index.clips)}")
        print(f"Total API calls saved on future tests: Unlimited!\n")
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR: Pre-caching failed: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
