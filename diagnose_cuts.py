"""
Scene Detection Diagnostic Tool
Compares FFmpeg raw detection vs. MIMIC's filtered detection
"""

import subprocess
import re
import sys
from pathlib import Path

def detect_raw_cuts(video_path: str, threshold: float = 0.15):
    """Raw FFmpeg scene detection without filtering."""
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-filter:v", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null",
        "-"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stderr
    
    timestamps = []
    matches = re.findall(r"pts_time:([\d\.]+)", output)
    for m in matches:
        ts = float(m)
        if ts >= 0.1:
            timestamps.append(ts)
    
    return sorted(set(timestamps))

def detect_filtered_cuts(timestamps, min_gap=0.15):
    """Apply MIMIC's gap filtering."""
    if not timestamps:
        return []
    
    filtered = [timestamps[0]]
    for i in range(1, len(timestamps)):
        if timestamps[i] - filtered[-1] > min_gap:
            filtered.append(timestamps[i])
    
    return filtered

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_cuts.py <video_path> [threshold] [min_gap]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
    min_gap = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
    
    print(f"\n{'='*80}")
    print(f"CUT DETECTION DIAGNOSTIC")
    print(f"{'='*80}")
    print(f"Video: {Path(video_path).name}")
    print(f"Scene Threshold: {threshold}")
    print(f"Minimum Gap: {min_gap}s")
    print(f"{'='*80}\n")
    
    # Raw detection
    raw_cuts = detect_raw_cuts(video_path, threshold)
    print(f"[RAW] FFmpeg detected {len(raw_cuts)} cuts:")
    for i, ts in enumerate(raw_cuts, 1):
        print(f"  {i:2d}. {ts:.3f}s")
    
    # Filtered detection
    filtered_cuts = detect_filtered_cuts(raw_cuts, min_gap)
    print(f"\n[FILTERED] After {min_gap}s gap filter: {len(filtered_cuts)} cuts:")
    for i, ts in enumerate(filtered_cuts, 1):
        print(f"  {i:2d}. {ts:.3f}s")
    
    # Show what was removed
    removed = set(raw_cuts) - set(filtered_cuts)
    if removed:
        print(f"\n[REMOVED] {len(removed)} cuts filtered out:")
        for ts in sorted(removed):
            print(f"  - {ts:.3f}s")
    
    # Calculate average cut duration
    if len(filtered_cuts) > 1:
        gaps = [filtered_cuts[i] - filtered_cuts[i-1] for i in range(1, len(filtered_cuts))]
        avg_gap = sum(gaps) / len(gaps)
        min_gap_actual = min(gaps)
        max_gap_actual = max(gaps)
        
        print(f"\n[STATS]")
        print(f"  Average cut duration: {avg_gap:.3f}s")
        print(f"  Shortest cut: {min_gap_actual:.3f}s")
        print(f"  Longest cut: {max_gap_actual:.3f}s")
        print(f"  Cuts per second: {len(filtered_cuts) / filtered_cuts[-1]:.2f}")
    
    print(f"\n{'='*80}\n")
