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


def cleanup_session(session_id: str, keep_dirs: bool = False) -> None:
    """
    Clean up temporary files for a session.
    
    Args:
        session_id: Session ID to clean
        keep_dirs: If True, keep directory structure but delete contents
    """
    session_dir = Path(f"temp/{session_id}")
    
    if not session_dir.exists():
        return
    
    if keep_dirs:
        # Delete contents but keep structure
        for subdir in session_dir.iterdir():
            if subdir.is_dir():
                for file in subdir.iterdir():
                    if file.is_file():
                        file.unlink()
    else:
        # Delete entire session directory
        shutil.rmtree(session_dir, ignore_errors=True)


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

