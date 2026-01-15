"""
Quick test script to verify the pipeline works.
Tests the fixed editor with sample data.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from models import StyleBlueprint, Segment, ClipIndex, ClipMetadata, EnergyLevel, MotionType, BestMoment
from engine.editor import match_clips_to_blueprint, print_edl_summary, validate_edl

def test_editor():
    """Test the fixed editor with mock data."""
    
    print("\n" + "="*60)
    print("TESTING FIXED EDITOR")
    print("="*60 + "\n")
    
    # Create mock blueprint (fast-paced reference with many cuts)
    blueprint = StyleBlueprint(
        total_duration=10.0,
        segments=[
            Segment(id=1, start=0.0, end=1.0, duration=1.0, energy=EnergyLevel.HIGH, motion=MotionType.DYNAMIC),
            Segment(id=2, start=1.0, end=2.0, duration=1.0, energy=EnergyLevel.HIGH, motion=MotionType.DYNAMIC),
            Segment(id=3, start=2.0, end=3.5, duration=1.5, energy=EnergyLevel.MEDIUM, motion=MotionType.DYNAMIC),
            Segment(id=4, start=3.5, end=4.5, duration=1.0, energy=EnergyLevel.HIGH, motion=MotionType.DYNAMIC),
            Segment(id=5, start=4.5, end=6.0, duration=1.5, energy=EnergyLevel.MEDIUM, motion=MotionType.STATIC),
            Segment(id=6, start=6.0, end=7.0, duration=1.0, energy=EnergyLevel.HIGH, motion=MotionType.DYNAMIC),
            Segment(id=7, start=7.0, end=8.5, duration=1.5, energy=EnergyLevel.LOW, motion=MotionType.STATIC),
            Segment(id=8, start=8.5, end=10.0, duration=1.5, energy=EnergyLevel.HIGH, motion=MotionType.DYNAMIC),
        ]
    )
    
    # Create mock clips with best moments
    clips = [
        ClipMetadata(
            filename="clip1.mp4",
            filepath="data/samples/clip1.mp4",
            duration=15.0,
            energy=EnergyLevel.HIGH,
            motion=MotionType.DYNAMIC,
            best_moments={
                "High": BestMoment(start=5.0, end=8.0, reason="Peak action"),
                "Medium": BestMoment(start=2.0, end=4.5, reason="Moderate pace"),
                "Low": BestMoment(start=0.0, end=2.0, reason="Calm opening")
            }
        ),
        ClipMetadata(
            filename="clip2.mp4",
            filepath="data/samples/clip2.mp4",
            duration=12.0,
            energy=EnergyLevel.MEDIUM,
            motion=MotionType.DYNAMIC,
            best_moments={
                "High": BestMoment(start=7.0, end=10.0, reason="Energetic moment"),
                "Medium": BestMoment(start=3.0, end=6.0, reason="Steady pace"),
                "Low": BestMoment(start=0.0, end=2.5, reason="Slow start")
            }
        ),
        ClipMetadata(
            filename="clip3.mp4",
            filepath="data/samples/clip3.mp4",
            duration=20.0,
            energy=EnergyLevel.LOW,
            motion=MotionType.STATIC,
            best_moments={
                "High": BestMoment(start=10.0, end=13.0, reason="Brief action"),
                "Medium": BestMoment(start=5.0, end=8.0, reason="Moderate section"),
                "Low": BestMoment(start=0.0, end=4.0, reason="Very calm")
            }
        ),
        ClipMetadata(
            filename="clip4.mp4",
            filepath="data/samples/clip4.mp4",
            duration=18.0,
            energy=EnergyLevel.HIGH,
            motion=MotionType.DYNAMIC,
            best_moments={
                "High": BestMoment(start=8.0, end=12.0, reason="High energy"),
                "Medium": BestMoment(start=4.0, end=7.0, reason="Medium pace"),
                "Low": BestMoment(start=0.0, end=3.0, reason="Calm intro")
            }
        ),
    ]
    
    clip_index = ClipIndex(clips=clips)
    
    # Run matching
    print(f"Blueprint: {blueprint.total_duration}s with {len(blueprint.segments)} segments")
    print(f"Clips: {len(clips)} clips available\n")
    
    edl = match_clips_to_blueprint(blueprint, clip_index)
    
    # Print summary
    print_edl_summary(edl, blueprint, clip_index)
    
    # Validate
    try:
        validate_edl(edl, blueprint)
        print("✅ EDL validation PASSED")
    except ValueError as e:
        print(f"❌ EDL validation FAILED: {e}")
        return False
    
    # Check that all clips were used
    used_clips = set()
    for decision in edl.decisions:
        filename = Path(decision.clip_path).name
        used_clips.add(filename)
    
    print(f"\n✅ Clips used: {len(used_clips)}/{len(clips)}")
    if len(used_clips) < len(clips):
        print(f"⚠️  WARNING: Not all clips were used!")
        print(f"   Used: {sorted(used_clips)}")
        print(f"   Available: {sorted(c.filename for c in clips)}")
    
    # Check for back-to-back repeats
    back_to_back = 0
    for i in range(len(edl.decisions) - 1):
        if edl.decisions[i].clip_path == edl.decisions[i+1].clip_path:
            back_to_back += 1
    
    if back_to_back > 0:
        print(f"⚠️  WARNING: {back_to_back} back-to-back repeats detected")
    else:
        print(f"✅ No back-to-back repeats")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_editor()
    sys.exit(0 if success else 1)
