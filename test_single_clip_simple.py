"""
Minimal Single Clip Analysis Test - JSON output only
"""

import sys
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import google.generativeai as genai
from engine.brain import (
    initialize_gemini,
    CLIP_COMPREHENSIVE_PROMPT,
    CACHE_VERSION,
    _parse_json_response
)
from engine.processors import get_video_duration
from utils.api_key_manager import get_key_manager
import time

# Configuration
CLIPS_DIR = Path("data/samples/clips")
TEST_CLIP = CLIPS_DIR / "clip.mp4"
OUTPUT_FILE = Path("test_result.json")

print(f"Testing clip: {TEST_CLIP}")
print(f"Cache Version: {CACHE_VERSION}")

# Check API keys
key_manager = get_key_manager()
print(f"API Keys: {key_manager.get_all_keys_count()} total, {key_manager.get_remaining_keys_count()} remaining")

if not TEST_CLIP.exists():
    print(f"ERROR: Clip not found: {TEST_CLIP}")
    sys.exit(1)

duration = get_video_duration(str(TEST_CLIP))
print(f"Clip Duration: {duration:.2f}s")

# Initialize and analyze
print("Initializing Gemini...")
model = initialize_gemini()

print("Uploading video...")
video_file = genai.upload_file(path=str(TEST_CLIP))

while video_file.state.name == "PROCESSING":
    print(f"  Processing... (state: {video_file.state.name})")
    time.sleep(5)
    video_file = genai.get_file(video_file.name)

if video_file.state.name == "FAILED":
    print("ERROR: Video processing failed!")
    sys.exit(1)

print(f"Upload complete: {video_file.uri}")

print("Requesting analysis...")
response = model.generate_content([video_file, CLIP_COMPREHENSIVE_PROMPT])

# Check response
result = {
    "status": "unknown",
    "raw_response": None,
    "parsed": None,
    "validation": {},
    "cache_preview": None
}

if response.candidates:
    candidate = response.candidates[0]
    result["finish_reason"] = candidate.finish_reason.name
    
    if candidate.finish_reason.name == "STOP":
        result["status"] = "success"
        try:
            raw_text = response.text
            result["raw_response"] = raw_text
            
            parsed = _parse_json_response(raw_text)
            result["parsed"] = parsed
            
            # Validation
            result["validation"] = {
                "energy": parsed.get("energy") is not None,
                "motion": parsed.get("motion") is not None,
                "vibes": len(parsed.get("vibes", [])) > 0,
                "content_description": len(parsed.get("content_description", "")) > 0,
                "best_moments_High": parsed.get("best_moments", {}).get("High") is not None,
                "best_moments_Medium": parsed.get("best_moments", {}).get("Medium") is not None,
                "best_moments_Low": parsed.get("best_moments", {}).get("Low") is not None,
            }
            
            # Cache preview
            result["cache_preview"] = {
                "energy": parsed.get("energy", "Unknown"),
                "motion": parsed.get("motion", "Unknown"),
                "vibes": parsed.get("vibes", []),
                "content_description": parsed.get("content_description", ""),
                "best_moments": parsed.get("best_moments", {}),
                "_cache_version": CACHE_VERSION,
            }
            
        except Exception as e:
            result["status"] = "parse_error"
            result["error"] = str(e)
    else:
        result["status"] = "blocked"
        result["error"] = f"Response stopped with reason: {candidate.finish_reason.name}"
else:
    result["status"] = "no_response"
    result["error"] = "No candidates returned"

# Save result
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\nResult saved to: {OUTPUT_FILE}")
print(f"Status: {result['status']}")

if result.get("validation"):
    all_valid = all(result["validation"].values())
    print(f"All fields present: {all_valid}")
    for field, valid in result["validation"].items():
        symbol = "OK" if valid else "MISSING"
        print(f"  {field}: {symbol}")
