# Test: Gemini as Editor

This directory contains tests to determine if Gemini 3 can replace the deterministic matching algorithm.

## Purpose

Test if Gemini can design the entire edit by seeing:
- Reference structure (all segments with vibes/energy)
- All clip metadata (energy/vibes/best_moments)

Compare Gemini's output to the current deterministic algorithm.

## Files

- `test_gemini_as_editor.py`: Main test script
- `README.md`: This file

## Usage

```bash
cd backend/test_gemini_matching
python test_gemini_as_editor.py
```

Requires `GEMINI_API_KEY` environment variable.

## Output

Results are saved to `gemini_edit_design_YYYYMMDD_HHMMSS.json` with:
- Reference analysis
- All clip analyses
- Gemini's edit design
- Full prompt used

## Safety

This test directory is completely separate from the main codebase. It does NOT modify:
- `backend/engine/brain.py`
- `backend/engine/editor.py`
- Any cache files
- Any production code

It only reads from cache and writes test results.
