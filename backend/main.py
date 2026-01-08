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

from dotenv import load_dotenv
from models import *
from engine.orchestrator import run_mimic_pipeline
from utils import ensure_directory, cleanup_session

# Load environment variables
load_dotenv()

# Root Directory Setup
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "results"

# Ensure dirs exist
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
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
    
    Returns:
        {
            "session_id": "uuid",
            "reference": {"filename": "...", "size": ...},
            "clips": [{"filename": "...", "size": ...}, ...]
        }
    """
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Create session directories
    session_dir = TEMP_DIR / session_id
    ref_dir = ensure_directory(session_dir / "reference")
    clips_dir = ensure_directory(session_dir / "clips")
    
    # Save reference
    ref_path = ref_dir / reference.filename
    with open(ref_path, "wb") as f:
        content = await reference.read()
        f.write(content)
    
    # Save clips
    clip_paths = []
    for clip in clips:
        clip_path = clips_dir / clip.filename
        with open(clip_path, "wb") as f:
            content = await clip.read()
            f.write(content)
        clip_paths.append(str(clip_path))
    
    # Store session info
    active_sessions[session_id] = {
        "reference_path": str(ref_path),
        "clip_paths": clip_paths,
        "status": "uploaded",
        "progress": 0.0
    }
    
    return {
        "session_id": session_id,
        "reference": {
            "filename": reference.filename,
            "size": ref_path.stat().st_size
        },
        "clips": [
            {"filename": Path(p).name, "size": Path(p).stat().st_size}
            for p in clip_paths
        ]
    }


@app.post("/api/upload-manual")
async def upload_manual(
    clips: List[UploadFile] = File(...),
    blueprint: str = File(...),
    clip_analysis: str = File(...)
):
    """
    Manual mode: Upload clips with pre-analyzed JSON from AI Studio.
    Bypasses Gemini API entirely - only runs matching + rendering.
    
    Returns:
        {"session_id": "uuid", "mode": "manual"}
    """
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Create session directories
    session_dir = TEMP_DIR / session_id
    clips_dir = ensure_directory(session_dir / "clips")
    
    # Save clips
    clip_paths = []
    for clip in clips:
        clip_path = clips_dir / clip.filename
        with open(clip_path, "wb") as f:
            content = await clip.read()
            f.write(content)
        clip_paths.append(str(clip_path))
    
    # Parse and validate JSON
    try:
        blueprint_data = json.loads(blueprint)
        clip_analysis_data = json.loads(clip_analysis)
        
        # Validate structure
        from models import StyleBlueprint, ClipIndex
        validated_blueprint = StyleBlueprint(**blueprint_data)
        validated_clips = ClipIndex(**clip_analysis_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    # Store session info with manual mode flag
    active_sessions[session_id] = {
        "mode": "manual",
        "clip_paths": clip_paths,
        "blueprint": validated_blueprint.model_dump(),
        "clip_index": validated_clips.model_dump(),
        "status": "uploaded",
        "progress": 0.0
    }
    
    return {
        "session_id": session_id,
        "mode": "manual",
        "clips": [{"filename": Path(p).name} for p in clip_paths]
    }


@app.post("/api/generate/{session_id}")
async def generate_video(session_id: str, background_tasks: BackgroundTasks):
    """
    Start video generation pipeline.
    Client should connect to WebSocket for real-time progress.
    
    Returns:
        {"status": "processing", "session_id": "..."}
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] == "processing":
        return {"status": "already_processing", "session_id": session_id}
    
    # Mark as processing
    session["status"] = "processing"
    session["progress"] = 0.0
    
    # Run pipeline in background
    background_tasks.add_task(
        process_video_pipeline,
        session_id,
        session["reference_path"],
        session["clip_paths"]
    )
    
    return {"status": "processing", "session_id": session_id}


def process_video_pipeline(session_id: str, ref_path: str = None, clip_paths: List[str] = None):
    """
    Run the MIMIC pipeline with progress updates.
    Supports both Auto mode (with Gemini API) and Manual mode (pre-analyzed JSON).
    """
    def progress_callback(step: int, total: int, message: str):
        active_sessions[session_id]["progress"] = step / total
        active_sessions[session_id]["current_step"] = message
    
    try:
        session = active_sessions[session_id]
        
        # Check if manual mode
        if session.get("mode") == "manual":
            # Manual mode: Use pre-provided analysis
            from models import StyleBlueprint, ClipIndex
            from engine.orchestrator import run_mimic_pipeline_manual
            
            blueprint = StyleBlueprint(**session["blueprint"])
            clip_index = ClipIndex(**session["clip_index"])
            clip_paths = session["clip_paths"]
            
            result = run_mimic_pipeline_manual(
                blueprint=blueprint,
                clip_index=clip_index,
                clip_paths=clip_paths,
                session_id=session_id,
                output_dir=str(RESULTS_DIR),
                progress_callback=progress_callback
            )
        else:
            # Auto mode: Full pipeline with Gemini
            result = run_mimic_pipeline(
                reference_path=ref_path,
                clip_paths=clip_paths,
                session_id=session_id,
                output_dir=str(RESULTS_DIR),
                progress_callback=progress_callback
            )
        
        if result.success:
            active_sessions[session_id]["status"] = "complete"
            active_sessions[session_id]["output_path"] = result.output_path
            active_sessions[session_id]["blueprint"] = result.blueprint.model_dump() if result.blueprint else None
            active_sessions[session_id]["clip_index"] = result.clip_index.model_dump() if result.clip_index else None
        else:
            active_sessions[session_id]["status"] = "error"
            active_sessions[session_id]["error"] = result.error
            
    except Exception as e:
        active_sessions[session_id]["status"] = "error"
        active_sessions[session_id]["error"] = str(e)


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
        filename=f"mimic_output_{session_id[:8]}.mp4"
    )


@app.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time progress updates.
    """
    await websocket.accept()
    
    try:
        while True:
            if session_id in active_sessions:
                session = active_sessions[session_id]
                await websocket.send_json({
                    "status": session["status"],
                    "progress": session.get("progress", 0.0),
                    "message": session.get("current_step", "")
                })
                
                # Stop sending if complete or error
                if session["status"] in ["complete", "error"]:
                    break
            
            await asyncio.sleep(1)  # Update every second
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


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


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

