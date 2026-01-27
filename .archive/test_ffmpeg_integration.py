import subprocess
from pathlib import Path

def test_ffmpeg_commands():
    print("Testing FFmpeg integration...\n")
    
    base_dir = Path(__file__).parent.parent
    
    test_video = base_dir / "data" / "samples" / "clips" / "clip.mp4"
    
    if not test_video.exists():
        print(f"ERROR: Test video not found: {test_video}")
        return False
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: FFmpeg version
    print("1. Testing 'ffmpeg -version'...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        print("   PASS: FFmpeg accessible")
        tests_passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        tests_failed += 1
    
    # Test 2: FFprobe duration
    print("\n2. Testing 'ffprobe -show_entries format=duration'...")
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(test_video)
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        print("   PASS: FFprobe can read video duration")
        tests_passed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        tests_failed += 1
    
    # Test 3: Standardization command (dry run with -t 1 to limit output)
    print("\n3. Testing standardization command (dry run, first 1 second)...")
    output_path = base_dir / "temp" / "test_standardize_output.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        cmd = [
            "ffmpeg",
            "-i", str(test_video),
            "-vf", (
                "scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
                "setsar=1"
            ),
            "-r", "30",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-t", "1",
            "-y",
            str(output_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        if output_path.exists():
            print("   PASS: Standardization command works")
            output_path.unlink()
            tests_passed += 1
        else:
            print("   FAIL: Output file not created")
            tests_failed += 1
    except subprocess.CalledProcessError as e:
        print(f"   FAIL: Command failed")
        print(f"   STDOUT: {e.stdout[:200]}")
        print(f"   STDERR: {e.stderr[:200]}")
        tests_failed += 1
        if output_path.exists():
            output_path.unlink()
    except Exception as e:
        print(f"   FAIL: {e}")
        tests_failed += 1
        if output_path.exists():
            output_path.unlink()
    
    print(f"\n{'='*50}")
    print(f"Results: {tests_passed} passed, {tests_failed} failed")
    print(f"{'='*50}\n")
    
    return tests_failed == 0

if __name__ == "__main__":
    success = test_ffmpeg_commands()
    exit(0 if success else 1)
