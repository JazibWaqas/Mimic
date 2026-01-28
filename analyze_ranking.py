import json
import os
from pathlib import Path

def analyze_results():
    results_dir = Path("data/results")
    jsons = list(results_dir.glob("*_master.json"))
    
    rank_data = []
    
    for j_path in jsons:
        with open(j_path, "r") as f:
            data = json.load(f)
        
        ref_name = j_path.name.replace("_ref", "").replace("_master.json", "")
        
        # 1. Total Segments
        blueprint = data.get("blueprint", {})
        segments = blueprint.get("segments", [])
        total_segments = len(segments)
        
        # 2. Vibe Match Score
        edl = data.get("edl", {})
        decisions = edl.get("decisions", [])
        vibe_matches = sum(1 for d in decisions if d.get("vibe_match"))
        vibe_score = (vibe_matches / len(decisions)) * 100 if decisions else 0
        
        # 3. Energy Compromises & Diversity
        clips_used = set()
        compromises = 0
        
        # To check energy compromises, we need to link back to clip_index
        clip_index = {c["filename"]: c for c in data.get("clip_index", {}).get("clips", [])}
        
        for d in decisions:
            clip_name = Path(d["clip_path"]).name
            clips_used.add(clip_name)
            
            # Find the segment to check its requested energy
            seg_id = d["segment_id"]
            seg = next((s for s in segments if s["id"] == seg_id), None)
            clip_meta = clip_index.get(clip_name)
            
            if seg and clip_meta:
                if seg["energy"] != clip_meta["energy"]:
                    compromises += 1
        
        diversity = (len(clips_used) / total_segments) * 100 if total_segments else 0
        
        # 4. Pacing / Dynamicism
        avg_cut = sum(s["duration"] for s in segments) / total_segments if total_segments else 0
        
        # 5. Composite Score Calculation (Out of 10)
        # Weights: Vibe(40%), Efficiency(20%), Diversity(20%), Pacing(20%)
        # Note: Efficiency = (1 - compromises/total_decisions)
        efficiency = (1 - (compromises / len(decisions))) if decisions else 0
        
        # Pacing score: High density is usually better for reels. 
        # Aim for < 1.0s avg cut for a "10" pacing
        pacing_score = max(0, min(1.0, 1.0 / avg_cut)) if avg_cut > 0 else 0
        
        composite = (vibe_score * 0.04) + (efficiency * 2.0) + (diversity * 0.02) + (pacing_score * 2.0)
        
        rank_data.append({
            "ref": ref_name,
            "score": round(composite, 1),
            "vibe_match": round(vibe_score, 1),
            "compromises": compromises,
            "diversity": round(diversity, 1),
            "avg_cut": round(avg_cut, 2),
            "total_segments": total_segments
        })
    
    # Sort by score descending
    rank_data.sort(key=lambda x: x["score"], reverse=True)
    
    print(json.dumps(rank_data, indent=2))

if __name__ == "__main__":
    analyze_results()
