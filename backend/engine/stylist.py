"""
Stylist: Applies visual aesthetics and text overlays to videos.
This module translates StyleBlueprints into FFmpeg filter chains.
"""

from pathlib import Path
import subprocess
from typing import Dict, Any, List

def apply_visual_styling(
    input_video: str,
    output_video: str,
    text_overlay: str,
    text_style: Dict[str, Any],
    color_grading: Dict[str, Any] = None
) -> None:
    """
    Apply visual styling and text overlay to a video using FFmpeg.
    """
    
    # If no text overlay, just copy and return
    if not text_overlay:
        import shutil
        shutil.copy2(input_video, output_video)
        return

    # 1. Map Font Selection (Keyword based)
    font_style_raw = text_style.get("font_style", "serif").lower()
    font_name = "Arial" # Default
    
    if "serif" in font_style_raw:
        font_name = "Georgia"
    elif "mono" in font_style_raw:
        font_name = "Courier New"
    elif "handwritten" in font_style_raw or "script" in font_style_raw:
        font_name = "Lucida Handwriting"
    elif "bold" in font_style_raw:
        font_name = "Arial Black"
    
    # 2. Color Mapping - High-End Minimalist
    # Defaulting to White for that premium look unless gold is specifically requested
    font_color = "white"
    color_effects = text_style.get("color_effects", "").lower()
    if "gold" in color_effects or "yellow" in color_effects:
        font_color = "0xEEEEEE" # Soft Off-White (looks better than pure yellow)

    # 3. Text Processing (Multi-line Support with Auto-Wrapping)
    import textwrap
    
    # First, handle explicit breaks (pipe or newline)
    raw_lines = text_overlay.replace("|", "\n").split("\n")
    
    # Then, auto-wrap long lines to fit typical 9:16 width (approx 35 chars)
    # This prevents the horizontol overflow seen in long phrases.
    wrapped_lines = []
    for line in raw_lines:
        if len(line.strip()) > 35:
            # Wrap to 35 characters
            wrapped_lines.extend(textwrap.wrap(line.strip(), width=35))
        else:
            if line.strip():
                wrapped_lines.append(line.strip())
    
    lines = wrapped_lines
    
    # 4. Build Filter Chain
    filters = []
    
    # A. Color Grading
    if color_grading:
        tone = color_grading.get("tone", "").lower()
        contrast = color_grading.get("contrast", "").lower()
        if "warm" in tone:
            filters.append("colorbalance=rh=0.08:gh=0.04:bh=-0.04")
        elif "cool" in tone:
            filters.append("colorbalance=rh=-0.04:gh=0.04:bh=0.08")
        if "high" in contrast:
            filters.append("eq=contrast=1.15:saturation=1.1")

    # B. Multi-line DrawText (Manual stacking for perfect alignment)
    placement = text_style.get("placement", "top").lower()
    font_size = 42 # Smaller is more premium
    line_height = font_size * 1.5
    
    # Determine base Y position
    if "top" in placement:
        base_y = "h/5"
    elif "bottom" in placement:
        base_y = f"h*0.8 - ({len(lines)} * {line_height}/2)"
    else:
        base_y = f"(h - ({len(lines)} * {line_height}))/2"

    for i, line in enumerate(lines):
        clean_l = line.replace("'", "").replace(":", "") # Filter out problematic chars
        y_offset = i * line_height
        
        drawtext = (
            f"drawtext=font='{font_name}':text='{clean_l}':"
            f"x=(w-text_w)/2:y={base_y}+{y_offset}:"
            f"fontsize={font_size}:fontcolor={font_color}:"
            f"shadowcolor=black@0.4:shadowx=2:shadowy=2"
        )
        filters.append(drawtext)
    
    filter_chain = ",".join(filters)
    
    # 5. FFmpeg Execution
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", filter_chain,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-c:a", "copy",
        output_video
    ]
    
    print(f"  [STYLIST] Applying Clean Aesthetic: {len(lines)} lines, Font: {font_name}")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  [OK] Stylized video ready: {Path(output_video).name}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Stylist Error: {e.stderr.decode(errors='ignore')}")
        import shutil
        shutil.copy2(input_video, output_video)
