"""
Comprehensive Test Suite: Can Gemini Replace Matching Algorithm?

Tests:
1. ref3 (worst case - abstract vibes)
2. ref4 consistency (re-run same reference)
3. ref9 (edge case - 2 segments only)
4. Timing and token measurement
5. Actual rendering test (ref4)
"""

import json
import os
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import google.generativeai as genai

PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
CLIPS_DIR = PROJECT_ROOT / "data" / "samples" / "clips"
REFERENCE_DIR = PROJECT_ROOT / "data" / "samples" / "reference"

def get_reference_hash(reference_path: Path) -> str:
    """Get hash for reference video."""
    with open(reference_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:12]

def find_reference_cache(reference_path: Path) -> Optional[Path]:
    """Find cache file for reference."""
    ref_hash = get_reference_hash(reference_path)
    
    for cache_file in CACHE_DIR.glob(f"ref_{ref_hash}_*.json"):
        if "hints" in cache_file.name:
            return cache_file
    
    return None

def load_reference_analysis(reference_path: Path) -> Optional[Dict[str, Any]]:
    """Load reference analysis from cache."""
    cache_file = find_reference_cache(reference_path)
    if cache_file and cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None

def get_clip_filename_from_hash(clip_hash: str) -> str | None:
    """Map clip cache hash to actual filename."""
    for clip_file in CLIPS_DIR.glob("*.mp4"):
        try:
            with open(clip_file, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:12]
            if file_hash == clip_hash:
                return clip_file.name
        except Exception:
            continue
    return None

def load_all_clip_analyses_with_filenames() -> List[Dict[str, Any]]:
    """Load all clip analyses and map to filenames."""
    clip_files = list(CACHE_DIR.glob("clip_comprehensive_*.json"))
    clips = []
    
    for clip_file in clip_files:
        with open(clip_file) as f:
            clip_data = json.load(f)
        
        clip_hash = clip_file.stem.replace("clip_comprehensive_", "")
        filename = get_clip_filename_from_hash(clip_hash)
        
        if filename:
            clip_data["filename"] = filename
            clips.append(clip_data)
    
    return clips

def build_simple_prompt(reference: Dict[str, Any], clips: List[Dict[str, Any]]) -> str:
    """Build the mega-prompt asking Gemini for decisions."""
    
    segments_text = []
    for seg in reference["segments"]:
        segments_text.append(
            f"Segment {seg['id']}: {seg['start']:.2f}s-{seg['end']:.2f}s ({seg['duration']:.2f}s) | "
            f"Energy: {seg['energy']} | Motion: {seg['motion']} | Vibe: {seg['vibe']} | "
            f"Arc: {seg['arc_stage']}"
        )
    
    clips_text = []
    for clip in clips:
        filename = clip.get("filename", "unknown")
        clips_text.append(
            f"{filename}: Energy={clip['energy']}, Motion={clip['motion']}, "
            f"Vibes=[{', '.join(clip.get('vibes', []))}], "
            f"Content=\"{clip.get('content_description', 'N/A')[:100]}\""
        )
    
    prompt = f"""You are a professional video editor. Design the complete edit.

REFERENCE VIDEO STRUCTURE:
Total Duration: {reference['total_duration']:.2f} seconds
Editing Style: {reference['editing_style']}
Emotional Intent: {reference['emotional_intent']}

SEGMENTS ({len(reference['segments'])} total):
{chr(10).join(segments_text)}

AVAILABLE CLIPS ({len(clips)} total):
{chr(10).join(clips_text)}

YOUR TASK:
For each segment, choose the best clip. Maximize vibe matching and diversity.

CONSTRAINTS:
- Use each clip maximum once (aim for diversity)
- Respect energy compatibility (High segment → High/Medium clip, Medium → Medium/High/Low, Low → Low/Medium)
- Maximize vibe match between segment vibe and clip vibes
- Provide brief reasoning for each choice

OUTPUT FORMAT (JSON array only):
[
  {{"segment_id": 1, "clip": "clip28.mp4", "reasoning": "Matches Nature vibe and Medium energy"}},
  {{"segment_id": 2, "clip": "clip12.mp4", "reasoning": "Travel vibe aligns with segment"}},
  ...
]

Respond ONLY with valid JSON array."""
    
    return prompt

def initialize_gemini() -> genai.GenerativeModel:
    """Initialize Gemini model."""
    from utils.api_key_manager import get_api_key
    api_key = get_api_key()
    if not api_key:
        raise ValueError("No API key available")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(
        "gemini-3-flash-preview",
        generation_config={
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 16384
        },
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    )
    return model

def extract_json_array(text: str) -> List[Dict[str, Any]] | None:
    """Extract JSON array from response."""
    import re
    
    json_match = re.search(r'```(?:json)?\s*(\[.*?\])', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    json_match = re.search(r'(\[.*\])', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None

def analyze_gemini_decisions(decisions: List[Dict[str, Any]], reference: Dict[str, Any], clips: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze Gemini's decisions."""
    clip_map = {c["filename"]: c for c in clips}
    
    vibe_matches = 0
    energy_matches = 0
    energy_compatible = 0
    total_segments = len(reference["segments"])
    
    clip_usage = {}
    vibe_match_details = []
    
    for dec in decisions:
        segment_id = dec.get("segment_id")
        clip_name = dec.get("clip")
        
        if not segment_id or not clip_name:
            continue
        
        clip_usage[clip_name] = clip_usage.get(clip_name, 0) + 1
        
        if segment_id <= len(reference["segments"]):
            seg = reference["segments"][segment_id - 1]
            clip_data = clip_map.get(clip_name)
            
            if clip_data:
                vibe_match = seg["vibe"] in clip_data.get("vibes", [])
                if vibe_match:
                    vibe_matches += 1
                vibe_match_details.append({
                    "segment_id": segment_id,
                    "segment_vibe": seg["vibe"],
                    "clip_vibes": clip_data.get("vibes", []),
                    "matched": vibe_match
                })
                
                if seg["energy"] == clip_data["energy"]:
                    energy_matches += 1
                
                seg_energy = seg["energy"]
                clip_energy = clip_data["energy"]
                
                if seg_energy == "High" and clip_energy in ["High", "Medium"]:
                    energy_compatible += 1
                elif seg_energy == "Medium" and clip_energy in ["High", "Medium", "Low"]:
                    energy_compatible += 1
                elif seg_energy == "Low" and clip_energy in ["Low", "Medium"]:
                    energy_compatible += 1
    
    return {
        "total_decisions": len(decisions),
        "unique_clips_used": len(clip_usage),
        "vibe_match_percent": (vibe_matches / total_segments * 100) if total_segments > 0 else 0,
        "energy_match_percent": (energy_matches / total_segments * 100) if total_segments > 0 else 0,
        "energy_compatible_percent": (energy_compatible / total_segments * 100) if total_segments > 0 else 0,
        "clip_usage": clip_usage,
        "max_clip_reuse": max(clip_usage.values()) if clip_usage else 0,
        "vibe_match_details": vibe_match_details
    }

def test_reference(reference_name: str, model: genai.GenerativeModel, clips: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Test a single reference."""
    print(f"\n{'='*80}")
    print(f"TESTING: {reference_name}")
    print(f"{'='*80}")
    
    reference_path = REFERENCE_DIR / reference_name
    if not reference_path.exists():
        return {"error": f"Reference file not found: {reference_name}"}
    
    reference = load_reference_analysis(reference_path)
    if not reference:
        return {"error": f"No cache found for {reference_name}"}
    
    print(f"Reference: {reference_name}")
    print(f"Segments: {len(reference['segments'])}")
    print(f"Duration: {reference['total_duration']:.2f}s")
    print(f"Style: {reference['editing_style']}")
    
    prompt = build_simple_prompt(reference, clips)
    prompt_length = len(prompt)
    estimated_tokens = prompt_length // 4
    
    print(f"Prompt size: {prompt_length:,} chars (~{estimated_tokens:,} tokens)")
    
    start_time = time.time()
    try:
        response = model.generate_content(prompt)
        elapsed = time.time() - start_time
        gemini_output = response.text
        
        decisions = extract_json_array(gemini_output)
        
        if decisions:
            analysis = analyze_gemini_decisions(decisions, reference, clips)
            analysis["response_time"] = elapsed
            analysis["prompt_tokens_estimated"] = estimated_tokens
            analysis["decisions"] = decisions
            analysis["raw_response"] = gemini_output
            
            print(f"[OK] Response time: {elapsed:.1f}s")
            print(f"[OK] Decisions: {analysis['total_decisions']}/{len(reference['segments'])}")
            print(f"[OK] Unique clips: {analysis['unique_clips_used']}")
            print(f"[OK] Vibe match: {analysis['vibe_match_percent']:.1f}%")
            print(f"[OK] Energy match: {analysis['energy_match_percent']:.1f}%")
            
            return analysis
        else:
            return {"error": "Could not extract JSON from response", "raw_response": gemini_output}
    
    except Exception as e:
        return {"error": str(e), "response_time": time.time() - start_time}

def compare_decisions(decisions1: List[Dict[str, Any]], decisions2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare two sets of decisions for consistency."""
    if len(decisions1) != len(decisions2):
        return {"match_percent": 0, "total": len(decisions1), "matched": 0}
    
    matches = 0
    for d1, d2 in zip(decisions1, decisions2):
        if d1.get("segment_id") == d2.get("segment_id") and d1.get("clip") == d2.get("clip"):
            matches += 1
    
    return {
        "match_percent": (matches / len(decisions1) * 100) if decisions1 else 0,
        "total": len(decisions1),
        "matched": matches
    }

def main():
    import sys
    
    print("="*80)
    print("COMPREHENSIVE GEMINI EDITOR TEST SUITE")
    print("="*80)
    
    print("\n1. Loading clip analyses...")
    clips = load_all_clip_analyses_with_filenames()
    print(f"   [OK] Loaded {len(clips)} clips")
    
    print("\n2. Initializing Gemini...")
    model = initialize_gemini()
    
    results = {}
    
    print("\n3. Running tests...")
    print("   (Each test takes ~3 minutes)")
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        print(f"\nRunning single test: {test_name}")
        if test_name == "ref4_consistency":
            test_ref4_1 = test_reference("ref4.mp4", model, clips)
            if "error" not in test_ref4_1:
                results["ref4_run1"] = test_ref4_1
            test_ref4_2 = test_reference("ref4.mp4", model, clips)
            if "error" not in test_ref4_2:
                results["ref4_run2"] = test_ref4_2
                if "decisions" in test_ref4_1 and "decisions" in test_ref4_2:
                    consistency = compare_decisions(test_ref4_1["decisions"], test_ref4_2["decisions"])
                    results["ref4_consistency"] = consistency
                    print(f"\n[CONSISTENCY] ref4: {consistency['match_percent']:.1f}% match ({consistency['matched']}/{consistency['total']})")
        elif test_name.startswith("ref"):
            result = test_reference(f"{test_name}.mp4", model, clips)
            if "error" not in result:
                results[test_name] = result
        else:
            print(f"Unknown test: {test_name}")
            return
    else:
        print("\nRunning all tests (this will take ~12 minutes)...")
        print("   Tip: Run individual tests with: python test_gemini_comprehensive.py ref4")
        
        test_ref4_1 = test_reference("ref4.mp4", model, clips)
        if "error" not in test_ref4_1:
            results["ref4_run1"] = test_ref4_1
        
        test_ref4_2 = test_reference("ref4.mp4", model, clips)
        if "error" not in test_ref4_2:
            results["ref4_run2"] = test_ref4_2
            if "decisions" in test_ref4_1 and "decisions" in test_ref4_2:
                consistency = compare_decisions(test_ref4_1["decisions"], test_ref4_2["decisions"])
                results["ref4_consistency"] = consistency
                print(f"\n[CONSISTENCY] ref4: {consistency['match_percent']:.1f}% match ({consistency['matched']}/{consistency['total']})")
        
        test_ref3 = test_reference("ref3.mp4", model, clips)
        if "error" not in test_ref3:
            results["ref3"] = test_ref3
        
        test_ref9 = test_reference("ref9.mp4", model, clips)
        if "error" not in test_ref9:
            results["ref9"] = test_ref9
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        if "error" in result:
            print(f"{test_name}: ERROR - {result['error']}")
        else:
            print(f"{test_name}:")
            print(f"  Decisions: {result['total_decisions']}")
            print(f"  Unique clips: {result['unique_clips_used']}")
            print(f"  Vibe match: {result['vibe_match_percent']:.1f}%")
            print(f"  Response time: {result.get('response_time', 0):.1f}s")
    
    output_file = PROJECT_ROOT / "backend" / "test_gemini_comprehensive_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Full results saved to: {output_file}")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review results in test_gemini_comprehensive_results.json")
    print("2. Check consistency: ref4_run1 vs ref4_run2")
    print("3. Compare ref3 (abstract vibes) vs current algorithm")
    print("4. Verify ref9 (edge case) handles correctly")
    print("5. If all pass, proceed with rendering test")

if __name__ == "__main__":
    main()
