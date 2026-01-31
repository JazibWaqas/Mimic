import os
import subprocess
import json
from pathlib import Path

def get_clip_metadata(file_path):
    cmd = [
        "ffprobe", "-v", "error", 
        "-show_format", "-show_streams", 
        "-of", "json", str(file_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        return None

def analyze():
    clip_dir = Path(r"c:\Users\OMNIBOOK\Documents\GitHub\Mimic\data\samples\clips")
    clips = list(clip_dir.glob("*.mp4"))
    
    results = []
    
    for clip in clips:
        meta = get_clip_metadata(clip)
        if not meta:
            continue
            
        video_stream = next((s for s in meta['streams'] if s['codec_type'] == 'video'), None)
        format_info = meta['format']
        
        if not video_stream:
            continue
            
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        
        # Calculate FPS
        r_frame_rate = video_stream.get('r_frame_rate', '0/0')
        if '/' in r_frame_rate:
            num, den = map(int, r_frame_rate.split('/'))
            fps = num / den if den != 0 else 0
        else:
            fps = float(r_frame_rate)
            
        bitrate = int(format_info.get('bit_rate', 0))
        duration = float(format_info.get('duration', 0))
        
        # Quality Logic
        # 1. Pixel Density (Bitrate / (Width * Height))
        # This tells us how much "data" is packed into each pixel. High = Sharp.
        pixel_density = bitrate / (width * height) if (width * height) > 0 else 0
        
        # 2. Cinematic vs "Soap Opera"
        # 60fps is usually smoother but less cinematic
        is_high_fps = fps > 31
        
        # 3. Resolution Tier
        res_tier = "SD"
        if width * height >= 1920 * 1080:
            res_tier = "FHD"
        elif width * height >= 1280 * 720:
            res_tier = "HD"
            
        results.append({
            "name": clip.name,
            "res": f"{width}x{height}",
            "res_tier": res_tier,
            "fps": round(fps, 2),
            "bitrate_kbps": round(bitrate / 1000, 2),
            "pixel_density": round(pixel_density, 3),
            "is_high_fps": is_high_fps
        })
        
    # Sort by pixel density (Clarity)
    results.sort(key=lambda x: x['pixel_density'], reverse=True)
    
    # Print findings
    print("\n--- CLIP QUALITY AUDIT ---")
    print(f"{'Filename':<15} | {'Res':<10} | {'FPS':<6} | {'Bitrate':<10} | {'Density':<8}")
    print("-" * 60)
    for r in results:
        fps_mark = "*" if r['is_high_fps'] else " "
        print(f"{r['name']:<15} | {r['res']:<10} | {r['fps']:<5}{fps_mark} | {r['bitrate_kbps']:<8} | {r['pixel_density']:<8}")

if __name__ == "__main__":
    analyze()
