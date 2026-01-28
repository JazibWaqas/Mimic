import os
import sys
from pathlib import Path

# Add the backend directory to sys.path to allow importing from engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from backend.engine.orchestrator import run_mimic_pipeline
from backend.models import PipelineResult

def test_reference(ref_name: str, session_suffix: str = "diverse_test"):
    # 1. Setup paths
    BASE_DIR = Path(__file__).resolve().parent
    ref_path = str(BASE_DIR / "data" / "samples" / "reference" / ref_name)
    clips_dir = BASE_DIR / "data" / "samples" / "clips"
    output_dir = str(BASE_DIR / "data" / "results")
    
    # Get all mp4 clips in the clips directory
    clip_paths = [str(p) for p in clips_dir.glob("*.mp4")]
    
    print("=" * 80)
    print(f"TESTING {ref_name.upper()} WITH HYBRID DETECTION")
    print("=" * 80)
    print(f"\n📹 Reference: {ref_name}")
    print(f"📎 Testing with {len(clip_paths)} clips")
    
    # 2. Run Pipeline
    session_id = f"{ref_name.split('.')[0]}_{session_suffix}"
    
    result: PipelineResult = run_mimic_pipeline(
        reference_path=ref_path,
        clip_paths=clip_paths,
        session_id=session_id,
        output_dir=output_dir
    )
    
    if result.success:
        print("=" * 80)
        print(f"🎉 Watch the result: {result.output_path}")
        print("=" * 80)
    else:
        print(f"❌ Pipeline failed: {result.error}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ref_to_test = sys.argv[1]
    else:
        ref_to_test = "ref3.mp4"
    
    test_reference(ref_to_test, session_suffix="final_hybrid_eval")
