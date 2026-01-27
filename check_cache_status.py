import json
from pathlib import Path

cache_dir = Path("data/cache")

# Check clip caches
clip_files = list(cache_dir.glob("clip_comprehensive_*.json"))
print(f"Total clip caches: {len(clip_files)}")

if clip_files:
    versions = {}
    motion_types = []
    for f in clip_files[:10]:
        data = json.load(open(f))
        v = data.get("_cache_version", "MISSING")
        versions[v] = versions.get(v, 0) + 1
        motion_types.append(data.get("motion", "MISSING"))
    
    print(f"Versions: {versions}")
    print(f"Sample motion types: {set(motion_types[:10])}")
