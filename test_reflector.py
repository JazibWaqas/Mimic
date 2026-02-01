import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from engine.reflector import reflect_on_edit
from models import PipelineResult

def run_reflection_on_existing_results():
    # Fix Windows console encoding
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except: pass

    results_dir = Path("data/results")
    output_dir = Path("data/results")
    
    # Find all master JSON files
    json_files = list(results_dir.glob("*.json"))
    
    print(f"🚀 FOUND {len(json_files)} EXISTING RESULTS TO REFLECT ON\n")
    
    for jf in json_files:
        if "DirectorAnalysis" in jf.name:
            continue
            
        print(f"🎬 PROCESSING: {jf.name}")
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result = PipelineResult(**data)
            
            if not result.blueprint or not result.edl:
                print(f"  ⚠️ Skipping {jf.name}: Missing blueprint or EDL data.")
                continue
                
            # Check if we should skip (already has a valid critique)
            if hasattr(result, 'critique') and result.critique and result.critique.overall_score != 5.0:
                print(f"  ⏭️ Skipping {jf.name}: Already has valid critique.")
                continue
                
            # Run Reflector
            import time
            time.sleep(2) # Small delay to avoid rate limits
            critique = reflect_on_edit(
                result.blueprint, 
                result.edl, 
                result.clip_index, 
                advisor=result.advisor,
                force_refresh=True # Force refresh to overwrite fallback
            )
            
            # Update the result object
            result.critique = critique
            
            # 1. Update the master JSON
            with open(jf, "w", encoding="utf-8") as f:
                f.write(result.model_dump_json(indent=2))
            
            # 2. Generate the clean TXT report
            txt_name = f"DirectorAnalysis_{jf.stem}.txt"
            txt_path = output_dir / txt_name
            
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write(f"DIRECTOR'S CRITIQUE: {jf.stem.upper()}\n")
                f.write("="*80 + "\n\n")
                f.write(f"OVERALL SCORE: {critique.overall_score}/10\n\n")
                f.write("DIRECTOR'S MONOLOGUE:\n")
                f.write(f"\"{critique.monologue}\"\n\n")
                f.write("STAR PERFORMERS:\n")
                for s in critique.star_performers:
                    f.write(f"  ⭐ {s}\n")
                f.write("\nDEAD WEIGHT (NECESSARY COMPROMISES):\n")
                for s in critique.dead_weight:
                    f.write(f"  ⚠️ {s}\n")
                f.write("\nREMAKE CHECKLIST (MISSING INGREDIENTS):\n")
                for item in critique.missing_ingredients:
                    f.write(f"  📋 {item}\n")
                f.write("\nTECHNICAL FIDELITY:\n")
                f.write(f"  🔧 {critique.technical_fidelity}\n\n")
                f.write("="*80 + "\n")
            
            print(f"  ✅ SUCCESS: Generated {txt_name}")
            
        except Exception as e:
            print(f"  ❌ FAILED {jf.name}: {e}")

if __name__ == "__main__":
    run_reflection_on_existing_results()
