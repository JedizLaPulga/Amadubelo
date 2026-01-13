"""
Disk Cleaner
Clean temporary files and caches.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Callable, Optional
import send2trash


def get_temp_locations() -> List[Dict]:
    """Get common temporary file locations on Windows."""
    
    user_home = Path.home()
    windows_dir = Path(os.environ.get('SYSTEMROOT', 'C:\\Windows'))
    
    locations = [
        {
            "name": "Windows Temp",
            "path": str(windows_dir / "Temp"),
            "description": "Windows temporary files",
            "safe": True,
        },
        {
            "name": "User Temp",
            "path": tempfile.gettempdir(),
            "description": "User temporary files",
            "safe": True,
        },
        {
            "name": "Prefetch",
            "path": str(windows_dir / "Prefetch"),
            "description": "Windows prefetch cache",
            "safe": True,
        },
        {
            "name": "Thumbnail Cache",
            "path": str(user_home / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer"),
            "description": "Windows thumbnail cache",
            "safe": True,
        },
        {
            "name": "Recent Files",
            "path": str(user_home / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent"),
            "description": "Recent files shortcuts",
            "safe": True,
        },
    ]
    
    return locations


def get_folder_size(path: str) -> int:
    """Calculate total size of a folder in bytes."""
    total_size = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    return total_size


def scan_temp_locations() -> List[Dict]:
    """Scan temp locations and return sizes."""
    locations = get_temp_locations()
    
    for loc in locations:
        path = loc["path"]
        if os.path.exists(path):
            loc["exists"] = True
            loc["size"] = get_folder_size(path)
            loc["size_formatted"] = format_size(loc["size"])
            loc["file_count"] = count_files(path)
        else:
            loc["exists"] = False
            loc["size"] = 0
            loc["size_formatted"] = "0 B"
            loc["file_count"] = 0
    
    return locations


def clean_folder(
    path: str,
    to_trash: bool = True,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Clean a folder by deleting its contents.
    
    Args:
        path: Folder path to clean
        to_trash: If True, move to recycle bin instead of permanent delete
        progress_callback: Optional callback(current, total, current_file)
        
    Returns:
        Dictionary with results
    """
    if not os.path.exists(path):
        return {"success": False, "error": "Path does not exist"}
    
    deleted_count = 0
    failed_count = 0
    freed_space = 0
    
    items = []
    try:
        items = list(os.scandir(path))
    except PermissionError:
        return {"success": False, "error": "Permission denied"}
    
    total = len(items)
    
    for i, item in enumerate(items):
        try:
            # Get size before deletion
            if item.is_file():
                size = item.stat().st_size
            else:
                size = get_folder_size(item.path)
            
            # Delete or move to trash
            if to_trash:
                send2trash.send2trash(item.path)
            else:
                if item.is_file():
                    os.remove(item.path)
                else:
                    shutil.rmtree(item.path)
            
            deleted_count += 1
            freed_space += size
            
        except Exception as e:
            failed_count += 1
        
        if progress_callback:
            progress_callback(i + 1, total, item.name)
    
    return {
        "success": True,
        "deleted": deleted_count,
        "failed": failed_count,
        "freed_space": freed_space,
        "freed_space_formatted": format_size(freed_space),
    }


def clean_all_temp(
    to_trash: bool = True,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """Clean all temporary locations."""
    locations = get_temp_locations()
    
    total_deleted = 0
    total_failed = 0
    total_freed = 0
    
    for loc in locations:
        if loc.get("safe", False) and os.path.exists(loc["path"]):
            result = clean_folder(loc["path"], to_trash, progress_callback)
            if result["success"]:
                total_deleted += result["deleted"]
                total_failed += result["failed"]
                total_freed += result["freed_space"]
    
    return {
        "deleted": total_deleted,
        "failed": total_failed,
        "freed_space": total_freed,
        "freed_space_formatted": format_size(total_freed),
    }


def count_files(path: str) -> int:
    """Count total files in a directory."""
    count = 0
    try:
        for _, _, files in os.walk(path):
            count += len(files)
    except (OSError, PermissionError):
        pass
    return count


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
