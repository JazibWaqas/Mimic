#!/bin/bash
# Run Gemini tests individually to avoid timeout

echo "Running Gemini Editor Tests..."
echo ""

echo "Test 1: ref4 (first run)"
python test_gemini_comprehensive.py ref4 > test_ref4_run1.log 2>&1

echo "Test 2: ref4 (consistency check)"
python test_gemini_comprehensive.py ref4_consistency > test_ref4_consistency.log 2>&1

echo "Test 3: ref3 (abstract vibes)"
python test_gemini_comprehensive.py ref3 > test_ref3.log 2>&1

echo "Test 4: ref9 (edge case - 2 segments)"
python test_gemini_comprehensive.py ref9 > test_ref9.log 2>&1

echo ""
echo "All tests complete. Check logs for results."
