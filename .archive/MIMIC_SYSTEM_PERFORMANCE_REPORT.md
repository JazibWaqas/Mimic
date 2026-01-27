# MIMIC System Performance Report - Raw Data

This document contains actual Gemini outputs and system performance data from three test runs.

---

## Example 1: Best Performance (ref4)

### Reference Analysis (Gemini Output)
```json
{
  "total_duration": 14.230975,
  "editing_style": "Cinematic Montage",
  "emotional_intent": "Dynamic",
  "arc_description": "Video with multiple scene changes",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 0.53,
      "duration": 0.53,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Nature",
      "arc_stage": "Intro",
      "reasoning": "Scene change to a blue raft on a river."
    },
    {
      "id": 2,
      "start": 0.53,
      "end": 0.93,
      "duration": 0.4,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Travel",
      "arc_stage": "Intro",
      "reasoning": "Scene change to a hand reaching out of a car window towards snowy mountains."
    },
    {
      "id": 3,
      "start": 0.93,
      "end": 1.4,
      "duration": 0.47,
      "energy": "High",
      "motion": "Dynamic",
      "vibe": "Friends",
      "arc_stage": "Intro",
      "reasoning": "Scene change to a group of friends in life jackets posing by a river."
    }
  ],
  "overall_reasoning": "The video is a fast-paced cinematic montage of travel memories with friends, featuring a repeating loop of short clips that create a dynamic and nostalgic feel.",
  "ideal_material_suggestions": [
    "High-quality travel footage",
    "Candid shots of friends",
    "Scenic nature views",
    "Action-oriented travel activities"
  ],
  "_cache_version": "6.1",
  "_cached_at": "2026-01-22 23:06:18"
}
```

### Key Matching Decisions
- Segment 1 (0.00-0.53s): clip1.mp4 selected - Score: 105.0 | Vibe:Nature match | Medium/Dynamic
- Segment 2 (0.53-0.93s): clip56.mp4 selected - Score: 110.0 | Vibe:Travel match | Medium/Dynamic
- Segment 3 (0.93-1.40s): clip37.mp4 selected - Score: 110.0 | Vibe:Friends match | High/Dynamic

### Performance Metrics
- Vibe Match Accuracy: 100% (30/30 segments)
- Clip Diversity: 30/55 unique clips used, no repeats
- Energy Compromises: 2 (Medium→Low: 1, Medium→High: 1)
- Processing Time: 18.9s

---

## Example 2: Average Performance (ref3)

### Reference Analysis (Gemini Output)
```json
{
  "total_duration": 15.5,
  "editing_style": "Cinematic Montage",
  "emotional_intent": "Nostalgic & Joyful",
  "arc_description": "A rapid-fire collection of memories that maintains a high emotional peak throughout, celebrating friendship through diverse shared experiences and travel highlights.",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 1.0,
      "duration": 1.0,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Travel",
      "arc_stage": "Intro"
    },
    {
      "id": 2,
      "start": 1.0,
      "end": 2.0,
      "duration": 1.0,
      "energy": "High",
      "motion": "Dynamic",
      "vibe": "Celebration",
      "arc_stage": "Build-up"
    },
    {
      "id": 3,
      "start": 2.0,
      "end": 3.0,
      "duration": 1.0,
      "energy": "High",
      "motion": "Dynamic",
      "vibe": "Social",
      "arc_stage": "Build-up"
    }
  ],
  "overall_reasoning": "The video employs a very strict rhythmic editing pattern, with cuts occurring almost exactly every second. This creates a 'heartbeat' effect that drives the viewer through a variety of locations and activities, reinforcing the theme of a shared life journey.",
  "ideal_material_suggestions": [
    "Slow-motion shots of group laughter to emphasize emotional connection.",
    "Wide-angle drone shots of the group in vast landscapes to show the scale of their travels.",
    "Close-up candid shots of friends' faces during high-energy moments like the party or karaoke.",
    "Golden hour lighting for outdoor shots to enhance the nostalgic, warm aesthetic."
  ],
  "_cache_version": "6.1",
  "_cached_at": "2026-01-25 01:10:53"
}
```

### Key Matching Decisions
- Segment 1 (0.00-1.00s): clip33.mp4 selected - Score: 105.0 | Vibe:Travel match | Medium/Dynamic
- Segment 2 (1.00-2.00s): clip38.mp4 selected - Score: 110.0 | Vibe:Celebration match | High/Dynamic
- Segment 3 (2.00-3.00s): clip23.mp4 selected - Score: 95.0 | Nearby:friends match | High/Dynamic

### Performance Metrics
- Vibe Match Accuracy: 53.3% (8/15 segments)
- Clip Diversity: 15/55 unique clips used, no repeats
- Energy Compromises: 1 (High→Medium: 1)
- Processing Time: 64.2s

---

## Example 3: Good Performance (ref5)

### Reference Analysis (Gemini Output)
```json
{
  "total_duration": 16.64585,
  "editing_style": "Cinematic Montage",
  "emotional_intent": "Dynamic",
  "arc_description": "Video with multiple scene changes",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 0.77,
      "duration": 0.77,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Travel",
      "arc_stage": "Intro",
      "reasoning": "Intro shot from a moving bus, setting the travel theme."
    },
    {
      "id": 2,
      "start": 0.77,
      "end": 1.73,
      "duration": 0.96,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Travel",
      "arc_stage": "Intro",
      "reasoning": "Transition to arriving at the destination, showing a person getting off the bus."
    },
    {
      "id": 3,
      "start": 1.73,
      "end": 7.6,
      "duration": 5.87,
      "energy": "Medium",
      "motion": "Dynamic",
      "vibe": "Nature",
      "arc_stage": "Build-up",
      "reasoning": "Montage of travel activities and scenery, building the narrative of the trip."
    }
  ],
  "overall_reasoning": "The video is a classic travel montage, starting with the journey, building up with scenic views and activities, and peaking with high-energy social moments among friends.",
  "ideal_material_suggestions": [
    "More varied shots of the group interacting.",
    "Close-ups of faces during the high-energy bus scenes.",
    "B-roll of the local culture or food.",
    "A clear concluding shot of the group together."
  ],
  "_cache_version": "6.1",
  "_cached_at": "2026-01-22 22:08:24"
}
```

### Key Matching Decisions
- Segment 1 (0.00-0.77s): clip33.mp4 selected - Score: 105.0 | Vibe:Travel match | Medium/Dynamic
- Segment 2 (0.77-1.73s): clip14.mp4 selected - Score: 110.0 | Vibe:Travel match | Medium/Dynamic
- Segment 3 (1.73-7.60s): clip28.mp4 selected - Score: 110.0 | Vibe:Nature match | Medium/Dynamic (subdivided into 6 cuts)

### Performance Metrics
- Vibe Match Accuracy: 96.2% (25/26 segments)
- Clip Diversity: 26/55 unique clips used, no repeats
- Energy Compromises: 6 (Medium→Low: 5, Medium→High: 1)
- Processing Time: 19.7s

---

## Sample Clip Analyses (Gemini Outputs)

### Clip 1: Hiking Trail (clip28.mp4)
```json
{
  "energy": "Medium",
  "motion": "Dynamic",
  "vibes": ["Nature", "Travel", "Hiking"],
  "content_description": "A first-person perspective of walking along a rocky, uneven trail through a pine forest.",
  "best_moments": {
    "High": {
      "start": 31.0,
      "end": 34.0,
      "reason": "Navigating a rockier section with more camera movement and dynamic perspective."
    },
    "Medium": {
      "start": 5.0,
      "end": 8.0,
      "reason": "Steady walking on the trail, representing the overall pace of the hike."
    },
    "Low": {
      "start": 21.0,
      "end": 24.0,
      "reason": "A slightly flatter, more stable part of the walk with minimal camera shake."
    }
  },
  "_cache_version": "6.1",
  "_cached_at": "2026-01-23 01:01:53"
}
```

### Clip 2: Beach Wave (clip55.mp4)
```json
{
  "energy": "High",
  "motion": "Dynamic",
  "vibes": ["Nature", "Beach", "Action"],
  "content_description": "A wave crashes onto a beach, eventually splashing over the camera lens.",
  "best_moments": {
    "High": {
      "start": 5.0,
      "end": 8.0,
      "reason": "The wave crashes directly into the camera, creating a high-energy splash and white foam."
    },
    "Medium": {
      "start": 2.5,
      "end": 5.0,
      "reason": "The wave builds up and begins to break, showing moderate motion and anticipation."
    },
    "Low": {
      "start": 0.0,
      "end": 2.5,
      "reason": "The opening shot shows relatively calm water before the main wave reaches the camera."
    }
  },
  "_cache_version": "6.1",
  "_cached_at": "2026-01-23 15:56:39"
}
```

### Clip 3: Urban Walking (clip54.mp4)
```json
{
  "energy": "Medium",
  "motion": "Dynamic",
  "vibes": ["Urban", "Walking", "Casual"],
  "content_description": "Two people walking away from the camera along a tiled corridor towards an outdoor area.",
  "best_moments": {
    "High": {
      "start": 1.0,
      "end": 3.0,
      "reason": "Steady walking pace with consistent camera movement following the subjects."
    },
    "Medium": {
      "start": 0.5,
      "end": 2.5,
      "reason": "Moderate movement as the subjects progress down the walkway."
    },
    "Low": {
      "start": 0.0,
      "end": 2.0,
      "reason": "Initial start of the walk with slightly less momentum."
    }
  },
  "_cache_version": "6.1",
  "_cached_at": "2026-01-23 15:56:07"
}
```

### Clip 4: Beach Camels (clip56.mp4)
```json
{
  "energy": "Medium",
  "motion": "Dynamic",
  "vibes": ["Travel", "Beach", "Animals"],
  "content_description": "A group of people and camels are gathered on a crowded beach under an overcast sky.",
  "best_moments": {
    "High": {
      "start": 1.2,
      "end": 3.2,
      "reason": "Dynamic camera movement panning across people towards the camels, creating a sense of discovery."
    },
    "Medium": {
      "start": 0.0,
      "end": 2.0,
      "reason": "Initial pan showing the beach environment and the scale of the crowd."
    },
    "Low": {
      "start": 2.5,
      "end": 4.272472,
      "reason": "The camera movement slows down as it focuses on the camels standing on the sand."
    }
  },
  "_cache_version": "6.1",
  "_cached_at": "2026-01-23 15:57:32"
}
```

### Clip 5: Camel Walking (clip51.mp4)
```json
{
  "energy": "Medium",
  "motion": "Dynamic",
  "vibes": ["Travel", "Nature", "Beach"],
  "content_description": "A decorated camel walks along a sunny beach with people swimming in the background.",
  "best_moments": {
    "High": {
      "start": 3.5,
      "end": 5.5,
      "reason": "The camel is fully in frame walking across the beach with dynamic camera movement and bright sunlight."
    },
    "Medium": {
      "start": 2.0,
      "end": 4.0,
      "reason": "The camera begins to pan as the camel enters the frame, creating a sense of movement."
    },
    "Low": {
      "start": 0.0,
      "end": 2.0,
      "reason": "A relatively calm opening shot of the ocean waves and the beach before the main action starts."
    }
  },
  "_cache_version": "6.1",
  "_cached_at": "2026-01-23 15:47:24"
}
```

---

## Summary

### What Gemini Extracts

**From Reference Videos:**
- Temporal structure (segment boundaries, durations)
- Energy levels (High/Medium/Low)
- Motion classification (Dynamic/Static)
- Semantic vibes (Nature, Travel, Friends, Celebration, etc.)
- Arc stages (Intro/Build-up/Peak/Outro)
- Reasoning for each segment

**From User Clips:**
- Overall energy and motion
- 3-4 semantic vibe tags
- Content description
- Best moments for each energy level (High/Medium/Low) with timestamps and reasoning

### How System Uses This Data

1. Reference analysis creates a "blueprint" of when cuts should happen and what vibe/energy each segment needs
2. Clip analysis provides metadata for matching - system finds clips with matching vibes and appropriate energy
3. Best moments extraction allows precise sub-clip selection based on segment energy requirements
4. Matching algorithm scores clips based on vibe alignment, energy compatibility, and best moment availability

### Performance Range

- Best case (ref4): 100% vibe match, perfect diversity, minimal compromises
- Average case (ref3): 53.3% vibe match, struggles with abstract vibes like "Social", "Candid", "Summer"
- Good case (ref5): 96.2% vibe match, handles concrete vibes well (Nature, Travel, Friends)
