import os
import hashlib
import json
from pathlib import Path

def get_system_hash(p: Path) -> str:
    """Matches backend/utils.py logic exactly (v12.8)."""
    file_size = p.stat().st_size
    hasher = hashlib.md5()
    with open(p, "rb") as f:
        if file_size < 128 * 1024:
            hasher.update(f.read())
        else:
            hasher.update(f.read(64 * 1024))
            f.seek(max(0, file_size - 64 * 1024))
            hasher.update(f.read(64 * 1024))
    # v12.8 Hardening: Include size in the hash
    hasher.update(str(file_size).encode())
    return hasher.hexdigest()

def extract_hash_from_cache_file(f: Path) -> str | None:
    """Safely extract hash from cache filenames without positional splitting."""
    name = f.stem
    if name.startswith("clip_comprehensive_"):
        return name.replace("clip_comprehensive_", "")
    if name.startswith("std_"):
        return name.replace("std_", "")
    return None

def clean():
    print("=" * 60)
    print("MIMIC DATA DEDUPLICATOR (Safe Mode)")
    print("=" * 60)

    # 1. Deduplicate Source Clips
    clips_dir = Path('data/samples/clips')
    if not clips_dir.exists():
        print(f"Folder {clips_dir} not found.")
        return

    hashes = {}
    active_hashes = set()
    
    # Sort to ensure consistent representative (e.g. clip60.mp4 over clip60_1.mp4)
    for f in sorted(clips_dir.glob('*.mp4')):
        try:
            h = get_system_hash(f)
            if h in hashes:
                print(f"[-] Deleting duplicate source: {f.name} (matches {hashes[h]})")
                f.unlink()
            else:
                hashes[h] = f.name
                active_hashes.add(h)
        except Exception as e:
            print(f"[!] Error processing {f.name}: {e}")

    # 2. Clean Cache Folders
    # Any file not matching a known active hash is an orphan.
    for folder, ext in [('data/cache/clips', '.json'), ('data/cache/standardized', '.mp4')]:
        path = Path(folder)
        if not path.exists():
            continue
            
        removed = 0
        for f in path.glob(f'*{ext}'):
            f_hash = extract_hash_from_cache_file(f)
            if not f_hash or f_hash not in active_hashes:
                # Special case: check if it's a legacy 12-char hash that matches an active prefix
                # (Optional: for now we are strict to enforce the new 32-char contract)
                print(f"[-] Removing orphaned/legacy cache: {f.name}")
                f.unlink()
                removed += 1
        print(f"[*] Cleaned {folder}: removed {removed} files.")

    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print(f"Active unique clips: {len(active_hashes)}")
    print("=" * 60)

if __name__ == "__main__":
    clean()
