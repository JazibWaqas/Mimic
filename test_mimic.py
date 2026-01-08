
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path so we can import the engine
sys.path.append(str(Path.cwd() / "backend"))

from engine.orchestrator import run_mimic_pipeline
from utils import ensure_directory

def run_test():
    """
    Runs an end-to-end test using the organized 'data/samples' folder.
    """
    load_dotenv(dotenv_path="backend/.env")
    
    # 1. Setup Paths
    base_dir = Path.cwd()
    ref_path = base_dir / "data" / "samples" / "reference" / "refrence_vid.mp4"
    clips_dir = base_dir / "data" / "samples" / "clips"
    output_dir = base_dir / "data" / "results"
    
    # 2. Collect Clips
    clip_paths = [str(p) for p in clips_dir.glob("*.mp4")]
    
    if not ref_path.exists():
        print(f"❌ Error: Reference video not found at {ref_path}")
        return

    if not clip_paths:
        print(f"❌ Error: No clips found in {clips_dir}")
        return

    # 3. Initialize Pipeline
    session_id = f"test-run-{int(time.time())}"
    ensure_directory(output_dir)
    
    print("\n" + "="*50)
    print("🎬 MIMIC - ORGANIZED TEST RUN")
    print("="*50)
    print(f"Blueprint: {ref_path.name}")
    print(f"Clip Count: {len(clip_paths)}")
    print(f"Session ID: {session_id}")
    print("="*50 + "\n")

    # 4. Run!
    result = run_mimic_pipeline(
        reference_path=str(ref_path),
        clip_paths=clip_paths,
        session_id=session_id,
        output_dir=str(output_dir)
    )

    if result.success:
        print("\n✨ SUCCESS! Final video created at:")
        print(f"👉 {result.output_path}")
    else:
        print(f"\n❌ FAILED: {result.error}")

if __name__ == "__main__":
    run_test()
