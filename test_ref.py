"""
Test a reference with the Vibes + BPM system.
Writes full terminal output to data/results/<ref_stem>_xray_output.txt.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from engine.orchestrator import run_mimic_pipeline
from engine.processors import get_video_duration
import os

# Paths - can be overridden with environment variable
import os
default_ref = os.environ.get('TEST_REFERENCE', 'ref5.mp4')
REFERENCE = Path(f"data/samples/reference/{default_ref}")
CLIPS_DIR = Path("data/samples/clips")
RESULTS_DIR = Path("data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Get all clips
CLIP_PATHS = sorted([str(CLIPS_DIR / f) for f in os.listdir(CLIPS_DIR) if f.endswith('.mp4')])

class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, s):
        for f in self.files:
            f.write(s)
            try: f.flush()
            except Exception: pass
    def flush(self):
        for f in self.files:
            try: f.flush()
            except Exception: pass

xray_path = RESULTS_DIR / f"{REFERENCE.stem}_xray_output.txt"
xray_file = open(xray_path, 'w', encoding='utf-8')
sys.stdout = Tee(sys.__stdout__, xray_file)

print("=" * 80)
print(f"TESTING {REFERENCE.name.upper()} WITH VIBES + DYNAMIC BPM")
print("=" * 80)

# Get reference info
ref_duration = get_video_duration(str(REFERENCE))
print(f"\n📹 Reference: {REFERENCE.name}")
print(f"   Duration: {ref_duration:.2f}s")
print(f"\n📎 Testing with {len(CLIP_PATHS)} clips")
print(f"   Cache Version: 6.1 (will re-analyze clips for vibes)")
print()

# Run pipeline
session_id = f"{REFERENCE.stem}_vibes_test"

print("🚀 Starting pipeline...")
print("   Step 1: Validating inputs")
print("   Step 2: Scene detection + BPM detection + Reference analysis")
print("   Step 3: Clip analysis (NEW: extracting vibes + content)")
print("   Step 4: Semantic matching (NEW: vibe-aware selection)")
print("   Step 5: Rendering with dynamic BPM sync")
print()

result = run_mimic_pipeline(
    reference_path=str(REFERENCE),
    clip_paths=CLIP_PATHS,
    session_id=session_id,
    output_dir=str(RESULTS_DIR),
    progress_callback=None
)

# Comprehensive debugging report
print("\n" + "=" * 80)
if result.success:
    output_path = RESULTS_DIR / f"mimic_output_{session_id}.mp4"
    output_duration = get_video_duration(str(output_path))
    
    print("✅ SUCCESS!")
    print(f"\n📊 Basic Results:")
    print(f"   Output: {output_path.name}")
    print(f"   Duration: {output_duration:.2f}s (ref: {ref_duration:.2f}s)")
    print(f"   Difference: {abs(output_duration - ref_duration):.2f}s")
    print(f"   Processing time: {result.processing_time_seconds:.1f}s")
    
    if result.blueprint and result.edl:
        from collections import defaultdict, Counter
        
        blueprint = result.blueprint
        edl = result.edl
        
        print(f"\n{'='*80}")
        print("🧠 COMPREHENSIVE SYSTEM ANALYSIS")
        print(f"{'='*80}")
        
        # 1. Reference Analysis Breakdown
        print(f"\n📹 Reference Analysis:")
        print(f"   Editing Style: {blueprint.editing_style}")
        print(f"   Emotional Intent: {blueprint.emotional_intent}")
        print(f"   Arc Description: {blueprint.arc_description[:100]}..." if len(blueprint.arc_description) > 100 else f"   Arc Description: {blueprint.arc_description}")
        print(f"   Total Segments: {len(blueprint.segments)}")
        
        # 1.5. Blueprint Full Detail (NEW)
        print(f"\n📑 BLUEPRINT FULL SEGMENT LIST:")
        for i, seg in enumerate(blueprint.segments):
            print(f"   {i+1:02d}: {seg.start:5.2f}-{seg.end:5.2f}s | {seg.energy.value:6} | Vibe: {seg.vibe:10} | {seg.arc_stage}")
        
        # 2. Arc Stage Distribution
        arc_stages = Counter([seg.arc_stage for seg in blueprint.segments])
        print(f"\n📈 Arc Stage Distribution:")
        for stage, count in arc_stages.most_common():
            pct = (count / len(blueprint.segments)) * 100
            print(f"   {stage}: {count} segments ({pct:.1f}%)")
        
        # 3. Vibe Distribution
        vibes = Counter([seg.vibe for seg in blueprint.segments if seg.vibe != "General"])
        if vibes:
            print(f"\n🎨 Vibe Distribution:")
            for vibe, count in vibes.most_common():
                pct = (count / len(blueprint.segments)) * 100
                print(f"   {vibe}: {count} segments ({pct:.1f}%)")
        
        # 4. Clip Usage Analysis
        clip_usage = defaultdict(int)
        clip_reasoning = defaultdict(list)
        for decision in edl.decisions:
            clip_name = Path(decision.clip_path).name
            clip_usage[clip_name] += 1
            clip_reasoning[clip_name].append(decision.reasoning)
        
        print(f"\n📎 Clip Usage Analysis:")
        print(f"   Unique clips used: {len(clip_usage)}/{len(CLIP_PATHS)}")
        print(f"   Most used clips:")
        for clip_name, count in sorted(clip_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = (count / len(edl.decisions)) * 100
            print(f"     {clip_name}: {count} times ({pct:.1f}%)")
        
        # 5. Reasoning Breakdown
        smart_matches = sum(1 for d in edl.decisions if "✨ Smart Match" in d.reasoning)
        good_fits = sum(1 for d in edl.decisions if "🎯 Good Fit" in d.reasoning)
        constraint_relax = sum(1 for d in edl.decisions if "⚙️ Constraint Relaxation" in d.reasoning)
        
        print(f"\n🧠 AI Reasoning Breakdown:")
        print(f"   ✨ Smart Match: {smart_matches} ({smart_matches/len(edl.decisions)*100:.1f}%)")
        print(f"   🎯 Good Fit: {good_fits} ({good_fits/len(edl.decisions)*100:.1f}%)")
        print(f"   ⚙️ Constraint Relaxation: {constraint_relax} ({constraint_relax/len(edl.decisions)*100:.1f}%)")
        
        # 6. Vibe Matching Stats
        vibe_matches = sum(1 for d in edl.decisions if d.vibe_match)
        print(f"\n🎨 Vibe Matching:")
        print(f"   Matches: {vibe_matches}/{len(edl.decisions)} ({vibe_matches/len(edl.decisions)*100:.1f}%)")
        
        # 7. Cut Statistics by Arc Stage
        print(f"\n📏 Cut Statistics by Arc Stage:")
        for stage in ["Intro", "Build-up", "Peak", "Outro", "Main"]:
            stage_decisions = []
            for i, decision in enumerate(edl.decisions):
                # Find which segment this decision belongs to
                for seg in blueprint.segments:
                    if seg.start <= decision.timeline_start < seg.end:
                        if seg.arc_stage == stage:
                            stage_decisions.append(decision.timeline_end - decision.timeline_start)
                        break
            
            if stage_decisions:
                avg = sum(stage_decisions) / len(stage_decisions)
                print(f"   {stage}: {len(stage_decisions)} cuts, avg {avg:.2f}s")
        
        # 8. Overall Cut Statistics
        durations = [(d.timeline_end - d.timeline_start) for d in edl.decisions]
        avg_cut = sum(durations) / len(durations)
        min_cut = min(durations)
        max_cut = max(durations)
        
        print(f"\n📏 Overall Cut Statistics:")
        print(f"   Total cuts: {len(edl.decisions)}")
        print(f"   Average cut: {avg_cut:.2f}s")
        print(f"   Shortest cut: {min_cut:.2f}s")
        print(f"   Longest cut: {max_cut:.2f}s")
        
        # 9. Sample Reasoning Examples
        print(f"\n💭 Sample AI Reasoning (first 5 decisions):")
        for i, decision in enumerate(edl.decisions[:5], 1):
            clip_name = Path(decision.clip_path).name
            print(f"   {i}. {clip_name}: {decision.reasoning[:80]}...")
        
        # 10. Clip Index Stats
        if result.clip_index:
            print(f"\n📦 CLIP REGISTRY ({len(result.clip_index.clips)} total):")
            for i, clip in enumerate(sorted(result.clip_index.clips, key=lambda x: x.filename)):
                vibes_str = ", ".join(clip.vibes[:3])
                print(f"   {i+1:02d}: {clip.filename:15} | {clip.energy.value:6} | {clip.duration:5.1f}s | Vibes: {vibes_str}")

            clips_with_moments = sum(1 for c in result.clip_index.clips if c.best_moments)
            clips_with_vibes = sum(1 for c in result.clip_index.clips if c.vibes)
            
            print(f"\n📋 Metadata Coverage:")
            print(f"   Best Moments: {clips_with_moments}/{len(result.clip_index.clips)}")
            print(f"   Vibes: {clips_with_vibes}/{len(result.clip_index.clips)}")
        
        # 15. ENHANCED LOGGING OUTPUT
        if result.edl and hasattr(result.edl, '_enhanced_logging'):
            enhanced = result.edl._enhanced_logging
            import json
            
            print(f"\n{'='*80}")
            print("🔍 ENHANCED LOGGING DATA")
            print(f"{'='*80}")
            
            # A. Candidate Rankings (sample 5-10 segments)
            print(f"\nA. PER-SEGMENT CANDIDATE RANKINGS (Top 3):")
            sample_segments = enhanced['candidate_rankings'][:10]
            for seg_data in sample_segments:
                print(f"\n   Segment {seg_data['segment_id']}:")
                for cand in seg_data['candidates']:
                    winner_marker = " ✅ WINNER" if cand['won'] else ""
                    print(f"     Rank {cand['rank']}: {cand['clip']} | Score: {cand['score']:.1f} | {cand['reasoning']}{winner_marker}")
                    if not cand['won']:
                        print(f"       Why lost: Score {cand['score']:.1f} vs winner {seg_data['candidates'][0]['score']:.1f} (diff: {seg_data['candidates'][0]['score'] - cand['score']:.1f})")
            
            # B. Eligibility Breakdowns
            print(f"\nB. ELIGIBILITY BREAKDOWNS (Sample segments):")
            for breakdown in enhanced['eligibility_breakdowns'][:5]:
                print(f"   Segment {breakdown['segment_id']} ({breakdown['segment_energy']} energy):")
                print(f"     Eligible: {breakdown['eligible_count']}/{breakdown['total_clips']}")
                print(f"     Filtered out: {breakdown['ineligible_count']} clips (energy mismatch)")
            
            # C. Semantic Neighbor Events
            print(f"\nC. SEMANTIC NEIGHBOR EVENTS:")
            print(f"   Total: {len(enhanced['semantic_neighbor_events'])} segments used semantic neighbors")
            if enhanced['semantic_neighbor_events']:
                neighbor_counts = {}
                for event in enhanced['semantic_neighbor_events']:
                    cat = event.get('matched_category', 'unknown')
                    neighbor_counts[cat] = neighbor_counts.get(cat, 0) + 1
                for cat, count in sorted(neighbor_counts.items(), key=lambda x: -x[1]):
                    print(f"     '{cat}': {count} times")
                print(f"\n   Sample events:")
                for event in enhanced['semantic_neighbor_events'][:5]:
                    print(f"     Segment {event['segment_id']}: '{event['segment_vibe']}' → matched '{event['matched_category']}' via {event['clip']}")
            
            # D. Unused Clips
            print(f"\nD. UNUSED CLIPS:")
            unused_data = enhanced['unused_clips']
            print(f"   Never eligible: {len(unused_data['never_eligible'])} clips")
            if unused_data['never_eligible']:
                print(f"     {', '.join(unused_data['never_eligible'][:10])}")
            print(f"   Eligible but never selected: {len(unused_data['eligible_but_not_selected'])} clips")
            if unused_data['eligible_but_not_selected']:
                print(f"     {', '.join(unused_data['eligible_but_not_selected'][:10])}")
            
            # Save enhanced data to JSON
            enhanced_file = RESULTS_DIR / f"{REFERENCE.stem}_enhanced_logging.json"
            with open(enhanced_file, 'w') as f:
                json.dump(enhanced, f, indent=2)
            print(f"\n   [OK] Full enhanced logging saved to: {enhanced_file}")
        
        # 11. Temporal Drift Check (Float Precision Verification)
        gaps = []
        overlaps = []
        for i in range(1, len(edl.decisions)):
            gap = edl.decisions[i].timeline_start - edl.decisions[i-1].timeline_end
            if abs(gap) > 0.001:
                if gap > 0:
                    gaps.append((i, gap))
                else:
                    overlaps.append((i, abs(gap)))
        
        print(f"\n🔍 Temporal Precision Check:")
        if gaps:
            print(f"   ⚠️ WARNING: Timeline Gaps Detected ({len(gaps)}):")
            for i, gap in gaps[:5]:  # Show first 5
                print(f"     Gap after decision {i}: {gap:.6f}s")
            if len(gaps) > 5:
                print(f"     ... and {len(gaps) - 5} more gaps")
        elif overlaps:
            print(f"   ⚠️ WARNING: Timeline Overlaps Detected ({len(overlaps)}):")
            for i, overlap in overlaps[:5]:
                print(f"     Overlap after decision {i}: {overlap:.6f}s")
            if len(overlaps) > 5:
                print(f"     ... and {len(overlaps) - 5} more overlaps")
        else:
            print(f"   ✅ TIMELINE INTEGRITY: No gaps or overlaps detected (all within 0.001s tolerance)")
        
        # 12. Material Efficiency Stats
        if result.clip_index:
            total_available_duration = sum(c.duration for c in result.clip_index.clips)
            used_unique_duration = sum(d.clip_end - d.clip_start for d in edl.decisions)
            
            # Calculate unique clip segments used (avoid double-counting if same clip used multiple times)
            unique_segments = set()
            for decision in edl.decisions:
                clip_name = Path(decision.clip_path).name
                segment_key = f"{clip_name}:{decision.clip_start:.2f}-{decision.clip_end:.2f}"
                unique_segments.add(segment_key)
            
            print(f"\n📦 Material Efficiency:")
            print(f"   Total source duration available: {total_available_duration:.2f}s")
            print(f"   Total duration used in edit: {used_unique_duration:.2f}s")
            print(f"   Unique clip segments used: {len(unique_segments)}")
            if total_available_duration > 0:
                utilization = (used_unique_duration / total_available_duration) * 100
                print(f"   Utilization Ratio: {utilization:.1f}%")
                if utilization < 10:
                    print(f"   💡 Note: Low utilization suggests clips may not match reference vibes well")
        
        # 13. Scoring Transparency (Reasoning Breakdown)
        print(f"\n📊 Selection Reasoning Breakdown:")
        arc_relevant = sum(1 for d in edl.decisions if "Intro-style" in d.reasoning or "Peak-intensity" in d.reasoning or "Outro-style" in d.reasoning or "Build-up" in d.reasoning)
        vibe_matched = sum(1 for d in edl.decisions if "Vibe" in d.reasoning)
        cooldown_warnings = sum(1 for d in edl.decisions if "⚠️" in d.reasoning or "Recently used" in d.reasoning)
        smooth_transitions = sum(1 for d in edl.decisions if "Smooth motion flow" in d.reasoning)
        usage_penalties = sum(1 for d in edl.decisions if "Used" in d.reasoning and "x" in d.reasoning)
        
        print(f"   Arc Stage Relevance: {arc_relevant} decisions ({arc_relevant/len(edl.decisions)*100:.1f}%)")
        print(f"   Vibe Matching: {vibe_matched} decisions ({vibe_matched/len(edl.decisions)*100:.1f}%)")
        print(f"   Visual Cooldown Warnings: {cooldown_warnings} decisions ({cooldown_warnings/len(edl.decisions)*100:.1f}%)")
        print(f"   Smooth Transitions: {smooth_transitions} decisions ({smooth_transitions/len(edl.decisions)*100:.1f}%)")
        print(f"   Usage Penalties Applied: {usage_penalties} decisions ({usage_penalties/len(edl.decisions)*100:.1f}%)")
        
        # 14. Detailed Reasoning Examples (Show scoring factors)
        print(f"\n💭 Detailed Reasoning Examples (first 3 decisions):")
        for i, decision in enumerate(edl.decisions[:3], 1):
            clip_name = Path(decision.clip_path).name
            segment = None
            for seg in blueprint.segments:
                if seg.start <= decision.timeline_start < seg.end:
                    segment = seg
                    break
            
            print(f"\n   Decision {i}:")
            print(f"     Timeline: {decision.timeline_start:.3f}s - {decision.timeline_end:.3f}s ({decision.timeline_end - decision.timeline_start:.3f}s)")
            print(f"     Clip: {clip_name}")
            print(f"     Source: {decision.clip_start:.2f}s - {decision.clip_end:.2f}s")
            if segment:
                print(f"     Segment: {segment.arc_stage} | {segment.energy.value}/{segment.motion.value} | Vibe: {segment.vibe}")
            print(f"     Reasoning: {decision.reasoning}")
            print(f"     Vibe Match: {'✅' if decision.vibe_match else '❌'}")
            
        print(f"\n{'='*80}")
        print(f"🎉 Watch the result: {output_path}")
        print(f"{'='*80}")
        
else:
    print("❌ FAILED")
    print(f"   Error: {result.error}")

print("=" * 80)

sys.stdout = sys.__stdout__
xray_file.close()
print(f"X-ray log: {xray_path}", file=sys.__stdout__)
