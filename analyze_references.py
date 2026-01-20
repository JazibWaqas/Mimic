import os
import sys
import json
from pathlib import Path

# Absolute path to the Mimic root and backend
ROOT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = ROOT_DIR / "backend"

# add to sys.path
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Now try importing
try:
    from engine.brain import analyze_reference_video
    from utils.api_key_manager import get_api_key
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

def main():
    reference_dir = ROOT_DIR / "data" / "samples" / "reference"
    # Skip ref3.mp4 for now (known recitation issues)
    # Prioritize ref4.mp4 and refrence2.mp4
    all_refs = list(reference_dir.glob("*.mp4"))
    references = [r for r in all_refs if "ref3.mp4" not in r.name]
    references.sort(key=lambda x: "ref4" not in x.name) # Put ref4 first
    
    if not references:
        print(f"No reference videos found in {reference_dir}")
        return

    print(f"🔍 Found {len(references)} reference videos. Starting deep analysis...")
    print(f"Using CACHE_VERSION 6.0 with Emotional Arc analysis.\n")

    successful = []
    failed = []

    for ref_path in references:
        print(f"🎬 Analyzing: {ref_path.name}...")
        try:
            # Re-analysis will be triggered because CACHE_VERSION changed to 6.0
            blueprint = analyze_reference_video(str(ref_path))
            
            print(f"   ✅ Done! Style: {blueprint.editing_style}")
            print(f"   ❤️  Intent: {blueprint.emotional_intent}")
            print(f"   📈 Arc: {blueprint.arc_description[:100]}...")
            print(f"   📊 Segments: {len(blueprint.segments)}")
            successful.append(ref_path.name)
            print("-" * 40)
        except Exception as e:
            print(f"   ⚠️  SKIPPING {ref_path.name}: {e}")
            failed.append((ref_path.name, str(e)))
            print("-" * 40)

    print("\n" + "=" * 40)
    print("🏁 ANALYSIS SUMMARY")
    print(f"   ✅ Successful: {len(successful)}")
    print(f"   ❌ Failed: {len(failed)}")
    for name, err in failed:
        print(f"      - {name}: {err[:100]}...")
    print("=" * 40)

if __name__ == "__main__":
    main()
