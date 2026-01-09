"""
Zero-API Pure Logic Test

Mocks the Brain module to only use cache files and pre-computed blueprints.
No network calls to Gemini will be made.
"""

import sys
import json
import os
from pathlib import Path
import uuid
from typing import List

# Mocking brain module before imports
import google.generativeai as genai

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "backend" / ".env")

sys.path.insert(0, str(Path(__file__).parent / "backend"))

import engine.brain as brain
from models import StyleBlueprint, ClipMetadata, ClipIndex, EnergyLevel, MotionType, BestMoment

def mock_analyze_reference_video(video_path: str, api_key: str | None = None) -> StyleBlueprint:
    print(f"\n[MOCK BRAIN] Using pre-computed blueprint for {Path(video_path).name}")
    blueprint_path = Path("data/samples/test_reference_blueprint.json")
    with open(blueprint_path, 'r') as f:
        data = json.load(f)
    return StyleBlueprint(**data)

def mock_analyze_all_clips(clip_paths: List[str], api_key: str | None = None, use_comprehensive: bool = True) -> ClipIndex:
    print(f"\n[MOCK BRAIN] Loading analysis for {len(clip_paths)} clips from cache...")
    
    cache_dir = Path("data/cache")
    clips = []
    
    from engine.processors import get_video_duration
    
    for path in clip_paths:
        duration = get_video_duration(path)
        filename = Path(path).name
        
        # Look for matching cache file by trying to hit the hash
        import hashlib
        with open(path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:12]
        
        cache_file = cache_dir / f"clip_comprehensive_{file_hash}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                best_moments = {
                    level: BestMoment(**bm_data)
                    for level, bm_data in data.get("best_moments", {}).items()
                }
                clips.append(ClipMetadata(
                    filename=filename,
                    filepath=path,
                    duration=duration,
                    energy=EnergyLevel(data["energy"]),
                    motion=MotionType(data["motion"]),
                    best_moments=best_moments
                ))
                print(f"  [OK] Loaded cache for {filename}")
        else:
            # Fallback for mock mode if cache missing
            print(f"  [WARN] No cache found for {filename}, using defaults")
            clips.append(ClipMetadata(
                filename=filename,
                filepath=path,
                duration=duration,
                energy=EnergyLevel.MEDIUM,
                motion=MotionType.DYNAMIC
            ))
            
    return ClipIndex(clips=clips)

# Apply mocks
brain.analyze_reference_video = mock_analyze_reference_video
brain.analyze_all_clips = mock_analyze_all_clips

from engine.orchestrator import run_mimic_pipeline

def main():
    print("\n" + "="*60)
    print("MOCKED ZERO-API RECONSTRUCTION")
    print("="*60)
    
    reference_path = "data/samples/reference/refrence_vid.mp4"
    clips_dir = Path("data/samples/clips")
    
    # Get all 16 clips
    all_files = list(clips_dir.glob("*.mp4")) + list(clips_dir.glob("*.MP4"))
    unique_files = {f.name.lower(): f for f in all_files}
    clip_files = sorted(unique_files.values())
    clip_paths = [str(f) for f in clip_files]
    
    session_id = f"reconstruction_{uuid.uuid4().hex[:8]}"
    
    result = run_mimic_pipeline(
        reference_path=reference_path,
        clip_paths=clip_paths,
        session_id=session_id,
        output_dir="data/results"
    )
    
    if not result.success:
        print(f"\n❌ FAILED: {result.error}")
        return 1
        
    print("\n" + "="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"Output: {result.output_path}")
    print(f"Segments: {len(result.blueprint.segments)}")
    print(f"Cuts: {len(result.edl.decisions)}")
    print(f"\n🎬 Your video is ready: {result.output_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
