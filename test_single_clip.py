"""
Single Clip Analysis Test - Verify API Flow

This script:
1. Analyzes ONE clip with Gemini
2. Prints the FULL raw response
3. Shows what gets cached
4. Reports API usage

Use this to verify the analysis pipeline before caching all clips.
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

# ============================================================================
# CONFIGURATION
# ============================================================================

# Pick a single clip to test
CLIPS_DIR = Path("data/samples/clips")
TEST_CLIP = CLIPS_DIR / "clip.mp4"  # First clip

# Cache directory
CACHE_DIR = Path("data/cache")

print("=" * 80)
print("🧪 SINGLE CLIP ANALYSIS TEST")
print("=" * 80)
print(f"Cache Version: {CACHE_VERSION}")
print(f"Test Clip: {TEST_CLIP}")
print()

# ============================================================================
# CHECK API KEYS
# ============================================================================

key_manager = get_key_manager()
print(f"📊 API Keys Available: {key_manager.get_all_keys_count()}")
print(f"📊 Keys Remaining: {key_manager.get_remaining_keys_count()}")
print()

# ============================================================================
# ANALYZE CLIP
# ============================================================================

if not TEST_CLIP.exists():
    print(f"❌ Test clip not found: {TEST_CLIP}")
    sys.exit(1)

duration = get_video_duration(str(TEST_CLIP))
print(f"📹 Clip Duration: {duration:.2f}s")
print()

# Initialize model
print("🔧 Initializing Gemini...")
model = initialize_gemini()
print()

# Upload video
print("📤 Uploading video to Gemini...")
print("   (This counts as 1 API interaction)")
video_file = genai.upload_file(path=str(TEST_CLIP))

# Wait for processing
import time
while video_file.state.name == "PROCESSING":
    print(f"   Waiting for processing (state: {video_file.state.name})...")
    time.sleep(5)
    video_file = genai.get_file(video_file.name)

if video_file.state.name == "FAILED":
    print(f"❌ Video processing failed!")
    sys.exit(1)

print(f"✅ Upload complete: {video_file.uri}")
print()

# Generate analysis
print("🧠 Requesting analysis from Gemini...")
print("   (This counts as 1 API interaction)")
print()

response = model.generate_content([video_file, CLIP_COMPREHENSIVE_PROMPT])

# Check response status
print("📊 Response Status:")
print(f"   Candidates: {len(response.candidates) if response.candidates else 0}")

if response.candidates:
    candidate = response.candidates[0]
    print(f"   Finish Reason: {candidate.finish_reason}")
    
    # Check for safety blocks
    if candidate.safety_ratings:
        print("   Safety Ratings:")
        for rating in candidate.safety_ratings:
            print(f"      - {rating.category}: {rating.probability}")
    
    # Check if blocked
    if candidate.finish_reason.name == "SAFETY":
        print("❌ Response was BLOCKED by safety filters!")
        print("   The video may contain content flagged as unsafe.")
        sys.exit(1)
    elif candidate.finish_reason.name == "STOP":
        print("✅ Response completed normally")
    elif candidate.finish_reason.name == "MAX_TOKENS":
        print("⚠️ Response was truncated due to max tokens")
    else:
        print(f"⚠️ Unexpected finish reason: {candidate.finish_reason.name}")
else:
    print("❌ No candidates in response!")
    if response.prompt_feedback:
        print(f"   Prompt feedback: {response.prompt_feedback}")
    sys.exit(1)

print()

# Try to get text
try:
    response_text = response.text
except ValueError as e:
    print(f"❌ Could not get response text: {e}")
    print()
    print("Full response object:")
    print(response)
    sys.exit(1)

# ============================================================================
# RAW RESPONSE
# ============================================================================

print("=" * 80)
print("RAW GEMINI RESPONSE:")
print("=" * 80)
print(response_text)
print("=" * 80)
print()

# ============================================================================
# PARSED RESPONSE
# ============================================================================

print("PARSED RESPONSE:")
print("=" * 80)

try:
    parsed = _parse_json_response(response_text)
    print(json.dumps(parsed, indent=2))
except Exception as e:
    print(f"❌ Parsing failed: {e}")
    sys.exit(1)

print("=" * 80)
print()

# ============================================================================
# VALIDATION
# ============================================================================

print("✅ VALIDATION CHECKS:")
print("-" * 40)

checks = {
    "energy": parsed.get("energy"),
    "motion": parsed.get("motion"),
    "vibes": parsed.get("vibes"),
    "content_description": parsed.get("content_description"),
    "best_moments.High": parsed.get("best_moments", {}).get("High"),
    "best_moments.Medium": parsed.get("best_moments", {}).get("Medium"),
    "best_moments.Low": parsed.get("best_moments", {}).get("Low"),
}

all_valid = True
for field, value in checks.items():
    if value is None or value == "" or value == []:
        print(f"   ❌ {field}: MISSING")
        all_valid = False
    else:
        if isinstance(value, dict):
            print(f"   ✅ {field}: {value.get('start', '?')}s - {value.get('end', '?')}s")
        elif isinstance(value, list):
            print(f"   ✅ {field}: {', '.join(value)}")
        else:
            print(f"   ✅ {field}: {value}")

print()

if all_valid:
    print("🎉 ALL FIELDS PRESENT - Analysis is working correctly!")
else:
    print("⚠️  SOME FIELDS MISSING - Check prompt or Gemini response")

print()

# ============================================================================
# API USAGE SUMMARY
# ============================================================================

print("📊 API USAGE SUMMARY:")
print("-" * 40)
print("   Upload: 1 call")
print("   Analysis: 1 call")
print("   Total: 2 API calls for 1 clip")
print()
print("   For 20 clips: 40 API calls (first run)")
print("   After caching: 0 API calls")
print()

# ============================================================================
# CACHE PREVIEW
# ============================================================================

print("💾 CACHE PREVIEW (what would be saved):")
print("-" * 40)

import hashlib
with open(TEST_CLIP, 'rb') as f:
    file_hash = hashlib.md5(f.read()).hexdigest()[:12]

cache_file = CACHE_DIR / f"clip_comprehensive_{file_hash}.json"
print(f"   Cache file: {cache_file.name}")

# Show what would be cached
cache_data = {
    "energy": parsed.get("energy", "Unknown"),
    "motion": parsed.get("motion", "Unknown"),
    "vibes": parsed.get("vibes", []),
    "content_description": parsed.get("content_description", ""),
    "best_moments": {},
    "_cache_version": CACHE_VERSION,
    "_cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
}

if "best_moments" in parsed:
    for level, moment in parsed["best_moments"].items():
        cache_data["best_moments"][level] = {
            "start": moment.get("start", 0),
            "end": moment.get("end", 0),
            "reason": moment.get("reason", "")
        }

print(json.dumps(cache_data, indent=2))
print()

# ============================================================================
# DONE
# ============================================================================

print("=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)
print()
print("Next steps:")
print("1. If all fields are present → Run full cache population")
print("2. If fields are missing → Check prompt or Gemini model")
print("3. Delete old cache: Remove-Item data/cache/*.json -Force")
