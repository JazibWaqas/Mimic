"""
Test Keys 2-4 with REAL content generation requests.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import google.generativeai as genai
from utils.api_key_manager import get_key_manager

mgr = get_key_manager()

print("Testing Keys 2-4 with REAL generate_content requests...\n")

for i in [1, 2, 3]:  # Test keys 2, 3, 4 (indices 1, 2, 3)
    key = mgr.keys[i]
    print(f"Key {i+1}: {key[:15]}...", end=" ")
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-3-flash-preview")
        
        # Real content generation request
        response = model.generate_content("Return JSON: {\"status\": \"ok\"}")
        
        if "ok" in response.text or "OK" in response.text:
            print("✅ WORKING")
        else:
            print(f"⚠️  Unexpected response: {response.text[:50]}")
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
            print("❌ QUOTA EXHAUSTED")
        else:
            print(f"❌ ERROR: {str(e)[:80]}")

print("\n✅ If you see 'WORKING' for all 3, we're good to go!")
