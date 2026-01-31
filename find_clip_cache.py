import os
import hashlib
import json
from pathlib import Path

# Paths
clips_dir = Path("c:/Users/OMNIBOOK/Documents/GitHub/Mimic/data/samples/clips")
cache_dir = Path("c:/Users/OMNIBOOK/Documents/GitHub/Mimic/data/cache")

def get_file_hash(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:12]

print(f"{'Filename':<12} | {'Hash':<14} | {'Subjects':<35} | {'Vibes':<25}")
print("-" * 100)

mislabeled_candidates = []

for clip in sorted(clips_dir.glob("*.mp4")):
    file_hash = get_file_hash(clip)
    cache_file = cache_dir / f"clip_comprehensive_{file_hash}.json"
    
    if cache_file.exists():
        with open(cache_file, encoding='utf-8') as f:
            data = json.load(f)
            subjects = data.get("primary_subject", [])
            vibes = data.get("vibes", [])
            
            # Identify potential issues:
            # 1. "People-Group" but vibes include "Nature", "Urban", "Scenic", or clip description is about objects
            desc = data.get("content_description", "").lower()
            
            is_people = "People-Group" in subjects or "People-Solo" in subjects
            is_scenic = any(s in subjects for s in ["Place-Nature", "Place-Urban"]) or any(v in vibes for v in ["Nature", "Urban"])
            is_object = "Object-Detail" in subjects or "tea" in desc or "pouring" in desc or "drink" in desc
            
            flag = ""
            if is_people and (is_scenic or is_object):
                flag = "[POTENTIAL MISMATCH]"
                mislabeled_candidates.append((clip.name, cache_file, data))
            
            subject_str = ", ".join(subjects)
            vibe_str = ", ".join(vibes)
            print(f"{clip.name:<12} | {file_hash:<14} | {subject_str:<35} | {vibe_str:<25} {flag}")
    else:
        print(f"{clip.name:<12} | {file_hash:<14} | [NO CACHE FOUND]")

print("\n\n" + "="*80)
print("POTENTIAL MISLABELED CLIPS FOUND:")
print("="*80)
for name, path, data in mislabeled_candidates:
    print(f"\nClip: {name}")
    print(f"Cache: {path}")
    print(f"Description: {data.get('content_description')}")
    print(f"Subjects: {data.get('primary_subject')}")
    print(f"Vibes: {data.get('vibes')}")
