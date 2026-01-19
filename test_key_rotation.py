"""
Test if API key rotation is working correctly.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from utils.api_key_manager import get_key_manager

mgr = get_key_manager()

print(f"Total keys: {mgr.get_all_keys_count()}")
print(f"Remaining keys: {mgr.get_remaining_keys_count()}")
print(f"\nCurrent key: {mgr.get_current_key()[:15]}...")

print("\n--- Simulating 11 quota exhaustions ---\n")

for i in range(12):
    current = mgr.get_current_key()
    if current:
        print(f"Attempt {i+1}: Using key {current[:15]}...")
        next_key = mgr.rotate_key(f"Test rotation {i+1}")
        if next_key:
            print(f"  → Rotated to: {next_key[:15]}...")
        else:
            print(f"  → No more keys available!")
            break
    else:
        print(f"Attempt {i+1}: No key available")
        break

print(f"\nFinal state:")
print(f"  Remaining keys: {mgr.get_remaining_keys_count()}")
print(f"  Exhausted keys: {len(mgr.exhausted_keys)}")
