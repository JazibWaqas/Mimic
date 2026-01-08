"""
Utility functions for MIMIC project.
"""

import shutil
from pathlib import Path
from typing import List


def ensure_directory(path: str | Path) -> Path:
    """
    Create directory if it doesn't exist.
    
    Returns:
        Path object for chaining
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def cleanup_session(session_id: str, cleanup_uploads: bool = False) -> None:
    """
    Clean up temporary processing files for a session.
    
    NOTE: This only cleans temp/ (intermediate processing files).
    Uploaded files in data/uploads/ are kept by default (permanent).
    
    Args:
        session_id: Session ID to clean
        cleanup_uploads: If True, also delete uploaded files from data/uploads/
    """
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Clean temp/ (intermediate processing files)
    temp_session_dir = BASE_DIR / "temp" / session_id
    if temp_session_dir.exists():
        shutil.rmtree(temp_session_dir, ignore_errors=True)
        print(f"[CLEANUP] Deleted temp files: {temp_session_dir}")
    
    # Optionally clean uploads/ (permanent files)
    if cleanup_uploads:
        uploads_session_dir = BASE_DIR / "data" / "uploads" / session_id
        if uploads_session_dir.exists():
            shutil.rmtree(uploads_session_dir, ignore_errors=True)
            print(f"[CLEANUP] Deleted uploaded files: {uploads_session_dir}")


def cleanup_all_temp() -> None:
    """Delete all temporary files."""
    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


def get_file_size_mb(path: str | Path) -> float:
    """Get file size in megabytes."""
    return Path(path).stat().st_size / (1024 * 1024)


def format_duration(seconds: float) -> str:
    """Format duration as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

