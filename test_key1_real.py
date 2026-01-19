"""
Test Key 1 with an actual video analysis request (not just list_models).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import google.generativeai as genai
from utils.api_key_manager import get_key_manager

mgr = get_key_manager()
key1 = mgr.keys[0]

print(f"Testing Key 1 with REAL video analysis request...")
print(f"Key: {key1[:15]}...\n")

try:
    genai.configure(api_key=key1)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    # Try to generate content (text-only, no video upload needed)
    response = model.generate_content("Say 'test' in JSON format: {\"result\": \"test\"}")
    
    print("✅ SUCCESS! Key 1 can make generate_content requests.")
    print(f"Response: {response.text[:100]}")
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ FAILED!")
    print(f"Error: {error_msg[:200]}")
    
    if "429" in error_msg or "quota" in error_msg:
        print("\n🔴 Key 1 IS exhausted for content generation.")
    else:
        print("\n⚠️  Different error (not quota).")
