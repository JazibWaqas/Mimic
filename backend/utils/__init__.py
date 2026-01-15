"""
Utils package for MIMIC backend.
"""

import sys
from pathlib import Path

# Import API key manager from this package
from .api_key_manager import get_key_manager, get_api_key, rotate_api_key

# Import utility functions from parent utils.py file
# We need to import from the parent module
_parent_utils = Path(__file__).parent.parent / "utils.py"
if _parent_utils.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("utils_module", _parent_utils)
    utils_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils_module)
    
    ensure_directory = utils_module.ensure_directory
    cleanup_session = utils_module.cleanup_session
    cleanup_all_temp = utils_module.cleanup_all_temp
    get_file_size_mb = utils_module.get_file_size_mb
    format_duration = utils_module.format_duration
else:
    # Fallback if utils.py doesn't exist
    def ensure_directory(path):
        Path(path).mkdir(parents=True, exist_ok=True)
        return Path(path)
    
    def cleanup_session(session_id: str, cleanup_uploads: bool = False):
        pass

__all__ = [
    'get_key_manager', 'get_api_key', 'rotate_api_key',
    'ensure_directory', 'cleanup_session', 'cleanup_all_temp',
    'get_file_size_mb', 'format_duration'
]
