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
    
    # Fallback if font isn't found
    if font_path.exists():
        # THE GOLD STANDARD FOR WINDOWS FONT PATHS IN FFMPEG:
        # 1. Use forward slashes
        # 2. ESCAPE THE COLON WITH DOUBLE BACKSLASH: C\\:/...
        # 3. DO NOT wrap in single quotes if using this escaping style
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
        # DEMO-READY HARDENING:
        # FFmpeg filtergraphs on Windows are notoriously fragile with punctuation.
        # For the demo, we strip characters that act as filter delimiters (comma, colon, quote).
        # This is better than a crashed video.
        clean_l = line.replace(":", "").replace(",", "").replace("'", "").replace('"', "").replace("\\", "")
        # Remove any other non-standard chars that might break the shell
        clean_l = "".join(c for c in clean_l if c.isalnum() or c in " .!?#@%&*()-_=+[]{}|;~")
        
        y_offset = f"({base_y.split('=')[1]}) + {i * line_height}"
        
        # We use the absolute simplest drawtext syntax that works on all Windows FFmpeg builds
        drawtext = (
            f"drawtext=text='{clean_l}':"
            f"x=(w-text_w)/2:y={y_offset}:"
            f"fontsize={font_size}:fontcolor={font_color}:"
            f"shadowcolor=black@0.4:shadowx=2:shadowy=2"
        )
        # We also omit fontfile to use the system default, which is safer than a broken path
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
    
    print(f"  [STYLIST] Applying Demo-Safe Aesthetic: {len(lines)} lines")
    try:
        # We use a short timeout for the stylist to avoid hanging
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        print(f"  [OK] Stylized video ready: {Path(output_video).name}")
    except Exception as e:
        print(f"  [WARN] Stylist failed (likely FFmpeg syntax), falling back to unstylized: {e}")
        import shutil
        shutil.copy2(input_video, output_video)
