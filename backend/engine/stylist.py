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
    color_grading: Dict[str, Any] = None,
    text_events: List[Any] = None # v12.2 Support for timed text
) -> None:
    """
    Apply visual styling and text overlay to a video using FFmpeg.
    Supports both legacy global overlay and v12.2 timed text events.
    """
    
    has_timed_events = bool(text_events and len(text_events) > 0)
    
    # SAFETY NET: Cap extreme complexity to prevent rendering failures
    if has_timed_events and len(text_events) > 25:
         print(f"  [STYLIST] Excessive text events ({len(text_events)}). Falling back to static mode.")
         has_timed_events = False
    
    # Priority Gate: If timed events exist (and passed safety), they OVERRIDE global static text.
    has_global_text = bool(text_overlay and text_overlay.strip())
    if has_timed_events:
        has_global_text = False
    
    if not has_global_text and not has_timed_events and not color_grading:
        print(f"  [STYLIST] No styling requested. Copying passthrough.")
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
        "handwritten": "lhandw.ttf", # Often needs custom install, fallback safe
        "bold": "arialbd.ttf"
    }
    
    # Try to find the actual font file on Windows
    font_file = font_map.get(font_style_raw, "arial.ttf")
    font_path = Path("C:/Windows/Fonts") / font_file
    
    # We rely on default font usage if path is tricky, but setup color
    font_color = "white"
    color_effects = text_style.get("color_effects", "").lower()
    if "gold" in color_effects or "yellow" in color_effects:
        font_color = "0xEEEEEE" 

    # 2. Build Filter Chain
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

    # B1. Legacy Global Text (Center/Top/Bottom static)
    if has_global_text:
        import textwrap
        raw_lines = text_overlay.replace("|", "\n").split("\n")
        lines = []
        for line in raw_lines:
            if len(line.strip()) > 35:
                lines.extend(textwrap.wrap(line.strip(), width=35))
            else:
                if line.strip(): lines.append(line.strip())
        
        placement = text_style.get("placement", "center").lower()
        font_size = 42
        line_height = font_size * 1.5
        
        if "top" in placement:
            base_y_expr = "h/5"
        elif "bottom" in placement:
            base_y_expr = f"h*0.8 - ({len(lines)} * {line_height}/2)"
        else:
            base_y_expr = f"(h - ({len(lines)} * {line_height}))/2"
            
        for i, line in enumerate(lines):
            clean_l = _sanitize_text_for_ffmpeg(line)
            y_offset = f"({base_y_expr}) + {i * line_height}"
            drawtext = (
                f"drawtext=text='{clean_l}':"
                f"x=(w-text_w)/2:y={y_offset}:"
                f"fontsize={font_size}:fontcolor={font_color}:"
                f"shadowcolor=black@0.4:shadowx=2:shadowy=2"
            )
            filters.append(drawtext)

    # B2. v12.2 Timed Text Events
    if has_timed_events:
        for evt in text_events:
            # Safely access attributes whether it's a dict or Pydantic model
            content = getattr(evt, 'content', evt.get('content') if isinstance(evt, dict) else str(evt))
            start_t = getattr(evt, 'start', evt.get('start', 0) if isinstance(evt, dict) else 0)
            end_t = getattr(evt, 'end', evt.get('end', 5) if isinstance(evt, dict) else 5)
            role = getattr(evt, 'role', evt.get('role', 'Decorative') if isinstance(evt, dict) else "").lower()
            
            clean_content = _sanitize_text_for_ffmpeg(content)
            
            # Dynamic Sizing based on Role
            evt_font_size = 64 if "anchor" in role else 48
                
            # Dynamic Placement
            # Anchors = Center, Emphasis = Slightly higher, Decorative = Bottom
            if "anchor" in role:
                x_pos = "(w-text_w)/2"
                y_pos = "(h-text_h)/2" 
            elif "emphasis" in role:
                x_pos = "(w-text_w)/2"
                y_pos = "(h-text_h)/3"
            else:
                x_pos = "(w-text_w)/2"
                y_pos = "h-(h/5)"
            
            drawtext = (
                f"drawtext=text='{clean_content}':"
                f"enable='between(t,{start_t},{end_t})':"
                f"x={x_pos}:y={y_pos}:"
                f"fontsize={evt_font_size}:fontcolor={font_color}:"
                f"shadowcolor=black@0.8:shadowx=3:shadowy=3"
            )
            filters.append(drawtext)
    
    # If no filters (e.g. empty inputs), just copy
    if not filters:
        import shutil
        shutil.copy2(input_video, output_video)
        return
        
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
    
    print(f"  [STYLIST] Applying v12.2 Styles: {len(filters)} filters (Timed Events: {len(text_events) if text_events else 0})")
    try:
        # Increased timeout for complex filter chains
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        print(f"  [OK] Stylized video ready: {Path(output_video).name}")
    except Exception as e:
        print(f"  [WARN] Stylist failed (likely FFmpeg syntax), falling back to unstylized: {e}")
        import shutil
        shutil.copy2(input_video, output_video)

def _sanitize_text_for_ffmpeg(text: str) -> str:
    """Helper to strip dangerous characters for Windows FFmpeg."""
    clean = text.replace(":", "").replace(",", "").replace("'", "").replace('"', "").replace("\\", "")
    return "".join(c for c in clean if c.isalnum() or c in " .!?#@%&*()-_=+[]{}|;~")
