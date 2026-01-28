# Temporary file with the V7 verification code to manually insert

# INSERT THIS CODE at line 54 in gemini_advisor.py (after the print statements, before cache_dir.mkdir):

    # VERIFICATION: Ensure we have V7 reference data for strategic planning
    # The Advisor needs narrative intent fields to make meaningful recommendations
    has_v7_data = hasattr(blueprint, 'must_have_content') and hasattr(blueprint, 'narrative_message')
    if not has_v7_data:
        print(f"  ⚠️ WARNING: Blueprint missing V7 narrative fields (must_have_content, narrative_message)")
        print(f"  ⚠️ Advisor will have limited strategic insight. Consider re-analyzing reference.")
        # Still proceed - the Advisor can work with basic blueprint data, just less effectively
    else:
        print(f"  ✅ V7 narrative data detected: '{blueprint.narrative_message[:60]}...'")
