import os
import sys
from pathlib import Path

# Add backend to path so we can import engine
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.engine.brain import analyze_reference_video
from backend.engine.processors import detect_scene_changes

def main():
    ref_dir = Path("data/samples/reference")
    videos = list(ref_dir.glob("*.mp4"))
    
    print(f"Found {len(videos)} reference videos for analysis.")
    
    for i, video_path in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] Processing: {video_path.name}")
        try:
            # We use scene detection hints to ensure perfect cut alignment
            # This matches the orchestrator's behavior
            print(f"  🔍 Detecting scene changes...")
            scene_timestamps = detect_scene_changes(str(video_path), threshold=0.15)
            
            print(f"  🧠 Calling Gemini 3 for comprehensive analysis...")
            result = analyze_reference_video(str(video_path), scene_timestamps=scene_timestamps)
            print(f"  ✅ Analysis saved to cache: {result.text_overlay[:30]}...")
        except Exception as e:
            print(f"  ❌ Error analyzing {video_path.name}: {e}")

if __name__ == "__main__":
    main()
