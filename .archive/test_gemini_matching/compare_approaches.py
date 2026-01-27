"""
Compare Gemini's edit design vs current deterministic algorithm.

Usage:
    python compare_approaches.py <gemini_output.json> <xray_output.txt>
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import re

def parse_xray_output(xray_path: Path) -> Dict[str, Any]:
    """Parse xray output to extract matching decisions."""
    with open(xray_path) as f:
        content = f.read()
    
    decisions = []
    
    segment_pattern = r'Segment (\d+):.*?Clip: (.+?) \(.*?\)'
    matches = re.findall(segment_pattern, content, re.DOTALL)
    
    for seg_id, clip_name in matches:
        decisions.append({
            "segment_id": int(seg_id),
            "clip_name": clip_name.strip()
        })
    
    return {
        "decisions": decisions,
        "raw_content": content
    }

def load_gemini_output(gemini_path: Path) -> Dict[str, Any]:
    """Load Gemini's edit design JSON."""
    with open(gemini_path) as f:
        data = json.load(f)
    return data

def compare_approaches(gemini_data: Dict[str, Any], xray_data: Dict[str, Any]):
    """Compare the two approaches."""
    print("="*80)
    print("COMPARISON: Gemini vs Current Algorithm")
    print("="*80)
    print()
    
    gemini_decisions = gemini_data.get("gemini_design", {}).get("editing_decisions", [])
    xray_decisions = xray_data.get("decisions", [])
    
    print(f"Gemini decisions: {len(gemini_decisions)}")
    print(f"Current algorithm decisions: {len(xray_decisions)}")
    print()
    
    if not gemini_decisions:
        print("⚠ No Gemini decisions found in output")
        return
    
    if not xray_decisions:
        print("⚠ No current algorithm decisions found in xray output")
        return
    
    gemini_clips = set(d.get("clip_id", "") for d in gemini_decisions)
    xray_clips = set(d.get("clip_name", "") for d in xray_decisions)
    
    print("DIVERSITY:")
    print(f"  Gemini used {len(gemini_clips)} unique clips")
    print(f"  Current algorithm used {len(xray_clips)} unique clips")
    print()
    
    print("REASONING QUALITY:")
    gemini_strategy = gemini_data.get("gemini_design", {}).get("overall_strategy", "")
    if gemini_strategy:
        print(f"  Gemini strategy: {gemini_strategy[:300]}...")
    else:
        print("  Gemini: No strategy provided")
    print("  Current algorithm: Deterministic scoring (no explicit strategy)")
    print()
    
    print("COMPROMISES:")
    gemini_compromises = gemini_data.get("gemini_design", {}).get("compromises", "")
    if gemini_compromises:
        print(f"  Gemini: {gemini_compromises[:300]}...")
    else:
        print("  Gemini: No compromises documented")
    print("  Current algorithm: See xray output for compromise details")
    print()
    
    print("="*80)
    print("VERDICT:")
    print("="*80)
    print("Review the outputs above to determine:")
    print("1. Does Gemini show better semantic understanding?")
    print("2. Does Gemini provide more coherent overall strategy?")
    print("3. Does Gemini achieve better diversity?")
    print("4. Is Gemini's reasoning transparent and explainable?")
    print()
    print("If Gemini performs better → Consider 'Gemini as editor' approach")
    print("If current algorithm performs better → Keep hybrid approach")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_approaches.py <gemini_output.json> <xray_output.txt>")
        sys.exit(1)
    
    gemini_path = Path(sys.argv[1])
    xray_path = Path(sys.argv[2])
    
    if not gemini_path.exists():
        print(f"Error: {gemini_path} not found")
        sys.exit(1)
    
    if not xray_path.exists():
        print(f"Error: {xray_path} not found")
        sys.exit(1)
    
    gemini_data = load_gemini_output(gemini_path)
    xray_data = parse_xray_output(xray_path)
    
    compare_approaches(gemini_data, xray_data)
