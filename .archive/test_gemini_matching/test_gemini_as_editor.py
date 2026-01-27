"""
Test: Can Gemini replace the matching algorithm?

This script tests if Gemini 3 can design the entire edit by seeing:
- Reference structure (all segments with vibes/energy)
- All clip metadata (energy/vibes/best_moments)

We compare Gemini's output to the current deterministic algorithm.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
REFERENCE_CACHE = CACHE_DIR / "ref_5782cea3a492_hda4304ec.json"

def load_reference_analysis() -> Dict[str, Any]:
    """Load ref4 reference analysis."""
    with open(REFERENCE_CACHE) as f:
        return json.load(f)

def load_all_clip_analyses() -> List[Dict[str, Any]]:
    """Load all clip comprehensive analyses from cache."""
    clip_files = list(CACHE_DIR.glob("clip_comprehensive_*.json"))
    clips = []
    for clip_file in clip_files:
        with open(clip_file) as f:
            clip_data = json.load(f)
            clip_data["_filename"] = clip_file.stem.replace("clip_comprehensive_", "")
            clips.append(clip_data)
    return clips

def build_mega_prompt(reference: Dict[str, Any], clips: List[Dict[str, Any]]) -> str:
    """Build the mega-prompt asking Gemini to design the edit."""
    
    segments_text = []
    for seg in reference["segments"]:
        segments_text.append(
            f"Segment {seg['id']}: {seg['start']:.2f}s-{seg['end']:.2f}s ({seg['duration']:.2f}s) | "
            f"Energy: {seg['energy']} | Motion: {seg['motion']} | Vibe: {seg['vibe']} | "
            f"Arc: {seg['arc_stage']} | Reasoning: {seg.get('reasoning', 'N/A')}"
        )
    
    clips_text = []
    for i, clip in enumerate(clips, 1):
        clip_id = clip["_filename"]
        clips_text.append(
            f"Clip {i} (ID: {clip_id}):\n"
            f"  Energy: {clip['energy']} | Motion: {clip['motion']}\n"
            f"  Vibes: {', '.join(clip.get('vibes', []))}\n"
            f"  Content: {clip.get('content_description', 'N/A')}\n"
            f"  Best Moments:\n"
            f"    High: {clip['best_moments']['High']['start']:.1f}s-{clip['best_moments']['High']['end']:.1f}s ({clip['best_moments']['High']['reason']})\n"
            f"    Medium: {clip['best_moments']['Medium']['start']:.1f}s-{clip['best_moments']['Medium']['end']:.1f}s ({clip['best_moments']['Medium']['reason']})\n"
            f"    Low: {clip['best_moments']['Low']['start']:.1f}s-{clip['best_moments']['Low']['end']:.1f}s ({clip['best_moments']['Low']['reason']})"
        )
    
    prompt = f"""You are a professional video editor designing a complete edit.

REFERENCE VIDEO STRUCTURE:
Total Duration: {reference['total_duration']:.2f} seconds
Editing Style: {reference['editing_style']}
Emotional Intent: {reference['emotional_intent']}
Arc Description: {reference['arc_description']}

SEGMENTS ({len(reference['segments'])} total):
{chr(10).join(segments_text)}

AVAILABLE CLIPS ({len(clips)} total):
{chr(10).join(clips_text)}

YOUR TASK:
Design the complete edit by choosing which clip (and which moment within that clip) to use for each segment.

CONSTRAINTS:
1. Each segment must be filled completely (match the segment duration)
2. Prefer using clips' "best moments" for the matching energy level
3. Maximize vibe match between segment vibe and clip vibes
4. Ensure diversity - don't use the same clip repeatedly
5. Maintain smooth flow - avoid jarring transitions
6. Respect energy matching (High segment → High/Medium clip, Medium → Medium/High/Low, Low → Low/Medium)

OUTPUT FORMAT (JSON only):
{{
  "editing_decisions": [
    {{
      "segment_id": 1,
      "clip_id": "02c224a130e3",
      "clip_start": 5.0,
      "clip_end": 7.5,
      "reasoning": "Why this clip/moment for this segment"
    }}
  ],
  "overall_strategy": "Your high-level editing strategy",
  "diversity_notes": "How you ensured clip diversity",
  "compromises": "Any compromises made (e.g., energy mismatch, vibe mismatch)"
}}

Respond ONLY with valid JSON."""
    
    return prompt

def initialize_gemini(api_key: str | None = None) -> genai.GenerativeModel:
    """Initialize Gemini model."""
    if api_key:
        genai.configure(api_key=api_key)
    else:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
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

def extract_json_from_response(text: str) -> Dict[str, Any] | None:
    """Try to extract JSON from Gemini's response (may have markdown code blocks)."""
    import re
    
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    json_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None

def test_gemini_matching():
    """Run the test."""
    print("="*80)
    print("TEST: Can Gemini Replace Matching Algorithm?")
    print("="*80)
    print()
    
    print("1. Loading reference analysis...")
    reference = load_reference_analysis()
    print(f"   ✓ Loaded {len(reference['segments'])} segments")
    print(f"   ✓ Total duration: {reference['total_duration']:.2f}s")
    
    print("2. Loading clip analyses...")
    clips = load_all_clip_analyses()
    print(f"   ✓ Loaded {len(clips)} clips")
    
    energy_dist = {"High": 0, "Medium": 0, "Low": 0}
    for clip in clips:
        energy_dist[clip["energy"]] += 1
    print(f"   ✓ Energy distribution: High={energy_dist['High']}, Medium={energy_dist['Medium']}, Low={energy_dist['Low']}")
    
    print("3. Building mega-prompt...")
    prompt = build_mega_prompt(reference, clips)
    prompt_length = len(prompt)
    estimated_tokens = prompt_length // 4
    print(f"   ✓ Prompt length: {prompt_length:,} characters (~{estimated_tokens:,} tokens estimated)")
    
    if estimated_tokens > 1000000:
        print(f"   ⚠ WARNING: Prompt exceeds 1M tokens - may hit context limits")
    
    print("4. Initializing Gemini...")
    model = initialize_gemini()
    
    print("5. Calling Gemini to design edit...")
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
        print(gemini_output[:2000])  # Show first 2000 chars
        if len(gemini_output) > 2000:
            print(f"\n... ({len(gemini_output) - 2000} more characters)")
        print()
        
        output_file = PROJECT_ROOT / "backend" / "test_gemini_matching" / f"gemini_edit_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        gemini_json = extract_json_from_response(gemini_output)
        
        if gemini_json:
            with open(output_file, 'w') as f:
                json.dump({
                    "test_metadata": {
                        "reference_file": "ref4.mp4",
                        "reference_hash": "5782cea3a492",
                        "num_segments": len(reference['segments']),
                        "num_clips": len(clips),
                        "prompt_tokens_estimated": estimated_tokens,
                        "response_time_seconds": elapsed,
                        "timestamp": datetime.now().isoformat()
                    },
                    "reference": reference,
                    "clips": clips,
                    "gemini_design": gemini_json,
                    "raw_prompt": prompt,
                    "raw_response": gemini_output
                }, f, indent=2)
            print(f"✓ Saved full output to: {output_file}")
            print()
            print("="*80)
            print("ANALYSIS:")
            print("="*80)
            
            if "editing_decisions" in gemini_json:
                decisions = gemini_json["editing_decisions"]
                print(f"✓ Gemini provided {len(decisions)} editing decisions")
                
                if len(decisions) == len(reference['segments']):
                    print("✓ All segments matched!")
                else:
                    print(f"⚠ Only {len(decisions)}/{len(reference['segments'])} segments matched")
                
                clip_usage = {}
                for dec in decisions:
                    clip_id = dec.get("clip_id", "unknown")
                    clip_usage[clip_id] = clip_usage.get(clip_id, 0) + 1
                
                print(f"✓ Used {len(clip_usage)} unique clips")
                print(f"✓ Most used clip: {max(clip_usage.items(), key=lambda x: x[1])}")
                
                if "overall_strategy" in gemini_json:
                    print(f"\nStrategy: {gemini_json['overall_strategy'][:200]}...")
                
                if "compromises" in gemini_json:
                    print(f"\nCompromises: {gemini_json['compromises'][:200]}...")
            else:
                print("⚠ Gemini output doesn't contain 'editing_decisions' field")
        else:
            print("⚠ WARNING: Could not extract JSON from Gemini response")
            print("Saving raw text instead...")
            with open(output_file.with_suffix('.txt'), 'w') as f:
                f.write(gemini_output)
            print(f"✓ Saved raw output to: {output_file.with_suffix('.txt')}")
        
        print()
        print("="*80)
        print("NEXT STEPS:")
        print("="*80)
        print("1. Review Gemini's edit design in the saved JSON file")
        print("2. Compare with current algorithm output (from ref4_xray_output.txt)")
        print("3. Evaluate:")
        print("   - Does Gemini show better reasoning?")
        print("   - Better vibe matches?")
        print("   - Better diversity?")
        print("   - More coherent overall strategy?")
        print("4. If yes → Consider pivoting to 'Gemini as editor' approach")
        print("5. If no → Current hybrid approach is optimal")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_matching()
