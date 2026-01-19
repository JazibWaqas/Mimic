"""
Test which API keys are fresh and which are exhausted.
Makes ONE minimal API call per key to check quota status.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import google.generativeai as genai
from utils.api_key_manager import get_key_manager

mgr = get_key_manager()

print("=" * 80)
print("🔑 API KEY HEALTH CHECK")
print("=" * 80)
print(f"\nTotal keys loaded: {len(mgr.keys)}\n")

# Test each key with a minimal request
results = []

for i, key in enumerate(mgr.keys, 1):
    print(f"Testing Key {i}/11: {key[:15]}...", end=" ")
    
    try:
        # Configure with this specific key
        genai.configure(api_key=key)
        
        # Make the smallest possible request (list models)
        models = genai.list_models()
        model_list = list(models)
        
        # If we got here, key is working
        print("✅ FRESH")
        results.append((i, key[:15], "FRESH", ""))
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
            print("❌ QUOTA EXHAUSTED")
            results.append((i, key[:15], "EXHAUSTED", "Quota limit"))
        elif "invalid" in error_msg or "api_key" in error_msg:
            print("⚠️  INVALID KEY")
            results.append((i, key[:15], "INVALID", "Bad key"))
        else:
            print(f"⚠️  ERROR: {str(e)[:50]}")
            results.append((i, key[:15], "ERROR", str(e)[:50]))

print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

fresh_count = sum(1 for r in results if r[2] == "FRESH")
exhausted_count = sum(1 for r in results if r[2] == "EXHAUSTED")
error_count = sum(1 for r in results if r[2] in ["INVALID", "ERROR"])

print(f"\n✅ Fresh keys:     {fresh_count}/11")
print(f"❌ Exhausted keys: {exhausted_count}/11")
print(f"⚠️  Error keys:    {error_count}/11")

if fresh_count >= 2:
    print(f"\n🎉 READY TO GO! You have {fresh_count} working keys.")
    print(f"   Estimated capacity: {fresh_count * 15} requests/minute")
elif fresh_count == 1:
    print(f"\n⚠️  CAUTION: Only 1 working key. May hit limits during test.")
else:
    print(f"\n🛑 NOT READY: No fresh keys available. Wait for quota reset.")

print("\n" + "=" * 80)
