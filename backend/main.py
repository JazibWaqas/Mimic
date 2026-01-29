"""
MIMIC FastAPI Backend
Handles file uploads, Gemini 3 processing, and video rendering.
"""

import os
import sys
from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uuid
from pathlib import Path
from typing import List
import asyncio
import json
import hashlib

from dotenv import load_dotenv
from models import *
from engine.orchestrator import run_mimic_pipeline
from engine.processors import generate_thumbnail
from utils import ensure_directory, cleanup_session

# Load environment variables
load_dotenv()

# Root Directory Setup - Matching test_ref.py structure
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"  # Only for intermediate processing files
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
CLIPS_DIR = SAMPLES_DIR / "clips"  # All user clips go here
REFERENCES_DIR = SAMPLES_DIR / "reference"  # All reference videos go here
RESULTS_DIR = DATA_DIR / "results"  # Final output videos
CACHE_DIR = DATA_DIR / "cache"      # Cached AI analyses
THUMBNAILS_DIR = DATA_DIR / "cache" / "thumbnails"

# Ensure dirs exist
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="MIMIC API", version="1.0.0")

# CORS for Next.js frontend - Apply Fix 1 from Section 9.5
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Specific URL, not "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track active sessions
active_sessions = {}

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/api/upload")
async def upload_files(
    reference: UploadFile = File(...),
    clips: List[UploadFile] = File(...)
):
    """
    Upload reference video and user clips.
    Saves directly to data/samples/ structure (matching test_ref.py).
    
    Returns:
        {
            "session_id": "uuid",
            "reference": {"filename": "...", "size": ...},
            "clips": [{"filename": "...", "size": ...}, ...]
        }
    """
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    print(f"\n[UPLOAD] New upload request")
    print(f"[UPLOAD] Session ID: {session_id}")
    print(f"[UPLOAD] Reference: {reference.filename}")
    print(f"[UPLOAD] Clips: {len(clips)} files")
    
    # Read reference content and calculate hash
    ref_content = await reference.read()
    ref_hash = hashlib.md5(ref_content).hexdigest()[:12]
    
    # Check if file with same content already exists
    existing_ref = None
    for existing_file in REFERENCES_DIR.glob("*.mp4"):
        if existing_file.is_file():
            try:
                with open(existing_file, 'rb') as f:
                    existing_hash = hashlib.md5(f.read()).hexdigest()[:12]
                if existing_hash == ref_hash:
                    existing_ref = existing_file
                    print(f"[UPLOAD] Reference content already exists: {existing_file.name} (reusing)")
                    break
            except Exception:
                continue
    
    if existing_ref:
        ref_path = existing_ref
    else:
        # Save new reference
        ref_path = REFERENCES_DIR / reference.filename
        if ref_path.exists():
            base_name = ref_path.stem
            counter = 1
            while ref_path.exists():
                ref_path = REFERENCES_DIR / f"{base_name}_{counter}{ref_path.suffix}"
                counter += 1
            print(f"[UPLOAD] Reference filename conflict, saved as: {ref_path.name}")
        
        with open(ref_path, "wb") as f:
            f.write(ref_content)
        print(f"[UPLOAD] Reference saved to: {ref_path}")
    
    # Save clips to data/samples/clips/ (matching test_ref.py)
    clip_paths = []
    skipped_count = 0
    
    # Pre-calculate hashes for all existing files to avoid reading them multiple times
    existing_hashes = {}
    existing_files_list = list(CLIPS_DIR.glob("*.mp4"))
    print(f"[UPLOAD] Checking {len(existing_files_list)} existing clips for duplicates...")
    for existing_file in existing_files_list:
        if existing_file.is_file():
            file_hash = get_file_hash(existing_file)
            if file_hash:
                existing_hashes[file_hash] = existing_file
                print(f"[UPLOAD] Hash for existing file: {existing_file.name} -> {file_hash}")
    
    print(f"[UPLOAD] Pre-calculated {len(existing_hashes)} existing clip hashes")
    
    for clip in clips:
        clip_content = await clip.read()
        # Fast hash for incoming content: if large, hash start and end
        hasher = hashlib.md5()
        if len(clip_content) < 2 * 1024 * 1024:
            hasher.update(clip_content)
        else:
            hasher.update(clip_content[:1024 * 1024])
            hasher.update(clip_content[-1024 * 1024:])
        
        clip_hash = hasher.hexdigest()[:12]
        print(f"[UPLOAD] Incoming clip '{clip.filename}' hash: {clip_hash}")
        
        # Check if file with same content already exists
        if clip_hash in existing_hashes:
            existing_clip = existing_hashes[clip_hash]
            print(f"[UPLOAD] ✅ DUPLICATE DETECTED: Clip content already exists as '{existing_clip.name}' (skipping save, will reuse)")
            clip_paths.append(str(existing_clip))
            skipped_count += 1
            continue
        
        print(f"[UPLOAD] ⚠️ NEW CLIP: Hash {clip_hash} not found in existing files, saving...")
        
        # Save new clip
        clip_path = CLIPS_DIR / clip.filename
        if clip_path.exists():
            base_name = clip_path.stem
            counter = 1
            while clip_path.exists():
                clip_path = CLIPS_DIR / f"{base_name}_{counter}{clip_path.suffix}"
                counter += 1
            print(f"[UPLOAD] Clip filename conflict, saved as: {clip_path.name}")
        
        with open(clip_path, "wb") as f:
            f.write(clip_content)
        clip_paths.append(str(clip_path))
        print(f"[UPLOAD] New clip saved: {clip_path.name}")
    
    print(f"[UPLOAD] {len(clips)} clips processed, {len(clip_paths)} clips will be used ({len(clip_paths) - skipped_count} new, {skipped_count} existing reused)")
    
    # Store session info
    active_sessions[session_id] = {
        "reference_path": str(ref_path),
        "clip_paths": clip_paths,
        "status": "uploaded",
        "progress": 0.0,
        "logs": []
    }
    
    print(f"[UPLOAD] Upload complete - session created\n")
    
    return {
        "session_id": session_id,
        "reference": {
            "filename": ref_path.name,
            "size": ref_path.stat().st_size
        },
        "clips": [
            {"filename": Path(p).name, "size": Path(p).stat().st_size}
            for p in clip_paths
        ]
    }


@app.post("/api/generate/{session_id}")
async def generate_video(session_id: str, background_tasks: BackgroundTasks):
    """
    Start video generation pipeline.
    Client should connect to WebSocket for real-time progress.
    
    Returns:
        {"status": "processing", "session_id": "..."}
    """
    # Session recovery not needed - files are in data/samples/ and session info is in memory
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please upload files first.")
    
    session = active_sessions[session_id]
    
    if session["status"] == "processing":
        return {"status": "already_processing", "session_id": session_id}
    
    # Mark as processing
    session["status"] = "processing"
    session["progress"] = 0.0
    
    # Run pipeline in background
    print(f"[GENERATE] Starting pipeline for session: {session_id}")
    print(f"[GENERATE] Reference: {session.get('reference_path')}")
    print(f"[GENERATE] Clips: {len(session.get('clip_paths', []))}")
    
    background_tasks.add_task(
        process_video_pipeline,
        session_id,
        session.get("reference_path"),
        session.get("clip_paths")
    )
    
    return {"status": "processing", "session_id": session_id}


def process_video_pipeline(session_id: str, ref_path: str = None, clip_paths: List[str] = None):
    """
    Run the MIMIC pipeline with progress updates.
    Uses Gemini API for analysis.
    """
    import time
    import sys
    from io import StringIO
    start_time = time.time()
    
    # Initialize logs list in session
    if session_id in active_sessions:
        active_sessions[session_id]["logs"] = []
    
    # Custom stdout handler to capture orchestrator output
    class LogCapture:
        def __init__(self, original_stdout, session_id):
            self.original_stdout = original_stdout
            self.session_id = session_id
            self.buffer = ""
        
        def write(self, s):
            # Write to original stdout (console)
            self.original_stdout.write(s)
            self.original_stdout.flush()
            
            # Store in session logs
            if self.session_id in active_sessions:
                if s.strip():  # Only store non-empty lines
                    # Split by newlines and add each line
                    lines = s.split('\n')
                    for line in lines:
                        if line.strip():
                            active_sessions[self.session_id]["logs"].append(line.strip())
                            # Keep only last 500 lines to avoid memory issues
                            if len(active_sessions[self.session_id]["logs"]) > 500:
                                active_sessions[self.session_id]["logs"].pop(0)
        
        def flush(self):
            self.original_stdout.flush()
    
    # Capture stdout
    log_capture = LogCapture(sys.stdout, session_id)
    original_stdout = sys.stdout
    sys.stdout = log_capture
    
    print(f"\n{'='*60}")
    print(f"[PIPELINE] STARTING NEW PIPELINE RUN")
    print(f"{'='*60}")
    print(f"[PIPELINE] Session ID: {session_id}")
    print(f"[PIPELINE] Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[PIPELINE] Reference: {ref_path}")
    print(f"[PIPELINE] Clips ({len(clip_paths) if clip_paths else 0}): {clip_paths}")
    print(f"{'='*60}\n")
    
    def progress_callback(step: int, total: int, message: str):
        if session_id in active_sessions:
            active_sessions[session_id]["progress"] = step / total
            active_sessions[session_id]["current_step"] = message
            print(f"[PROGRESS] Step {step}/{total}: {message}")
    
    try:
        if session_id not in active_sessions:
            print(f"[PIPELINE] ERROR: Session {session_id} not found in active_sessions")
            return
        
        session = active_sessions[session_id]
        
        # Run pipeline with Gemini API
        print(f"[PIPELINE] Running pipeline with Gemini...")
        result = run_mimic_pipeline(
            reference_path=ref_path,
            clip_paths=clip_paths,
            session_id=session_id,
            output_dir=str(RESULTS_DIR),
            progress_callback=progress_callback
        )
        
        elapsed = time.time() - start_time
        
        if result.success:
            print(f"\n[PIPELINE] SUCCESS - Pipeline completed in {elapsed:.1f}s")
            print(f"[PIPELINE] Output: {result.output_path}")
            active_sessions[session_id]["status"] = "complete"
            active_sessions[session_id]["output_path"] = result.output_path
            active_sessions[session_id]["blueprint"] = result.blueprint.model_dump() if result.blueprint else None
            active_sessions[session_id]["clip_index"] = result.clip_index.model_dump() if result.clip_index else None
        else:
            print(f"\n[PIPELINE] FAILED - Error: {result.error}")
            active_sessions[session_id]["status"] = "error"
            active_sessions[session_id]["error"] = result.error
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[PIPELINE] EXCEPTION after {elapsed:.1f}s: {e}")
        import traceback
        traceback.print_exc()
        active_sessions[session_id]["status"] = "error"
        active_sessions[session_id]["error"] = str(e)
    finally:
        # Restore stdout
        sys.stdout = original_stdout


@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """
    Get current processing status.
    
    Returns:
        {
            "status": "uploaded" | "processing" | "complete" | "error",
            "progress": 0.0-1.0,
            "current_step": "Analyzing reference...",
            "output_path": "..." (if complete)
        }
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]


@app.get("/api/download/{session_id}")
async def download_video(session_id: str):
    """
    Download final video.
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] != "complete":
        raise HTTPException(status_code=400, detail="Video not ready")
    
    output_path = session["output_path"]
    
    if not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"mimic_output_{session_id}.mp4"
    )


@app.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time progress updates.
    """
    print(f"[WS] Connection attempt for session: {session_id}")
    # Accept WebSocket connection (CORS is handled at HTTP level)
    origin = websocket.headers.get("origin")
    print(f"[WS] Origin: {origin}")
    allowed_origins = [FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"]
    
    # In development, be more lenient
    if origin and origin not in allowed_origins:
        # Log but allow in development (localhost variants)
        if "localhost" in origin or "127.0.0.1" in origin:
            print(f"[WS] Allowing localhost origin: {origin}")
        else:
            print(f"[WS] Rejecting connection from origin: {origin}")
            await websocket.close(code=1008, reason="Origin not allowed")
            return
    
    try:
        await websocket.accept()
        print(f"[WS] Connection accepted for session: {session_id}")
    except Exception as e:
        print(f"[WS] Failed to accept connection: {e}")
        return
    
    try:
        # Wait up to 10 seconds for session to be created
        wait_count = 0
        max_wait = 10
        
        while wait_count < max_wait:
            if session_id in active_sessions:
                print(f"[WS] Session found: {session_id}")
                break
            await asyncio.sleep(0.5)
            wait_count += 0.5
        
        if session_id not in active_sessions:
            print(f"[WS] Session not found after {max_wait}s: {session_id}")
            await websocket.send_json({
                "status": "error",
                "progress": 0.0,
                "message": "Session not found. Make sure you've uploaded files first."
            })
            await websocket.close(code=1000)
            return
        
        # Send initial status
        session = active_sessions[session_id]
        await websocket.send_json({
            "status": session["status"],
            "progress": session.get("progress", 0.0),
            "message": session.get("current_step", "Waiting to start...")
        })
        
        while True:
            if session_id in active_sessions:
                session = active_sessions[session_id]
                await websocket.send_json({
                    "status": session["status"],
                    "progress": session.get("progress", 0.0),
                    "message": session.get("current_step", ""),
                    "logs": session.get("logs", [])
                })
                
                # Stop sending if complete or error
                if session["status"] in ["complete", "error"]:
                    print(f"[WS] Session {session_id} finished with status: {session['status']}")
                    break
            else:
                # Session was deleted
                await websocket.send_json({
                    "status": "error",
                    "progress": 0.0,
                    "message": "Session expired"
                })
                break
            
            await asyncio.sleep(1)  # Update every second
            
    except Exception as e:
        print(f"[WS] Error in WebSocket handler: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "status": "error",
                "progress": 0.0,
                "message": f"Error: {str(e)}"
            })
        except:
            pass
    finally:
        try:
            await websocket.close(code=1000)
            print(f"[WS] Connection closed for session: {session_id}")
        except:
            pass


@app.get("/api/history")
async def get_history():
    """
    Get list of past projects (optional feature).
    For hackathon, can just return sessions from memory.
    """
    history = [
        {
            "session_id": sid,
            "status": session["status"],
            "created_at": session.get("created_at", ""),
            "reference_filename": Path(session["reference_path"]).name,
            "clip_count": len(session["clip_paths"])
        }
        for sid, session in active_sessions.items()
    ]
    return {"projects": history}


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Clean up session files.
    """
    if session_id in active_sessions:
        cleanup_session(session_id)
        del active_sessions[session_id]
        return {"status": "deleted"}
    
    raise HTTPException(status_code=404, detail="Session not found")


# Serve static files for previews (using explicit endpoints instead)
# Files are served via /api/files/ endpoints for better control

@app.get("/api/references")
async def list_reference_samples():
    """
    List all reference videos from data/samples/reference/ (matching test_ref.py structure).
    """
    if not REFERENCES_DIR.exists():
        return {"references": []}
    
    references = []
    for ref_path in REFERENCES_DIR.iterdir():
        if ref_path.is_file() and ref_path.suffix.lower() == '.mp4':
             ref_hash = get_file_hash(ref_path)
             thumb_name = f"thumb_ref_{ref_hash}.jpg"
             thumb_path = THUMBNAILS_DIR / thumb_name
             
             if not thumb_path.exists():
                 generate_thumbnail(str(ref_path), str(thumb_path))
                 
             references.append({
                "filename": ref_path.name,
                "path": f"/api/files/references/{ref_path.name}",
                "thumbnail_url": f"/api/files/thumbnails/{thumb_name}",
                "size": ref_path.stat().st_size,
                "created_at": ref_path.stat().st_mtime
            })
    # Sort by newest first
    references.sort(key=lambda x: x["created_at"], reverse=True)
    return {"references": references}

@app.get("/api/clips")
async def list_all_clips():
    """
    List all clips from data/samples/clips/ (matching test_ref.py structure).
    Used for the 'Gallery' page.
    """
    all_clips = []
    
    # Read all clips from data/samples/clips/ (matching test_ref.py)
    if CLIPS_DIR.exists():
        for clip_path in CLIPS_DIR.iterdir():
            if clip_path.is_file() and clip_path.suffix.lower() == '.mp4':
                clip_hash = get_file_hash(clip_path)
                thumb_name = f"thumb_clip_{clip_hash}.jpg"
                thumb_path = THUMBNAILS_DIR / thumb_name
                
                if not thumb_path.exists():
                    generate_thumbnail(str(clip_path), str(thumb_path))
                
                all_clips.append({
                    "session_id": "samples",
                    "filename": clip_path.name,
                    "path": f"/api/files/samples/clips/{clip_path.name}",
                    "thumbnail_url": f"/api/files/thumbnails/{thumb_name}",
                    "size": clip_path.stat().st_size,
                    "created_at": clip_path.stat().st_mtime
                })
    
    # Sort by newest first
    all_clips.sort(key=lambda x: x["created_at"], reverse=True)
    print(f"[API] Returning {len(all_clips)} clips from {CLIPS_DIR}")
    return {"clips": all_clips}

@app.delete("/api/clips/{session_id}/{filename}")
async def delete_specific_clip(session_id: str, filename: str):
    """
    Delete a specific clip from data/samples/clips/.
    """
    clip_path = CLIPS_DIR / filename
    if clip_path.exists():
        clip_path.unlink()
        print(f"[API] Deleted clip: {clip_path}")
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Clip not found")

@app.get("/api/results")
async def list_all_results():
    """
    List all generated videos in the results folder.
    Used for the 'Vault' page.
    """
    results = []
    for result_path in RESULTS_DIR.glob("*.mp4"):
        if result_path.is_file():
            res_hash = get_file_hash(result_path) # Might be slow for large results, but okay for list
            thumb_name = f"thumb_res_{res_hash}.jpg"
            thumb_path = THUMBNAILS_DIR / thumb_name
            
            if not thumb_path.exists():
                generate_thumbnail(str(result_path), str(thumb_path))
                
            results.append({
                "filename": result_path.name,
                "url": f"/api/files/results/{result_path.name}",
                "thumbnail_url": f"/api/files/thumbnails/{thumb_name}",
                "size": result_path.stat().st_size,
                "created_at": result_path.stat().st_mtime
            })
    # Sort by newest first
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return {"results": results}

@app.delete("/api/results/{filename}")
async def delete_result(filename: str):
    """
    Delete a generated video from the vault.
    """
    result_path = RESULTS_DIR / filename
    if result_path.exists():
        result_path.unlink()
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Result not found")

# ============================================================================
# INTELLIGENCE ENDPOINTS (For Vault A)
# ============================================================================

# Hash cache to avoid reading files multiple times
hash_cache = {}

def get_file_hash(path: Path) -> str:
    """Helper to get a fast hash of a file without reading the whole thing."""
    if not path.exists():
        return ""
    
    # Check cache first
    path_str = str(path)
    file_stat = path.stat()
    cache_key = f"{path_str}_{file_stat.st_mtime}_{file_stat.st_size}"
    
    if cache_key in hash_cache:
        return hash_cache[cache_key]
    
    try:
        # For small files, read the whole thing. For large files, read chunks.
        hasher = hashlib.md5()
        file_size = file_stat.st_size
        
        with open(path, "rb") as f:
            if file_size < 2 * 1024 * 1024:  # < 2MB
                hasher.update(f.read())
            else:
                # Read first 1MB
                hasher.update(f.read(1024 * 1024))
                # Seek to near the end and read another 1MB
                f.seek(max(0, file_size - 1024 * 1024))
                hasher.update(f.read(1024 * 1024))
        
        res = hasher.hexdigest()[:12]
        hash_cache[cache_key] = res
        return res
    except Exception as e:
        print(f"[HASH] Error hashing {path}: {e}")
        return hashlib.md5(path.name.encode()).hexdigest()[:12]

@app.get("/api/intelligence")
async def get_intelligence(type: str, filename: str):
    """
    Find and serve the AI intelligence/analysis JSON for a specific file.
    
    Types: 
    - results: Look for master JSON in data/results/
    - references: Look for ref_{hash}_h*.json in data/cache/
    - clips: Look for clip_comprehensive_{hash}.json in data/cache/
    """
    try:
        if type == "results":
            # Strip extension and search for master JSON
            stem = Path(filename).stem
            # In orchestrator.py, results are saved as "{ref_name}_{session_id}.json"
            # The frontend sends the filename of the MP4, e.g., "ref4_12345678.mp4"
            json_name = f"{stem}.json"
            json_path = RESULTS_DIR / json_name
            
            if not json_path.exists():
                # Try finding any JSON that starts with the stem (in case of extension mismatch)
                matches = list(RESULTS_DIR.glob(f"{stem}*.json"))
                if matches:
                    json_path = matches[0]
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        elif type == "references":
            ref_path = REFERENCES_DIR / filename
            if not ref_path.exists():
                raise HTTPException(status_code=404, detail="Reference video not found")
            
            ref_hash = get_file_hash(ref_path)
            # Reference cache naming: ref_{hash}_h{fingerprint}.json
            matches = list(CACHE_DIR.glob(f"ref_{ref_hash}_h*.json"))
            if matches:
                with open(matches[0], 'r', encoding='utf-8') as f:
                    return json.load(f)

        elif type == "clips":
            clip_path = CLIPS_DIR / filename
            if not clip_path.exists():
                raise HTTPException(status_code=404, detail="Clip video not found")
            
            clip_hash = get_file_hash(clip_path)
            # Clip cache naming: clip_comprehensive_{hash}.json
            json_path = CACHE_DIR / f"clip_comprehensive_{clip_hash}.json"
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        raise HTTPException(status_code=404, detail=f"Intelligence not found for {type}/{filename}")
        
    except Exception as e:
        print(f"[INTEL] Error fetching intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FILE SERVING ENDPOINTS (Explicit file serving for reliability)
# ============================================================================

@app.get("/api/files/results/{filename}")
async def serve_result_file(filename: str):
    """
    Serve a result video file explicitly.
    """
    result_path = RESULTS_DIR / filename
    if not result_path.exists() or not result_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(result_path),
        media_type="video/mp4",
        filename=filename
    )

@app.get("/api/files/references/{filename}")
async def serve_reference_file(filename: str):
    """
    Serve a reference video file explicitly.
    """
    ref_path = DATA_DIR / "samples" / "reference" / filename
    if not ref_path.exists() or not ref_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(ref_path),
        media_type="video/mp4",
        filename=filename
    )

@app.get("/api/files/samples/clips/{filename}")
async def serve_sample_clip_file(filename: str):
    """
    Serve a sample clip video file explicitly.
    """
    clip_path = DATA_DIR / "samples" / "clips" / filename
    if not clip_path.exists() or not clip_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(clip_path),
        media_type="video/mp4",
        filename=filename
    )

@app.get("/api/files/thumbnails/{filename}")
async def serve_thumbnail_file(filename: str):
    """
    Serve a thumbnail image file explicitly.
    """
    thumb_path = THUMBNAILS_DIR / filename
    if not thumb_path.exists() or not thumb_path.is_file():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(
        path=str(thumb_path),
        media_type="image/jpeg",
        filename=filename
    )


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

