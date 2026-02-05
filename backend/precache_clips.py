"""
Pre-cache all clips in data/samples/clips/ for quota-free future tests.
This analyzes all clips once via Gemini API AND standardizes them for FFmpeg.
After this, everything is "Hot" and ready for instant rendering.
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# MIMIC Imports
from engine.brain import analyze_all_clips
from engine.processors import standardize_clip
from utils import get_file_hash, ensure_directory, save_hash_registry

load_dotenv()

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    clips_dir = data_dir / "samples" / "clips"
    cache_dir = data_dir / "cache"
    standardized_cache = cache_dir / "standardized"
    
    ensure_directory(standardized_cache)
    
    if not clips_dir.exists():
        print(f"ERROR: Clips directory not found: {clips_dir}")
        return
    
    clip_files = sorted(clips_dir.glob("*.mp4"))
    
    if not clip_files:
        print(f"ERROR: No MP4 files found in {clips_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"BULLETPROOF PRE-CACHING: {len(clip_files)} CLIPS")
    print(f"{'='*60}\n")
    print("Step 1: AI Analysis (Gemini 3)")
    print("Step 2: Video Standardization (High-Def Master)")
    print("\nAfter this, the system will be 'Offline-Ready' for these clips.\n")
    
    clip_paths = [str(f) for f in clip_files]
    
    # --- PHASE 1: AI ANALYSIS ---
    try:
        print(f"[PHASE 1] Starting Parallel AI Analysis...")
        clip_index = analyze_all_clips(clip_paths)
        print(f"\n[OK] AI Analysis complete for {len(clip_index.clips)} clips.")
    except Exception as e:
        print(f"\n[ERROR] Phase 1 failed: {e}")
        return

    # --- PHASE 2: STANDARDIZATION ---
    print(f"\n[PHASE 2] Starting Standardization & Persistent Caching...")
    
    def process_standardization(clip_path):
        p = Path(clip_path)
        h = get_file_hash(p)
        cached_path = standardized_cache / f"std_{h}.mp4"
        
        if cached_path.exists():
            print(f"  [SKIP] Already standardized: {p.name}")
            return True
        
        print(f"  [RUN] Standardizing: {p.name}...")
        try:
            # find energy for this clip (v12.5 Context-Aware)
            from models import EnergyLevel
            clip_energy = EnergyLevel.MEDIUM
            for cm in clip_index.clips:
                if cm.filename == p.name:
                    clip_energy = cm.energy  # Pass ENUM, not string
                    break
            
            # We standardize to a temp file first then move to cache to avoid partials
            temp_out = standardized_cache / f"tmp_{h}.mp4"
            standardize_clip(str(p), str(temp_out), energy=clip_energy)
            temp_out.rename(cached_path)
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to standardize {p.name}: {e}")
            return False

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_standardization, clip_paths))
    
    success_count = sum(1 for r in results if r)
    
    print(f"\n{'='*60}")
    print(f"FINAL STATUS")
    print(f"{'='*60}")
    print(f"AI Index: {len(clip_index.clips)} clips cached")
    print(f"Standardized: {success_count}/{len(clip_files)} files in persistent cache")
    print(f"{'='*60}\n")
    
    # Save the hash registry to ensure speed on next run
    save_hash_registry()
    print("System is now primed for maximum performance.")

if __name__ == "__main__":
    main()
