import hashlib
import json
from pathlib import Path

cache_dir = Path("c:/Users/OMNIBOOK/Documents/GitHub/Mimic/data/cache")
clips_dir = Path("c:/Users/OMNIBOOK/Documents/GitHub/Mimic/data/samples/clips")

# List of common "filler" or "scenic" clips that often get mislabeled
scenic_clips = ["clip28.mp4", "clip30.mp4", "clip35.mp4", "clip45.mp4", "clip51.mp4", "clip52.mp4", "clip55.mp4", "clip57.mp4"]
object_clips = ["clip20.mp4", "clip34.mp4", "clip41.mp4", "clip42.mp4"]

all_targets = scenic_clips + object_clips

print(f"{'Filename':<15} | {'Description':<50} | {'Current Subjects'}")
print("-" * 100)

for t in all_targets:
    path = clips_dir / t
    if not path.exists(): continue
    
    h = hashlib.md5(open(path, 'rb').read()).hexdigest()[:12]
    p = cache_dir / f"clip_comprehensive_{h}.json"
    
    if p.exists():
        d = json.load(open(p))
        desc = d.get("content_description", "No description")
        subjects = d.get("primary_subject", [])
        print(f"{t:<15} | {desc[:48]:<50} | {subjects}")
