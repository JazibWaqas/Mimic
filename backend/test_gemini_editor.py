"""
Test: Can Gemini replace the matching algorithm?

Simple test: Give Gemini ref4 structure + all clips, ask for decisions.
Compare to current algorithm output.
"""

import json
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai

PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
CLIPS_DIR = PROJECT_ROOT / "data" / "samples" / "clips"
REFERENCE_CACHE = CACHE_DIR / "ref_5782cea3a492_hda4304ec.json"

def load_reference_analysis() -> Dict[str, Any]:
    """Load ref4 reference analysis."""
    with open(REFERENCE_CACHE) as f:
        return json.load(f)

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
        else:
            print(f"Warning: Could not find filename for hash {clip_hash}")
    
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
                if seg["vibe"] in clip_data.get("vibes", []):
                    vibe_matches += 1
                
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
        "max_clip_reuse": max(clip_usage.values()) if clip_usage else 0
    }

def main():
    print("="*80)
    print("TEST: Can Gemini Replace Matching Algorithm?")
    print("="*80)
    print()
    
    print("1. Loading reference analysis...")
    reference = load_reference_analysis()
    print(f"   [OK] Loaded {len(reference['segments'])} segments")
    print(f"   [OK] Total duration: {reference['total_duration']:.2f}s")
    
    print("2. Loading clip analyses and mapping to filenames...")
    clips = load_all_clip_analyses_with_filenames()
    print(f"   [OK] Loaded {len(clips)} clips with filenames")
    
    energy_dist = {"High": 0, "Medium": 0, "Low": 0}
    for clip in clips:
        energy_dist[clip["energy"]] += 1
    print(f"   [OK] Energy: High={energy_dist['High']}, Medium={energy_dist['Medium']}, Low={energy_dist['Low']}")
    
    print("3. Building prompt...")
    prompt = build_simple_prompt(reference, clips)
    prompt_length = len(prompt)
    estimated_tokens = prompt_length // 4
    print(f"   [OK] Prompt: {prompt_length:,} chars (~{estimated_tokens:,} tokens)")
    
    print("4. Initializing Gemini...")
    model = initialize_gemini()
    
    print("5. Calling Gemini...")
    print("   (This may take 30-60 seconds)")
    print()
    
    try:
        import time
        start_time = time.time()
        response = model.generate_content(prompt)
        elapsed = time.time() - start_time
        
        gemini_output = response.text
        
        print("="*80)
        print(f"GEMINI RESPONSE (took {elapsed:.1f}s):")
        print("="*80)
        print(gemini_output[:1500])
        if len(gemini_output) > 1500:
            print(f"\n... ({len(gemini_output) - 1500} more characters)")
        print()
        
        decisions = extract_json_array(gemini_output)
        
        if decisions:
            print("="*80)
            print("ANALYSIS:")
            print("="*80)
            
            analysis = analyze_gemini_decisions(decisions, reference, clips)
            
            print(f"Decisions provided: {analysis['total_decisions']}/{len(reference['segments'])}")
            print(f"Unique clips used: {analysis['unique_clips_used']}")
            print(f"Max clip reuse: {analysis['max_clip_reuse']}")
            print(f"Vibe match: {analysis['vibe_match_percent']:.1f}%")
            print(f"Energy match: {analysis['energy_match_percent']:.1f}%")
            print(f"Energy compatible: {analysis['energy_compatible_percent']:.1f}%")
            print()
            
            print("Sample decisions:")
            for dec in decisions[:5]:
                print(f"  Segment {dec.get('segment_id')}: {dec.get('clip')} - {dec.get('reasoning', 'N/A')[:60]}")
            
            print()
            print("="*80)
            print("VERDICT:")
            print("="*80)
            print(f"[OK] Gemini provided {len(decisions)} decisions")
            print(f"[OK] Used {analysis['unique_clips_used']} unique clips")
            print(f"[OK] Vibe match: {analysis['vibe_match_percent']:.1f}%")
            print()
            print("Compare this to current algorithm output in ref4_xray_output.txt")
            print("Does Gemini show better reasoning? Better diversity?")
            
            output_file = PROJECT_ROOT / "backend" / "test_gemini_editor_output.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "decisions": decisions,
                    "analysis": analysis,
                    "raw_response": gemini_output,
                    "prompt": prompt
                }, f, indent=2)
            print(f"\n[OK] Saved full output to: {output_file}")
        else:
            print("[WARN] Could not extract JSON array from response")
            print("Raw response saved to test_gemini_editor_output.txt")
            with open(PROJECT_ROOT / "backend" / "test_gemini_editor_output.txt", 'w') as f:
                f.write(gemini_output)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
