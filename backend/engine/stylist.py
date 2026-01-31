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
        print(f"  [STYLIST] No text overlay requested. Skipping text rendering.")
        import shutil
        shutil.copy2(input_video, output_video)
        return

    # 1. Map Font Selection (Windows Path Resolution)
    font_style_raw = text_style.get("font_style", "serif").lower()
    
    # Map to standard Windows font filenames
    font_map = {
        "serif": "georgia.ttf",
        "sans-serif": "arial.ttf",
        "mono": "consola.ttf",
        "handwritten": "lhandw.ttf",
        "bold": "arialbd.ttf"
    }
    
    # Try to find the actual font file on Windows
    font_file = font_map.get(font_style_raw, "arial.ttf")
    font_path = Path("C:/Windows/Fonts") / font_file
    
    # Fallback if font isn't found (using string name as last resort)
    if font_path.exists():
        # BATTLE-TESTED WINDOWS FONT PATH FOR FFmpeg:
        # We need C\\:/Windows/Fonts/arial.ttf (double escape the colon)
        # And we DO NOT use quotes around the fontfile path in the filter string.
        active_font = str(font_path).replace("\\", "/").replace(":", "\\\\:")
    else:
        active_font = "Arial"
    
    # 2. Color Mapping - High-End Minimalist
    font_color = "white"
    color_effects = text_style.get("color_effects", "").lower()
    if "gold" in color_effects or "yellow" in color_effects:
        font_color = "0xEEEEEE" 

    # 3. Text Processing (Multi-line Support with Auto-Wrapping)
    import textwrap
    
    raw_lines = text_overlay.replace("|", "\n").split("\n")
    
    wrapped_lines = []
    for line in raw_lines:
        if len(line.strip()) > 35:
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
    font_size = 42
    line_height = font_size * 1.5
    
    if "top" in placement:
        base_y = "base_y=h/5"
    elif "bottom" in placement:
        base_y = f"base_y=h*0.8 - ({len(lines)} * {line_height}/2)"
    else:
        base_y = f"base_y=(h - ({len(lines)} * {line_height}))/2"

    for i, line in enumerate(lines):
        # ESCAPING FOR FFMPEG DRAWTEXT: ' : and \ need special handling
        # Also escaping > which caused issues in ref3
        clean_l = line.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:").replace(">", "\\>")
        
        y_offset = f"({base_y.split('=')[1]}) + {i * line_height}"
        
        drawtext = (
            f"drawtext=fontfile={active_font}:text='{clean_l}':"
            f"x=(w-text_w)/2:y={y_offset}:"
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
    
    print(f"  [STYLIST] Applying Clean Aesthetic: {len(lines)} lines, Font: {active_font}")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  [OK] Stylized video ready: {Path(output_video).name}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Stylist Error: {e.stderr.decode(errors='ignore')}")
        import shutil
        shutil.copy2(input_video, output_video)
